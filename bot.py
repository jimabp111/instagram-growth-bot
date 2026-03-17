"""
Instagram Business Growth Bot
-------------------------------
Stratégie : Follow des comptes ciblés → unfollow si pas de follow-back après 7 jours
Limite : ~20-30 follows/jour avec délais aléatoires pour simuler comportement humain
"""

import time
import random
import json
import os
from datetime import datetime, timedelta
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, UserNotFound, FollowError

# ─── CONFIG ──────────────────────────────────────────────────────────────────
CONFIG = {
    "username": os.getenv("IG_USERNAME", ""),
    "password": os.getenv("IG_PASSWORD", ""),

    # Mots-clés pour trouver des cibles (hashtags business)
    "target_hashtags": [
        "entrepreneuriat",
        "businessowner",
        "startupfrancaise",
        "marketingdigital",
        "ecommercefrance",
        "entrepreneur",
        "smallbusiness",
    ],

    # Comptes concurrents/similaires dont on follow les followers
    "target_accounts": [
        # ex: "garyvee", "mrbeast" — mets tes concurrents ici
    ],

    # Limites quotidiennes (rester discret)
    "daily_follow_limit": 25,
    "daily_unfollow_limit": 20,

    # Délais aléatoires entre actions (secondes)
    "delay_between_follows": (45, 120),   # min, max
    "delay_between_sessions": (3600, 7200),  # 1h à 2h entre sessions

    # Unfollow si pas de follow-back après X jours
    "unfollow_after_days": 7,

    # Filtres qualité (éviter bots et comptes inactifs)
    "min_followers": 100,
    "max_followers": 50000,
    "min_posts": 5,
    "max_following_ratio": 10,  # following/followers ratio max
}

DB_FILE = "follow_database.json"

# ─── DATABASE ────────────────────────────────────────────────────────────────
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {
        "followed": {},       # {user_id: {"username": ..., "followed_at": ..., "follow_back": false}}
        "unfollowed": [],     # liste des user_ids déjà unfollow
        "daily_stats": {},    # {date: {"follows": 0, "unfollows": 0}}
        "blacklist": [],      # comptes à ne jamais toucher
    }

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2, default=str)

def get_today_stats(db):
    today = str(datetime.now().date())
    if today not in db["daily_stats"]:
        db["daily_stats"][today] = {"follows": 0, "unfollows": 0}
    return db["daily_stats"][today]

