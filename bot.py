import discord
from discord.ext import commands
import siegeapi
import asyncio
import hikari
import lightbulb
import dotenv
import os

bot = lightbulb.BotApp(token=os.environ["TOKEN"])



@bot.command
@lightbulb.option("username","the username of the rainbow six siege profile")
@lightbulb.command("rank", "get yourself a nice new role :D")
@lightbulb.implements(lightbulb.SlashCommand)
async def player_rank(ctx, username)-> None:
    api = siegeapi.SiegeAPI()
    player = api.get_player(username)
    if player is not None:
        rank = player.get_rank()

        # Rolle erstellen oder vorhandene Rolle abrufen
        role = discord.utils.get(ctx.guild.roles, name=rank)

        if role is not None:
            # Discord-Rolle dem Nutzer geben
            await ctx.author.add_roles(role)
            await ctx.send(f"Der Rang des Spielers {username} ist {rank}. Die Discord-Rolle wurde hinzugefügt.")
        else:
            await ctx.send("Die entsprechende Discord-Rolle wurde nicht gefunden.\n Melde dich bitte bei ApfelTeeSaft#7181")
    else:
        await ctx.send(f"Der Spieler {username} wurde nicht gefunden.")
print("Bot is up and running!")
bot.run()