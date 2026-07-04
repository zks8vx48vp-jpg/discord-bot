import discord
from discord.ext import commands
import random
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# واجهة الألعاب الجماعية الاحترافية
class CollectiveGamesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🕵️‍♂️ من الجاسوس؟", style=discord.ButtonStyle.danger)
    async def spy_game(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.send_message("🕵️‍♂️ **تنبيه:** ابدأ الآن بإرسال الكلمات السرية للأعضاء! الجاسوس بيننا.. استعدوا للتحقيق! 🔍", ephemeral=False)

    @discord.ui.button(label="⚡ تحدي السرعة", style=discord.ButtonStyle.primary)
    async def speed_game(self, i: discord.Interaction, b: discord.ui.Button):
        words = ["برمجة", "ديسكورد", "احتراف", "تحدي"]
        await i.response.send_message(f"🚀 **تحدي السرعة:** أول من يكتب كلمة **{random.choice(words)}** في الشات هو الفائز! استعدوا! 🔥", ephemeral=False)

    @discord.ui.button(label="🔮 توقعات الجماعة", style=discord.ButtonStyle.success)
    async def prediction(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.send_message("🔮 **توقعاتنا:** هل أنتم جاهزون لمعرفة من سيحقق أكبر إنجاز في السيرفر اليوم؟ اكتبوا 'أنا' للمشاركة! 🌟", ephemeral=False)

# تفعيل الألعاب بكلمة "ألعاب"
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "ألعاب" in message.content or "تحدي" in message.content:
        embed = discord.Embed(
            title="🎮 مركز التحديات الجماعية",
            description="مرحباً بكم يا أبطال! الساحة جاهزة.. من سينتصر اليوم؟ اختر التحدي وابدأ الحماس! 🔥",
            color=discord.Color.dark_gold()
        )
        embed.set_footer(text="نظام الألعاب الجماعية الاحترافي - استمتعوا!")
        await message.reply(embed=embed, view=CollectiveGamesView())

    await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f'✅ النظام الاحترافي يعمل بكفاءة: {bot.user}')

bot.run(os.environ.get('TOKEN'))
