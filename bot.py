import discord
import os
import random
import asyncio
from discord.ext import commands

# --- إعداد الصلاحيات والبادئة ---
intents = discord.Intents.default()
intents.message_content = True  # تفعيل قراءة الرسائل

# تعريف البوت مع إيقاف أمر المساعدة الافتراضي لتخصيصه
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ==========================================
# 🟢 حدث التشغيل (تمت إضافة حالة الاستماع)
# ==========================================
@bot.event
async def on_ready():
    print(f"====================================")
    print(f"🤖 تم تشغيل البوت بنجاح: {bot.user.name}")
    print(f"🆔 معرف البوت: {bot.user.id}")
    print(f"====================================")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!مساعدة"))

# ==========================================
# 📜 أمر المساعدة (Embed احترافي)
# ==========================================
@bot.command(name="مساعدة")
async def help_command(ctx):
    embed = discord.Embed(
        title="✨ قائمة أوامر بوت الألعاب والترفيه ✨",
        description="أهلاً بك! إليك الأوامر المتاحة:",
        color=discord.Color.blurple()
    )
    embed.add_field(name="🎮 !تخمين", value="لعبة تخمين الأرقام (1-10).", inline=False)
    embed.add_field(name="🪨 !مقص [حجر/ورقة/مقص]", value="لعبة حجر ورقة مقص ضد البوت.", inline=False)
    embed.add_field(name="🎯 !العاب", value="عرض قائمة الألعاب المتاحة.", inline=False)
    embed.add_field(name="👋 !ترحيب", value="استقبل رسالة ترحيبية.", inline=False)
    embed.set_footer(text=f"طلب بواسطة: {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

# ==========================================
# 👋 أمر الترحيب التفاعلي
# ==========================================
@bot.command(name="ترحيب")
async def welcome(ctx):
    responses = [
        f"يا هلا والله بـ {ctx.author.mention}! منور السيرفر يا وحش 🔥",
        f"أرحبببب يا {ctx.author.mention}! أنورت وأسفرت بوجودك دائمًا 👑",
        f"هلا بالشيخ {ctx.author.mention}، جيتك شرف لنا وللسيرفر كله ✨"
    ]
    await ctx.send(random.choice(responses))

# ==========================================
# 🎯 أمر عرض قائمة الألعاب
# ==========================================
@bot.command(name="العاب")
async def games_list(ctx):
    embed = discord.Embed(title="🎮 الألعاب المتاحة", color=discord.Color.green())
    embed.add_field(name="تخمين الرقم", value="`!تخمين`", inline=True)
    embed.add_field(name="حجر ورقة مقص", value="`!مقص`", inline=True)
    await ctx.send(embed=embed)

# ==========================================
# 🔢 لعبة تخمين الأرقام
# ==========================================
@bot.command(name="تخمين")
async def guess_game(ctx):
    secret_number = random.randint(1, 10)
    await ctx.send(f"🎲 {ctx.author.mention}، اخترت رقماً سرياً بين **1 و 10**. أمامك **3 محاولات**:")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()

    for i in range(3):
        try:
            msg = await bot.wait_for('message', check=check, timeout=30.0)
            guess = int(msg.content)
            if guess == secret_number:
                await ctx.send(f"🎉 كفوووو! الرقم السري كان **{secret_number}**.")
                return
            else:
                await ctx.send(f"❌ خطأ! متبقي لك {2-i} محاولات.")
        except asyncio.TimeoutError:
            await ctx.send(f"⏱️ انتهى الوقت! الرقم كان **{secret_number}**.")
            return
    await ctx.send(f"😢 خسرت! الرقم الصحيح كان **{secret_number}**.")

# ==========================================
# 🪨 لعبة حجر ورقة مقص
# ==========================================
@bot.command(name="مقص")
async def rps_game(ctx, choice: str = None):
    choices = ["حجر", "ورقة", "مقص"]
    if choice not in choices:
        await ctx.send("⚠️ اختر: `!مقص حجر` أو `!مقص ورقة` أو `!مقص مقص`.")
        return
    bot_choice = random.choice(choices)
    
    if choice == bot_choice:
        await ctx.send(f"👔 تعادل! اخترت {choice} وأنا {bot_choice}.")
    elif (choice == "حجر" and bot_choice == "مقص") or (choice == "ورقة" and bot_choice == "حجر") or (choice == "مقص" and bot_choice == "ورقة"):
        await ctx.send(f"🎉 فزت علي! (اختيارك: {choice} | اختياري: {bot_choice})")
    else:
        await ctx.send(f"🤖 فزت عليك! (اختيارك: {choice} | اختياري: {bot_choice})")

# ==========================================
# 🔑 تشغيل البوت (آمن)
# ==========================================
bot.run(os.getenv('TOKEN'))
