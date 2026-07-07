from flask import Flask, request
import requests
import os
import json
import re

app = Flask(__name__)

BOT_TOKEN = "8851655567:AAEGziVSFXpZSAMD1hSjreZhP-OBfQUjvoc"
ADMIN_CHAT_ID = "8625787020"
VIDEO_FILE_ID = "BAACAgEAAxkBAAP7akugXF318MJWQ3616dZDkwJJ4hkAAnEHAALuAmBGFLl3swomiE88BA"

# === ФАЙЛЫ ===
USERS_FILE = "users.json"
LANG_FILE = "lang.json"
PENDING_FILE = "pending.json"

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
pending_reply = load_json(PENDING_FILE)

def save_pending():
    save_json(PENDING_FILE, pending_reply)

def save_lang():
    save_json(LANG_FILE, user_lang)

# === ТЕКСТЫ ===
TEXTS = {
    "ru": {
        "welcome": "✨ *Добро пожаловать в NeXus Bot!*\n\n▸ Ваш личный помощник\n▸ Быстрая связь с поддержкой\n▸ Удобное меню для общения\n\n📌 *Выберите действие ниже:*",
        "tutor": "📹 *Вот ваш видео-урок!*",
        "support": "📩 *Напишите ваше сообщение сюда. Администратор ответит вам в ближайшее время.*",
        "choose_lang": "🌐 *Выберите язык:*",
        "lang_changed": "✅ *Язык изменён.*",
        "reply_sent": "✅ *Ответ отправлен*",
        "choose_action": "📌 *Выберите действие:*",
        "admin_reply": "📨 *Ответ администратора:*\n",
        "about": "ℹ️ *NeXus Bot*\n\nВерсия 2.0\nРазработан для удобного общения\n\n▸ Быстрые ответы\n▸ Удобное меню\n▸ Поддержка 24/7"
    },
    "en": {
        "welcome": "✨ *Welcome to NeXus Bot!*\n\n▸ Your personal assistant\n▸ Fast support\n▸ Easy menu\n\n📌 *Choose an action below:*",
        "tutor": "📹 *Here's your video tutorial!*",
        "support": "📩 *Write your message here. Admin will reply soon.*",
        "choose_lang": "🌐 *Choose language:*",
        "lang_changed": "✅ *Language changed.*",
        "reply_sent": "✅ *Reply sent*",
        "choose_action": "📌 *Choose action:*",
        "admin_reply": "📨 *Admin reply:*\n",
        "about": "ℹ️ *NeXus Bot*\n\nVersion 2.0\nDesigned for easy communication\n\n▸ Fast replies\n▸ Easy menu\n▸ 24/7 support"
    }
}

