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

    msg = await ctx.send(
        "جاري إنشاء اللعبة...",
        view=SetupView()
    )

    games[gid]["message"] = msg

    await update_setup(gid)


# =========================
# ⚙️ صفحة الإعداد
# =========================

class SetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # ➕ إضافة
    @discord.ui.button(
        label="إضافة +",
        style=discord.ButtonStyle.blurple,
        row=0
    )
    async def add_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        class AddRoleView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=30)

            @discord.ui.select(
                placeholder="اختر الدور",
                options=[
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
            )
            async def select_role(
                self,
                interaction2: discord.Interaction,
                select: discord.ui.Select
            ):

                role = select.values[0]

                games[interaction.guild.id][role] += 1

                await update_setup(interaction.guild.id)

                await interaction2.response.defer()

        await interaction.response.send_message(
            "اختر الدور الذي تريد إضافته",
            view=AddRoleView(),
            ephemeral=True
        )

    # ➖ إزالة
    @discord.ui.button(
        label="إزالة -",
        style=discord.ButtonStyle.danger,
        row=0
    )
    async def remove_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        class RemoveRoleView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=30)

            @discord.ui.select(
                placeholder="اختر الدور",
                options=[
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
            )
            async def select_role(
                self,
                interaction2: discord.Interaction,
                select: discord.ui.Select
            ):

                role = select.values[0]

                if games[interaction.guild.id][role] > 0:
                    games[interaction.guild.id][role] -= 1

                await update_setup(interaction.guild.id)

                await interaction2.response.defer()

        await interaction.response.send_message(
            "اختر الدور الذي تريد إزالته",
            view=RemoveRoleView(),
            ephemeral=True
        )

    # 🗑 حذف
    @discord.ui.button(
        label="حذف",
        style=discord.ButtonStyle.danger,
        row=0
    )
    async def delete_game(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.message.delete()

        if interaction.guild.id in games:
            del games[interaction.guild.id]

    # ✅ تأكيد
    @discord.ui.button(
        label="تأكيد",
        style=discord.ButtonStyle.success,
        row=1
    )
    async def confirm(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await update_lobby(interaction.guild.id)

        await interaction.response.defer()


# =========================
# 🔁 تحديث الإعداد
# =========================

async def update_setup(gid):

    g = games[gid]

    total = (
        g["قاتل"] +
        g["طبيب"] +
        g["مدني"]
    )

    text = f"""
# لعبة المستذئب

تم إنشاء لعبة جديدة، اختر الأدوار التي تريد اللعب بها.

☠️ قاتل: {g['قاتل']}
💊 طبيب: {g['طبيب']}
👤 مدني: {g['مدني']}

الأدوار: {total}/24
"""

    await g["message"].edit(
        content=text,
        view=SetupView()
    )


# =========================
# 🎮 اللوبي
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

        g = games[interaction.guild.id]

        total = (
            g["قاتل"] +
            g["طبيب"] +
            g["مدني"]
        )

        if interaction.user in g["players"]:
            return await interaction.response.send_message(
                "أنت داخل مسبقًا",
                ephemeral=True
            )

        if len(g["players"]) >= total:
            return await interaction.response.send_message(
                "اللعبة ممتلئة",
                ephemeral=True
            )

        g["players"].append(interaction.user)

        await update_lobby(interaction.guild.id)

        await interaction2.response.defer()

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

    total = (
        g["قاتل"] +
        g["طبيب"] +
        g["مدني"]
    )

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

☠️ قاتل: {g['قاتل']}
💊 طبيب: {g['طبيب']}
👤 مدني: {g['مدني']}
"""

    await g["message"].edit(
        content=text,
        view=LobbyView()
    )


bot.run(TOKEN)
