import discord
from discord.ext import commands
from discord import app_commands

from database import (
    get_global_sps_leaderboard,
    get_server_messages_leaderboard,
    get_server_voice_leaderboard
)


class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    soorten = [
        app_commands.Choice(name="SPS Globaal", value="sps"),
        app_commands.Choice(name="Messages Deze Server", value="messages"),
        app_commands.Choice(name="Voice Deze Server", value="voice")
    ]

    @app_commands.command(name="leaderboard", description="Bekijk een leaderboard")
    @app_commands.choices(soort=soorten)
    async def leaderboard(self, interaction: discord.Interaction, soort: app_commands.Choice[str]):
        keuze = soort.value

        if keuze == "sps":
            data = get_global_sps_leaderboard()

            if not data:
                await interaction.response.send_message("Nog geen SPS stats gevonden.")
                return

            regels = []
            for i, (user_id, wins, losses, draws) in enumerate(data, start=1):
                user = self.bot.get_user(user_id)
                naam = user.name if user else f"User {user_id}"
                regels.append(
                    f"**#{i}** {naam} — 🏆 {wins} wins | 💀 {losses} losses | 🤝 {draws} draws"
                )

            embed = discord.Embed(
                title="🌍 Globale SPS Leaderboard",
                description="\n".join(regels),
                color=discord.Color.gold()
            )

            await interaction.response.send_message(embed=embed)

        elif keuze == "messages":
            if interaction.guild is None:
                await interaction.response.send_message("Dit kan alleen in een server.", ephemeral=True)
                return

            data = get_server_messages_leaderboard(interaction.guild.id)

            if not data:
                await interaction.response.send_message("Nog geen message stats in deze server.")
                return

            regels = []
            for i, (user_id, messages) in enumerate(data, start=1):
                member = interaction.guild.get_member(user_id)
                naam = member.display_name if member else f"User {user_id}"
                regels.append(
                    f"**#{i}** {naam} — 💬 {messages} berichten"
                )

            embed = discord.Embed(
                title=f"💬 Message Leaderboard - {interaction.guild.name}",
                description="\n".join(regels),
                color=discord.Color.blue()
            )

            await interaction.response.send_message(embed=embed)

        elif keuze == "voice":
            if interaction.guild is None:
                await interaction.response.send_message("Dit kan alleen in een server.", ephemeral=True)
                return

            data = get_server_voice_leaderboard(interaction.guild.id)

            if not data:
                await interaction.response.send_message("Nog geen voice stats in deze server.")
                return

            regels = []
            for i, (user_id, voice_seconds) in enumerate(data, start=1):
                member = interaction.guild.get_member(user_id)
                naam = member.display_name if member else f"User {user_id}"

                uren = voice_seconds // 3600
                minuten = (voice_seconds % 3600) // 60
                seconden = voice_seconds % 60

                regels.append(
                    f"**#{i}** {naam} — 🎤 {uren}u {minuten}m {seconden}s"
                )

            embed = discord.Embed(
                title=f"🎤 Voice Leaderboard - {interaction.guild.name}",
                description="\n".join(regels),
                color=discord.Color.purple()
            )

            await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))