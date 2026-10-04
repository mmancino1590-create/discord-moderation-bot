# language: Python 3.11+, file: relay_bot.py
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

# Secure environmental fetch for cloud systems (Render, Wispbyte, etc.)
TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

if not TOKEN or not GEMINI_KEY:
    import sys
    print("❌ CRITICAL ERROR: DISCORD_TOKEN or GEMINI_API_KEY environment variables are missing!")
    sys.exit(1)

genai.configure(api_key=GEMINI_KEY)
ai_model = genai.GenerativeModel("gemini-2.5-flash-preview-04-17")

intents = discord.Intents.all()
client = discord.Client(intents=intents)

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
    "mod": "`!warn` `!warnings` `!clearwarnings` `!mute` `!unmute` `!slowmode` `!purge` `!lock` `!unlock` `!kick` `!ban` `!unban` `!softban` `!nick` `!deafen` `!undeafen` `!move` `!clearreactions`",
    "utility": "`!poll` `!endpoll` `!remind` `!todo` `!math` `!hash` `!base64` `!timestamp` `!color` `!translate` `!encrypt` `!decrypt` `!tinytext` `!charinfo` `!jumbo` `!snipe` `!editsnipe` `!afk` `!unafk` `!note` `!notes` `!clearnotes` `!xpinfo` `!counting` `!setcounting`",
    "config": "`!setconfess` `!setstarboard` `!addfilter` `!removefilter` `!addcmd` `!removecmd` `!giveaway` `!endgiveaway` `!reactionrole` `!setlevel` `!autorole`",
    "ai": "`-pyloc [question]` — asks Gemini AI and posts answer in channel",
    "relay": "`!say [#channel_mention] [message]` — Broadcasts a message to any channel via Discord (replaces the local terminal loop)."
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
Use code with caution.
text = text.replace('r', 'w').replace('l', 'w').replace('R', 'W').replace('L', 'W')
text = text.replace('na', 'nya').replace('Na', 'Nya').replace('ni', 'nyi')
return text + " uwu"
def pirate_speak(text):
replacements = {
"hello": "ahoy", "hi": "ahoy", "yes": "aye", "no": "nay",
"you": "ye", "the": "th'", "my": "me", "friend": "matey",
"is": "be", "are": "be", "money": "gold",
}
words = text.lower().split()
return ' '.join(replacements.get(w, w) for w in words) + " arrr!"
def pig_latin(text):
result = []
for word in text.split():
if not word:
continue
if word[0].lower() in 'aeiou':
result.append(word + 'yay')
else:
result.append(word[1:] + word[0] + 'ay')
return ' '.join(result)
def mock_text(text):
return ''.join(c.upper() if i % 2 else c.lower() for i, c in enumerate(text))
def to_emojify(text):
mapping = {c: f":regional_indicator_{c}:" for c in "abcdefghijklmnopqrstuvwxyz"}
mapping.update({str(i): f"{i}\u20e3" for i in range(10)})
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
else:
await channel.send("No one entered the giveaway.")
except:
pass
await asyncio.sleep(10)
@client.event
async def on_ready():
print(f"\n[debug] logged in as {client.user}")
print(f"[debug] {len(client.guilds)} server(s)")
# Local keyboard input console loop is deactivated so cloud hosting does not freeze
# client.loop.create_task(input_loop())
client.loop.create_task(reminder_loop())
client.loop.create_task(unmute_loop())
client.loop.create_task(giveaway_loop())
@client.event
async def on_message_delete(message):
if not message.author.bot:
snipe_data[message.channel.id] = {
"content": message.content,
"author": str(message.author),
"time": datetime.datetime.utcnow()
}
@client.event
async def on_message_edit(before, after):
if not before.author.bot:
edit_snipe_data[before.channel.id] = {
"before": before.content,
"after": after.content,
"author": str(before.author),
"time": datetime.datetime.utcnow()
}
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
embed.add_field(name="Jump", value=f"Link")
await ch.send(f"⭐ {reaction.count}", embed=embed)
key = f"{reaction.message.id}:{str(reaction.emoji)}"
if key in reaction_roles:
guild = reaction.message.guild
role = guild.get_role(reaction_roles[key])
member = guild.get_member(user.id)
if role and member:
await member.add_roles(role)
@client.event
async def on_reaction_remove(reaction, user):
if user.bot:
return
key = f"{reaction.message.id}:{str(reaction.emoji)}"
if key in reaction_roles:
guild = reaction.message.guild
role = guild.get_role(reaction_roles[key])
member = guild.get_member(user.id)
if role and member:
await member.remove_roles(role)
@client.event
async def on_message(message):
global counting_last, counting_last_user, confession_channel_id, starboard_channel_id, counting_channel_id
if message.author.bot:
return
if active_channel and message.channel.id == active_channel.id:
att = f" [+{len(message.attachments)} file(s)]" if message.attachments else ""
print(f"\n[{message.author.display_name}]: {message.content}{att}")
print("> ", end="", flush=True)
for w in word_filters:
if w.lower() in message.content.lower():
try:
await message.delete()
await message.channel.send(f"{message.author.mention} that word is filtered.", delete_after=5)
except:
pass
return
if message.author.id not in xp_cooldown:
xp_gain = random.randint(5, 15)
level_data[message.author.id]["xp"] += xp_gain
xp_cooldown.add(message.author.id)
asyncio.get_event_loop().call_later(60, lambda: xp_cooldown.discard(message.author.id))
xp_needed = level_data[message.author.id]["level"] * 100
if level_data[message.author.id]["xp"] >= xp_needed:
level_data[message.author.id]["level"] += 1
level_data[message.author.id]["xp"] = 0
await message.channel.send(f"🎉 {message.author.mention} leveled up to Level {level_data[message.author.id]['level']}!")
message_counts[message.author.id] += 1
if message.author.id in afk_users:
del afk_users[message.author.id]
await message.channel.send(f"Welcome back {message.author.mention}!", delete_after=5)
for mention in message.mentions:
if mention.id in afk_users:
await message.channel.send(f"{mention.display_name} is AFK: {afk_users[mention.id]}", delete_after=10)
if counting_channel_id and message.channel.id == counting_channel_id:
try:
num = int(message.content.strip())
if num == counting_last + 1 and message.author.id != counting_last_user:
counting_last = num
counting_last_user = message.author.id
await message.add_reaction("✅")
else:
counting_last = 0
counting_last_user = None
await message.channel.send(f"❌ {message.author.mention} ruined it! Back to 0.")
except:
try:
await message.delete()
except:
pass
return
if message.channel.id in active_trivia:
q, answer = active_trivia[message.channel.id]
if message.content.lower().strip() == answer.lower():
trivia_scores[message.author.id] += 1
economy[message.author.id] += 50
del active_trivia[message.channel.id]
await message.channel.send(f"✅ {message.author.mention} got it! {answer} (+50 coins)")
if message.channel.id in active_riddle:
q, answer = active_riddle[message.channel.id]
if message.content.lower().strip() == answer.lower():
economy[message.author.id] += 75
del active_riddle[message.channel.id]
await message.channel.send(f"🧩 {message.author.mention} solved it! {answer} (+75 coins)")
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
# CLOUD REMOTE RELAY COMMAND (Replaces local computer CMD interface)
# Usage: !say #general Hello guys!
if command == "!say":
if not message.author.guild_permissions.administrator:
await message.channel.send("❌ Only Administrators can use the bot relay.")
return
if not message.channel_mentions or len(args) < 3:
await message.channel.send("Usage: !say [#channel] [text]")
return
target_channel = message.channel_mentions[0]
# Extract message text excluding the channel mention token
raw_text = content.split(' ', 2)[2]
try:
await message.delete()
await target_channel.send(raw_text)
except Exception as e:
await message.channel.send(f"Could not send message: {e}")
return
# AI
if command == "-pyloc":
if not rest:
await message.channel.send("Usage: -pyloc [question]")
return
async with message.channel.typing():
reply = await ask_ai(rest)
for chunk in [reply[i:i+2000] for i in range(0, len(reply), 2000)]:
await message.channel.send(chunk)
# INFO
elif command == "!help":
page = args[1].lower() if len(args) > 1 else None
if page in HELP_CATEGORIES:
embed = Embed(title=f"📖 Commands — {page}", description=HELP_CATEGORIES[page], color=Color.blurple())
embed.set_footer(text="Categories: info fun economy social mod utility config ai relay")
await message.channel.send(embed=embed)
else:
embed = Embed(title="📖 Help", description="Use !help [category]\n\nCategories:\ninfo fun economy social mod utility config ai relay", color=Color.blurple())
await message.channel.send(embed=embed)
elif command == "!ping":
await message.channel.send(f"🏓 Pong! {round(client.latency * 1000)}ms")
elif command == "!uptime":
elapsed = int(time.time() - start_time)
h, m, s = elapsed // 3600, (elapsed % 3600) // 60, elapsed % 60
await message.channel.send(f"⏱️ Uptime: {h}h {m}m {s}s")
elif command == "!serverinfo":
g = message.guild
embed = Embed(title=g.name, color=Color.blue())
embed.add_field(name="Members", value=g.member_count)
embed.add_field(name="Channels", value=len(g.channels))
embed.add_field(name="Roles", value=len(g.roles))
embed.add_field(name="Boosts", value=g.premium_subscription_count)
embed.add_field(name="Owner", value=str(g.owner))
embed.add_field(name="Created", value=g.created_at.strftime("%Y-%m-%d"))
if g.icon:
embed.set_thumbnail(url=g.icon.url)
await message.channel.send(embed=embed)
elif command == "!userinfo":
target = message.mentions[0] if message.mentions else message.author
embed = Embed(title=str(target), color=Color.green())
embed.add_field(name="ID", value=target.id)
embed.add_field(name="Joined", value=target.joined_at.strftime("%Y-%m-%d") if target.joined_at else "N/A")
embed.add_field(name="Created", value=target.created_at.strftime("%Y-%m-%d"))
embed.add_field(name="Roles", value=len(target.roles) - 1)
embed.add_field(name="Messages", value=message_counts[target.id])
embed.add_field(name="Level", value=level_data[target.id]["level"])
embed.set_thumbnail(url=target.display_avatar.url)
await message.channel.send(embed=embed)
elif command == "!avatar":
target = message.mentions[0] if message.mentions else message.author
embed = Embed(title=f"{target.display_name}'s avatar", color=Color.purple())
embed.set_image(url=target.display_avatar.url)
await message.channel.send(embed=embed)
elif command == "!banner":
target = message.mentions[0] if message.mentions else message.author
fetched = await client.fetch_user(target.id)
if fetched.banner:
embed = Embed(title=f"{target.display_name}'s banner", color=Color.purple())
embed.set_image(url=fetched.banner.url)
await message.channel.send(embed=embed)
else:
await message.channel.send("No banner set.")
elif command == "!membercount":
await message.channel.send(f"👥 Members: {message.guild.member_count}")
elif command == "!servericon":
if message.guild.icon:
embed = Embed(title=f"{message.guild.name} icon", color=Color.blue())
embed.set_image(url=message.guild.icon.url)
await message.channel.send(embed=embed)
elif command == "!boosts":
g = message.guild
await message.channel.send(f"💎 Boosts: {g.premium_subscription_count} (Level {g.premium_tier})")
elif command == "!roleinfo":
if rest:
role = discord.utils.find(lambda r: r.name.lower() == rest.lower(), message.guild.roles)
if role:
embed = Embed(title=role.name, color=role.color)
embed.add_field(name="ID", value=role.id)
embed.add_field(name="Members", value=len(role.members))
embed.add_field(name="Mentionable", value=role.mentionable)
embed.add_field(name="Hoisted", value=role.hoist)
embed.add_field(name="Created", value=role.created_at.strftime("%Y-%m-%d"))
await message.channel.send(embed=embed)
elif command == "!channelinfo":
ch = message.channel
embed = Embed(title=f"#{ch.name}", color=Color.teal())
embed.add_field(name="ID", value=ch.id)
embed.add_field(name="Topic", value=ch.topic or "None")
embed.add_field(name="NSFW", value=ch.nsfw)
embed.add_field(name="Slowmode", value=f"{ch.slowmode_delay}s")
embed.add_field(name="Created", value=ch.created_at.strftime("%Y-%m-%d"))
await message.channel.send(embed=embed)
elif command == "!botinfo":
elapsed = int(time.time() - start_time)
h, m, s = elapsed // 3600, (elapsed % 3600) // 60, elapsed % 60
embed = Embed(title="Bot Info", color=Color.blurple())
embed.add_field(name="Servers", value=len(client.guilds))
embed.add_field(name="Uptime", value=f"{h}h {m}m {s}s")
embed.add_field(name="Features", value="500+")
embed.set_thumbnail(url=client.user.display_avatar.url)
await message.channel.send(embed=embed)
elif command == "!randomuser":
member = random.choice(message.guild.members)
await message.channel.send(f"🎲 Random member: {member.mention}")
elif command == "!randomchannel":
ch = random.choice(message.guild.text_channels)
await message.channel.send(f"🎲 Random channel: {ch.mention}")
elif command == "!firstmessage":
async for msg in message.channel.history(oldest_first=True, limit=1):
await message.channel.send(f"📜 First message: {msg.jump_url}")
elif command == "!joinedat":
target = message.mentions[0] if message.mentions else message.author
if target.joined_at:
await message.channel.send(f"📅 {target.mention} joined {target.joined_at.strftime('%Y-%m-%d %H:%M:%S')}")
elif command == "!emojilist":
emojis = [str(e) for e in message.guild.emojis[:30]]
await message.channel.send(' '.join(emojis) if emojis else "No custom emojis.")
elif command == "!invites":
try:
invites = await message.guild.invites()
inv_list = '\n'.join([f"{i.code} — {i.uses} uses ({i.inviter})" for i in invites[:10]])
await message.channel.send(f"Invites:\n{inv_list or 'None'}")
except:
await message.channel.send("No permission.")
# FUN
elif command == "!roll":
try:
if 'd' in rest.lower():
parts = rest.lower().split('d')
n, sides = int(parts[0] or 1), int(parts[1])
else:
n, sides = 1, int(rest) if rest.isdigit() else 6
n = min(n, 20)
rolls = [random.randint(1, sides) for _ in range(n)]
await message.channel.send(f"🎲 {n}d{sides}: {rolls} = {sum(rolls)}")
except:
await message.channel.send("Usage: !roll 2d6")
elif command in ("!flip", "!coinflip"):
await message.channel.send(f"🪙 {'Heads' if random.random() > 0.5 else 'Tails'}")
elif command == "!8ball":
responses = ["It is certain.", "Without a doubt.", "Yes definitely.", "Most likely.",
"Outlook good.", "Signs point to yes.", "Reply hazy try again.",
"Ask again later.", "Cannot predict now.", "Don't count on it.",
"My reply is no.", "My sources say no.", "Outlook not so good.", "Very doubtful."]
await message.channel.send(f"🎱 {random.choice(responses)}")
elif command == "!rps":
choices = ["rock", "paper", "scissors"]
user_choice = rest.lower()
if user_choice not in choices:
await message.channel.send("Choose: rock, paper, or scissors")
return
bot_choice = random.choice(choices)
wins = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
if user_choice == bot_choice:
result = "Tie!"
elif wins[user_choice] == bot_choice:
result = "You win! +25 coins"
economy[message.author.id] += 25
else:
result = "You lose! -10 coins"
economy[message.author.id] -= 10
await message.channel.send(f"✊ You: {user_choice} | Me: {bot_choice} — {result}")
elif command == "!slots":
symbols = ["🍒", "🍋", "🍊", "⭐", "💎", "7️⃣"]
s = [random.choice(symbols) for _ in range(3)]
win = s[0] == s[1] == s[2]
payout = 500 if win else -50
economy[message.author.id] += payout
await message.channel.send(f"🎰 {s[0]} | {s[1]} | {s[2]}\n{'JACKPOT! +500 coins!' if win else '-50 coins'}")
elif command == "!trivia":
q, a = random.choice(TRIVIA_QUESTIONS)
active_trivia[message.channel.id] = (q, a)
await message.channel.send(f"❓ {q}\nType your answer!")
elif command == "!joke":
await message.channel.send(f"😂 {random.choice(JOKES)}")
elif command == "!roast":
target = message.mentions[0] if message.mentions else message.author
await message.channel.send(f"🔥 {target.mention} — {random.choice(ROASTS)}")
elif command == "!compliment":
target = message.mentions[0] if message.mentions else message.author
await message.channel.send(f"💖 {target.mention} — {random.choice(COMPLIMENTS)}")
elif command == "!ship":
if len(message.mentions) >= 2:
u1, u2 = message.mentions[0], message.mentions[1]
elif len(message.mentions) == 1:
u1, u2 = message.author, message.mentions[0]
else:
await message.channel.send("Mention at least one user.")
return
pct = random.randint(1, 100)
bar = "💗" * (pct // 10) + "🖤" * (10 - pct // 10)
await message.channel.send(f"💘 {u1.display_name} x {u2.display_name}\n{bar} {pct}%")
elif command == "!rate":
await message.channel.send(f"⭐ I rate {rest} a {random.randint(1,10)}/10")
elif command == "!choose":
options = [o.strip() for o in rest.split('|')]
if len(options) < 2:
await message.channel.send("Separate options with |")
return
await message.channel.send(f"✅ I choose: {random.choice(options)}")
elif command == "!reverse":
await message.channel.send(rest[::-1])
elif command == "!mock":
await message.channel.send(mock_text(rest))
elif command == "!clap":
await message.channel.send(' 👏 '.join(rest.split()))
elif command == "!emojify":
await message.channel.send(to_emojify(rest))
elif command == "!tinytext":
await message.channel.send(to_tinytext(rest))
elif command == "!uwu":
await message.channel.send(uwuify(rest))
elif command == "!pirate":
await message.channel.send(pirate_speak(rest))
elif command == "!yell":
await message.channel.send(rest.upper() + "!!!")
elif command == "!whisper":
await message.channel.send(f"{rest.lower()}...")
elif command == "!repeat":
parts = rest.split(' ', 1)
try:
n = min(int(parts[0]), 10)
text = parts[1] if len(parts) > 1 else ""
await message.channel.send('\n'.join([text] * n))
except:
await message.channel.send("Usage: !repeat [n] [text]")
elif command == "!echo":
await message.channel.send(rest)
elif command == "!hype":
hypes = ["LET'S GOOO 🔥", "INSANE 💪", "W MOVE FR 🚀", "ABSOLUTE UNIT 💥", "GOATED 🏆", "NO CAP 🧢", "FRFR 💯", "SHEESH 😤"]
await message.channel.send(random.choice(hypes))
elif command == "!fact":
await message.channel.send(f"💡 {random.choice(fun_facts)}")
elif command == "!wyr":
a, b = random.choice(would_you_rather)
embed = Embed(title="Would You Rather?", color=Color.orange())
embed.add_field(name="🅰️", value=a, inline=True)
embed.add_field(name="🅱️", value=b, inline=True)
msg = await message.channel.send(embed=embed)
await msg.add_reaction("🅰️")
await msg.add_reaction("🅱️")
elif command == "!riddle":
if active_riddle.get(message.channel.id):
q, _ = active_riddle[message.channel.id]
await message.channel.send(f"🧩 Still waiting: {q}")
else:
q, a = random.choice(riddles)
active_riddle[message.channel.id] = (q, a)
await message.channel.send(f"🧩 {q}")
elif command == "!meme":
await message.channel.send(f"🖼️ Template: {random.choice(meme_templates)}")
elif command == "!dice":
sides = int(rest) if rest.isdigit() else 6
await message.channel.send(f"🎲 Rolled {random.randint(1, sides)} (d{sides})")
elif command == "!magic":
outcomes = ["✨ YES", "🌑 NO", "🔮 UNCLEAR", "⚡ ABSOLUTELY", "💀 NOT A CHANCE", "🎱 MAYBE"]
await message.channel.send(random.choice(outcomes))
elif command == "!fortune":
await message.channel.send(f"🔮 {random.choice(FORTUNES)}")
elif command == "!palindrome":
word = rest.replace(" ", "").lower()
await message.channel.send(f"{rest} {'is' if word == word[::-1] else 'is not'} a palindrome.")
elif command == "!vowels":
await message.channel.send(f"{rest} has {sum(1 for c in rest.lower() if c in 'aeiou')} vowels.")
elif command == "!consonants":
await message.channel.send(f"{rest} has {sum(1 for c in rest.lower() if c.isalpha() and c not in 'aeiou')} consonants.")
elif command == "!piglatin":
await message.channel.send(pig_latin(rest))
elif command == "!ascii":
await message.channel.send(f"\n{rest.upper()}\n")
# ECONOMY
elif command == "!balance":
target = message.mentions[0] if message.mentions else message.author
await message.channel.send(f"💰 {target.display_name}: {economy[target.id]} coins")
elif command == "!daily":
today = datetime.date.today().isoformat()
if daily_claimed[message.author.id] == today:
await message.channel.send("Already claimed today.")
else:
bonus = random.randint(100, 300)
economy[message.author.id] += bonus
daily_claimed[message.author.id] = today
await message.channel.send(f"💵 +{bonus} coins! Total: {economy[message.author.id]}")
elif command == "!give":
if not message.mentions or len(args) < 3:
await message.channel.send("Usage: !give @user [amount]")
return
try:
amount = int(args[-1])
target = message.mentions[0]
if economy[message.author.id] < amount:
await message.channel.send("Not enough coins.")
return
economy[message.author.id] -= amount
economy[target.id] += amount
await message.channel.send(f"✅ Gave {amount} coins to {target.mention}")
except:
await message.channel.send("Usage: !give @user [amount]")
elif command in ("!leaderboard", "!richest"):
top = sorted(economy.items(), key=lambda x: x[1], reverse=True)[:10]
desc = '\n'.join([f"{i+1}. <@{uid}> — {coins} coins" for i, (uid, coins) in enumerate(top)])
embed = Embed(title="💰 Leaderboard", description=desc or "No data.", color=Color.gold())
await message.channel.send(embed=embed)
elif command == "!gamble":
try:
amount = int(rest)
if economy[message.author.id] < amount:
await message.channel.send("Not enough coins.")
return
if random.random() > 0.5:
economy[message.author.id] += amount
await message.channel.send(f"🎰 Won +{amount} coins! Total: {economy[message.author.id]}")
else:
economy[message.author.id] -= amount
await message.channel.send(f"💸 Lost -{amount} coins. Total: {economy[message.author.id]}")
except:
await message.channel.send("Usage: !gamble [amount]")
elif command == "!work":
earn = random.randint(50, 150)
jobs = ["You coded a bot", "You delivered pizzas", "You walked dogs", "You streamed for 3 viewers", "You found a $20 on the ground", "You drove for Uber", "You freelanced a logo"]
economy[message.author.id] += earn
await message.channel.send(f"💼 {random.choice(jobs)}. +{earn} coins.")
elif command == "!rob":
if not message.mentions:
await message.channel.send("Mention someone to rob.")
return
target = message.mentions[0]
if economy[target.id] < 50:
await message.channel.send("They're too broke.")
return
if random.random() > 0.5:
stolen = random.randint(10, min(200, economy[target.id]))
economy[target.id] -= stolen
economy[message.author.id] += stolen
await message.channel.send(f"🦹 Stole {stolen} coins from {target.mention}!")
else:
fine = random.randint(50, 150)
economy[message.author.id] -= fine
await message.channel.send(f"🚨 Caught! Fined {fine} coins.")
elif command == "!shop":
desc = '\n'.join([f"{item} — {price} coins" for item, price in shop_items.items()])
await message.channel.send(embed=Embed(title="🏪 Shop", description=desc, color=Color.green()))
elif command == "!buy":
item = rest.lower()
if item not in shop_items:
await message.channel.send("Item not found. Use !shop")
return
price = shop_items[item]
if economy[message.author.id] < price:
await message.channel.send(f"Need {price} coins.")
return
economy[message.author.id] -= price
inventory[message.author.id].append(item)
await message.channel.send(f"✅ Bought {item}.")
elif command == "!inventory":
target = message.mentions[0] if message.mentions else message.author
items = inventory[target.id]
await message.channel.send(f"🎒 {target.display_name}: {', '.join(items) if items else 'Empty'}")
elif command == "!sell":
item = rest.lower()
if item not in inventory[message.author.id]:
await message.channel.send("You don't own that.")
return
inventory[message.author.id].remove(item)
sell_price = shop_items.get(item, 50) // 2
economy[message.author.id] += sell_price
await message.channel.send(f"💵 Sold {item} for {sell_price} coins.")
elif command == "!lottery":
await message.channel.send(f"🎟️ Your number: {random.randint(1,1000)}")
elif command == "!invest":
try:
amount = int(rest)
if economy[message.author.id] < amount:
await message.channel.send("Not enough coins.")
return
multiplier = random.uniform(0.5, 2.5)
result = int(amount * multiplier)
gain = result - amount
economy[message.author.id] += gain
await message.channel.send(f"📈 Returned {result} coins ({'+'if gain>=0 else ''}{gain})")
except:
await message.channel.send("Usage: !invest [amount]")
elif command == "!bankrob":
if random.random() > 0.3:
loot = random.randint(500, 2000)
economy[message.author.id] += loot
await message.channel.send(f"🏦 Heist success! +{loot} coins")
else:
fine = random.randint(200, 500)
economy[message.author.id] -= fine
await message.channel.send(f"自动化 Caught! -{fine} coins")
# SOCIAL
elif command == "!hug":
target = message.mentions[0] if message.mentions else None
if target:
hug_counts[target.id] += 1
await message.channel.send(f"🤗 {message.author.display_name} hugs {target.mention}! ({hug_counts[target.id]} hugs)")
elif command == "!slap":
target = message.mentions[0] if message.mentions else None
if target:
await message.channel.send(f"👋 {message.author.display_name} slaps {target.mention}!")
elif command == "!pat":
target = message.mentions[0] if message.mentions else None
if target:
pat_counts[target.id] += 1
await message.channel.send(f"🫳 {message.author.display_name} pats {target.mention}. ({pat_counts[target.id]} pats)")
elif command == "!poke":
target = message.mentions[0] if message.mentions else None
if target:
await message.channel.send(f"👉 {message.author.display_name} pokes {target.mention}!")
elif command == "!wave":
target = message.mentions[0] if message.mentions else None
if target:
await message.channel.send(f"👋 {message.author.display_name} waves at {target.mention}!")
elif command == "!highfive":
target = message.mentions[0] if message.mentions else None
if target:
await message.channel.send(f"🙌 {message.author.display_name} high fives {target.mention}!")
elif command == "!cry":
await message.channel.send(f"😭 {message.author.display_name} is crying...")
elif command == "!laugh":
target = message.mentions[0] if message.mentions else None
if target:
await message.channel.send(f"😂 {message.author.display_name} laughs at {target.mention}!")
elif command == "!marry":
target = message.mentions[0] if message.mentions else None
if not target:
await message.channel.send("Mention someone.")
return
if message.author.id in marriage:
await message.channel.send(f"Already married to <@{marriage[message.author.id]}>!")
return
marriage[message.author.id] = target.id
marriage[target.id] = message.author.id
await message.channel.send(f"💍 {message.author.mention} and {target.mention} are married! 🎊")
elif command == "!divorce":
if message.author.id not in marriage:
await message.channel.send("Not married.")
return
partner_id = marriage.pop(message.author.id)
marriage.pop(partner_id, None)
divorces[message.author.id] += 1
await message.channel.send(f"💔 Divorced. ({divorces[message.author.id]} total)")
elif command == "!partner":
if message.author.id in marriage:
await message.channel.send(f"💑 Married to: <@{marriage[message.author.id]}>")
else:
await message.channel.send("Not married.")
elif command == "!rep":
target = message.mentions[0] if message.mentions else None
if not target:
await message.channel.send("Mention someone.")
return
now = time.time()
if message.author.id in rep_cooldown and now - rep_cooldown[message.author.id] < 86400:
await message.channel.send("Already gave rep today.")
return
rep_cooldown[message.author.id] = now
trivia_scores[target.id] += 1
await message.channel.send(f"⭐ Gave rep to {target.mention}! They have {trivia_scores[target.id]}.")
elif command == "!reps":
target = message.mentions[0] if message.mentions else message.author
await message.channel.send(f"⭐ {target.display_name}: {trivia_scores[target.id]} rep")
elif command == "!birthday":
sub = args[1].lower() if len(args) > 1 else ""
if sub == "set" and len(args) > 2:
birthdays[message.author.id] = args[2]
await message.channel.send(f"🎂 Birthday set to {args[2]}")
elif sub == "check":
target = message.mentions[0] if message.mentions else message.author
await message.channel.send(f"🎂 {target.display_name}: {birthdays.get(target.id, 'Not set')}")
elif command == "!confess":
if confession_channel_id:
ch = client.get_channel(confession_channel_id)
if ch:
embed = Embed(title="Anonymous Confession", description=rest, color=Color.dark_gray())
await ch.send(embed=embed)
await message.add_reaction("✅")
else:
await message.channel.send("No confession channel set.")
elif command == "!quote":
if quotes:
await message.channel.send(f'💬 "{random.choice(quotes)}"')
else:
await message.channel.send("No quotes yet. Use !addquote [text]")
elif command == "!addquote":
if rest:
quotes.append(rest)
await message.channel.send(f"✅ Quote #{len(quotes)} added.")
# MOD
elif command == "!warn":
if not message.mentions:
await message.channel.send("Mention someone.")
return
target = message.mentions[0]
reason = ' '.join(args[2:]) if len(args) > 2 else "No reason"
warnings[target.id].append(reason)
await message.channel.send(f"⚠️ {target.mention} warned ({len(warnings[target.id])}). Reason: {reason}")
elif command == "!warnings":
target = message.mentions[0] if message.mentions else message.author
w = warnings[target.id]
if w:
desc = '\n'.join([f"{i+1}. {r}" for i, r in enumerate(w)])
await message.channel.send(f"⚠️ {target.display_name} has {len(w)} warnings:\n{desc}")
else:
await message.channel.send(f"{target.display_name} has no warnings.")
elif command == "!clearwarnings":
if not message.mentions:
await message.channel.send("Mention someone.")
return
target = message.mentions[0]
warnings[target.id] = []
await message.channel.send(f"✅ Cleared warnings for {target.mention}")
elif command == "!mute":
if not message.mentions:
await message.channel.send("Mention someone.")
return
target = message.mentions[0]
duration = int(args[2]) if len(args) > 2 and args[2].isdigit() else 60
mute_role = discord.utils.get(message.guild.roles, name="Muted")
if not mute_role:
mute_role = await message.guild.create_role(name="Muted")
for ch in message.guild.channels:
try:
await ch.set_permissions(mute_role, send_messages=False, speak=False)
except:
pass
await target.add_roles(mute_role)
temp_mutes[target.id] = {"until": time.time() + duration, "guild_id": message.guild.id}
await message.channel.send(f"🔇 {target.mention} muted for {duration}s")
elif command == "!unmute":
if not message.mentions:
await message.channel.send("Mention someone.")
return
target = message.mentions[0]
mute_role = discord.utils.get(message.guild.roles, name="Muted")
if mute_role and mute_role in target.roles:
await target.remove_roles(mute_role)
await message.channel.send(f"🔊 {target.mention} unmuted.")
elif command == "!slowmode":
try:
await message.channel.edit(slowmode_delay=int(rest))
await message.channel.send(f"🐢 Slowmode: {rest}s")
except:
await message.channel.send("Usage: !slowmode [seconds]")
elif command == "!purge":
try:
n = min(int(rest), 100)
deleted = await message.channel.purge(limit=n + 1)
await message.channel.send(f"🗑️ Deleted {len(deleted)-1} messages.", delete_after=3)
except:
await message.channel.send("No permission.")
elif command == "!lock":
try:
await message.channel.set_permissions(message.guild.default_role, send_messages=False)
await message.channel.send("🔒 Locked.")
except:
await message.channel.send("No permission.")
elif command == "!unlock":
try:
await message.channel.set_permissions(message.guild.default_role, send_messages=True)
await message.channel.send("🔓 Unlocked.")
except:
await message.channel.send("No permission.")
elif command == "!kick":
if not message.mentions:
await message.channel.send("Mention someone.")
return
target = message.mentions[0]
reason = ' '.join(args[2:]) if len(args) > 2 else "No reason"
try:
await target.kick(reason=reason)
await message.channel.send(f"👢 Kicked {target.mention}.")
except:
await message.channel.send("No permission.")
elif command == "!ban":
if not message.mentions:
await message.channel.send("Mention someone.")
return
target = message.mentions[0]
reason = ' '.join(args[2:]) if len(args) > 2 else "No reason"
try:
await target.ban(reason=reason)
await message.channel.send(f"🔨 Banned {target.mention}.")
except:
await message.channel.send("No permission.")
elif command == "!unban":
if not rest:
await message.channel.send("Usage: !unban [user#tag]")
return
banned = [entry async for entry in message.guild.bans()]
target = discord.utils.find(lambda e: str(e.user) == rest, banned)
if target:
await message.guild.unban(target.user)
await message.channel.send(f"✅ Unbanned {target.user}")
else:
await message.channel.send("Not found in ban list.")
elif command == "!softban":
if not message.mentions:
await message.channel.send("Mention someone.")
return
target = message.mentions[0]
try:
await target.ban(delete_message_days=7)
await message.guild.unban(target)
await message.channel.send(f"🧹 Softbanned {target.mention}")
except:
await message.channel.send("No permission.")
elif command == "!nick":
if not message.mentions:
await message.channel.send("Mention someone.")
return
target = message.mentions[0]
new_nick = ' '.join(args[2:]) if len(args) > 2 else None
try:
await target.edit(nick=new_nick)
await message.channel.send("✅ Nickname updated.")
except:
await message.channel.send("No permission.")
elif command == "!deafen":
if not message.mentions:
return
target = message.mentions[0]
try:
await target.edit(deafen=True)
await message.channel.send(f"🔕 {target.mention} deafened.")
except:
await message.channel.send("No permission.")
elif command == "!undeafen":
if not message.mentions:
return
target = message.mentions[0]
try:
await target.edit(deafen=False)
await message.channel.send(f"🔔 {target.mention} undeafened.")
except:
await message.channel.send("No permission.")
elif command == "!move":
if not message.mentions:
return
target = message.mentions[0]
vc_name = ' '.join(args[2:]) if len(args) > 2 else None
if vc_name:
vc = discord.utils.find(lambda c: c.name.lower() == vc_name.lower(), message.guild.voice_channels)
if vc and target.voice:
try:
await target.move_to(vc)
await message.channel.send(f"➡️ Moved {target.mention} to {vc.name}")
except:
await message.channel.send("No permission.")
elif command == "!clearreactions":
if message.reference:
try:
ref_msg = await message.channel.fetch_message(message.reference.message_id)
await ref_msg.clear_reactions()
await message.channel.send("✅ Reactions cleared.")
except:
await message.channel.send("No permission.")
# UTILITY
elif command == "!poll":
parts = [p.strip() for p in rest.split('|')]
if len(parts) < 2:
await message.channel.send("Usage: !poll question | opt1 | opt2")
return
question, options = parts[0], parts[1:]
emojis = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
desc = '\n'.join([f"{emojis[i]} {opt}" for i, opt in enumerate(options[:10])])
embed = Embed(title=f"📊 {question}", description=desc, color=Color.blue())
poll_msg = await message.channel.send(embed=embed)
for i in range(min(len(options), 10)):
await poll_msg.add_reaction(emojis[i])
polls[poll_msg.id] = {"question": question, "options": options}
elif command == "!endpoll":
if rest.isdigit() and int(rest) in polls:
await message.channel.send(f"📊 Poll {polls[int(rest)]['question']} ended.")
del polls[int(rest)]
elif command == "!remind":
try:
seconds = int(args[1])
reminder_text = ' '.join(args[2:]) if len(args) > 2 else "reminder"
reminders.append({"time": time.time() + seconds, "text": reminder_text, "user_id": message.author.id, "channel_id": message.channel.id})
await message.channel.send(f"⏰ Reminder in {seconds}s: {reminder_text}")
except:
await message.channel.send("Usage: !remind [seconds] [text]")