import discord
from discord.ext import commands
from discord import app_commands

from database import (
    get_global_sps_leaderboard,
    get_server_messages_leaderboard,
    get_server_voice_leaderboard,
    get_server_level_leaderboard
)


class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    soorten = [
        app_commands.Choice(name="sps", value="sps"),
        app_commands.Choice(name="berichten", value="berichten"),
        app_commands.Choice(name="voice", value="voice"),
        app_commands.Choice(name="levels", value="levels")
    ]

    @app_commands.command(
        name="leaderboard",
        description="Bekijk een leaderboard"
    )
    @app_commands.choices(soort=soorten)
    async def leaderboard(
        self,
        interaction: discord.Interaction,
        soort: app_commands.Choice[str]
    ):
        keuze = soort.value

        # =========================
        # SPS
        # =========================

        if keuze == "sps":
            data = get_global_sps_leaderboard()

            if not data:
                await interaction.response.send_message(
                    "Aw, niemand heeft nog een potje steen, papier, schaar met mij gespeeld :(",
                )
                return

            regels = []
            medals = {
                1: "🥇",
                2: "🥈",
                3: "🥉"
            }

            for i, (user_id, wins, losses, draws) in enumerate(data, start=1):
                icoon = medals.get(i, f"#{i}")

                regels.append(
                    f"**{icoon}** <@{user_id}>\n"
                    f"`{wins}` wins | "
                    f"`{losses}` losses | "
                    f"`{draws}` draws\n"
                )

            embed = discord.Embed(
                title="Leaderboard - Steen, Papier, Schaar",
                description="\n".join(regels),
                color=discord.Color.gold()
            )

            embed.set_footer(
                text=interaction.guild.name,
                icon_url=(
                    interaction.guild.icon.url
                    if interaction.guild.icon
                    else discord.Embed.Empty
                )
            )

            await interaction.response.send_message(embed=embed)

        # =========================
        # MESSAGES
        # =========================

        elif keuze == "berichten":
            if interaction.guild is None:
                await interaction.response.send_message(
                    "Dit kan alleen in een server!",
                    ephemeral=True
                )
                return

            data = get_server_messages_leaderboard(
                interaction.guild.id
            )

            if not data:
                await interaction.response.send_message(
                    "Dat is wel heel pijnlijk, niemand heeft nog een bericht gestuurd in deze server."
                )
                return

            regels = []
            medals = {
                1: "🥇",
                2: "🥈",
                3: "🥉"
            }

            for i, (user_id, messages) in enumerate(data, start=1):
                icoon = medals.get(i, f"#{i}")

                regels.append(
                    f"**{icoon}** <@{user_id}>  •  "
                    f"`{messages}` berichten"
                )

            embed = discord.Embed(
                title=f"Leaderboard - Berichten",
                description="\n".join(regels),
                color=discord.Color.blue()
            )

            embed.set_footer(
                text=interaction.guild.name,
                icon_url=(
                    interaction.guild.icon.url
                    if interaction.guild.icon
                    else discord.Embed.Empty
                )
            )

            await interaction.response.send_message(embed=embed)

        # =========================
        # VOICE
        # =========================

        elif keuze == "voice":
            if interaction.guild is None:
                await interaction.response.send_message(
                    "Dit kan alleen in een server!",
                    ephemeral=True
                )
                return

            data = get_server_voice_leaderboard(
                interaction.guild.id
            )

            if not data:
                await interaction.response.send_message(
                    "Niemand heeft nog in voice gezeten, dus hoe wil ik een leaderboard maken? Lege vaas"
                )
                return

            regels = []
            medals = {
                1: "🥇",
                2: "🥈",
                3: "🥉"
            }

            for i, (user_id, voice_seconds) in enumerate(data, start=1):
                icoon = medals.get(i, f"#{i}")

                uren = voice_seconds // 3600
                minuten = (voice_seconds % 3600) // 60
                seconden = voice_seconds % 60

                regels.append(
                    f"**{icoon}** <@{user_id}>  •  "
                    f"`{uren}u {minuten}m {seconden}s`"
                )

            embed = discord.Embed(
                title=f"Leaderboard - Voice",
                description="\n".join(regels),
                color=discord.Color.purple()
            )

            embed.set_footer(
                text=interaction.guild.name,
                icon_url=(
                    interaction.guild.icon.url
                    if interaction.guild.icon
                    else discord.Embed.Empty
                )
            )

            await interaction.response.send_message(embed=embed)

        # =========================
        # LEVELS
        # =========================

        elif keuze == "levels":
            if interaction.guild is None:
                await interaction.response.send_message(
                    "Dit kan alleen in een server!",
                    ephemeral=True
                )
                return

            data = get_server_level_leaderboard(
                interaction.guild.id
            )

            if not data:
                await interaction.response.send_message(
                    "Lmao niemand heeft nog een level behaald in deze server, noobies"
                )
                return

            regels = []

            medals = {
                1: "🥇",
                2: "🥈",
                3: "🥉"
            }

            for i, (user_id, level, xp) in enumerate(data, start=1):

                member = interaction.guild.get_member(user_id)

                if member:
                    username = member.display_name
                else:
                    username = f"<@{user_id}>"

                icoon = medals.get(i, f"#{i}")

                regels.append(
                    f"{icoon} **{username}**\n"
                    f"   Level **{level}**  •  `{xp:,} XP`"
                )

            embed = discord.Embed(
                title="Leaderboard - Levels",
                description="\n\n".join(regels),
                color=discord.Color.blurple()
            )

            embed.set_footer(
                text=interaction.guild.name,
                icon_url=(
                    interaction.guild.icon.url
                    if interaction.guild.icon
                    else discord.Embed.Empty
                )
            )

            await interaction.response.send_message(
                embed=embed
            )


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))