import os

from dotenv import load_dotenv
import yaylib


# 環境変数の読み込み
load_dotenv()
email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")

# ログイン
client = yaylib.Client()
client.login(email=email, password=password)

# 投稿
client.create_post("Hello with yaylib!")
