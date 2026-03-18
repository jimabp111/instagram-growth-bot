import os
import time

username = os.getenv("IG_USERNAME")
password = os.getenv("IG_PASSWORD")

username = os.getenv("IG_USERNAME", "info@icxinc.ca")
password = os.getenv("IG_PASSWORD", "Horloge5831!")
print("Bot demarre!")

while True:
    print("Bot actif...")
    time.sleep(3600)
