import discord
from discord.ext import commands
import os
import random
import asyncio

TOKEN = os.environ.get("DISCORD_TOKEN")

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

games = {}

# ==================================
# تشغيل البوت
# ==================================

@bot.event
async def on_ready():
    print(f"✅ {bot.user}")


# ==================================
# قوائم الإضافة
# ==================================

class AddRoleSelect(discord.ui.Select):

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

        games[gid]["roles_count"][role] += 1

        await update_setup(gid)

        await interaction.response.defer()


# ==================================
# قوائم الإزالة
# ==================================

class RemoveRoleSelect(discord.ui.Select):

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

        if games[gid]["roles_count"][role] > 0:
            games[gid]["roles_count"][role] -= 1

        await update_setup(gid)

        await interaction.response.defer()


# ==================================
# واجهة الإعداد
# ==================================

class SetupView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(AddRoleSelect())
        self.add_item(RemoveRoleSelect())

    # ==========================
    # تأكيد
    # ==========================

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

        await update_lobby(gid)

        await interaction.response.defer()

    # ==========================
    # حذف
    # ==========================

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


# ==================================
# واجهة اللوبي
# ==================================

class LobbyView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    # ==========================
    # انضمام
    # ==========================

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

        total = total_roles(gid)

        if interaction.user in game["players"]:

            return await interaction.response.send_message(
                "❌ أنت داخل اللعبة",
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

        # ==========================
        # يبدأ تلقائي
        # ==========================

        if len(game["players"]) == total:

            await start_real_game(gid)

    # ==========================
    # مغادرة
    # ==========================

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


# ==================================
# التصويت
# ==================================

class VoteSelect(discord.ui.Select):

    def __init__(self, gid):

        self.gid = gid

        game = games[gid]

        options = []

        for player in game["alive"]:

            options.append(
                discord.SelectOption(
                    label=player.name,
                    value=str(player.id)
                )
            )

        super().__init__(
            placeholder="اختر لاعب للتصويت",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        gid = self.gid

        game = games[gid]

        voted_id = int(self.values[0])

        voted_player = None

        for p in game["alive"]:

            if p.id == voted_id:
                voted_player = p

        if voted_player:

            game["alive"].remove(voted_player)

            await interaction.message.channel.send(
                f"📢 تم طرد {voted_player.mention}"
            )

        await interaction.response.defer()


class VoteView(discord.ui.View):

    def __init__(self, gid):
        super().__init__(timeout=20)

        self.add_item(VoteSelect(gid))


# ==================================
# حساب الأدوار
# ==================================

def total_roles(gid):

    data = games[gid]["roles_count"]

    return (
        data["قاتل"] +
        data["طبيب"] +
        data["مدني"]
    )


# ==================================
# تحديث الإعداد
# ==================================

async def update_setup(gid):

    game = games[gid]

    total = total_roles(gid)

    text = f"""
# لعبة المستذئب

الأدوار: {total}/24

☠️ قاتل: {game['roles_count']['قاتل']}
💊 طبيب: {game['roles_count']['طبيب']}
👤 مدني: {game['roles_count']['مدني']}
"""

    await game["message"].edit(
        content=text,
        view=SetupView()
    )


# ==================================
# تحديث اللوبي
# ==================================

async def update_lobby(gid):

    game = games[gid]

    total = total_roles(gid)

    players_text = ""

    if not game["players"]:

        players_text = "لا يوجد مشاركين"

    else:

        for p in game["players"]:
            players_text += f"• {p.mention}\n"

    text = f"""
# لعبة المستذئبين {len(game['players'])}/{total}

تبدأ اللعبة عندما يكتمل العدد.

## المشاركون
{players_text}

## الأدوار

☠️ قاتل: {game['roles_count']['قاتل']}
💊 طبيب: {game['roles_count']['طبيب']}
👤 مدني: {game['roles_count']['مدني']}
"""

    await game["message"].edit(
        content=text,
        view=LobbyView()
    )


# ==================================
# بدء اللعبة
# ==================================

async def start_real_game(gid):

    game = games[gid]

    players = game["players"][:]

    random.shuffle(players)

    roles = []

    for i in range(game["roles_count"]["قاتل"]):
        roles.append("قاتل")

    for i in range(game["roles_count"]["طبيب"]):
        roles.append("طبيب")

    for i in range(game["roles_count"]["مدني"]):
        roles.append("مدني")

    random.shuffle(roles)

    game["alive"] = players[:]

    # توزيع الأدوار
    for player, role in zip(players, roles):

        game["roles"][player.id] = role

        await player.send(f"🎭 دورك: {role}")

    channel = game["message"].channel

    await channel.send("🎮 بدأت اللعبة")

    # ==================================
    # الحلقة الرئيسية
    # ==================================

    while True:

        alive = game["alive"]

        killers = [
            p for p in alive
            if game["roles"][p.id] == "قاتل"
        ]

        civilians = [
            p for p in alive
            if game["roles"][p.id] != "قاتل"
        ]

        # ==========================
        # فوز
        # ==========================

        if not killers:

            await channel.send("🎉 فاز المدنيين")
            return

        if len(killers) >= len(civilians):

            await channel.send("☠️ فاز القاتل")
            return

        # ==========================
        # الليل
        # ==========================

        await channel.send("🌙 بدأ الليل")

        await asyncio.sleep(10)

        target = random.choice(civilians)

        saved = None

        doctors = [
            p for p in alive
            if game["roles"][p.id] == "طبيب"
        ]

        if doctors:
            saved = random.choice(alive)

        if target != saved:

            game["alive"].remove(target)

            await channel.send(
                f"☠️ مات {target.mention}"
            )

        else:

            await channel.send(
                "💊 الطبيب أنقذ شخصًا"
            )

        # ==========================
        # النهار
        # ==========================

        await channel.send("☀️ بدأ النهار")

        await asyncio.sleep(5)

        # ==========================
        # التصويت
        # ==========================

        await channel.send(
            "🗳️ التصويت بدأ",
            view=VoteView(gid)
        )

        await asyncio.sleep(20)


# ==================================
# أمر اللعبة
# ==================================

@bot.command(name="العبة")
async def game(ctx):

    gid = ctx.guild.id

    games[gid] = {

        "players": [],
        "alive": [],
        "roles": {},

        "roles_count": {
            "قاتل": 1,
            "طبيب": 1,
            "مدني": 3
        },

        "message": None
    }

    msg = await ctx.send(
        "جاري إنشاء اللعبة...",
        view=SetupView()
    )

    games[gid]["message"] = msg

    await update_setup(gid)


# ==================================
# تشغيل البوت
# ==================================

bot.run(TOKEN)
