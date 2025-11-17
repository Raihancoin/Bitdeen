import sqlite3
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

# বট কনফিগ
BOT_TOKEN = "7871777877:AAFrlqwM4P7O2wO9NLbAxLtrz-1CenIsShw"
BOT_USERNAME = "bitdeen"

class BitdeenBot:
    def __init__(self):
        self.setup_database()
    
    def setup_database(self):
        """ডাটাবেস সেটআপ"""
        conn = sqlite3.connect('bitdeen.db')
        c = conn.cursor()
        
        # ইউজার্স টেবিল
        c.execute('''CREATE TABLE IF NOT EXISTS users
                    (id INTEGER PRIMARY KEY,
                     telegram_id INTEGER UNIQUE,
                     username TEXT,
                     first_name TEXT,
                     points INTEGER DEFAULT 0,
                     referral_code TEXT)''')
        
        # টাস্কস টেবিল
        c.execute('''CREATE TABLE IF NOT EXISTS tasks
                    (id INTEGER PRIMARY KEY,
                     name TEXT,
                     reward INTEGER)''')
        
        # স্যাম্পল টাস্কস যোগ করুন
        c.execute("SELECT COUNT(*) FROM tasks")
        if c.fetchone()[0] == 0:
            tasks = [
                ("টেলিগ্রাম চ্যানেল জয়েন করুন", 50),
                ("টুইটার ফলো করুন", 75),
                ("ডিস্কর্ড জয়েন করুন", 60),
                ("রেফারেল দিন", 25)
            ]
            c.executemany("INSERT INTO tasks (name, reward) VALUES (?, ?)", tasks)
        
        conn.commit()
        conn.close()
        print("✅ ডাটাবেস তৈরি হয়েছে!")
    
    def generate_referral_code(self):
        """রেফারেল কোড তৈরি"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    def start_command(self, update: Update, context):
        """/start কমান্ড"""
        user = update.effective_user
        
        # ডাটাবেসে ইউজার সেভ করুন
        conn = sqlite3.connect('bitdeen.db')
        c = conn.cursor()
        
        # ইউজার এক্সিস্ট করে কিনা চেক করুন
        c.execute("SELECT * FROM users WHERE telegram_id = ?", (user.id,))
        if not c.fetchone():
            referral_code = self.generate_referral_code()
            c.execute("INSERT INTO users (telegram_id, username, first_name, referral_code) VALUES (?, ?, ?, ?)",
                     (user.id, user.username, user.first_name, referral_code))
            conn.commit()
        
        conn.close()
        
        # ওয়েলকাম মেসেজ
        welcome_text = f"""
🤖 **Bitdeen BDN Airdrop বটে স্বাগতম!**

👋 হ্যালো {user.first_name}!

🎯 **টাস্ক সম্পন্ন করে BDN টোকেন উপার্জন করুন**
👥 **বন্ধুদের রেফার করুন - 25 BDN পাবেন**
💰 **মোট সাপ্লাই: 1,000,000 BDN**

**নিচের মেনু থেকে অপশন সিলেক্ট করুন:**
        """
        
        # কীবোর্ড
        keyboard = [
            [InlineKeyboardButton("🎯 BDN উপার্জন", callback_data='tasks')],
            [InlineKeyboardButton("💰 আমার ব্যালেন্স", callback_data='balance')],
            [InlineKeyboardButton("👥 রেফারেল", callback_data='referral')],
            [InlineKeyboardButton("🏆 লিডারবোর্ড", callback_data='leaderboard')]
        ]
        
        update.message.reply_text(
            welcome_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    def button_handler(self, update: Update, context):
        """বাটন ক্লিক হ্যান্ডলার"""
        query = update.callback_query
        query.answer()
        data = query.data
        user_id = query.from_user.id
        
        if data == 'tasks':
            self.show_tasks(query, user_id)
        elif data == 'balance':
            self.show_balance(query, user_id)
        elif data == 'referral':
            self.show_referral(query, user_id)
        elif data == 'leaderboard':
            self.show_leaderboard(query)
        elif data.startswith('complete_'):
            task_id = int(data.split('_')[1])
            self.complete_task(query, user_id, task_id)
        elif data == 'menu':
            self.show_menu(query)
    
    def show_menu(self, query):
        """মেইন মেনু দেখান"""
        menu_text = "🤖 **Bitdeen BDN Airdrop**\n\nনিচের অপশন সিলেক্ট করুন:"
        
        keyboard = [
            [InlineKeyboardButton("🎯 BDN উপার্জন", callback_data='tasks')],
            [InlineKeyboardButton("💰 আমার ব্যালেন্স", callback_data='balance')],
            [InlineKeyboardButton("👥 রেফারেল", callback_data='referral')],
            [InlineKeyboardButton("🏆 লিডারবোর্ড", callback_data='leaderboard')]
        ]
        
        query.edit_message_text(
            menu_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    def show_tasks(self, query, user_id):
        """টাস্কস দেখান"""
        conn = sqlite3.connect('bitdeen.db')
        c = conn.cursor()
        
        c.execute("SELECT * FROM tasks")
        tasks = c.fetchall()
        
        tasks_text = "🎯 **BDN উপার্জনের টাস্কস:**\n\n"
        keyboard = []
        
        for task in tasks:
            task_id, name, reward = task
            tasks_text += f"• {name}\n  🎁 {reward} BDN\n\n"
            keyboard.append([InlineKeyboardButton(
                f"✅ {name} (+{reward} BDN)",
                callback_data=f'complete_{task_id}'
            )])
        
        keyboard.append([InlineKeyboardButton("🔙 মেনু", callback_data='menu')])
        
        query.edit_message_text(
            tasks_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        conn.close()
    
    def complete_task(self, query, user_id, task_id):
        """টাস্ক কমপ্লিট করুন"""
        conn = sqlite3.connect('bitdeen.db')
        c = conn.cursor()
        
        # টাস্কের রিওয়ার্ড পান
        c.execute("SELECT reward FROM tasks WHERE id = ?", (task_id,))
        reward = c.fetchone()[0]
        
        # ইউজারের ব্যালেন্স আপডেট করুন
        c.execute("UPDATE users SET points = points + ? WHERE telegram_id = ?", 
                 (reward, user_id))
        conn.commit()
        
        # নতুন ব্যালেন্স পান
        c.execute("SELECT points FROM users WHERE telegram_id = ?", (user_id,))
        new_balance = c.fetchone()[0]
        
        success_text = f"""
