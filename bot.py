import discord
from discord.ext import commands
import os

TOKEN = os.environ.get("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

games = {}


@bot.event
async def on_ready():
    print(f"البوت شغال: {bot.user}")


# =========================
# 🎮 إنشاء اللعبة
# =========================

@bot.command(name="العبة")
async def create_game(ctx):

    gid = ctx.guild.id

    games[gid] = {
        "roles": {
            "قاتل": 1,
            "طبيب": 1,
            "مدني": 3
        },
        "players": [],
        "message": None
    }

    msg = await ctx.send(
        "⚙️ جاري إنشاء اللعبة...",
        view=SetupView()
    )

    games[gid]["message"] = msg

    await update_setup(gid)


# =========================
# ➕ إضافة رتبة
# =========================

class AddRoleSelect(discord.ui.Select):
    def __init__(self):

        options = [
            discord.SelectOption(label="قاتل", emoji="☠️"),
            discord.SelectOption(label="طبيب", emoji="💊"),
            discord.SelectOption(label="مدني", emoji="👤")
        ]

        super().__init__(
            placeholder="إضافة +",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        role = self.values[0]

        games[interaction.guild.id]["roles"][role] += 1

        await update_setup(interaction.guild.id)

        await interaction.response.defer()


# =========================
# ➖ حذف رتبة
# =========================

class RemoveRoleSelect(discord.ui.Select):
    def __init__(self):

        options = [
            discord.SelectOption(label="قاتل", emoji="☠️"),
            discord.SelectOption(label="طبيب", emoji="💊"),
            discord.SelectOption(label="مدني", emoji="👤")
        ]

        super().__init__(
            placeholder="إزالة -",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        role = self.values[0]

        if games[interaction.guild.id]["roles"][role] > 0:
            games[interaction.guild.id]["roles"][role] -= 1

        await update_setup(interaction.guild.id)

        await interaction.response.defer()


# =========================
# ⚙️ صفحة الإعداد
# =========================

class SetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(AddRoleSelect())
        self.add_item(RemoveRoleSelect())

    # ✅ تأكيد
    @discord.ui.button(label="تأكيد", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):

        await update_lobby(interaction.guild.id)

        await interaction.response.defer()


# =========================
# 🔁 تحديث صفحة الإعداد
# =========================

async def update_setup(gid):

    g = games[gid]

    total = sum(g["roles"].values())

    text = f"""
# لعبة المستذئب

تم إنشاء لعبة جديدة، اختر الأدوار التي تريد اللعب بها.

الأدوار: {total}/24

☠️ قاتل: {g['roles']['قاتل']}
💊 طبيب: {g['roles']['طبيب']}
👤 مدني: {g['roles']['مدني']}
"""

    await g["message"].edit(
        content=text,
        view=SetupView()
    )


# =========================
# 🎮 صفحة اللوبي
# =========================

class LobbyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # 🎮 انضمام
    @discord.ui.button(label="انضم إلى اللعبة", style=discord.ButtonStyle.green)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):

        g = games[interaction.guild.id]

        total = sum(g["roles"].values())

        if interaction.user in g["players"]:
            return await interaction.response.send_message(
                "⚠️ أنت داخل مسبقًا",
                ephemeral=True
            )

        if len(g["players"]) >= total:
            return await interaction.response.send_message(
                "❌ اللعبة ممتلئة",
                ephemeral=True
            )

        g["players"].append(interaction.user)

        await update_lobby(interaction.guild.id)

        await interaction.response.defer()

    # 🚪 مغادرة
    @discord.ui.button(label="غادر اللعبة", style=discord.ButtonStyle.red)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):

        g = games[interaction.guild.id]

        if interaction.user in g["players"]:
            g["players"].remove(interaction.user)

        await update_lobby(interaction.guild.id)

        await interaction.response.defer()


# =========================
# 🔁 تحديث اللوبي
# =========================

async def update_lobby(gid):

    g = games[gid]

    total = sum(g["roles"].values())

    text = f"""
# لعبة المستذئبين {len(g['players'])}/{total}

تبدأ اللعبة عندما يساوي عدد اللاعبين عدد الأدوار.

## المشاركون
"""

    if not g["players"]:
        text += "لا يوجد مشاركين\n"

    else:
        for p in g["players"]:
            text += f"• {p.mention}\n"

    text += f"""

## الأدوار

☠️ قاتل: {g['roles']['قاتل']}
💊 طبيب: {g['roles']['طبيب']}
👤 مدني: {g['roles']['مدني']}
"""

    await g["message"].edit(
        content=text,
        view=LobbyView()
    )


bot.run(TOKEN)
