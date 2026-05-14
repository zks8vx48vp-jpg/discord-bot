import discord
from discord.ext import commands

TOKEN = "حط_توكن_البوت_هنا"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# =========================
# بيانات اللعبة
# =========================

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
                emoji="☠️",
                description="إضافة قاتل"
            ),

            discord.SelectOption(
                label="طبيب",
                emoji="💊",
                description="إضافة طبيب"
            ),

            discord.SelectOption(
                label="مدني",
                emoji="👤",
                description="إضافة مدني"
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

        await update_message(gid)

        await interaction.response.defer()


# =========================
# قائمة الإزالة -
# =========================

class RemoveSelect(discord.ui.Select):
    def __init__(self):

        options = [

            discord.SelectOption(
                label="قاتل",
                emoji="☠️",
                description="إزالة قاتل"
            ),

            discord.SelectOption(
                label="طبيب",
                emoji="💊",
                description="إزالة طبيب"
            ),

            discord.SelectOption(
                label="مدني",
                emoji="👤",
                description="إزالة مدني"
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

        await update_message(gid)

        await interaction.response.defer()


# =========================
# الواجهة
# =========================

class GameView(discord.ui.View):
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

        await interaction.response.send_message(
            "✅ تم تأكيد الأدوار"
        )

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


# =========================
# تحديث الرسالة
# =========================

async def update_message(gid):

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
        view=GameView()
    )


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
        "message": None
    }

    total = 5

    msg = await ctx.send(
        f"""
# لعبة المستذئب

☠️ قاتل: 1
💊 طبيب: 1
👤 مدني: 3

الأدوار: {total}/24
""",
        view=GameView()
    )

    games[gid]["message"] = msg


# =========================
# تشغيل البوت
# =========================

bot.run(TOKEN)
