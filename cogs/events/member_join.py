from discord.ext import commands

class MemberJoin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(f"{member} has joined the server.")

async def setup(bot):
    await bot.add_cog(MemberJoin(bot))