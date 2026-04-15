import time
import discord
from discord.ext import commands

from database import create_server_profile_if_not_exists, add_message, add_voice_seconds


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_join_times = {}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        user_id = message.author.id
        guild_id = message.guild.id

        create_server_profile_if_not_exists(user_id, guild_id)
        add_message(user_id, guild_id)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot or member.guild is None:
            return

        user_id = member.id
        guild_id = member.guild.id
        now = time.time()

        key = (user_id, guild_id)

        create_server_profile_if_not_exists(user_id, guild_id)

        # Joined a voice channel
        if before.channel is None and after.channel is not None:
            self.voice_join_times[key] = now

        # Left a voice channel
        elif before.channel is not None and after.channel is None:
            join_time = self.voice_join_times.pop(key, None)
            if join_time is not None:
                seconds = int(now - join_time)
                add_voice_seconds(user_id, guild_id, seconds)

        # Switched voice channels
        elif before.channel != after.channel:
            join_time = self.voice_join_times.get(key)
            if join_time is not None:
                seconds = int(now - join_time)
                add_voice_seconds(user_id, guild_id, seconds)

            self.voice_join_times[key] = now


async def setup(bot):
    await bot.add_cog(Stats(bot))