# ─── BOT CLASS ───────────────────────────────────────────────────────────────
class InstagramGrowthBot:
    def __init__(self):
        self.client = Client()
        self.db = load_db()
        self.session_file = "session.json"

    def login(self):
        """Connexion avec gestion de session pour éviter les re-logins fréquents"""
        print(f"[{self._now()}] 🔐 Connexion à Instagram...")

        if os.path.exists(self.session_file):
            try:
                self.client.load_settings(self.session_file)
                self.client.login(CONFIG["username"], CONFIG["password"])
                print(f"[{self._now()}] ✅ Session restaurée")
                return True
            except Exception:
                print(f"[{self._now()}] ⚠️  Session expirée, re-login...")

        try:
            self.client.login(CONFIG["username"], CONFIG["password"])
            self.client.dump_settings(self.session_file)
            print(f"[{self._now()}] ✅ Connecté avec succès")
            return True
        except Exception as e:
            print(f"[{self._now()}] ❌ Erreur login: {e}")
            return False

    def is_quality_account(self, user_info) -> bool:
        """Filtrer les bots et comptes non pertinents"""
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
            return False  # Skip comptes privés

        return True

    def human_delay(self, delay_range):
        """Délai aléatoire pour simuler comportement humain"""
        delay = random.uniform(*delay_range)
        print(f"[{self._now()}] ⏳ Pause {delay:.0f}s...")
        time.sleep(delay)

    def follow_by_hashtag(self, hashtag: str, limit: int):
        """Follow des utilisateurs qui postent sous un hashtag"""
        stats = get_today_stats(self.db)
        followed_count = 0

        print(f"\n[{self._now()}] 🔍 Recherche via #{hashtag}...")

        try:
            medias = self.client.hashtag_medias_recent(hashtag, amount=50)
        except Exception as e:
            print(f"[{self._now()}] ❌ Erreur hashtag {hashtag}: {e}")
            return 0

        random.shuffle(medias)  # Ordre aléatoire

        for media in medias:
            if followed_count >= limit:
                break
            if stats["follows"] >= CONFIG["daily_follow_limit"]:
                print(f"[{self._now()}] 🛑 Limite journalière atteinte ({CONFIG['daily_follow_limit']} follows)")
                break

            user_id = str(media.user.pk)
            username = media.user.username

            # Skip si déjà dans la DB ou blacklist
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
                    print(f"[{self._now()}] ⏭️  Skip @{username} (qualité insuffisante)")
                    continue

                # FOLLOW
                self.client.user_follow(user_id)

                # Enregistrer dans la DB
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

            except (UserNotFound, FollowError) as e:
                print(f"[{self._now()}] ⚠️  Impossible de follow @{username}: {e}")
            except Exception as e:
                print(f"[{self._now()}] ❌ Erreur: {e}")
                time.sleep(30)

        return followed_count

    def check_follow_backs(self):
        """Vérifier qui nous a follow en retour"""
        print(f"\n[{self._now()}] 🔄 Vérification des follow-backs...")

        try:
            followers = self.client.user_followers(self.client.user_id, amount=500)
            follower_ids = {str(uid) for uid in followers.keys()}
        except Exception as e:
            print(f"[{self._now()}] ❌ Erreur récupération followers: {e}")
            return

        updated = 0
        for user_id, data in self.db["followed"].items():
            if not data["follow_back"] and user_id in follower_ids:
                self.db["followed"][user_id]["follow_back"] = True
                self.db["followed"][user_id]["followed_back_at"] = str(datetime.now())
                print(f"[{self._now()}] 💚 @{data['username']} nous a follow back!")
                updated += 1

        if updated > 0:
            save_db(self.db)
        print(f"[{self._now()}] ℹ️  {updated} nouveaux follow-backs détectés")

    def unfollow_non_followers(self):
        """Unfollow les comptes qui n'ont pas follow back après X jours"""
        stats = get_today_stats(self.db)
        unfollow_limit = datetime.now() - timedelta(days=CONFIG["unfollow_after_days"])
        unfollowed_count = 0

        print(f"\n[{self._now()}] 🗑️  Recherche comptes à unfollow (>7 jours sans follow-back)...")

        to_unfollow = []
        for user_id, data in self.db["followed"].items():
            if data["follow_back"]:
                continue  # Ils nous ont follow back → on garde

            followed_at = datetime.fromisoformat(data["followed_at"])
            if followed_at < unfollow_limit:
                to_unfollow.append((user_id, data))

        print(f"[{self._now()}] 📋 {len(to_unfollow)} comptes à unfollow")

        for user_id, data in to_unfollow:
            if stats["unfollows"] >= CONFIG["daily_unfollow_limit"]:
                print(f"[{self._now()}] 🛑 Limite unfollow journalière atteinte")
                break

            try:
                self.client.user_unfollow(user_id)

                # Déplacer vers unfollowed
                self.db["unfollowed"].append(user_id)
                del self.db["followed"][user_id]
                stats["unfollows"] += 1
                unfollowed_count += 1
                save_db(self.db)

                print(f"[{self._now()}] ❌ Unfollow @{data['username']} (suivi depuis {data['followed_at'][:10]})")
                self.human_delay(CONFIG["delay_between_follows"])

            except Exception as e:
                print(f"[{self._now()}] ⚠️  Erreur unfollow @{data['username']}: {e}")

        return unfollowed_count

    def print_stats(self):
        """Afficher les statistiques"""
        today = str(datetime.now().date())
        stats = self.db["daily_stats"].get(today, {"follows": 0, "unfollows": 0})

        total_followed = len(self.db["followed"])
        follow_backs = sum(1 for d in self.db["followed"].values() if d["follow_back"])
        total_unfollowed = len(self.db["unfollowed"])

        print(f"""
╔══════════════════════════════════════╗
║         📊 STATISTIQUES              ║
╠══════════════════════════════════════╣
║  Aujourd'hui:                        ║
║    • Follows:        {stats['follows']:>5}            ║
║    • Unfollows:      {stats['unfollows']:>5}            ║
╠══════════════════════════════════════╣
║  Total:                              ║
║    • Actuellement suivis: {total_followed:>5}       ║
║    • Follow-backs:        {follow_backs:>5}       ║
║    • Taux conversion:  {(follow_backs/max(total_followed+total_unfollowed,1)*100):>5.1f}%       ║
║    • Total unfollowed:    {total_unfollowed:>5}       ║
╚══════════════════════════════════════╝
        """)

    def run_daily_session(self):
        """Session quotidienne complète"""
        print(f"\n{'='*50}")
        print(f"[{self._now()}] 🚀 Démarrage session quotidienne")
        print(f"{'='*50}")

        if not self.login():
            return

        # 1. Vérifier les follow-backs
        self.check_follow_backs()
        self.human_delay((30, 60))

        # 2. Unfollow les non-followers de +7 jours
        self.unfollow_non_followers()
        self.human_delay((60, 120))

        # 3. Follow nouveaux comptes via hashtags
        stats = get_today_stats(self.db)
        remaining = CONFIG["daily_follow_limit"] - stats["follows"]

        if remaining > 0:
            hashtags = random.sample(CONFIG["target_hashtags"],
                                     min(3, len(CONFIG["target_hashtags"])))
            per_hashtag = max(1, remaining // len(hashtags))

            for hashtag in hashtags:
                if get_today_stats(self.db)["follows"] >= CONFIG["daily_follow_limit"]:
                    break
                self.follow_by_hashtag(hashtag, per_hashtag)
                self.human_delay((120, 300))

        # 4. Stats finales
        self.print_stats()
        print(f"\n[{self._now()}] ✅ Session terminée")

    def _now(self):
        return datetime.now().strftime("%H:%M:%S")


# ─── MAIN ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    bot = InstagramGrowthBot()

    print("🤖 Instagram Growth Bot")
    print("=" * 40)
    print("1. Session unique (maintenant)")
    print("2. Mode continu (toutes les 24h)")
    print("3. Stats seulement")
    print("4. Unfollow seulement")

    choice = input("\nChoix: ").strip()

    if choice == "1":
        bot.run_daily_session()

    elif choice == "2":
        print("\n🔄 Mode continu activé. Ctrl+C pour arrêter.")
        while True:
            bot.run_daily_session()
            delay = random.uniform(*CONFIG["delay_between_sessions"])
            print(f"\n⏳ Prochain cycle dans {delay/3600:.1f}h...")
            time.sleep(delay)

    elif choice == "3":
        bot.db = load_db()
        bot.print_stats()

    elif choice == "4":
        if bot.login():
            bot.check_follow_backs()
            bot.unfollow_non_followers()
            bot.print_stats()
