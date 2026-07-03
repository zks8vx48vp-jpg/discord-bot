import discord
from discord.ext import commands
import os

# إعدادات الصلاحيات
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

class WerewolfView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.players = []
        self.killers = 1
        self.doctors = 1
        self.civilians = 3

    def get_embed(self):
        embed = discord.Embed(title="لعبة المستذئبين", color=discord.Color.dark_purple())
        players_list = "\n".join([f"• {p.mention}" for p in self.players]) if self.players else "لا يوجد مشاركون"
        embed.add_field(name="المشاركون", value=players_list, inline=False)
        embed.add_field(name="الأدوار", value=f"💀 قاتل: {self.killers}\n💊 طبيب: {self.doctors}\n👤 مدني: {self.civilians}", inline=False)
        return embed

    @discord.ui.button(label="انضم للعبة", style=discord.ButtonStyle.green)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user not in self.players:
            self.players.append(interaction.user)
            await interaction.response.edit_message(embed=self.get_embed())
        else:
            await interaction.response.send_message("أنت مشترك بالفعل!", ephemeral=True)

    @discord.ui.button(label="غادر اللعبة", style=discord.ButtonStyle.red)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.players:
            self.players.remove(interaction.user)
            await interaction.response.edit_message(embed=self.get_embed())

    @discord.ui.button(label="إضافة دور +", style=discord.ButtonStyle.secondary)
    async def add_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.civilians += 1
        await interaction.response.edit_message(embed=self.get_embed())

    @discord.ui.button(label="إزالة دور -", style=discord.ButtonStyle.secondary)
    async def remove_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.civilians > 0:
            self.civilians -= 1
        await interaction.response.edit_message(embed=self.get_embed())

    @discord.ui.button(label="تأكيد اللعبة", style=discord.ButtonStyle.primary)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"✅ تم تأكيد الإعدادات! اللعبة ستبدأ بـ {len(self.players)} لاعبين.", ephemeral=False)
        self.stop() 

@bot.command()
async def لعبة(ctx):
    view = WerewolfView()
    await ctx.send(embed=view.get_embed(), view=view)

# جلب التوكن من إعدادات Railway
bot.run(os.environ['TOKEN'])
