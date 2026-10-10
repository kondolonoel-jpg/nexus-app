#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Patch le dashboard NEXUS original pour ajouter :
   - écran de connexion / inscription (auth gate)
   - flux d'actualités temps réel (backend)
   - section Analyse IA des marchés (régime D1 + W1 + raisons)
"""
import io, sys

SRC = "/home/user/uploads/NEXUS_Dashboard_KONDOLO_NOEL_COMMAND_INTERNET_V3.html"
DST = "/home/user/nexus-app/static/index.html"

with io.open(SRC, "r", encoding="utf-8") as f:
    html = f.read()

def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"[FAIL] ancre introuvable ou multiple ({count}x) : {label}")
    return text.replace(old, new)

# ---------------------------------------------------------------- 1. Renumérotation des sections 06..11 -> 07..12
for old_n, new_n in [("11", "12"), ("10", "11"), ("09", "10"), ("08", "09"), ("07", "08"), ("06", "07")]:
    html = replace_once(html, f'section-index">{old_n} — ', f'section-index">{new_n} — ', f"renum {old_n}")

# ---------------------------------------------------------------- 1b. Enregistrer la page Analyse IA dans le routeur d'origine
html = replace_once(
    html,
    "const PAGES = ['home','command','risk','protocol','playbook','backtest','news','journal','shots','reviews','accounts','system'];",
    "const PAGES = ['home','command','risk','protocol','playbook','backtest','news','analysis','journal','shots','reviews','accounts','system'];",
    "PAGES",
)

# ---------------------------------------------------------------- 1c. Neutralise le mode « pages » : toutes les sections toujours visibles
html = replace_once(
    html,
    """    html.js main > section{
      display:none;
      border-top:none;
      scroll-margin-top:0;
      padding:32px 0 72px;
    }""",
    """    html.js main > section{
      display:block;
      border-top:none;
      scroll-margin-top:70px;
      padding:32px 0 72px;
    }""",
    "sections visibles",
)
html = replace_once(
    html,
    "html.js .hero{display:none}",
    "html.js .hero{display:grid}",
    "hero visible",
)
html = replace_once(
    html,
    """    html.js[data-page="home"] main,
    html.js[data-page="home"] .site-footer{display:none}
    html.js[data-page="home"] .hero{flex:1 1 auto;min-height:calc(100vh - 100px);align-items:center;padding:28px 0 36px;grid-template-columns:1fr}""",
    """    html.js[data-page="home"] main,
    html.js[data-page="home"] .site-footer{display:block}
    html.js[data-page="home"] .hero{flex:none;min-height:0;align-items:end;padding:clamp(60px,8vw,100px) 0 56px;grid-template-columns:1fr}""",
    "home scroll",
)

# ---------------------------------------------------------------- 2. CSS additionnel avant </head>
EXTRA_CSS = """
<style id="nexus-ext">
/* enregistrement de la page Analyse IA dans le système de pages d'origine */
html.js[data-page="analysis"] #analysis{display:block;animation:pageIn .38s cubic-bezier(.22,.86,.28,1) both}
/* ====== AUTH GATE ====== */
.auth-gate{position:fixed;inset:0;z-index:200;display:flex;align-items:center;justify-content:center;padding:22px;overflow:auto;background:radial-gradient(circle at 12% -6%,rgba(213,173,70,.14),transparent 30rem),radial-gradient(circle at 88% 108%,rgba(121,174,235,.10),transparent 30rem),rgba(6,9,14,.985)}
.auth-card{width:min(430px,100%);padding:30px 28px 24px;border:1px solid var(--line);background:linear-gradient(150deg,rgba(24,32,45,.96),rgba(11,15,23,.98));box-shadow:var(--shadow)}
.auth-brand{display:flex;align-items:center;gap:11px;margin-bottom:6px}
.auth-brand .brand-mark{width:38px;height:38px}
.auth-brand b{font:600 17px/1.15 "Playfair Display",Georgia,serif}
.auth-brand b span{color:var(--gold)}
.auth-sub{margin:8px 0 18px;color:var(--text-faint);font-size:11px;line-height:1.6}
.auth-tabs{display:grid;grid-template-columns:1fr 1fr;gap:0;margin-bottom:18px;border:1px solid var(--line)}
.auth-tab{padding:10px 6px;border:0;background:rgba(255,255,255,.02);color:var(--text-faint);font:10px/1 "DM Mono",monospace;letter-spacing:.08em;text-transform:uppercase;cursor:pointer;transition:.18s}
.auth-tab.active{background:rgba(213,173,70,.12);color:var(--gold-bright)}
.auth-form .field{margin-bottom:12px;min-width:0}
.auth-form label{display:block;margin-bottom:5px;color:var(--text-dim);font:9.5px/1 "DM Mono",monospace;letter-spacing:.07em;text-transform:uppercase}
.auth-msg{min-height:16px;margin:2px 0 12px;color:var(--red);font-size:11px}
.auth-msg.ok{color:var(--green)}
.auth-foot{margin-top:16px;padding-top:14px;border-top:1px solid var(--line-soft);color:var(--text-faint);font-size:9.5px;line-height:1.55}
.auth-gate .btn-primary{width:100%;min-height:42px}
.auth-gate[hidden]{display:none!important}
body.locked{overflow:hidden}
/* ====== USER CHIP ====== */
.user-chip{display:flex;align-items:center;gap:9px;flex:0 0 auto}
.user-chip-name{max-width:130px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--gold-bright);font:500 10px/1 "DM Mono",monospace;letter-spacing:.05em}
.user-chip .btn{min-height:28px;padding:6px 10px;font-size:8.5px}
@media(max-width:1360px){
  .nav-links{gap:11px}
  .user-chip-name{max-width:90px}
}
@media(max-width:1100px){
  .nav-inner{flex-wrap:wrap;row-gap:8px;padding:8px 0}
}
@media(max-width:980px){
  .user-chip-name{max-width:84px}
}
@media(max-width:620px){
  .logout-txt{display:none}
  .user-chip .btn{min-height:26px;padding:5px 9px}
  .user-chip-name{max-width:64px}
  .nav-inner{gap:12px}
}
/* ====== FLUX NEWS TEMPS RÉEL ====== */
.live-feed{padding:0;margin-bottom:13px;overflow:hidden}
.live-feed-head{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:10px;padding:15px 17px 12px;border-bottom:1px solid var(--line-soft)}
.live-feed-head h3{display:flex;align-items:center;gap:9px;margin:0;font:600 18px/1.2 "Playfair Display",Georgia,serif}
.live-feed-head .live-dot{width:8px;height:8px;border-radius:50%;background:var(--red);box-shadow:0 0 0 4px rgba(226,110,99,.12),0 0 12px rgba(226,110,99,.7);animation:pulse 1.6s infinite}
.live-feed-status{color:var(--text-faint);font:9px/1.5 "DM Mono",monospace;letter-spacing:.04em;text-align:right}
.live-feed-status b{color:var(--green);font-weight:500}
.live-feed-filters{display:flex;flex-wrap:wrap;gap:6px;padding:11px 17px;border-bottom:1px solid var(--line-soft)}
.nf-chip{padding:6px 10px;border:1px solid var(--line);background:transparent;color:var(--text-faint);font:9px/1 "DM Mono",monospace;letter-spacing:.06em;text-transform:uppercase;cursor:pointer;transition:.16s}
.nf-chip:hover{color:var(--text);border-color:var(--gold-dim)}
.nf-chip.active{background:rgba(213,173,70,.13);border-color:var(--gold);color:var(--gold-bright)}
.nf-chip.hot.active{background:var(--red-soft);border-color:rgba(226,110,99,.6);color:var(--red)}
.live-feed-list{max-height:520px;overflow:auto;scrollbar-width:thin}
.nf-item{display:grid;grid-template-columns:74px 1fr;gap:12px;padding:12px 17px;border-bottom:1px solid var(--line-soft);transition:background .15s}
.nf-item:hover{background:rgba(255,255,255,.02)}
.nf-item:last-child{border-bottom:0}
.nf-time{color:var(--gold);font:9.5px/1.6 "DM Mono",monospace;white-space:nowrap}
.nf-time small{display:block;color:var(--text-faint);font-size:8.5px}
.nf-title{margin:0}
.nf-title a{color:var(--text);font-size:12px;line-height:1.45;text-decoration:none;transition:color .15s}
.nf-title a:hover{color:var(--gold-bright)}
.nf-sum{margin:4px 0 7px;color:var(--text-faint);font-size:10.5px;line-height:1.5;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.nf-meta{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.nf-src{color:var(--text-dim);font:8.5px/1 "DM Mono",monospace;letter-spacing:.05em}
.nf-tag{padding:2.5px 6px;border:1px solid var(--line);color:var(--text-faint);font:8px/1 "DM Mono",monospace;letter-spacing:.05em;text-transform:uppercase}
.nf-tag.hi{border-color:rgba(226,110,99,.55);color:var(--red);background:var(--red-soft)}
.nf-tag.cat-Forex{border-color:rgba(121,174,235,.4);color:var(--blue)}
.nf-tag.cat-Macro{border-color:rgba(213,173,70,.45);color:var(--gold)}
.nf-tag.cat-Crypto{border-color:rgba(80,198,136,.4);color:var(--green)}
.nf-tag.cat-Energie{border-color:rgba(231,169,76,.45);color:var(--amber)}
.live-feed-empty{padding:30px 17px;color:var(--text-faint);font-size:11px;text-align:center}
/* ====== ANALYSE IA ====== */
.ai-toolbar{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px;margin-bottom:13px;padding:14px 17px;border:1px solid var(--line);background:rgba(16,22,32,.76)}
.ai-toolbar p{margin:0;color:var(--text-dim);font-size:11px}
.ai-toolbar p strong{color:var(--green);font-weight:600}
.ai-toolbar p em{color:var(--text-faint);font-style:normal;font:9px/1.6 "DM Mono",monospace}
.ai-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:13px}
.ai-card{display:flex;flex-direction:column;padding:0;border:1px solid var(--line);background:linear-gradient(160deg,rgba(23,31,44,.9),rgba(13,18,27,.94));overflow:hidden;transition:border-color .2s,transform .2s}
.ai-card:hover{border-color:rgba(213,173,70,.45);transform:translateY(-2px)}
.ai-head{display:flex;align-items:start;justify-content:space-between;gap:10px;padding:16px 17px 13px;border-bottom:1px solid var(--line-soft)}
.ai-head h3{display:flex;align-items:center;gap:8px;margin:0;font:600 17px/1.2 "Playfair Display",Georgia,serif}
.ai-head h3::before{width:6px;height:6px;content:"";border-radius:50%;background:var(--gold);box-shadow:0 0 8px rgba(213,173,70,.6)}
.ai-sym{margin-top:4px;color:var(--text-faint);font:8.5px/1.4 "DM Mono",monospace;letter-spacing:.06em;text-transform:uppercase}
.ai-price{text-align:right;color:var(--text);font:600 16px/1.2 "DM Mono",monospace}
.ai-price small{display:block;margin-top:3px;color:var(--text-faint);font:8.5px/1 "DM Mono",monospace}
.ai-regimes{display:grid;grid-template-columns:1fr 1fr;gap:9px;padding:13px 17px}
.ai-regime{padding:11px 12px;border:1px solid var(--line-soft);background:rgba(7,10,15,.5)}
.ai-tf{display:block;margin-bottom:7px;color:var(--text-faint);font:8.5px/1 "DM Mono",monospace;letter-spacing:.09em;text-transform:uppercase}
.regime-badge{display:inline-block;padding:5px 9px;border:1px solid;font:600 10px/1 "DM Mono",monospace;letter-spacing:.07em}
.regime-badge.up{color:var(--green);border-color:rgba(80,198,136,.5);background:var(--green-soft)}
.regime-badge.down{color:var(--red);border-color:rgba(226,110,99,.5);background:var(--red-soft)}
.regime-badge.flat{color:var(--amber);border-color:rgba(231,169,76,.5);background:var(--amber-soft)}
.regime-badge.mix{color:var(--blue);border-color:rgba(121,174,235,.5);background:var(--blue-soft)}
.ai-conf{display:flex;align-items:center;gap:7px;margin-top:9px;color:var(--text-faint);font:8.5px/1 "DM Mono",monospace}
.ai-conf-bar{flex:1;height:3px;background:rgba(255,255,255,.07)}
.ai-conf-bar i{display:block;height:100%;background:var(--gold)}
.ai-bias{margin:0 17px 12px;padding:9px 11px;border-left:2px solid var(--gold-dim);color:var(--text-dim);background:rgba(213,173,70,.05);font-size:10.5px;line-height:1.5}
.ai-reasons{margin:0;padding:0 17px 13px;list-style:none}
.ai-reasons li{position:relative;margin-bottom:7px;padding-left:16px;color:var(--text-dim);font-size:10.5px;line-height:1.5}
.ai-reasons li::before{position:absolute;left:0;top:6px;width:5px;height:5px;content:"";border-radius:50%;background:var(--gold-dim)}
.ai-reasons li.tech::before{background:var(--blue)}
.ai-reasons li.fund::before{background:var(--green)}
.ai-newsbox{margin:0 17px 13px;padding:10px 12px;border:1px dashed var(--line);background:rgba(7,10,15,.4)}
.ai-newsbox h4{margin:0 0 7px;color:var(--text-faint);font:8.5px/1 "DM Mono",monospace;letter-spacing:.09em;text-transform:uppercase}
.ai-newsbox p{margin:0 0 5px;color:var(--text-dim);font-size:10px;line-height:1.45}
.ai-newsbox p i{color:var(--text-faint);font:8.5px/1 "DM Mono",monospace;font-style:normal}
.ai-foot{margin-top:auto;display:flex;align-items:center;justify-content:space-between;gap:8px;padding:10px 17px;border-top:1px solid var(--line-soft);color:var(--text-faint);font:8.5px/1.5 "DM Mono",monospace}
.ai-legend{display:flex;flex-wrap:wrap;gap:14px;margin-top:13px;padding:11px 14px;border:1px solid var(--line-soft);color:var(--text-faint);font:9px/1.6 "DM Mono",monospace}
.ai-legend span{display:inline-flex;align-items:center;gap:6px}
.ai-legend i{width:7px;height:7px;border-radius:50%}
.ai-loading{grid-column:1/-1;padding:40px 20px;color:var(--text-faint);font:10px/1.6 "DM Mono",monospace;letter-spacing:.08em;text-align:center;text-transform:uppercase}
/* ====== MODE TOUTES SECTIONS (scroll complet) ====== */
html.allpages main{display:block!important}
html.allpages main>section{display:block!important;animation:none!important}
html.allpages .site-footer{display:block!important}
html.allpages .hero{min-height:0!important;flex:none!important}
html.allpages section{scroll-margin-top:78px}
html.allpages .news-widget-grid .external-frame{display:block}
.mode-toggle{position:fixed;left:14px;bottom:14px;z-index:95;padding:10px 13px;border:1px solid var(--line);background:rgba(11,18,26,.96);color:var(--text-dim);font:9px/1 "DM Mono",monospace;letter-spacing:.07em;text-transform:uppercase;cursor:pointer;box-shadow:0 10px 24px rgba(0,0,0,.35);transition:color .15s,border-color .15s}
.mode-toggle:hover{color:var(--gold-bright);border-color:var(--gold-dim)}
/* niveaux + variation */
.ai-levels{display:flex;flex-wrap:wrap;gap:7px;padding:0 17px 12px}
.lv{padding:4px 8px;border:1px solid var(--line);color:var(--text-dim);font:8.5px/1.3 "DM Mono",monospace}
.lv b{color:var(--text);font-weight:500}
.lv.sup{border-color:rgba(80,198,136,.3)} .lv.sup b{color:var(--green)}
.lv.res{border-color:rgba(226,110,99,.3)} .lv.res b{color:var(--red)}
.lv.up{border-color:rgba(80,198,136,.3)} .lv.up b{color:var(--green)}
.lv.down{border-color:rgba(226,110,99,.3)} .lv.down b{color:var(--red)}
/* radar calendrier */
.cal-radar{padding:0;margin-bottom:13px;overflow:hidden}
.cal-head{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:10px;padding:15px 17px 12px;border-bottom:1px solid var(--line-soft)}
.cal-head h3{margin:0;font:600 18px/1.2 "Playfair Display",Georgia,serif}
.cal-list{display:grid;grid-template-columns:repeat(auto-fill,minmax(285px,1fr));gap:8px;padding:13px 15px}
.cal-ev{padding:9px 11px;border:1px solid var(--line-soft);background:rgba(7,10,15,.5);display:flex;flex-direction:column;gap:4px}
.cal-ev .when{color:var(--gold);font:9px/1.5 "DM Mono",monospace}
.cal-ev .ttl{color:var(--text);font-size:11.5px;line-height:1.4}
.cal-ev .meta{display:flex;flex-wrap:wrap;gap:6px;align-items:center;color:var(--text-faint);font:8.5px/1 "DM Mono",monospace}
.cal-ev.past{opacity:.55}
.imp{padding:2.5px 6px;border:1px solid;font:8px/1 "DM Mono",monospace;letter-spacing:.05em;text-transform:uppercase}
.imp.High{color:var(--red);border-color:rgba(226,110,99,.55);background:var(--red-soft)}
.imp.Medium{color:var(--amber);border-color:rgba(231,169,76,.5);background:var(--amber-soft)}
.imp.Low{color:var(--text-faint);border-color:var(--line)}
@media(max-width:920px){.ai-grid{grid-template-columns:1fr}}
@media(max-width:620px){.nf-item{grid-template-columns:1fr}.nf-time{white-space:normal}.ai-regimes{grid-template-columns:1fr}}
</style>
"""
html = replace_once(html, "</head>", EXTRA_CSS + "</head>", "css")

# ---------------------------------------------------------------- 3. Nav : lien Analyse IA + user chip
html = replace_once(
    html,
    '<a href="#news">News</a>',
    '<a href="#news">News</a><a href="#analysis">Analyse IA</a>',
    "nav link",
)
html = replace_once(
    html,
    '<button class="nav-toggle" id="navToggle" type="button" aria-expanded="false" aria-controls="navLinks">Menu</button>',
    '<div class="user-chip" id="userChip" hidden><span class="user-chip-name" id="userChipName"></span><button class="btn btn-small" id="logoutBtn" type="button" title="Déconnexion">⏻ <span class="logout-txt">Déconnexion</span></button></div>\n    <button class="nav-toggle" id="navToggle" type="button" aria-expanded="false" aria-controls="navLinks">Menu</button>',
    "user chip",
)

# ---------------------------------------------------------------- 4. Flux news temps réel dans la section News
LIVE_FEED = """<article class="card live-feed" id="liveFeed">
        <header class="live-feed-head"><div><h3>Flux d&rsquo;actualités temps réel</h3><p class="card-sub" style="margin:5px 0 0">Agrégation continue ForexLive · Investing.com · OilPrice · CryptoPotato — rafraichie côté serveur toutes les 3 minutes.</p></div>
        <div class="live-feed-status" id="nfStatus"><span class="source-live" style="color:var(--text-faint)"><i></i> Connexion au flux…</span></div></header>
        <div class="live-feed-filters" id="nfFilters">
          <button class="nf-chip active" data-cat="all" type="button">Tous</button>
          <button class="nf-chip" data-cat="Forex" type="button">Forex</button>
          <button class="nf-chip" data-cat="Macro" type="button">Macro</button>
          <button class="nf-chip" data-cat="Crypto" type="button">Crypto</button>
          <button class="nf-chip" data-cat="Énergie" type="button">Énergie</button>
          <button class="nf-chip hot" data-impact="high" type="button">⚡ Impact fort</button>
        </div>
        <div class="live-feed-list" id="nfList"><div class="live-feed-empty">Chargement du flux temps réel…</div></div>
      </article>
      <div class="impact-grid">"""
html = replace_once(html, '<div class="impact-grid">', LIVE_FEED, "live feed")

# ---------------------------------------------------------------- 5. Section Analyse IA (après News, avant Journal)
AI_SECTION = """<section class="container reveal" id="analysis" aria-labelledby="analysisTitle">
      <div class="section-head"><div><div class="section-index">06 — Analyse IA des marchés</div><h2 id="analysisTitle">Régime journalier &amp; hebdomadaire, avec les raisons</h2><p class="section-desc">Le moteur NEXUS AI croise l&rsquo;analyse technique (EMA 20/50, RSI, MACD, ADX, structure des plus hauts/plus bas), le calendrier économique, le contexte fondamental et les actualités à fort impact pour qualifier le régime de 13 marchés : Or, Argent, GBP/USD, EUR/USD, USD/JPY, AUD/USD, USD/CAD, DXY, US30, US100, US500, Pétrole WTI, Bitcoin. Actualisation serveur toutes les 15 minutes.</p></div><p class="section-aside">L&rsquo;analyse automatique informe le contexte : elle ne remplace ni votre plan de trade ni votre gestion du risque.</p></div>
      <div class="ai-toolbar"><p id="aiStatus"><strong>Initialisation…</strong> <em>le moteur calcule les régimes en cours.</em></p><button class="btn btn-small" id="aiRefresh" type="button">↻ Actualiser l&rsquo;analyse</button></div>
      <article class="card cal-radar" id="calRadar"><header class="cal-head"><div><h3>Radar macro de la semaine</h3><p class="card-sub" style="margin:4px 0 0">Calendrier économique ForexFactory : publications et discours à impact High/Medium, croisés avec les marchés suivis.</p></div><span class="external-source">Source · ForexFactory</span></header><div class="cal-list" id="calList"><div class="live-feed-empty">Chargement du calendrier…</div></div></article>
      <div class="ai-grid" id="aiGrid"><div class="ai-loading">Calcul des régimes journalier &amp; hebdomadaire en cours…</div></div>
      <div class="ai-legend"><span><i style="background:var(--blue)"></i> Raison technique</span><span><i style="background:var(--green)"></i> Raison fondamentale / news</span><span><i style="background:var(--gold-dim)"></i> Synthèse &amp; niveaux</span><span>MAJ serveur : <b id="aiUpdatedAt">—</b></span></div>
    </section>

    <section class="container reveal" id="journal" aria-labelledby="journalTitle">"""
html = replace_once(html, '<section class="container reveal" id="journal" aria-labelledby="journalTitle">', AI_SECTION, "ai section")

# ---------------------------------------------------------------- 6. Auth overlay + script avant </body>
AUTH_OVERLAY = """
  <!-- ================= AUTH GATE ================= -->
  <div class="auth-gate" id="authGate">
    <div class="auth-card">
      <div class="auth-brand"><span class="brand-mark" aria-hidden="true" style="display:grid;place-items:center;border:1px solid var(--gold);background:#090c12;width:38px;height:38px;color:var(--gold);font:600 15px/1 'Playfair Display',Georgia,serif">KN</span><b>KONDOLO NOEL <span>/ NEXUS</span></b></div>
      <p class="auth-sub">Poste de contrôle trading sécurisé. Créez votre compte ou connectez-vous pour accéder au Command Center, aux news temps réel et à l&rsquo;analyse IA des marchés.</p>
      <div class="auth-tabs" role="tablist">
        <button class="auth-tab active" id="tabLogin" type="button" role="tab">Connexion</button>
        <button class="auth-tab" id="tabRegister" type="button" role="tab">Créer un compte</button>
      </div>
      <form class="auth-form" id="loginForm" autocomplete="on" novalidate>
        <div class="field"><label for="loginUser">Nom d&rsquo;utilisateur</label><input id="loginUser" required autocomplete="username" placeholder="votre identifiant"></div>
        <div class="field"><label for="loginPass">Mot de passe</label><input id="loginPass" type="password" required autocomplete="current-password" placeholder="••••••••"></div>
        <div class="auth-msg" id="loginMsg"></div>
        <button class="btn btn-primary" id="loginBtn" type="submit">Se connecter</button>
      </form>
      <form class="auth-form" id="registerForm" hidden autocomplete="on" novalidate>
        <div class="field"><label for="regUser">Nom d&rsquo;utilisateur</label><input id="regUser" required minlength="3" maxlength="32" autocomplete="username" placeholder="3 à 32 caractères (lettres, chiffres, espace)"></div>
        <div class="field"><label for="regEmail">Email (optionnel)</label><input id="regEmail" type="email" autocomplete="email" placeholder="vous@exemple.com"></div>
        <div class="field"><label for="regPass">Mot de passe</label><input id="regPass" type="password" required minlength="6" autocomplete="new-password" placeholder="6 caractères minimum"></div>
        <div class="field"><label for="regPass2">Confirmer le mot de passe</label><input id="regPass2" type="password" required autocomplete="new-password" placeholder="répétez le mot de passe"></div>
        <div class="auth-msg" id="regMsg"></div>
        <button class="btn btn-primary" id="regBtn" type="submit">Créer mon compte</button>
      </form>
      <p class="auth-foot">Vos données de trading locales restent dans votre navigateur. L&rsquo;authentification protège l&rsquo;accès au dashboard et active les services serveur : news temps réel &amp; analyse IA.</p>
    </div>
  </div>
"""

CLIENT_SCRIPT = """
<script>
/* ================= NEXUS AUTH + LIVE NEWS + ANALYSE IA ================= */
(function(){
'use strict';
var TOKEN_KEY='nexus_token_v1';
function $(s){return document.querySelector(s)}
function $$(s){return Array.prototype.slice.call(document.querySelectorAll(s))}
/* Stockage du token : localStorage + sessionStorage (fallback iframes sandbox) */
function saveToken(t){try{localStorage.setItem(TOKEN_KEY,t)}catch(e){}try{sessionStorage.setItem(TOKEN_KEY,t)}catch(e){}}
function loadToken(){try{var t=localStorage.getItem(TOKEN_KEY);if(t)return t}catch(e){}try{return sessionStorage.getItem(TOKEN_KEY)}catch(e){return null}}
function clearToken(){try{localStorage.removeItem(TOKEN_KEY)}catch(e){}try{sessionStorage.removeItem(TOKEN_KEY)}catch(e){}}

/* ---------- Navigation une seule page : le menu fait défiler vers chaque section ---------- */
document.addEventListener('click',function(e){
  var t=e.target;
  var a=(t&&t.closest)?t.closest('a[href^="#"]'):null;
  if(!a)return;
  var id=(a.getAttribute('href')||'').slice(1);
  var el=id&&document.getElementById(id);
  if(!el)return;
  e.preventDefault();e.stopPropagation();
  var nl=document.getElementById('navLinks'),nt=document.getElementById('navToggle');
  if(nl)nl.classList.remove('open');
  if(nt){nt.setAttribute('aria-expanded','false');nt.textContent='Menu';}
  try{history.replaceState(null,'','#'+id)}catch(_){}
  try{el.scrollIntoView({behavior:'smooth',block:'start'})}catch(_){}
},true);

var gate=$('#authGate'), chip=$('#userChip'), chipName=$('#userChipName');
var user=null, newsTimer=null, aiTimer=null, statusTimer=null;
var nfState={cat:'all',impact:false,items:[],updated:null,refresh:180};
var aiState={updated:null,refresh:900};

/* ---------- API ---------- */
function api(path,opts){
  opts=opts||{};
  var headers=opts.headers||{};
  var tok=loadToken();
  if(tok){
    headers['Authorization']='Bearer '+tok;
    // Repli : certains proxys retirent le header Authorization -> token aussi en query string
    path+=(path.indexOf('?')===-1?'?':'&')+'token='+encodeURIComponent(tok);
  }
  if(opts.body) headers['Content-Type']='application/json';
  return fetch(path,{method:opts.method||'GET',headers:headers,body:opts.body?JSON.stringify(opts.body):undefined}).catch(function(){
    var e=new Error('Serveur NEXUS injoignable. Ouvrez l\u2019application via la preview du serveur, pas le fichier HTML seul.');
    e.network=true; throw e;
  }).then(function(res){
    return res.json().catch(function(){return {}}).then(function(data){
      if(!res.ok) { var e=new Error(data.error||('Erreur '+res.status)); e.status=res.status; throw e; }
      return data;
    });
  });
}

/* ---------- Verbes UI ---------- */
function setMsg(sel,txt,ok){var el=$(sel);el.textContent=txt||'';el.classList.toggle('ok',!!ok)}
function btnLoading(btn,on,label){if(!btn)return;btn.disabled=on;if(on){btn.dataset.label=btn.textContent;btn.textContent=label||'…'}else if(btn.dataset.label){btn.textContent=btn.dataset.label}}

/* ---------- Auth ---------- */
function showTab(which){
  var login=which==='login';
  $('#tabLogin').classList.toggle('active',login);
  $('#tabRegister').classList.toggle('active',!login);
  $('#loginForm').hidden=!login;
  $('#registerForm').hidden=login;
}
$('#tabLogin').addEventListener('click',function(){showTab('login')});
$('#tabRegister').addEventListener('click',function(){showTab('register')});

$('#loginForm').addEventListener('submit',function(ev){
  ev.preventDefault();
  var u=$('#loginUser').value.trim(), p=$('#loginPass').value;
  if(!u||!p){setMsg('#loginMsg','Renseignez votre nom d\u2019utilisateur et votre mot de passe.');return}
  var btn=$('#loginBtn');
  setMsg('#loginMsg','');
  btnLoading(btn,true,'Connexion…');
  api('/api/login',{method:'POST',body:{username:u,password:p}})
    .then(function(d){saveToken(d.token);user=d.user;enterApp()})
    .catch(function(e){setMsg('#loginMsg',e.message)})
    .then(function(){btnLoading(btn,false)});
});

$('#registerForm').addEventListener('submit',function(ev){
  ev.preventDefault();
  var u=$('#regUser').value.trim(), p1=$('#regPass').value,p2=$('#regPass2').value;
  if(u.length<3||u.length>32){setMsg('#regMsg','Nom d\u2019utilisateur : 3 à 32 caractères (lettres, chiffres, espace, _ . -).');return}
  if(p1.length<6){setMsg('#regMsg','Mot de passe trop court : 6 caractères minimum.');return}
  if(p1!==p2){setMsg('#regMsg','Les mots de passe ne correspondent pas.');return}
  var btn=$('#regBtn');
  setMsg('#regMsg','');
  btnLoading(btn,true,'Création…');
  api('/api/register',{method:'POST',body:{username:u,email:$('#regEmail').value.trim(),password:p1}})
    .then(function(d){saveToken(d.token);user=d.user;enterApp()})
    .catch(function(e){setMsg('#regMsg',e.message)})
    .then(function(){btnLoading(btn,false)});
});

$('#logoutBtn').addEventListener('click',function(){
  clearToken();
  location.reload();
});

function enterApp(){
  document.body.classList.remove('locked');
  gate.hidden=true;
  chip.hidden=false;
  chipName.textContent='● '+(user||'');
  startLive();
}

/* ---------- Horodatage relatif ---------- */
function ago(ts){
  var s=Math.max(1,Math.floor(Date.now()/1000-ts));
  if(s<60)return 'il y a '+s+' s';
  var m=Math.floor(s/60); if(m<60)return 'il y a '+m+' min';
  var h=Math.floor(m/60); if(h<24)return 'il y a '+h+' h';
  return 'il y a '+Math.floor(h/24)+' j';
}
function fmtPrice(p){
  if(p==null||isNaN(p))return '—';
  var d=p>=1000?1:(p>=50?2:(p>=2?3:5));
  return p.toLocaleString('fr-FR',{minimumFractionDigits:Math.min(d,4),maximumFractionDigits:d});
}

/* ---------- News temps réel ---------- */
function renderNews(){
  var list=$('#nfList');
  var items=nfState.items.filter(function(it){
    var okCat=nfState.cat==='all'||it.category===nfState.cat;
    var okImp=!nfState.impact||it.impact==='high';
    return okCat&&okImp;
  });
  if(!items.length){list.innerHTML='<div class="live-feed-empty">Aucune actualité pour ce filtre.</div>';return}
  list.innerHTML=items.slice(0,60).map(function(it){
    var catCls='cat-'+String(it.category).normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').replace(/[^A-Za-z]/g,'');
    var when=new Date(it.timestamp*1000);
    var clock=when.toLocaleTimeString('fr-FR',{hour:'2-digit',minute:'2-digit'});
    return '<div class="nf-item">'
      +'<div class="nf-time">'+ago(it.timestamp)+'<small>'+clock+' UTC</small></div>'
      +'<div><p class="nf-title"><a href="'+(it.link||'#')+'" target="_blank" rel="noopener noreferrer">'+esc(it.title)+'</a></p>'
      +(it.summary?'<p class="nf-sum">'+esc(it.summary)+'</p>':'')
      +'<div class="nf-meta"><span class="nf-src">'+esc(it.source)+'</span><span class="nf-tag '+catCls+'">'+esc(it.category)+'</span>'
      +(it.impact==='high'?'<span class="nf-tag hi">⚡ impact fort</span>':'')
      +'</div></div></div>';
  }).join('');
}
function esc(s){return String(s||'').replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',\"'\":'&#39;'}[c]})}

function updateNfStatus(){
  var el=$('#nfStatus');
  if(!nfState.updated){el.innerHTML='<span class="source-live" style="color:var(--text-faint)"><i></i> Synchronisation…</span>';return}
  el.innerHTML='<span class="source-live"><i></i> LIVE</span> · dernière synchro serveur <b>'+ago(nfState.updated)+'</b> · '+nfState.items.length+' dépêches';
}

function fetchNews(){
  api('/api/news?limit=120').then(function(d){
    nfState.items=d.items||[];
    nfState.updated=d.updated_at;
    nfState.refresh=d.refresh_interval||180;
    renderNews();updateNfStatus();
  }).catch(function(){
    $('#nfStatus').innerHTML='<span style="color:var(--red)">Flux indisponible — vérifiez le serveur.</span>';
    $('#nfList').innerHTML='<div class="live-feed-empty">Impossible de joindre le backend /api/news.</div>';
  });
}

$$('#nfFilters .nf-chip').forEach(function(btn){
  btn.addEventListener('click',function(){
    if(btn.dataset.impact){
      nfState.impact=!nfState.impact;
      btn.classList.toggle('active',nfState.impact);
    }else{
      nfState.cat=btn.dataset.cat;
      $$('#nfFilters .nf-chip').forEach(function(b){if(!b.dataset.impact)b.classList.toggle('active',b===btn)});
    }
    renderNews();
  });
});

/* ---------- Analyse IA ---------- */
function regimeClass(r){
  if(/HAUSSIER/.test(r))return 'up';
  if(/BAISSIER/.test(r))return 'down';
  if(/RANGE|NEUTRE/.test(r))return 'flat';
  return 'mix';
}
function reasonsHtml(arr,cls){
  return (arr||[]).map(function(r){return '<li class="'+cls+'">'+esc(r)+'</li>'}).join('');
}
function chgmt(v){
  if(v==null||isNaN(v))return '—';
  return (v>0?'+':'')+v.toLocaleString('fr-FR',{maximumFractionDigits:2})+'%';
}
function levelsHtml(a){
  var lv=a.levels||{}, c=a.change||{};
  var parts='';
  if(lv.support!=null)parts+='<span class="lv sup">S <b>'+fmtPrice(lv.support)+'</b></span>';
  if(lv.resistance!=null)parts+='<span class="lv res">R <b>'+fmtPrice(lv.resistance)+'</b></span>';
  return parts?'<div class="ai-levels">'+parts+'</div>':'';
}
/* ---------- Calendrier économique ---------- */
function fetchCalendar(){
  api('/api/calendar?limit=80').then(function(d){
    renderCalendar(d.events||[]);
  }).catch(function(){
    var el=$('#calList');if(el)el.innerHTML='<div class="live-feed-empty">Calendrier indisponible.</div>';
  });
}
function renderCalendar(events){
  var el=$('#calList');if(!el)return;
  var hi=events.filter(function(e){return e.impact==='High'||e.impact==='Medium'});
  hi.sort(function(a,b){
    var now=Date.now()/1000;
    var da=Math.abs(a.timestamp-now), db=Math.abs(b.timestamp-now);
    return da-db;
  });
  if(!hi.length){el.innerHTML='<div class="live-feed-empty">Aucun événement High/Medium cette semaine.</div>';return}
  el.innerHTML=hi.slice(0,18).map(function(e){
    var d=new Date(e.timestamp*1000);
    var when=(e.past?'✔ publié':'⏳ prévu')+' · '+d.toLocaleString('fr-FR',{weekday:'short',day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'});
    var nums=[];
    if(e.forecast)nums.push('prév. '+esc(e.forecast));
    if(e.previous)nums.push('préc. '+esc(e.previous));
    return '<div class="cal-ev'+(e.past?' past':'')+'">'
      +'<span class="when">'+when+'</span>'
      +'<span class="ttl">'+esc(e.title)+'</span>'
      +'<span class="meta"><span class="imp '+esc(e.impact)+'">'+esc(e.impact)+'</span><span>'+esc(e.country)+'</span>'+(nums.length?'<span>'+nums.join(' · ')+'</span>':'')+'</span>'
      +'</div>';
  }).join('');
}
function renderAnalysis(d){
  var grid=$('#aiGrid');
  var entries=Object.keys(d.analysis||{}).map(function(k){return d.analysis[k]}).filter(function(a){return !a.error});
  if(!entries.length){grid.innerHTML='<div class="ai-loading">Aucune analyse disponible — le serveur récupère les données de marché…</div>';return}
  grid.innerHTML=entries.map(function(a){
    var dr=a.daily||{}, wr=a.weekly||{};
    var dCls=regimeClass(dr.regime||''), wCls=regimeClass(wr.regime||'');
    var conf=Math.round(((dr.strength||0)+(wr.strength||0))/2);
    var news=(a.news||[]).map(function(n){return '<p>«&nbsp;'+esc(n.title)+'&nbsp;» <i>— '+esc(n.source)+(n.impact==='high'?' · ⚡ impact fort':'')+'</i></p>'}).join('')
      ||'<p style="color:var(--text-faint)">Pas d&rsquo;actualité spécifique détectée sur les dernières heures.</p>';
    return '<article class="ai-card">'
      +'<header class="ai-head"><div><h3>'+esc(a.name)+'</h3><div class="ai-sym">'+esc(a.symbol)+' · '+esc(a.group)+'</div></div>'
      +'<div class="ai-price">'+fmtPrice(a.price)+'<small>'+(a.currency||'')+' · MAJ '+ago(d.updated_at)+'</small></div></header>'
      +'<div class="ai-regimes">'
      +'<div class="ai-regime"><span class="ai-tf">Régime journalier (D1)</span><span class="regime-badge '+dCls+'">'+esc(dr.regime||'—')+'</span>'
      +'<div class="ai-conf"><span>force</span><span class="ai-conf-bar"><i style="width:'+(dr.strength||0)+'%"></i></span><span>'+(dr.strength||0)+'%</span></div></div>'
      +'<div class="ai-regime"><span class="ai-tf">Régime hebdomadaire (W1)</span><span class="regime-badge '+wCls+'">'+esc(wr.regime||'—')+'</span>'
      +'<div class="ai-conf"><span>force</span><span class="ai-conf-bar"><i style="width:'+(wr.strength||0)+'%"></i></span><span>'+(wr.strength||0)+'%</span></div></div>'
      +'</div>'
      +'<p class="ai-bias"><b>Biais :</b> '+esc(a.bias||'—')+'</p>'
      +'<ul class="ai-reasons">'
      +reasonsHtml(dr.reasons,'tech')+reasonsHtml(wr.reasons.map(function(r){return '[W1] '+r}),'tech')
      +reasonsHtml(a.fundamental,'fund')
      +'</ul>'
      +levelsHtml(a)
      +'<div class="ai-newsbox"><h4>Contexte actualités ('+esc(a.symbol)+')</h4>'+news+'</div>'
      +'<footer class="ai-foot"><span>RSI D1 '+(dr.rsi!=null?dr.rsi:'—')+' · ADX D1 '+(dr.adx!=null?dr.adx:'—')+' · '+chgmt(a.change&&a.change.d5)+' / 5j · '+chgmt(a.change&&a.change.d20)+' / 20j</span><span>'+esc(a.symbol)+'</span></footer>'
      +'</article>';
  }).join('');
}
function updateAiStatus(d){
  var st=$('#aiStatus');
  if(d&&d.updated_at){
    st.innerHTML='<strong>Synchronisé</strong> <em>· dernière analyse '+ago(d.updated_at)+' · prochain calcul automatique dans '+Math.round((d.refresh_interval||900)/60)+' min</em>';
    $('#aiUpdatedAt').textContent=new Date(d.updated_at*1000).toLocaleString('fr-FR');
  }else{
    st.innerHTML='<strong>Initialisation…</strong> <em>le moteur calcule les régimes en cours.</em>';
  }
}
function fetchAnalysis(force){
  var btn=$('#aiRefresh');
  var doFetch=function(){
    api('/api/analysis').then(function(d){
      aiState.updated=d.updated_at||aiState.updated;
      renderAnalysis(d);updateAiStatus(d);
      return d;
    }).catch(function(){
      $('#aiGrid').innerHTML='<div class="ai-loading">Backend injoignable (/api/analysis). Vérifiez que le serveur tourne.</div>';
      return null;
    });
  };
  if(!force){doFetch();return}
  // Recalcul forcé : déclenche côté serveur puis attend la nouvelle version.
  btn.disabled=true;btn.textContent='Recalcul en cours…';
  var oldTs=aiState.updated||0;
  var st=$('#aiStatus');
  st.innerHTML='<strong>Recalcul demandé…</strong> <em>le moteur actualise les régimes (± 15 s).</em>';
  api('/api/analysis/refresh',{method:'POST'}).catch(function(){});
  var tries=0;
  var poll=setInterval(function(){
    tries++;
    api('/api/analysis').then(function(d){
      if(d.updated_at&&d.updated_at>oldTs){
        clearInterval(poll);
        aiState.updated=d.updated_at;
        renderAnalysis(d);updateAiStatus(d);
        btn.disabled=false;btn.textContent='↻ Actualiser l\\u2019analyse';
      }else if(tries>=20){
        clearInterval(poll);
        renderAnalysis(d);updateAiStatus(d);
        btn.disabled=false;btn.textContent='↻ Actualiser l\\u2019analyse';
      }
    }).catch(function(){
      if(tries>=20){clearInterval(poll);btn.disabled=false;btn.textContent='↻ Actualiser l\\u2019analyse'}
    });
  },2000);
}
$('#aiRefresh').addEventListener('click',function(){fetchAnalysis(true)});

/* ---------- Boucles temps réel ---------- */
var calTimer=null;
function startLive(){
  fetchNews();
  fetchAnalysis();
  fetchCalendar();
  if(newsTimer)clearInterval(newsTimer);
  newsTimer=setInterval(fetchNews,60000);          // resynchro client chaque minute
  if(aiTimer)clearInterval(aiTimer);
  aiTimer=setInterval(function(){fetchAnalysis()},5*60000);
  if(calTimer)clearInterval(calTimer);
  calTimer=setInterval(fetchCalendar,5*60000);     // calendrier resynchro toutes les 5 min
  if(statusTimer)clearInterval(statusTimer);
  statusTimer=setInterval(updateNfStatus,15000);   // compte à rebours affiché
}

/* ---------- Init : session existante ? ---------- */
(function init(){
  document.body.classList.add('locked');
  var tok=loadToken();
  if(!tok){gate.hidden=false;return}
  api('/api/whoami').then(function(d){user=d.user;enterApp()})
    .catch(function(){clearToken();gate.hidden=false;document.body.classList.remove('locked')});
})();
})();
</script>
"""

html = replace_once(html, "</body>", AUTH_OVERLAY + CLIENT_SCRIPT + "</body>", "auth+script")

with io.open(DST, "w", encoding="utf-8") as f:
    f.write(html)

print("OK ->", DST, len(html), "octets")
