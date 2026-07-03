import discord
from discord.ext import commands
import random
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

class GamesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔢 تخمين الرقم", style=discord.ButtonStyle.primary)
    async def guess(self, i: discord.Interaction, b: discord.ui.Button):
        num = random.randint(1, 50)
        await i.response.send_message(f"🎯 **تحدي الذكاء:** الرقم السري الذي اخترته هو: **{num}**.. هل كنت تتوقعه يا بطل؟", ephemeral=True)

    @discord.ui.button(label="🧠 تحدي الألغاز", style=discord.ButtonStyle.secondary)
    async def brain(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.send_message("🧩 **لغز اليوم:** أنا لي أسنان كثيرة ولكني لا أعض، فمن أنا؟ (فكر جيداً قبل أن تسألني!)", ephemeral=True)

    @discord.ui.button(label="✨ حظك اليوم", style=discord.ButtonStyle.success)
    async def luck(self, i: discord.Interaction, b: discord.ui.Button):
        fortunes = ["اليوم تبتسم لك الدنيا! 🌟", "فرصة ذهبية في طريقها إليك.. استعد! 🚀", "يوم مليء بالإنجازات والنجاح! 🏆"]
        await i.response.send_message(f"🔮 **نصيبك من الحظ:** {random.choice(fortunes)}", ephemeral=True)

    @discord.ui.button(label="🏎️ سباق السرعة", style=discord.ButtonStyle.danger)
    async def race(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.send_message("🔥 **سباق السرعة:** انطلقت السيارات! القوة والسرعة هي عنوانك اليوم.. أنت الفائز بجدارة! 🏆", ephemeral=True)

@bot.command()
async def games(ctx):
    embed = discord.Embed(
        title="🎮 مركز الألعاب التفاعلي",
        description="أهلاً بك في عالم التحدي! اختر لعبتك المفضلة من الأزرار بالأسفل، واصنع يومك بلمسة واحدة. 🔥",
        color=discord.Color.gold()
    )
    embed.set_footer(text="صُمم بكل حب لتجربة احترافية ✨")
    await ctx.send(embed=embed, view=GamesView())

@bot.event
async def on_ready():
    print(f'✅ البوت في حالة تأهب قصوى ويعمل بنجاح: {bot.user}')

bot.run(os.environ.get('TOKEN'))
