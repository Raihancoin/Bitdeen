import { Telegraf } from "telegraf";
import fetch from "node-fetch";

const BOT_TOKEN = "7871777877:AAFrlqwM4P7O2wO9NLbAxLtrz-1CenIsShw";
const bot = new Telegraf(BOT_TOKEN);
const FIREBASE_DB_URL = "https://bitdeen-a1ebe-default-rtdb.firebaseio.com/users.json";

// নতুন ইউজার /start করলে Firebase এ সেভ হবে
bot.start(async (ctx) => {
  const userId = ctx.from.id;
  const name = ctx.from.first_name;

  await fetch(`${FIREBASE_DB_URL}/${userId}.json`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      id: userId,
      name: name,
      balance: 0,
      joinedAt: Date.now()
    })
  });

  ctx.reply(`স্বাগতম ${name}! 🎉\nআপনার BitDeen অ্যাকাউন্ট তৈরি হয়েছে।`);
});

bot.launch();
console.log("Bot is running...");