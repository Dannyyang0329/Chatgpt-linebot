import os
import openai
from flask import Flask, request, abort
from dotenv import load_dotenv

from linebot import LineBotApi
from linebot import WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *


app = Flask(__name__)

handler = WebhookHandler(os.getenv('CHANNEL_SECRET', default=''))
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN', default=''))
openai.api_key = os.getenv("GPT_TOKEN", default='')

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
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


model_engine = "text-davinci-003"

@handler.add(MessageEvent)
def handle_message(event):
    completion = openai.Completion.create(
        engine=model_engine,
        prompt=event.message.text,
        max_tokens=1024,
        n=1, stop=None,
        temperature=0.5
    )
    botReply = completion.choices[0].text
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=botReply))


if __name__ == "__main__":
    load_dotenv()
    app.run()

