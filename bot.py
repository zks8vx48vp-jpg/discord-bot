import discord
from discord.ext import commands
import random
import asyncio

TOKEN = MTQ5MTU2ODcyOTYxMDM4NzYzNw.GAXWJg.fN5hc1q20EkdQzpR2XE4-wenQmfH3yz1O83VoU

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

games = {}

@bot.event
async def on_ready():
    print(f"البوت شغال: {bot.user}")

@bot.command(name="العبة")
async def start_game(ctx):
    guild_id = ctx.guild.id
    if guild_id in games:
        await ctx.send("⚠️ في لعبة شغالة بالفعل!")
        return
    games[guild_id] = {"players": [], "channel": ctx.channel}
    await ctx.send("🎮 بدأت لعبة القاتل والطبيب!\nاكتب **!انضم** للانضمام\nلما يكتمل اللاعبين اكتب **!ابدأ**")

@bot.command(name="انضم")
async def join_game(ctx):
    guild_id = ctx.guild.id
    if guild_id not in games:
        await ctx.send("❌ ما في لعبة! اكتب **!العبة** لبدء لعبة")
        return
    players = games[guild_id]["players"]
    if ctx.author in players:
        await ctx.send("⚠️ أنت منضم بالفعل!")
        return
    players.append(ctx.author)
    await ctx.send(f"✅ {ctx.author.mention} انضم! عدد اللاعبين: {len(players)}")

@bot.command(name="ابدأ")
async def begin_game(ctx):
    guild_id = ctx.guild.id
    if guild_id not in games:
        await ctx.send("❌ ما في لعبة!")
        return
    players = games[guild_id]["players"]
    if len(players) < 4:
        await ctx.send("❌ تحتاج على الأقل 4 لاعبين!")
        return
    random.shuffle(players)
    roles = {}
    roles[players[0]] = "🔪 قاتل"
    roles[players[1]] = "💉 طبيب"
    for p in players[2:]:
        roles[p] = "👤 مواطن"
    games[guild_id]["roles"] = roles
    games[guild_id]["alive"] = list(players)
    games[guild_id]["phase"] = "night"
    await ctx.send("🌙 بدأت اللعبة! كل لاعب راح يستلم دوره بالخاص...")
    for player, role in roles.items():
        try:
            await player.send(f"دورك في اللعبة: **{role}**")
        except:
            pass
    await asyncio.sleep(2)
    await night_phase(ctx, guild_id)

async def night_phase(ctx, guild_id):
    game = games[guild_id]
    alive = game["alive"]
    roles = game["roles"]
    channel = game["channel"]
    await channel.send("🌙 **الليل نزل... الكل نايم**\nالقاتل والطبيب راح يختارون في الخاص!")
    killer = next((p for p, r in roles.items() if r == "🔪 قاتل" and p in alive), None)
    doctor = next((p for p, r in roles.items() if r == "💉 طبيب" and p in alive), None)
    kill_target = None
    save_target = None
    alive_names = "\n".join([f"{i+1}. {p.display_name}" for i, p in enumerate(alive)])
    if killer:
        try:
            await killer.send(f"🔪 اختر ضحيتك (اكتب الرقم):\n{alive_names}")
            def check_killer(m): return m.author == killer and m.channel.type == discord.ChannelType.private
            msg = await bot.wait_for("message", check=check_killer, timeout=60)
            idx = int(msg.content.strip()) - 1
            kill_target = alive[idx]
        except:
            kill_target = random.choice(alive)
    if doctor:
        try:
            await doctor.send(f"💉 من تريد تنقذ؟ (اكتب الرقم):\n{alive_names}")
            def check_doctor(m): return m.author == doctor and m.channel.type == discord.ChannelType.private
            msg = await bot.wait_for("message", check=check_doctor, timeout=60)
            idx = int(msg.content.strip()) - 1
            save_target = alive[idx]
        except:
            save_target = None
    await channel.send("☀️ **الصبح طلع!**")
    if kill_target and kill_target != save_target:
        alive.remove(kill_target)
        role_name = roles[kill_target]
        await channel.send(f"💀 **{kill_target.display_name}** مات الليل! كان دوره: {role_name}")
    else:
        await channel.send("✨ الطبيب أنقذ الضحية! ما مات أحد الليل!")
    winner = check_winner(guild_id)
    if winner:
        await channel.send(f"🏆 **انتهت اللعبة! الفائز: {winner}**")
        del games[guild_id]
        return
    living = "\n".join([f"• {p.display_name}" for p in alive])
    await channel.send(f"👥 **اللاعبون الأحياء:**\n{living}\n\n🗳️ صوتوا على من تظنه القاتل! اكتب **!صوت @اسم**")

def check_winner(guild_id):
    game = games[guild_id]
    alive = game["alive"]
    roles = game["roles"]
    killers = [p for p in alive if roles[p] == "🔪 قاتل"]
    citizens = [p for p in alive if roles[p] != "🔪 قاتل"]
    if not killers:
        return "المواطنون 👤"
    if len(killers) >= len(citizens):
        return "القاتل 🔪"
    return None

@bot.command(name="صوت")
async def vote(ctx, member: discord.Member):
    guild_id = ctx.guild.id
    if guild_id not in games:
        await ctx.send("❌ ما في لعبة!")
        return
    game = games[guild_id]
    alive = game["alive"]
    if member not in alive:
        await ctx.send("❌ هذا اللاعب مو موجود!")
        return
    alive.remove(member)
    role_name = game["roles"][member]
    await ctx.send(f"🗳️ تم إخراج **{member.display_name}**! كان دوره: {role_name}")
    winner = check_winner(guild_id)
    if winner:
        await ctx.send(f"🏆 **انتهت اللعبة! الفائز: {winner}**")
        del games[guild_id]
    else:
        await night_phase(ctx, guild_id)

@bot.command(name="إيقاف")
async def stop_game(ctx):
    guild_id = ctx.guild.id
    if guild_id in games:
        del games[guild_id]
        await ctx.send("🛑 تم إيقاف اللعبة!")

bot.run(TOKEN)
