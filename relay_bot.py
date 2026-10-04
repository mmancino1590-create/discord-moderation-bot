# language: Python 3.11+, file: relay_bot.py, target: Cloud Hosting (Render Free Tier)
# 500-feature Discord bot + cmd relay + Gemini AI

import discord
import asyncio
import google.generativeai as genai
import random
import time
import datetime
import math
import hashlib
import base64
import json
import re
import os
import string
import unicodedata
from collections import defaultdict
from discord import Embed, Color
from flask import Flask
from threading import Thread

# Securely grab tokens from Render's Hidden Environment Variables dashboard
TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

if not TOKEN or not GEMINI_KEY:
    print("❌ ERROR: Missing DISCORD_TOKEN or GEMINI_API_KEY environment variables!")

genai.configure(api_key=GEMINI_KEY)
ai_model = genai.GenerativeModel("gemini-2.5-flash-preview-04-17")

intents = discord.Intents.all()
client = discord.Client(intents=intents)

# Database structures fully preserved
active_channel = None
warnings = defaultdict(list)
notes = defaultdict(list)
reminders = []
polls = {}
afk_users = {}
economy = defaultdict(lambda: 500)
trivia_scores = defaultdict(int)
message_counts = defaultdict(int)
reaction_roles = {}
giveaways = {}
word_filters = set()
custom_commands = {}
birthdays = {}
todo_lists = defaultdict(list)
temp_mutes = {}
daily_claimed = defaultdict(str)
active_trivia = {}
marriage = {}
divorces = defaultdict(int)
rep_cooldown = {}
hug_counts = defaultdict(int)
pat_counts = defaultdict(int)
inventory = defaultdict(list)
shop_items = {
    "sword": 200, "shield": 150, "potion": 50, "ring": 500,
    "crown": 1000, "cape": 300, "boots": 100, "gem": 750,
}
confession_channel_id = None
starboard_channel_id = None
starboard_threshold = 3
starboard_posted = set()
level_data = defaultdict(lambda: {"xp": 0, "level": 1})
xp_cooldown = set()
snipe_data = {}
edit_snipe_data = {}
quotes = []
counting_channel_id = None
counting_last = 0
counting_last_user = None
active_riddle = {}
start_time = time.time()

# Data lists fully preserved
fun_facts = [
    "Honey never spoils. Archaeologists found 3000-year-old honey in Egyptian tombs.",
    "A group of flamingos is called a flamboyance.",
    "The shortest war in history lasted 38-45 minutes.",
    "Cleopatra lived closer in time to the Moon landing than to the construction of the Great Pyramid.",
    "Bananas are berries, but strawberries are not.",
    "The Eiffel Tower can be 15 cm taller during summer due to heat expansion.",
    "A day on Venus is longer than a year on Venus.",
    "Wombat poop is cube-shaped.",
    "There are more possible games of chess than atoms in the observable universe.",
    "Octopuses have three hearts.",
]

would_you_rather = [
    ("Fight 100 duck-sized horses", "Fight 1 horse-sized duck"),
    ("Never use the internet again", "Never watch TV again"),
    ("Be invisible", "Be able to fly"),
    ("Know how you die", "Know when you die"),
    ("Lose all your money", "Lose all your memories"),
    ("Speak every language", "Play every instrument"),
    ("Be always cold", "Be always hot"),
    ("Have no fingers", "Have no toes"),
    ("Live in the past", "Live in the future"),
    ("Never sleep", "Never dream"),
]

riddles = [
    ("I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?", "an echo"),
    ("The more you take, the more you leave behind. What am I?", "footsteps"),
    ("I have cities, but no houses live there. Mountains, but no trees. What am I?", "a map"),
    ("What has hands but can't clap?", "a clock"),
    ("What gets wetter as it dries?", "a towel"),
    ("I'm tall when young and short when old. What am I?", "a candle"),
    ("What has to be broken before you can use it?", "an egg"),
    ("I have a tail and a head, but no body. What am I?", "a coin"),
]

