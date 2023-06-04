import hikari
import lightbulb
import requests
import os
import dotenv

SIEGE_API_KEY = "DEIN_SIEGE_API_SCHLÜSSEL"

bot = lightbulb.BotApp(token=os.environ["TOKEN"])

@bot.command()
@lightbulb.option("password", "the password for your ubisoft account, dw well keep it safe")
@lightbulb.option("username","well guess what it is")
@lightbulb.command("rank","get yourself a new role")
@lightbulb.implements(lightbulb.SlashCommand)
async def set_rank(ctx):
    def check_author(message):
        return message.author.id == ctx.author.id

    

    username = ctx.options.username
    password = ctx.options.password

    try:
        # Ubisoft-Anmeldeinformationen erhalten und ein Anmelde-Token abrufen
        auth_url = "https://public-ubiservices.ubi.com/v3/profiles/sessions"
        auth_payload = {"rememberMe": "true", "name": username, "password": password}
        auth_response = requests.post(auth_url, json=auth_payload)
        auth_data = auth_response.json()
        auth_token = auth_data["ticket"]

        # SiegeAPI-Abfrage mit dem Anmelde-Token, um den Rang des Spielers zu erhalten
        rank_url = f"https://api.siegeapi.io/ranked/emea/{username}"
        rank_headers = {"Authorization": SIEGE_API_KEY, "Ubi-AppId": "39baebad-39e5-4552-8c25-2c9b919064e2", "Ubi-SessionId": auth_token}
        rank_response = requests.get(rank_url, headers=rank_headers)
        rank_data = rank_response.json()
        rank = rank_data["rank"]

        # Rolle mit demselben Namen wie der Rang erstellen oder aktualisieren
        guild = ctx.get_guild()  # Server-Objekt abrufen
        role = hikari.Role(guild_id=guild.id, name=rank)
        role_exists = False

        for existing_role in guild.roles.values():
            if existing_role.name == rank:
                role_exists = True
                role = existing_role
                break

        if not role_exists:
            role = await guild.create_role(name=rank)

        # Rolle dem Befehlsaufrufer hinzufügen
        member = await guild.fetch_member(ctx.author.id)
        await member.add_role(role)

        await ctx.respond(f"Deine Rangrolle wurde zu {rank} aktualisiert!")

    except KeyError:
        await ctx.respond("Dein Rang konnte nicht gefunden werden.")
    except:
        await ctx.respond("Ein Fehler ist aufgetreten. Bitte überprüfe deine Anmeldeinformationen.")

bot.run()