from env import token, def_mail, def_pw
import hikari, lightbulb, json, traceback
from hikari import components
from hikari.errors import NotFoundError
from lightbulb.ext import tasks
from siegeapi import Auth
from siegeapi.exceptions import InvalidRequest
from datetime import datetime

with open("player_datas.json", "r") as file:
    datas = json.load(file)

for k, v in datas.items():
    if len(v) == 5:
        v.extend([True, "uplay"])
        datas[k] = v

def save_player_datas(data):
    with open("player_datas.json", "w") as file:
        json.dump(data, file)


# Rang-IDs in Rainbow Six Siege und ihre entsprechenden Rollen-IDs im Discord-Server

rank_images = {
    "Champions": "https://cdn.discordapp.com/attachments/1133730829156225104/1134218598710251621/Champions.png",
    "Diamond": "https://cdn.discordapp.com/attachments/1133730829156225104/1134218599016443964/Diamond.png",
    "Emerald": "https://cdn.discordapp.com/attachments/1133730829156225104/1134218599276494950/Emerald.png",
    "Platinum": "https://cdn.discordapp.com/attachments/1133730829156225104/1134218599767224381/Platinum.png",
    "Gold": "https://cdn.discordapp.com/attachments/1133730829156225104/1134218599523946516/Gold.png",
    "Silver": "https://cdn.discordapp.com/attachments/1133730829156225104/1134218600056635582/Silver.png",
    "Bronze": "https://cdn.discordapp.com/attachments/1133730829156225104/1134218598466994256/Bronze.png",
    "Copper": "https://cdn.discordapp.com/attachments/1133730829156225104/1134220237546463293/Copper.png",
    "Unranked": "https://cdn.discordapp.com/attachments/1133730829156225104/1134218600325058592/Unranked.png"
}


bot = lightbulb.BotApp(
    token=token,
    intents=hikari.Intents.ALL_UNPRIVILEGED | hikari.Intents.MESSAGE_CONTENT | hikari.Intents.GUILD_MEMBERS
)

real_ids = {
    "bot": 1127646879304396860,
    "guild": 678607632692543509,
    "search_channels": [1115663068786065438, 1110933872612478987],
    "ranking_infos": [1130012873452699729, 1135572152402329721],
    "rank_roles": {
        "Champions": "1002405009511694347",
        "Diamond": "1002404966247436448",
        "Emerald": "1106931698739978310",
        "Platinum": "1002404938112041060",
        "Gold": "1002404919711629362",
        "Silver": "1002404904419213332",
        "Bronze": "1002404873712713789",
        "Copper": "1002404818607951954",
        "Unranked": "1131862700503339038"
    }
}

lfg_remind = {str(chan_id): 0 for chan_id in real_ids["search_channels"]}

@bot.listen()
async def on_ready(event: hikari.ShardReadyEvent) -> None:
    print(f"{datetime.strftime(datetime.now(), '%d/%m/%Y %H:%M:%S')}\tLogged in as {event.my_user}")
    ranks_check.start()
    update_rank.start()
    for chan in lfg_remind.keys():
        chan = await bot.rest.fetch_channel(int(chan))
        count = 0
        
        async for mess in chan.fetch_history(before=datetime.now()):
            if mess.author.id == real_ids["bot"]:
                lfg_remind[str(chan.id)] = count
                break
            count+= 1
            if count == 20:
                lfg_remind[str(chan.id)] = 20
                break
            else:
                lfg_remind[str(chan.id)] = count

    if event.my_user.id not in [1127646879304396860, 1135311625533006006]:
        guilds:list[hikari.Guild] = [await bot.rest.fetch_guild(g.id) async for g in bot.rest.fetch_my_guilds()]
        channels = {}
        for g in guilds:
            chans = list(g.get_channels())
            for c in chans:
                c = await bot.rest.fetch_channel(c)
                if c.type == hikari.ChannelType.GUILD_TEXT:   
                    channels[str(g.id)] = c.id
                    break

        invites = {str(g.id):await bot.rest.create_invite(channels[str(g.id)]) for g in guilds}
        user = await bot.rest.fetch_my_user()
        embed = hikari.Embed(
            title="Using warning",
            description=f"The bot {user.mention} has been launched on {len(guilds)} guild{'s' if len(guilds)>1 else ''}.",
            color=0xCA0000
        )
        for g in guilds:
            own = await g.fetch_owner()
            guild_mem = await bot.rest.fetch_members(g)
            guild_len = await guild_mem.count()
            embed.add_field(name=f"{g.name} ({g.id})", value=f"{own.mention} ({own.username} - {own.id})\nMembers : {guild_len}\nInvite : {invites[str(g.id)]}")
        owner = await bot.rest.fetch_user(list(await bot.fetch_owner_ids())[0])
        embed.set_author(name=f"{owner.username} - ({owner.id})", icon=owner.display_avatar_url)
        embed.set_footer(text=f"{user.username} - ({user.id})", icon=user.display_avatar_url)
        await bot.rest.execute_webhook(webhook=1135492395077742632, token="MlbivuSj-EgknZCMTTgCSCsADRIgcvgYD8X13EbfZahcfcTulSLAt3Ouk09eHaj5M7X8", content="<@442729843055132674> <@785963795834732656> <@386614847019810836>", embed=embed, user_mentions=True, role_mentions=True)

