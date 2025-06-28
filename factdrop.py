import os
import telebot
from telebot.types import Message
from dotenv import load_dotenv
import requests
from db import supabase
from datetime import datetime, UTC
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')
if not BOT_TOKEN:
    raise ValueError("Telegram bot token is missing. Check your .env file.")

bot = telebot.TeleBot(BOT_TOKEN)

welcome_message = (
    "👋 Hey!\n\n"
    "Welcome to *FactDrop*, your daily dose of weird, wonderful, and wildly random facts.\n\n"
    "📬 You’ll start receiving one random fact every day in your DMs.\n"
    "🧠 Want one now? Just type /random\n\n"
    "Ready to blow your mind? Let's go 🚀"
)

def get_random_fact():
    url = 'https://uselessfacts.jsph.pl/api/v2/facts/random'
    response = requests.get(url)
    return response.json().get('text', 'No fact found.')

def get_daily_fact():
    url = 'https://uselessfacts.jsph.pl/api/v2/facts/today'
    response = requests.get(url)
    return response.json().get('text', 'No fact found for today.')
    
# /start
@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message: Message):
    chat_id = message.chat.id    
    bot.send_chat_action(chat_id, 'typing')
    
    # Check if user is already subscribed
    existing = supabase.table('Subscribers').select('*').eq('chat_id', chat_id).execute()
    if not existing.data:
        supabase.table('Subscribers').insert({'chat_id': chat_id}).execute()
    
    bot.send_message(message, welcome_message, parse_mode='Markdown')
 
# /random   
@bot.message_handler(commands=['random'])
def send_random_fact(message: Message):
    chat_id = message.chat.id
    bot.send_chat_action(chat_id, 'typing')
    random_fact = get_random_fact()
    bot.send_message(message, random_fact)

# /unsubscribe
@bot.message_handler(commands=['unsubscribe'])
def unsubscribe_user(message: Message):
    chat_id = message.chat.id
    try:
        supabase.table('Subscribers').delete().eq('chat_id', chat_id).execute()
        bot.send_message(
            message,
            "❌ You've been unsubscribed from daily facts.\n\n"
            "If you change your mind, just send /start again to hop back in! 🚀",
            parse_mode='Markdown'
        )
    except Exception as e:
        print(f"[!] Error unsubscribing {chat_id}: {e}")
        bot.send_message(message, "⚠️ Something went wrong. Try again later.", parse_mode='Markdown')
        
# /time
@bot.message_handler(commands=['time'])
def send_delivery_time(message: Message):
    chat_id = message.chat.id
    bot.send_chat_action(chat_id, 'typing')
    try:
        response = supabase.table('Subscribers').select('*').eq('chat_id', chat_id).execute()
        if not response.data:
            bot.send_message(message, "ℹ️ You're not subscribed yet. Use /start to begin receiving daily facts.", parse_mode='Markdown')
            return
        
        sub_time = datetime.fromisoformat(response.data[0]['subscribed_at'])
        utc_time = sub_time.time().strftime('%H:%M')
        
        bot.send_message(
            message,
            f"🕒 Your daily fact will be sent every day at *{utc_time} UTC*.",
            parse_mode='Markdown'
        )
    except Exception as e:
        print(f"[!] Error fetching time for {chat_id}: {e}")
        bot.send_message(message, "⚠️ Couldn't fetch your delivery time.", parse_mode='Markdown')
    
# Daily job
def send_daily_facts():
    now = datetime.now(UTC)
    try:
        subscribers = supabase.table('Subscribers').select('*').execute().data
    except Exception as e:
        print(f"[!] Failed to fetch subscribers: {e}")
        return
    
    fact = get_daily_fact()
    for sub in subscribers:
        try:
            sub_time = datetime.fromisoformat(sub['subscribed_at'])
            if sub_time.hour == now.hour:
                bot.send_message(sub['chat_id'], f"🗓️ *Daily Fact*:\n\n{fact}", parse_mode='Markdown')
                print(f"✅ Sent to {sub['chat_id']} at hour {now.hour}")
        except Exception as e:
            print(f"[!] Error sending to {sub['chat_id']}: {e}")
            
# Schedule the job
scheduler = BackgroundScheduler()
scheduler.add_job(send_daily_facts, 'interval', hours=1)
scheduler.start()
    
print("✅ Bot is running and daily scheduler started.")
bot.infinity_polling()