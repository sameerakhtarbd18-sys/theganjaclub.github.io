/* Grow Assistant Widget — The Ganja Club
   Drop-in: <script src="/grow-widget.js"></script>
   Adds a floating chat button + slide-out drawer to any page. */

(function () {
  'use strict';

  // ── Styles (injected once) ──────────────────────────────────
  if (!document.getElementById('grow-widget-css')) {
    var css = document.createElement('style');
    css.id = 'grow-widget-css';
    css.textContent = `
:root{--gw-green:#059669;--gw-green-dark:#047857;--gw-radius:8px;--gw-z:2147483646}
#gw-fab{position:fixed;bottom:24px;right:24px;z-index:var(--gw-z);width:52px;height:52px;border-radius:50%;background:var(--gw-green);color:#fff;border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:26px;box-shadow:0 4px 16px rgba(5,150,105,.35);transition:transform .2s,box-shadow .2s;-webkit-tap-highlight-color:transparent}
#gw-fab:hover{transform:scale(1.08);box-shadow:0 6px 22px rgba(5,150,105,.5)}
#gw-fab:active{transform:scale(.95)}
#gw-badge{position:absolute;top:-6px;right:-6px;width:10px;height:10px;border-radius:50%;background:#ef4444;border:2px solid #fff;animation:gw-pulse 2s infinite}
@keyframes gw-pulse{0%,100%{opacity:1}50%{opacity:.3}}

#gw-overlay{position:fixed;inset:0;z-index:calc(var(--gw-z) + 1);background:rgba(0,0,0,.45);display:none;align-items:flex-end;justify-content:center}
#gw-overlay.open{display:flex}
#gw-drawer{width:100%;max-width:400px;height:520px;max-height:calc(100vh - 80px);background:var(--gw-bg,#fff);color:var(--gw-text,#111827);border-radius:12px 12px 0 0;display:flex;flex-direction:column;overflow:hidden;box-shadow:0 -4px 32px rgba(0,0,0,.18);animation:gw-slideUp .25s ease;font-family:Inter,-apple-system,BlinkMacSystemFont,sans-serif}
@keyframes gw-slideUp{from{transform:translateY(100%)}to{transform:translateY(0)}}

#gw-header{display:flex;align-items:center;justify-content:space-between;padding:14px 16px;border-bottom:1px solid var(--gw-line,#e5e7eb);background:var(--gw-card,#f9fafb);flex-shrink:0}
#gw-header-left{display:flex;align-items:center;gap:10px}
#gw-header-icon{font-size:24px;line-height:1}
#gw-header-title{font-size:.9rem;font-weight:600;letter-spacing:-.01em;color:var(--gw-text,#111827)}
#gw-header-sub{font-size:.68rem;color:var(--gw-dim,#6b7280)}
#gw-close{background:none;border:none;font-size:20px;color:var(--gw-dim,#6b7280);cursor:pointer;padding:4px 8px;border-radius:4px;transition:all .15s}
#gw-close:hover{color:var(--gw-text,#111827);background:var(--gw-line,#e5e7eb)}

#gw-disclaimer{font-size:.65rem;color:var(--gw-dim,#6b7280);text-align:center;padding:8px 16px;border-bottom:1px solid var(--gw-line,#e5e7eb);background:var(--gw-card,#f9fafb);flex-shrink:0;line-height:1.4}

#gw-messages{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:10px;background:var(--gw-bg,#fff)}
#gw-messages::-webkit-scrollbar{width:3px}
#gw-messages::-webkit-scrollbar-track{background:transparent}
#gw-messages::-webkit-scrollbar-thumb{background:var(--gw-line,#e5e7eb);border-radius:2px}

.gw-msg{max-width:88%;padding:9px 12px;border-radius:var(--gw-radius);font-size:.8rem;line-height:1.5;animation:gw-fade .2s ease}
.gw-msg-bot{background:var(--gw-card,#f9fafb);color:var(--gw-text,#111827);align-self:flex-start;border:1px solid var(--gw-line,#e5e7eb);border-bottom-left-radius:2px}
.gw-msg-user{background:var(--gw-green);color:#fff;align-self:flex-end;border-bottom-right-radius:2px;font-weight:500}
.gw-msg-src{display:block;font-size:.6rem;color:var(--gw-dim,#6b7280);margin-top:5px;padding-top:5px;border-top:1px solid var(--gw-line,#e5e7eb)}
.gw-msg-user .gw-msg-src{color:rgba(255,255,255,.55);border-top-color:rgba(255,255,255,.15)}
@keyframes gw-fade{from{opacity:0;transform:translateY(3px)}to{opacity:1;transform:translateY(0)}}

.gw-typing{display:flex;gap:3px;padding:9px 12px}
.gw-typing span{width:5px;height:5px;background:var(--gw-dim,#6b7280);border-radius:50%;animation:gw-bounce 1.4s infinite ease-in-out}
.gw-typing span:nth-child(2){animation-delay:.2s}
.gw-typing span:nth-child(3){animation-delay:.4s}
@keyframes gw-bounce{0%,80%,100%{transform:translateY(0)}40%{transform:translateY(-5px)}}

#gw-input-wrap{display:flex;gap:6px;padding:10px 14px;border-top:1px solid var(--gw-line,#e5e7eb);background:var(--gw-card,#f9fafb);flex-shrink:0}
#gw-input-wrap input{flex:1;padding:9px 12px;background:var(--gw-bg,#fff);border:1px solid var(--gw-line,#e5e7eb);border-radius:var(--gw-radius);color:var(--gw-text,#111827);font-size:.8rem;font-family:inherit;outline:none;transition:border-color .15s}
#gw-input-wrap input:focus{border-color:var(--gw-green)}
#gw-input-wrap input::placeholder{color:var(--gw-dim,#6b7280)}
#gw-input-wrap button{width:36px;height:36px;background:var(--gw-green);color:#fff;border:none;border-radius:var(--gw-radius);font-size:1rem;cursor:pointer;transition:all .15s;display:flex;align-items:center;justify-content:center;flex-shrink:0}
#gw-input-wrap button:hover{background:var(--gw-green-dark)}
#gw-input-wrap button:disabled{opacity:.4;cursor:not-allowed}

#gw-suggestions{display:flex;gap:5px;flex-wrap:wrap;padding:10px 14px 0;flex-shrink:0;background:var(--gw-bg,#fff)}
#gw-suggestions button{background:transparent;border:1px solid var(--gw-line,#e5e7eb);color:var(--gw-dim,#6b7280);padding:5px 10px;border-radius:16px;font-size:.68rem;cursor:pointer;font-family:inherit;transition:all .15s}
#gw-suggestions button:hover{color:var(--gw-text,#111827);border-color:var(--gw-green);background:var(--gw-card,#f9fafb)}

@media(min-width:768px){
  #gw-overlay{align-items:center}
  #gw-drawer{border-radius:12px;height:540px;max-height:calc(100vh - 60px)}
}`;
    document.head.appendChild(css);
  }

  // ── Read blog theme ─────────────────────────────────────────
  function getTheme() {
    var html = document.documentElement;
    var isDark = html.getAttribute('data-theme') === 'dark';
    return isDark ? 'dark' : 'light';
  }

  function applyTheme() {
    var t = getTheme();
    var r = document.documentElement;
    if (t === 'dark') {
      r.style.setProperty('--gw-bg', '#0f172a');
      r.style.setProperty('--gw-card', '#1e293b');
      r.style.setProperty('--gw-text', '#f1f5f9');
      r.style.setProperty('--gw-dim', '#94a3b8');
      r.style.setProperty('--gw-line', '#334155');
    } else {
      r.style.setProperty('--gw-bg', '#ffffff');
      r.style.setProperty('--gw-card', '#f9fafb');
      r.style.setProperty('--gw-text', '#111827');
      r.style.setProperty('--gw-dim', '#6b7280');
      r.style.setProperty('--gw-line', '#e5e7eb');
    }
  }

  // ── Wait for DOM ────────────────────────────────────────────
  function init() {
    if (document.getElementById('gw-overlay')) return; // already injected

    applyTheme();

    // Observe theme changes
    var observer = new MutationObserver(function () {
      applyTheme();
    });
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });

    // Create FAB
    var fab = document.createElement('button');
    fab.id = 'gw-fab';
    fab.setAttribute('aria-label', 'Ask Grow Assistant');
    fab.title = 'Ask Grow Assistant';
    fab.innerHTML = '🌱<span id="gw-badge"></span>';
    document.body.appendChild(fab);

    // Create overlay + drawer
    var overlay = document.createElement('div');
    overlay.id = 'gw-overlay';
    overlay.innerHTML =
      '<div id="gw-drawer">' +
        '<div id="gw-header">' +
          '<div id="gw-header-left">' +
            '<span id="gw-header-icon">🤖</span>' +
            '<div><div id="gw-header-title">Grow Assistant</div><div id="gw-header-sub">Powered by The Ganja Club</div></div>' +
          '</div>' +
          '<button id="gw-close" aria-label="Close">&times;</button>' +
        '</div>' +
        '<div id="gw-disclaimer">&#9888;&#65039; Educational only. No medical advice.</div>' +
        '<div id="gw-messages">' +
          '<div class="gw-msg gw-msg-bot">Hey! I\'m your cannabis cultivation guide. Ask me anything about growing — nutrients, lighting, pest control, troubleshooting. What can I help with?</div>' +
        '</div>' +
        '<div id="gw-suggestions">' +
          '<button data-q="What nutrients for veg stage?">Veg nutrients</button>' +
          '<button data-q="How to prevent powdery mildew?">Powdery mildew</button>' +
          '<button data-q="What pH for soil growing?">Water pH</button>' +
          '<button data-q="How to know when to harvest?">Harvest timing</button>' +
        '</div>' +
        '<div id="gw-input-wrap">' +
          '<input type="text" id="gw-input" placeholder="Ask a growing question..." onkeydown="if(event.key===\'Enter\')window._gwAsk()">' +
          '<button id="gw-send" onclick="window._gwAsk()">➤</button>' +
        '</div>' +
      '</div>';
    document.body.appendChild(overlay);

    // Events
    fab.onclick = openDrawer;
    document.getElementById('gw-close').onclick = closeDrawer;
    overlay.onclick = function (e) { if (e.target === overlay) closeDrawer(); };

    // Suggestion chips
    var chips = document.querySelectorAll('#gw-suggestions button');
    chips.forEach(function (btn) {
      btn.onclick = function () { quickAsk(btn.dataset.q); };
    });

    // Expose ask function globally
    window._gwAsk = ask;

    // Escape to close
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && overlay.classList.contains('open')) closeDrawer();
    });
  }

  // ── Open / Close ────────────────────────────────────────────
  function openDrawer() {
    applyTheme();
    var overlay = document.getElementById('gw-overlay');
    overlay.classList.add('open');
    var badge = document.getElementById('gw-badge');
    if (badge) badge.style.display = 'none';
    setTimeout(function () {
      var input = document.getElementById('gw-input');
      if (input) input.focus();
    }, 300);
  }

  function closeDrawer() {
    document.getElementById('gw-overlay').classList.remove('open');
  }

  // ── Chat logic ──────────────────────────────────────────────
  var isAsking = false;

  function addMsg(text, type, sources) {
    var messages = document.getElementById('gw-messages');
    var div = document.createElement('div');
    div.className = 'gw-msg gw-msg-' + type;
    div.textContent = text;
    if (sources && sources.length) {
      var src = document.createElement('span');
      src.className = 'gw-msg-src';
      src.textContent = '📄 ' + sources.map(function (s) { return s.source; }).join(' · ');
      div.appendChild(src);
    }
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  function addTyping() {
    var messages = document.getElementById('gw-messages');
    var div = document.createElement('div');
    div.className = 'gw-msg gw-msg-bot gw-typing';
    div.id = 'gw-typing';
    div.innerHTML = '<span></span><span></span><span></span>';
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  function removeTyping() {
    var el = document.getElementById('gw-typing');
    if (el) el.remove();
  }

  async function ask() {
    var input = document.getElementById('gw-input');
    var sendBtn = document.getElementById('gw-send');
    var question = input.value.trim();
    if (!question || isAsking) return;

    isAsking = true;
    sendBtn.disabled = true;
    input.disabled = true;
    addMsg(question, 'user');
    input.value = '';
    addTyping();

    try {
      var resp = await fetch('/.netlify/functions/ask-grow', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: question })
      });
      var data = await resp.json();
      removeTyping();
      if (data.error) {
        addMsg('Sorry, something went wrong. Please try again.', 'bot');
      } else {
        addMsg(data.answer, 'bot', data.sources);
      }
    } catch (e) {
      removeTyping();
      addMsg('Network error. Please check your connection and try again.', 'bot');
    }

    isAsking = false;
    sendBtn.disabled = false;
    input.disabled = false;
    input.focus();
  }

  function quickAsk(q) {
    var input = document.getElementById('gw-input');
    input.value = q;
    ask();
  }

  // ── Boot ────────────────────────────────────────────────────
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
