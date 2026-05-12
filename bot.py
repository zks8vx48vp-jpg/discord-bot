import discord
from discord.ext import commands
import random
import os

TOKEN = os.environ.get("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

games = {}


# 🎮 بدء اللعبة
@bot.command(name="العبة")
async def start_game(ctx):
    gid = ctx.guild.id

    if gid in games:
        return await ctx.send("⚠️ في لعبة شغالة")

    games[gid] = {
        "players": [],
        "roles": {},
        "alive": [],
        "phase": "lobby",
        "channel": ctx.channel,
        "killed": None,
        "healed": None,
        "votes": {}
    }

    await ctx.send("🎮 بدأت اللعبة! اكتب !انضم")


# ➕ انضمام
@bot.command(name="انضم")
async def join(ctx):
    g = games.get(ctx.guild.id)
    if not g:
        return await ctx.send("❌ ما في لعبة")

    if ctx.author in g["players"]:
        return await ctx.send("⚠️ أنت داخل")

    g["players"].append(ctx.author)
    await ctx.send(f"✅ انضم {ctx.author.mention}")


# 📜 بدء وتوزيع أدوار
@bot.command(name="ابدأ")
async def start(ctx):
    g = games.get(ctx.guild.id)
    if not g:
        return

    players = g["players"]

    if len(players) < 3:
        return await ctx.send("❌ لازم 3 لاعبين")

    roles = ["قاتل", "طبيب"] + ["مدني"] * (len(players) - 2)
    random.shuffle(roles)

    g["alive"] = players.copy()

    for i, p in enumerate(players):
        g["roles"][p] = roles[i]
        try:
            await p.send(f"🎭 دورك: {roles[i]}")
        except:
            pass

    g["phase"] = "night"
    await ctx.send("🌙 بدأت اللعبة - الليل بدأ!")


# ☠️ قتل
@bot.command(name="قتل")
async def kill(ctx, member: discord.Member):
    g = games.get(ctx.guild.id)

    if g["roles"].get(ctx.author) != "قاتل":
        return await ctx.send("❌ مو أنت القاتل")

    g["killed"] = member
    await ctx.send("☠️ تم اختيار ضحية")


# 💊 علاج
@bot.command(name="علاج")
async def heal(ctx, member: discord.Member):
    g = games.get(ctx.guild.id)

    if g["roles"].get(ctx.author) != "طبيب":
        return await ctx.send("❌ مو أنت الطبيب")

    g["healed"] = member
    await ctx.send("💊 تم اختيار علاج")


# 🌅 إنهاء الليل → حساب النتائج
@bot.command(name="نهار")
async def day(ctx):
    g = games.get(ctx.guild.id)
    if not g:
        return

    killed = g["killed"]
    healed = g["healed"]

    result = ""

    if killed and killed != healed:
        if killed in g["alive"]:
            g["alive"].remove(killed)
            result = f"☠️ مات {killed.mention}"
    else:
        result = "💊 ما مات أحد"

    g["killed"] = None
    g["healed"] = None
    g["phase"] = "day"

    await ctx.send(f"🌅 النهار بدأ\n{result}")


# 🗳️ تصويت
@bot.command(name="تصويت")
async def vote(ctx, member: discord.Member):
    g = games.get(ctx.guild.id)

    if ctx.author not in g["alive"]:
        return await ctx.send("❌ أنت ميت")

    g["votes"][member] = g["votes"].get(member, 0) + 1
    await ctx.send(f"🗳️ صوتت لـ {member.mention}")


# 🏁 إنهاء التصويت
@bot.command(name="نتيجة")
async def result(ctx):
    g = games.get(ctx.guild.id)

    if not g["votes"]:
        return await ctx.send("❌ ما فيه تصويت")

    most_voted = max(g["votes"], key=g["votes"].get)

    if most_voted in g["alive"]:
        g["alive"].remove(most_voted)

    g["votes"] = {}

    await ctx.send(f"☠️ تم إعدام {most_voted.mention}")


# 🏆 فوز
@bot.command(name="فحص")
async def check_win(ctx):
    g = games.get(ctx.guild.id)

    killers = [p for p in g["alive"] if g["roles"].get(p) == "قاتل"]
    civilians = [p for p in g["alive"] if g["roles"].get(p) != "قاتل"]

    if len(killers) == 0:
        return await ctx.send("🏆 المدنيين فازوا!")

    if len(killers) >= len(civilians):
        return await ctx.send("🏆 القتلة فازوا!")

    await ctx.send("🎮 اللعبة مستمرة")
