# =========================================
# أمر اللعبة
# =========================================

@bot.command(name="العبة")
async def game(ctx):

    gid = ctx.guild.id

    games[gid] = {

        "players": [],
        "alive": [],
        "roles": {},

        "roles_count": {
            "قاتل": 1,
            "طبيب": 1,
            "مدني": 3
        },

        "night_kill": None,
        "night_save": None,

        "message": None
    }

    total = total_roles(gid)

    text = f"""
# لعبة المستذئب

الأدوار: {total}/24

☠️ قاتل: 1
💊 طبيب: 1
👤 مدني: 3
"""

    msg = await ctx.send(
        content=text,
        view=SetupView()
    )

    games[gid]["message"] = msg
