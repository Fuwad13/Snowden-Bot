import discord
from discord.ext import commands
from games_utils import constants as cs
from games_utils import helper
import typing
import json


class Owner(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.bfh = helper.BattleFieldHelper(bot)

	@commands.command(name= '@initdb', hidden = True)
	@commands.is_owner()
	async def _initdb(self, ctx):
		try :
			await self.bot.db.execute(""" CREATE TABLE IF NOT EXISTS battlefield ( p_id bigint PRIMARY KEY, created_at bigint NOT NULL,joinpos serial,opt_status boolean default false, cooldowns json default '{"n_hourly" : 0,"n_daily" : 0,"n_weekly" : 0,"n_monthly" : 0,"n_work" : 0, "n_loot" : 0, "n_attack" : 0, "n_heal" : 0, "n_opt_in_toggle" : 0}', stats json default '{}'); """)

			await self.bot.db.execute(""" CREATE TABLE IF NOT EXISTS inventory (p_id bigint, balance bigint default 500, exp bigint default 100 , hp int default 100, shield int default 0, common json default '{}', rare json default '{}', legendary json default '{}', epic json default '{}', mythic json default '{}', CONSTRAINT fk_p_id FOREIGN KEY (p_id) REFERENCES battlefield(p_id)); """)
		except:
			await ctx.send(f"{cs.EMOJIS['redtick']} There was an unexpected error!")
		


	@commands.group(name = '@db',aliases = ['@psql'], hidden = True, invoke_without_command = True)
	@commands.is_owner()
	async def db(self, ctx):
		await ctx.send("Ok")

	
	@db.command(name = 'fetchval', aliases = ['getval'], hidden = True)
	@commands.is_owner()
	async def _fetchval(self, ctx, query: str, arg: int):
		
		val = await self.bot.db.fetchval(query, arg)
		await ctx.send(val)

	@commands.command(name = '@updateinv', aliases = ['@updinv', '@updateinventory'], hidden = True)
	@commands.is_owner()
	async def updateinv(self, ctx, player : typing.Union[discord.Member, discord.User], *,json_str : str):
		player_id = player.id
		
		items_dict = json.loads(json_str)
		success = await self.bfh.bulk_update_inventory(player_id= player_id, items_dict= items_dict
		)
		if success:
			await ctx.reply(f"{cs.EMOJIS['greentick']}")




	

	


def setup(bot):
	bot.add_cog(Owner(bot))