import requests
import discord
from discord.ext import commands
import json
import re

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

@bot.command(
    brief = "Shows a list of valid config options to modify.",
    help = "Displays every config option to modify, and its current state."
)
@commands.has_role('Sysops')
async def config_options(context, *args):
    properties_file = open("/opt/minecraft/server.properties", "r")
    return_string: str = ""
    for line in properties_file.readlines():
        if line.startswith("#"): # comment
            continue
        
        equal_search = re.search(r"([a-z-.]+)=([a-z0-9 A-Z-\\{}]+)", line)
        groups = equal_search.groups()
        if len(groups) == 1:
            return_string += "**" + equal_search.group(1) + "**: **no value**"

        elif len(groups) == 2:
            return_string += "**" + equal_search.group(1) + "**: **" + equal_search.group(2) + "**"

    new_embed = discord.Embed(title = "Config List", description = return_string, color = discord.Colour.from_rgb(6, 4, 54))
    await context.send(embed = new_embed)


if __name__ == "__main__":
    bot.run(token)