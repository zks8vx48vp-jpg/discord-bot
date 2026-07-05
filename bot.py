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
        self.topic = None
        self.categories = ["حيوانات", "ملابس", "أكلات", "سيارات", "فواكه", "أنمي", "كيبوب", "قيمرز"]

    def get_embed(self, title="🎮 لعبة برّا السالفة"):
        player_list = "\n".join([f"BBB@ • {p.name}" for p in self.players]) if self.players else "لا يوجد مشاركين"
        embed = discord.Embed(title=title, color=discord.Color.blurple())
        embed.add_field(name="المشاركون", value=player_list, inline=False)
        embed.set_footer(text="BBB @ System | نظام احترافي")
        return embed

session = SpyGame()

# 1. لوحة اختيار التصنيف وإنشاء الروم
class CategoryView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.select(placeholder="اختر التصنيف...", options=[discord.SelectOption(label=c, value=c) for c in session.categories])
    async def select_category(self, i: discord.Interaction, s: discord.ui.Select):
        session.topic = s.values[0]
        
        # إنشاء الروم الاحترافي
        guild = i.guild
        channel = await guild.create_text_channel(f"برّا-السالفة-{random.randint(1,99)}")
        
        # توزيع الأدوار
        spy = random.choice(session.players)
        for p in session.players:
            if p == spy:
                await p.send("🕵️‍♂️ **أنت برّا السالفة!**")
            else:
                await p.send(f"✅ **أنت داخل السالفة!** الموضوع: **{session.topic}**")
        
        await i.response.edit_message(content=f"✅ تم اختيار: **{session.topic}**\n🔥 تم إنشاء روم خاص: {channel.mention}", embed=None, view=None)

# 2. اللوحة الرئيسية (انضمام/إلغاء/تأكيد)
class MainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="انضم للعبة", style=discord.ButtonStyle.green)
    async def join(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user not in session.players:
            session.players.append(i.user)
            await i.response.edit_message(embed=session.get_embed())
    
    @discord.ui.button(label="إلغاء", style=discord.ButtonStyle.red)
    async def leave(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user in session.players:
            session.players.remove(i.user)
            await i.response.edit_message(embed=session.get_embed())

    @discord.ui.button(label="تأكيد", style=discord.ButtonStyle.primary)
    async def confirm(self, i: discord.Interaction, b: discord.ui.Button):
        if len(session.players) < 3:
            await i.response.send_message("❌ العدد قليل! نحتاج 3 لاعبين على الأقل.", ephemeral=True)
        else:
            await i.response.edit_message(content="🎯 **اختر تصنيف اللعبة الآن:**", embed=None, view=CategoryView())

@bot.command()
async def لعبه(ctx):
    session.players = [] # تصفير القائمة لبدء لعبة جديدة
    await ctx.send(embed=session.get_embed(), view=MainView())

bot.run(os.environ.get('TOKEN'))