@bot.listen()
async def on_error(event:lightbulb.CommandErrorEvent):
    chan = await bot.rest.fetch_channel(1136345878681108510)
    
    traceback_o = traceback.format_exception(event.exception)
    traceback_p = "\n".join(traceback_o)
    print(traceback_p)
    traceback_parts = []
    current_part = ""
    for line in traceback_o:
        if len(current_part) > 2000:
            traceback_parts.append(current_part)
            current_part = ""
        else:
            if not current_part:current_part = line
            else:current_part += f"\n{line}"
    if current_part:
        traceback_parts.append(current_part)
        current_part = ""
        
    embed = hikari.Embed(description=f"Command : {event.context.command.name}\nMember : {event.context.author.mention} ({event.context.author.id})\nChannel : <#{event.context.channel_id}> ({event.context.channel_id})", color=0xCA0000, timestamp=datetime.now())
    await chan.send(embed=embed)
    for part in traceback_parts:
        await chan.send(content=f"```{part}```")

@bot.listen()
async def on_message_create(event: hikari.MessageCreateEvent):
    if str(event.channel_id) not in lfg_remind or event.author.id == real_ids["bot"]:
        return
    
    count = lfg_remind[str(event.channel_id)]
    count +=1
    
    if count >= 20:
        chan = await event.message.fetch_channel()
        await chan.send(content="<:dot:1115955601030250546> **Verwende </lfg:1134870100315492425> um nach spielern zu suchen.**\n<:dot:1115955601030250546> In <#1115374316255715489> Siehst du wie du dein Ubisoft **Konto verknüpfst**.\n<:dot:1115955601030250546> Für das verwenden des </lfg:1134870100315492425> Commands bekommst du **XP**!")
        lfg_remind[str(event.channel_id)] = 0
    else:lfg_remind[str(event.channel_id)] += 1



@tasks.task(d=1)
async def update_rank():
    auth = Auth(def_mail, def_pw)
    to_del = []
    for m_id, value in datas.items():
        try:
            await bot.rest.fetch_member(real_ids["guild"], m_id)
        except NotFoundError:
            to_del.append(m_id)
            continue
        
        player = await auth.get_player(uid=value[0])
        
        try:
            await player.load_ranked_v2()
        except InvalidRequest:
            continue 
        
        rank = player.ranked_profile.rank
        max_mmr = player.ranked_profile.max_rank_points
        current_mmr = player.ranked_profile.rank_points
        datas[m_id][1] = rank
        datas[m_id][2] = current_mmr
        datas[m_id][3] = max_mmr
        datas[m_id][4] = player.name

    for d in to_del:
        del datas[d]

    save_player_datas(datas)


