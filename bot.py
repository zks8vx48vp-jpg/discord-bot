import discord
from discord.ext import commands
import random
import asyncio

TOKEN = "حط_توكن_البوت_هنا"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

games = {}

# تشغيل البوت
@bot.event
async def on_ready():
    print(f"✅ اشتغل البوت: {bot.user}")

# بدء اللعبة
@bot.command(name="مافيا")
async def mafia(ctx):
    guild_id = ctx.guild.id

    if guild_id in games:
        await ctx.send("⚠️ فيه لعبة شغالة بالفعل")
        return

    games[guild_id] = {
        "players": [],
        "started": False
    }

    await ctx.send(
        "🎭 بدأت لعبة المافيا!\n"
        "اكتب !دخول عشان تدخل\n"
        "الادمن يكتب !ابدأ لما يكتملون"
    )

# دخول اللاعبين
@bot.command(name="دخول")
async def join(ctx):
    guild_id = ctx.guild.id

    if guild_id not in games:
        await ctx.send("❌ مافيه لعبة شغالة")
        return

    player = ctx.author

    if player in games[guild_id]["players"]:
        await ctx.send("⚠️ انت داخل بالفعل")
        return

    games[guild_id]["players"].append(player)

    await ctx.send(f"✅ دخل {player.mention}")

# بدء توزيع الرتب
@bot.command(name="ابدأ")
async def start(ctx):
    guild_id = ctx.guild.id

    if guild_id not in games:
        await ctx.send("❌ مافيه لعبة")
        return

    players = games[guild_id]["players"]

    if len(players) < 4:
        await ctx.send("⚠️ لازم 4 لاعبين على الأقل")
        return

    roles = ["قاتل", "طبيب"]
    
    while len(roles) < len(players):
        roles.append("مدني")

    random.shuffle(roles)

    for player, role in zip(players, roles):
        try:
            await player.send(f"🎭 رتبتك هي: **{role}**")
        except:
            await ctx.send(f"❌ ما قدرت ارسل خاص لـ {player.name}")

    games[guild_id]["started"] = True

    await ctx.send("🔥 بدأت اللعبة وتم توزيع الرتب بالخاص")

# إنهاء اللعبة
@bot.command(name="انهاء")
async def end(ctx):
    guild_id = ctx.guild.id

    if guild_id in games:
        del games[guild_id]
        await ctx.send("🛑 انتهت اللعبة")
    else:
        await ctx.send("❌ مافيه لعبة شغالة")

bot.run(TOKEN)
