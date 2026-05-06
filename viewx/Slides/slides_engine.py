import os
import webbrowser
import random

# ─────────────────────────────────────────────
#  KEYFRAMES Y ANIMACIONES CSS
# ─────────────────────────────────────────────

KEYFRAMES = """
@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}

@keyframes slideInLeft {
  from { opacity: 0; --tx: -80px; }
  to   { opacity: 1; --tx: 0px; }
}

@keyframes slideInRight {
  from { opacity: 0; --tx: 80px; }
  to   { opacity: 1; --tx: 0px; }
}

@keyframes slideInUp {
  from { opacity: 0; --ty: 60px; }
  to   { opacity: 1; --ty: 0px; }
}

@keyframes slideInDown {
  from { opacity: 0; --ty: -60px; }
  to   { opacity: 1; --ty: 0px; }
}

@keyframes zoomIn {
  from { opacity: 0; --scale: 0.5; }
  to   { opacity: 1; --scale: 1; }
}

@keyframes zoomOut {
  from { opacity: 0; --scale: 1.5; }
  to   { opacity: 1; --scale: 1; }
}

@keyframes bounce {
  0%   { opacity: 0; --ty: 0px; }
  40%  { --ty: -20px; }
  60%  { --ty: 5px; }
  80%  { --ty: -8px; }
  100% { opacity: 1; --ty: 0px; }
}

@keyframes flip {
  from { opacity: 0; --rot: -90deg; }
  to   { opacity: 1; --rot: 0deg; }
}

@keyframes spin {
  from { opacity: 0; --rot: -180deg; --scale: 0.5; }
  to   { opacity: 1; --rot: 0deg; --scale: 1; }
}

@keyframes shake {
  0%   { --tx: 0px; }
  20%  { --tx: -10px; }
  40%  { --tx: 10px; }
  60%  { --tx: -6px; }
  80%  { --tx: 6px; }
  100% { opacity: 1; --tx: 0px; }
}

@keyframes pulse {
  0%,100% { --scale: 1; opacity: 1; }
  50%     { --scale: 1.2; opacity: 0.85; }
}

@keyframes glow {
  0%,100% { text-shadow: 0 0 5px currentColor; }
  50%     { text-shadow: 0 0 20px currentColor, 0 0 40px currentColor; }
}

@keyframes float {
  0%,100% { --ty: 0px; }
  50%     { --ty: -15px; }
}

@keyframes floatX {
  0%,100% { --tx: 0px; }
  50%     { --tx: -15px; }
}

@keyframes colorShift {
  from { filter: hue-rotate(0deg); }
  to   { filter: hue-rotate(360deg); }
}

@keyframes morphShape {
  0%   { border-radius: 0%; }
  50%  { border-radius: 50%; }
  100% { border-radius: 0%; }
}

@keyframes blink-caret {
  50% { border-color: transparent; }
}

@keyframes rotate {
  from { --rot: 0deg; }
  to   { --rot: 360deg; }
}

@keyframes rotate-reverse {
  from { --rot: 360deg; }
  to   { --rot: 0deg; }
}

@keyframes swing {
  0%,100% { --rot: -10deg; }
  50%     { --rot: 10deg; }
}

@keyframes wiggle {
  0%,100% { --tx: 0px; }
  25%     { --tx: -8px; }
  75%     { --tx: 8px; }
}

@keyframes bounceX {
  0%,100% { --tx: 0px; }
  50%     { --tx: 40px; }
}

@keyframes bounceY {
  0%,100% { --ty: 0px; }
  50%     { --ty: 40px; }
}

/* ⚠️ orbit se deja con transform completo porque es especial */
@keyframes orbit {
  0%   { transform: rotate(0deg) translateX(100px) rotate(0deg); }
  100% { transform: rotate(360deg) translateX(100px) rotate(-360deg); }
}

@keyframes drift {
  0%   { --tx: 0px;   --ty: 0px; }
  25%  { --tx: 30px;  --ty: -20px; }
  50%  { --tx: -20px; --ty: 30px; }
  75%  { --tx: 20px;  --ty: 15px; }
  100% { --tx: 0px;   --ty: 0px; }
}

@keyframes wave {
  0%,100% { --ty: 0px; }
  50%     { --ty: -30px; }
}

@keyframes heartbeat {
  0%,100% { --scale: 1; }
  50%     { --scale: 1.3; }
}

@keyframes flash {
  0%,100% { opacity: 1; }
  50%     { opacity: 0.3; }
}

@keyframes slideLeft {
  from { --tx: 0px; }
  to   { --tx: -100%; }
}

@keyframes slideRight {
  from { --tx: 0px; }
  to   { --tx: 100%; }
}

/* Extras */

@keyframes growBar {
  from { width: 0%; }
  to   { width: var(--target-width, 100%); }
}

@keyframes slideInFromLeft {
  from { opacity: 0; --tx: -100px; }
  to   { opacity: 1; --tx: 0px; }
}

@keyframes slideInFromRight {
  from { opacity: 0; --tx: 100px; }
  to   { opacity: 1; --tx: 0px; }
}

@keyframes slideInFromTop {
  from { opacity: 0; --ty: -100px; }
  to   { opacity: 1; --ty: 0px; }
}

@keyframes slideInFromBottom {
  from { opacity: 0; --ty: 100px; }
  to   { opacity: 1; --ty: 0px; }
}

@keyframes rotate360 {
  from { --rot: 0deg; }
  to   { --rot: 360deg; }
}

@keyframes shimmer {
  from { background-position: -200% 0; }
  to   { background-position: 200% 0; }
}
"""

TRANSITION_CSS = {
    "fade": {
        "js": """
            slides[old].style.opacity='0';
            slides[old].style.transition='opacity 0.5s ease';
            slides[cur].classList.add('active');
            slides[cur].style.opacity='0';
            setTimeout(()=>{ slides[cur].style.opacity='1'; }, 50);
            setTimeout(()=>{ 
                slides[old].classList.remove('active');
                slides[old].style.opacity='';
                slides[old].style.transition='';
            }, 500);
        """
    },
    "slide": {
        "js": """
            slides[old].style.transform='translateX(-100%)';
            slides[old].style.transition='transform 0.4s ease';
            slides[cur].classList.add('active');
            slides[cur].style.transform='translateX(100%)';
            slides[cur].style.transition='none';
            setTimeout(()=>{
                slides[cur].style.transition='transform 0.4s ease';
                slides[cur].style.transform='translateX(0)';
            }, 50);
            setTimeout(()=>{
                slides[old].classList.remove('active');
                slides[old].style.transform='';
                slides[old].style.transition='';
            }, 450);
        """
    },
    "zoom": {
        "js": """
            slides[old].style.transform='scale(1.1)';
            slides[old].style.opacity='0';
            slides[old].style.transition='transform 0.4s ease, opacity 0.4s ease';
            slides[cur].classList.add('active');
            slides[cur].style.transform='scale(0.9)';
            slides[cur].style.opacity='0';
            slides[cur].style.transition='none';
            setTimeout(()=>{
                slides[cur].style.transition='transform 0.4s ease, opacity 0.4s ease';
                slides[cur].style.transform='scale(1)';
                slides[cur].style.opacity='1';
            }, 50);
            setTimeout(()=>{
                slides[old].classList.remove('active');
                slides[old].style.transform='';
                slides[old].style.opacity='';
                slides[old].style.transition='';
            }, 450);
        """
    },
    "none": {"js": "slides[old].classList.remove('active'); slides[cur].classList.add('active');"}
}

