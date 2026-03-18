# Instagram Business Growth Bot
# Follow automatique - Unfollow apres 7 jours sans follow-back

import time
import random
import json
import os
from datetime import datetime, timedelta
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, UserNotFound

CONFIG = {
"username": os.getenv("IG_USERNAME"),
"password": os.getenv("IG_PASSWORD"),
“target_hashtags”: [
“entrepreneuriat”,
“businessowner”,
“startupfrancaise”,
“marketingdigital”,
“ecommercefrance”,
“entrepreneur”,
“smallbusiness”,
],
“daily_follow_limit”: 20,
“daily_unfollow_limit”: 15,
“delay_between_follows”: (45, 120),
“delay_between_sessions”: (3600, 7200),
“unfollow_after_days”: 7,
“min_followers”: 100,
“max_followers”: 50000,
“min_posts”: 5,
“max_following_ratio”: 10,
}

DB_FILE = “follow_database.json”

def load_db():
if os.path.exists(DB_FILE):
with open(DB_FILE, “r”) as f:
return json.load(f)
return {
“followed”: {},
“unfollowed”: [],
“daily_stats”: {},
“blacklist”: [],
}

def save_db(db):
with open(DB_FILE, “w”) as f:
json.dump(db, f, indent=2, default=str)

def get_today_stats(db):
today = str(datetime.now().date())
if today not in db[“daily_stats”]:
db[“daily_stats”][today] = {“follows”: 0, “unfollows”: 0}
return db[“daily_stats”][today]

class InstagramGrowthBot:
def **init**(self):
self.client = Client()
proxy_host = os.getenv(“PROXY_HOST”)
proxy_port = os.getenv(“PROXY_PORT”)
proxy_user = os.getenv(“PROXY_USER”)
proxy_pass = os.getenv(“PROXY_PASS”)
if proxy_host:
proxy_url = f”http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}”
self.client.set_proxy(proxy_url)
print(f”Proxy configuré: {proxy_host}”)
self.db = load_db()
self.session_file = “session.json”

