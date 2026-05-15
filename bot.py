import discord
from discord.ext import commands
import os
import random
import asyncio

TOKEN = os.environ.get("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

games = {}

# =========================
# تشغيل البوت
# =========================

@bot.event
async def on_ready():
    print(f"✅ البوت شغال: {bot.user}")


# =========================
# قائمة الإضافة +
# =========================

class AddSelect(discord.ui.Select):
    def __init__(self):

        options = [

            discord.SelectOption(
                label="قاتل",
                emoji="☠️"
            ),

            discord.SelectOption(
                label="طبيب",
                emoji="💊"
            ),

            discord.SelectOption(
                label="مدني",
                emoji="👤"
            )
        ]

        super().__init__(
            placeholder="إضافة +",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        gid = interaction.guild.id

        role = self.values[0]

        games[gid][role] += 1

        await update_setup(gid)

        await interaction.response.defer()


# =========================
# قائمة الإزالة -
# =========================

class RemoveSelect(discord.ui.Select):
    def __init__(self):

        options = [

            discord.SelectOption(
                label="قاتل",
                emoji="☠️"
            ),

            discord.SelectOption(
                label="طبيب",
                emoji="💊"
            ),

            discord.SelectOption(
                label="مدني",
                emoji="👤"
            )
        ]

        super().__init__(
            placeholder="إزالة -",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        gid = interaction.guild.id

        role = self.values[0]

        if games[gid][role] > 0:
            games[gid][role] -= 1

        await update_setup(gid)

        await interaction.response.defer()


# =========================
# واجهة الإعداد
# =========================

class SetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(AddSelect())
        self.add_item(RemoveSelect())

    # ✅ تأكيد
    @discord.ui.button(
        label="تأكيد",
        style=discord.ButtonStyle.success
    )
    async def confirm(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        gid = interaction.guild.id

        game = games[gid]

        total = (
            game["قاتل"] +
            game["طبيب"] +
            game["مدني"]
        )

        text = f"""
# لعبة المستذئبين 0/{total}

تبدأ اللعبة عندما يكتمل العدد.

## المشاركون
لا يوجد مشاركين

## الأدوار

☠️ قاتل: {game['قاتل']}
💊 طبيب: {game['طبيب']}
👤 مدني: {game['مدني']}
"""

        await game["message"].edit(
            content=text,
            view=LobbyView()
        )

        await interaction.response.defer()

    # 🗑 حذف
    @discord.ui.button(
        label="حذف",
        style=discord.ButtonStyle.danger
    )
    async def delete(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.message.delete()

        if interaction.guild.id in games:
            del games[interaction.guild.id]


# =========================
# واجهة اللوبي
# =========================

class LobbyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # 🎮 انضمام
    @discord.ui.button(
        label="انضم إلى اللعبة",
        style=discord.ButtonStyle.success
    )
    async def join(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        gid = interaction.guild.id

        game = games[gid]

        total = (
            game["قاتل"] +
            game["طبيب"] +
            game["مدني"]
        )

        if interaction.user in game["players"]:

            return await interaction.response.send_message(
                "❌ أنت داخل اللعبة مسبقًا",
                ephemeral=True
            )

        if len(game["players"]) >= total:

            return await interaction.response.send_message(
                "❌ اللعبة ممتلئة",
                ephemeral=True
            )

        game["players"].append(interaction.user)

        await update_lobby(gid)

        await interaction.response.defer()

        # =========================
        # بدء اللعبة تلقائي
        # =========================

        if len(game["players"]) == total:

            await start_real_game(gid)

    # 🚪 مغادرة
    @discord.ui.button(
        label="غادر اللعبة",
        style=discord.ButtonStyle.danger
    )
    async def leave(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        gid = interaction.guild.id

        game = games[gid]

        if interaction.user in game["players"]:
            game["players"].remove(interaction.user)

        await update_lobby(gid)

        await interaction.response.defer()


# =========================
# تحديث صفحة الإعداد
# =========================

async def update_setup(gid):

    game = games[gid]

    total = (
        game["قاتل"] +
        game["طبيب"] +
        game["مدني"]
    )

    text = f"""
# لعبة المستذئب

☠️ قاتل: {game['قاتل']}
💊 طبيب: {game['طبيب']}
👤 مدني: {game['مدني']}

الأدوار: {total}/24
"""

    await game["message"].edit(
        content=text,
        view=SetupView()
    )


# =========================
# تحديث اللوبي
# =========================

async def update_lobby(gid):

    game = games[gid]

    total = (
        game["قاتل"] +
        game["طبيب"] +
        game["مدني"]
    )

    text = f"""
# لعبة المستذئبين {len(game['players'])}/{total}

تبدأ اللعبة عندما يكتمل العدد.

## المشاركون
"""

    if not game["players"]:

        text += "لا يوجد مشاركين\n"

    else:

        for player in game["players"]:
            text += f"• {player.mention}\n"

    text += f"""

## الأدوار

☠️ قاتل: {game['قاتل']}
💊 طبيب: {game['طبيب']}
👤 مدني: {game['مدني']}
"""

    await game["message"].edit(
        content=text,
        view=LobbyView()
    )


# =========================
# بدء اللعبة الحقيقية
# =========================

async def start_real_game(gid):

    game = games[gid]

    players = game["players"]

    random.shuffle(players)

    killers = players[:game["قاتل"]]

    doctors = players[
        game["قاتل"]:
        game["قاتل"] + game["طبيب"]
    ]

    civilians = players[
        game["قاتل"] + game["طبيب"]:
    ]

    # =========================
    # إرسال الأدوار
    # =========================

    for p in killers:
        await p.send("☠️ أنت قاتل")

    for p in doctors:
        await p.send("💊 أنت طبيب")

    for p in civilians:
        await p.send("👤 أنت مدني")

    channel = game["message"].channel

    # =========================
    # الليل
    # =========================

    await channel.send("🌙 بدأ الليل")

    await asyncio.sleep(10)

    # =========================
    # النهار
    # =========================

    await channel.send("☀️ بدأ النهار")

    await asyncio.sleep(10)

    # =========================
    # التصويت
    # =========================

    await channel.send("🗳️ بدأ التصويت")


# =========================
# أمر اللعبة
# =========================

@bot.command(name="العبة")
async def game(ctx):

    gid = ctx.guild.id

    games[gid] = {

        "قاتل": 1,
        "طبيب": 1,
        "مدني": 3,

        "players": [],

        "message": None
    }

    msg = await ctx.send(
        "جاري إنشاء اللعبة...",
        view=SetupView()
    )

    games[gid]["message"] = msg

    await update_setup(gid)


# =========================
# تشغيل البوت
# =========================

bot.run(TOKEN)
