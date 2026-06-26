from __future__ import annotations


def datamatrix_explorer_js() -> str:
    return r"""
    (function initExplorer(){
        var dataEl = document.getElementById('dm-explorer-data');
        if(!dataEl || !window.Plotly) return;

        var payload = JSON.parse(dataEl.textContent);
        var meta = {};
        payload.columns.forEach(function(c){ meta[c.name] = c; });

        var state = {
            globalSearch: '',
            numericRanges: {},
            catSelections: {},
            boolFilter: {},
            missingOnly: {},
            visibleCols: payload.columns.map(function(c){ return c.name; }),
            xCol: payload.columns[0] ? payload.columns[0].name : '',
            yCol: '',
            colorCol: '',
            chartType: 'auto',
            page: 0,
            pageSize: 25,
            sortCol: '',
            sortDir: 'asc',
            chartReady: false
        };

        var palette = ['#6366F1','#22D3EE','#F472B6','#A78BFA','#34D399','#FBBF24','#FB7185','#38BDF8'];
        function colorForGroup(name, idx){ return palette[idx % palette.length]; }

        if(payload.truncated){
            var banner = document.getElementById('dm-exp-truncated');
            if(banner){
                banner.style.display = 'block';
                banner.textContent = 'Interactive mode loaded ' + payload.loadedRows.toLocaleString()
                    + ' of ' + payload.totalRows.toLocaleString()
                    + ' rows. Filters apply to the loaded sample.';
            }
        }

        function colMeta(name){ return meta[name] || {type:'text', name:name}; }
        function numVal(v){
            if(v === null || v === undefined || v === '') return null;
            var n = parseFloat(v);
            return isNaN(n) ? null : n;
        }

        function applyFilters(){
            var rows = payload.records;
            var q = state.globalSearch.trim().toLowerCase();
            if(q){
                rows = rows.filter(function(r){
                    return payload.columns.some(function(c){
                        if(state.visibleCols.indexOf(c.name) < 0) return false;
                        var v = r[c.name];
                        return v != null && String(v).toLowerCase().indexOf(q) >= 0;
                    });
                });
            }
            return rows.filter(function(r){
                for(var col in state.missingOnly){
                    if(!state.missingOnly[col]) continue;
                    if(r[col] !== null && r[col] !== undefined && r[col] !== '') return false;
                }
                for(var col in state.numericRanges){
                    var rng = state.numericRanges[col];
                    if(!rng) continue;
                    var v = numVal(r[col]);
                    if(v === null) return false;
                    if(rng.min != null && v < rng.min) return false;
                    if(rng.max != null && v > rng.max) return false;
                }
                for(var col in state.catSelections){
                    var sel = state.catSelections[col];
                    if(!sel || !sel.length) continue;
                    var sv = r[col] == null ? '' : String(r[col]);
                    if(sel.indexOf(sv) < 0) return false;
                }
                for(var col in state.boolFilter){
                    var bf = state.boolFilter[col];
                    if(!bf || bf === 'all') continue;
                    var truthy = r[col] === true || r[col] === 'True' || r[col] === 1 || r[col] === '1';
                    if(bf === 'true' && !truthy) return false;
                    if(bf === 'false' && truthy) return false;
                }
                return true;
            });
        }

        function buildFilterPanel(){
            var host = document.getElementById('dm-exp-filters');
            if(!host) return;
            host.innerHTML = '';
            payload.columns.forEach(function(c){
                var card = document.createElement('div');
                card.className = 'dm-exp-filter-card';
                var title = document.createElement('label');
                title.textContent = c.name + ' (' + c.type + ')';
                card.appendChild(title);

                var missLbl = document.createElement('label');
                missLbl.style.fontSize = '0.75rem';
                missLbl.innerHTML = '<input type="checkbox" data-miss="' + c.name + '"/> Missing only';
                card.appendChild(missLbl);

                if(c.type === 'numeric' && c.min != null && c.max != null){
                    var min = c.min, max = c.max;
                    state.numericRanges[c.name] = {min: min, max: max};
                    var sliderMin = document.createElement('input');
                    sliderMin.type = 'range';
                    sliderMin.min = min; sliderMin.max = max;
                    sliderMin.step = Math.max((max - min) / 100, 0.01);
                    sliderMin.value = min;
                    var slider = document.createElement('input');
                    slider.type = 'range';
                    slider.min = min; slider.max = max;
                    slider.step = sliderMin.step;
                    slider.value = max;
                    var readout = document.createElement('div');
                    readout.className = 'dm-exp-range-row';
                    readout.textContent = min.toFixed(2) + ' — ' + max.toFixed(2);
                    card.appendChild(sliderMin);
                    card.appendChild(slider);
                    card.appendChild(readout);
                    function syncRange(){
                        var lo = parseFloat(sliderMin.value), hi = parseFloat(slider.value);
                        if(lo > hi){ var t = lo; lo = hi; hi = t; }
                        state.numericRanges[c.name] = {min: lo, max: hi};
                        readout.textContent = lo.toFixed(2) + ' — ' + hi.toFixed(2);
                        refresh();
                    }
                    slider.addEventListener('input', syncRange);
                    sliderMin.addEventListener('input', syncRange);
                } else if((c.type === 'categorical' || c.type === 'boolean') && c.values){
                    var list = document.createElement('div');
                    list.className = 'dm-exp-cat-list';
                    state.catSelections[c.name] = c.values.map(function(v){ return v.label; });
                    c.values.slice(0, 15).forEach(function(v){
                        var lbl = document.createElement('label');
                        var safe = String(v.label).replace(/"/g, '&quot;');
                        lbl.innerHTML = '<input type="checkbox" checked data-cat="' + c.name + '" value="' + safe + '"/> '
                            + v.label + ' (' + v.count + ')';
                        list.appendChild(lbl);
                    });
                    card.appendChild(list);
                } else if(c.type === 'boolean'){
                    var sel = document.createElement('select');
                    sel.dataset.bool = c.name;
                    sel.innerHTML = '<option value="all">All</option><option value="true">True only</option><option value="false">False only</option>';
                    state.boolFilter[c.name] = 'all';
                    sel.addEventListener('change', function(){ state.boolFilter[c.name] = sel.value; refresh(); });
                    card.appendChild(sel);
                }
                host.appendChild(card);
            });

            host.querySelectorAll('input[data-miss]').forEach(function(cb){
                cb.addEventListener('change', function(){
                    state.missingOnly[cb.dataset.miss] = cb.checked;
                    refresh();
                });
            });
            host.querySelectorAll('input[data-cat]').forEach(function(cb){
                cb.addEventListener('change', function(){
                    var col = cb.dataset.cat;
                    var selected = [];
                    host.querySelectorAll('input[data-cat="' + col + '"]').forEach(function(x){
                        if(x.checked) selected.push(x.value);
                    });
                    state.catSelections[col] = selected;
                    refresh();
                });
            });
        }

        function buildColumnChecks(){
            var host = document.getElementById('dm-exp-col-checks');
            if(!host) return;
            host.innerHTML = '';
            payload.columns.forEach(function(c){
                var lbl = document.createElement('label');
                lbl.innerHTML = '<input type="checkbox" checked data-vis="' + c.name + '"/> ' + c.name;
                host.appendChild(lbl);
            });
            host.querySelectorAll('input[data-vis]').forEach(function(cb){
                cb.addEventListener('change', function(){
                    var col = cb.dataset.vis;
                    if(cb.checked){
                        if(state.visibleCols.indexOf(col) < 0) state.visibleCols.push(col);
                    } else {
                        state.visibleCols = state.visibleCols.filter(function(x){ return x !== col; });
                    }
                    refresh();
                });
            });
        }

        function fillSelects(){
            var xSel = document.getElementById('dm-exp-x');
            var ySel = document.getElementById('dm-exp-y');
            var cSel = document.getElementById('dm-exp-color');
            if(!xSel) return;
            xSel.innerHTML = '';
            payload.columns.forEach(function(c){
                var o = document.createElement('option');
                o.value = c.name; o.textContent = c.name + ' (' + c.type + ')';
                xSel.appendChild(o);
            });
            [ySel, cSel].forEach(function(sel){
                if(!sel) return;
                while(sel.options.length > 1) sel.remove(1);
                payload.columns.forEach(function(c){
                    var o = document.createElement('option');
                    o.value = c.name; o.textContent = c.name;
                    sel.appendChild(o);
                });
            });
            xSel.value = state.xCol;
        }

        function renderStats(rows){
            var el = document.getElementById('dm-exp-stats');
            if(!el) return;
            var cols = state.visibleCols.length;
            var miss = 0, cells = rows.length * cols;
            if(cells){
                rows.forEach(function(r){
                    state.visibleCols.forEach(function(c){
                        if(r[c] === null || r[c] === undefined || r[c] === '') miss++;
                    });
                });
            }
            el.innerHTML =
                '<span class="dm-exp-stat-pill">' + rows.length.toLocaleString() + ' rows (filtered)</span>' +
                '<span class="dm-exp-stat-pill">' + cols + ' visible columns</span>' +
                '<span class="dm-exp-stat-pill">' + (cells ? (100 - miss/cells*100).toFixed(1) : 0) + '% complete</span>' +
                '<span class="dm-exp-stat-pill">' + payload.totalRows.toLocaleString() + ' total in dataset</span>';
        }

        function item(l,v){ return '<div class="dm-exp-profile-item"><span>' + l + '</span><strong>' + v + '</strong></div>'; }
        function uniqueCount(a){ var s={}; a.forEach(function(v){ s[String(v)]=1; }); return Object.keys(s).length; }
        function mean(a){ return a.reduce(function(x,y){return x+y;},0)/a.length; }
        function std(a){ var m=mean(a); return Math.sqrt(a.reduce(function(s,v){ return s+(v-m)*(v-m); },0)/a.length); }
        function topValue(a){ var c={}; a.forEach(function(v){ var k=String(v); c[k]=(c[k]||0)+1; }); var best=null,b=0; for(var k in c){ if(c[k]>b){b=c[k];best=[k,c[k]];} } return best; }

        function renderProfile(rows, colName){
            var el = document.getElementById('dm-exp-profile');
            if(!el || !colName) return;
            var c = colMeta(colName);
            var vals = rows.map(function(r){ return r[colName]; }).filter(function(v){ return v !== null && v !== undefined && v !== ''; });
            var html = '<div class="dm-card-title"><span class="accent-dot"></span>Column profile: <strong>' + colName + '</strong></div><div class="dm-exp-profile-grid">';
            html += item('Type', c.type) + item('Non-null', vals.length) + item('Unique', uniqueCount(vals));
            if(c.type === 'numeric'){
                var nums = vals.map(numVal).filter(function(v){ return v !== null; });
                if(nums.length){
                    nums.sort(function(a,b){ return a-b; });
                    html += item('Mean', mean(nums).toFixed(3));
                    html += item('Median', nums[Math.floor(nums.length/2)].toFixed(3));
                    html += item('Min', nums[0].toFixed(3));
                    html += item('Max', nums[nums.length-1].toFixed(3));
                    html += item('Std Dev', std(nums).toFixed(3));
                }
            } else {
                var top = topValue(vals);
                html += item('Top value', top ? top[0] + ' (' + top[1] + ')' : '—');
            }
            html += '</div>';
            el.innerHTML = html;
        }

        function pickChartType(xc, yc){
            if(state.chartType !== 'auto') return state.chartType;
            if(!yc){
                if(xc.type === 'numeric') return 'histogram';
                if(xc.type === 'datetime') return 'line';
                return 'bar';
            }
            if(xc.type === 'numeric' && yc.type === 'numeric') return 'scatter';
            if((xc.type === 'categorical' || xc.type === 'boolean') && yc.type === 'numeric') return 'box';
            if(xc.type === 'numeric' && (yc.type === 'categorical' || yc.type === 'boolean')) return 'box';
            return 'bar';
        }

        function renderChart(rows){
            var target = document.getElementById('dm-explorer-chart');
            if(!target || !state.xCol) return;
            var xc = colMeta(state.xCol);
            var yc = state.yCol ? colMeta(state.yCol) : null;
            var ctype = pickChartType(xc, yc);
            var traces = [];
            var layout = {
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                margin: {l:50,r:20,t:30,b:50},
                font: {family: "'Geist','Segoe UI',sans-serif", color: '#E2E5FF'}
            };

            if(ctype === 'histogram'){
                var nums = rows.map(function(r){ return numVal(r[state.xCol]); }).filter(function(v){ return v !== null; });
                traces.push({type:'histogram', x: nums, marker:{color:'#6366F1'}, nbinsx: Math.min(40, Math.ceil(Math.sqrt(nums.length))||10)});
            } else if(ctype === 'bar'){
                var counts = {};
                rows.forEach(function(r){
                    var k = r[state.xCol] == null ? '(null)' : String(r[state.xCol]);
                    counts[k] = (counts[k] || 0) + 1;
                });
                var labels = Object.keys(counts).slice(0, 20);
                traces.push({type:'bar', x: labels, y: labels.map(function(k){ return counts[k]; }), marker:{color:'#6366F1'}});
            } else if(ctype === 'scatter' && yc){
                layout.xaxis = {title: state.xCol};
                layout.yaxis = {title: state.yCol};
                if(state.colorCol){
                    var groups = {};
                    rows.forEach(function(r){
                        var x=numVal(r[state.xCol]), y=numVal(r[state.yCol]);
                        if(x===null || y===null) return;
                        var k = r[state.colorCol] == null ? '(null)' : String(r[state.colorCol]);
                        if(!groups[k]) groups[k] = {x:[], y:[]};
                        groups[k].x.push(x);
                        groups[k].y.push(y);
                    });
                    Object.keys(groups).slice(0, 12).forEach(function(k, i){
                        traces.push({
                            type:'scatter', mode:'markers', name: k,
                            x: groups[k].x, y: groups[k].y,
                            marker:{size:8, color: colorForGroup(k, i), opacity:0.75}
                        });
                    });
                    layout.showlegend = true;
                } else {
                    var xs=[], ys=[];
                    rows.forEach(function(r){
                        var x=numVal(r[state.xCol]), y=numVal(r[state.yCol]);
                        if(x!==null && y!==null){ xs.push(x); ys.push(y); }
                    });
                    traces.push({type:'scatter', mode:'markers', x:xs, y:ys, marker:{size:8, color:'#6366F1', opacity:0.65}});
                }
            } else if(ctype === 'box'){
                var catCol = (xc.type === 'categorical' || xc.type === 'boolean') ? state.xCol : state.yCol;
                var numCol = catCol === state.xCol ? state.yCol : state.xCol;
                var groups = {};
                rows.forEach(function(r){
                    var k = r[catCol] == null ? '(null)' : String(r[catCol]);
                    var v = numVal(r[numCol]);
                    if(v === null) return;
                    if(!groups[k]) groups[k] = [];
                    groups[k].push(v);
                });
                Object.keys(groups).slice(0, 15).forEach(function(k){
                    traces.push({type:'box', y: groups[k], name: k, boxpoints: 'outliers'});
                });
                layout.yaxis = {title: numCol};
            } else if(ctype === 'pie'){
                var pc = {};
                rows.forEach(function(r){
                    var k = r[state.xCol] == null ? '(null)' : String(r[state.xCol]);
                    pc[k] = (pc[k] || 0) + 1;
                });
                var pl = Object.keys(pc).slice(0, 12);
                traces.push({type:'pie', labels: pl, values: pl.map(function(k){ return pc[k]; }), hole: 0.45});
            } else if(ctype === 'line'){
                var series = {};
                rows.forEach(function(r){
                    var k = r[state.xCol];
                    if(!k) return;
                    series[k] = (series[k] || 0) + 1;
                });
                var keys = Object.keys(series).sort().slice(0, 200);
                traces.push({type:'scatter', mode:'lines+markers', x: keys, y: keys.map(function(k){ return series[k]; }), line:{color:'#6366F1', width:2}});
            }

            if(!traces.length){
                target.innerHTML = '<div style="padding:60px;text-align:center;color:var(--text-secondary)">No data to chart with current filters</div>';
                state.chartReady = false;
                return;
            }
            Plotly.newPlot(target, traces, layout, {responsive:true, displaylogo:false});
            state.chartReady = true;
        }

        function sortRows(rows){
            if(!state.sortCol) return rows;
            var col = state.sortCol;
            var dir = state.sortDir === 'desc' ? -1 : 1;
            var cm = colMeta(col);
            return rows.slice().sort(function(a, b){
                var av = a[col], bv = b[col];
                if(av === null || av === undefined || av === '') return 1;
                if(bv === null || bv === undefined || bv === '') return -1;
                if(cm.type === 'numeric'){
                    return (numVal(av) - numVal(bv)) * dir;
                }
                return String(av).localeCompare(String(bv), undefined, {numeric:true, sensitivity:'base'}) * dir;
            });
        }

        function renderTable(rows){
            var wrap = document.getElementById('dm-exp-table-wrap');
            if(!wrap) return;
            rows = sortRows(rows);
            var cols = state.visibleCols;
            var totalPages = Math.max(1, Math.ceil(rows.length / state.pageSize));
            state.page = Math.min(state.page, totalPages - 1);
            var start = state.page * state.pageSize;
            var slice = rows.slice(start, start + state.pageSize);
            var html = '<table class="dm-table dm-table-sortable"><thead><tr>';
            cols.forEach(function(c){
                var mark = state.sortCol === c ? (state.sortDir === 'asc' ? ' ▲' : ' ▼') : '';
                html += '<th data-sort="' + c + '" style="cursor:pointer" title="Sort by ' + c + '">' + c + mark + '</th>';
            });
            html += '</tr></thead><tbody>';
            slice.forEach(function(r){
                html += '<tr>';
                cols.forEach(function(c){
                    var v = r[c];
                    html += '<td>' + (v === null || v === undefined ? '—' : String(v)) + '</td>';
                });
                html += '</tr>';
            });
            html += '</tbody></table>';
            wrap.innerHTML = html;
            wrap.querySelectorAll('th[data-sort]').forEach(function(th){
                th.addEventListener('click', function(){
                    var col = th.dataset.sort;
                    if(state.sortCol === col){
                        state.sortDir = state.sortDir === 'asc' ? 'desc' : 'asc';
                    } else {
                        state.sortCol = col;
                        state.sortDir = 'asc';
                    }
                    refresh();
                });
            });
            var info = document.getElementById('dm-exp-page-info');
            if(info) info.textContent = 'Page ' + (state.page + 1) + ' of ' + totalPages;
        }

        function refresh(){
            var rows = applyFilters();
            renderStats(rows);
            renderProfile(rows, state.xCol);
            renderChart(rows);
            renderTable(rows);
        }

        function resetFilters(){
            state.globalSearch = '';
            state.missingOnly = {};
            state.boolFilter = {};
            state.page = 0;
            payload.columns.forEach(function(c){
                if(c.type === 'numeric' && c.min != null){
                    state.numericRanges[c.name] = {min: c.min, max: c.max};
                }
                if(c.values) state.catSelections[c.name] = c.values.map(function(v){ return v.label; });
            });
            var search = document.getElementById('dm-exp-search');
            if(search) search.value = '';
            buildFilterPanel();
            refresh();
        }

        function downloadCsv(rows){
            var cols = state.visibleCols;
            var lines = [cols.join(',')];
            rows.forEach(function(r){
                lines.push(cols.map(function(c){
                    var v = r[c];
                    if(v === null || v === undefined) return '';
                    var s = String(v).replace(/"/g, '""');
                    return s.indexOf(',') >= 0 || s.indexOf('"') >= 0 ? '"' + s + '"' : s;
                }).join(','));
            });
            var blob = new Blob([lines.join('\n')], {type:'text/csv;charset=utf-8;'});
            var a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = 'datamatrix_filtered.csv';
            a.click();
        }

        buildFilterPanel();
        buildColumnChecks();
        fillSelects();

        var search = document.getElementById('dm-exp-search');
        if(search) search.addEventListener('input', function(){ state.globalSearch = search.value; state.page = 0; refresh(); });
        ['dm-exp-x','dm-exp-y','dm-exp-color','dm-exp-chart-type'].forEach(function(id){
            var el = document.getElementById(id);
            if(!el) return;
            el.addEventListener('change', function(){
                if(id === 'dm-exp-x') state.xCol = el.value;
                if(id === 'dm-exp-y') state.yCol = el.value;
                if(id === 'dm-exp-color') state.colorCol = el.value;
                if(id === 'dm-exp-chart-type') state.chartType = el.value;
                refresh();
            });
        });
        var resetBtn = document.getElementById('dm-exp-reset');
        if(resetBtn) resetBtn.addEventListener('click', resetFilters);
        var dl = document.getElementById('dm-exp-download');
        if(dl) dl.addEventListener('click', function(){ downloadCsv(applyFilters()); });
        var prev = document.getElementById('dm-exp-prev');
        var next = document.getElementById('dm-exp-next');
        if(prev) prev.addEventListener('click', function(){ if(state.page>0){ state.page--; refresh(); }});
        if(next) next.addEventListener('click', function(){
            var rows = applyFilters();
            var total = Math.ceil(rows.length / state.pageSize);
            if(state.page < total - 1){ state.page++; refresh(); }
        });

        window.dmRefreshExplorer = function(){
            refresh();
            var chart = document.getElementById('dm-explorer-chart');
            if(chart && state.chartReady && window.Plotly) Plotly.Plots.resize(chart);
        };

        refresh();
    })();
    """
