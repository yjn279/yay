import os

import anthropic
from dotenv import load_dotenv
import yaylib
from yaylib import Message

# 環境変数の読み込み
load_dotenv()
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
email: str = os.getenv("YAY_EMAIL")
password: str = os.getenv("YAY_PASSWORD")

# 確認ダイアログ
def confirm(text, default=None):
    if default is None or default == True:
        text += " ([y]/n)? "
        return input(text) in ["", "y", "Y"]
    elif default == False:
        text += " (y/[n])? "
        return input(text) in ["", "n", "N"]
    
    text += f" ([y]/{default})? "
    text = input(text)
    if text in ["", "y", "Y"]:
        return True, ""
    else:
        return False, text
    
# プロンプト
messages = []
with open("src/prompts/system.md") as f:
    system = f.read()

# Anthropic API
client = anthropic.Anthropic()

class MyBot(yaylib.Client):
    def on_ready(self):
        print("ボットがオンラインになりました！")

    def on_chat_request(self, total_count):
        # チャットリクエストはすべて承認する
        chat_requests = self.get_chat_requests()
        for chat_room in chat_requests.chat_rooms:
            self.accept_chat_requests([chat_room.id])

        # 最新のメッセージをon_message関数に送信
        message = self.get_messages(chat_requests.chat_rooms[0].id)
        self.on_message(message[0])

    def on_message(self, message: Message):
        # 相手のメッセージを出力
        print(f"\n> {message.text}")
        messages.append({
            "role": "user",
            "content": [{ "type": "text", "text": message.text }]
        })

        # AIのメッセージ
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1000,
            temperature=0.2,
            system=system,
            messages=messages,
        )
        texts = response.content[0].text

        # AIのメッセージを送信
        if confirm(texts):
            for text in texts.replace("- ", "").split("\n"):
                self.send_message(message.room_id, text=text)
            messages.append({
                "role": "assistant",
                "content": [{ "type": "text", "text": texts }]
            })
            return

        # 自分でメッセージを送信
        texts = ""
        while True:
            exit, text = confirm("Exit:", default="your response")
            if exit:
                texts += "- "
                break
            else:
                self.send_message(message.room_id, text=text)
                texts += "- " + text + "\n"

        messages.append({
            "role": "assistant",
            "content": [{ "type": "text", "text": texts }]
        })
            

    def on_chat_room_delete(self, room_id):
        print(f"チャットルームが削除されました。ルームID: {room_id}")


intents = yaylib.Intents.none()
intents.chat_message = True

bot = MyBot(intents=intents)
bot.run(email, password)
