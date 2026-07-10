from flask import Flask
import requests
import os
import json
import time
import threading
import re

app = Flask(__name__)

BOT_TOKEN = "8610679847:AAFRUGWWgkK12Kru1UcM-aZ8qgkV3wafJVM"
ADMIN_CHAT_ID = "8625787020"

CHANNEL_LINK = "https://t.me/generatorlinkroblox"
CHANNEL_USERNAME = "@generatorlinkroblox"

VIDEO_FILE_ID = "BAACAgEAAxkBAAMEak_s2su5rFY-_mGadbk0NpnF7hIAAgkKAAKaLYBGe0mN8-ql6Ow8BA"

# === ФАЙЛЫ ===
USERS_FILE = "users.json"
LANG_FILE = "lang.json"
STATS_FILE = "stats.json"

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

# === СТАТИСТИКА ===
default_stats = {
    "total_users": 0,
    "start_commands": 0,
    "link_clicks": {"immortal": 0, "shockify": 0},
    "tutor_views": 0,
    "service_selected": 0
}

stats = load_json(STATS_FILE)
if not stats:
    stats = default_stats
    save_json(STATS_FILE, stats)

def update_stats(key, subkey=None):
    global stats
    if subkey:
        stats[key][subkey] = stats[key].get(subkey, 0) + 1
    else:
        stats[key] = stats.get(key, 0) + 1
    save_json(STATS_FILE, stats)

