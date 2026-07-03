import discord
from discord.ext import commands
import random
import os

# إعدادات الصلاحيات
intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix='!', intents=intents)

# 1. كلاس الألعاب (مغامرات وسباق)
class AdventureView(discord.ui.View):
    def __init__(self): super().__init__(timeout=60)
    @discord.ui.button(label="مغامرات الغابة", style=discord.ButtonStyle.primary, emoji="🌲")
    async def forest(self, i, b): await i.response.send_message("🌲 أنت الآن في غابة مليئة بالكنوز!", ephemeral=True)
    @discord.ui.button(label="تحدي الذكاء", style=discord.ButtonStyle.success, emoji="🧠")
    async def brain(self, i, b): await i.response.send_message("🧠 حل اللغز التالي للنجاة!", ephemeral=True)
    @discord.ui.button(label="سباق السرعة", style=discord.ButtonStyle.danger, emoji="🏎️")
    async def race(self, i, b): await i.response.send_message("🏎️ انطلق بأقصى سرعة للفوز بالسباق!", ephemeral=True)

# 2. كلاس حجر ورقة مقص
class RPSView(discord.ui.View):
    def __init__(self): super().__init__(timeout=60)
    async def play(self, i, user_c):
        choices = ["حجر 🪨", "ورقة 📄", "مقص ✂️"]
        b_c = random.choice(choices)
        await i.response.send_message(f"أنت اخترت: {user_c} | البوت اختار: {b_c}", ephemeral=True)
    @discord.ui.button(label="حجر", style=discord.ButtonStyle.secondary, emoji="🪨")
    async def rock(self, i, b): await self.play(i, "حجر 🪨")
    @discord.ui.button(label="ورقة", style=discord.ButtonStyle.secondary, emoji="📄")
    async def paper(self, i, b): await self.play(i, "ورقة 📄")
    @discord.ui.button(label="مقص", style=discord.ButtonStyle.secondary, emoji="✂️")
    async def scissors(self, i, b): await self.play(i, "مقص ✂️")

# 3. كلاس التخمين
class GuessView(discord.ui.View):
    def __init__(self): super().__init__(timeout=60)
    @discord.ui.button(label="1", style=discord.ButtonStyle.secondary)
    async def g1(self, i, b): await i.response.send_message(f"النتيجة: {'صح' if random.randint(1,3)==1 else 'خطأ'}", ephemeral=True)
    @discord.ui.button(label="2", style=discord.ButtonStyle.secondary)
    async def g2(self, i, b): await i.response.send_message(f"النتيجة: {'صح' if random.randint(1,3)==2 else 'خطأ'}", ephemeral=True)
    @discord.ui.button(label="3", style=discord.ButtonStyle.secondary)
    async def g3(self, i, b): await i.response.send_message(f"النتيجة: {'صح' if random.randint(1,3)==3 else 'خطأ'}", ephemeral=True)

# 4. الأمر الرئيسي
@bot.command(name='ألعاب')
async def games(ctx):
    embed = discord.Embed(title="🎮 مركز الألعاب الاحترافي", description="اختر فئة من الأزرار:", color=discord.Color.gold())
    view = discord.ui.View()
    
    b1 = discord.ui.Button(label="مغامرات", style=discord.ButtonStyle.primary)
    b1.callback = lambda i: i.response.send_message("اختر لعبة:", view=AdventureView(), ephemeral=True)
    b2 = discord.ui.Button(label="حجر ورقة مقص", style=discord.ButtonStyle.success)
    b2.callback = lambda i: i.response.send_message("اختر حركتك:", view=RPSView(), ephemeral=True)
    b3 = discord.ui.Button(label="تخمين الرقم", style=discord.ButtonStyle.danger)
    b3.callback = lambda i: i.response.send_message("خمن الرقم (1-3):", view=GuessView(), ephemeral=True)
    
    view.add_item(b1); view.add_item(b2); view.add_item(b3)
    await ctx.send(embed=embed, view=view)

@bot.event
async def on_ready(): print(f'✅ البوت {bot.user} جاهز للعب!')

# ضع التوكن هنا مباشرة بين القوسين وعلامات التنصيص
bot.run('YOUR_TOKEN_HERE')
