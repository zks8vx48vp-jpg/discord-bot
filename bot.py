import discord
from discord.ext import commands
import random
import os

# إعدادات الصلاحيات (مهم جداً لتفعيل الأزرار والرسائل)
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

class SpyGameSession:
    def __init__(self):
        self.players = []
        self.topic = "لم يتم الاختيار"
        self.active = False
        self.spy = None
        self.categories = ["حيوانات", "ملابس", "أكلات", "سيارات", "فواكه", "شخصيات كرتون", "مشروبات", "حلويات", "مسلسلات", "أنمي", "كيبوب", "قيمرز"]

    def get_embed(self):
        # التنسيق الذي طلبته للأسماء
        player_list = "\n".join([f"BBB@ • {p.name}" for p in self.players]) if self.players else "لا يوجد مشاركين"
        embed = discord.Embed(title="🎮 لعبة برّا السالفة", color=discord.Color.dark_theme())
        embed.add_field(name="المشاركون", value=player_list, inline=False)
        embed.add_field(name="الإعدادات", value=f"التصنيف: **{self.topic}**\nالحالة: {'بدأت' if self.active else 'بانتظار التأكيد'}", inline=False)
        embed.set_footer(text="BBB @ System | 5/15/26")
        return embed

session = SpyGameSession()

# نظام القائمة المنسدلة للتصنيفات
class CategorySelect(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label=c, value=c) for c in session.categories]
        super().__init__(placeholder="اختر تصنيف السالفة...", options=options)
    
    async def callback(self, i: discord.Interaction):
        session.topic = self.values[0]
        await i.response.edit_message(embed=session.get_embed())

class MainGameView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CategorySelect())

    @discord.ui.button(label="انضم للعبة", style=discord.ButtonStyle.green)
    async def join(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user not in session.players:
            session.players.append(i.user)
            await i.response.edit_message(embed=session.get_embed())
        else:
            await i.response.send_message("❌ أنت مشارك بالفعل!", ephemeral=True)

    @discord.ui.button(label="تأكيد وبدء", style=discord.ButtonStyle.primary)
    async def start(self, i: discord.Interaction, b: discord.ui.Button):
        if len(session.players) < 3:
            return await i.response.send_message("❌ العدد المطلوب 3 لاعبين على الأقل!", ephemeral=True)
        
        session.active = True
        session.spy = random.choice(session.players)
        
        # إنشاء روم اللعبة
        channel = await i.guild.create_text_channel("برّا-السالفة")
        
        # إرسال الأدوار بالخاص
        for p in session.players:
            if p == session.spy:
                await p.send("🕵️‍♂️ **أنت برّا السالفة!** حاول التمويه واكتشاف الموضوع.")
            else:
                await p.send(f"✅ **أنت داخل السالفة!** الموضوع هو: **{session.topic}**")
        
        await i.response.send_message(f"🔥 **بدأت اللعبة!** تم إنشاء الروم: {channel.mention}")

    @discord.ui.button(label="إزالة", style=discord.ButtonStyle.danger)
    async def delete(self, i: discord.Interaction, b: discord.ui.Button):
        session.players = []
        session.active = False
        await i.response.edit_message(embed=session.get_embed())

@bot.event
async def on_ready():
    print(f'✅ نظام {bot.user} يعمل بكامل قوته!')

@bot.command()
async def لعبه(ctx):
    await ctx.send(embed=session.get_embed(), view=MainGameView())

# تشغيل البوت عبر توكن مخفي في الموقع
bot.run(os.environ.get('TOKEN'))
