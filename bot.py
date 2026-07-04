import discord
from discord.ext import commands
import random
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# واجهة الأزرار
class CollectiveGamesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🕵️‍♂️ الجاسوس", style=discord.ButtonStyle.danger)
    async def spy_game(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.send_message("🕵️‍♂️ **تم تفعيل وضع الجاسوس!** الكل يرسل كلمته السرية في الخاص.. الحذر مطلوب! 🔍", ephemeral=False)

    @discord.ui.button(label="⚡ تحدي السرعة", style=discord.ButtonStyle.primary)
    async def speed_game(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.send_message("🚀 **تحدي السرعة:** أول واحد يكتب 'تم' في الشات هو الفائز بلقب الأسرع! 🔥", ephemeral=False)

# الحدث الرئيسي للردود والألعاب
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    msg = message.content.lower()

    # 1. الردود التلقائية
    if "سلام" in msg or "هلا" in msg:
        await message.reply(f"أهلاً يا بطل {message.author.mention}! نورت السيرفر. ✨")

    # 2. تشغيل قائمة الألعاب
    elif "ألعاب" in msg or "تحدي" in msg:
        embed = discord.Embed(
            title="🎮 مركز التحديات الجماعية",
            description="الساحة جاهزة يا أبطال! اختاروا التحدي من الأزرار بالأسفل:",
            color=discord.Color.gold()
        )
        await message.channel.send(embed=embed, view=CollectiveGamesView())

    # هذا السطر مهم جداً لكي تعمل الأوامر (مثل !games) إذا احتجتها
    await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f'✅ البوت يعمل الآن وبكل كفاءة: {bot.user}')

bot.run(os.environ.get('TOKEN'))
