import discord
from discord.ext import commands
import os
import Helper

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=Helper.get_prefix, case_insensitive=False, intents=intents)
client.remove_command('help')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f"cogs.{filename[:-3]}")

with open('BOT_TOKEN.txt', 'r') as file:
    client.run(file.read())

