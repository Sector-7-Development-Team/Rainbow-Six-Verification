from siegeapi import Auth
import asyncio
import hikari
import lightbulb
import dotenv
import os
import siegeapi

bot = lightbulb.BotApp(token=os.environ["TOKEN"])

@bot.command
@lightbulb.option("password", "das passwort für deinen Ubisoft Account. WICHTIG! das passwort wird nicht gespeichert!")
@lightbulb.option("email", "Die Email von deinem Ubisoft Account.")
@lightbulb.command("Login", "Logs you into your Ubisoft account and gives you your R6 rank automatically.")
@lightbulb.implements(lightbulb.SlashCommand)
async def auth(ctx: lightbulb.Context) -> None:
    auth = Auth("email","password")
    player = await auth.get_player(uid="")

    await player.load_ranked_v2()
    print(f"Ranked Points: {player.ranked_profile.rank_points}")
    print(f"Rank: {player.ranked_profile.rank}")
    print(f"Max Rank Points: {player.ranked_profile.max_rank_points}")
    print(f"Max Rank: {player.ranked_profile.max_rank}")
    
    if player.ranked_profile.rank ==  or  or 

    await auth.close()