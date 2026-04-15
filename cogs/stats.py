import time
import discord
from discord.ext import commands

from database import create_profile_if_not_exists, add_message, add_voice_seconds


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_join_times = {}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        create_profile_if_not_exists(message.author.id)
        add_message(message.author.id)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return

        user_id = member.id
        now = time.time()

        create_profile_if_not_exists(user_id)

        # Joined a voice channel
        if before.channel is None and after.channel is not None:
            self.voice_join_times[user_id] = now

        # Left a voice channel
        elif before.channel is not None and after.channel is None:
            join_time = self.voice_join_times.pop(user_id, None)
            if join_time is not None:
                seconds = int(now - join_time)
                add_voice_seconds(user_id, seconds)

        # Switched voice channels
        elif before.channel != after.channel:
            join_time = self.voice_join_times.get(user_id)
            if join_time is not None:
                seconds = int(now - join_time)
                add_voice_seconds(user_id, seconds)

            self.voice_join_times[user_id] = now


async def setup(bot):
    await bot.add_cog(Stats(bot))