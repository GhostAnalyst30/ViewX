from __future__ import annotations

from .explorer_runtime import datamatrix_explorer_js


def html_modal_runtime_js() -> str:
    return """
    (function(){
        function closeModal(el){ if(el) el.classList.remove('open'); }
        document.addEventListener('keydown', function(e){
            if(e.key !== 'Escape') return;
            document.querySelectorAll('.vx-modal-overlay.open').forEach(function(m){
                m.classList.remove('open');
            });
        });
        window.vxOpenModal = function(id){
            var m = document.getElementById(id);
            if(m) m.classList.add('open');
        };
        window.vxCloseModal = function(id){
            closeModal(document.getElementById(id));
        };
        document.querySelectorAll('.vx-modal-overlay').forEach(function(overlay){
            overlay.addEventListener('click', function(e){
                if(e.target === overlay) overlay.classList.remove('open');
            });
        });
        var search = document.getElementById('vx-data-search');
        if(search){
            search.addEventListener('input', function(){
                var q = search.value.toLowerCase();
                document.querySelectorAll('.vx-prev-tbl tbody tr').forEach(function(row){
                    row.style.display = row.textContent.toLowerCase().indexOf(q) >= 0 ? '' : 'none';
                });
            });
        }
    })();
    """


def html_table_sort_js() -> str:
    return """
    (function(){
        document.querySelectorAll('.vx-sortable-table').forEach(function(table){
            table.querySelectorAll('th').forEach(function(th, colIdx){
                th.style.cursor = 'pointer';
                th.title = 'Click to sort';
                th.addEventListener('click', function(){
                    var tbody = table.querySelector('tbody');
                    if(!tbody) return;
                    var rows = Array.from(tbody.querySelectorAll('tr'));
                    var asc = th.dataset.sortDir !== 'asc';
                    table.querySelectorAll('th').forEach(function(h){ delete h.dataset.sortDir; });
                    th.dataset.sortDir = asc ? 'asc' : 'desc';
                    rows.sort(function(a, b){
                        var av = (a.children[colIdx] || {}).textContent || '';
                        var bv = (b.children[colIdx] || {}).textContent || '';
                        var an = parseFloat(av.replace(/[^0-9.-]/g, ''));
                        var bn = parseFloat(bv.replace(/[^0-9.-]/g, ''));
                        var cmp = (!isNaN(an) && !isNaN(bn)) ? (an - bn) : av.localeCompare(bv);
                        return asc ? cmp : -cmp;
                    });
                    rows.forEach(function(r){ tbody.appendChild(r); });
                });
            });
        });
    })();
    """


def html_plotly_resize_js(container_class: str) -> str:
    return f"""
    (function(){{
        var cont = document.querySelector('.{container_class}');
        var t;
        function resize(){{
            var d = cont ? cont.querySelector('.plotly-graph-div') : null;
            if(d && window.Plotly){{
                var w = cont.clientWidth, h = cont.clientHeight;
                if(w>0&&h>0) Plotly.relayout(d,{{width:w,height:h}});
            }}
        }}
        if(window.ResizeObserver && cont)
            new ResizeObserver(function(){{clearTimeout(t);t=setTimeout(resize,50);}}).observe(cont);
        window.addEventListener('resize',function(){{clearTimeout(t);t=setTimeout(resize,100);}});
        (function wait(n){{
            var d=cont?cont.querySelector('.plotly-graph-div'):null;
            if(d&&window.Plotly) resize();
            else if(n>0) setTimeout(function(){{wait(n-1);}},120);
        }})(18);
    }})();
    """