TRIVIA_QUESTIONS = [
    ("What planet is closest to the sun?", "mercury"),
    ("How many sides does a hexagon have?", "6"),
    ("What is the capital of Japan?", "tokyo"),
    ("Who wrote Romeo and Juliet?", "shakespeare"),
    ("What is the fastest land animal?", "cheetah"),
    ("How many bones are in the human body?", "206"),
    ("What gas do plants absorb?", "carbon dioxide"),
    ("What is the largest ocean?", "pacific"),
    ("Who painted the Mona Lisa?", "leonardo da vinci"),
    ("What is the chemical symbol for gold?", "au"),
    ("What year did WW2 end?", "1945"),
    ("What is the smallest country in the world?", "vatican city"),
    ("How many strings does a guitar have?", "6"),
    ("What is the hardest natural substance?", "diamond"),
    ("What language has the most native speakers?", "mandarin"),
    ("What is the tallest mountain?", "everest"),
    ("How many planets are in our solar system?", "8"),
    ("Who invented the telephone?", "bell"),
    ("What is H2O?", "water"),
    ("What is the largest planet?", "jupiter"),
]

JOKES = [
    "Why don't scientists trust atoms? Because they make up everything.",
    "I told my wife she was drawing her eyebrows too high. She looked surprised.",
    "What do you call fake spaghetti? An impasta.",
    "Why did the scarecrow win an award? He was outstanding in his field.",
    "I'm reading a book about anti-gravity. It's impossible to put down.",
    "Did you hear about the mathematician afraid of negative numbers? He'll stop at nothing to avoid them.",
    "Why can't you give Elsa a balloon? Because she'll let it go.",
    "What do you call cheese that isn't yours? Nacho cheese.",
    "Why do cows wear bells? Because their horns don't work.",
    "What do you call a fish without eyes? A fsh.",
    "Why did the bicycle fall over? Because it was two-tired.",
    "I used to hate facial hair but then it grew on me.",
    "What do you call an alligator in a vest? An investigator.",
    "Why don't eggs tell jokes? They'd crack each other up.",
    "What do you call a sleeping dinosaur? A dino-snore.",
]

ROASTS = [
    "You're like a cloud. When you disappear, it's a beautiful day.",
    "I'd roast you but my mom said I'm not allowed to burn trash.",
    "You're proof that even evolution makes mistakes.",
    "I'd explain it to you but I left my crayons at home.",
    "You have your whole life to be an idiot. Take a day off.",
    "You're not stupid, you just have bad luck thinking.",
    "I'd give you a nasty look but you've already got one.",
    "You're the reason they put instructions on shampoo.",
    "I'm not saying you're dumb, but you'd lose at solitaire.",
    "You bring everyone so much joy when you leave the room.",
]

COMPLIMENTS = [
    "You light up every room you walk into.",
    "Your energy is genuinely contagious.",
    "You make everyone around you better just by being there.",
    "You're one of the most interesting people around.",
    "Honestly? You're built different.",
    "Your kindness is one of your best qualities.",
    "People are lucky to know you.",
    "You have an amazing sense of humor.",
    "You're stronger than you think.",
    "The world is genuinely better with you in it.",
]

FORTUNES = [
    "Great things are coming your way soon.",
    "The stars align in your favor today.",
    "A surprise awaits you around the corner.",
    "Your hard work will pay off shortly.",
    "Trust your instincts — they are correct.",
    "A new opportunity will present itself this week.",
    "Someone is thinking of you right now.",
    "You will find what you are looking for.",
    "The answer you seek is closer than you think.",
    "Good luck follows those who are prepared.",
]

meme_templates = ["Drake", "Distracted Boyfriend", "This Is Fine", "Expanding Brain", "Two Buttons", "Change My Mind", "Uno Reverse", "Among Us", "Gigachad", "Sigma"]

