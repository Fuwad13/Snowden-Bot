import asyncio
from collections import defaultdict
import datetime as dt
import json
import time

import discord
from discord.ext import commands
import humanize
from main import SnowdenBot
from utils.clist_api import Round, _query_api



# constants
_CONTESTS_PER_PAGE = 5
_CONTEST_PAGINATE_WAIT_TIME = 5 * 60
_FINISHED_CONTESTS_LIMIT = 5
_CONTEST_REFRESH_PERIOD = 10 * 60  # seconds
_GUILD_SETTINGS_BACKUP_PERIOD = 6 * 60 * 60  # seconds

#_TIME_ZONE = environ.get('TIME_ZONE') or 'UTC'
_PYTZ_TIMEZONES_GIST_URL = ('https://gist.github.com/heyalexej/'
                            '8bf688fd67d7199be4a1682b3eec7568')
_WEBSITE_ALLOWED_PATTERNS = defaultdict(list)
_WEBSITE_ALLOWED_PATTERNS['codeforces.com'] = ['']
_WEBSITE_ALLOWED_PATTERNS['codechef.com'] = [
    'lunch', 'cook', 'rated']
_WEBSITE_ALLOWED_PATTERNS['atcoder.jp'] = [
    'abc:', 'arc:', 'agc:', 'grand', 'beginner', 'regular']
_WEBSITE_ALLOWED_PATTERNS['topcoder.com'] = ['srm', 'tco']
_WEBSITE_ALLOWED_PATTERNS['codingcompetitions.withgoogle.com'] = ['']
_WEBSITE_ALLOWED_PATTERNS['facebook.com/hackercup'] = ['']
_WEBSITE_ALLOWED_PATTERNS['codedrills.io'] = ['']

_WEBSITE_DISALLOWED_PATTERNS = defaultdict(list)
_WEBSITE_DISALLOWED_PATTERNS['codeforces.com'] = [
    'wild', 'fools', 'kotlin', 'unrated']
_WEBSITE_DISALLOWED_PATTERNS['codechef.com'] = ['unrated']
_WEBSITE_DISALLOWED_PATTERNS['atcoder.jp'] = []
_WEBSITE_DISALLOWED_PATTERNS['topcoder.com'] = []
_WEBSITE_DISALLOWED_PATTERNS['codingcompetitions.withgoogle.com'] = [
    'registration']
_WEBSITE_DISALLOWED_PATTERNS['facebook.com/hackercup'] = []
_WEBSITE_DISALLOWED_PATTERNS['codedrills.io'] = []

_SUPPORTED_WEBSITES = [
    'codeforces.com',
    'codechef.com',
    'atcoder.jp',
    'topcoder.com',
    'codingcompetitions.withgoogle.com',
    'facebook.com/hackercup',
    'codedrills.io'
]


