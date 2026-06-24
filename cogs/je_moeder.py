from discord.ext import commands
import re

class JeMoeder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        content = message.content.lower()

        if re.search(r"\b(je moeder|jouw moeder)\b", content):
            await message.channel.send("JOUW MOEDER!")

async def setup(bot):
    await bot.add_cog(JeMoeder(bot))