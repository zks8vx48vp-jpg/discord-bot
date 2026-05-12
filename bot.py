import discord
from discord.ext import commands
from discord.ui import View, Button
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


# 🎮 إنشاء اللعبة
@bot.command(name="العبة")
async def create_game(ctx):

    gid = ctx.guild.id

    games[gid] = {
        "players": [],
        "max": 6,
        "killers": 1,
        "doctors": 1,
        "message": None,
        "started": False
    }

    msg = await ctx.send("🐺 جاري إعداد لعبة المستذئب...", view=SetupView())

    games[gid]["message"] = msg


# ⚙️ لوحة التحكم (الأزرار + و -)
class SetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # ➕ لاعب
    @discord.ui.button(label="➕ لاعب", style=discord.ButtonStyle.green)
    async def add_player(self, interaction: discord.Interaction, button: discord.ui.Button):

        g = games[interaction.guild.id]
        g["max"] += 1

        await update_ui(interaction.guild.id)


    # ➖ لاعب
    @discord.ui.button(label="➖ لاعب", style=discord.ButtonStyle.red)
    async def remove_player(self, interaction: discord.Interaction, button: discord.ui.Button):

        g = games[interaction.guild.id]
        if g["max"] > 3:
            g["max"] -= 1

        await update_ui(interaction.guild.id)


    # ➕ قاتل
    @discord.ui.button(label="➕ قاتل", style=discord.ButtonStyle.danger)
    async def add_killer(self, interaction: discord.Interaction, button: discord.ui.Button):

        g = games[interaction.guild.id]
        g["killers"] += 1

        await update_ui(interaction.guild.id)


    # ➕ طبيب
    @discord.ui.button(label="➕ طبيب", style=discord.ButtonStyle.blurple)
    async def add_doctor(self, interaction: discord.Interaction, button: discord.ui.Button):

        g = games[interaction.guild.id]
        g["doctors"] += 1

        await update_ui(interaction.guild.id)


    # 🎮 انضمام
    @discord.ui.button(label="🎮 انضمام", style=discord.ButtonStyle.green)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):

        g = games[interaction.guild.id]

        if interaction.user in g["players"]:
            return await interaction.response.send_message("⚠️ أنت داخل", ephemeral=True)

        if len(g["players"]) >= g["max"]:
            return await interaction.response.send_message("❌ اللوبي ممتلئ", ephemeral=True)

        g["players"].append(interaction.user)

        await interaction.response.send_message("✅ انضممت", ephemeral=True)

        await update_ui(interaction.guild.id)


    # 🚪 مغادرة
    @discord.ui.button(label="🚪 مغادرة", style=discord.ButtonStyle.gray)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):

        g = games[interaction.guild.id]

        if interaction.user in g["players"]:
            g["players"].remove(interaction.user)

        await interaction.response.send_message("🚪 خرجت", ephemeral=True)

        await update_ui(interaction.guild.id)


# 🔁 تحديث الرسالة
async def update_ui(gid):

    g = games[gid]

    text = f"""
🐺 **لعبة المستذئب**

👥 اللاعبين: {len(g['players'])}/{g['max']}
☠️ قتلة: {g['killers']}
💊 أطباء: {g['doctors']}

👤 المشاركون:
"""

    if not g["players"]:
        text += "لا يوجد أحد"
    else:
        for p in g["players"]:
            text += f"• {p.mention}\n"

    await g["message"].edit(content=text, view=SetupView())


# ▶️ (جاهز لاحقًا للبدء)
@bot.command(name="ابدأ")
async def start(ctx):
    await ctx.send("🚀 جاهز نضيف نظام اللعب بعد اللوبي")