# ─────────────────────────────────────────────
#  TEMAS
# ─────────────────────────────────────────────

THEMES = {
    "dark": {
        "bg": "#0f0f1a", "surface": "#1a1a2e", "primary": "#e94560",
        "accent": "#0f3460", "text": "#eaeaea", "muted": "#888",
        "font": "'Segoe UI', sans-serif", "border": "rgba(255,255,255,0.08)",
        "shadow": "rgba(0,0,0,0.5)", "code_bg": "rgba(0,0,0,0.55)", "code_text": "#b0f0b0",
    },
    "light": {
        "bg": "#f8f9fa", "surface": "#ffffff", "primary": "#4361ee",
        "accent": "#3f37c9", "text": "#212529", "muted": "#6c757d",
        "font": "'Inter', sans-serif", "border": "rgba(0,0,0,0.1)",
        "shadow": "rgba(0,0,0,0.15)", "code_bg": "#f0f0f0", "code_text": "#2d6a4f",
    },
    "neon": {
        "bg": "#0d0221", "surface": "#110132", "primary": "#00ff88",
        "accent": "#ff006e", "text": "#ffffff", "muted": "#aaaaff",
        "font": "'Courier New', monospace", "border": "rgba(0,255,136,0.2)",
        "shadow": "rgba(0,255,136,0.1)", "code_bg": "rgba(0,0,0,0.7)", "code_text": "#00ff88",
    },
    "sunset": {
        "bg": "#1a0533", "surface": "#2d1051", "primary": "#ff6b6b",
        "accent": "#ffd93d", "text": "#fff5e6", "muted": "#c9a2d4",
        "font": "'Georgia', serif", "border": "rgba(255,107,107,0.2)",
        "shadow": "rgba(0,0,0,0.4)", "code_bg": "rgba(0,0,0,0.4)", "code_text": "#ffd93d",
    },
    "ocean": {
        "bg": "#0a192f", "surface": "#112240", "primary": "#64ffda",
        "accent": "#48cae4", "text": "#ccd6f6", "muted": "#8892b0",
        "font": "'Helvetica Neue', sans-serif", "border": "rgba(100,255,218,0.15)",
        "shadow": "rgba(0,0,0,0.4)", "code_bg": "rgba(0,0,0,0.45)", "code_text": "#64ffda",
    },
    "corporate": {
        "bg": "#ffffff", "surface": "#f5f7ff", "primary": "#2563eb",
        "accent": "#7c3aed", "text": "#1e293b", "muted": "#64748b",
        "font": "'Arial', sans-serif", "border": "rgba(0,0,0,0.08)",
        "shadow": "rgba(0,0,0,0.1)", "code_bg": "#f1f5f9", "code_text": "#1e293b",
    },
    "retro": {
        "bg": "#2b1d0e", "surface": "#3d2b1f", "primary": "#f4a261",
        "accent": "#e76f51", "text": "#fdf0d5", "muted": "#c8b8a2",
        "font": "'Courier New', monospace", "border": "rgba(244,162,97,0.2)",
        "shadow": "rgba(0,0,0,0.5)", "code_bg": "rgba(0,0,0,0.4)", "code_text": "#f4a261",
    },
}

# ─────────────────────────────────────────────
#  PRESENTACIÓN
# ─────────────────────────────────────────────

class Presentation:
    slides = []
    current = None
    _theme = "dark"
    _bg_style = ""
    _music = ""
    _transition = "slide"
    _font_url = ""
    _font_name = ""
    _logo = ""
    _kiosk = False
    _timer = 0
    _show_nums = True
    _metadata = {}

    @classmethod
    def theme(cls, name: str):
        cls._theme = name
        return cls

    @classmethod
    def custom_theme(cls, **kwargs):
        THEMES["_custom"] = {**THEMES["dark"], **kwargs}
        cls._theme = "_custom"
        return cls

    @classmethod
    def background(cls, css: str):
        cls._bg_style = css
        return cls

    @classmethod
    def music(cls, url: str):
        cls._music = url
        return cls

    @classmethod
    def transition(cls, name: str):
        if name in TRANSITION_CSS:
            cls._transition = name
        return cls

    @classmethod
    def font(cls, name: str, weights="400;600;700"):
        cls._font_url = f"https://fonts.googleapis.com/css2?family={name.replace(' ', '+')}:wght@{weights}&display=swap"
        cls._font_name = f"'{name}', sans-serif"
        return cls

    @classmethod
    def logo(cls, url: str):
        cls._logo = url
        return cls

    @classmethod
    def kiosk(cls, value=True):
        cls._kiosk = value
        return cls

    @classmethod
    def auto_advance(cls, seconds: int):
        cls._timer = seconds
        return cls

    @classmethod
    def hide_numbers(cls):
        cls._show_nums = False
        return cls

    @classmethod
    def meta(cls, title="", author="", date=""):
        cls._metadata = {"title": title, "author": author, "date": date}
        return cls

    @classmethod
    def _get_theme(cls):
        return THEMES.get(cls._theme, THEMES["dark"])

    @classmethod
    def render_body(cls):
        return "".join(s._render() for s in cls.slides)

    @classmethod
    def export(cls, filename="presentacion.html"):
        t = cls._get_theme()
        body = cls.render_body()
        n = len(cls.slides)

        font_link = f'<link rel="stylesheet" href="{cls._font_url}">' if cls._font_url else ""
        font_var = cls._font_name if cls._font_name else t["font"]

        music_tag = f'<audio id="bgm" src="{cls._music}" loop autoplay style="display:none"></audio>' if cls._music else ""
        logo_tag = f'<img id="logo" src="{cls._logo}" style="position:fixed;top:16px;left:16px;height:36px;z-index:100;opacity:.85">' if cls._logo else ""
        bg_extra = f"background:{cls._bg_style};" if cls._bg_style else ""

        tr = TRANSITION_CSS.get(cls._transition, TRANSITION_CSS["slide"])
        transition_js = tr.get("js")
        auto_js = f"setInterval(()=>next(),{cls._timer*1000});" if cls._timer else ""

        dots_html = ''.join(f'<div class="dot{" active" if i==0 else ""}" onclick="goTo({i})" title="Slide {i+1}"></div>' for i in range(n))
        
        meta_bar = ""
        if cls._metadata:
            m = cls._metadata
            meta_bar = f'<div id="meta-bar"><span>{m.get("title","")}</span><span style="opacity:.5">|</span><span>{m.get("author","")}</span><span style="opacity:.5">{m.get("date","")}</span></div>'

        controls_html = "" if cls._kiosk else f"""
<div id="controls">
  <button onclick="prev()" title="←">&#8592;</button>
  <button onclick="toggleFullscreen()" title="F11">&#9974;</button>
  <span id="slide-counter">1 / {n}</span>
  <button onclick="toggleMute()" id="mute-btn" title="M">&#128266;</button>
  <button onclick="next()" title="→">&#8594;</button>
</div>"""

        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{cls._metadata.get('title','Presentación')}</title>
{font_link}
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
{KEYFRAMES}
:root{{
  --bg:{t['bg']};--surface:{t['surface']};--primary:{t['primary']};
  --accent:{t['accent']};--text:{t['text']};--muted:{t['muted']};
  --font:{font_var};--border:{t['border']};--shadow:{t['shadow']};
  --code-bg:{t['code_bg']};--code-text:{t['code_text']};
}}
html,body{{
  width:100%;height:100%;overflow:hidden;
  background:var(--bg);{bg_extra}
  color:var(--text);font-family:var(--font);
}}
#deck{{width:100%;height:100%;display:grid;grid-template:1fr/1fr;}}
section.slide{{
  grid-area:1/1;width:100%;height:100%;
  position:relative;overflow:auto;
  display:none;
}}
section.slide.active{{display:block;}}

