import discord
from discord.ext import commands
from discord import app_commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Bekijk alle commands")
    async def help(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title="Help",
            description="Hier zijn alle commands:",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="Games",
            value="`/sps` - Steen, papier, schaar spelen",
            inline=False
        )

        embed.add_field(
            name="Stats",
            value="`/profiel` - Bekijk stats van jezelf of een ander\n`/leaderboard` - Bekijk rankings",
            inline=False
        )

        embed.add_field(
            name="Overig",
            value="`/mop` - Krijg een random mop, of niet",
            inline=False
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Help(bot))