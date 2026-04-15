import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from database import setup_database

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Ingelogd als {bot.user}")


async def main():
    setup_database()

    async with bot:
        await bot.load_extension("cogs.commands.SPS.steen_papier_schaar")
        await bot.load_extension("cogs.profile")
        await bot.load_extension("cogs.stats")

        await bot.start(TOKEN)


import asyncio
asyncio.run(main())