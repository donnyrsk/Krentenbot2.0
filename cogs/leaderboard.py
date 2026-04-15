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
        app_commands.Choice(name="Steen papier schaar", value="sps"),
        app_commands.Choice(name="Messages", value="messages"),
        app_commands.Choice(name="Voice", value="voice")
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
            medals = {1: "🥇", 2: "🥈", 3: "🥉"}

            for i, (user_id, wins, losses, draws) in enumerate(data, start=1):
                icoon = medals.get(i, f"#{i}")
                regels.append(
                    f"**{icoon}** <@{user_id}> — 🏆 {wins} wins | 💀 {losses} losses | 🤝 {draws} draws"
                )

            embed = discord.Embed(
                title="🌍 Steen papier schaar leaderboard",
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
            medals = {1: "🥇", 2: "🥈", 3: "🥉"}

            for i, (user_id, messages) in enumerate(data, start=1):
                icoon = medals.get(i, f"#{i}")
                regels.append(f"**{icoon}** <@{user_id}> — 💬 {messages} berichten")

            embed = discord.Embed(
                title=f"💬 Message Leaderboard - **{interaction.guild.name}**",
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
            medals = {1: "🥇", 2: "🥈", 3: "🥉"}

            for i, (user_id, voice_seconds) in enumerate(data, start=1):
                icoon = medals.get(i, f"#{i}")
                uren = voice_seconds // 3600
                minuten = (voice_seconds % 3600) // 60
                seconden = voice_seconds % 60

                regels.append(
                    f"**{icoon}** <@{user_id}> — 🎤 {uren}u {minuten}m {seconden}s"
                )

            embed = discord.Embed(
                title=f"🎤 Voice Leaderboard - **{interaction.guild.name}**",
                description="\n".join(regels),
                color=discord.Color.purple()
            )

            await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))