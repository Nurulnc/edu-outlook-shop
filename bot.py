import telebot
from telebot import types
import json
import os
import pandas as pd
import io

# ================== তোমার তথ্য ==================
TOKEN = "8594094725:AAEtkG2hAgpn7oNxtp8uvrBiFwcaZ2d-oKA"
ADMIN_ID = 1651695602

PRICE_OUTLOOK = 2.5   # প্রতি Outlook/Hotmail
PRICE_EDU = 2       # প্রতি .EDU মেইল

STOCK_FILE = "stock.json"

# প্রথমবার রান করলে স্টক তৈরি
if not os.path.exists(STOCK_FILE):
    with open(STOCK_FILE, "w") as f:
        json.dump({"outlook": 200, "edu": 150}, f)

def load_stock():
    with open(STOCK_FILE, "r") as f:
        return json.load(f)

def save_stock(s):
    with open(STOCK_FILE, "w") as f:
        json.dump(s, f, indent=4)

stock = load_stock()
user_data = {}

bot = telebot.TeleBot(TOKEN)

# ================== START ==================
@bot.message_handler(commands=['start'])
def start(m):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("Outlook/Hotmail", callback_data="cat_outlook"),
        types.InlineKeyboardButton(".EDU Mail", callback_data="cat_edu")
    )
    bot.send_message(m.chat.id,
                     "*Mail Shop*\n\n"
                     f"Outlook/Hotmail → {PRICE_OUTLOOK} Tk\n"
                     f".EDU Mail → {PRICE_EDU} Tk\n\n"
                     f"স্টক: Outlook → {stock['outlook']} | EDU → {stock['edu']}\n\n"
                     "কী কিনবে?",
                     parse_mode="Markdown", reply_markup=markup)

# ================== CATEGORY SELECT ==================
@bot.callback_query_handler(func=lambda c: c.data.startswith("cat_"))
def select_cat(c):
    cat = c.data.split("_")[1]
    name = "Outlook/Hotmail" if cat == "outlook" else ".EDU Mail"
    price = PRICE_OUTLOOK if cat == "outlook" else PRICE_EDU

    if stock[cat] <= 0:
        bot.answer_callback_query(c.id, f"{name} স্টক শেষ!", show_alert=True)
        return

    user_data[c.from_user.id] = {"cat": cat, "state": "qty"}

    bot.edit_message_text(chat_id=c.message.chat.id, message_id=c.message.message_id,
                          text=f"*{name}*\n\nদাম: {price} Tk each\nস্টকে আছে: {stock[cat]} টা\n\nকতগুলো লাগবে?",
                          parse_mode="Markdown")
    bot.send_message(c.message.chat.id, "শুধু সংখ্যা লিখো (যেমন: 5)")

# ================== QUANTITY ==================
@bot.message_handler(func=lambda m: m.from_user.id in user_data and user_data[m.from_user.id]["state"] == "qty")
def get_qty(m):
    uid = m.from_user.id
    cat = user_data[uid]["cat"]
    try:
        qty = int(m.text.strip())
        if qty < 1 or qty > stock[cat]:
            bot.send_message(uid, f"স্টকে মাত্র {stock[cat]}টা আছে!")
            return
    except:
        bot.send_message(uid, "শুধু সংখ্যা লিখো")
        return

    price = PRICE_OUTLOOK if cat == "outlook" else PRICE_EDU
    user_data[uid].update({"qty": qty, "total": qty * price})
    bot.send_message(uid,
                     f"*পেমেন্ট করো*\n\n"
                     f"bKash: 01815243007\n"
                     f"Binance Pay: 38017799\n\n"
                     f"Total: *{qty * price} Taka*\n\n"
                     "স্ক্রিনশট + ট্রানজেকশন আইডি পাঠাও",
                     parse_mode="Markdown")

