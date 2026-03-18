import os
import time

username = os.getenv("IG_USERNAME")
password = os.getenv("IG_PASSWORD")

username = os.getenv("IG_USERNAME", "info@icxinc.ca")
print("Password:", password)
print("Bot demarre!")

while True:
    print("Bot actif...")
    time.sleep(3600)
