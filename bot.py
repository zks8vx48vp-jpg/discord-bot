import discord
from discord.ext import commands
import random
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

class GameSession:
    def __init__(self):
        self.players = []
        self.spy = None
        self.topic = None
        self.turn_index = 0
        self.active = False
        self.categories = ["حيوانات", "ملابس", "أكلات", "سيارات", "فواكه", "شخصيات كرتون", "مشروبات", "حلويات", "مسلسلات", "أنمي", "كيبوب", "قيمرز"]

session = GameSession()

# واجهة التصويت بالأزرار
class VoteView(discord.ui.View):
    def __init__(self, players):
        super().__init__(timeout=60)
        for p in players:
            self.add_item(self.create_button(p))

    def create_button(self, player):
        btn = discord.ui.Button(label=player.name, style=discord.ButtonStyle.secondary)
        async def callback(i: discord.Interaction):
            await i.response.send_message(f"🗳️ صوتَّ لـ {player.name}", ephemeral=True)
        btn.callback = callback
        return btn

# الواجهة الرئيسية للأزرار
class MainGameView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="👤 انضم للعبة", style=discord.ButtonStyle.green)
    async def join(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user not in session.players:
            session.players.append(i.user)
            await i.response.send_message(f"✅ انضم {i.user.name}", ephemeral=True)
        
    @discord.ui.button(label="🚀 ابدأ اللعبة", style=discord.ButtonStyle.primary)
    async def start(self, i: discord.Interaction, b: discord.ui.Button):
        if len(session.players) < 3:
            return await i.response.send_message("❌ تحتاج 3 لاعبين على الأقل!", ephemeral=True)
        
        session.active = True
        session.spy = random.choice(session.players)
        session.topic = random.choice(session.categories)
        
        for p in session.players:
            if p == session.spy:
                await p.send("🕵️‍♂️ **أنت برّا السالفة!** حاول تمويههم.")
            else:
                await p.send(f"✅ **أنت داخل السالفة!** الموضوع هو: **{session.topic}**")
        
        await i.response.send_message("🔥 **بدأت اللعبة!** تم إرسال الأدوار بالخاص للجميع.")

    @discord.ui.button(label="➡️ دورك انتهى", style=discord.ButtonStyle.danger)
    async def next_turn(self, i: discord.Interaction, b: discord.ui.Button):
        session.turn_index = (session.turn_index + 1) % len(session.players)
        next_p = session.players[session.turn_index]
        await i.response.send_message(f"⏳ الدور الآن لـ {next_p.mention}", ephemeral=False)

    @discord.ui.button(label="🗳️ ابدأ التصويت", style=discord.ButtonStyle.secondary)
    async def vote(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.send_message("🚨 **التصويت:** من هو برّا السالفة؟ اضغط على اسمه:", view=VoteView(session.players))

@bot.event
async def on_ready():
    print(f'✅ النظام الاحترافي يعمل الآن: {bot.user}')

@bot.command()
async def لعبه(ctx):
    embed = discord.Embed(
        title="🎮 نظام 'برّا السالفة' الاحترافي",
        description="استخدم الأزرار فقط للتحكم في اللعبة.",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed, view=MainGameView())

# تشغيل البوت باستخدام متغير البيئة (الذي وضعته في موقع الاستضافة)
bot.run(os.environ.get('TOKEN'))
