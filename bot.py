# =========================================
# تحديث اللوبي الاحترافي
# =========================================

async def update_lobby(gid):

    game = games[gid]

    total = total_roles(gid)

    players_text = ""

    if not game["players"]:

        players_text = "لا يوجد مشاركين"

    else:

        for p in game["players"]:
            players_text += f"• {p.mention}\n"

    embed = discord.Embed(
        title=f"🎮 لعبة المستذئبين {len(game['players'])}/{total}",
        description=(
            "تبدأ اللعبة عندما يكتمل العدد.\n"
        ),
        color=discord.Color.dark_red()
    )

    embed.add_field(
        name="👥 المشاركون",
        value=players_text,
        inline=False
    )

    embed.add_field(
        name="☠️ قاتل",
        value=str(game["roles_count"]["قاتل"]),
        inline=True
    )

    embed.add_field(
        name="💊 طبيب",
        value=str(game["roles_count"]["طبيب"]),
        inline=True
    )

    embed.add_field(
        name="👤 مدني",
        value=str(game["roles_count"]["مدني"]),
        inline=True
    )

    await game["message"].edit(
        embed=embed,
        content=None,
        view=LobbyView()
    )


# =========================================
# الليل الاحترافي
# =========================================

night_embed = discord.Embed(
    title="🌙 بدأ الليل",
    description=(
        "القاتل يختار ضحيته...\n"
        "الطبيب يختار شخصًا لحمايته..."
    ),
    color=discord.Color.dark_blue()
)

await channel.send(embed=night_embed)

game["night_kill"] = None
game["night_save"] = None

# =========================================
# إرسال اختيارات القاتل
# =========================================

for killer in killers:

    try:

        killer_embed = discord.Embed(
            title="☠️ دور القاتل",
            description="اختر شخصًا لقتله",
            color=discord.Color.red()
        )

        await killer.send(
            embed=killer_embed,
            view=KillView(gid, killer)
        )

    except:
        pass

# =========================================
# إرسال اختيارات الطبيب
# =========================================

doctors = [
    p for p in alive
    if game["roles"][p.id] == "طبيب"
]

for doctor in doctors:

    try:

        doctor_embed = discord.Embed(
            title="💊 دور الطبيب",
            description="اختر شخصًا لحمايته",
            color=discord.Color.green()
        )

        await doctor.send(
            embed=doctor_embed,
            view=SaveView(gid)
        )

    except:
        pass

# انتظار الليل
await asyncio.sleep(30)

killed = game["night_kill"]
saved = game["night_save"]

# =========================================
# نتيجة الليل
# =========================================

if killed and killed != saved:

    if killed in game["alive"]:

        game["alive"].remove(killed)

        dead_embed = discord.Embed(
            title="☠️ مات لاعب",
            description=f"{killed.mention}",
            color=discord.Color.dark_red()
        )

        await channel.send(embed=dead_embed)

else:

    save_embed = discord.Embed(
        title="💊 نجاة",
        description="الطبيب أنقذ شخصًا الليلة",
        color=discord.Color.green()
    )

    await channel.send(embed=save_embed)

# =========================================
# النهار
# =========================================

day_embed = discord.Embed(
    title="☀️ بدأ النهار",
    description=(
        "ناقشوا الآن من القاتل\n"
        "ثم صوتوا لطرده"
    ),
    color=discord.Color.gold()
)

await channel.send(embed=day_embed)

await asyncio.sleep(10)

# =========================================
# التصويت الاحترافي
# =========================================

game["votes"] = {}

vote_embed = discord.Embed(
    title="🗳️ التصويت بدأ",
    description=(
        "اختر اللاعب الذي تريد طرده\n\n"
        "⏳ مدة التصويت: 20 ثانية"
    ),
    color=discord.Color.red()
)

vote_message = await channel.send(
    embed=vote_embed,
    view=VoteView(gid)
)

# انتظار التصويت
await asyncio.sleep(20)

# حذف الأزرار
await vote_message.edit(view=None)

# =========================================
# حساب الأصوات
# =========================================

vote_count = {}

for voted_id in game["votes"].values():

    if voted_id not in vote_count:
        vote_count[voted_id] = 0

    vote_count[voted_id] += 1

# =========================================
# لا يوجد تصويت
# =========================================

if not vote_count:

    no_vote_embed = discord.Embed(
        title="❌ انتهى التصويت",
        description="لم يصوت أحد",
        color=discord.Color.dark_red()
    )

    await channel.send(embed=no_vote_embed)

# =========================================
# تعادل أو طرد
# =========================================

else:

    highest_vote = max(vote_count.values())

    highest_players = []

    for player_id, amount in vote_count.items():

        if amount == highest_vote:
            highest_players.append(player_id)

    # =====================================
    # تعادل
    # =====================================

    if len(highest_players) > 1:

        tie_embed = discord.Embed(
            title="⚖️ تعادل",
            description="لم يتم طرد أحد",
            color=discord.Color.orange()
        )

        await channel.send(embed=tie_embed)

    # =====================================
    # طرد
    # =====================================

    else:

        voted_player = None

        for p in game["alive"]:

            if p.id == highest_players[0]:
                voted_player = p

        if voted_player:

            game["alive"].remove(voted_player)

            role = game["roles"][voted_player.id]

            result_embed = discord.Embed(
                title="📢 تم طرد لاعب",
                description=(
                    f"{voted_player.mention}\n\n"
                    f"🎭 دوره كان: **{role}**"
                ),
                color=discord.Color.dark_red()
            )

            await channel.send(embed=result_embed)
