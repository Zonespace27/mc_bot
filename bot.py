import requests
import discord
from discord.ext import commands
import json
import re
import platform
import subprocess
from time import sleep

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
        if json_data["error"] == "protocol error: io error: Connection refused (os error 111)":
            new_embed = discord.Embed(title = "Player Count", description = "The server is currently down. Please try again later.", color = discord.Colour.from_rgb(12, 110, 48))
            await context.send(embed = new_embed)
            return

        desc = "**" + str(json_data["players"]["now"]) + "** player" + ("" if json_data["players"]["now"] == 1 else "s") + "\n\n"
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
    if platform.system() == "Linux":
        properties_file = open("/opt/minecraft/server.properties", "r")
    else:
        properties_file = open("opt/minecraft/server.properties", "r")
    return_string: str = ""
    for line in properties_file.readlines():
        if line.startswith("#"): # comment
            continue
        
        equal_search = re.search(r"([a-z-.]+)=([a-z0-9 A-Z-\\{}]+)", line)
        if not equal_search:
            equal_search = re.search(r"([a-z-.]+)=", line)
        
        if not equal_search:
            continue

        groups = equal_search.groups()
        if len(groups) == 1:
            return_string += equal_search.group(1) + ": no value\n"

        elif len(groups) == 2:
            return_string += equal_search.group(1) + ": " + equal_search.group(2) + "\n"
        
    properties_file.close()

    new_embed = discord.Embed(title = "Config List", description = return_string, color = discord.Colour.from_rgb(6, 4, 54))
    await context.send(embed = new_embed)

@bot.command(
    brief = "Set a config option.",
    help = "Provided a config option and a value, will set the option to that value. Takes the args of CONFIG, and SET."
)
@commands.has_role('Sysops')
async def config_set(context, *args):
    if len(args) < 2:
        new_embed = discord.Embed(title = "Config Set Failed", description = "Two arguments required for configuration setting.", color = discord.Colour.from_rgb(6, 4, 54))
        await context.send(embed = new_embed)
        return

    if platform.system() == "Linux":
        properties_file = open("/opt/minecraft/server.properties", "r+")
    else:
        properties_file = open("opt/minecraft/server.properties", "r+")
    return_list: list[str] = properties_file.readlines()
    found = False
    for line in return_list:
        if line.startswith("#"): # comment
            continue
        
        if re.search(args[0], line):
            list_index = return_list.index(line)
            return_list.remove(line)
            return_list.insert(list_index, f"{args[0]}={args[1]}\n")
            found = True
            break
    
    if found:
        properties_file.seek(0)
        properties_file.truncate(0)
        properties_file.writelines(return_list)
        properties_file.close()
        new_embed = discord.Embed(title = "Config Set", description = "Configuration set.", color = discord.Colour.from_rgb(6, 4, 54))
        await context.send(embed = new_embed)
        return
    
    properties_file.close()

    new_embed = discord.Embed(title = "Config Set", description = f"Configuration {args[1]} not found.", color = discord.Colour.from_rgb(6, 4, 54))
    await context.send(embed = new_embed)

@bot.command(
    brief = "Reboot the server.",
    help = "Kill the server process before rebooting it. Reboot takes 1-2 minutes."
)
@commands.has_role('Sysops')
async def reboot(context, *args):
    if not(platform.system() == "Linux"):
        new_embed = discord.Embed(title = "Restart Failed", description = "Cannot restart server.", color = discord.Colour.from_rgb(7, 102, 42))
        await context.send(embed = new_embed)
        return # CBA to write shell commands for windows rn

    subprocess.call("killall -9 java", shell=True)
    sleep(1.5) # Give it some time to gracefully exit
    subprocess.call("cd /opt/minecraft", shell=True)
    subprocess.call("./run.sh", shell=True)

    new_embed = discord.Embed(title = "Restarted", description = "Server is now rebooting.", color = discord.Colour.from_rgb(7, 102, 42))
    await context.send(embed = new_embed)

if __name__ == "__main__":
    bot.run(token)