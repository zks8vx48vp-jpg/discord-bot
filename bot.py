import discord
from discord.ext import commands
from discord.ui import View, Button
import random
import os
import asyncio

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


# 🎮 لوحة الانضمام
class LobbyView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎮 انضمام", style=discord.ButtonStyle.green)
    async def join(self, interaction: discord.Interaction, button: Button):

        g = games.get(interaction.guild.id)

        if not g:
            return await interaction.response.send_message("❌ ما في لعبة", ephemeral=True)

        if interaction.user in g["players"]:
            return await interaction.response.send_message("⚠️ أنت داخل", ephemeral=True)

        g["players"].append(interaction.user)

        await interaction.response.send_message("✅ انضممت!", ephemeral=True)


# 🌙 أزرار الليل
class NightView(View):
    def __init__(self, gid):
        super().__init__(timeout=60)
        self.gid = gid

    @discord.ui.button(label="☠️ قتل", style=discord.ButtonStyle.red)
    async def kill(self, interaction: discord.Interaction, button: Button):

        g = games[self.gid]

        if g["roles"].get(interaction.user) != "قاتل":
            return await interaction.response.send_message("❌ مو أنت القاتل", ephemeral=True)

        g["killed"] = interaction.user
        await interaction.response.send_message("☠️ تم اختيار ضحية", ephemeral=True)

    @discord.ui.button(label="💊 علاج", style=discord.ButtonStyle.green)
    async def heal(self, interaction: discord.Interaction, button: Button):

        g = games[self.gid]

        if g["roles"].get(interaction.user) != "طبيب":
            return await interaction.response.send_message("❌ مو أنت الطبيب", ephemeral=True)

        g["healed"] = interaction.user
        await interaction.response.send_message("💊 تم اختيار علاج", ephemeral=True)


# 🗳️ التصويت بالأزرار
class VoteView(View):
    def __init__(self, gid, alive):
        super().__init__(timeout=30)

        self.gid = gid

        for p in alive:
            self.add_item(VoteButton(p))


class VoteButton(Button):
    def __init__(self, player):
        super().__init__(label=player.display_name, style=discord.ButtonStyle.blurple)
        self.player = player

    async def callback(self, interaction: discord.Interaction):

        g = games[interaction.guild.id]

        if interaction.user not in g["alive"]:
            return await interaction.response.send_message("❌ أنت ميت", ephemeral=True)

        g["votes"][self.player] = g["votes"].get(self.player, 0) + 1

        await interaction.response.send_message("🗳️ تم التصويت", ephemeral=True)


# 🎮 بدء اللعبة
@bot.command(name="العبة")
async def start_game(ctx):

    gid = ctx.guild.id

    games[gid] = {
        "players": [],
        "roles": {},
        "alive": [],
        "killed": None,
        "healed": None,
        "votes": {},
        "channel": ctx.channel
    }

    await ctx.send("🎮 اللعبة بدأت! اضغط انضمام 👇", view=LobbyView())


# ▶️ توزيع الأدوار + تشغيل اللعبة
@bot.command(name="ابدأ")
async def start(ctx):

    g = games[ctx.guild.id]
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

    await ctx.send("🚀 بدأت اللعبة التلقائية!")

    await game_loop(ctx.guild.id)


# 🔁 اللوب التلقائي (كل اللعبة هنا)
async def game_loop(gid):

    g = games[gid]
    channel = g["channel"]

    while True:

        if len(g["alive"]) <= 1:
            break

        # 🌙 ليل
        await channel.send("🌙 الليل بدأ...")
        await channel.send("استخدم الأزرار 👇", view=NightView(gid))

        await asyncio.sleep(20)

        killed = g["killed"]
        healed = g["healed"]

        if killed and killed != healed:
            if killed in g["alive"]:
                g["alive"].remove(killed)
            await channel.send(f"☠️ مات {killed.mention}")
        else:
            await channel.send("💊 ما صار قتل")

        g["killed"] = None
        g["healed"] = None

        # 🌅 نهار
        await channel.send("🌅 النهار بدأ")

        g["votes"] = {}

        await channel.send("🗳️ التصويت بدأ 👇", view=VoteView(gid, g["alive"]))

        await asyncio.sleep(30)

        if g["votes"]:
            most = max(g["votes"], key=g["votes"].get)

            if most in g["alive"]:
                g["alive"].remove(most)

            await channel.send(f"☠️ تم إعدام {most.mention}")

        # 🏁 فحص الفوز
        killers = [p for p in g["alive"] if g["roles"].get(p) == "قاتل"]
        others = [p for p in g["alive"] if g["roles"].get(p) != "قاتل"]

        if len(killers) == 0:
            await channel.send("🏆 المدنيين فازوا!")
            break

        if len(killers) >= len(others):
            await channel.send("🏆 القتلة فازوا!")
            break


bot.run(TOKEN)