✅ **টাস্ক সম্পন্ন হয়েছে!**

🎁 **আপনি পেয়েছেন:** {reward} BDN
💰 **নতুন ব্যালেন্স:** {new_balance} BDN

🎯 আরও টাস্ক সম্পন্ন করে BDN উপার্জন করুন!
        """
        
        keyboard = [
            [InlineKeyboardButton("🎯 আরও টাস্ক", callback_data='tasks')],
            [InlineKeyboardButton("💰 ব্যালেন্স", callback_data='balance')],
            [InlineKeyboardButton("🔙 মেনু", callback_data='menu')]
        ]
        
        query.edit_message_text(
            success_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        conn.close()
    
    def show_balance(self, query, user_id):
        """ব্যালেন্স দেখান"""
        conn = sqlite3.connect('bitdeen.db')
        c = conn.cursor()
        
        c.execute("SELECT points FROM users WHERE telegram_id = ?", (user_id,))
        balance = c.fetchone()[0]
        
        balance_text = f"""
💰 **আপনার Bitdeen ওয়ালেট**

💎 **বর্তমান ব্যালেন্স:** {balance} BDN
🎯 **আপনার পয়েন্ট:** {balance}
🚀 **আপনার র‍্যাঙ্ক:** #{random.randint(1, 100)}

*BDN টোকেন ডিস্ট্রিবিউশন শুরু হবে শীঘ্রই!*
        """
        
        keyboard = [
            [InlineKeyboardButton("🎯 BDN উপার্জন", callback_data='tasks')],
            [InlineKeyboardButton("🔙 মেনু", callback_data='menu')]
        ]
        
        query.edit_message_text(
            balance_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        conn.close()
    
    def show_referral(self, query, user_id):
        """রেফারেল দেখান"""
        conn = sqlite3.connect('bitdeen.db')
        c = conn.cursor()
        
        c.execute("SELECT referral_code FROM users WHERE telegram_id = ?", (user_id,))
        referral_code = c.fetchone()[0]
        
        referral_text = f"""
👥 **Bitdeen রেফারেল প্রোগ্রাম**

📋 **আপনার রেফারেল কোড:** 
`{referral_code}`

💰 **রেফারেল রিওয়ার্ড:** 25 BDN

🔗 **আপনার রেফারেল লিংক:**
https://t.me/{BOT_USERNAME}?start={referral_code}

**কিভাবে কাজ করে:**
1. বন্ধুকে আপনার রেফারেল লিংক দিন
2. বন্ধু বটে জয়েন করলে
3. আপনি পাবেন 25 BDN
4. আপনার বন্ধুও বোনাস পাবেন!

🎯 **রেফারেল দিয়ে আরও BDN উপার্জন করুন!**
        """
        
        keyboard = [
            [InlineKeyboardButton("🔙 মেনু", callback_data='menu')]
        ]
        
        query.edit_message_text(
            referral_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        conn.close()
    
    def show_leaderboard(self, query):
        """লিডারবোর্ড দেখান"""
        conn = sqlite3.connect('bitdeen.db')
        c = conn.cursor()
        
        c.execute("SELECT first_name, points FROM users ORDER BY points DESC LIMIT 10")
        top_users = c.fetchall()
        
        leaderboard_text = "🏆 **Bitdeen লিডারবোর্ড**\n\n"
        
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        
        for i, (name, points) in enumerate(top_users):
            if i < len(medals):
                leaderboard_text += f"{medals[i]} {name}: {points} BDN\n"
            else:
                leaderboard_text += f"{i+1}. {name}: {points} BDN\n"
        
        keyboard = [
            [InlineKeyboardButton("🔙 মেনু", callback_data='menu')]
        ]
        
        query.edit_message_text(
            leaderboard_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        conn.close()
    
    def run(self):
        """বট চালু করুন"""
        updater = Updater(BOT_TOKEN)
        dispatcher = updater.dispatcher
        
        # কমান্ড হ্যান্ডলার
        dispatcher.add_handler(CommandHandler("start", self.start_command))
        dispatcher.add_handler(CallbackQueryHandler(self.button_handler))
        
        # বট শুরু
        print("🚀 Bitdeen বট শুরু হচ্ছে...")
        updater.start_polling()
        updater.idle()

if __name__ == '__main__':
    bot = BitdeenBot()
    bot.run()
