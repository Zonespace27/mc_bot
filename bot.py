import requests
import discord
from discord.ext import commands
import json

token: str = ""

if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix = "]", intents = intents)

    token_file = open("token.txt")
    token = token_file.read()
    token_file.close()

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name = "for people to check the ]playercount"))

@bot.command(
    brief = "Displays player count.",
    help = "Displays the numerical player count."
)
async def playercount(context, *args):
    try:
        foo = requests.get("https://mcapi.us/server/status?ip=146.190.59.241&port=21030")
        json_data = json.loads(foo.content)
        desc = "**" + str(json_data["players"]["now"]) + "** player" + ("s" if json_data["players"]["now"] > 1 else "") + "\n\n"
        for player in json_data["players"]["sample"]:
            desc += "**" + player["name"] + "**" + "\n"

        new_embed = discord.Embed(title = "Player Count", description = desc, color = discord.Colour.from_rgb(12, 110, 48))
        await context.send(embed = new_embed)
    except:
        await context.channel.send("An error has occured. Try again later.")

if __name__ == "__main__":
    bot.run(token)