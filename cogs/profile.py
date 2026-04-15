import discord
from discord.ext import commands
from discord import app_commands

from database import create_profile_if_not_exists, get_profile


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="profiel", description="Bekijk jouw profiel")
    async def profiel(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        create_profile_if_not_exists(user_id)

        profile = get_profile(user_id)
        wins, losses, draws, messages, voice_seconds = profile

        uren = voice_seconds // 3600
        minuten = (voice_seconds % 3600) // 60

        embed = discord.Embed(
            title=f"Profiel van {interaction.user.display_name}",
            color=discord.Color.blue()
        )

        embed.add_field(name="Wins", value=str(wins), inline=True)
        embed.add_field(name="Losses", value=str(losses), inline=True)
        embed.add_field(name="Draws", value=str(draws), inline=True)
        embed.add_field(name="Messages", value=str(messages), inline=True)
        embed.add_field(name="Voice time", value=f"{uren}u {minuten}m", inline=True)

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Profile(bot))