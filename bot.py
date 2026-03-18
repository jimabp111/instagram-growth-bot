import os
import time

username = os.getenv("IG_USERNAME")
password = os.getenv("IG_PASSWORD")

print("Username:", username)
print("Password:", password)
print("Bot demarre!")

while True:
    print("Bot actif...")
    time.sleep(3600)
