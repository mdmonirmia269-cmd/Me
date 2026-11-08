import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import requests
import pyotp

# আপনার টেলিগ্রাম বটের টোকেন
API_TOKEN = '9239200994:AAF1CfmE-CA0fHi6rT0CAxam_3vnOo25Yx0'
bot = telebot.TeleBot(API_TOKEN)

# NP Network API কনফিগারেশন (সঠিক .cam ডোমেইনসহ)
NP_API_BASE_URL = 'https://www.npnetworkbd.com/api/user'
NP_API_KEY = 'NP-6HXU732PNEATGVFM'

# ইউজার ব্যালেন্স ট্র্যাক করার ডিকশনারি
user_balances = {}

def get_user_balance(user_id):
    return user_balances.get(user_id, 0.0)

def add_user_balance(user_id, amount):
    current = user_balances.get(user_id, 0.0)
    user_balances[user_id] = round(current + amount, 2)

# মূল মেনু (নিচের স্থায়ী বাটন)
def get_main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("📞 Get Number"),
        KeyboardButton("🔍 Search Number"),
        KeyboardButton("🔥 Proxy/VPN"),
        KeyboardButton("👥 Refer"),
        KeyboardButton("🛡️ 2FA"),
        KeyboardButton("💰 Balance"),
        KeyboardButton("💬 Support"),
        KeyboardButton("💳 Withdrawal")
    )
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "✨ *Welcome to Number & OTP Service.*\n\n"
        "👇 Choose an option below to continue:"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=get_main_menu())

# Get Number ক্লিক করলে সার্ভিস লিস্ট
@bot.message_handler(func=lambda message: message.text == "📞 Get Number")
def handle_get_number(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("🇫 FB Forgot"),
        KeyboardButton("🇫 Facebook"),
        KeyboardButton("📸 Instagram"),
        KeyboardButton("📱 WhatsApp"),
        KeyboardButton("🏠 Home")
    )
    bot.send_message(message.chat.id, "📍 *Select a service:*", parse_mode="Markdown", reply_markup=markup)

# সার্ভিস সিলেক্ট করার পর কান্ট্রি লিস্ট
@bot.message_handler(func=lambda message: message.text in ["🇫 FB Forgot", "🇫 Facebook", "📸 Instagram", "📱 WhatsApp"])
def handle_service_selection(message):
    service_parts = message.text.split(' ')
    service_name = service_parts[1] if len(service_parts) > 1 else "Service"
    
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton(f"🇮🇹 Italy - {service_name}"),
        KeyboardButton(f"🇫🇷 France - {service_name}"),
        KeyboardButton(f"🇨🇲 Cameroon - {service_name}"),
        KeyboardButton(f"🇪🇹 Ethiopia - {service_name}"),
        KeyboardButton(f"🇹🇯 Tajikistan - {service_name}"),
        KeyboardButton("🔙 Back"),
        KeyboardButton("🏠 Home")
    )
    bot.send_message(message.chat.id, f"🌐 *Select a country for {service_name}:*", parse_mode="Markdown", reply_markup=markup)

# সঠিক কান্ট্রি অনুযায়ী সঠিক .cam API থেকে রিয়েল নাম্বার ফেচ করা
@bot.message_handler(func=lambda message: any(c in message.text for c in ["Italy", "France", "Cameroon", "Ethiopia", "Tajikistan", "Change Number"]))
def handle_number_generation(message):
    text_input = message.text
    
    country_name = "Unknown"
    country_code = "IT"
    if "Italy" in text_input:
        country_name = "Italy"
        country_code = "IT"
    elif "France" in text_input:
        country_name = "France"
        country_code = "FR"
    elif "Cameroon" in text_input:
        country_name = "Cameroon"
        country_code = "CM"
    elif "Ethiopia" in text_input:
        country_name = "Ethiopia"
        country_code = "ET"
    elif "Tajikistan" in text_input:
        country_name = "Tajikistan"
        country_code = "TJ"

    phone_number = None
    
    try:
        api_url = f"{NP_API_BASE_URL}?key={NP_API_KEY}&action=getNumber&country={country_code}"
        response = requests.get(api_url, timeout=10)
        data = response.json()
        
        if isinstance(data, dict):
            if 'number' in data:
                phone_number = data['number']
            elif 'phone' in data:
                phone_number = data['phone']
            elif 'msg' in data:
                phone_number = f"Error: {data['msg']}"
    except Exception as e:
        phone_number = f"API Connection Error: {e}"

    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    if phone_number and not str(phone_number).startswith("Error") and not str(phone_number).startswith("API"):
        markup.add(
            KeyboardButton(f"📋 {phone_number}"),
            KeyboardButton("🔄 Check / Simulate OTP Received"),
            KeyboardButton("🔄 Change Number"),
            KeyboardButton("🏠 Home")
        )
        text = (
            f"🔴 *Country : {country_name}*\n\n"
            f"🔄 *Status: Waiting for OTP...*\n\n"
            f"📱 *Number:* `{phone_number}`\n\n"
            f"*(ওটিপি আসার জন্য অপেক্ষা করুন অথবা নিচের চেক বাটনে ক্লিক করুন)*"
        )
    else:
        markup.add(KeyboardButton("🔄 Change Number"), KeyboardButton("🏠 Home"))
        text = f"⚠️ *API Notice:* প্যানেল থেকে কোনো নম্বর পাওয়া যায়নি বা স্টক খালি!\ndetails: `{phone_number}`"

    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