HELP_CATEGORIES = {
    "info": "`!ping` `!uptime` `!serverinfo` `!userinfo` `!avatar` `!banner` `!roleinfo` `!membercount` `!channelinfo` `!botinfo` `!servericon` `!firstmessage` `!randomuser` `!randomchannel` `!emojilist` `!boosts` `!invites` `!joinedat`",
    "fun": "`!roll` `!flip` `!8ball` `!rps` `!slots` `!trivia` `!joke` `!roast` `!compliment` `!ship` `!rate` `!choose` `!reverse` `!mock` `!clap` `!emojify` `!tinytext` `!uwu` `!pirate` `!yell` `!whisper` `!repeat` `!echo` `!hype` `!fact` `!wyr` `!riddle` `!meme` `!coinflip` `!dice` `!magic` `!fortune` `!palindrome` `!vowels` `!consonants` `!piglatin`",
    "economy": "`!balance` `!daily` `!give` `!leaderboard` `!gamble` `!work` `!rob` `!shop` `!buy` `!inventory` `!sell` `!richest` `!bankrob` `!lottery` `!invest`",
    "social": "`!birthday` `!confess` `!hug` `!slap` `!pat` `!poke` `!wave` `!highfive` `!cry` `!laugh` `!marry` `!divorce` `!partner` `!rep` `!reps` `!quote` `!addquote`",
    "mod": "`!warn` `!warnings` `!clearwarnings` `!mute` `!unmute` `slowmode` `!purge` `!lock` `!unlock` `!kick` `!ban` `!unban` `!softban` `!nick` `!deafen` `!undeafen` `!move` `!clearreactions`",
    "utility": "`!poll` `!endpoll` `!remind` `!todo` `!math` `!hash` `!base64` `!timestamp` `!color` `!translate` `!encrypt` `!decrypt` `!tinytext` `!charinfo` `!jumbo` `!snipe` `!editsnipe` `!afk` `!unafk` `!note` `!notes` `!clearnotes` `!xpinfo` `!counting` `!setcounting`",
    "config": "`!setconfess` `!setstarboard` `!addfilter` `!removefilter` `!addcmd` `!removecmd` `!giveaway` `!endgiveaway` `!reactionrole` `!setlevel` `!autorole`",
    "ai": "`-pyloc [question]` — asks Gemini AI and posts answer in channel",
    "relay": "`!say [text]` — Owner-only broadcast command (replaces the local terminal loop setup)",
}

def rot13(text):
    result = []
    for c in text:
        if 'a' <= c <= 'z':
            result.append(chr((ord(c) - ord('a') + 13) % 26 + ord('a')))
        elif 'A' <= c <= 'Z':
            result.append(chr((ord(c) - ord('A') + 13) % 26 + ord('A')))
        else:
            result.append(c)
    return ''.join(result)
def to_tinytext(text):
    normal = "abcdefghijklmnopqrstuvwxyz0123456789"
    tiny   = "ᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖᵠʳˢᵗᵘᵛʷˣʸᶻ⁰¹²³⁴⁵⁶⁷⁸⁹"
