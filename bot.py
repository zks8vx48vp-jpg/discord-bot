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


# 🎮 إنشاء اللعبة
@bot.command(name="العبة")
async def create_game(ctx):

    gid = ctx.guild.id

    games[gid] = {
        "قاتل": 1,
        "طبيب": 1,
        "مدني": 3,
        "players": [],
        "message": None
    }

    msg = await ctx.send(
        "🐺 جاري إنشاء اللعبة...",
        view=GameView()
    )

    games[gid]["message"] = msg

    await update_game(gid)


# ➕ إضافة رتبة
class AddRoleSelect(discord.ui.Select):
    def __init__(self):

        options = [
            discord.SelectOption(label="قاتل", emoji="☠️"),
            discord.SelectOption(label="طبيب", emoji="💊"),
            discord.SelectOption(label="مدني", emoji="👤")
        ]

        super().__init__(
            placeholder="➕ إضافة رتبة",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        role = self.values[0]

        games[interaction.guild.id][role] += 1

        await update_game(interaction.guild.id)

        await interaction.response.defer()


# ➖ حذف رتبة
class RemoveRoleSelect(discord.ui.Select):
    def __init__(self):

        options = [
            discord.SelectOption(label="قاتل", emoji="☠️"),
            discord.SelectOption(label="طبيب", emoji="💊"),
            discord.SelectOption(label="مدني", emoji="👤")
        ]

        super().__init__(
            placeholder="➖ حذف رتبة",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        role = self.values[0]

        if games[interaction.guild.id][role] > 1:
            games[interaction.guild.id][role] -= 1

        await update_game(interaction.guild.id)

        await interaction.response.defer()


# 🎮 الأزرار
class GameView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(AddRoleSelect())
        self.add_item(RemoveRoleSelect())

    # 🎮 انضمام
    @discord.ui.button(label="🎮 انضم إلى اللعبة", style=discord.ButtonStyle.green)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):

        g = games[interaction.guild.id]

        total_roles = g["قاتل"] + g["طبيب"] + g["مدني"]

        if interaction.user in g["players"]:
            return await interaction.response.send_message(
                "⚠️ أنت داخل مسبقًا",
                ephemeral=True
            )

        if len(g["players"]) >= total_roles:
            return await interaction.response.send_message(
                "❌ اللعبة ممتلئة",
                ephemeral=True
            )

        g["players"].append(interaction.user)

        await update_game(interaction.guild.id)

        await interaction.response.send_message(
            "✅ انضممت إلى اللعبة",
            ephemeral=True
        )

    # 🚪 مغادرة
    @discord.ui.button(label="🚪 غادر اللعبة", style=discord.ButtonStyle.red)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):

        g = games[interaction.guild.id]

        if interaction.user in g["players"]:
            g["players"].remove(interaction.user)

        await update_game(interaction.guild.id)

        await interaction.response.send_message(
            "🚪 غادرت اللعبة",
            ephemeral=True
        )


# 🔁 تحديث الرسالة
async def update_game(gid):

    g = games[gid]

    total_roles = g["قاتل"] + g["طبيب"] + g["مدني"]

    text = f"""
🐺 **المستذئبين {len(g['players'])}/{total_roles}**

📢 تبدأ اللعبة عندما يساوي عدد اللاعبين عدد الأدوار.

## عدد الأدوار
☠️ قاتل: {g['قاتل']}
💊 طبيب: {g['طبيب']}
👤 مدني: {g['مدني']}

## المشاركون
"""

    if not g["players"]:
        text += "لا يوجد مشاركين"
    else:
        for p in g["players"]:
            text += f"• {p.display_name}\n"

    await g["message"].edit(
        content=text,
        view=GameView()
    )


bot.run(TOKEN)
