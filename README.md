# 🤖 Instagram Business Growth Bot

Bot automatisé pour faire croître une page business Instagram :
- ✅ Follow automatique de comptes ciblés (par hashtag)
- ✅ Unfollow automatique après 7 jours si pas de follow-back
- ✅ Délais humains pour éviter les bans
- ✅ Filtres qualité (élimine les bots et inactifs)
- ✅ Base de données locale de suivi
- ✅ Stats détaillées

---

## 📦 Installation

### 1. Prérequis
- Python 3.9+
- pip

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Configurer tes identifiants
```bash
cp .env.example .env
```
Édite `.env` et remplis :
```
IG_USERNAME=ton_username
IG_PASSWORD=ton_mot_de_passe
```

Ou directement dans `bot.py` dans la section `CONFIG`.

---

## ⚙️ Configuration (dans bot.py)

```python
CONFIG = {
    # Hashtags à cibler (business, ta niche)
    "target_hashtags": [
        "entrepreneuriat",
        "businessowner",
        "ecommercefrance",
        # Ajoute tes hashtags de niche ici
    ],

    # Limites journalières (NE PAS dépasser 30 follows/jour)
    "daily_follow_limit": 25,
    "daily_unfollow_limit": 20,

    # Unfollow si pas de follow-back après X jours
    "unfollow_after_days": 7,

    # Filtres : type de comptes à cibler
    "min_followers": 100,      # Au moins 100 followers
    "max_followers": 50000,    # Max 50k (influenceurs ciblables)
    "min_posts": 5,            # Compte actif
}
```

---

## 🚀 Utilisation

```bash
python bot.py
```

Menu :
```
1. Session unique (maintenant)      → Lance une session complète
2. Mode continu (toutes les 24h)    → Tourne en arrière-plan
3. Stats seulement                  → Voir tes statistiques
4. Unfollow seulement               → Nettoyer tes follows
```

---

## 🗃️ Fichiers générés

| Fichier | Description |
|---------|-------------|
| `follow_database.json` | Historique de tous tes follows/unfollows |
| `session.json` | Session Instagram (ne pas partager) |

---

## 📊 Exemple de stats

```
╔══════════════════════════════════════╗
║         📊 STATISTIQUES              ║
╠══════════════════════════════════════╣
║  Aujourd'hui:                        ║
║    • Follows:           23           ║
║    • Unfollows:         15           ║
╠══════════════════════════════════════╣
║  Total:                              ║
║    • Actuellement suivis:   312      ║
║    • Follow-backs:           89      ║
║    • Taux conversion:      28.5%     ║
║    • Total unfollowed:      156      ║
╚══════════════════════════════════════╝
```

---

## ⚠️ Règles de sécurité (IMPORTANT)

1. **Max 25-30 follows/jour** — Instagram détecte les volumes anormaux
2. **Ne jamais tourner H24 les premiers jours** — commence doucement
3. **Utilise un compte secondaire d'abord** pour tester
4. **Ne pas changer de réseau IP trop souvent** — utilise toujours le même Wi-Fi ou un VPN fixe
5. **Active la 2FA sur ton compte** Instagram pour le protéger

---

## 🔧 Lancer en arrière-plan (Linux/Mac)

```bash
# Lancer en background
nohup python bot.py > bot.log 2>&1 &

# Voir les logs
tail -f bot.log

# Arrêter
kill $(pgrep -f bot.py)
```

### Avec un cron job (toutes les 24h à 9h du matin) :
```bash
crontab -e
# Ajouter :
0 9 * * * cd /chemin/vers/bot && python bot.py << 'EOF'
1
EOF
```

---

## 📌 Hashtags business recommandés (France)

```python
"target_hashtags": [
    "entrepreneuriat", "businessowner", "startupfrancaise",
    "marketingdigital", "ecommercefrance", "entrepreneur",
    "smallbusiness", "croissanceentreprise", "businesscoach",
    "autoentrepreneur", "reseauxsociaux", "digitalmarketing",
]
```
