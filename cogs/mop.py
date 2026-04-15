import discord
import random
from discord.ext import commands
from discord import app_commands

class Mop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    moppen = [
        "Ik geef zo een mop voor je hoofd",
        "Sorry, geen zin in.",
        "Val je moeder lekker lastig ofzo",
        "Ga buiten spelen alsjeblieft",
        "Ik ken helemaal geen mop, stop met vragen",
        "Wil je een krentenbol?",
        "Deze week zijn de krentenbollen in de bonus bij de appie, wist je dat? Nee grapje, ik wil gewoon dat je opflikkerd",
        "Sterf ff lekker af joh bloedzuiger",
        "Waarom kunnen skeletten niet liegen? Omdat je er dwars doorheen kijkt 😂😂",
        "Wat zegt een programmeur als hij het koud heeft? Er zit een bug in mijn jas 😂😂",
        "Waarom ging de computer naar therapie? Hij had te veel issues 😂😂",
        "Wat is het favoriete drankje van een programmeur? Java 😂😂"
    ]

    @app_commands.command(name="mop", description="Ik vertel een mop, als ik daar zin in heb tenminste.")
    async def mop(self, interaction: discord.Interaction):
        mop = random.choice(self.moppen)
        await interaction.response.send_message(mop)
async def setup(bot):
    await bot.add_cog(Mop(bot))