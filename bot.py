from env import token
import hikari
import lightbulb
import json
from siegeapi import Auth
from hikari import components
from hikari import snowflakes


bot = lightbulb.BotApp(
    token=token,
    intents=hikari.Intents.ALL_UNPRIVILEGED | hikari.Intents.MESSAGE_CONTENT | hikari.Intents.GUILD_MEMBERS
)




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




@bot.command()
@lightbulb.option("password", "The password for your Ubisoft account")
@lightbulb.option("email", "Your Ubisoft email")
@lightbulb.option("username", "Your Ubisoft username")
@lightbulb.command("get-rank", "Get your Rank")
@lightbulb.implements(lightbulb.SlashCommand)
async def create_rank(ctx: lightbulb.Context) -> None:
    password = ctx.options.password
    mail = ctx.options.email
    username = ctx.options.username
    member = ctx.member

    guild_id = 678607632692543509
    auth = Auth(mail, password)
    player = await auth.get_player(username)

    await player.load_ranked_v2()
    rank_name = player.ranked_profile.rank
    rank_role_id = rank_roles.get(rank_name)

    if rank_name in rank_roles:
        await bot.rest.add_role_to_member(guild_id, member, rank_role_id)
        await ctx.respond(content=f"Du hast dich mit **{player.name}** verifiziert.\nDir wurde der Rank {rank_name} gegeben.", flags=hikari.MessageFlag.EPHEMERAL)

        # Save player data to JSON file
        save_player_data(player.name, rank_name, ctx.author.id)

    else:
        await ctx.respond(content=f"Ein Fehler ist aufgetreten beim Verifizieren deines Ranges. Bitte öffne ein <#963132179813109790>!", flags=hikari.MessageFlag.EPHEMERAL)

    await auth.close()


def save_player_data(player_name, rank, discord_user_id):
    data = {
        "player_name": player_name,
        "rank": rank,
        "discord_user_id": discord_user_id,
    }

    with open("player_data.json", "w") as file:
        json.dump(data, file)




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
                content="Um deinen Rang zu aktualisieren musst du erneut den /get-rank command ausführen",
                flags=hikari.MessageFlag.EPHEMERAL
            )

        elif custom_id.startswith("remove"):
            guild_id = 678607632692543509
            member = await bot.rest.fetch_member(guild_id, event.interaction.user.id)

            # Fetch the roles of the member
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