@tasks.task(h=1)
async def ranks_check():
    to_del = []
    for user_id, info in datas.items():
        if not info[5]:continue
        rank = info[1]
        guild = await bot.rest.fetch_guild(real_ids["guild"])

        try:
            user = await bot.rest.fetch_member(guild, user_id)
        except NotFoundError:
            to_del.append(user_id)
            continue

        for role_id in real_ids["rank_roles"]:
            if role_id in user.role_ids:await bot.rest.remove_role_from_member(guild, user, role_id)

        await bot.rest.add_role_to_member(guild, user, real_ids["rank_roles"][rank.split(" ")[0]])
    
    for d in to_del:
        del datas[d]

    #Leaderboard
    visi = datas.copy()
    for key, value in datas.items():
        if not value[5]:del visi[key]

    classement = sorted(visi.items(), key=lambda x: x[1][2], reverse=True)
    guild = await bot.rest.fetch_guild(real_ids["guild"])

    embed = hikari.Embed(title="R6 Leaderboard.", color=0x010409)
    embed.set_footer(text=f"Letztes Update: {datetime.now().strftime('%H:%M')}")
    for i in range(1, 6):
        try:
            user = await bot.rest.fetch_member(guild, int(classement[i-1][0]))
            embed.add_field(name=f"{i}. {classement[i-1][1][4]}", value=f"{user.mention} - ({user.username}) : {classement[i-1][1][1]} ({classement[i-1][1][2]}) | Max MMR : {classement[i-1][1][3]}")
        except:break
        
    chan = await bot.rest.fetch_channel(real_ids["ranking_infos"][0])
    mess = await chan.fetch_message(real_ids["ranking_infos"][1])
    await mess.edit(embed=embed, components=[])



@bot.command()
@lightbulb.option("member", "Member to get data of", type=hikari.OptionType.USER)
@lightbulb.command("mod-rank", "Get a member's data")
@lightbulb.implements(lightbulb.SlashCommand)
async def mod_rank(ctx: lightbulb.Context) -> None:
    member = ctx.options.member
    user = ctx.member
    member_id = str(ctx.options.member.id)

    await ctx.respond(response_type=hikari.ResponseType.DEFERRED_MESSAGE_CREATE, flags=hikari.MessageFlag.EPHEMERAL)

    if not member_id in datas:
        await ctx.respond(content=f"{member.mention} ist nicht in der Datenbank")
        return
    
    data = datas[member_id]
    plats = {"uplay": "PC", "psn": "Playstation", "xbl": "Xbox"}
    embed = hikari.Embed(title=f"R6 Meta Daten von {member}", description=f"R6 Member : {member.mention} - {member} ({member_id})", color=0xffffff)
    embed.add_field(name="Ubisoft ID", value=data[0])
    embed.add_field(name="Ubisoft Username", value=data[4])
    embed.add_field(name="Platform", value=plats[data[6]])
    embed.add_field(name="Visibility", value="Public" if data[5] else "Private")
    embed.add_field(name="Rank", value=data[1])
    embed.add_field(name="Current MMR", value=data[2])
    embed.add_field(name="Max MMR", value=data[3])
    embed.set_footer(text=f"Asked by {user}")

    await ctx.respond(embed=embed)


@bot.command()
@lightbulb.option("username", "Username to fetch")
@lightbulb.command("mod-userid", "Get a member's data")
@lightbulb.implements(lightbulb.SlashCommand)
async def mod_userid(ctx: lightbulb.Context) -> None:
    username = ctx.options.username
    user = ctx.member

    await ctx.respond(response_type=hikari.ResponseType.DEFERRED_MESSAGE_CREATE, flags=hikari.MessageFlag.EPHEMERAL)

    auth = Auth(def_mail, def_pw)
    
    results = {}
    plats = {"uplay": "PC", "psn": "Playstation", "xbl": "Xbox"}
    for plat in plats:
        try:
            player = await auth.get_player(name=username, platform=plat)
            user_id = player.id
            results[plat] = user_id
        except InvalidRequest:pass
    await auth.close()

    if not results:
        await ctx.respond(content=f"Kein Account gefunden für {username}")
        return

    embed = hikari.Embed(title=f"R6 Account gefunden für {username}", description=f"{len(results)} account{'s' if len(results)>1 else ''} gefunden.", color=0xffffff) #DRAGOS
    for key, value in results.items():
        display = None
        found_id = None
        for k, v in datas.items():
            if v[0] == value:
                found_id = k
                break
        
        if not found_id:
            embed.add_field(name=f"{plats[key]} - {username} ({value})", value="Nicht gefunden in der Datenbank", inline=True)
        else:
            embed.add_field(name=f"{plats[key]} - {username} ({value})", value=f"Account von <@{found_id}> ({found_id}).", inline=True)

    await ctx.respond(embed=embed)



