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


# =========================
# تشغيل البوت
# =========================

@bot.event
async def on_ready():
    print(f"✅ {bot.user}")


# =========================
# التصويت
# =========================

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
            placeholder="اختر شخص للتصويت",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        gid = self.gid

        voted_id = int(self.values[0])

        game = games[gid]

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


# =========================
# الانضمام
# =========================

class JoinView(discord.ui.View):

    def __init__(self, gid):
        super().__init__(timeout=None)

        self.gid = gid

    @discord.ui.button(
        label="انضم إلى اللعبة",
        style=discord.ButtonStyle.success
    )
    async def join(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        game = games[self.gid]

        if interaction.user in game["players"]:

            return await interaction.response.send_message(
                "❌ أنت داخل اللعبة",
                ephemeral=True
            )

        game["players"].append(interaction.user)

        players_text = ""

        for p in game["players"]:
            players_text += f"• {p.mention}\n"

        await interaction.message.edit(
            content=f"""
# لعبة المستذئبين {len(game['players'])}/5

## المشاركون
{players_text}
""",
            view=self
        )

        await interaction.response.defer()

        # يبدأ تلقائي
        if len(game["players"]) >= 5 and not game["started"]:

            game["started"] = True

            await start_game(
                self.gid,
                interaction.channel
            )


# =========================
# بدء اللعبة
# =========================

async def start_game(gid, channel):

    game = games[gid]

    players = game["players"][:]

    random.shuffle(players)

    killer = players[0]
    doctor = players[1]

    game["roles"][killer.id] = "قاتل"
    game["roles"][doctor.id] = "طبيب"

    for p in players[2:]:
        game["roles"][p.id] = "مدني"

    game["alive"] = players[:]

    # =========================
    # إرسال الأدوار
    # =========================

    for p in players:

        role = game["roles"][p.id]

        await p.send(f"🎭 دورك: {role}")

    await channel.send("🎮 بدأت اللعبة")

    while True:

        # =========================
        # فحص الفوز
        # =========================

        killers = [
            p for p in game["alive"]
            if game["roles"][p.id] == "قاتل"
        ]

        civilians = [
            p for p in game["alive"]
            if game["roles"][p.id] != "قاتل"
        ]

        if not killers:

            await channel.send("🎉 فاز المدنيين")
            break

        if len(killers) >= len(civilians):

            await channel.send("☠️ فاز القاتل")
            break

        # =========================
        # الليل
        # =========================

        await channel.send("🌙 بدأ الليل")

        await asyncio.sleep(5)

        killer_alive = killers[0]

        targets = [
            p for p in game["alive"]
            if p != killer_alive
        ]

        killed = random.choice(targets)

        # =========================
        # الطبيب
        # =========================

        doctors = [
            p for p in game["alive"]
            if game["roles"][p.id] == "طبيب"
        ]

        saved = None

        if doctors:

            saved = random.choice(game["alive"])

        # =========================
        # القتل
        # =========================

        if killed != saved:

            game["alive"].remove(killed)

            await channel.send(
                f"☠️ مات {killed.mention}"
            )

        else:

            await channel.send(
                "💊 الطبيب أنقذ شخصًا"
            )

        # =========================
        # النهار
        # =========================

        await channel.send("☀️ بدأ النهار")

        await asyncio.sleep(5)

        # =========================
        # التصويت
        # =========================

        await channel.send(
            "🗳️ بدأ التصويت",
            view=VoteView(gid)
        )

        await asyncio.sleep(20)


# =========================
# أمر اللعبة
# =========================

@bot.command(name="العبة")
async def game(ctx):

    gid = ctx.guild.id

    games[gid] = {

        "players": [],
        "alive": [],
        "roles": {},
        "started": False
    }

    await ctx.send(
        """
# لعبة المستذئبين 0/5

اضغط للانضمام
""",
        view=JoinView(gid)
    )


bot.run(TOKEN)
