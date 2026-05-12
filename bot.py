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


@bot.event
async def on_ready():
    print(f"البوت شغال: {bot.user}")


# 🎮 إنشاء اللعبة (إعدادات)
@bot.command(name="العبة")
async def create_game(ctx, max_players: int = 6, killers: int = 1, doctors: int = 1):

    gid = ctx.guild.id

    games[gid] = {
        "players": [],
        "roles": {},
        "alive": [],
        "max": max_players,
        "killers": killers,
        "doctors": doctors,
        "started": False,
        "message": None,
        "channel": ctx.channel
    }

    view = LobbyView()

    msg = await ctx.send(f"""
🐺 **لعبة المستذئب**

👥 اللاعبين: 0/{max_players}
☠️ قتلة: {killers}
💊 أطباء: {doctors}

📢 انضم أو غادر
""", view=view)

    games[gid]["message"] = msg


# 🎮 اللوبي (انضمام + مغادرة)
class LobbyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎮 انضمام", style=discord.ButtonStyle.green)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):

        g = games[interaction.guild.id]

        if interaction.user in g["players"]:
            return await interaction.response.send_message("⚠️ أنت داخل مسبقًا", ephemeral=True)

        if len(g["players"]) >= g["max"]:
            return await interaction.response.send_message("❌ اللوبي ممتلئ", ephemeral=True)

        g["players"].append(interaction.user)

        await interaction.response.send_message("✅ انضممت", ephemeral=True)

        await update_lobby(interaction.guild.id)


    @discord.ui.button(label="🚪 مغادرة", style=discord.ButtonStyle.red)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):

        g = games[interaction.guild.id]

        if interaction.user in g["players"]:
            g["players"].remove(interaction.user)

        await interaction.response.send_message("🚪 خرجت", ephemeral=True)

        await update_lobby(interaction.guild.id)


# 🔁 تحديث اللوبي
async def update_lobby(gid):

    g = games[gid]

    text = f"""
🐺 **لعبة المستذئب {len(g['players'])}/{g['max']}**

☠️ قتلة: {g['killers']}
💊 أطباء: {g['doctors']}

👥 المشاركون:
"""

    if not g["players"]:
        text += "لا يوجد أحد"
    else:
        for p in g["players"]:
            text += f"• {p.mention}\n"

    await g["message"].edit(content=text, view=LobbyView())


# ▶️ بدء اللعبة
@bot.command(name="ابدأ")
async def start(ctx):

    g = games[ctx.guild.id]

    if len(g["players"]) < g["max"]:
        return await ctx.send("❌ لازم يكتمل العدد")

    g["started"] = True

    players = g["players"].copy()
    random.shuffle(players)

    roles = []

    for _ in range(g["killers"]):
        roles.append("قاتل")

    for _ in range(g["doctors"]):
        roles.append("طبيب")

    while len(roles) < len(players):
        roles.append("مدني")

    random.shuffle(roles)

    g["alive"] = players.copy()

    for i, p in enumerate(players):
        g["roles"][p] = roles[i]
        try:
            await p.send(f"🎭 دورك: {roles[i]}")
        except:
            pass

    await ctx.send("🚀 بدأت اللعبة!")
