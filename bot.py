import discord
from discord.ext import commands
import siegeapi
import os
import dotenv
import hikari
import lightbulb

bot = lightbulb.BotApp(token=os.environ["TOKEN"],intents=hikari.Intents.ALL)

@bot.command()
@lightbulb.option("username","well guess what it is")
@lightbulb.command("rank","get yourself a new role")
@lightbulb.implements(lightbulb.SlashCommand)
async def player_rank(ctx, username):
    api = siegeapi.SiegeAPI()
    player = api.get_player(username)
    if player is not None:
        rank = player.get_rank()
        await ctx.send(f"Der Rang des Spielers {username} ist {rank}.")
    else:
        await ctx.send(f"Der Spieler {username} wurde nicht gefunden.")

bot.run()