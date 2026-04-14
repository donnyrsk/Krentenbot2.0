import os
import asyncio
import discord
import logging
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='krentenbot.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

async def load_cogs():
    for root, _, files in os.walk("cogs"):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                path = os.path.join(root, file)
                module = path.replace(os.sep, ".")[:-3]
                print(f"Loading {module}")
                await bot.load_extension(module)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Slash commands gesynced: {len(synced)}")
    except Exception as e:
        print(f"Sync fout: {e}")

    print(f"Ingelogd als {bot.user} ({bot.user.id})")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(token)

asyncio.run(main())