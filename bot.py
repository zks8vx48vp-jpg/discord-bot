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
        "قاتل": 1,
        "طبيب": 1,
        "مدني": 3,
        "players": [],
        "message": None
    }

    msg = await ctx.send("جاري إنشاء اللعبة...", view=SetupView())

    games[gid]["message"] = msg

    await update_setup(gid)


# =========================
# ⚙️ إعداد اللعبة
# =========================

class SetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        # ➕ إضافة
        class AddSelect(discord.ui.Select):
            def __init__(self):

                options = [
                    discord.SelectOption(label="قاتل", emoji="☠️"),
                    discord.SelectOption(label="طبيب", emoji="💊"),
                    discord.SelectOption(label="مدني", emoji="👤"),
                ]

                super().__init__(
                    placeholder="إضافة +",
                    options=options
                )

            async def callback(self, interaction: discord.Interaction):

                role = self.values[0]
                games[interaction.guild.id][role] += 1

                await update_setup(interaction.guild.id)
                await interaction.response.defer()

        self.add_item(AddSelect())

        # ➖ إزالة
        class RemoveSelect(discord.ui.Select):
            def __init__(self):

                options = [
                    discord.SelectOption(label="قاتل", emoji="☠️"),
                    discord.SelectOption(label="طبيب", emoji="💊"),
                    discord.SelectOption(label="مدني", emoji="👤"),
                ]

                super().__init__(
                    placeholder="إزالة -",
                    options=options
                )

            async def callback(self, interaction: discord.Interaction):

                role = self.values[0]

                if games[interaction.guild.id][role] > 0:
                    games[interaction.guild.id][role] -= 1

                await update_setup(interaction.guild.id)
                await interaction.response.defer()

        self.add_item(RemoveSelect())

    # 🗑 حذف
    @discord.ui.button(label="حذف", style=discord.ButtonStyle.danger)
    async def delete_game(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.message.delete()
        games.pop(interaction.guild.id, None)

    # ✅ تأكيد
    @discord.ui.button(label="تأكيد", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):

        await update_lobby(interaction.guild.id)
        await interaction.response.defer()


# =========================
# 🔁 تحديث الإعداد
# =========================

async def update_setup(gid):

    g = games[gid]

    total = g["قاتل"] + g["طبيب"] + g["مدني"]

    text = f"""
# لعبة المستذئب

☠️ قاتل: {g['قاتل']}
💊 طبيب: {g['طبيب']}
👤 مدني: {g['مدني']}

الأدوار: {total}/24
"""

    await g["message"].edit(content=text, view=SetupView())


# =========================
# 🎮 اللوبي
# =========================

class LobbyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="انضم إلى اللعبة", style=discord.ButtonStyle.success)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):

        g = games[interaction.guild.id]
        total = g["قاتل"] + g["طبيب"] + g["مدني"]

        if interaction.user in g["players"]:
            return await interaction.response.send_message("أنت داخل مسبقًا", ephemeral=True)

        if len(g["players"]) >= total:
            return await interaction.response.send_message("اللعبة ممتلئة", ephemeral=True)

        g["players"].append(interaction.user)

        await update_lobby(interaction.guild.id)
        await interaction.response.defer()

    @discord.ui.button(label="غادر اللعبة", style=discord.ButtonStyle.danger)
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

    total = g["قاتل"] + g["طبيب"] + g["مدني"]

    text = f"""
# لعبة المستذئبين {len(g['players'])}/{total}

تبدأ اللعبة عندما يكتمل العدد.

## المشاركون
"""

    for p in g["players"]:
        text += f"• {p.mention}\n"

    text += f"""

## الأدوار
☠️ قاتل: {g['قاتل']}
💊 طبيب: {g['طبيب']}
👤 مدني: {g['مدني']}
"""

    await g["message"].edit(content=text, view=LobbyView())


bot.run(TOKEN)