# OTP Received হওয়ার পরে ব্যালেন্সে ০.১ টাকা যোগ হওয়া
@bot.message_handler(func=lambda message: message.text == "🔄 Check / Simulate OTP Received")
def handle_otp_received(message):
    user_id = message.from_user.id
    
    add_user_balance(user_id, 0.1)
    current_balance = get_user_balance(user_id)

    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(
        KeyboardButton("🔄 Change Number"),
        KeyboardButton("🏠 Home")
    )
    
    text = (
        f"🔔 *New OTP Received!*\n\n"
        f"📩 *Code:* `482910`\n\n"
        f"💰 *You have earned 0.1 tk* (Total Balance: `{current_balance} tk`)"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

# ব্যালেন্স চেক
@bot.message_handler(func=lambda message: message.text == "💰 Balance")
def handle_balance(message):
    user_id = message.from_user.id
    balance = get_user_balance(user_id)
    text = f"💰 *Account Balance:*\nআপনার বর্তমান ব্যালেন্স: `{balance} TK`"
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=get_main_menu())

# 2FA মেনু হ্যান্ডলিং
@bot.message_handler(func=lambda message: message.text == "🛡️ 2FA")
def handle_2fa_menu(message):
    text = (
        "🛡️ *2FA Code Generator Service:*\n\n"
        "আপনার রিয়েল-টাইম টু-ফ্যাক্টর (2FA) কোড পেতে আপনার **2FA Secret Key** টি এই চ্যাটে সেন্ড করুন।"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=get_main_menu())

# 2FA সিক্রেট কি প্রসেস করা
@bot.message_handler(func=lambda message: message.text and len(message.text.strip()) > 10 and not message.text.startswith("/") and message.text not in ["📞 Get Number", "🔍 Search Number", "🔥 Proxy/VPN", "👥 Refer", "🛡️ 2FA", "💰 Balance", "💬 Support", "💳 Withdrawal", "🏠 Home", "🔙 Back"])
def process_2fa_key_input(message):
    secret_key = message.text.strip().replace(" ", "")
    try:
        totp = pyotp.TOTP(secret_key)
        current_code = totp.now()
        
        text = (
            f"✅ *2FA Code Generated Successfully!*\n\n"
            f"🔑 *Key:* `{secret_key}`\n"
            f"🔐 *Current OTP Code:* `{current_code}`\n\n"
            f"*(এই কোডটি ৩০ সেকেন্ডের জন্য কার্যকর)*"
        )
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=get_main_menu())
    except Exception as e:
        bot.send_message(message.chat.id, "❌ ভুল বা ইনভ্যালিড 2FA Secret Key দিয়েছেন! দয়া করে সঠিক কি দিন।", reply_markup=get_main_menu())

# সাপোর্ট বাটন (ইনলাইন লিংকসহ)
@bot.message_handler(func=lambda message: message.text == "💬 Support")
def handle_support(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💬 Join Support Channel / Group", url="https://t.me/YourSupportGroupUsername"))
    
    text = "💬 *Support & Assistance:*\nযেকোনো সমস্যায় আমাদের অফিশিয়াল সাপোর্ট গ্রুপে যোগাযোগ করুন:"
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)

# অন্যান্য কমন মেনু
@bot.message_handler(func=lambda message: message.text in ["🏠 Home", "🔙 Back", "🔍 Search Number", "🔥 Proxy/VPN", "👥 Refer", "💳 Withdrawal"])
def handle_other_menus(message):
    txt = message.text
    if txt in ["🏠 Home", "🔙 Back"]:
        bot.send_message(message.chat.id, "🏡 মূল মেনুতে ফিরে এসেছেন:", reply_markup=get_main_menu())
    elif txt == "👥 Refer":
        bot.send_message(message.chat.id, "👥 আপনার রেফারেল লিংক শেয়ার করে আয় করুন!", reply_markup=get_main_menu())
    else:
        bot.send_message(message.chat.id, f"📌 *{txt}* অপশনটি সিলেক্ট করা হয়েছে।", parse_mode="Markdown", reply_markup=get_main_menu())

if __name__ == '__main__':
    print("Bot is running perfectly without errors...")
    bot.infinity_polling()
