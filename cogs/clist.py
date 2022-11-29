import discord
from discord.ext import commands


class ClistReminder(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        #clist api stuffs
        
        self.base_url = "https://clist.by/api/v1/contest/"
        self.api_key = "f4caba195a30836df60a2d40d4136fe08243bf3c"
        self.api_username = "fuwad2"
        self.credentials = "/?username=fuwad2&api_key=f4caba195a30836df60a2d40d4136fe08243bf3c"

        
        





async def setup(bot):
    await bot.add_cog(ClistReminder(bot))


