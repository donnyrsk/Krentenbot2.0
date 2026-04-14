from discord.ext import commands

class MessageFilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bad_words = ["kanker"]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        content = message.content.lower()

        if any(word in content for word in self.bad_words):
            await message.delete()
            await message.channel.send("Niet kanker zeggen in mijn christelijke discord server!")

async def setup(bot):
    await bot.add_cog(MessageFilter(bot))