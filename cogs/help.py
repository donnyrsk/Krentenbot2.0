import discord
from discord.ext import commands
from discord import app_commands


class HelpView(discord.ui.View):
    def __init__(self, author_id):
        super().__init__(timeout=60)
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "Deze help-pagina is niet van jou.",
                ephemeral=True
            )
            return False

        return True

    def create_embed(self, interaction, page):
        if page == "main":
            embed = discord.Embed(
                title="Help",
                description="Klik op de knoppen hieronder om meer te leren over de verschillende commands.",
                color=discord.Color.blurple()
            )

        elif page == "lorcana":
            embed = discord.Embed(
                title="Help - Lorcana",
                description="Bouw en beheer je Lorcana decks.",
                color=discord.Color.blurple()
            )

            embed.add_field(
                name="Deck",
                value=(
                    "`/lordeck nieuw` - Maak een nieuw deck\n"
                    "`/lordeck add` - Voeg kaarten toe\n"
                    "`/lordeck remove` - Verwijder kaarten\n"
                    "`/lordeck bekijken` - Bekijk je deck\n"
                    "`/lordeck delete` - Verwijder je deck"
                ),
                inline=False
            )

            embed.add_field(
                name="Analyse",
                value=(
                    "`/lordeck analyse` - Analyseer je deck\n"
                    "`/lordeck suggesties` - Krijg kaartensuggesties"
                ),
                inline=False
            )

        elif page == "server":
            embed = discord.Embed(
                title="Help - Server",
                description="Overige commands",
                color=discord.Color.blurple()
            )

            embed.add_field(
                name="Profiel & Rankings",
                value=(
                    "`/profiel` - Bekijk stats van jezelf of een ander\n"
                    "`/leaderboard` - Bekijk de rankings"
                ),
                inline=False
            )

            embed.add_field(
                name="Games & Fun",
                value=(
                    "`/sps` - Steen, papier, schaar spelen\n"
                    "`/mop` - Krijg een random mop, of niet"
                ),
                inline=False
            )

        embed.set_footer(
            text=interaction.guild.name,
            icon_url=(
                interaction.guild.icon.url
                if interaction.guild.icon
                else discord.Embed.Empty
            )
        )

        return embed

    @discord.ui.button(
        label="Lorcana",
        style=discord.ButtonStyle.primary
    )
    async def lorcana(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        embed = self.create_embed(interaction, "lorcana")

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    @discord.ui.button(
        label="Server",
        style=discord.ButtonStyle.secondary
    )
    async def server(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        embed = self.create_embed(interaction, "server")

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="help",
        description="Bekijk alle commands"
    )
    async def help(self, interaction: discord.Interaction):

        view = HelpView(interaction.user.id)

        embed = view.create_embed(
            interaction,
            "main"
        )

        await interaction.response.send_message(
            embed=embed,
            view=view
        )


async def setup(bot):
    await bot.add_cog(Help(bot))