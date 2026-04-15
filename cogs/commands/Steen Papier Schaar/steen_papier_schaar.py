import discord
import random
from discord.ext import commands
from discord import app_commands

class SteenPapierSchaar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    keuzes = [
        app_commands.Choice(name="Steen", value="steen"),
        app_commands.Choice(name="Papier", value="papier"),
        app_commands.Choice(name="Schaar", value="schaar")
    ]

    @app_commands.command(name="sps", description="Speel steen, papier, schaar")
    @app_commands.choices(keuze=keuzes)
    async def sps(self, interaction: discord.Interaction, keuze: app_commands.Choice[str]):
        user_keuze = keuze.value
        bot_keuze = random.choice(["steen", "papier", "schaar"])

        if user_keuze == "steen":
            user_emote = "🪨"
        elif user_keuze == "papier":
            user_emote = "📄"
        elif user_keuze == "schaar":
            user_emote = "✂️"

        if bot_keuze == "steen":
            bot_emote = "🪨"
        elif bot_keuze == "papier":
            bot_emote = "📄"
        elif bot_keuze == "schaar":
            bot_emote = "✂️"

        if bot_keuze == user_keuze:
            uitslag = f"Bot kiest {bot_emote} | Jij kiest {user_emote}\n\nWAT?! GELIJKSPEL?! *tieft pc in het water*"
        elif (
            (user_keuze == "steen" and bot_keuze == "schaar") or
            (user_keuze == "papier" and bot_keuze == "steen") or
            (user_keuze == "schaar" and bot_keuze == "papier")
        ):
            uitslag = f"Bot kiest {bot_emote} | Jij kiest {user_emote}\n\nIk heb {bot_keuze} gekozen, jij wint verdomme *slaat bureau in tienen*"
        else:
            uitslag = f"Bot kiest {bot_emote} | Jij kiest {user_emote}\n\nIk heb {bot_keuze} gekozen, jij verliest TERING NOOB! 🖕"

        await interaction.response.send_message(uitslag)

async def setup(bot):
    await bot.add_cog(SteenPapierSchaar(bot))