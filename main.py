import os
import asyncio
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

    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game("Krentenbot | /help")
    )

    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} slash commands gesynct")
        for command in bot.tree.get_commands():
            print(f"/{command.name}")
    except Exception as e:
        print(f"Sync fout: {e}")


async def main():
    setup_database()

    async with bot:
        await bot.load_extension("cogs.sps")
        await bot.load_extension("cogs.profile")
        await bot.load_extension("cogs.stats")
        await bot.load_extension("cogs.mop")
        await bot.load_extension("cogs.je_moeder")
        await bot.load_extension("cogs.leaderboard")
        await bot.load_extension("cogs.help")

        await bot.start(TOKEN)


asyncio.run(main())