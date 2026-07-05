import discord
from discord.ext import commands
import random
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

class SpyGame:
    def __init__(self):
        self.players = []
        self.spy = None
        self.topic = None
        self.word = None
        # مكتبة ضخمة من الكلمات
        self.categories = {
            "حيوانات": ["نمر", "أسد", "فهد", "ذئب", "ثعلب", "زرافة", "فيل", "كنغر", "قرد", "دب", "تمساح", "نسر", "صقر", "غزال", "أرنب"],
            "قيمرز": ["سوني", "إكس بوكس", "بي سي", "نينتندو", "سويتش", "ماينكرافت", "قراند", "فورت نايت", "روبلوكس", "كود", "فيفا", "فالورانت", "أوفرواتش"],
            "أكلات": ["كبسة", "برجر", "بيتزا", "شاورما", "سوشي", "ماندي", "مكرونة", "مشاوي", "سلطة", "أرز", "كباب", "ستيك", "شوربة"],
            "أنمي": ["ناروتو", "ون بيس", "هجوم العمالقة", "ديث نوت", "دراغون بول", "قاتل الشياطين", "جوجوتسو كايسن", "هنتر", "بليتش"],
            "فواكه": ["تفاح", "موز", "برتقال", "مانجو", "فراولة", "عنب", "أناناس", "بطيخ", "رمان", "كرز", "كيوي"],
            "سيارات": ["مرسيدس", "بي إم دبليو", "فيراري", "لامبورغيني", "تويوتا", "نيسان", "هيونداي", "فورد", "بورش", "دودج"]
        }

    def get_embed(self):
        player_list = "\n".join([f"BBB@ • {p.name}" for p in self.players]) if self.players else "لا يوجد"
        embed = discord.Embed(title=f"🎮 لعبة برّا السالفة {len(self.players)}/10", color=discord.Color.dark_theme())
        embed.add_field(name="المشاركون", value=player_list, inline=False)
        embed.set_footer(text="BBB @ System | قاعدة بيانات موسعة")
        return embed

session = SpyGame()

class MainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="انضم للعبة", style=discord.ButtonStyle.green)
    async def join(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user not in session.players:
            session.players.append(i.user)
            await i.response.edit_message(embed=session.get_embed())

    @discord.ui.button(label="تأكيد", style=discord.ButtonStyle.primary)
    async def confirm(self, i: discord.Interaction, b: discord.ui.Button):
        if len(session.players) < 3:
            return await i.response.send_message("❌ تحتاج 3 لاعبين على الأقل!", ephemeral=True)
        
        # اختيار عشوائي ذكي
        cat = random.choice(list(session.categories.keys()))
        session.word = random.choice(session.categories[cat])
        session.spy = random.choice(session.players)
        
        # إنشاء الروم وتوزيع الأدوار
        channel = await i.guild.create_text_channel("برّا-السالفة")
        for p in session.players:
            if p == session.spy:
                await p.send("🕵️‍♂️ **أنت برّا السالفة!**")
            else:
                await p.send(f"✅ **أنت داخل السالفة!** التصنيف: {cat} والكلمة: **{session.word}**")
        
        await i.response.edit_message(content=f"🔥 تم إنشاء الروم: {channel.mention}", embed=None, view=None)

@bot.command()
async def لعبه(ctx):
    session.players = []
    await ctx.send(embed=session.get_embed(), view=MainView())

bot.run(os.environ.get('TOKEN'))
