import telebot
from telebot import types
import pandas as pd
import io

# ================== তোমার তথ্য ==================
TOKEN = "8594094725:AAEtkG2hAgpn7oNxtp8uvrBiFwcaZ2d-oKA"
ADMIN_ID = 1651695602

PRICE_OUTLOOK = 2.5
PRICE_EDU = 2

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
                     "কী কিনতে চাও?",
                     parse_mode="Markdown", reply_markup=markup)

# ================== CATEGORY ==================
@bot.callback_query_handler(func=lambda c: c.data.startswith("cat_"))
def cat(c):
    cat = c.data.split("_")[1]
    name = "Outlook/Hotmail" if cat == "outlook" else ".EDU Mail"
    price = PRICE_OUTLOOK if cat == "outlook" else PRICE_EDU

    user_data[c.from_user.id] = {"cat": cat}

    bot.edit_message_text(chat_id=c.message.chat.id, message_id=c.message.message_id,
                          text=f"*{name}*\n\nদাম: {price} Tk each\n\nকতগুলো লাগবে?",
                          parse_mode="Markdown")
    bot.send_message(c.message.chat.id, "শুধু সংখ্যা লিখো (যেমন: 5)")

# ================== QUANTITY ==================
@bot.message_handler(func=lambda m: m.from_user.id in user_data)
def qty(m):
    try:
        quantity = int(m.text.strip())
        if quantity < 1:
            raise
    except:
        bot.send_message(m.chat.id, "শুধু সংখ্যা লিখো")
        return

    cat = user_data[m.from_user.id]["cat"]
    price = PRICE_OUTLOOK if cat == "outlook" else PRICE_EDU
    total = quantity * price

    bot.send_message(m.chat.id,
                     f"*পেমেন্ট করো*\n\n"
                     f"bKash: 01815243007\n"
                     f"Binance Pay: 38017799\n\n"
                     f"Total: *{total} Taka* ({quantity} × {price} Tk)\n\n"
                     "স্ক্রিনশট + ট্রানজেকশন আইডি পাঠাও",
                     parse_mode="Markdown")

    user_data[m.from_user.id]["qty"] = quantity

# ================== PAYMENT PROOF ==================
@bot.message_handler(content_types=['photo', 'text'])
def proof(m):
    if m.from_user.id not in user_data:
        return

    uid = m.from_user.id
    qty = user_data[uid]["qty"]
    cat_name = "Outlook/Hotmail" if user_data[uid]["cat"] == "outlook" else ".EDU Mail"

    if m.content_type == 'photo':
        bot.forward_message(ADMIN_ID, uid, m.message_id)

    bot.send_message(ADMIN_ID,
                     f"NEW ORDER\n\n"
                     f"Category: {cat_name}\n"
                     f"User ID: <code>{uid}</code>\n"
                     f"Quantity: {qty}\n\n"
                     f"অ্যাপ্রুভ করতে ফাইল আপলোড করো + ক্যাপশনে লিখো:\n"
                     f"<code>/approve {uid} {qty}</code>",
                     parse_mode="HTML")

    bot.send_message(uid, "অর্ডার পেয়েছি! পেমেন্ট চেক করে অ্যাকাউন্ট পাঠানো হবে")
    del user_data[uid]

# ================== APPROVE WITH FILE (Excel/CSV/TXT) ==================
@bot.message_handler(content_types=['document'])
def approve_with_file(m):
    if m.from_user.id != ADMIN_ID:
        return

    if not m.caption or not m.caption.startswith("/approve"):
        bot.reply_to(m, "ক্যাপশনে লিখো: /approve user_id quantity\nযেমন: /approve 123456789 5")
        return

    try:
        parts = m.caption.split()
        if len(parts) != 3:
            bot.reply_to(m, "ফরম্যাট: /approve user_id quantity")
            return

        user_id = int(parts[1])
        qty = int(parts[2])

        # ফাইল ডাউনলোড
        file_info = bot.get_file(m.document.file_id)
        downloaded = bot.download_file(file_info.file_path)

        lines = []
        filename = m.document.file_name.lower()

        if filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(downloaded))
            lines = df.astype(str).stack().tolist()
        elif filename.endswith('.csv'):
            lines = downloaded.decode('utf-8').splitlines()
        else:  # txt or others
            lines = downloaded.decode('utf-8').splitlines()

        # শুধু mail:pass যুক্ত লাইন রাখো
        accounts = [line.strip() for line in lines if line.strip() and ':' in line]

        if len(accounts) < qty:
            bot.reply_to(m, f"ফাইলে মাত্র {len(accounts)}টা আছে, কিন্তু {qty}টা লাগবে!")
            return

        # প্রথম কয়টা পাঠাও
        to_send = "\n".join([f"<code>{acc}</code>" for acc in accounts[:qty]])

        cat = "edu" if "edu" in m.caption.lower() else "outlook"
        cat_name = "Outlook/Hotmail" if cat == "outlook" else ".EDU Mail"

        bot.send_message(user_id,
                         f"পেমেন্ট কনফার্মড!\n\n"
                         f"তোমার {cat_name}:\n\n{to_send}\n\n"
                         "পাসওয়ার্ড তৎক্ষণাৎ চেঞ্জ করো!\nধন্যবাদ",
                         parse_mode="HTML")

        bot.reply_to(m, f"{qty}টা {cat_name} পাঠানো হয়েছে → {user_id}")

    except Exception as e:
        bot.reply_to(m, f"এরর: {str(e)}")

# ================== FALLBACK ==================
@bot.message_handler(func=lambda m: True)
def fb(m):
    bot.send_message(m.chat.id, "/start দিয়ে শুরু করো")

bot.infinity_polling()
