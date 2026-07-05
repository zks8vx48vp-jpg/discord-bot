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
        self.topic = "لم يتم الاختيار"
        self.spy_count = 1
        self.categories = {
            "حيوانات": ["نمر", "أسد", "فهد", "ذئب", "زرافة", "فيل", "قرد"],
            "قيمرز": ["سوني", "إكس بوكس", "بي سي", "نينتندو", "فورت نايت"],
            "أكلات": ["كبسة", "برجر", "بيتزا", "شاورما", "سوشي"]
        }

    def get_embed(self):
        player_list = "\n".join([f"BBB@ • {p.name}" for p in self.players]) if self.players else "لا يوجد مشاركين"
        embed = discord.Embed(title="🎮 لعبة برّا السالفة", color=discord.Color.dark_theme())
        embed.add_field(name="المشاركون", value=player_list, inline=False)
        embed.add_field(name="الأدوار", value=f"🕵️‍♂️ برّا السالفة: {self.spy_count}\n👤 جوا السالفة: {len(self.players) - self.spy_count if len(self.players) > 0 else 0}", inline=False)
        embed.set_footer(text="BBB @ System")
        return embed

session = SpyGame()

class MainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # الصف الأول: تأكيد وحذف
    @discord.ui.button(label="تأكيد", style=discord.ButtonStyle.green, row=0)
    async def confirm(self, i: discord.Interaction, b: discord.ui.Button):
        if len(session.players) < 3:
            return await i.response.send_message("❌ اقل شيء 3 لاعبين!", ephemeral=True)
        # هنا تظهر قائمة اختيار التصنيفات بعد التأكيد
        await i.response.edit_message(content="🎯 اختر التصنيف:", view=CategoryView())

    @discord.ui.button(label="حذف", style=discord.ButtonStyle.danger, row=0)
    async def delete(self, i: discord.Interaction, b: discord.ui.Button):
        session.players = []
        await i.response.edit_message(embed=session.get_embed())

    # الصف الثاني: إضافة وإزالة
    @discord.ui.button(label="إضافة +", style=discord.ButtonStyle.secondary, row=1)
    async def add(self, i: discord.Interaction, b: discord.ui.Button):
        session.spy_count += 1
        await i.response.edit_message(embed=session.get_embed())

    @discord.ui.button(label="إزالة -", style=discord.ButtonStyle.secondary, row=1)
    async def sub(self, i: discord.Interaction, b: discord.ui.Button):
        if session.spy_count > 1: session.spy_count -= 1
        await i.response.edit_message(embed=session.get_embed())
    
    @discord.ui.button(label="انضم للعبة", style=discord.ButtonStyle.primary, row=2)
    async def join(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user not in session.players:
            session.players.append(i.user)
            await i.response.edit_message(embed=session.get_embed())

class CategoryView(discord.ui.View):
    def __init__(self):
        super().__init__()
        for cat in session.categories.keys():
            self.add_item(discord.ui.Button(label=cat, custom_id=cat))

    async def interaction_check(self, i: discord.Interaction) -> bool:
        cat = i.data['custom_id']
        word = random.choice(session.categories[cat])
        
        # إنشاء الروم
        channel = await i.guild.create_text_channel("برّا-السالفة")
        
        # توزيع الأدوار
        spies = random.sample(session.players, session.spy_count)
        for p in session.players:
            if p in spies:
                await p.send("🕵️‍♂️ **أنت برّا السالفة!**")
            else:
                await p.send(f"✅ **أنت جوا السالفة!** التصنيف: {cat}، الكلمة: **{word}**")
        
        await i.response.edit_message(content=f"🔥 بدأت اللعبة في {channel.mention}", embed=None, view=None)
        return True

@bot.command()
async def لعبه(ctx):
    session.players = []
    await ctx.send(embed=session.get_embed(), view=MainView())

bot.run(os.environ.get('TOKEN'))