class ClistReminder(commands.Cog):

    def __init__(self, bot : SnowdenBot):
        self.bot = bot
        self.bot.clist_cog = self

        #clist api stuffs
        
        self.base_url = "https://clist.by/api/v1/contest/"
        self.api_key = "f4caba195a30836df60a2d40d4136fe08243bf3c"
        self.api_username = "fuwad2"
        self.credentials = "/?username=fuwad2&api_key=f4caba195a30836df60a2d40d4136fe08243bf3c"
        self.last_cache_timestamp = 0

        self.contest_cache = None
        self.future_contests = None
        self.running_contests = None
        self.finished_contests = None
        self.task_list = []
        self.start_time_map = defaultdict(list)

        


    
    # not to call
    async def create_table(self):

        query = """ CREATE TABLE IF NOT EXISTS clistdata ( id integer PRIMARY KEY, api_data json default '{}'); """

        await self.bot.db.execute(query)

        query = """ INSERT INTO clistdata (id) VALUES ($1) ;"""

        await self.bot.db.execute(query, 2022)



    async def cache_contests(self):
        current_timestamp = time.time()
        last_cache_timestamp = self.last_cache_timestamp


        if current_timestamp - last_cache_timestamp < 1800:
            # if last cache was less than 30 minutes ago
            return
        data = await _query_api() # list of dicts
        data_dict = {}
        cnt = 0

        for i in data:
            data_dict[cnt] = i
            cnt += 1
        data_json = json.dumps(data_dict)
        query = """ UPDATE clistdata SET api_data = $1 WHERE id = $2; """
        await self.bot.db.execute(query, data_json, 2022)
        self.last_cache_timestamp = current_timestamp
         
    async def generate_contest_cache(self):
        print("Generating contest cache")
        await self.cache_contests()
        query = """ SELECT api_data FROM clistdata WHERE id = $1; """
        data = await self.bot.db.fetchval(query, 2022)
        data_dict : dict= json.loads(data)

        contests = [Round(contest) for k, contest in data_dict.items()]
        self.contest_cache = [
            contest for contest in contests if contest.is_desired(_WEBSITE_ALLOWED_PATTERNS, _WEBSITE_DISALLOWED_PATTERNS)]
        
    
    async def _update_task(self):
        self.bot.logger.info(f'Updating reminder tasks.')
        await self.generate_contest_cache()
        contest_cache = self.contest_cache
        current_time = dt.datetime.utcnow()

        self.future_contests = [
            contest for contest in contest_cache
            if contest.start_time > current_time
        ]
        self.finished_contests = [
            contest for contest in contest_cache
            if contest.start_time +
            contest.duration < current_time
        ]
        self.running_contests = [
            contest for contest in contest_cache
            if contest.start_time <= current_time <=
            contest.start_time + contest.duration
        ]

        self.running_contests.sort(key=lambda contest: contest.start_time)
        self.finished_contests.sort(
            key=lambda contest: contest.start_time +
            contest.duration,
            reverse=True
        )
        self.future_contests.sort(key=lambda contest: contest.start_time)

        self.start_time_map.clear()
        for contest in self.future_contests:
            self.start_time_map[int(contest.start_time.timestamp())].append(contest)
        # Keep most recent _FINISHED_LIMIT
        self.finished_contests = \
            self.finished_contests[:_FINISHED_CONTESTS_LIMIT]
        await self._reschedule_tasks()
        
        await asyncio.sleep(_CONTEST_REFRESH_PERIOD)
        self.bot.loop.create_task(self._update_task())

    async def _reschedule_tasks(self):
        for task in self.task_list:
            task.cancel()
        self.task_list.clear()
        role_id = 1047221079950757918

        channel_id = 1047199249227591791
        channel = self.bot.get_channel(channel_id)
        guild = self.bot.get_guild(874735250842984458)
        role = guild.get_role(role_id)
        before = [600, 7200, 86400]
        for start_time, contests in self.start_time_map.items():
            for before_secs in before:
                task = self.bot.loop.create_task(self._send_reminder_at(channel, role, contests, before_secs, start_time))
                self.task_list.append(task)
                        
                    
                    

    async def _send_reminder_at(self, channel, role, contests, before_secs, start_time):
        send_time = start_time - before_secs
        delay = send_time - dt.datetime.utcnow().timestamp()
        if delay <= 0:
            return
        await asyncio.sleep(delay)

        embed = discord.Embed(title="Contest Reminder", description=f"About to start in {humanize.precisedelta(before_secs)}" ,color=0x2F3136)
        for contest in contests:
            embed.add_field(
                name=f"**{contest.name}**", 
                value=f"Start time: <t:{start_time}:F> | <t:{start_time}:R>\nDuration: {humanize.precisedelta(contest.duration_in_seconds)}\n[link]({contest.url} \"Link to contest\")")
        await channel.send(f"{role.mention}", embed=embed)


    @commands.group(name="clist",help="Contest listing commands" ,invoke_without_command=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def clist(self, ctx : commands.Context):
        await ctx.send_help(ctx.command)

    @clist.command(name="finished",help="List recently finished contests")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _finished(self, ctx : commands.Context):
        embed = discord.Embed(title="Recently finished contests", color=0x2F3136)
        for contest in self.finished_contests:
            embed.add_field(
                name=f"**{contest.name}**", 
                value=f"Start time: <t:{int(contest.start_time.timestamp())}:F> | <t:{int(contest.start_time.timestamp())}:R>\nDuration: {humanize.precisedelta(contest.duration_in_seconds)}\n[link]({contest.url} \"Link to contest\")", inline=False)

        await ctx.send(embed=embed)
    
    @clist.command(name="active",help="List currently running contests")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _active(self, ctx : commands.Context):
        embed = discord.Embed(title="Currently running contests", color=0x2F3136)
        for contest in self.running_contests:
            embed.add_field(
                name=f"**{contest.name}**", 
                value=f"Start time: <t:{int(contest.start_time.timestamp())}:F> | <t:{int(contest.start_time.timestamp())}:R>\nDuration: {humanize.precisedelta(contest.duration_in_seconds)}\n[link]({contest.url} \"Link to contest\")", inline=False)
        await ctx.send(embed=embed)

    @clist.command(name="future",aliases = ["upcoming"],help="List upcoming contests")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _future(self, ctx : commands.Context):
        embed = discord.Embed(title="Upcoming contests", color=0x2F3136)
        for contest in self.future_contests[:5]:
            embed.add_field(
                name=f"**{contest.name}**", 
                value=f"Start time: <t:{int(contest.start_time.timestamp())}:F> | <t:{int(contest.start_time.timestamp())}:R>\nDuration: {humanize.precisedelta(contest.duration_in_seconds)}\n[link]({contest.url} \"Link to contest\")", inline=False)
        await ctx.send(embed=embed)

            
        




        





async def setup(bot):
    await bot.add_cog(ClistReminder(bot))


