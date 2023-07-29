from env import token, def_mail, def_pw
import hikari
import lightbulb
from lightbulb.ext import tasks
import json
from siegeapi import Auth
from siegeapi.exceptions import FailedToConnect, InvalidRequest
from hikari import components
from hikari import snowflakes

bot = lightbulb.BotApp(
    token=token,
    intents=hikari.Intents.ALL_UNPRIVILEGED | hikari.Intents.MESSAGE_CONTENT | hikari.Intents.GUILD_MEMBERS
)

with open("player_datas.json", "r") as file:
    datas = json.load(file)

def save_player_datas(data):
    with open("player_datas.json", "w") as file:
        json.dump(data, file)


# Rang-IDs in Rainbow Six Siege und ihre entsprechenden Rollen-IDs im Discord-Server
rank_roles = {
    "Champions": "1002405009511694347",
    "Diamond 1": "1002404966247436448",
    "Diamond 2": "1002404966247436448",
    "Diamond 3": "1002404966247436448",
    "Diamond 4": "1002404966247436448",
    "Diamond 5": "1002404966247436448",
    "Emerald 1": "1106931698739978310",
    "Emerald 2": "1106931698739978310",
    "Emerald 3": "1106931698739978310",
    "Emerald 4": "1106931698739978310",
    "Emerald 5": "1106931698739978310",
    "Platinum 1": "1002404938112041060",
    "Platinum 2": "1002404938112041060",
    "Platinum 3": "1002404938112041060",
    "Platinum 4": "1002404938112041060",
    "Platinum 5": "1002404938112041060",
    "Gold 1": "1002404919711629362",
    "Gold 2": "1002404919711629362",
    "Gold 3": "1002404919711629362",
    "Gold 4": "1002404919711629362",
    "Gold 5": "1002404919711629362",
    "Silver 1": "1002404904419213332",
    "Silver 2": "1002404904419213332",
    "Silver 3": "1002404904419213332",
    "Silver 4": "1002404904419213332",
    "Silver 5": "1002404904419213332",
    "Bronze 1": "1002404873712713789",
    "Bronze 2": "1002404873712713789",
    "Bronze 3": "1002404873712713789",
    "Bronze 4": "1002404873712713789",
    "Bronze 5": "1002404873712713789",
    "Copper 1": "1002404818607951954",
    "Copper 2": "1002404818607951954",
    "Copper 3": "1002404818607951954",
    "Copper 4": "1002404818607951954",
    "Copper 5": "1002404818607951954",
    "Unranked": "1131862700503339038"
}

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

@tasks.task(auto_start=True, h=1)
async def ranks_check():
    for user_id, info in datas.items():
        rank = info[1]
        guild = await bot.rest.fetch_guild(678607632692543509)
        user = guild.get_member(user_id)

        for role_id in rank_roles:
            if role_id in user.role_ids:await bot.rest.remove_role_from_member(guild, user, role_id)

        await bot.rest.add_role_to_member(guild, user, rank_roles[rank])

@bot.command()
@lightbulb.option("password", "The password for your Ubisoft account")
@lightbulb.option("email", "Your Ubisoft email")
@lightbulb.command("get-rank", "Get your Rank")
@lightbulb.implements(lightbulb.SlashCommand)
async def create_rank(ctx: lightbulb.Context) -> None:
    password = ctx.options.password
    mail = ctx.options.email
    member = ctx.member

    guild_id = 678607632692543509
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
    rank_role_id = rank_roles.get(rank_name)

    if rank_name in rank_roles:
        await bot.rest.add_role_to_member(guild_id, member, rank_role_id)
        await ctx.respond(content=f"Du hast dich mit **{player.name}** verifiziert.\nDir wurde der Rank {rank_name} gegeben.", flags=hikari.MessageFlag.EPHEMERAL)

        # Save player datas to JSON file
        datas[str(ctx.author.id)] = [auth.userid, rank_name]
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
        await ctx.respond(content=f"Du hast noch keinen Account verlinkt. Bitte verwende **/get-rank** in <#886559555629244417> um deinen Rang zu erhalten.\nWeiter Informationen findest du in <#1115374316255715489>.", flags=hikari.MessageFlag.EPHEMERAL)
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
    datas[str(ctx.author.id)][1] = rank
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
    
    channel_id = 1115374316255715489  # ID des Kanals, in dem die eingebettete Nachricht gesendet werden soll
    channel = await bot.rest.fetch_channel(channel_id)

    embed = hikari.Embed(
        title="**Rank Rolle erhalten**",
        description="Du kannst deinen Rang erhalten, indem du die `/get-rank`\nim <#886559555629244417> Channel verwendest. "
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
            "    \"player_name\": \"Dein Ingame Name\",\n"
            "    \"rank\": \"Dein Aktueler Rang\",\n"
            "    \"discord_user_id\": 442729843055132674\n"
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
    
    ban_roles = [
            "1002339919672381582",
            "907309021722193972",
            "895342175305498655"
        ]
    
    user_id = ctx.member
    guild_id = 678607632692543509


    member = await bot.rest.fetch_member(guild_id, user_id)
    user_roles = [str(role_id) for role_id in member.role_ids]

    if any(role in ban_roles for role in user_roles):
        await channel.send(embed=embed, components=[update, remove])


@bot.listen()
async def on_interaction_create(event: hikari.InteractionCreateEvent):
    if event.interaction.type is hikari.InteractionType.MESSAGE_COMPONENT:
        custom_id = event.interaction.custom_id
        message_id = custom_id.split("_")[-1]  # Extract the message_id from the custom_id

        if custom_id.startswith("update"):
            await event.interaction.create_initial_response(
                hikari.ResponseType.MESSAGE_CREATE,
                content="Um deinen Rang zu aktualisieren öffne ein <#963132179813109790>",
                flags=hikari.MessageFlag.EPHEMERAL
            )

        elif custom_id.startswith("remove"):
            guild_id = 678607632692543509
            member = await bot.rest.fetch_member(guild_id, event.interaction.user.id)

            #Fetch the roles of the member
            roles = [str(role_id) for role_id in member.role_ids]

            for rank_name, role_id in rank_roles.items():
                if role_id in roles:
                    await bot.rest.remove_role_from_member(guild_id, member, int(role_id))
                    print(f"Role {role_id} removed from {member.username}.")

            await event.interaction.create_initial_response(
                hikari.ResponseType.MESSAGE_CREATE,
                content="Dein Rang wurde aus deinen Rollen entfernt!",
                flags=hikari.MessageFlag.EPHEMERAL
            )



bot.run()