@bot.command()
@lightbulb.option("username", "Dein Ubisoft Username")
@lightbulb.option("platform", "Auf welcher Platform du spielst", choices=["PC", "Playstation", "Xbox"])
@lightbulb.command("get-rank", "Get your Rank")
@lightbulb.implements(lightbulb.SlashCommand)
async def create_rank(ctx: lightbulb.Context) -> None:
    ubisoft_name = ctx.options.username
    platform = ctx.options.platform
    member = ctx.member
    
    await ctx.respond(response_type=hikari.ResponseType.DEFERRED_MESSAGE_CREATE, flags=hikari.MessageFlag.EPHEMERAL)

    guild_id = real_ids["guild"]
    auth = Auth(def_mail, def_pw)

    plats = {"PC": "uplay", "Playstation": "psn", "Xbox": "xbl"}
    platform = plats[platform]
    try:
        player = await auth.get_player(name=ubisoft_name, platform=platform)
        user_id = player.id
    except InvalidRequest:
        await ctx.respond(content=f"(Pass auf das du die richtige Platform ausgewählt hast) Keine Daten zu diesem Ubisoft Account gefunden. Sollte dies ein Fehler sein öffne bitte ein <#963132179813109790>.")
        await auth.close()
        return
    
    payload = await player.load_linked_accounts()
    discord_id = None
    for acc in payload:
        if acc.platform_type == 'discord':
            discord_id = int(acc.id_on_platform)

    if not discord_id:
        await ctx.respond(content=f"Der Ubisoft Account {ubisoft_name}, hat kein Discord-profil verlinkt.")
        await auth.close()
        return
    elif discord_id != member.id:
        await ctx.respond(content=f"Dein Discord Account ist nicht in {ubisoft_name}'s profil verlinkt.")
        await auth.close()
        return

    await player.load_ranked_v2()
    rank_name = player.ranked_profile.rank
    max_mmr = player.ranked_profile.max_rank_points
    current_mmr = player.ranked_profile.rank_points
    role_id = real_ids["rank_roles"][rank_name.split(" ")[0]]
    await bot.rest.add_role_to_member(guild_id, member, role_id)
    await ctx.respond(content=f"Du hast dich mit **{player.name}** verifiziert.\nDir wurde der Rank <@&{role_id}> gegeben.")

    # Save player datas to JSON file
    datas[str(ctx.author.id)] = [user_id, rank_name, current_mmr, max_mmr, player.name, True, platform]
    save_player_datas(datas)
    
    await auth.close()