# === ПРОВЕРКА ПОДПИСКИ ===
def is_subscribed(user_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember"
    params = {"chat_id": CHANNEL_USERNAME, "user_id": user_id}
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        if data.get("ok"):
            status = data["result"].get("status")
            return status in ["member", "administrator", "creator"]
    except:
        pass
    return False

# === ТЕКСТЫ ===
TEXTS = {
    "ru": {
        "welcome": "🔥 *Сюда!*\n\nТут ты можешь получить доступ к крутым инструментам.\n\n👉 *Подпишись на канал*, чтобы начать:",
        "main_menu": "⚡ *Выбери действие:*",
        "tutor": "📹 *Видео-тутор*\n\nСмотри и делай.",
        "about": "ℹ️ *О боте*\n\nПросто, быстро, без регистрации.\nНажимай и пользуйся.",
        "choose_service": "👇 *Выбери сервис для перехода:*",
        "need_sub": "⚠️ *Ты не подписан на канал!*\n\n👉 Нажми на кнопку ниже, чтобы подписаться.",
        "choose_lang": "🌐 *Выбери язык:*",
        "lang_changed": "✅ *Язык изменён.*",
        "admin_reply": "📨 *Ответ администратора:*\n",
        "reply_sent": "✅ *Ответ отправлен*",
        "no_user": "⚠️ *Нет активного диалога.*"
    },
    "en": {
        "welcome": "🔥 *Come here!*\n\nHere you can access cool tools.\n\n👉 *Subscribe to the channel* to start:",
        "main_menu": "⚡ *Choose an action:*",
        "tutor": "📹 *Video tutorial*\n\nWatch and do.",
        "about": "ℹ️ *About the bot*\n\nSimple, fast, no registration.\nJust press and use.",
        "choose_service": "👇 *Choose a service to go to:*",
        "need_sub": "⚠️ *You are not subscribed to the channel!*\n\n👉 Press the button below to subscribe.",
        "choose_lang": "🌐 *Choose language:*",
        "lang_changed": "✅ *Language changed.*",
        "admin_reply": "📨 *Admin reply:*\n",
        "reply_sent": "✅ *Reply sent*",
        "no_user": "⚠️ *No active dialog.*"
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
        ["🔗 Immortal.st", "🔗 Shockify.st"],
        ["🔙 Назад"]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": False
}

SERVICE_KEYBOARD_EN = {
    "keyboard": [
        ["🔗 Immortal.st", "🔗 Shockify.st"],
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

                    # === АДМИН ===
                    if str(chat_id) == ADMIN_CHAT_ID:
                        reply_to = msg.get("reply_to_message")
                        if reply_to:
                            if pending_reply.get("user_id"):
                                target_id = pending_reply["user_id"]
                                target_lang = user_lang.get(str(target_id), "ru")
                                send_message(target_id, TEXTS[target_lang]["admin_reply"] + text)
                                send_message(ADMIN_CHAT_ID, f"✅ *Ответ отправлен* @{pending_reply.get('username', 'anon')}")
                                pending_reply = {}
                                offset = update["update_id"] + 1
                                continue

                        if text.startswith("/reply "):
                            parts = text.split(" ", 2)
                            if len(parts) >= 3 and parts[1].isdigit():
                                target_id = int(parts[1])
                                reply_text = parts[2]
                                target_lang = user_lang.get(str(target_id), "ru")
                                send_message(target_id, TEXTS[target_lang]["admin_reply"] + reply_text)
                                send_message(ADMIN_CHAT_ID, f"✅ *Ответ отправлен* (ID: {target_id})")
                            offset = update["update_id"] + 1
                            continue

                        if text == '/users':
                            send_message(ADMIN_CHAT_ID, f"👥 *Всего пользователей:* {len(USERS)}")
                            offset = update["update_id"] + 1
                            continue

                        if text == '/stats':
                            stats_text = (
                                "📊 *СТАТИСТИКА БОТА*\n"
                                "─────────────────\n"
                                f"👥 *Всего пользователей:* {len(USERS)}\n"
                                f"📥 *Команд /start:* {stats.get('start_commands', 0)}\n"
                                f"🔗 *Выбор сервиса:* {stats.get('service_selected', 0)}\n"
                                "─────────────────\n"
                                f"⚡ *Immortal.st:* {stats['link_clicks'].get('immortal', 0)}\n"
                                f"⚡ *Shockify.st:* {stats['link_clicks'].get('shockify', 0)}\n"
                                "─────────────────\n"
                                f"📹 *Просмотров тутора:* {stats.get('tutor_views', 0)}"
                            )
                            send_message(ADMIN_CHAT_ID, stats_text)
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

                        if text == '/start':
                            send_message(ADMIN_CHAT_ID, "👋 *Привет, админ!*\n\nБот работает.", MAIN_KEYBOARD_RU)
                            offset = update["update_id"] + 1
                            continue

                        if text == '/help':
                            help_text = (
                                "📋 *Команды:*\n\n"
                                "/help — помощь\n"
                                "/users — количество пользователей\n"
                                "/stats — статистика\n"
                                "/reply ID Текст — ответить\n"
                                "/sendall Текст — рассылка"
                            )
                            send_message(ADMIN_CHAT_ID, help_text)
                            offset = update["update_id"] + 1
                            continue

                    # === ПОЛЬЗОВАТЕЛИ ===
                    save_user(user_id)
                    lang = user_lang.get(str(user_id), "ru")
                    t = TEXTS[lang]

                    # === ПРОВЕРКА ПОДПИСКИ ===
                    if not is_subscribed(user_id):
                        inline_keyboard = {
                            "inline_keyboard": [
                                [{"text": "📢 Подписаться на канал", "url": CHANNEL_LINK}]
                            ]
                        }
                        requests.post(
                            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                            json={
                                "chat_id": chat_id,
                                "text": t["need_sub"],
                                "parse_mode": "Markdown",
                                "reply_markup": inline_keyboard
                            }
                        )
                        offset = update["update_id"] + 1
                        continue

                    # === ПОСЛЕ ПОДПИСКИ ===
                    if text == '/start':
                        keyboard = MAIN_KEYBOARD_EN if lang == "en" else MAIN_KEYBOARD_RU
                        send_message(chat_id, t["main_menu"], keyboard)
                        update_stats("start_commands")
                        offset = update["update_id"] + 1
                        continue

                    # === СМЕНА ЯЗЫКА ===
                    if text in ["🌐 Сменить язык", "🌐 Change language"]:
                        send_message(chat_id, t["choose_lang"], LANG_KEYBOARD)
                        offset = update["update_id"] + 1
                        continue

                    if text == "🇷🇺 Русский":
                        user_lang[str(user_id)] = "ru"
                        save_lang()
                        keyboard = MAIN_KEYBOARD_RU
                        send_message(chat_id, TEXTS["ru"]["lang_changed"], keyboard)
                        offset = update["update_id"] + 1
                        continue

                    if text == "🇬🇧 English":
                        user_lang[str(user_id)] = "en"
                        save_lang()
                        keyboard = MAIN_KEYBOARD_EN
                        send_message(chat_id, TEXTS["en"]["lang_changed"], keyboard)
                        offset = update["update_id"] + 1
                        continue

                    # === НАЗАД ===
                    if text in ["🔙 Назад", "🔙 Back"]:
                        keyboard = MAIN_KEYBOARD_EN if lang == "en" else MAIN_KEYBOARD_RU
                        send_message(chat_id, t["main_menu"], keyboard)
                        offset = update["update_id"] + 1
                        continue

                    # === КНОПКА "Создать ссылку" ===
                    if text in ["🔗 Создать ссылку", "🔗 Create link"]:
                        keyboard = SERVICE_KEYBOARD_EN if lang == "en" else SERVICE_KEYBOARD_RU
                        send_message(chat_id, t["choose_service"], keyboard)
                        update_stats("service_selected")
                        offset = update["update_id"] + 1
                        continue

                    # === ВЫБОР СЕРВИСА ===
                    if text == "🔗 Immortal.st":
                        send_message(chat_id, "🔗 [Immortal.st](https://immortal.st/?code=NzA2NTI5NTE4NDExMTQxMjYwNg==)", MAIN_KEYBOARD_RU if lang == "ru" else MAIN_KEYBOARD_EN)
                        update_stats("link_clicks", "immortal")
                        offset = update["update_id"] + 1
                        continue

                    if text == "🔗 Shockify.st":
                        send_message(chat_id, "🔗 [Shockify.st](https://shockify.st/?code=Mzc0NTc1NjEwNTMxNjIzNDQ2NA==)", MAIN_KEYBOARD_RU if lang == "ru" else MAIN_KEYBOARD_EN)
                        update_stats("link_clicks", "shockify")
                        offset = update["update_id"] + 1
                        continue

                    # === ТУТОР ===
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
                        send_message(chat_id, t["main_menu"], keyboard)
                        update_stats("tutor_views")
                        offset = update["update_id"] + 1
                        continue

                    # === О БОТЕ ===
                    if text in ["ℹ️ О боте", "ℹ️ About"]:
                        keyboard = MAIN_KEYBOARD_EN if lang == "en" else MAIN_KEYBOARD_RU
                        send_message(chat_id, t["about"], keyboard)
                        offset = update["update_id"] + 1
                        continue

                    # === ВСЁ ОСТАЛЬНОЕ ===
                    keyboard = MAIN_KEYBOARD_EN if lang == "en" else MAIN_KEYBOARD_RU
                    send_message(chat_id, t["main_menu"], keyboard)
                    offset = update["update_id"] + 1

        except Exception as e:
            print("Polling error:", e)
        time.sleep(1)

@app.route('/')
def home():
    return "Bot is alive!", 200

if __name__ == "__main__":
    threading.Thread(target=poll, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
