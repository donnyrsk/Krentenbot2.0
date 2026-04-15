import discord
import random
from discord.ext import commands
from discord import app_commands

from database import create_sps_profile_if_not_exists, add_win, add_loss, add_draw


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
        user_id = interaction.user.id
        user_keuze = keuze.value
        bot_keuze = random.choice(["steen", "papier", "schaar"])

        create_sps_profile_if_not_exists(user_id)

        emoji = {
            "steen": "🪨",
            "papier": "📄",
            "schaar": "✂️"
        }

        user_emote = emoji[user_keuze]
        bot_emote = emoji[bot_keuze]

        if bot_keuze == user_keuze:
            add_draw(user_id)
            uitslag = f"Bot kiest {bot_emote} | Jij kiest {user_emote}\n\nWAT?! GELIJKSPEL?! *tieft pc in het water*"
        elif (
            (user_keuze == "steen" and bot_keuze == "schaar") or
            (user_keuze == "papier" and bot_keuze == "steen") or
            (user_keuze == "schaar" and bot_keuze == "papier")
        ):
            add_win(user_id)
            uitslag = f"Bot kiest {bot_emote} | Jij kiest {user_emote}\n\nIk heb schaar gekozen, jij wint verdomme *slaat bureau in tienen*"
        else:
            add_loss(user_id)
            uitslag = f"Bot kiest {bot_emote} | Jij kiest {user_emote}\n\nIk heb papier gekozen, jij verliest TERING NOOB! 🖕"

        await interaction.response.send_message(uitslag)


async def setup(bot):
    await bot.add_cog(SteenPapierSchaar(bot))