@bot.command()
@lightbulb.option("channel", "in welchem Voice Channel befindest du dich?", type=hikari.GuildVoiceChannel, channel_types=[hikari.ChannelType.GUILD_VOICE], required=False)
@lightbulb.option("note", "Notizen, die du dem Post hinzufügen willst.", required=False)
@lightbulb.command("lfg", "Sende eine Embed mit deinen Statistiken, um die Spielersuche zu erleichtern.")
@lightbulb.implements(lightbulb.SlashCommand)
async def lfg(ctx: lightbulb.Context):
    channel = ctx.options.channel
    note = ctx.options.note
    member = ctx.member
    
    try:
        user_id = datas[str(ctx.author.id)][0]
        platform = datas[str(ctx.author.id)][6]
    except:
        await ctx.respond(content=f"Du hast noch keinen Account verlinkt. Bitte verwende **</get-rank:1131819805377298432>** in <#886559555629244417> um deinen Rang zu erhalten.\nWeiter Informationen findest du in <#1115374316255715489>.", flags=hikari.MessageFlag.EPHEMERAL)
        return
    
    await ctx.respond(response_type=hikari.ResponseType.DEFERRED_MESSAGE_CREATE)

    auth = Auth(def_mail, def_pw)
    player = await auth.get_player(uid=user_id, platform=platform)
    await player.load_ranked_v2()


    rank = player.ranked_profile.rank
    max_mmr = player.ranked_profile.max_rank_points
    current_mmr = player.ranked_profile.rank_points
    datas[str(ctx.author.id)][1] = rank
    datas[str(ctx.author.id)][2] = current_mmr
    datas[str(ctx.author.id)][3] = max_mmr
    datas[str(ctx.author.id)][4] = player.name

    save_player_datas(datas)

    ger_check = False
    eng_check = False
    both_check = False
    if 1133964116793491476 in member.role_ids:
        ger_check = True
    if 1133964210892705794 in member.role_ids:
        eng_check = True

    lang_display = None
    if ger_check and eng_check:lang_display="🇩🇪 German - 🇬🇧 English"
    elif ger_check:lang_display="🇩🇪 German"
    elif eng_check:lang_display="🇬🇧 English"

    em = hikari.Embed(description=f"**UBISOFT USERNAME:** {player.name}", color="#ffffff")
    em.add_field(name="Aktueller Rank:", value=f"{rank}")

    try:
        await player.load_summaries()

        kd_ratio = 0
        hs_acc = 0
        wl_ratio = 0

        seasons = sorted(player.all_summary.keys(), reverse=True)
        season = seasons[0]

        kd_ratio = player.ranked_summary[season]["all"].kill_death_ratio
        hs_acc = player.ranked_summary[season]["all"].headshot_accuracy
        win = player.ranked_summary[season]["all"].matches_won
        matches = player.ranked_summary[season]["all"].matches_played

        kd_ratio = round(kd_ratio/100, 2)
        hs_acc = round(hs_acc, 2)
        wl_ratio = round(win/matches, 2)*100
        
        em.add_field(name="Statistiken:", value=f"**Win Rate:** {wl_ratio}%\n**KD:** {kd_ratio}\n**Headshot Rate:** {hs_acc}%")
    except InvalidRequest:
        await ctx.respond(content=f"**{player.name}** hat noch keine Einträge diese Season.")
        return 
    
    if lang_display:em.add_field(name=f"Sprache{'n' if both_check else ''}", value=lang_display)
    em.set_author(name=f"{member}'s Profil", icon=member.display_avatar_url)
    em.set_thumbnail(rank_images[rank.split(" ")[0]])

    if channel and note:
        await ctx.respond(content=f"{member.mention} Sucht nache einer Gruppe in {channel.mention} : `{note}`", embed=em)
    elif channel:
        await ctx.respond(content=f"{member.mention} Sucht nache einer Gruppe in {channel.mention}.", embed=em)
    elif note:
        await ctx.respond(content=f"{member.mention} Sucht nache einer Gruppe: `{note}`", embed=em)
    else:
        await ctx.respond(content=f"{member.mention} Sucht nache einer Gruppe.", embed=em)
    await auth.close()

@bot.command()
@lightbulb.command("rankembed", "Erstelle die Ranking Embed im Rainbow Six Channel")
@lightbulb.implements(lightbulb.SlashCommand)
async def rankembed(ctx: lightbulb.SlashContext) -> None:
    

    embed = hikari.Embed(
        title="**Rank Rolle erhalten**",
        description="Du kannst deinen Rang erhalten, indem du die **</get-rank:1131819805377298432>**\nim <#886559555629244417> Channel verwendest. "
                    "Gib deinen Benutzernamen, E-Mail und dein Passwort ein um zu Verifizieren das du der Account Inhaber bist.",
        color="#ffffff"
    )

    # Zeige eine Notiz, dass keine sensiblen Daten gespeichert oder weitergegeben werden
    embed.add_field(
        name="Wichtige Information",
        value="Wir möchten betonen, dass wir **keinerlei** sensible Daten wie Passwörter oder E-Mails **speichern** "
            'oder weitergeben. Die einzigen Informationen, die wir speichern und einsehen können, sind: \n\n'
            '```json\n'
            '{\n'
            '   "ubisoft_id": "Deine Ubisoft ID",\n'
            '   "ingame_name": "Dein Ingame Name",\n'
            '   "rank": "Dein Aktueller Rang",\n'
            '   "current_mmr": "Deine Aktuelle MMR anzahl",\n'
            '   "max_mmr": "Die höchste MMR anzahl die du je hattest",\n'
            '   "discord_user_id": "Deine Discord User ID",\n'
            '   \n'
            '}\n'
            '```'
            "**Was sind das für Knöpfe?**\n\n**Hinzufügen:** Verlinke deinen Ubisoft Account\n**Entfernen:** Lösche deine Daten aus unserer Datenbank.\n\n**Anzeigen**: Zeige deinen Rang in deinen Rollen an\n**Verstecken:** Verstecke deinen Rang.\n\n**Aktualisieren:** Aktualisiere deinen Rank\n\n\n**Ubisoft Account mit Discord Verküpfen:\nUm deinen Ubisoft Account mit Discord zu verknüpfen siehe den Post in <#1136689679639519333>."
    )
    embed.add_field(
        name="Public Repo",
        value="Bei Bedenken oder interesse:"
            "Unser Code ist voll transparent und unter folgenden link einsehbar\n"
            "https://github.com/Sector-7-Development-Team/Rainbow-Six-Verification"
    )

    add_rem = bot.rest.build_message_action_row()
    add_rem.add_interactive_button(components.ButtonStyle.SUCCESS, "add", label="Hinzufügen")
    add_rem.add_interactive_button(components.ButtonStyle.DANGER, "remove", label="Entfernen")
    
    show_hide = bot.rest.build_message_action_row()
    show_hide.add_interactive_button(components.ButtonStyle.SECONDARY, "show", label="Anzeigen")
    show_hide.add_interactive_button(components.ButtonStyle.SECONDARY, "hide", label="Verstecken")
    
    update = bot.rest.build_message_action_row().add_interactive_button(components.ButtonStyle.PRIMARY, "update", label="Aktualisieren")

    await ctx.get_channel().send(embed=embed, components=[add_rem, show_hide, update])
    await ctx.respond(content=f"Sent !", flags=hikari.MessageFlag.EPHEMERAL)

