import discord
from discord.ext import commands
from discord.ui import View, Button
import random
import os

TOKEN = os.environ.get("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

games = {}


# 🚀 تشغيل البوت
@bot.event
async def on_ready():
    print(f"البوت شغال: {bot.user}")


# 🎮 لوحة الانضمام (Lobby)
class LobbyView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎮 انضمام", style=discord.ButtonStyle.green)
    async def join(self, interaction: discord.Interaction, button: Button):

        gid = interaction.guild.id
        g = games.get(gid)

        if not g:
            return await interaction.response.send_message("❌ ما في لعبة", ephemeral=True)

        if interaction.user in g["players"]:
            return await interaction.response.send_message("⚠️ أنت داخل مسبقًا", ephemeral=True)

        g["players"].append(interaction.user)

        await interaction.response.send_message("✅ انضممت للعبة!", ephemeral=True)


# 🌙 أزرار الليل (قتل / علاج)
class NightView(View):
    def __init__(self, guild_id):
        super().__init__(timeout=60)
        self.guild_id = guild_id

    @discord.ui.button(label="☠️ قتل", style=discord.ButtonStyle.red)
    async def kill(self, interaction: discord.Interaction, button: Button):

        g = games.get(self.guild_id)

        if g["roles"].get(interaction.user) != "قاتل":
            return await interaction.response.send_message("❌ مو أنت القاتل", ephemeral=True)

        g["killed"] = interaction.user
        await interaction.response.send_message("☠️ تم اختيار الضحية", ephemeral=True)

    @discord.ui.button(label="💊 علاج", style=discord.ButtonStyle.green)
    async def heal(self, interaction: discord.Interaction, button: Button):

        g = games.get(self.guild_id)

        if g["roles"].get(interaction.user) != "طبيب":
            return await interaction.response.send_message("❌ مو أنت الطبيب", ephemeral=True)

        g["healed"] = interaction.user
        await interaction.response.send_message("💊 تم اختيار العلاج", ephemeral=True)


# 🎮 بدء اللعبة
@bot.command(name="العبة")
async def start_game(ctx):
    gid = ctx.guild.id

    if gid in games:
        return await ctx.send("⚠️ في لعبة شغالة بالفعل")

    games[gid] = {
        "players": [],
        "roles": {},
        "alive": [],
        "killed": None,
        "healed": None,
        "votes": {}
    }

    view = LobbyView()

    await ctx.send("🎮 لعبة القاتل والطبيب بدأت!\nاضغط زر الانضمام 👇", view=view)


# ▶️ بدء وتوزيع الأدوار
@bot.command(name="ابدأ")
async def start(ctx):
    g = games.get(ctx.guild.id)

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

    await ctx.send("🌙 بدأت اللعبة! اكتب !ليل")


# 🌙 تشغيل الليل (أزرار)
@bot.command(name="ليل")
async def night(ctx):
    g = games.get(ctx.guild.id)
    if not g:
        return

    view = NightView(ctx.guild.id)

    await ctx.send("🌙 الليل بدأ... استخدم الأزرار 👇", view=view)


# 🌅 النهار
@bot.command(name="نهار")
async def day(ctx):
    g = games.get(ctx.guild.id)

    killed = g["killed"]
    healed = g["healed"]

    if killed and killed != healed:
        if killed in g["alive"]:
            g["alive"].remove(killed)
        result = f"☠️ مات {killed.mention}"
    else:
        result = "💊 ما مات أحد"

    g["killed"] = None
    g["healed"] = None

    await ctx.send(f"🌅 النهار بدأ\n{result}")


# 🗳️ التصويت
@bot.command(name="تصويت")
async def vote(ctx, member: discord.Member):

    g = games.get(ctx.guild.id)

    if ctx.author not in g["alive"]:
        return await ctx.send("❌ أنت ميت")

    g["votes"][member] = g["votes"].get(member, 0) + 1

    await ctx.send(f"🗳️ صوتت لـ {member.mention}")


# ☠️ نتيجة التصويت
@bot.command(name="نتيجة")
async def result(ctx):

    g = games.get(ctx.guild.id)

    if not g["votes"]:
        return await ctx.send("❌ ما في تصويت")

    most = max(g["votes"], key=g["votes"].get)

    if most in g["alive"]:
        g["alive"].remove(most)

    g["votes"] = {}

    await ctx.send(f"☠️ تم إعدام {most.mention}")


# 🏁 فحص الفوز
@bot.command(name="فحص")
async def check(ctx):

    g = games.get(ctx.guild.id)

    killers = [p for p in g["alive"] if g["roles"].get(p) == "قاتل"]
    others = [p for p in g["alive"] if g["roles"].get(p) != "قاتل"]

    if len(killers) == 0:
        return await ctx.send("🏆 المدنيين فازوا!")

    if len(killers) >= len(others):
        return await ctx.send("🏆 القتلة فازوا!")

    await ctx.send("🎮 اللعبة مستمرة")
