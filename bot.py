import discord
from discord.ext import commands
import random
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# قاعدة بيانات التصنيفات (موسعة جداً)
CATEGORIES = {
    "حيوانات": ["نمر", "أسد", "زرافة", "فيل", "قرد", "دب", "ثعلب", "ذئب", "تمساح"],
    "قيمرز": ["سوني", "إكس بوكس", "بي سي", "نينتندو", "فورت نايت", "ماينكرافت", "فيفا", "قراند"],
    "أكلات": ["كبسة", "برجر", "بيتزا", "شاورما", "سوشي", "ماندي", "كباب", "ستيك"],
    "أنمي": ["ناروتو", "ون بيس", "هجوم العمالقة", "ديث نوت", "قاتل الشياطين"],
    "سيارات": ["مرسيدس", "بي إم دبليو", "فيراري", "لامبورغيني", "تويوتا", "نيسان"]
}

class GameSession:
    def __init__(self):
        self.players = []
        self.spy = None
        self.word = None
        self.topic = None

session = GameSession()

class CategoryView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        # أزرار التصنيفات
        for cat in CATEGORIES.keys():
            self.add_item(discord.ui.Button(label=cat, custom_id=cat, style=discord.ButtonStyle.secondary))

    async def interaction_check(self, i: discord.Interaction) -> bool:
        cat = i.data['custom_id']
        session.topic = cat
        session.word = random.choice(CATEGORIES[cat])
        session.spy = random.choice(session.players)
        
        # إنشاء الروم
        guild = i.guild
        channel = await guild.create_text_channel(f"برّا-السالفة-{random.randint(1,99)}")
        
        # الرسائل بالخاص
        for p in session.players:
            if p == session.spy:
                await p.send("🕵️‍♂️ **أنت برّا السالفة!**")
            else:
                await p.send(f"✅ **أنت جوا السالفة!**\nالتصنيف: {session.topic}\nالكلمة: **{session.word}**")
        
        await i.response.send_message(f"🔥 بدأت اللعبة! الروم: {channel.mention}", ephemeral=False)
        return True

class MainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="تأكيد", style=discord.ButtonStyle.green, row=0)
    async def confirm(self, i: discord.Interaction, b: discord.ui.Button):
        if len(session.players) < 3:
            return await i.response.send_message("❌ اقل شيء 3 لاعبين!", ephemeral=True)
        await i.response.edit_message(content="🎯 اختر التصنيف لبدء اللعبة:", view=CategoryView())

    @discord.ui.button(label="حذف", style=discord.ButtonStyle.danger, row=0)
    async def delete(self, i: discord.Interaction, b: discord.ui.Button):
        session.players = []
        await i.response.edit_message(content="تم تصفير اللعبة، ابدأ من جديد!", view=MainView())

    @discord.ui.button(label="إضافة +", style=discord.ButtonStyle.secondary, row=1)
    async def add(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.send_message("تم تفعيل وضع الإضافة!", ephemeral=True)

    @discord.ui.button(label="إزالة -", style=discord.ButtonStyle.secondary, row=1)
    async def remove(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.send_message("تم تفعيل وضع الإزالة!", ephemeral=True)

    @discord.ui.button(label="انضم للعبة", style=discord.ButtonStyle.primary, row=2)
    async def join(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user not in session.players:
            session.players.append(i.user)
            msg = f"🎮 لعبة برّا السالفة\nالمشاركون ({len(session.players)}/10):\n" + "\n".join([f"BBB@ • {p.name}" for p in session.players])
            await i.response.edit_message(content=msg)

@bot.command()
async def لعبه(ctx):
    await ctx.send("🎮 **لعبة برّا السالفة**\nاضغط انضم للبدء:", view=MainView())

bot.run(os.environ.get('TOKEN'))
