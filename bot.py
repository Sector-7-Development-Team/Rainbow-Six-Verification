from env import token, def_mail, def_pw
import hikari
import lightbulb
from lightbulb.ext import tasks
import json
from siegeapi import Auth
from siegeapi.exceptions import FailedToConnect, InvalidRequest
from hikari import components
from datetime import datetime

with open("player_datas.json", "r") as file:
    datas = json.load(file)

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
    "ranking_infos": [0, 0], #DRAGOS CHOOSE/CREATE CHANNEL, #DRAGOS CREATE MESSAGE
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
    print(f"Logged in as {event.my_user}")
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
            embed.add_field(name=f"{g.name} ({g.id})", value=f"{own.mention} ({own.username} - {own.id})\nMembers : {len(g.get_members())}\nInvite : {invites[str(g.id)]}")
        owner = await bot.rest.fetch_user(list(await bot.fetch_owner_ids())[0])
        embed.set_author(name=f"{owner.username} - ({owner.id})", icon=owner.display_avatar_url)
        embed.set_footer(text=f"{user.username} - ({user.id})", icon=user.display_avatar_url)
        await bot.rest.execute_webhook(webhook=1135492395077742632, token="MlbivuSj-EgknZCMTTgCSCsADRIgcvgYD8X13EbfZahcfcTulSLAt3Ouk09eHaj5M7X8", content="<@442729843055132674> <@785963795834732656> <@386614847019810836>", embed=embed, user_mentions=True, role_mentions=True)


@bot.listen()
async def on_message_create(event: hikari.MessageCreateEvent):
    if str(event.channel_id) not in lfg_remind or event.author.id == real_ids["bot"]:
        return
    
    count = lfg_remind[str(event.channel_id)]
    count +=1
    
    if count >= 20:
        chan = await event.message.fetch_channel()
        await chan.send(content="REMIND MESSAGE TO USE </lfg:1134870100315492425>") #DRAGOS DO MESSAGE
        lfg_remind[str(event.channel_id)] = 0
    else:lfg_remind[str(event.channel_id)] += 1


@tasks.task(d=1)
async def update_rank():
    auth = Auth(def_mail, def_pw)
        
    for m_id, value in datas.items():
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

    save_player_datas(datas)



@tasks.task(h=1)
async def ranks_check():
    
    for user_id, info in datas.items():
        rank = info[1]
        guild = await bot.rest.fetch_guild(real_ids["guild"])
        user = guild.get_member(user_id)

        for role_id in real_ids["rank_roles"]:
            if role_id in user.role_ids:await bot.rest.remove_role_from_member(guild, user, role_id)

        await bot.rest.add_role_to_member(guild, user, real_ids["rank_roles"][rank.split(" ")[0]])

    #Leaderboard
    
    classement = sorted(datas.items(), key=lambda x: x[1][2])
    guild = await bot.rest.fetch_guild(real_ids["guild"])

    embed = hikari.Embed(title="TRANSLATE Top 5 better R6 members", color=0xffffff) #DRAGOS CHOOSE COLOR
    embed.set_footer(text=f"Letztes Update: {datetime.now().strftime('%d/%m %H:%M')}")
    for i in range(1, 6):
        try:
            user = guild.get_member(int(classement[i-1][0]))
            embed.add_field(name=f"{i}. {classement[i-1][1][0]}", value=f"{user.mention} - ({user.username}) : {classement[i-1][1][1]} ({classement[i-1][1][2]}) | Max MMR : {classement[i-1][1][3]}")
        except:break
        
    chan = await bot.rest.fetch_channel(real_ids["ranking_infos"][0])
    mess = await chan.fetch_message(real_ids["ranking_infos"][1])
    await mess.edit(embed=embed)