#progress-bar{{position:fixed;top:0;left:0;height:3px;background:linear-gradient(90deg,var(--primary),var(--accent));transition:width .4s ease;z-index:200;}}
#controls{{position:fixed;bottom:12px;left:50%;transform:translateX(-50%);display:flex;align-items:center;gap:12px;z-index:100;background:rgba(0,0,0,.45);backdrop-filter:blur(10px);border:1px solid var(--border);border-radius:40px;padding:8px 20px;opacity:0;transition:opacity .3s;}}
body:hover #controls{{opacity:1;}}
#controls button{{background:none;border:none;color:var(--text);font-size:20px;cursor:pointer;padding:4px 8px;border-radius:50%;transition:background .2s,transform .15s;}}
#controls button:hover{{background:rgba(255,255,255,.12);transform:scale(1.12);}}
#slide-counter{{font-size:13px;color:var(--muted);min-width:50px;text-align:center;}}
#dots{{position:fixed;bottom:72px;left:50%;transform:translateX(-50%);display:flex;gap:7px;z-index:100;opacity:0;transition:opacity .3s;}}
body:hover #dots{{opacity:1;}}
.dot{{width:7px;height:7px;border-radius:50%;background:rgba(255,255,255,.25);cursor:pointer;transition:background .25s,transform .25s,width .25s;}}
.dot.active{{background:var(--primary);transform:scale(1.2);width:20px;border-radius:4px;}}
#meta-bar{{position:fixed;bottom:0;left:0;right:0;display:flex;gap:12px;align-items:center;padding:6px 20px;font-size:11px;color:var(--muted);z-index:100;background:rgba(0,0,0,.2);backdrop-filter:blur(4px);}}
.slide-number{{position:absolute;bottom:32px;right:20px;font-size:16px;color:var(--muted);opacity:.5;z-index:10;}}
#shortcuts{{position:fixed;top:18px;right:{('24px' if not cls._logo else '80px')};font-size:10px;color:var(--muted);z-index:100;opacity:0;transition:opacity .3s;}}
body:hover #shortcuts{{opacity:.7;}}
.c-component{{
  position:absolute;
  white-space:normal;
  word-wrap:break-word;
}}
.code-block{{background:var(--code-bg);border:1px solid var(--border);border-radius:10px;padding:18px 22px;font-family:'Courier New',monospace;font-size:14px;line-height:1.7;color:var(--code-text);white-space:pre;overflow:auto;}}
.code-block .line-numbers{{color:var(--muted);user-select:none;margin-right:16px;opacity:.5;}}
.c-card{{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:24px;box-shadow:0 8px 32px var(--shadow);}}
.c-badge{{display:inline-block;padding:4px 12px;border-radius:99px;background:var(--primary);color:#fff;font-size:13px;font-weight:600;}}
.c-divider{{height:2px;background:linear-gradient(90deg,transparent,var(--primary),transparent);border:none;}}
.progress-ring-text{{fill:var(--text);font-family:var(--font);}}
.c-tooltip{{position:relative;display:inline-block;cursor:help;}}
.c-tooltip .tooltip-text{{visibility:hidden;opacity:0;background:var(--surface);color:var(--text);border:1px solid var(--border);border-radius:8px;padding:8px 12px;font-size:13px;position:absolute;bottom:125%;left:50%;transform:translateX(-50%);white-space:nowrap;z-index:999;transition:opacity .2s;box-shadow:0 4px 16px var(--shadow);}}
.c-tooltip:hover .tooltip-text{{visibility:visible;opacity:1;}}
.c-quote{{border-left:4px solid var(--primary);padding:16px 24px;background:var(--surface);border-radius:0 12px 12px 0;}}
.c-quote blockquote{{font-size:20px;font-style:italic;line-height:1.6;}}
.c-quote cite{{font-size:13px;color:var(--muted);margin-top:8px;display:block;}}
.c-table{{border-collapse:collapse;width:100%;}}
.c-table th{{background:var(--primary);color:#fff;padding:12px 16px;text-align:left;font-size:14px;}}
.c-table td{{padding:10px 16px;font-size:14px;border-bottom:1px solid var(--border);}}
.c-table tr:hover td{{background:var(--surface);}}
.c-timeline{{list-style:none;position:relative;padding-left:32px;}}
.c-timeline::before{{content:'';position:absolute;left:10px;top:0;bottom:0;width:2px;background:var(--border);}}
.c-timeline li{{position:relative;margin-bottom:24px;}}
.c-timeline li::before{{content:'';position:absolute;left:-26px;top:4px;width:12px;height:12px;border-radius:50%;background:var(--primary);border:2px solid var(--bg);box-shadow:0 0 8px var(--primary);}}
.c-timeline .tl-year{{font-size:12px;color:var(--muted);margin-bottom:4px;}}
.c-timeline .tl-title{{font-weight:700;font-size:16px;}}
.c-timeline .tl-desc{{font-size:14px;color:var(--muted);margin-top:4px;line-height:1.5;}}
.c-iconstat{{text-align:center;}}
.c-iconstat .stat-icon{{font-size:36px;margin-bottom:8px;display:block;}}
.c-iconstat .stat-value{{font-size:42px;font-weight:800;color:var(--primary);}}
.c-iconstat .stat-label{{font-size:14px;color:var(--muted);margin-top:4px;}}
.c-columns{{display:grid;gap:24px;width:100%;}}
#notes-panel{{display:none;position:fixed;bottom:0;left:0;right:0;background:rgba(0,0,0,.92);color:#fff;padding:20px;font-size:14px;line-height:1.6;z-index:999;border-top:2px solid var(--primary);max-height:35vh;overflow-y:auto;}}
#notes-panel.visible{{display:block;}}
.c-chart-bar{{background:var(--surface);border-radius:12px;padding:20px;}}
.c-chart-bar .bar-row{{display:flex;align-items:center;gap:12px;margin-bottom:12px;}}
.c-chart-bar .bar-label{{font-size:13px;width:100px;flex-shrink:0;color:var(--muted);}}
.c-chart-bar .bar-track{{flex:1;background:var(--border);border-radius:99px;height:20px;overflow:hidden;}}
.c-chart-bar .bar-fill{{height:100%;border-radius:99px;background:var(--primary);transition:width 0.8s ease;}}
.c-chart-bar .bar-value{{font-size:13px;font-weight:700;min-width:40px;text-align:right;color:var(--text);}}
</style>
</head>
<body>
{music_tag}
{logo_tag}
<div id="progress-bar" style="width:0%"></div>
<div id="dots">{dots_html}</div>
<div id="shortcuts">← → Space · F fullscreen · N notas · M mute</div>
<div id="deck">{body}</div>
{controls_html}
{meta_bar}
<div id="notes-panel"></div>
<script>
let cur=0, old=0, total={n}, muted=false, notesVisible=false;
const slides=document.querySelectorAll('.slide');
const dots=document.querySelectorAll('.dot');
const counter=document.getElementById('slide-counter');
const bar=document.getElementById('progress-bar');
const bgm=document.getElementById('bgm');
const notesPanel=document.getElementById('notes-panel');

// Función para reiniciar y mantener animaciones
function restartAnimations(slide) {{
    if(!slide) return;
    // Encontrar todos los elementos con animación
    const animatedElements = slide.querySelectorAll('[style*="animation:"]');
    animatedElements.forEach(el => {{
        // Guardar la animación original
        const originalAnimation = el.style.animation;
        if(originalAnimation && originalAnimation !== 'none') {{
            // Reiniciar la animación
            el.style.animation = 'none';
            // Forzar reflow
            void el.offsetHeight;
            // Restaurar la animación
            el.style.animation = originalAnimation;
        }}
    }});
}}

function goTo(n){{
  if(n<0||n>=total)return;
  if(n===cur)return;
  old=cur; cur=n;
  
  // Aplicar transición
  {transition_js}
  
  // Actualizar UI
  dots.forEach(d=>d.classList.remove('active'));
  if(dots[cur]) dots[cur].classList.add('active');
  if(counter)counter.textContent=(cur+1)+' / '+total;
  if(bar)bar.style.width=((cur+1)/total*100)+'%';
  
  // Reiniciar animaciones después de la transición
  setTimeout(() => {{
    restartAnimations(slides[cur]);
  }}, 100);
  
  if(notesVisible && notesPanel){{
    notesPanel.innerHTML=speakerNotes[cur]||'<em style="opacity:.4">Sin notas.</em>';
  }}
}}

function next(){{ if(cur<total-1) goTo(cur+1); }}
function prev(){{ if(cur>0) goTo(cur-1); }}
function toggleFullscreen(){{
  if(!document.fullscreenElement) document.documentElement.requestFullscreen();
  else document.exitFullscreen();
}}
function toggleMute(){{
  muted=!muted;
  if(bgm) bgm.muted=muted;
  const btn=document.getElementById('mute-btn');
  if(btn) btn.innerHTML=muted?'&#128267;':'&#128266;';
}}
function toggleNotes(){{
  notesVisible=!notesVisible;
  if(notesPanel){{
    notesPanel.classList.toggle('visible',notesVisible);
    notesPanel.innerHTML=speakerNotes[cur]||'<em style="opacity:.4">Sin notas.</em>';
  }}
}}

document.addEventListener('keydown',e=>{{
  if(e.target.tagName==='INPUT'||e.target.tagName==='TEXTAREA')return;
  if(e.key==='ArrowRight'||e.key===' ') next();
  if(e.key==='ArrowLeft') prev();
  if(e.key.toLowerCase()==='f') toggleFullscreen();
  if(e.key.toLowerCase()==='m') toggleMute();
  if(e.key.toLowerCase()==='n') toggleNotes();
  if(e.key==='Home') goTo(0);
  if(e.key==='End') goTo(total-1);
}});

let tx=0;
document.addEventListener('touchstart',e=>{{ tx=e.touches[0].clientX; }});
document.addEventListener('touchend',e=>{{
  if(e.changedTouches[0]){{
    const dx=e.changedTouches[0].clientX-tx;
    if(dx<-50) next(); else if(dx>50) prev();
  }}
}});

document.querySelectorAll('a[data-slide]').forEach(a=>{{
  a.addEventListener('click',e=>{{ e.preventDefault(); goTo(parseInt(a.dataset.slide)-1); }});
}});

function startCountUp(el){{
  const end=parseFloat(el.dataset.countEnd)||0;
  const dur=parseInt(el.dataset.countDur)||1500;
  const prefix=el.dataset.prefix||'';
  const suffix=el.dataset.suffix||'';
  const decimals=parseInt(el.dataset.decimals)||0;
  let start=Date.now();
  (function run(){{
    let t=Math.min((Date.now()-start)/dur,1);
    const ease=t<0.5?2*t*t:(1-Math.pow(-2*t+2,2)/2);
    const v=(end*ease).toFixed(decimals);
    el.textContent=prefix+v+suffix;
    if(t<1) requestAnimationFrame(run);
  }})();
}}

const countObs=new IntersectionObserver(entries=>{{
  entries.forEach(e=>{{ if(e.isIntersecting){{ startCountUp(e.target); countObs.unobserve(e.target); }} }});
}});
document.querySelectorAll('[data-count-end]').forEach(el=>countObs.observe(el));
{auto_js}

// Inicializar primera slide y mantener animaciones corriendo
setTimeout(()=>{{
  slides[0].classList.add('active');
  restartAnimations(slides[0]);
}}, 10);
</script>
</body>
</html>"""

        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✅ Exportado: {os.path.abspath(filename)}")
        return filename

    @classmethod
    def show(cls, filename="presentacion.html"):
        path = cls.export(filename)
        webbrowser.open("file://" + os.path.abspath(path))

    @classmethod
    def reset(cls):
        cls.slides = []
        cls.current = None
        cls._theme = "dark"
        cls._bg_style = ""
        cls._music = ""
        cls._transition = "slide"
        cls._font_url = ""
        cls._font_name = ""
        cls._logo = ""
        cls._kiosk = False
        cls._timer = 0
        cls._show_nums = True
        cls._metadata = {}


# ─────────────────────────────────────────────
#  SLIDE
# ─────────────────────────────────────────────

class Slide:
    def __init__(self, title="", index=1, bg="", overlay_opacity=0.0,
                 notes="", transition=None):
        self.title = title
        self.index = index
        self.elements = []
        self._bg = bg
        self._overlay = overlay_opacity
        self._notes = notes
        self._transition = transition

    def __enter__(self):
        Presentation.current = self
        return self

    def __exit__(self, *_):
        Presentation.slides.append(self)
        Presentation.current = None

    def _render(self):
        bg_style = ""
        overlay = ""
        if self._bg:
            if self._bg.startswith("http") or self._bg.startswith("/") or "." in self._bg:
                bg_style = f"background:url('{self._bg}') center/cover no-repeat;"
            else:
                bg_style = f"background:{self._bg};"
            if self._overlay > 0:
                overlay = f'<div style="position:absolute;inset:0;background:rgba(0,0,0,{self._overlay});z-index:0"></div>'

        notes_tag = f'<div data-notes="{self._notes}" style="display:none"></div>' if self._notes else ""
        num = f'<div class="slide-number">{self.index} / {len(Presentation.slides)+1}</div>' if Presentation._show_nums else ""

        body = "".join(el._render() for el in self.elements)
        return f'<section class="slide" id="slide-{self.index}" style="{bg_style}">{overlay}{notes_tag}{body}{num}</section>'


# ─────────────────────────────────────────────
#  SLIDES ESPECIALES
# ─────────────────────────────────────────────

class GradientSlide(Slide):
    def __init__(self, title, index, colors, direction="135deg", notes=""):
        bg = f"linear-gradient({direction},{','.join(colors)})"
        super().__init__(title, index, bg=bg, notes=notes)


class ParticleSlide(Slide):
    def __init__(self, title, index, particle_color=None, notes=""):
        super().__init__(title, index, notes=notes)
        self._pc = particle_color or "var(--primary)"

    def _render(self):
        particles = ""
        for _ in range(30):
            x = random.randint(0, 100)
            y = random.randint(0, 100)
            sz = random.randint(2, 8)
            dur = round(random.uniform(5, 12), 1)
            dly = round(random.uniform(0, 6), 1)
            op = round(random.uniform(0.08, 0.35), 2)
            particles += f'<div style="position:absolute;left:{x}%;top:{y}%;width:{sz}px;height:{sz}px;border-radius:50%;background:{self._pc};opacity:{op};animation:float {dur}s ease-in-out {dly}s infinite;z-index:0"></div>'
        notes_tag = f'<div data-notes="{self._notes}" style="display:none"></div>' if self._notes else ""
        body = "".join(el._render() for el in self.elements)
        return f'<section class="slide" id="slide-{self.index}">{particles}{notes_tag}{body}</section>'


class SplitSlide(Slide):
    def __init__(self, title, index, left_color=None, right_color=None, split=50, notes=""):
        super().__init__(title, index, notes=notes)
        self._lc = left_color or "var(--surface)"
        self._rc = right_color or "var(--bg)"
        self._split = split

    def _render(self):
        bg = f"linear-gradient(90deg, {self._lc} {self._split}%, {self._rc} {self._split}%)"
        notes_tag = f'<div data-notes="{self._notes}" style="display:none"></div>' if self._notes else ""
        body = "".join(el._render() for el in self.elements)
        return f'<section class="slide" id="slide-{self.index}" style="background:{bg}">{notes_tag}{body}</section>'


# ─────────────────────────────────────────────
#  COMPONENTE BASE
# ─────────────────────────────────────────────

class Component:
    def __init__(self):
        self.styles = {"position": "absolute"}
        self._anim = None
        self._delay = 0.0
        self._duration = 0.6
        self._easing = "ease"
        self._loop = False
        self._extra_cls = []
        self._onclick = ""
        self._tooltip = ""
        if Presentation.current:
            Presentation.current.elements.append(self)

    def pos(self, left=None, top=None, right=None, bottom=None, unit="%"):
        """Establece la posición del componente"""
        def fmt(v): return f"{v}{unit}" if isinstance(v, (int, float)) else v
        
        if left is not None: 
            self.styles["left"] = fmt(left)
        if top is not None: 
            self.styles["top"] = fmt(top)
        if right is not None: 
            self.styles["right"] = fmt(right)
        if bottom is not None: 
            self.styles["bottom"] = fmt(bottom)
        
        # Si estamos seteando posición y hay transform de centrado, ajustarlo
        if "transform" in self.styles and ("translateX(-50%)" in self.styles["transform"] or "translateY(-50%)" in self.styles["transform"]):
            # Mantener el centrado pero permitir posición
            current_transform = self.styles["transform"]
            if "translateX(-50%)" in current_transform and "translateY(-50%)" in current_transform:
                # Ya está centrado en ambos ejes, mantener
                pass
            elif "translateX(-50%)" in current_transform and top is not None:
                # Centrado en X pero Y específico
                self.styles["transform"] = "translateX(-50%)"
            elif "translateY(-50%)" in current_transform and left is not None:
                # Centrado en Y pero X específico
                self.styles["transform"] = "translateY(-50%)"
        
        return self

    def size(self, width=None, height=None):
        """Establece el tamaño del componente"""
        if width is not None: 
            self.styles["width"] = f"{width}px" if isinstance(width, int) else width
        if height is not None: 
            self.styles["height"] = f"{height}px" if isinstance(height, int) else height
        return self

    def center(self, axis="both"):
        """Centra el componente correctamente"""
        if axis in ("both", "x"): 
            self.styles["left"] = "50%"
        if axis in ("both", "y"): 
            self.styles["top"] = "50%"
        
        # Resetear transform completamente
        if axis == "both":
            self.styles["transform"] = "translate(-50%, -50%)"
        elif axis == "x":
            self.styles["transform"] = "translateX(-50%)"
        elif axis == "y":
            self.styles["transform"] = "translateY(-50%)"
        
        return self

    def z(self, value: int):
        self.styles["z-index"] = str(value)
        return self

    def opacity(self, value: float):
        self.styles["opacity"] = str(value)
        return self

    def onclick(self, js: str):
        self._onclick = js
        return self

    def tooltip(self, text: str):
        self._tooltip = text
        return self

    def border(self, color=None, width=1, radius=8):
        self.styles["border"] = f"{width}px solid {color or 'var(--primary)'}"
        self.styles["border-radius"] = f"{radius}px"
        return self

    def shadow(self, intensity="md"):
        shadows = {"sm": "0 2px 8px rgba(0,0,0,.2)", "md": "0 8px 24px rgba(0,0,0,.35)",
                   "lg": "0 16px 48px rgba(0,0,0,.5)", "glow": "0 0 30px var(--primary)"}
        self.styles["box-shadow"] = shadows.get(intensity, intensity)
        return self

    def fade_in(self, delay=0.0, duration=0.6):
        return self._set_anim("fadeIn", delay, duration)

    def slide_in(self, direction="left", delay=0.0, duration=0.6):
        anim = {"left": "slideInLeft", "right": "slideInRight",
                "up": "slideInUp", "down": "slideInDown"}.get(direction, "slideInLeft")
        return self._set_anim(anim, delay, duration)

    def zoom_in(self, delay=0.0, duration=0.6):
        return self._set_anim("zoomIn", delay, duration)

    def zoom_out(self, delay=0.0, duration=0.6):
        return self._set_anim("zoomOut", delay, duration)

    def bounce(self, delay=0.0, duration=0.8):
        return self._set_anim("bounce", delay, duration)

    def flip(self, delay=0.0, duration=0.7):
        return self._set_anim("flip", delay, duration)

    def spin(self, delay=0.0, duration=0.8):
        return self._set_anim("spin", delay, duration)

    def shake(self, delay=0.0, duration=0.6):
        return self._set_anim("shake", delay, duration)

    def pulse_loop(self):
        self._loop = True
        return self._set_anim("pulse", 0, 1.5)

    def float_loop(self):
        self._loop = True
        return self._set_anim("float", 0, 3.0)

    def glow_loop(self):
        self._loop = True
        return self._set_anim("glow", 0, 2.0)

    def color_shift_loop(self):
        self._loop = True
        return self._set_anim("colorShift", 0, 4.0)

    def morph_loop(self):
        self._loop = True
        return self._set_anim("morphShape", 0, 3.0)

    def rotate_loop(self, speed=3):
        self._loop = True
        return self._set_anim("rotate", 0, speed)

    def swing_loop(self):
        self._loop = True
        return self._set_anim("swing", 0, 1.5)

    def wiggle_loop(self):
        self._loop = True
        return self._set_anim("wiggle", 0, 0.3)

    def orbit_loop(self, speed=4):
        self._loop = True
        return self._set_anim("orbit", 0, speed)

    def drift_loop(self, speed=5):
        self._loop = True
        return self._set_anim("drift", 0, speed)

    def wave_loop(self):
        self._loop = True
        return self._set_anim("wave", 0, 2.0)

    def heartbeat_loop(self):
        self._loop = True
        return self._set_anim("heartbeat", 0, 1)

    def move_path(self, path_type="float", speed=2, delay=0):
        path_map = {"float": "float", "orbit": "orbit", "drift": "drift",
                    "wave": "wave", "bounce_x": "bounceX", "bounce_y": "bounceY",
                    "zigzag": "wiggle", "rotate": "rotate", "pulse": "pulse"}
        anim_name = path_map.get(path_type, "float")
        self._loop = True
        return self._set_anim(anim_name, delay, speed)
    
    def move_x(self, start=0, end=100, duration=2, loop=True):
        """Mueve el componente horizontalmente"""
        self._add_keyframe_animation(f"moveX-{id(self)}", 
                                    f"transform: translateX({start}px)",
                                    f"transform: translateX({end}px)")
        self._loop = loop
        return self._set_anim(f"moveX-{id(self)}", 0, duration)

    def move_y(self, start=0, end=100, duration=2, loop=True):
        """Mueve el componente verticalmente"""
        self._add_keyframe_animation(f"moveY-{id(self)}",
                                    f"transform: translateY({start}px)",
                                    f"transform: translateY({end}px)")
        self._loop = loop
        return self._set_anim(f"moveY-{id(self)}", 0, duration)

    def bounce_continuous(self, height=30, duration=0.8):
        """Rebote continuo"""
        self._add_keyframe_animation(f"bounce-{id(self)}",
                                    f"transform: translateY(0)",
                                    f"transform: translateY(-{height}px)",
                                    f"transform: translateY(0)")
        self._loop = True
        return self._set_anim(f"bounce-{id(self)}", 0, duration)

    def shake_continuous(self, intensity=10, duration=0.3):
        """Temblor continuo"""
        self._add_keyframe_animation(f"shake-{id(self)}",
                                    f"transform: translateX(0)",
                                    f"transform: translateX(-{intensity}px)",
                                    f"transform: translateX({intensity}px)",
                                    f"transform: translateX(0)")
        self._loop = True
        return self._set_anim(f"shake-{id(self)}", 0, duration)

    def _add_keyframe_animation(self, name, *keyframes):
        """Añade keyframes dinámicos al documento"""
        # Esto se manejará en el HTML generado
        if not hasattr(Presentation, '_dynamic_keyframes'):
            Presentation._dynamic_keyframes = {}
        
        steps = []
        step_size = 100 / (len(keyframes) - 1) if len(keyframes) > 1 else 100
        
        for i, kf in enumerate(keyframes):
            percent = i * step_size
            steps.append(f"{percent}% {{ {kf} }}")
        
        Presentation._dynamic_keyframes[name] = "\n".join(steps)

    def _set_anim(self, name, delay, duration, easing="ease"):
        self._anim = name
        self._delay = delay
        self._duration = duration
        self._easing = easing
        return self

    def _anim_style(self):
        if not self._anim:
            return ""
        iteration = "infinite" if self._loop else "1"
        return f"animation: {self._anim} {self._duration}s {self._easing} {self._delay}s {iteration} forwards;"

    def _render_style(self):
        """Genera el estilo CSS del componente respetando position y animaciones"""
        styles_list = []
        
        # Primero, aplicar todos los estilos normales
        for k, v in self.styles.items():
            if k != 'transform':  # Excluir transform por ahora
                styles_list.append(f"{k}:{v}")
        
        # Manejar el transform de posición
        pos_transform = self.styles.get('transform', '')
        
        # Añadir transform si existe (con su punto y coma)
        if pos_transform:
            styles_list.append(f"transform:{pos_transform}")
        
        # Manejar la animación
        if self._anim:
            iteration = "infinite" if self._loop else "1"
            fill_mode = "forwards" if not self._loop else "none"
            anim_css = f"animation: {self._anim} {self._duration}s {self._easing} {self._delay}s {iteration} {fill_mode}"
            styles_list.append(anim_css)
        
        # Unir todo con punto y coma
        return ";".join(styles_list) + ";"

    def _data_attrs(self):
        return ""

    def _wrap_tooltip(self, inner):
        if not self._tooltip:
            return inner
        return f'<span class="c-tooltip">{inner}<span class="tooltip-text">{self._tooltip}</span></span>'

    def _render(self):
        raise NotImplementedError


# ─────────────────────────────────────────────
#  COMPONENTES DE TEXTO
# ─────────────────────────────────────────────

class Title(Component):
    def __init__(self, text, color=None):
        super().__init__()
        self.text = text
        self._color = color
        self.styles.update({"font-size": "52px", "font-weight": "700",
                           "text-align": "center", "width": "80%"})

    def gradient_text(self, c1, c2, direction="135deg"):
        self.styles.update({"background": f"linear-gradient({direction},{c1},{c2})",
                           "-webkit-background-clip": "text",
                           "-webkit-text-fill-color": "transparent",
                           "background-clip": "text"})
        return self

    def size_px(self, px: int):
        self.styles["font-size"] = f"{px}px"
        return self

    def _render(self):
        c = f"color:{self._color};" if self._color else "color:var(--text);"
        style = self._render_style()
        # Asegurar que el estilo termina correctamente
        if not style.endswith(';'):
            style += ';'
        return self._wrap_tooltip(f'<h1 class="c-component" style="{style}{c}">{self.text}</h1>')


class Subtitle(Component):
    def __init__(self, text, color=None):
        super().__init__()
        self.text = text
        self.styles.update({"font-size": "26px", "font-weight": "300",
                           "text-align": "center", "width": "70%", "color": "var(--muted)"})
        if color:
            self.styles["color"] = color

    def _render(self):
        style = self._render_style()
        if not style.endswith(';'):
            style += ';'
        return self._wrap_tooltip(f'<p class="c-component" style="{style}">{self.text}</p>')


class Text(Component):
    def __init__(self, text, size=18, color=None):
        super().__init__()
        self.text = text
        if color:
            self.styles["color"] = color
        self.styles.update({"font-size": f"{size}px", "line-height": "1.6", "max-width": "70%"})

    def _render(self):
        style = self._render_style()
        if not style.endswith(';'):
            style += ';'
        return self._wrap_tooltip(f'<p class="c-component" style="{style}">{self.text}</p>')

class Quote(Component):
    def __init__(self, text, author="", color=None):
        super().__init__()
        self.text = text
        self.author = author
        self._color = color or "var(--primary)"
        self.styles.update({"width": "65%"})

    def _render(self):
        cite = f'<cite>— {self.author}</cite>' if self.author else ""
        return self._wrap_tooltip(f'<div class="c-component c-quote" style="{self._render_style()};border-color:{self._color}"><blockquote>{self.text}</blockquote>{cite}</div>')

class Shape(Component):
    """Forma geométrica decorativa con animaciones"""
    def __init__(self, kind="rect", w=100, h=100, color=None, opacity=1.0):
        super().__init__()
        self._kind = kind
        self._color = color or "var(--primary)"
        self._opacity = opacity
        self.styles.update({
            "width": f"{w}px", 
            "height": f"{h}px", 
            "background": self._color, 
            "opacity": str(opacity)
        })
        if kind == "circle":
            self.styles["border-radius"] = "50%"
        elif kind == "diamond":
            self.styles["transform"] = "rotate(45deg)"
        elif kind == "triangle":
            self.styles.update({
                "width": "0", 
                "height": "0", 
                "background": "transparent",
                "border-left": f"{w//2}px solid transparent",
                "border-right": f"{w//2}px solid transparent",
                "border-bottom": f"{h}px solid {self._color}",
            })

    def morph_loop(self):
        """Animación que cambia la forma (círculo ↔ cuadrado)"""
        self._loop = True
        return self._set_anim("morphShape", 0, 3.0)

    def _render(self):
        return self._wrap_tooltip(f'<div class="c-component" style="{self._render_style()}"></div>')

class Code(Component):
    def __init__(self, code, lang="", line_numbers=False):
        super().__init__()
        self.code = code
        self.lang = lang
        self._line_numbers = line_numbers
        self.styles.update({"font-size": "14px", "width": "75%", "max-height": "55%"})

    def _render(self):
        import html as htmllib
        lines = self.code.split("\n")
        if self._line_numbers:
            numbered = "\n".join(f'<span class="line-numbers">{i+1:2d}</span>{htmllib.escape(l)}' for i, l in enumerate(lines))
            safe = numbered
        else:
            safe = htmllib.escape(self.code)
        lang_badge = f'<div style="font-size:10px;color:var(--muted);margin-bottom:6px;text-transform:uppercase">{self.lang}</div>' if self.lang else ""
        return self._wrap_tooltip(f'<div class="c-component" style="{self._render_style()}">{lang_badge}<pre class="code-block">{safe}</pre></div>')


class BulletList(Component):
    def __init__(self, items, icon="▸", stagger=0.15, color=None):
        super().__init__()
        self.items = items
        self._icon = icon
        self._stagger = stagger
        self._col = color or "var(--primary)"
        self.styles.update({"font-size": "18px", "line-height": "2", "list-style": "none", "width": "65%"})

    def _render(self):
        lis = ""
        for i, item in enumerate(self.items):
            icon = f'<span style="color:{self._col};margin-right:10px">{self._icon}</span>'
            lis += f'<li style="display:flex;align-items:center;">{icon}{item}</li>'
        return self._wrap_tooltip(f'<ul class="c-component" style="{self._render_style()}">{lis}</ul>')


class Button(Component):
    def __init__(self, text, target_slide=None, url=None, color=None, outline=False):
        super().__init__()
        self.text = text
        self._target_slide = target_slide
        self._url = url
        self._color = color or "var(--primary)"
        self._outline = outline
        self.styles.update({"padding": "12px 32px", "border-radius": "8px",
                           "font-size": "16px", "font-weight": "600", "cursor": "pointer",
                           "display": "inline-block", "transition": "transform .15s",
                           "text-decoration": "none"})

    def _render(self):
        if self._outline:
            extra = f"background:transparent;color:{self._color};border:2px solid {self._color};"
        else:
            extra = f"background:{self._color};color:#fff;border:none;"

        if self._target_slide:
            click = f'onclick="goTo({self._target_slide - 1})"'
            tag = "button"
        elif self._url:
            click = ""
            tag = "a"
            extra += f'href="{self._url}" target="_blank"'
        else:
            click = self._onclick or ""
            tag = "button"

        return self._wrap_tooltip(f'<{tag} class="c-component" style="{self._render_style()}{extra}" {click}>{self.text}</{tag}>')


class Badge(Component):
    def __init__(self, text, color=None, bg=None):
        super().__init__()
        self.text = text
        self._color = color or "#fff"
        self._bg = bg or "var(--primary)"
        self.styles.update({"padding": "6px 18px", "border-radius": "99px",
                           "font-size": "13px", "font-weight": "600", "display": "inline-block"})

    def _render(self):
        return self._wrap_tooltip(f'<span class="c-component" style="{self._render_style()};background:{self._bg};color:{self._color}">{self.text}</span>')


class Divider(Component):
    def __init__(self, width="60%", color=None, thickness=2):
        super().__init__()
        self._color = color or "var(--primary)"
        self.styles.update({"width": width, "height": f"{thickness}px", "border": "none"})

    def _render(self):
        return self._wrap_tooltip(f'<hr class="c-component" style="{self._render_style()};background:linear-gradient(90deg,transparent,{self._color},transparent)">')


class Image(Component):
    def __init__(self, src, alt="", rounded=True):
        super().__init__()
        self.src = src
        self.alt = alt
        self.styles.update({"max-width": "60%", "max-height": "60%", "object-fit": "cover"})
        if rounded:
            self.styles["border-radius"] = "15px"

    def _render(self):
        return self._wrap_tooltip(f'<img class="c-component" src="{self.src}" alt="{self.alt}" style="{self._render_style()}">')


class Card(Component):
    def __init__(self, title="", body="", icon=""):
        super().__init__()
        self._title = title
        self._body = body
        self._icon = icon
        self.styles.update({"width": "300px", "padding": "24px",
                           "background": "var(--surface)", "border-radius": "16px",
                           "border": "1px solid var(--border)"})

    def _render(self):
        icon_html = f'<div style="font-size:36px;margin-bottom:12px">{self._icon}</div>' if self._icon else ""
        return self._wrap_tooltip(f'<div class="c-component" style="{self._render_style()}">{icon_html}<h3 style="font-size:18px;margin-bottom:10px;color:var(--primary)">{self._title}</h3><p style="font-size:14px;line-height:1.6;color:var(--muted)">{self._body}</p></div>')

class IconStat(Component):
    def __init__(self, icon, value, label, color=None):
        super().__init__()
        self.icon = icon
        self.value = value
        self.label = label
        self._color = color or "var(--primary)"
        self.styles.update({"text-align": "center", "width": "200px"})

    def _render(self):
        val_html = f'<div class="stat-value" style="color:{self._color}">{self.value}</div>'
        return self._wrap_tooltip(f'<div class="c-component c-iconstat" style="{self._render_style()}"><span class="stat-icon">{self.icon}</span>{val_html}<div class="stat-label">{self.label}</div></div>')


class Timeline(Component):
    def __init__(self, events):
        super().__init__()
        self.events = events
        self.styles.update({"width": "60%"})

    def _render(self):
        items = ""
        for ev in self.events:
            items += f'<li><div class="tl-year">{ev.get("year","")}</div><div class="tl-title">{ev.get("title","")}</div><div class="tl-desc">{ev.get("desc","")}</div></li>'
        return self._wrap_tooltip(f'<ul class="c-component c-timeline" style="{self._render_style()}">{items}</ul>')


class Table(Component):
    def __init__(self, headers, rows):
        super().__init__()
        self.headers = headers
        self.rows = rows
        self.styles.update({"width": "80%", "border-radius": "12px", "overflow": "hidden", "border": f"1px solid var(--border)"})

    def _render(self):
        ths = "".join(f"<th>{h}</th>" for h in self.headers)
        trs = "".join(f"<tr>{''.join(f'<td>{cell}</td>' for cell in row)}</tr>" for row in self.rows)
        return self._wrap_tooltip(f'<div class="c-component" style="{self._render_style()}"><table class="c-table"><thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table></div>')


class Columns(Component):
    def __init__(self, *components_lists, cols=None, gap=24):
        super().__init__()
        self._cols_content = components_lists
        n = cols or len(components_lists)
        self.styles.update({"display": "grid", "grid-template-columns": f"repeat({n}, 1fr)",
                           "gap": f"{gap}px", "width": "90%", "position": "relative"})

    def _render(self):
        cols_html = ""
        for col_items in self._cols_content:
            items_html = ""
            if isinstance(col_items, list):
                for item in col_items:
                    items_html += item._render()
            else:
                items_html = str(col_items)
            cols_html += f'<div style="display:flex;flex-direction:column;gap:16px">{items_html}</div>'
        return self._wrap_tooltip(f'<div class="c-component" style="{self._render_style()}">{cols_html}</div>')


class QRCode(Component):
    def __init__(self, url, size=150):
        super().__init__()
        self.url = url
        self._sz = size
        self.styles.update({"width": f"{size}px", "height": f"{size}px"})

    def _render(self):
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size={self._sz}x{self._sz}&data={self.url}"
        return self._wrap_tooltip(f'<img class="c-component" src="{qr_url}" style="{self._render_style()};background:#fff;padding:10px;border-radius:12px" alt="QR">')


class Tooltip(Component):
    def __init__(self, content, tip_text):
        super().__init__()
        self.content = content
        self.tip_text = tip_text
        self.styles.update({"font-size": "18px", "cursor": "help"})

    def _render(self):
        return self._wrap_tooltip(f'<div class="c-component" style="{self._render_style()}"><span class="c-tooltip">{self.content}<span class="tooltip-text">{self.tip_text}</span></span></div>')


# ─────────────────────────────────────────────
#  COMPONENTES ANIMADOS ADICIONALES
# ─────────────────────────────────────────────

class MovingFigure(Component):
    def __init__(self, shape="circle", size=50, color=None, opacity=0.8):
        super().__init__()
        self.shape = shape
        self._color = color or "var(--primary)"
        self._opacity = opacity
        self.styles.update({
            "width": f"{size}px",
            "height": f"{size}px",
            "background": self._color,
            "opacity": str(opacity),
            "border-radius": "50%" if shape == "circle" else "0%",
        })
        if shape == "triangle":
            self.styles.update({
                "width": "0", "height": "0", "background": "transparent",
                "border-left": f"{size//2}px solid transparent",
                "border-right": f"{size//2}px solid transparent",
                "border-bottom": f"{size}px solid {self._color}",
            })
        elif shape == "diamond":
            self.styles["transform"] = "rotate(45deg)"

    def gradient(self, color1, color2):
        self.styles["background"] = f"linear-gradient(135deg, {color1}, {color2})"
        return self

    def _render(self):
        return self._wrap_tooltip(f'<div class="c-component" style="{self._render_style()}"></div>')


class RotatingIcon(Component):
    def __init__(self, icon="★", size=48, color=None):
        super().__init__()
        self.icon = icon
        self._color = color or "var(--primary)"
        self.styles.update({"font-size": f"{size}px", "color": self._color,
                           "text-align": "center", "line-height": "1"})
        self._loop = True
        self._set_anim("rotate", 0, 2)

    def _render(self):
        return self._wrap_tooltip(f'<div class="c-component" style="{self._render_style()}">{self.icon}</div>')


class OrbitingObject(Component):
    def __init__(self, shape="circle", size=30, orbit_radius=100, color=None):
        super().__init__()
        self.orbit_radius = orbit_radius
        self._color = color or "var(--primary)"
        self.styles.update({"width": f"{size}px", "height": f"{size}px",
                           "background": self._color,
                           "border-radius": "50%" if shape == "circle" else "0%"})
        self._loop = True
        self._set_anim("orbit", 0, 4)

    def _render(self):
        return self._wrap_tooltip(f'<div class="c-component" style="{self._render_style()}"></div>')


class GlowText(Component):
    def __init__(self, text, color=None, size=48):
        super().__init__()
        self.text = text
        self._color = color or "var(--primary)"
        self.styles.update({"font-size": f"{size}px", "font-weight": "800",
                           "color": self._color, "text-align": "center"})
        self._loop = True
        self._set_anim("glow", 0, 2.0)

    def _render(self):
        return self._wrap_tooltip(f'<div class="c-component" style="{self._render_style()}">{self.text}</div>')


class ParticleSystem(Component):
    def __init__(self, count=30, colors=None, behaviors=None):
        super().__init__()
        self.count = count
        self.colors = colors or ["var(--primary)", "var(--accent)"]
        self.behaviors = behaviors or ["float", "drift", "pulse"]
        self.styles = {"position": "absolute", "inset": "0", "z-index": "-1", "overflow": "hidden"}

    def _render(self):
        particles = []
        for _ in range(self.count):
            size = random.randint(3, 8)
            x = random.randint(0, 100)
            y = random.randint(0, 100)
            color = random.choice(self.colors)
            behavior = random.choice(self.behaviors)
            speed = random.uniform(4, 10)
            delay = random.uniform(0, 5)
            opacity = random.uniform(0.1, 0.4)
            particles.append(f'<div style="position:absolute;left:{x}%;top:{y}%;width:{size}px;height:{size}px;border-radius:50%;background:{color};opacity:{opacity};animation:{behavior} {speed}s ease-in-out {delay}s infinite;"></div>')
        return f'<div style="{self._render_style()}">{"".join(particles)}</div>'


class ProgressCircle(Component):
    def __init__(self, percent=75, label="", size=130, color=None):
        super().__init__()
        self.pct = max(0, min(100, percent))
        self.label = label
        self.sz = size
        self._col = color or "var(--primary)"
        self.styles.update({"width": f"{size}px", "height": f"{size}px"})

    def _render(self):
        r = self.sz / 2 - 10
        circ = 2 * 3.14159 * r
        dash = circ * self.pct / 100
        return self._wrap_tooltip(f'<div class="c-component" style="{self._render_style()}"><svg width="{self.sz}" height="{self.sz}" viewBox="0 0 {self.sz} {self.sz}"><circle cx="{self.sz//2}" cy="{self.sz//2}" r="{r}" fill="none" stroke="rgba(255,255,255,.1)" stroke-width="8"/><circle cx="{self.sz//2}" cy="{self.sz//2}" r="{r}" fill="none" stroke="{self._col}" stroke-width="8" stroke-dasharray="{dash:.1f} {circ:.1f}" stroke-linecap="round" transform="rotate(-90 {self.sz//2} {self.sz//2})"/><text x="{self.sz//2}" y="{self.sz//2 - 4}" text-anchor="middle" dominant-baseline="central" class="progress-ring-text" font-size="22" font-weight="700">{self.pct}%</text><text x="{self.sz//2}" y="{self.sz//2 + 20}" text-anchor="middle" class="progress-ring-text" font-size="11" opacity=".6">{self.label}</text></svg></div>')


class CountUp(Component):
    def __init__(self, end, prefix="", suffix="", duration_ms=1500, color=None, decimals=0, size=64):
        super().__init__()
        self._end = end
        self._prefix = prefix
        self._suffix = suffix
        self._dur_ms = duration_ms
        self._decimals = decimals
        self._col = color or "var(--primary)"
        self.styles.update({"font-size": f"{size}px", "font-weight": "800", "text-align": "center", "color": self._col})

    def _render(self):
        return self._wrap_tooltip(f'<div class="c-component" style="{self._render_style()}" data-count-end="{self._end}" data-count-dur="{self._dur_ms}" data-prefix="{self._prefix}" data-suffix="{self._suffix}" data-decimals="{self._decimals}">{self._prefix}0{self._suffix}</div>')