```
def login(self):
    print(f"[{self._now()}] Connexion à Instagram...")
    try:
        self.client.login(CONFIG["username"], CONFIG["password"])
        print(f"[{self._now()}] ✅ Connecté avec succès")
        return True
    except Exception as e:
        print(f"[{self._now()}] ❌ Erreur login: {e}")
        return False

def is_quality_account(self, user_info):
    followers = user_info.follower_count
    following = user_info.following_count
    posts = user_info.media_count
    if followers < CONFIG["min_followers"]:
        return False
    if followers > CONFIG["max_followers"]:
        return False
    if posts < CONFIG["min_posts"]:
        return False
    if followers > 0 and (following / max(followers, 1)) > CONFIG["max_following_ratio"]:
        return False
    if user_info.is_private:
        return False
    return True

def human_delay(self, delay_range):
    delay = random.uniform(*delay_range)
    print(f"[{self._now()}] ⏳ Pause {delay:.0f}s...")
    time.sleep(delay)

def follow_by_hashtag(self, hashtag, limit):
    stats = get_today_stats(self.db)
    followed_count = 0
    print(f"\n[{self._now()}] 🔍 Recherche via #{hashtag}...")
    try:
        medias = self.client.hashtag_medias_recent(hashtag, amount=50)
    except Exception as e:
        print(f"[{self._now()}] ❌ Erreur hashtag {hashtag}: {e}")
        return 0

    random.shuffle(medias)

    for media in medias:
        if followed_count >= limit:
            break
        if stats["follows"] >= CONFIG["daily_follow_limit"]:
            print(f"[{self._now()}] 🛑 Limite journalière atteinte")
            break

        user_id = str(media.user.pk)
        username = media.user.username

        if user_id in self.db["followed"]:
            continue
        if user_id in self.db["unfollowed"]:
            continue
        if user_id in self.db["blacklist"]:
            continue
        if username == CONFIG["username"]:
            continue

        try:
            user_info = self.client.user_info(user_id)
            if not self.is_quality_account(user_info):
                print(f"[{self._now()}] ⏭️  Skip @{username}")
                continue

            self.client.user_follow(user_id)
            self.db["followed"][user_id] = {
                "username": username,
                "followed_at": str(datetime.now()),
                "follow_back": False,
                "followers": user_info.follower_count,
            }
            stats["follows"] += 1
            followed_count += 1
            save_db(self.db)
            print(f"[{self._now()}] ✅ Follow @{username} ({user_info.follower_count:,} followers)")
            self.human_delay(CONFIG["delay_between_follows"])

        except (UserNotFound, Exception) as e:
            print(f"[{self._now()}] ⚠️  Erreur @{username}: {e}")
            time.sleep(30)

    return followed_count

def check_follow_backs(self):
    print(f"\n[{self._now()}] 🔄 Vérification des follow-backs...")
    try:
        followers = self.client.user_followers(self.client.user_id, amount=500)
        follower_ids = {str(uid) for uid in followers.keys()}
    except Exception as e:
        print(f"[{self._now()}] ❌ Erreur: {e}")
        return

    updated = 0
    for user_id, data in self.db["followed"].items():
        if not data["follow_back"] and user_id in follower_ids:
            self.db["followed"][user_id]["follow_back"] = True
            print(f"[{self._now()}] 💚 @{data['username']} nous a follow back!")
            updated += 1

    if updated > 0:
        save_db(self.db)
    print(f"[{self._now()}] ℹ️  {updated} nouveaux follow-backs")

def unfollow_non_followers(self):
    stats = get_today_stats(self.db)
    unfollow_limit = datetime.now() - timedelta(days=CONFIG["unfollow_after_days"])
    unfollowed_count = 0

    print(f"\n[{self._now()}] 🗑️  Recherche comptes à unfollow...")

    to_unfollow = []
    for user_id, data in self.db["followed"].items():
        if data["follow_back"]:
            continue
        followed_at = datetime.fromisoformat(data["followed_at"])
        if followed_at < unfollow_limit:
            to_unfollow.append((user_id, data))

    print(f"[{self._now()}] 📋 {len(to_unfollow)} comptes à unfollow")

    for user_id, data in to_unfollow:
        if stats["unfollows"] >= CONFIG["daily_unfollow_limit"]:
            break
        try:
            self.client.user_unfollow(user_id)
            self.db["unfollowed"].append(user_id)
            del self.db["followed"][user_id]
            stats["unfollows"] += 1
            unfollowed_count += 1
            save_db(self.db)
            print(f"[{self._now()}] ❌ Unfollow @{data['username']}")
            self.human_delay(CONFIG["delay_between_follows"])
        except Exception as e:
            print(f"[{self._now()}] ⚠️  Erreur unfollow: {e}")

    return unfollowed_count

def print_stats(self):
    today = str(datetime.now().date())
    stats = self.db["daily_stats"].get(today, {"follows": 0, "unfollows": 0})
    total_followed = len(self.db["followed"])
    follow_backs = sum(1 for d in self.db["followed"].values() if d["follow_back"])
    total_unfollowed = len(self.db["unfollowed"])
    print(f"""
```

╔══════════════════════════════════════╗
║         📊 STATISTIQUES              ║
╠══════════════════════════════════════╣
║  Aujourd’hui: Follows: {stats[‘follows’]:>3} | Unfollows: {stats[‘unfollows’]:>3} ║
╠══════════════════════════════════════╣
║  Total suivis:     {total_followed:>5}              ║
║  Follow-backs:     {follow_backs:>5}              ║
║  Total unfollowed: {total_unfollowed:>5}              ║
╚══════════════════════════════════════╝
“””)

```
def run_daily_session(self):
    print(f"\n{'='*50}")
    print(f"[{self._now()}] 🚀 Démarrage session quotidienne")
    print(f"{'='*50}")

    if not self.login():
        return

    self.check_follow_backs()
    self.human_delay((30, 60))
    self.unfollow_non_followers()
    self.human_delay((60, 120))

    stats = get_today_stats(self.db)
    remaining = CONFIG["daily_follow_limit"] - stats["follows"]

    if remaining > 0:
        hashtags = random.sample(CONFIG["target_hashtags"], min(3, len(CONFIG["target_hashtags"])))
        per_hashtag = max(1, remaining // len(hashtags))
        for hashtag in hashtags:
            if get_today_stats(self.db)["follows"] >= CONFIG["daily_follow_limit"]:
                break
            self.follow_by_hashtag(hashtag, per_hashtag)
            self.human_delay((120, 300))

    self.print_stats()
    print(f"\n[{self._now()}] ✅ Session terminée")

def _now(self):
    return datetime.now().strftime("%H:%M:%S")
```

if **name** == “**main**”:
bot = InstagramGrowthBot()
print(“🤖 Instagram Growth Bot - Mode automatique”)
while True:
bot.run_daily_session()
delay = random.uniform(*CONFIG[“delay_between_sessions”])
print(f”\n⏳ Prochain cycle dans {delay/3600:.1f}h…”)
time.sleep(delay)
