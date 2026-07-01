import os

from discord.ext import commands
import random
import asyncio

# إعداد الصلاحيات الأساسية للبوت (Intents)
intents = discord.Intents.default()
intents.message_content = True  # تفعيل قراءة محتوى الرسائل

# إنشاء كائن البوت مع بادئة الأوامر (!) وتغيير نص المساعدة الافتراضي
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ==========================================
# 🟢 حدث تشغيل البوت بنجاح
# ==========================================
@bot.event
async def on_ready():
    print(f"====================================")
    print(f"🤖 تم تشغيل البوت بنجاح يا مبرمج!")
    print(f"👑 اسم البوت: {bot.user.name}")
    print(f"🆔 معرف البوت: {bot.user.id}")
    print(f"====================================")
    
    # تعيين حالة البوت (يستمع إلى !مساعدة)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!مساعدة"))

# ==========================================
# 📜 أمر المساعدة العام
# ==========================================
@bot.command(name="مساعدة")
async def help_command(ctx):
    embed = discord.Embed(
        title="✨ قائمة أوامر بوت الألعاب والترفيه ✨",
        description="أهلاً بك! أنا بوت الألعاب السريع. إليك الأوامر المتاحة حالياً:",
        color=discord.Color.blurple()
    )
    embed.add_field(name="🎮 !تخمين", value="ابدأ لعبة تخمين الأرقام من 1 إلى 10.", inline=False)
    embed.add_field(name="🪨 !مقص", value="العب حجر، ورقة، مقص ضد البوت. (مثال: `!مقص حجر`)", inline=False)
    embed.add_field(name="🎯 !العاب", value="عرض الألعاب المتاحة حالياً في البوت.", inline=False)
    embed.add_field(name="👋 !ترحيب", value="يرحب بك البوت بطريقة رهيبة.", inline=False)
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
    embed = discord.Embed(
        title="🎮 الألعاب المتاحة حالياً 🎮",
        description="اختر أحد الأوامر التالية لبدء اللعب والتحدي:",
        color=discord.Color.green()
    )
    embed.add_field(name="1️⃣ لعبة تخمين الرقم", value="اكتب الأمر: `!تخمين`", inline=True)
    embed.add_field(name="2️⃣ لعبة حجر ورقة مقص", value="اكتب الأمر: `!مقص [حجر/ورقة/مقص]`", inline=True)
    embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/3408/3408506.png")
    await ctx.send(embed=embed)

# ==========================================
# 🔢 1- لعبة تخمين الأرقام
# ==========================================
@bot.command(name="تخمين")
async def guess_game(ctx):
    secret_number = random.randint(1, 10)
    await ctx.send(f"🎲 {ctx.author.mention}، لقد اخترت رقماً سرياً بين **1 و 10**. أمامك **3 محاولات** لتخمينه! اكتب تخمينك الآن:")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()

    attempts = 3
    for i in range(attempts):
        try:
            # انتظار رد المستخدم لمدة 30 ثانية
            msg = await bot.wait_for('message', check=check, timeout=30.0)
            guess = int(msg.content)

            if guess == secret_number:
                await ctx.send(f"🎉 كفوووو يا وحش! إجابتك صحيحة مبروك الفوز 🥳 الرقم السري هو **{secret_number}**.")
                return
            elif guess < secret_number:
                await ctx.send(f"❌ الرقم السري **أكبر** من {guess}! متبقي لك {attempts - (i + 1)} محاولات.")
            else:
                await ctx.send(f"❌ الرقم السري **أصغر** من {guess}! متبقي لك {attempts - (i + 1)} محاولات.")
        
        except asyncio.TimeoutError:
            await ctx.send(f"⏱️ انتهى الوقت! تأخرت في الرد، الرقم السري كان **{secret_number}**.")
            return

    await ctx.send(f"😢 للأسف خسرت جميع محاولاتك! الرقم السري الصحيح كان **{secret_number}**. حاول مرة أخرى!")

# ==========================================
# 🪨 2- لعبة حجر ورقة مقص
# ==========================================
@bot.command(name="مقص")
async def rps_game(ctx, choice: str = None):
    choices = ["حجر", "ورقة", "مقص"]
    
    if not choice or choice not in choices:
        await ctx.send("⚠️ يرجى تحديد اختيارك بشكل صحيح! مثال: `!مقص حجر` أو `!مقص ورقة` أو `!مقص مقص`.")
        return

    bot_choice = random.choice(choices)
    
    embed = discord.Embed(title="🪨 ورقة ✂️ مقص", color=discord.Color.orange())
    embed.add_field(name="اختيارك:", value=choice, inline=True)
    embed.add_field(name="اختيار البوت:", value=bot_choice, inline=True)

    if choice == bot_choice:
        embed.description = "👔 **النتيجة: تعادل!** لعبنا نفس الشيء."
    elif (choice == "حجر" and bot_choice == "مقص") or \
         (choice == "ورقة" and bot_choice == "حجر") or \
         (choice == "مقص" and bot_choice == "ورقة"):
        embed.description = f"🎉 **النتيجة: أنت الفائز!** كفوو هزمتني 😎"
    else:
        embed.description = "🤖 **النتيجة: البوت فاز عليك!** حظاً أوفر المرة القادمة 😜"

    await ctx.send(embed=embed)

# ==========================================
# 🔑 تشغيل البوت عبر التوكن
# ==========================================
# ⚠️ استبدل النص بالأسفل بتوكن بوتك الجديد والمستخرج من موقع المطورين
bot.run(os.getenv('TOKEN'))


bot.run(BOT_TOKEN)
