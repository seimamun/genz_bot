from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from flask import Flask, render_template
import time
import random
from pymongo import MongoClient

# MongoDB connection
MONGO_URI = "your_mongodb_connection_string"  # Replace with your MongoDB URI
client = MongoClient(MONGO_URI)
db = client['mining_bot']
users = db['users']

# Flask app for the web interface
app = Flask(__name__)

# Telegram Bot Handlers
def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user = users.find_one({"user_id": user_id})

    if not user:
        users.insert_one({"user_id": user_id, "balance": 0, "last_mine_time": 0})
        update.message.reply_text("Welcome to the Mining Bot! Start mining with /mine.")
    else:
        update.message.reply_text("Welcome back! Start mining with /mine.")

def mine(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user = users.find_one({"user_id": user_id})

    if not user:
        update.message.reply_text("Please use /start to register first.")
        return

    current_time = time.time()
    cooldown = 60  # Cooldown in seconds

    if current_time - user['last_mine_time'] < cooldown:
        remaining_time = int(cooldown - (current_time - user['last_mine_time']))
        update.message.reply_text(f"Please wait {remaining_time} seconds before mining again.")
        return

    reward = random.randint(1, 10)
    new_balance = user['balance'] + reward
    users.update_one({"user_id": user_id}, {"$set": {"balance": new_balance, "last_mine_time": current_time}})
    update.message.reply_text(f"You mined {reward} coins! Your balance is now {new_balance}.")

def balance(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user = users.find_one({"user_id": user_id})

    if not user:
        update.message.reply_text("Please use /start to register first.")
        return

    update.message.reply_text(f"Your current balance is {user['balance']} coins.")

# Flask Routes for Web Interface
@app.route('/')
def index():
    all_users = list(users.find())
    return render_template('index.html', users=all_users)

# Start Bot
def main():
    TOKEN = "your_telegram_bot_token"  # Replace with your bot token
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("mine", mine))
    dp.add_handler(CommandHandler("balance", balance))

    updater.start_polling()

# Run Flask and Bot
if __name__ == '__main__':
    from threading import Thread
    Thread(target=main).start()
    app.run(host="0.0.0.0", port=5000)