def datamatrix_runtime_js() -> str:
    return """
    function switchTab(name, btn) {
        document.querySelectorAll('.dm-tab').forEach(function(t){ t.classList.remove('active'); });
        document.querySelectorAll('.nav-btn').forEach(function(b){ b.classList.remove('active'); });
        var tab = document.getElementById('tab-' + name);
        if(tab) tab.classList.add('active');
        if(btn) btn.classList.add('active');
        if(window.location.hash !== '#' + name) history.replaceState(null, '', '#' + name);

        if(window.innerWidth <= 768) {
            document.getElementById('dmSidebar').classList.remove('open');
            document.getElementById('dmOverlay').classList.remove('open');
        }

        setTimeout(function(){
            document.querySelectorAll('.js-plotly-plot').forEach(function(el){
                if(window.Plotly) Plotly.Plots.resize(el);
            });
            if(name === 'explore' && window.dmRefreshExplorer) window.dmRefreshExplorer();
        }, 300);
    }

    function toggleSidebar() {
        document.getElementById('dmSidebar').classList.toggle('open');
        document.getElementById('dmOverlay').classList.toggle('open');
    }

    function dmLoadLazyPlot(item) {
        var plot = item.querySelector('.dm-lazy-plot');
        if(!plot || plot.dataset.loaded === '1') return;
        var tplId = plot.dataset.tpl;
        var tpl = tplId ? document.getElementById(tplId) : null;
        if(tpl) {
            plot.innerHTML = tpl.innerHTML;
            plot.dataset.loaded = '1';
            var graph = plot.querySelector('.js-plotly-plot');
            if(graph && window.Plotly) Plotly.Plots.resize(graph);
        }
    }

    document.querySelectorAll('.dm-col-header').forEach(function(h){
        h.addEventListener('click', function(){
            var item = h.parentElement;
            item.classList.toggle('open');
            if(item.classList.contains('open')) dmLoadLazyPlot(item);
        });
    });

    var colSearch = document.getElementById('dm-col-search');
    if(colSearch) {
        colSearch.addEventListener('input', function(){
            var q = colSearch.value.toLowerCase();
            document.querySelectorAll('.dm-col-item').forEach(function(item){
                var name = (item.dataset.col || '').toLowerCase();
                item.style.display = name.indexOf(q) >= 0 ? '' : 'none';
            });
            document.querySelectorAll('#dm-summary-table tbody tr').forEach(function(row){
                var name = (row.dataset.col || '').toLowerCase();
                row.style.display = name.indexOf(q) >= 0 ? '' : 'none';
            });
        });
    }

    var expandBtn = document.getElementById('dm-expand-all');
    if(expandBtn) {
        expandBtn.addEventListener('click', function(){
            var open = expandBtn.dataset.state !== 'open';
            expandBtn.dataset.state = open ? 'open' : 'closed';
            expandBtn.textContent = open ? 'Collapse all' : 'Expand all';
            document.querySelectorAll('.dm-col-item').forEach(function(item){
                item.classList.toggle('open', open);
                if(open) dmLoadLazyPlot(item);
            });
        });
    }

    var alertsToggle = document.getElementById('dm-alerts-toggle');
    if(alertsToggle) {
        alertsToggle.addEventListener('click', function(){
            var extra = document.getElementById('dm-alerts-extra');
            if(extra) {
                var show = extra.style.display === 'none';
                extra.style.display = show ? 'block' : 'none';
                alertsToggle.textContent = show ? 'Show less' : 'Show all (' + extra.dataset.count + ' more)';
            }
        });
    }

    var highlightsToggle = document.getElementById('dm-highlights-toggle');
    if(highlightsToggle) {
        highlightsToggle.addEventListener('click', function(){
            var extra = document.getElementById('dm-highlights-extra');
            if(extra) {
                var show = extra.style.display === 'none';
                extra.style.display = show ? 'block' : 'none';
                highlightsToggle.textContent = show ? 'Show less' : 'Show all (' + (extra.children.length) + ' more)';
            }
        });
    }

    (function initSamplePagination(){
        var table = document.getElementById('dm-sample-table');
        if(!table) return;
        var tbody = table.querySelector('tbody');
        if(!tbody) return;
        var rows = Array.from(tbody.querySelectorAll('tr'));
        var pageSize = 20;
        var page = 0;
        var info = document.getElementById('dm-sample-page-info');
        var prev = document.getElementById('dm-sample-prev');
        var next = document.getElementById('dm-sample-next');

        function render(){
            var total = Math.max(1, Math.ceil(rows.length / pageSize));
            page = Math.min(page, total - 1);
            rows.forEach(function(r, i){
                r.style.display = (i >= page * pageSize && i < (page + 1) * pageSize) ? '' : 'none';
            });
            if(info) info.textContent = 'Page ' + (page + 1) + ' of ' + total;
        }
        if(prev) prev.addEventListener('click', function(){ if(page > 0){ page--; render(); }});
        if(next) next.addEventListener('click', function(){
            var total = Math.ceil(rows.length / pageSize);
            if(page < total - 1){ page++; render(); }
        });
        render();
    })();

    (function initHashTab(){
        var hash = (window.location.hash || '').replace('#', '');
        if(!hash) return;
        var btn = document.querySelector('.nav-btn[data-tab="' + hash + '"]');
        if(btn) switchTab(hash, btn);
    })();

    document.addEventListener('keydown', function(e){
        if(e.key === 'Escape') {
            document.getElementById('dmSidebar').classList.remove('open');
            document.getElementById('dmOverlay').classList.remove('open');
        }
    });
    """ + datamatrix_explorer_js()