# ================== PAYMENT PROOF ==================
@bot.message_handler(content_types(['photo', 'text'], func=lambda m: m.from_user.id in user_data)
def proof(m):
    uid = m.from_user.id
    data = user_data[uid]
    cat_name = "Outlook/Hotmail" if data["cat"] == "outlook" else ".EDU Mail"

    if m.content_type == 'photo':
        bot.forward_message(ADMIN_ID, uid, m.message_id)

    bot.send_message(ADMIN_ID,
                     f"NEW ORDER\n\n"
                     f"Category: {cat_name}\n"
                     f"User ID: <code>{uid}</code>\n"
                     f"Quantity: {data['qty']}\n\n"
                     f"অ্যাপ্রুভ করতে:\n"
                     f"1. টেক্সটে পেস্ট করো অথবা\n"
                     f"2. Excel/CSV/TXT ফাইল আপলোড করে ক্যাপশনে লিখো:\n"
                     f"<code>/approve {uid} {data['qty']}</code>",
                     parse_mode="HTML")

    bot.send_message(uid, "অর্ডার পেয়েছি! পেমেন্ট চেক করে অ্যাকাউন্ট পাঠানো হবে। ধন্যবাদ")
    user_data.pop(uid, None)

# ================== APPROVE WITH FILE (Excel/CSV/TXT) ==================
@bot.message_handler(content_types=['document'])
def approve_with_file(m):
    if m.from_user.id != ADMIN_ID:
        return

    if not m.caption or not m.caption.startswith("/approve"):
        bot.reply_to(m, "ক্যাপশনে লিখো: /approve user_id quantity")
        return

    try:
        parts = m.caption.split()
        user_id = int(parts[1])
        qty = int(parts[2])

        file_info = bot.get_file(m.document.file_id)
        downloaded = bot.download_file(file_info.file_path)

        lines = []
        filename = m.document.file_name.lower()

        if filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(downloaded))
            lines = df.astype(str).stack().tolist()

        elif filename.endswith('.csv'):
            text = downloaded.decode('utf-8')
            lines = text.splitlines()

        else:  # .txt বা অন্য
            text = downloaded.decode('utf-8')
            lines = text.splitlines()

        accounts = [line.strip() for line in lines if line.strip() and ':' in line]
        if len(accounts) < qty:
            bot.reply_to(m, f"ফাইলে মাত্র {len(accounts)}টা আছে, কিন্তু {qty}টা লাগবে!")
            return

        cat = "edu" if "edu" in m.caption.lower() else "outlook"
        if stock[cat] < qty:
            bot.reply_to(m, f"{cat.upper()} স্টকে মাত্র {stock[cat]টা আছে!")
            return

        stock[cat] -= qty
        save_stock(stock)

        to_send = "\n".join([f"<code>{acc}</code>" for acc in accounts[:qty]])
        cat_name = "Outlook/Hotmail" if cat == "outlook" else ".EDU Mail"

        bot.send_message(user_id,
                         f"পেমেন্ট কনফার্মড!\n\n"
                         f"তোমার {cat_name}:\n\n{to_send}\n\n"
                         "পাসওয়ার্ড তৎক্ষণাৎ চেঞ্জ করো!\nধন্যবাদ",
                         parse_mode="HTML")

        bot.reply_to(m, f"{qty}টা {cat_name} পাঠানো হয়েছে\nস্টক বাকি: {stock[cat]}টা", parse_mode="Markdown")

    except Exception as e:
        bot.reply_to(m, f"এরর: {str(e)}")

# ================== APPROVE WITH TEXT (যদি ফাইল না দাও) ==================
@bot.message_handler(commands=['approve'])
def approve_with_text(m):
    if m.from_user.id != ADMIN_ID:
        return
    # একই কাজ করবে, শুধু টেক্সট দিয়ে (আগের কোড থেকে কপি করো যদি চাও)

# ================== STOCK CONTROL ==================
@bot.message_handler(commands=['stock'])
def stock_cmd(m):
    if m.from_user.id != ADMIN_ID: return
    bot.reply_to(m, f"Outlook → *{stock['outlook']}*\nEDU → *{stock['edu']}*", parse_mode="Markdown")

@bot.message_handler(commands=['add', 'set'])
def manage_stock(m):
    if m.from_user.id != ADMIN_ID: return
    try:
        p = m.text.split()
        action, cat, amt = p[0][1:], p[1].lower(), int(p[2])
        old = stock[cat]
        if action == "add":
            stock[cat] += amt
        else:
            stock[cat] = amt
        save_stock(stock)
        bot.reply_to(m, f"{cat.upper()}: {old} → *{stock[cat]}*", parse_mode="Markdown")
    except:
        bot.reply_to(m, "উদাহরণ:\n/add outlook 50\n/set edu 0")

# ================== FALLBACK ==================
@bot.message_handler(func=lambda m: True)
def fallback(m):
    bot.send_message(m.chat.id, "/start দিয়ে শুরু করো")

bot.infinity_polling()
