import discord
from discord.ext import commands
from discord import app_commands

from database import (
    create_sps_profile_if_not_exists,
    create_server_profile_if_not_exists,
    get_sps_profile,
    get_server_profile
)


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="profiel", description="Bekijk jouw profiel")
    async def profiel(self, interaction: discord.Interaction):
        user_id = interaction.user.id

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

            if server_profile is not None:
                messages, voice_seconds = server_profile

        uren = voice_seconds // 3600
        minuten = (voice_seconds % 3600) // 60
        seconden = voice_seconds % 60

        totaal_sps = wins + losses + draws
        winrate = round((wins / totaal_sps) * 100, 1) if totaal_sps > 0 else 0

        embed = discord.Embed(
            title=f"📊 Profiel van {interaction.user.display_name}",
            description=f"Stats overzicht voor **{interaction.user.mention}**",
            color=discord.Color.blurple()
        )

        if interaction.user.avatar:
            embed.set_thumbnail(url=interaction.user.avatar.url)

        embed.add_field(
            name="👤 Algemeen",
            value=(
                f"**Gebruiker:** {interaction.user.mention}\n"
                f"**Server:** {server_naam}"
            ),
            inline=False
        )

        embed.add_field(
            name="🎮 Steen Papier Schaar",
            value=(
                f"**Wins:** {wins}\n"
                f"**Losses:** {losses}\n"
                f"**Draws:** {draws}\n"
                f"**Totaal gespeeld:** {totaal_sps}\n"
                f"**Winrate:** {winrate}%"
            ),
            inline=False
        )

        embed.add_field(
            name="💬 Server Stats",
            value=(
                f"**Messages:** {messages}\n"
                f"**Voice time:** {uren}u {minuten}m {seconden}s"
            ),
            inline=False
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Profile(bot))