import csv
import datetime as dt
import os
from pprint import pprint

from dotenv import load_dotenv
import numpy as np
import pandas as pd
import yaylib


def main():
    # 環境変数の読み込み
    load_dotenv()
    email = os.getenv("YAY_EMAIL")
    password = os.getenv("YAY_PASSWORD")

    # ログイン
    client = yaylib.Client()
    client.login(email=email, password=password)

    # CSV読み込み
    df = pd.read_csv("data/users.csv", index_col=0, dtype={
        "id": str,
        "nickname": str,
        "biography": str,
        "cover_image": str,
    })

    # ユーザー一覧取得
    response = client.search_users(gender=1)
    data = response.data
    users = data.get("users")

    # ユーザー情報をDataFrameに格納
    new_df = pd.DataFrame(users)
    new_df = new_df.set_index("id")
    new_df["biography"] = new_df["biography"].str.replace("\n", " ").replace('"', "")
    new_df["score"] = new_df.apply(score, axis="columns")
    new_df = new_df[["nickname", "biography", "profile_icon", "score"]]

    # CSVにデータを追加
    df = pd.concat([df, new_df], axis=0)
    df = df.drop_duplicates(keep="last")
    df.to_csv("data/users.csv", quoting=csv.QUOTE_ALL)


def score(user):
    supply = user["followers_count"]
    frequency = user["posts_count"]

    recency = int(user["last_loggedin_at"])
    recency = dt.datetime.fromtimestamp(recency)
    recency = dt.datetime.now() - recency
    recency = recency / dt.timedelta (hours=1)

    score = np.log(frequency / (recency * supply + 1) + 1)
    score += 1 if user["followed_by"] else 0
    score += 1 if not user["age_verified"] else 0
    score += 1 if user["new_user"] else 0
    return score

if __name__ == "__main__":
    main()