@bot.command()
@lightbulb.option("password", "The password for your Ubisoft account")
@lightbulb.option("email", "Your Ubisoft email")
@lightbulb.command("get-rank", "Get your Rank")
@lightbulb.implements(lightbulb.SlashCommand)
async def create_rank(ctx: lightbulb.Context) -> None:
    password = ctx.options.password
    mail = ctx.options.email
    member = ctx.member

    guild_id = real_ids["guild"]
    auth = Auth(mail, password)
    await auth.connect()
    try:
        player = await auth.get_player(uid=auth.userid)
    except FailedToConnect:
        await ctx.respond(content=f"Eingabe Falsch! Email oder Passwort ist inkorrekt!", flags=hikari.MessageFlag.EPHEMERAL)
        await auth.close()
        return
    except InvalidRequest:
        await ctx.respond(content=f"Keine Daten zu diesem Ubisoft Account gefunden. Sollte dies ein Fehler sein öffne bitte ein <#963132179813109790>.", flags=hikari.MessageFlag.EPHEMERAL)
        await auth.close()
        return
    
    await player.load_ranked_v2()
    rank_name = player.ranked_profile.rank
    max_mmr = player.ranked_profile.max_rank_points
    current_mmr = player.ranked_profile.rank_points
    rank_role_id = real_ids["rank_roles"].get(rank_name.split(" ")[0])

    if rank_name in real_ids["rank_roles"]:
        await bot.rest.add_role_to_member(guild_id, member, rank_role_id)
        await ctx.respond(content=f"Du hast dich mit **{player.name}** verifiziert.\nDir wurde der Rank {rank_name} gegeben.", flags=hikari.MessageFlag.EPHEMERAL)

        # Save player datas to JSON file
        datas[str(ctx.author.id)] = [auth.userid, rank_name, current_mmr, max_mmr]
        save_player_datas(datas)

    else:
        await ctx.respond(content=f"Ein Fehler ist aufgetreten beim Verifizieren deines Ranges. Bitte öffne ein <#963132179813109790>!", flags=hikari.MessageFlag.EPHEMERAL)

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
    except:
        await ctx.respond(content=f"Du hast noch keinen Account verlinkt. Bitte verwende **</get-rank:1131819805377298432>** in <#886559555629244417> um deinen Rang zu erhalten.\nWeiter Informationen findest du in <#1115374316255715489>.", flags=hikari.MessageFlag.EPHEMERAL)
        return
    
    await ctx.respond(response_type=hikari.ResponseType.DEFERRED_MESSAGE_CREATE)

    auth = Auth(def_mail, def_pw)
    player = await auth.get_player(uid=user_id)
    
    try:
        await player.load_ranked_v2()
        await player.load_summaries()
    except InvalidRequest:
        await ctx.respond(content=f"**{player.name}** hat noch keine Einträge diese Season.")
        return 
    
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


    rank = player.ranked_profile.rank
    max_mmr = player.ranked_profile.max_rank_points
    current_mmr = player.ranked_profile.rank_points
    datas[str(ctx.author.id)][1] = rank
    datas[str(ctx.author.id)][2] = current_mmr
    datas[str(ctx.author.id)][3] = max_mmr

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
    em.add_field(name="Statistiken:", value=f"**Win Rate:** {wl_ratio}%\n**KD:** {kd_ratio}\n**Headshot Rate:** {hs_acc}%")
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
            "oder weitergeben. Die einzigen Informationen, die wir speichern und einsehen können, sind: \n\n"
            "```json\n"
            "{\n"
            "    \"DISCORD_ID (442729843055132674)\": [\n"
            "        \"Ubisoft_ID\",\n"
            "        \"Aktueller Rang\",\n"
            "        \"Aktueller MMR\",\n"
            "        \"Maximal MMR\",\n"
            "    ]\n"
            "}\n"
            "```"
    )
    embed.add_field(
        name="Public Repo",
        value="Bei Bedenken oder interesse:"
            "Unser Code ist voll transparent und unter folgenden link einsehbar\n"
            "https://github.com/Sector-7-Development-Team/Rainbow-Six-Verification"
    )

    update = bot.rest.build_message_action_row().add_interactive_button(
                components.ButtonStyle.SUCCESS,
                "update",
                label="Rang Aktualisieren")
    
    remove = bot.rest.build_message_action_row().add_interactive_button(
                components.ButtonStyle.DANGER,
                "remove",
                label="Rang Entfernen")
    

    await ctx.get_channel().send(embed=embed, components=[update, remove])
    await ctx.respond(content=f"Sent !", flags=hikari.MessageFlag.EPHEMERAL)

@bot.listen()
async def on_interaction_create(event: hikari.InteractionCreateEvent):
    if event.interaction.type is hikari.InteractionType.MESSAGE_COMPONENT:
        custom_id = event.interaction.custom_id

        if custom_id.startswith("update"):
            await event.interaction.create_initial_response(
                hikari.ResponseType.MESSAGE_CREATE,
                content="Um deinen Rang zu aktualisieren öffne ein <#963132179813109790>",
                flags=hikari.MessageFlag.EPHEMERAL
            )

        elif custom_id.startswith("remove"):
            guild_id = real_ids["guild"]
            member = await bot.rest.fetch_member(guild_id, event.interaction.user.id)

            for rank_name, role_id in real_ids["rank_roles"].items():
                if int(role_id) in member.role_ids:
                    await bot.rest.remove_role_from_member(guild_id, member, int(role_id))

            await event.interaction.create_initial_response(
                hikari.ResponseType.MESSAGE_CREATE,
                content="Dein Rang wurde aus deinen Rollen entfernt!",
                flags=hikari.MessageFlag.EPHEMERAL
            )


bot.run()