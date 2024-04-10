import os

from dotenv import load_dotenv
from supabase import create_client, Client
import yaylib

def main():
    # 環境変数の読み込み
    load_dotenv()
    url: str = os.getenv("SUPABASE_URL")
    key: str = os.getenv("SUPABASE_KEY")
    email: str = os.getenv("YAY_EMAIL")
    password: str = os.getenv("YAY_PASSWORD")

    # Supabaseクライアントの作成
    supabase: Client = create_client(url, key)

    # Yay!へのログイン
    client = yaylib.Client()
    client.login(email=email, password=password)

    # タイムラインの取得
    timeline = client.get_timeline_by_hashtag("いいねでこちゃ", number=100)
    for post in timeline.posts:
        user = post.user
        if user.gender != 1:
            continue
        
        biography = user.biography
        if "関西" in biography or "かんさい" in biography:
            continue

        client.like(post.id)
        data, count = supabase.table("likes").insert({
            "user_id": "8569176",
            "post_id": post.id,
        }).execute()


if __name__ == "__main__":
    main()
