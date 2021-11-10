import discord
from discord import mentions
from discord.ext import commands

class Events(commands.Cog):
    """Events Listeners cog"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener('on_message')
    async def on_bot_mention(self, message):
        if (message.guild is None) or (message.author.bot ):
            return

        if message.content.lower() == "<@862771284014530561>" or message.content.lower() == "<@!862771284014530561>":
            return await message.reply(f"My prefixes are : `s/` \n`sd` \n{self.bot.user.mention} ", mention_author = False)
def setup(bot):
    bot.add_cog(Events(bot))