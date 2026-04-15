from discord.ext import commands

class JeMoeder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.jemoeder = ["je moeder", "je ma", "je mama"]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        content = message.content.lower()

        if any(word in content for word in self.jemoeder):
            await message.channel.send("JOUW MOEDER!")

async def setup(bot):
    await bot.add_cog(JeMoeder(bot))