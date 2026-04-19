import discord
from discord import user
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

    @app_commands.command(name="profiel", description="Bekijk een profiel")
    @app_commands.describe(user="De gebruiker waarvan je het profiel wilt zien")
    async def profiel(self, interaction: discord.Interaction, user: discord.User = None):

        target = user or interaction.user
        user_id = target.id

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
        seconden = voice_seconds % 60

        totaal = wins + losses + draws
        winrate = round((wins / totaal) * 100, 1) if totaal > 0 else 0

        embed = discord.Embed(
            title=f"📊 Profiel van {target.display_name}",
            description=f"Stats overzicht voor {target.mention}",
            color=discord.Color.blurple()
        )

        if target.avatar:
            embed.set_thumbnail(url=target.avatar.url)

        embed.add_field(
            name="🎮 SPS Stats",
            value=(
                "```"
                f"Wins     | {wins}\n"
                f"Losses   | {losses}\n"
                f"Draws    | {draws}\n"
                f"Played   | {totaal}\n"
                f"Winrate  | {winrate}%\n"
                "```"
            ),
            inline=False
        )

        embed.add_field(
            name="💬 Server Stats",
            value=(
                "```"
                f"Messages | {messages}\n"
                f"Voice    | {uren}u {minuten}m {seconden}s\n"
                "```"
            ),
            inline=False
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Profile(bot))