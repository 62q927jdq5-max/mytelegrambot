from flask import Flask
import requests
import os
import json
import time
import threading
import re

app = Flask(__name__)

BOT_TOKEN = "8851655567:AAEGziVSFXpZSAMD1hSjreZhP-OBfQUjvoc"
ADMIN_CHAT_ID = "8625787020"

# === ВСТАВЬ СЮДА СВОЙ FILE_ID ВИДЕО ===
VIDEO_FILE_ID = "BAACAgEAAxkBAAP7akugXF318MJWQ3616dZDkwJJ4hkAAnEHAALuAmBGFLl3swomiE88BA"

# === ФАЙЛЫ ===
USERS_FILE = "users.json"
LANG_FILE = "lang.json"

def load_json(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r") as f:
        USERS = json.load(f)
else:
    USERS = []

def save_user(user_id):
    if user_id not in USERS:
        USERS.append(user_id)
        with open(USERS_FILE, "w") as f:
            json.dump(USERS, f)

user_lang = load_json(LANG_FILE)

def save_lang():
    save_json(LANG_FILE, user_lang)

pending_reply = {}

# === ТЕКСТЫ ===
TEXTS = {
    "ru": {
        "welcome": "👋 *Привет!*\n\n▸ Этот бот поможет тебе получить доступ к инструментам.\n▸ Нажми на кнопку ниже, чтобы выбрать сервис.\n\n📌 *Всё просто — выбирай и переходи.*",
        "choose_action": "📌 *Выбери действие:*",
        "tutor": "📹 *Вот твой видео-тутор!*",
        "about": "ℹ️ *О боте*\n\nПростой помощник для перехода на нужные сервисы.\n▸ Без сложностей\n▸ Без регистрации\n▸ Просто нажми и переходи",
        "choose_lang": "🌐 *Выбери язык:*",
        "lang_changed": "✅ *Язык изменён.*",
        "reply_sent": "✅ *Ответ отправлен*",
        "admin_reply": "📨 *Ответ администратора:*\n",
        "no_user": "⚠️ *Зажми сообщение с ID пользователя → Ответить*"
    },
    "en": {
        "welcome": "👋 *Hello!*\n\n▸ This bot helps you access tools.\n▸ Press the button below to choose a service.\n\n📌 *Simple — just choose and go.*",
        "choose_action": "📌 *Choose an action:*",
        "tutor": "📹 *Here's your video tutorial!*",
        "about": "ℹ️ *About the bot*\n\nSimple assistant for accessing services.\n▸ No complications\n▸ No registration\n▸ Just press and go",
        "choose_lang": "🌐 *Choose language:*",
        "lang_changed": "✅ *Language changed.*",
        "reply_sent": "✅ *Reply sent*",
        "admin_reply": "📨 *Admin reply:*\n",
        "no_user": "⚠️ *Long press message with user ID → Reply*"
    }
}

# === КНОПКИ ===
LANG_KEYBOARD = {
    "keyboard": [
        ["🇷🇺 Русский", "🇬🇧 English"]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": True
}

MAIN_KEYBOARD_RU = {
    "keyboard": [
        ["🔗 Создать ссылку", "📹 Тутор видео"],
        ["ℹ️ О боте", "🌐 Сменить язык"]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": False
}

MAIN_KEYBOARD_EN = {
    "keyboard": [
        ["🔗 Create link", "📹 Tutorial video"],
        ["ℹ️ About", "🌐 Change language"]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": False
}

SERVICE_KEYBOARD_RU = {
    "keyboard": [
        ["⚡ Immortal.st", "⚡ Shockify.st"],
        ["🔙 Назад"]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": False
}

SERVICE_KEYBOARD_EN = {
    "keyboard": [
        ["⚡ Immortal.st", "⚡ Shockify.st"],
        ["🔙 Back"]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": False
}

def send_message(chat_id, text, reply_markup=None, parse_mode="Markdown"):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(url, json=payload)

def send_link(chat_id, url, text="🔗 *Перейдите по ссылке:*"):
    send_message(chat_id, f"{text}\n\n{url}")

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {"timeout": 30, "allowed_updates": ["message"]}
    if offset:
        params["offset"] = offset
    try:
        r = requests.get(url, params=params, timeout=35)
        return r.json().get("result", [])
    except:
        return []

def poll():
    offset = None
    while True:
        try:
            updates = get_updates(offset)
            for update in updates:
                if "message" in update:
                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    text = msg.get("text", "")
                    username = msg["from"].get("username", "anon")
                    user_id = msg["from"]["id"]

                    # === АДМИН: ответ через reply ===
                    reply_to = msg.get("reply_to_message")
                    if reply_to and str(chat_id) == ADMIN_CHAT_ID:
                        reply_text = reply_to.get("text", "")
                        match = re.search(r'ID:\s*(\d+)', reply_text)
                        if match:
                            target_id = int(match.group(1))
                            lang = user_lang.get(str(target_id), "ru")
                            send_message(target_id, TEXTS[lang]["admin_reply"] + text)
                            send_message(ADMIN_CHAT_ID, f"✅ *Ответ отправлен* (ID: {target_id})")
                            offset = update["update_id"] + 1
                            continue

                    # === АДМИН: команды ===
                    if str(chat_id) == ADMIN_CHAT_ID:
                        if text == '/users':
                            send_message(ADMIN_CHAT_ID, f"👥 *Всего пользователей:* {len(USERS)}")
                            offset = update["update_id"] + 1
                            continue
                        if text.startswith('/reply '):
                            parts = text.split(" ", 2)
                            if len(parts) >= 3 and parts[1].isdigit():
                                target_id = int(parts[1])
                                reply_text = parts[2]
                                lang = user_lang.get(str(target_id), "ru")
                                send_message(target_id, TEXTS[lang]["admin_reply"] + reply_text)
                                send_message(ADMIN_CHAT_ID, f"✅ *Ответ отправлен* (ID: {target_id})")
                            offset = update["update_id"] + 1
                            continue
                        if text.startswith('/sendall '):
                            msg = text.replace("/sendall ", "")
                            for uid in USERS:
                                try:
                                    send_message(uid, msg)
                                except:
                                    pass
                            send_message(ADMIN_CHAT_ID, f"✅ *Рассылка отправлена* {len(USERS)} пользователям.")
                            offset = update["update_id"] + 1
                            continue

                    # === ОБЫЧНЫЕ ПОЛЬЗОВАТЕЛИ ===
                    save_user(user_id)
                    lang = user_lang.get(str(user_id), "ru")
                    t = TEXTS[lang]

                    # Смена языка
                    if text in ["🌐 Сменить язык", "🌐 Change language"]:
                        send_message(chat_id, t["choose_lang"], LANG_KEYBOARD)
                        offset = update["update_id"] + 1
                        continue

                    if text == "🇷🇺 Русский":
                        user_lang[str(user_id)] = "ru"
                        save_lang()
                        send_message(chat_id, TEXTS["ru"]["lang_changed"], MAIN_KEYBOARD_RU)
                        offset = update["update_id"] + 1
                        continue

                    if text == "🇬🇧 English":
                        user_lang[str(user_id)] = "en"
                        save_lang()
                        send_message(chat_id, TEXTS["en"]["lang_changed"], MAIN_KEYBOARD_EN)
                        offset = update["update_id"] + 1
                        continue

                    # === НАЗАД ===
                    if text in ["🔙 Назад", "🔙 Back"]:
                        keyboard = MAIN_KEYBOARD_EN if lang == "en" else MAIN_KEYBOARD_RU
                        send_message(chat_id, t["choose_action"], keyboard)
                        offset = update["update_id"] + 1
                        continue

                    # === КНОПКА "Создать ссылку" ===
                    if text in ["🔗 Создать ссылку", "🔗 Create link"]:
                        keyboard = SERVICE_KEYBOARD_EN if lang == "en" else SERVICE_KEYBOARD_RU
                        send_message(chat_id, "⚡ *Выбери сервис:*", keyboard)
                        offset = update["update_id"] + 1
                        continue

                    # === ВЫБОР СЕРВИСА ===
                    if text == "⚡ Immortal.st":
                        send_link(chat_id, "https://immortal.st/?code=NzA2NTI5NTE4NDExMTQxMjYwNg==")
                        keyboard = MAIN_KEYBOARD_EN if lang == "en" else MAIN_KEYBOARD_RU
                        send_message(chat_id, t["choose_action"], keyboard)
                        offset = update["update_id"] + 1
                        continue

                    if text == "⚡ Shockify.st":
                        send_link(chat_id, "https://shockify.st/?code=Mzc0NTc1NjEwNTMxNjIzNDQ2NA==")
                        keyboard = MAIN_KEYBOARD_EN if lang == "en" else MAIN_KEYBOARD_RU
                        send_message(chat_id, t["choose_action"], keyboard)
                        offset = update["update_id"] + 1
                        continue

                    # === ТУТОР (отправка ВИДЕО) ===
                    if text in ["📹 Тутор видео", "📹 Tutorial video"]:
                        requests.post(
                            f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo",
                            json={
                                "chat_id": chat_id,
                                "video": VIDEO_FILE_ID,
                                "caption": t["tutor"]
                            }
                        )
                        keyboard = MAIN_KEYBOARD_EN if lang == "en" else MAIN_KEYBOARD_RU
                        send_message(chat_id, t["choose_action"], keyboard)
                        offset = update["update_id"] + 1
                        continue

                    # === О БОТЕ ===
                    if text in ["ℹ️ О боте", "ℹ️ About"]:
                        keyboard = MAIN_KEYBOARD_EN if lang == "en" else MAIN_KEYBOARD_RU
                        send_message(chat_id, t["about"], keyboard)
                        offset = update["update_id"] + 1
                        continue

                    # === СТАРТ ===
                    if text == '/start':
                        keyboard = MAIN_KEYBOARD_EN if lang == "en" else MAIN_KEYBOARD_RU
                        send_message(chat_id, t["welcome"], keyboard)
                        offset = update["update_id"] + 1
                        continue

                    # === ВСЁ ОСТАЛЬНОЕ ===
                    keyboard = MAIN_KEYBOARD_EN if lang == "en" else MAIN_KEYBOARD_RU
                    send_message(chat_id, t["choose_action"], keyboard)
                    offset = update["update_id"] + 1

        except Exception as e:
            print("Polling error:", e)
        time.sleep(1)

@app.route('/')
def home():
    return "Bot is alive! (polling mode)", 200

if __name__ == "__main__":
    threading.Thread(target=poll, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