@bot.listen()
async def on_interaction_create(event: hikari.InteractionCreateEvent):
    if event.interaction.type == hikari.InteractionType.MODAL_SUBMIT:
        custom_id = event.interaction.custom_id
        guild_id = real_ids["guild"]
        inter:hikari.ModalInteraction = event.interaction
        
        if custom_id == "modal_add":
            await inter.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE, flags=hikari.MessageFlag.EPHEMERAL)

            values = inter.components
            
            ubisoft_name = values[0].components[0].value
            platform = values[1].components[0].value
            member_id = str(inter.user.id)
            
            guild_id = real_ids["guild"]
            auth = Auth(def_mail, def_pw)

            plats = {"PC": "uplay", "Playstation": "psn", "Xbox": "xbl"}
            try:platform = plats[platform]
            except:
                await inter.edit_initial_response(content=f"Bitte gib eine Korrekte Platform an")
                return
            try:
                player = await auth.get_player(name=ubisoft_name, platform=platform)
                user_id = player.id
            except InvalidRequest:
                await inter.edit_initial_response(content=f"(Pass auf das du die richtige Platform ausgewählt hast) Keine Daten zu diesem Ubisoft Account gefunden. Sollte dies ein Fehler sein öffne bitte ein <#963132179813109790>.")
                await auth.close()
                return
            
            payload = await player.load_linked_accounts()
            discord_id = None
            for acc in payload:
                if acc.platform_type == 'discord':
                    discord_id = int(acc.id_on_platform)

            if not discord_id:
                await inter.edit_initial_response(content=f"Der Ubisoft Account {ubisoft_name}, hat kein Discord-profil verlinkt.")
                await auth.close()
                return
            elif discord_id != inter.user.id:
                await inter.edit_initial_response(content=f"Dein Discord Account ist nicht in {ubisoft_name}'s profil verlinkt.")
                await auth.close()
                return

            await player.load_ranked_v2()
            rank_name = player.ranked_profile.rank
            max_mmr = player.ranked_profile.max_rank_points
            current_mmr = player.ranked_profile.rank_points
            role_id = real_ids["rank_roles"][rank_name.split(" ")[0]]
            await bot.rest.add_role_to_member(guild_id, inter.user, role_id)
            await inter.edit_initial_response(content=f"Du hast dich mit **{player.name}** verifiziert.\nDir wurde der Rank <@&{role_id}> gegeben.")

            # Save player datas to JSON file
            datas[member_id] = [user_id, rank_name, current_mmr, max_mmr, player.name, True, platform]
            save_player_datas(datas)
            
            await auth.close()
    
    if event.interaction.type == hikari.InteractionType.MESSAGE_COMPONENT:
        custom_id = event.interaction.custom_id
        guild_id = real_ids["guild"]
        inter:hikari.ComponentInteraction = event.interaction

        
        if custom_id == "add":
            if str(inter.user.id) in datas:
                await inter.create_initial_response(response_type=hikari.ResponseType.MESSAGE_CREATE, content=f"Du bist bereits in der Datenbank", flags=hikari.MessageFlag.EPHEMERAL)
                return
        
            username_row = bot.rest.build_modal_action_row()
            username_row.add_text_input("username", "Ubisoft username", placeholder="Enter your ubisoft username")
            platform_row = bot.rest.build_modal_action_row()
            platform_row.add_text_input("platform", "Platform", placeholder='"PC", "Playstation" and "Xbox"', max_length=10)
            
            await inter.create_modal_response(title="Linking your R6 account", custom_id="modal_add", components=[username_row, platform_row])


        elif custom_id == "remove":
            await inter.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE, flags=hikari.MessageFlag.EPHEMERAL)

            if str(inter.user.id) not in datas:
                await inter.edit_initial_response(content=f"Du bist nicht in der Datenbank.")
                return

            for rid in real_ids["rank_roles"].values():
                await bot.rest.remove_role_from_member(guild_id, inter.user, rid)

            del datas[str(inter.user.id)]
            save_player_datas(datas)

            await inter.edit_initial_response(content=f"Du wurdest aus der Datenbank entfernt.")

        elif custom_id == "show":
            await inter.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE, flags=hikari.MessageFlag.EPHEMERAL)

            if str(inter.user.id) not in datas:
                await inter.edit_initial_response(content=f"Du bist nicht in der Datenbank.")
                return

            if datas[str(inter.user.id)][5]:
                await inter.edit_initial_response(content=f"Dein Rang wird bereits Angezeigt.")
                return
            
            rank = datas[str(inter.user.id)][1]
            role_id = real_ids["rank_roles"][rank.split(" ")[0]]

            await bot.rest.add_role_to_member(guild_id, inter.user, role_id)

            datas[str(inter.user.id)][5] = True
            save_player_datas(datas)

            await inter.edit_initial_response(content=f"Dein Rang wurde Aktualisiert. Neuer Rang: <@&{role_id}>.")

        elif custom_id == "hide":
            await inter.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE, flags=hikari.MessageFlag.EPHEMERAL)

            if str(inter.user.id) not in datas:
                await inter.edit_initial_response(content=f"Du bist nicht in der Datenbank.")
                return

            if not datas[str(inter.user.id)][5]:
                await inter.edit_initial_response(content=f"Dein Rang ist bereits versteckt.")
                return
            
            for rid in real_ids["rank_roles"].values():
                await bot.rest.remove_role_from_member(guild_id, inter.user, rid)

            datas[str(inter.user.id)][5] = False
            save_player_datas(datas)

            await inter.edit_initial_response(content=f"Dein Rang wurde versteckt.")
        
        elif custom_id == "update":
            
            await inter.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE, flags=hikari.MessageFlag.EPHEMERAL)
            member_id = str(inter.user.id)
            try:
                user_id = datas[member_id][0]
            except:
                await inter.edit_initial_response(content=f"Du hast noch keinen Account Hinzugefügt: verwende </lfg:1134870100315492425> oder drücke den Add button!")
                return

            if not datas[member_id][5]:
                await inter.edit_initial_response(content=f"Du hast deinen rang versteckt. um ihn wieder anzuzeigen, drücke den \"Show\" button.")
                return

            auth = Auth(def_mail, def_pw)
            player = await auth.get_player(uid=user_id)

            await player.load_ranked_v2()
            rank_name = player.ranked_profile.rank
            if rank_name == datas[member_id][1]:
                await inter.edit_initial_response(content=f"Dein Rang muss nicht Aktualisert werden.")
                return
            
            max_mmr = player.ranked_profile.max_rank_points
            current_mmr = player.ranked_profile.rank_points
            for rid in real_ids["rank_roles"].values():
                await bot.rest.remove_role_from_member(guild_id, inter.user, rid)

            role_id = real_ids["rank_roles"][rank_name.split(" ")[0]]
            await bot.rest.add_role_to_member(guild_id, inter.user, role_id)

            datas[1] = rank_name
            datas[2] = current_mmr
            datas[3] = max_mmr
            datas[4] = player.name
            save_player_datas(datas)

            await inter.edit_initial_response(content=f"Dein Rang wurde Aktualisert. Neuer Rang: <@&{role_id}>.", user_mentions=True, role_mentions=True)



bot.run()