# === КЛАВИАТУРЫ ===
LANG_KEYBOARD = {
    "keyboard": [
        ["🇷🇺 Русский", "🇬🇧 English"]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": True
}

MAIN_KEYBOARD_RU = {
    "keyboard": [
        ["🎥 Видео-урок", "ℹ️ О боте"],
        ["📩 Написать администратору", "🌐 Сменить язык"]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": False
}

MAIN_KEYBOARD_EN = {
    "keyboard": [
        ["🎥 Video tutorial", "ℹ️ About"],
        ["📩 Write to admin", "🌐 Change language"]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": False
}

@app.route('/')
def home():
    return "Bot is alive!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    global pending_reply
    data = request.get_json()
    
    if data and 'message' in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')
        username = data['message']['from'].get('username', 'anon')
        user_id = data['message']['from']['id']

        # === АДМИН ===
        if str(chat_id) == ADMIN_CHAT_ID:
            reply_to = data['message'].get('reply_to_message')
            if reply_to:
                reply_text = reply_to.get('text', '')
                match = re.search(r'ID:\s*(\d+)', reply_text)
                if match:
                    target_id = int(match.group(1))
                    target_lang = user_lang.get(str(target_id), "ru")
                    requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                        json={
                            "chat_id": target_id,
                            "text": TEXTS[target_lang]["admin_reply"] + text,
                            "parse_mode": "Markdown"
                        }
                    )
                    requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                        json={
                            "chat_id": ADMIN_CHAT_ID,
                            "text": f"✅ *Ответ отправлен* (ID: {target_id})",
                            "parse_mode": "Markdown"
                        }
                    )
                    return "ok", 200
                else:
                    if pending_reply.get("user_id"):
                        target_id = pending_reply["user_id"]
                        target_lang = user_lang.get(str(target_id), "ru")
                        requests.post(
                            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                            json={
                                "chat_id": target_id,
                                "text": TEXTS[target_lang]["admin_reply"] + text,
                                "parse_mode": "Markdown"
                            }
                        )
                        requests.post(
                            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                            json={
                                "chat_id": ADMIN_CHAT_ID,
                                "text": f"✅ *Ответ отправлен* @{pending_reply.get('username', 'anon')}",
                                "parse_mode": "Markdown"
                            }
                        )
                        pending_reply = {}
                        save_pending()
                        return "ok", 200
                    else:
                        requests.post(
                            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                            json={
                                "chat_id": ADMIN_CHAT_ID,
                                "text": "⚠️ *Не удалось определить получателя.*",
                                "parse_mode": "Markdown"
                            }
                        )
                        return "ok", 200

            if text == '/start':
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": ADMIN_CHAT_ID,
                        "text": "👋 *Привет, админ!*\n\n▸ Бот работает\n▸ Отвечай на сообщения пользователей\n▸ Используй /help для списка команд",
                        "parse_mode": "Markdown",
                        "reply_markup": MAIN_KEYBOARD_RU
                    }
                )
                return "ok", 200

            if text == '/help':
                help_text = (
                    "📋 *Команды:*\n\n"
                    "/help — помощь\n"
                    "/users — количество пользователей\n"
                    "/reply — ответить пользователю\n"
                    "/sendall — рассылка\n\n"
                    "📌 *Зажми сообщение → Ответить*"
                )
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": ADMIN_CHAT_ID,
                        "text": help_text,
                        "parse_mode": "Markdown"
                    }
                )
                return "ok", 200

            if text == '/users':
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": ADMIN_CHAT_ID,
                        "text": f"👥 *Всего пользователей:* {len(USERS)}",
                        "parse_mode": "Markdown"
                    }
                )
                return "ok", 200

            if text.startswith("/sendall "):
                msg = text.replace("/sendall ", "")
                for uid in USERS:
                    try:
                        requests.post(
                            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                            json={"chat_id": uid, "text": msg}
                        )
                    except:
                        pass
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": ADMIN_CHAT_ID,
                        "text": f"✅ *Рассылка отправлена* {len(USERS)} пользователям.",
                        "parse_mode": "Markdown"
                    }
                )
                return "ok", 200

            if text.startswith("/reply "):
                parts = text.split(" ", 1)
                if len(parts) == 2:
                    reply_text = parts[1]
                    if pending_reply.get("user_id"):
                        target_id = pending_reply["user_id"]
                        target_username = pending_reply.get("username", "anon")
                        target_lang = user_lang.get(str(target_id), "ru")
                        requests.post(
                            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                            json={
                                "chat_id": target_id,
                                "text": TEXTS[target_lang]["admin_reply"] + reply_text,
                                "parse_mode": "Markdown"
                            }
                        )
                        requests.post(
                            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                            json={
                                "chat_id": ADMIN_CHAT_ID,
                                "text": f"✅ *Ответ отправлен* @{target_username}",
                                "parse_mode": "Markdown"
                            }
                        )
                        pending_reply = {}
                        save_pending()
                        return "ok", 200
                    else:
                        requests.post(
                            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                            json={
                                "chat_id": ADMIN_CHAT_ID,
                                "text": "⚠️ *Нет активного диалога.*",
                                "parse_mode": "Markdown"
                            }
                        )
                        return "ok", 200
                else:
                    requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                        json={
                            "chat_id": ADMIN_CHAT_ID,
                            "text": "⚠️ *Используй:* `/reply Текст`",
                            "parse_mode": "Markdown"
                        }
                    )
                    return "ok", 200

            # === ОБЫЧНЫЙ ОТВЕТ АДМИНА ===
            if pending_reply.get("user_id"):
                target_id = pending_reply["user_id"]
                target_username = pending_reply.get("username", "anon")
                target_lang = user_lang.get(str(target_id), "ru")
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": target_id,
                        "text": TEXTS[target_lang]["admin_reply"] + text,
                        "parse_mode": "Markdown"
                    }
                )
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": ADMIN_CHAT_ID,
                        "text": f"✅ *Ответ отправлен* @{target_username}",
                        "parse_mode": "Markdown"
                    }
                )
                pending_reply = {}
                save_pending()
                return "ok", 200
            else:
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": ADMIN_CHAT_ID,
                        "text": "⚠️ *Нет активного диалога.*",
                        "parse_mode": "Markdown"
                    }
                )
                return "ok", 200

        # === ПОЛЬЗОВАТЕЛЬ ===
        save_user(user_id)
        pending_reply["user_id"] = user_id
        pending_reply["username"] = username
        save_pending()

        lang = user_lang.get(str(user_id), "ru")
        t = TEXTS[lang]

        # Смена языка
        if text in ["🌐 Сменить язык", "🌐 Change language"]:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": t["choose_lang"],
                    "reply_markup": LANG_KEYBOARD
                }
            )
            return "ok", 200

        if text == "🇷🇺 Русский":
            user_lang[str(user_id)] = "ru"
            save_lang()
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": TEXTS["ru"]["lang_changed"],
                    "parse_mode": "Markdown",
                    "reply_markup": MAIN_KEYBOARD_RU
                }
            )
            return "ok", 200

        if text == "🇬🇧 English":
            user_lang[str(user_id)] = "en"
            save_lang()
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": TEXTS["en"]["lang_changed"],
                    "parse_mode": "Markdown",
                    "reply_markup": MAIN_KEYBOARD_EN
                }
            )
            return "ok", 200

        # === ПЕРЕСЫЛКА ТЕКСТА (БЕЗ ИЗМЕНЕНИЙ) ===
        # Просто пересылаем то, что написал пользователь
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": ADMIN_CHAT_ID,
                "text": text,
                "parse_mode": "Markdown"
            }
        )

        # === ОБРАБОТКА КНОПОК ===
        keyboard = MAIN_KEYBOARD_EN if lang == "en" else MAIN_KEYBOARD_RU

        if text == '/start':
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": t["welcome"],
                    "parse_mode": "Markdown",
                    "reply_markup": keyboard
                }
            )

        elif text in ["🎥 Видео-урок", "🎥 Video tutorial"]:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo",
                json={
                    "chat_id": chat_id,
                    "video": VIDEO_FILE_ID,
                    "caption": t["tutor"],
                    "parse_mode": "Markdown"
                }
            )
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": t["choose_action"],
                    "parse_mode": "Markdown",
                    "reply_markup": keyboard
                }
            )

        elif text in ["ℹ️ О боте", "ℹ️ About"]:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": t["about"],
                    "parse_mode": "Markdown",
                    "reply_markup": keyboard
                }
            )

        elif text in ["📩 Написать администратору", "📩 Write to admin"]:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": t["support"],
                    "parse_mode": "Markdown",
                    "reply_markup": keyboard
                }
            )

        else:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": t["choose_action"],
                    "parse_mode": "Markdown",
                    "reply_markup": keyboard
                }
            )

    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
