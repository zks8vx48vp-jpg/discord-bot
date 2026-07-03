import discord
from discord.ext import commands
import random
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# قائمة التخمين بتنسيق احترافي
class GuessView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
    
    @discord.ui.button(label="1", style=discord.ButtonStyle.blurple)
    async def g1(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.send_message("🎯 لقد اخترت الرقم 1.. جاري التحقق.. الحظ ليس معك هذه المرة!", ephemeral=True)

    @discord.ui.button(label="2", style=discord.ButtonStyle.blurple)
    async def g2(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.send_message("🎉 تهانينا! لقد أصبت الهدف! الرقم 2 هو الفائز.", ephemeral=True)

# قائمة المغامرات بتنسيق احترافي
class AdventureView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        
    @discord.ui.button(label="مغامرة الغابة المظلمة", style=discord.ButtonStyle.success)
    async def forest(self, i: discord.Interaction, b: discord.ui.Button):
        embed = discord.Embed(title="🌲 مغامرة الغابة", description="لقد دخلت الغابة، هل أنت مستعد لمواجهة الوحوش؟", color=discord.Color.green())
        await i.response.send_message(embed=embed, ephemeral=True)

# القائمة الرئيسية
class MainMenuView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="⚔️ ابدأ المغامرة", style=discord.ButtonStyle.success)
    async def adv(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.send_message("اختيار رائع! استعد للرحلة:", view=AdventureView(), ephemeral=True)

    @discord.ui.button(label="🎲 حجر ورقة مقص", style=discord.ButtonStyle.secondary)
    async def rps(self, i: discord.Interaction, b: discord.ui.Button):
        res = random.choice(["حجر 🪨", "ورقة 📄", "مقص ✂️"])
        await i.response.send_message(f"أنا اخترت: **{res}**\nهل فزت عليّ؟", ephemeral=True)

@bot.command()
async def games(ctx):
    embed = discord.Embed(
        title="✨ أهلاً بك في عالم التحدي!",
        description="لقد انضممت إلى المركز الاحترافي للألعاب. اختر طريقك الآن:",
        color=discord.Color.gold()
    )
    embed.set_footer(text="استمتع بوقتك!")
    await ctx.send(embed=embed, view=MainMenuView())

@bot.event
async def on_ready():
    print(f'✅ البوت يعمل بوقار: {bot.user}')

bot.run(os.environ.get('TOKEN'))
