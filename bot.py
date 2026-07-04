import telebot
from telebot import types
import sqlite3

# التوكن والـ ID الخاص بك جاهز ومكتوب
TOKEN = '8873897702:AAEpHpVkHQFA7E__XzY29N0hnkpC8KxYPsk'
SUPER_ADMIN_ID = 5187414420

bot = telebot.TeleBot(TOKEN)

def init_db():
    conn = sqlite3.connect('vet_data.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS admins (user_id INTEGER PRIMARY KEY)')
    cursor.execute('CREATE TABLE IF NOT EXISTS subjects (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS lectures (id INTEGER PRIMARY KEY AUTOINCREMENT, subject_id INTEGER, name TEXT, file_id TEXT, file_type TEXT)')
    conn.commit()
    conn.close()

init_db()

def is_admin(user_id):
    if user_id == SUPER_ADMIN_ID:
        return True
    conn = sqlite3.connect('vet_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM admins WHERE user_id = ?', (user_id,))
    res = cursor.fetchone()
    conn.close()
    return res is not None

def main_menu_markup(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    conn = sqlite3.connect('vet_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM subjects')
    subjects = cursor.fetchall()
    conn.close()
    for sub in subjects:
        markup.add(types.KeyboardButton(sub[0]))
    if is_admin(user_id):
        markup.add(types.KeyboardButton("🛠️ لوحة التحكم"))
    return markup

@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.send_message(message.chat.id, "📚 أهلاً بك في بوت المحاضرات المفتوح!\nاختر المادة من الأزرار بالأسفل:", reply_markup=main_menu_markup(message.from_user.id))

@bot.message_handler(func=lambda message: message.text == "🛠️ لوحة التحكم" and is_admin(message.from_user.id))
def admin_panel(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("➕ إضافة مادة جديدة", callback_data="add_sub"))
    markup.add(types.InlineKeyboardButton("👤 إضافة مشرف جديد", callback_data="add_adm"))
    bot.send_message(message.chat.id, "⚙️ لوحة التحكم:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    conn = sqlite3.connect('vet_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM subjects WHERE name = ?', (message.text,))
    subject = cursor.fetchone()
    if subject:
        sub_id = subject[0]
        cursor.execute('SELECT name, file_id, file_type FROM lectures WHERE subject_id = ?', (sub_id,))
        lectures = cursor.fetchall()
        conn.close()
        if not lectures:
            bot.send_message(message.chat.id, "لا توجد محاضرات مضافة بعد.")
            return
        for lec in lectures:
            bot.send_message(message.chat.id, f"📖 {lec[0]}")
    else:
        conn.close()

bot.infinity_polling()
