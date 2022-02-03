
from re import S
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import os

from time import time

app = Flask(__name__)

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

def start_watch(id, check): #ストップウォッチ計測開始
    if not check: #スタートしてない時
        message = "ストップウォッチがスタートしました。"
        start[id] = time()
        check = True
        return message, check
    elif check: #既にスタートしてる時
        message = "ストップウォッチはスタートしています。"
        return message, check

def stop_watch(id, check): #ストップウォッチ計測終了
    if check: #既にスタートしてる時
        end = time()
        difference = int(end - start[id])
        hour = difference // 3600
        minute = (difference % 3600) // 60
        second = difference % 60
        message = f"計測時間は{hour}時間{minute}分{second}秒です。"
        check = False
        return message, check
    elif not check: #スタートしてない時
        message = "ストップウォッチはまだスタートしていません。"
        return message, check

start = {} #ストップウォッチのスタート時間初期化
check_start = False #Trueはスタート中、Falseはストップ中
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    if event.message.text == "スタート":
        reply_message = start_watch(user_id, check_start)[0] #ストップウォッチ開始
        global check_start
        check_start = start_watch(user_id, check_start)[1] #チェック結果代入
    elif event.message.text == "ストップ":
        reply_message = stop_watch(user_id)[0] #ストップウォッチ計測時間代入
        global check_start
        check_start = stop_watch(user_id)[1] #チェック結果代入
    else:
        reply_message = event.message.text
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message))


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)