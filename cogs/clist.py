import datetime as dt

import discord
from discord.ext import commands
from main import SnowdenBot
from utils.clist_api import Round, _query_api


class ClistReminder(commands.Cog):

    def __init__(self, bot : SnowdenBot):
        self.bot = bot

        #clist api stuffs
        
        self.base_url = "https://clist.by/api/v1/contest/"
        self.api_key = "f4caba195a30836df60a2d40d4136fe08243bf3c"
        self.api_username = "fuwad2"
        self.credentials = "/?username=fuwad2&api_key=f4caba195a30836df60a2d40d4136fe08243bf3c"

    
    async def create_table(self):

        query = """ CREATE TABLE IF NOT EXISTS clistdata ( id integer PRIMARY KEY, api_data json default '{}'); """

        await self.bot.db.execute(query)

        query = """ INSERT INTO clistdata (id) VALUES ($1) ;"""

        await self.bot.db.execute(query, 2022)

    async def cache_contests(self):
        data = await _query_api()
         



        





async def setup(bot):
    await bot.add_cog(ClistReminder(bot))


