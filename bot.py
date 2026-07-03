import discord
from discord.ext import commands
import os

# إعداد البوت
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# تعريف الأزرار
class MyView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="تحية", style=discord.ButtonStyle.primary)
    async def hello(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("مرحباً بك! أنا البوت الخاص بك.")

    @discord.ui.button(label="وقت النظام", style=discord.ButtonStyle.secondary)
    async def time(self, interaction: discord.Interaction, button: discord.ui.Button):
        import datetime
        now = datetime.datetime.now().strftime("%H:%M:%S")
        await interaction.response.send_message(f"الوقت الحالي هو: {now}")

@bot.event
async def on_ready():
    print(f'البوت يعمل الآن باسم {bot.user}')

# أمر لإظهار القائمة
@bot.command()
async def menu(ctx):
    view = MyView()
    await ctx.send("اختر أمراً من الأزرار:", view=view)

# تشغيل البوت باستخدام التوكن من Railway
token = os.getenv('TOKEN')
if token:
    bot.run(token)
else:
    print("خطأ: لم يتم العثور على التوكن في إعدادات البيئة.")
