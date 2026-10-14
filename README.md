# NEXUS Command — V4 Backend + Frontend

Dashboard de trading **KONDOLO NOEL / NEXUS** enrichi de trois nouveaux systèmes :

## 1. 🔐 Authentification (création de compte + connexion)
- Écran d'accueil verrouillé : impossible d'accéder au Command Center sans compte.
- Onglets **Connexion** / **Créer un compte** (pseudo 3–32 caractères, mot de passe ≥ 6 caractères, email optionnel).
- Mots de passe hachés **PBKDF2-HMAC-SHA256** (120 000 itérations + sel aléatoire) — jamais stockés en clair.
- Session par **token signé HMAC-SHA256** (validité 7 jours), envoyé via header `Authorization: Bearer …` avec repli en query string `?token=…` (résistant aux proxys qui retirent le header).
- Utilisateurs stockés dans `nexus.db` (SQLite). Bouton **Déconnexion** dans la barre de navigation (à côté du pseudo).

## 2. 📡 Actualités en temps réel
Section **News** → carte **« Flux d'actualités temps réel »** :
- Agrégation côté serveur de sources RSS : **ForexLive, Investing.com (Top + Forex), OilPrice, CryptoPotato**.
- Rafraîchissement serveur **toutes les 3 minutes** ; resynchronisation du navigateur toutes les 60 s.
- Indicateur **LIVE**, horodatage relatif (« il y a 2 min »), heure UTC.
- Filtres : Tous / Forex / Macro / Crypto / Énergie + bouton **⚡ Impact fort** (détection par mots-clés : FOMC, Fed, NFP, CPI, BCE, BoE, OPEC…).
- Les widgets externes Tradays / Dukascopy restent en place dans la section.

## 3. 🤖 Section « Analyse IA des marchés » (nouvelle section 06)
Le moteur calcule pour chaque marché le **régime JOURNALIER (D1)** et le **régime HEBDOMADAIRE (W1)** :
`HAUSSIER FORT / HAUSSIER / BAISSIER / BAISSIER FORT / RANGE-NEUTRE`, avec :
- **Force de la tendance** (0–100 %), **RSI 14**, **ADX (lissage de Wilder)**.
- **Niveaux clés** : support / résistance (pivots fractals) + variation 5j / 20j.
- **Raisons détaillées** de l'analyse, classées :
  - 🔵 *Technique* : alignement EMA 20/50, RSI, histogramme MACD, ADX, proximité des plus hauts/bas récents.
  - 🟢 *Fondamentale / news / calendrier* : actualités à fort impact ET événements macro (FOMC, NFP, CPI, discours de banques centrales…) croisés avec le marché.
- **Biais global** : alignement ou divergence D1 ↔ W1.
- **Radar macro de la semaine** : calendrier économique ForexFactory (impact High/Medium), affiché et croisé avec chaque marché.

### Marchés suivis — 13 (données Yahoo Finance, sans clé API)
Or, Argent, GBP/USD, EUR/USD, USD/JPY, AUD/USD, USD/CAD, DXY, US30, US100, US500, Pétrole WTI, Bitcoin.

- Actualisation serveur **toutes les 15 min** + bouton **« ↻ Actualiser l'analyse »** (recalcul à la demande via `POST /api/analysis/refresh`).

## 4. 📅 Calendrier économique (ForexFactory)
- Flux JSON hebdomadaire `ff_calendar_thisweek.json`, rafraîchi **toutes les 30 min**.
- Carte **« Radar macro de la semaine »** dans la section Analyse IA : événements High/Medium triés par proximité, avec prévision/précédent et statut publié/à venir.
- Chaque événement est rattaché aux marchés concernés (USD → DXY/Or/Indices, GBP → GBPUSD, CAD → USDCAD/WTI, etc.) et injecté dans les raisons fondamentales de l'analyse.

## API (Flask, port 8000)
| Méthode | Route | Description |
|---|---|---|
| POST | `/api/register` | Créer un compte `{username, password, email?}` → `{token}` |
| POST | `/api/login` | Connexion `{username, password}` → `{token}` |
| GET | `/api/whoami` | Vérifie le token (header ou `?token=`) |
| GET | `/api/news?limit=&category=&impact=` | Flux d'actualités temps réel |
| GET | `/api/analysis` | Analyse IA de tous les marchés |
| GET | `/api/analysis/<SYMBOL>` | Analyse fraîche d'un marché (ex. `XAUUSD`) |
| POST | `/api/analysis/refresh` | Force le recalcul en arrière-plan |
| GET | `/api/calendar?impact=&country=&upcoming=&limit=` | Calendrier économique ForexFactory |
| GET | `/api/markets` | Liste des marchés suivis |
| GET | `/api/health` | État serveur + fraîcheur des caches |

## Démarrage
```bash
cd nexus-app
pip install flask requests
python3 server.py          # http://0.0.0.0:8000
```

## 🌍 Hébergement en ligne
Voir **`HEBERGEMENT.md`** : guide pas à pas pour Render.com (gratuit), ngrok/Cloudflare Tunnel (depuis votre PC), VPS Ubuntu + Nginx + HTTPS, ou Docker. Fichiers fournis : `requirements.txt`, `Procfile`, `render.yaml`, `Dockerfile`.

## Indicateur MetaTrader 5
Le code MQL5 de l'indicateur **Accurate Trend Indicator** se trouve dans `MQL5/Indicators/AccurateTrendIndicator.mq5`. Il affiche des bougies colorées et des étiquettes BUY/SELL, avec alertes texte, son et push mobile déclenchées en temps réel. Installation, paramètres et configuration du push : voir `MQL5/README.md`.

## Fichiers
- `server.py` — backend complet (auth, news, analyse IA)
- `static/index.html` — dashboard NEXUS V4 (build du fichier d'origine patché)
- `build_frontend.py` — script qui re-patche le HTML d'origine (reproductible)
- `nexus.db` — base utilisateurs (créée au premier lancement)
- `.secret_key` — clé de signature des tokens (générée automatiquement)

> ⚠️ Les analyses sont générées automatiquement à titre informatif : ce ne sont pas des conseils financiers.
