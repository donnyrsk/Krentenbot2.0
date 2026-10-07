import discord
from database import get_level_progress
from discord.ext import commands
from discord import app_commands

from database import (
    create_sps_profile_if_not_exists,
    create_server_profile_if_not_exists,
    get_sps_profile,
    get_server_profile
)

def progress_bar(current, total, length=10):
    if total == 0:
        return "▱" * length

    filled = int((current / total) * length)
    return "▰" * filled + "▱" * (length - filled)


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="profiel", description="Bekijk een profiel")
    @app_commands.describe(user="De gebruiker waarvan je het profiel wilt zien")
    async def profiel(self, interaction: discord.Interaction, user: discord.Member = None):

        target = user or interaction.user
        user_id = target.id

        server_icon_url = None
        if interaction.guild and interaction.guild.icon:
            server_icon_url = interaction.guild.icon.url

        create_sps_profile_if_not_exists(user_id)
        wins, losses, draws = get_sps_profile(user_id)

        messages = 0
        voice_seconds = 0
        server_naam = "Geen server"

        if interaction.guild is not None:
            guild_id = interaction.guild.id
            server_naam = interaction.guild.name

            create_server_profile_if_not_exists(user_id, guild_id)
            server_profile = get_server_profile(user_id, guild_id)

            if server_profile:
                messages, voice_seconds = server_profile

        uren = voice_seconds // 3600
        minuten = (voice_seconds % 3600) // 60

        totaal = wins + losses + draws
        winrate = round((wins / totaal) * 100, 1) if totaal > 0 else 0

        xp = (
            wins * 100
            + draws * 20
            + messages * 5
            + int(voice_seconds / 60)
        )

        level, level_progress, level_required = get_level_progress(xp)

        embed = discord.Embed(
            title=f"{target.display_name} | {target.name}",
            description=(
                f"Level **{level}**  •  `{level_progress}/{level_required} XP`\n"
                f"`{progress_bar(level_progress, level_required, length=12)}`"
            ),
            color=discord.Color.blurple()
        )
        
        if target.avatar:
            embed.set_thumbnail(url=target.avatar.url)

        embed.add_field(
            name="Steen, Papier, Schaar",
            value=f"Wins: `{wins}`\nLosses: `{losses}`\nWinrate: `{winrate}%`",
            inline=True
        )

        embed.add_field(
            name="Activiteit",
            value=f"Berichten: `{messages}`\nVoice: `{uren}u {minuten}m`",
            inline=True
        )

        embed.set_footer(
            text=f"{server_naam}",
            icon_url=server_icon_url if server_icon_url else None
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Profile(bot))