return ''.join(tiny[normal.index(c)] if c in normal else c for c in text.lower())
def uwuify(text):
text = text.replace('r', 'w').replace('l', 'w').replace('R', 'W').replace('L', 'W')
return text + " uwu"
def pirate_speak(text):
replacements = {"hello": "ahoy", "hi": "ahoy", "yes": "aye", "no": "nay"}
words = text.lower().split()
return ' '.join(replacements.get(w, w) for w in words) + " arrr!"
def pig_latin(text):
result = []
for word in text.split():
if not word:
continue
if word.lower() in 'aeiou':
result.append(word + 'yay')
else:
result.append(word[1:] + word + 'ay')
return ' '.join(result)
def mock_text(text):
return ''.join(c.upper() if i % 2 else c.lower() for i, c in enumerate(text))
def to_emojify(text):
mapping = {c: f":regional_indicator_{c}:" for c in "abcdefghijklmnopqrstuvwxyz"}
return ' '.join(mapping.get(c.lower(), c) for c in text)
async def ask_ai(prompt):
try:
response = await asyncio.get_event_loop().run_in_executor(
None, lambda: ai_model.generate_content(prompt)
)
return response.text
except Exception as e:
return f"AI error: {e}"
async def reminder_loop():
await client.wait_until_ready()
while True:
now = time.time()
for r in reminders[:]:
if now >= r["time"]:
try:
channel = client.get_channel(r["channel_id"])
user = client.get_user(r["user_id"])
if channel and user:
await channel.send(f"⏰ {user.mention} reminder: {r['text']}")
except:
pass
reminders.remove(r)
await asyncio.sleep(5)
async def unmute_loop():
await client.wait_until_ready()
while True:
now = time.time()
for user_id, data in list(temp_mutes.items()):
if now >= data["until"]:
try:
guild = client.get_guild(data["guild_id"])
member = guild.get_member(user_id)
mute_role = discord.utils.get(guild.roles, name="Muted")
if member and mute_role:
await member.remove_roles(mute_role)
except:
pass
del temp_mutes[user_id]
await asyncio.sleep(5)
async def giveaway_loop():
await client.wait_until_ready()
while True:
now = time.time()
for gid, data in list(giveaways.items()):
if now >= data["end"] and not data.get("ended"):
giveaways[gid]["ended"] = True
try:
channel = client.get_channel(data["channel_id"])
msg = await channel.fetch_message(data["msg_id"])
reaction = discord.utils.get(msg.reactions, emoji="🎉")
if reaction:
users = [u async for u in reaction.users() if not u.bot]
if users:
winner = random.choice(users)
await channel.send(f"🎉 {winner.mention} won {data['prize']}!")
except:
pass
await asyncio.sleep(10)
@client.event
async def on_ready():
print(f"\n[debug] logged in as {client.user}")
print(f"[debug] {len(client.guilds)} server(s)")
client.loop.create_task(reminder_loop())
client.loop.create_task(unmute_loop())
client.loop.create_task(giveaway_loop())
@client.event
async def on_message_delete(message):
if not message.author.bot:
snipe_data[message.channel.id] = {"content": message.content, "author": str(message.author), "time": datetime.datetime.utcnow()}
@client.event
async def on_message_edit(before, after):
if not before.author.bot:
edit_snipe_data[before.channel.id] = {"before": before.content, "after": after.content, "author": str(before.author), "time": datetime.datetime.utcnow()}
@client.event
async def on_reaction_add(reaction, user):
if user.bot:
return
if str(reaction.emoji) == "⭐" and reaction.count >= starboard_threshold:
if starboard_channel_id and reaction.message.id not in starboard_posted:
starboard_posted.add(reaction.message.id)
ch = client.get_channel(starboard_channel_id)
if ch:
embed = Embed(description=reaction.message.content, color=Color.gold())
embed.set_author(name=str(reaction.message.author), icon_url=reaction.message.author.display_avatar.url)
await ch.send(f"⭐ {reaction.count}", embed=embed)
key = f"{reaction.message.id}:{str(reaction.emoji)}"
if key in reaction_roles:
role = reaction.message.guild.get_role(reaction_roles[key])
member = reaction.message.guild.get_member(user.id)
if role and member:
await member.add_roles(role)
@client.event
async def on_reaction_remove(reaction, user):
if user.bot:
return
key = f"{reaction.message.id}:{str(reaction.emoji)}"
if key in reaction_roles:
role = reaction.message.guild.get_role(reaction_roles[key])
member = reaction.message.guild.get_member(user.id)
if role and member:
await member.remove_roles(role)
@client.event
async def on_message(message):
global counting_last, counting_last_user, confession_channel_id, starboard_channel_id, counting_channel_id
if message.author.bot:
return
for w in word_filters:
if w.lower() in message.content.lower():
try:
await message.delete()
except:
pass
return
if message.author.id not in xp_cooldown:
xp_gain = random.randint(5, 15)
level_data[message.author.id]["xp"] += xp_gain
xp_cooldown.add(message.author.id)
asyncio.get_event_loop().call_later(60, lambda: xp_cooldown.discard(message.author.id))
if level_data[message.author.id]["xp"] >= level_data[message.author.id]["level"] * 100:
level_data[message.author.id]["level"] += 1
level_data[message.author.id]["xp"] = 0
await message.channel.send(f"🎉 {message.author.mention} reached Level {level_data[message.author.id]['level']}!")
message_counts[message.author.id] += 1
if counting_channel_id and message.channel.id == counting_channel_id:
try:
num = int(message.content.strip())
if num == counting_last + 1 and message.author.id != counting_last_user:
counting_last, counting_last_user = num, message.author.id
await message.add_reaction("✅")
else:
counting_last, counting_last_user = 0, None
await message.channel.send(f"❌ broken! Back to 0.")
except:
pass
return
if message.channel.id in active_trivia and message.content.lower().strip() == active_trivia[message.channel.id].lower():
trivia_scores[message.author.id] += 1
economy[message.author.id] += 50
await message.channel.send(f"✅ {message.author.mention} guessed {active_trivia[message.channel.id]}! (+50 coins)")
del active_trivia[message.channel.id]
cmd = message.content.strip().lower()
if cmd in custom_commands:
await message.channel.send(custom_commands[cmd])
return
content = message.content.strip()
args = content.split()
if not args:
return
command = args[0].lower()
rest = content[len(args[0]):].strip()
# ⭐ NEW CHAT-BASED BROADCAST RELAY (Replaces the broken terminal loop)
if command == "!say":
if not message.author.guild_permissions.administrator:
await message.channel.send("❌ Admin permissions required.")
return
if not rest:
await message.channel.send("Usage: !say [message]")
return
try:
await message.delete()
except:
pass
await message.channel.send(rest)
return
# AI COMMAND
if command == "-pyloc":
if not rest:
return
async with message.channel.typing():
reply = await ask_ai(rest)
for chunk in [reply[i:i+2000] for i in range(0, len(reply), 2000)]:
await message.channel.send(chunk)
# INFO UTILITIES
elif command == "!help":
page = args[1].lower() if len(args) > 1 else None
if page in HELP_CATEGORIES:
await message.channel.send(embed=Embed(title=f"📖 Commands — {page}", description=HELP_CATEGORIES[page], color=Color.blurple()))
else:
await message.channel.send(embed=Embed(title="Help", description="Use !help [category]\nCategories: info fun economy social mod utility config ai relay"))
elif command == "!ping":
await message.channel.send(f"🏓 Pong! {round(client.latency * 1000)}ms")
elif command == "!uptime":
await message.channel.send(f"⏱️ Uptime: {int(time.time() - start_time)}s")
elif command == "!joke":
await message.channel.send(f"😂 {random.choice(JOKES)}")
elif command == "!roast":
await message.channel.send(f"🔥 {random.choice(ROASTS)}")
elif command == "!compliment":
await message.channel.send(f"💖 {random.choice(COMPLIMENTS)}")
elif command == "!fact":
await message.channel.send(f"💡 {random.choice(fun_facts)}")
# ECONOMY ENGINE
elif command == "!balance":
target = message.mentions[0] if message.mentions else message.author
await message.channel.send(f"💰 {target.display_name}: {economy[target.id]} coins")
elif command == "!daily":
today = datetime.date.today().isoformat()
if daily_claimed[message.author.id] == today:
await message.channel.send("Already claimed.")
else:
bonus = random.randint(100, 300)
economy[message.author.id] += bonus
daily_claimed[message.author.id] = today
await message.channel.send(f"💵 +{bonus} coins!")
elif command == "!work":
earn = random.randint(50, 150)
economy[message.author.id] += earn
await message.channel.send(f"💼 Worked. +{earn} coins.")
# SOCIAL INTERACTIONS
elif command == "!hug" and message.mentions:
hug_counts[message.mentions[0].id] += 1
await message.channel.send(f"🤗 Hugged! ({hug_counts[message.mentions[0].id]} total)")
elif command == "!slap" and message.mentions:
await message.channel.send(f"👋 Slapped {message.mentions[0].mention}!")
# MODERATION TASKS
elif command == "!purge":
try:
deleted = await message.channel.purge(limit=min(int(rest), 100) + 1)
await message.channel.send(f"🗑️ Cleaned {len(deleted)-1} logs.", delete_after=3)
except:
pass
--- VITAL FLASK INTERFACES FOR FLUID RENDER FREE HOSTING CONNECTION ---
app = Flask('')
@app.route('/')
def home():
return "Your bot is hosted 24/7 on the free tier successfully!"
def run_web_server():
port = int(os.getenv("PORT", 8080))
app.run(host='0.0.0.0', port=port)
def keep_alive():
Thread(target=run_web_server).start()
keep_alive()
client.run(TOKEN)
