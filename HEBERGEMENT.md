# 🌍 Héberger NEXUS Command — guide pas à pas

Votre application = **1 backend Python (Flask/Gunicorn) + 1 fichier HTML**. Elle a besoin de :
- Python 3.9+ avec `flask` et `requests`
- Un accès Internet **sortant** (Yahoo Finance, flux RSS, ForexFactory)
- Un dossier persistant pour `data/` (comptes utilisateurs + clé de session)

Fichiers fournis pour le déploiement : `requirements.txt`, `Procfile`, `render.yaml`, `Dockerfile`.

---

## Option 1 — Render.com ⭐ recommandé (gratuit, HTTPS automatique)

1. Créez un compte sur [render.com](https://render.com) (connexion GitHub).
2. Poussez le dossier `nexus-app` sur un dépôt GitHub :
   ```bash
   git init && git add -A && git commit -m "NEXUS V4"
   git remote add origin https://github.com/VOTRE_PSEUDO/nexus.git
   git push -u origin main
   ```
3. Render → **New → Web Service** → choisissez le dépôt.
4. Render lit `render.yaml` tout seul (build `pip install -r requirements.txt`, démarrage gunicorn).
5. En ~2 min vous obtenez une URL publique `https://nexus-command.onrender.com` avec **HTTPS**.

⚠️ Plan gratuit : le disque est réinitialisé à chaque **redéploiement** (les comptes créés repartent de zéro ; votre code, lui, reste). Pour conserver les comptes :
- ajouter un **disque persistant** monté sur `/opt/render/project/src/data` (quelques $/mois), ou
- redéployer rarement (le plan gratuit « sleep » se réveille juste au premier visiteur, sans perte).

---

## Option 2 — Cloudflare Tunnel / ngrok (le plus rapide, depuis votre PC)

Idéal pour utiliser l'app chez vous sans toucher au routeur, avec une URL publique HTTPS :

1. Sur votre ordinateur : `pip install flask requests gunicorn` puis dans `nexus-app` :
   ```bash
   gunicorn --bind 0.0.0.0:8000 --workers 2 --threads 4 server:app
   ```
2. Ouvrez un tunnel gratuit :
   - **ngrok** : `ngrok http 8000` → URL `https://xxxx.ngrok.io`
   - ou **cloudflared** : `cloudflared tunnel --url http://localhost:8000`
3. Partagez l'URL : votre dashboard est accessible partout, HTTPS inclus.
   (Le PC doit rester allumé ; pour du 24h/24, préférez l'option 1 ou 3.)

---

## Option 3 — VPS Ubuntu (contrôle total, ~4-6 €/mois, données persistantes)

Chez Hetzner / OVH / Contabo / DigitalOcean (Ubuntu 22.04+) :

```bash
# 1. Système
sudo apt update && sudo apt install -y python3-pip python3-venv nginx certbot python3-certbot-nginx unzip

# 2. Monter le projet
sudo mkdir -p /opt/nexus && sudo chown $USER /opt/nexus
#    (copiez le contenu de nexus-app dans /opt/nexus via scp, git ou upload)

# 3. Environnement Python
cd /opt/nexus
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# 4. Service systemd
sudo tee /etc/systemd/system/nexus.service > /dev/null <<EOF
[Unit]
Description=NEXUS Command
After=network.target
[Service]
User=$USER
WorkingDirectory=/opt/nexus
ExecStart=/opt/nexus/.venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 2 --threads 4 server:app
Restart=always
[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload && sudo systemctl enable --now nexus

# 5. Nginx + HTTPS
sudo tee /etc/nginx/sites-available/nexus > /dev/null <<EOF
server {
    listen 80;
    server_name VOTRE-DOMAINE.com;   # ou l'IP du VPS
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF
sudo ln -s /etc/nginx/sites-available/nexus /etc/nginx/sites-enabled/ && sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d VOTRE-DOMAINE.com    # HTTPS gratuit Let's Encrypt (sautez si vous utilisez l'IP seule)
```

Vos données (`/opt/nexus/data/`) restent sur le disque : comptes conservés, sauvegardes faciles (`cp data/nexus.db`).

---

## Option 4 — Docker (n'importe quel hébergeur)

```bash
docker build -t nexus-command .
docker run -d --name nexus -p 8000:8000 -v nexus-data:/app/data --restart unless-stopped nexus-command
```
Le volume `nexus-data` conserve comptes et clé entre les mises à jour.

---

## 🔒 Après la mise en ligne
- L'HTTPS est **obligatoire et déjà prévu** : les navigateurs n'acceptent le stockage de session que sur HTTPS ou localhost.
- Le premier visiteur crée son compte depuis l'écran de connexion ; les mots de passe sont hachés (PBKDF2), jamais en clair.
- Sauvegarde : copiez régulièrement `data/nexus.db` (comptes) — c'est le seul fichier critique.

## ❓ Quelle option choisir ?
| Besoin | Choix |
|---|---|
| En ligne en 5 min, gratuit | **Render.com** (option 1) |
| Depuis votre PC, sans config réseau | **ngrok / cloudflared** (option 2) |
| 24h/24 + données durables + votre domaine | **VPS** (option 3) |
| Vous maîtrisez Docker | option 4 |
