import discord
from discord.ext import commands
from discord.ext.commands.core import check
from games_utils import constants as cs
from games_utils import helper
import typing
import json


class Owner(commands.Cog):
	"""Owner only cog"""
	def __init__(self, bot):
		self.bot = bot
		self.bfh = helper.BattleFieldHelper(bot)

	@commands.command(name= '/initdb', hidden = True)
	@commands.is_owner()
	async def _initdb(self, ctx):
		try :
			await self.bot.db.execute(""" CREATE TABLE IF NOT EXISTS battlefield ( p_id bigint PRIMARY KEY, created_at bigint NOT NULL,joinpos serial,balance bigint default 500,freeze_status boolean default false,opt_status boolean default false, hp int default 100, sp int default 0, exp bigint default 100, equipments json default '{"armour" : null, "weapon" : null}', cooldowns json default '{"n_hourly" : 0,"n_daily" : 0,"n_weekly" : 0,"n_monthly" : 0,"n_work" : 0, "n_loot" : 0, "n_attack" : 0, "n_heal" : 0, "n_opt_in_toggle" : 0, "n_w_equip" : 0,"n_a_equip" : 0}', common json default '{}', rare json default '{}', legendary json default '{}', epic json default '{}', mythic json default '{}', stats json default '{}',invisibility bigint default 0, voter boolean default false); """)
			await ctx.send(f"{cs.EMOJIS['greentick']} Initiated database table for Battlefield!")


			
		except Exception as e:
			await ctx.send(f"{cs.EMOJIS['redtick']} There was an unexpected error!\n{e}")
		


	@commands.group(name = '/db',aliases = ['/psql'], hidden = True, invoke_without_command = True)
	@commands.is_owner()
	async def db(self, ctx):
		await ctx.send("Ok")

	
	@db.command(name = 'fetchval', aliases = ['getval'], hidden = True)
	@commands.is_owner()
	async def _fetchval(self, ctx, query: str, arg: int):
		
		val = await self.bot.db.fetchval(query, arg)
		await ctx.send(val)

	@commands.command(name = '/updateinv', aliases = ['/updinv', '/updateinventory'], hidden = True)
	@commands.is_owner()
	async def updateinv(self, ctx, player : typing.Union[discord.Member, discord.User], *,json_str : str):
		player_id = player.id
		
		items_dict = json.loads(json_str)
		success = await self.bfh.bulk_update_inventory(player_id= player_id, items_dict= items_dict
		)
		if success:
			await ctx.reply(f"{cs.EMOJIS['greentick']} Successfully updated inventory for {player.name}")

	@commands.group(name = '/set', help = "Set/Update a player's hp/xp/sp or other things", hidden = True, invoke_without_command = True)
	@commands.is_owner()
	async def _set(self,ctx):
		await ctx.send("Set/Update a player's hp , xp , sp or other stuffs!")

	@_set.command(name = "exp", aliases = ['xp'], hidden = True)
	@commands.is_owner()
	async def _setexp(self, ctx, player : typing.Union[discord.Member, discord.User], amount : int):
		player_id = player.id
		r = await self.bot.db.execute("UPDATE battlefield SET exp = $1 where p_id = $2;", amount, player_id)
		await ctx.send(str(r))

	@_set.command(name = "hp", hidden = True)
	@commands.is_owner()
	async def _sethp(self, ctx, player : typing.Union[discord.Member, discord.User], amount : int):
		player_id = player.id
		r = await self.bot.db.execute("UPDATE battlefield SET hp = $1 where p_id = $2;", amount, player_id)
		await ctx.send(str(r))

	@_set.command(name = "sp", aliases = ['shieldpoint', 'shp', 'ap'], hidden = True)
	@commands.is_owner()
	async def _setsp(self, ctx, player : typing.Union[discord.Member, discord.User], amount : int):
		player_id = player.id
		r = await self.bot.db.execute("UPDATE battlefield SET sp = $1 where p_id = $2;", amount, player_id)
		await ctx.send(str(r))

	@commands.command(name = "/cleanup", aliases = ['/clean'],hidden = True )
	@commands.is_owner()
	async def _cleanup(self, ctx, amount : int = 10):
		def is_snowden(message):
			return message.author == self.bot.user

		deleted = await ctx.channel.purge(limit = amount, check = is_snowden, bulk = False)

		await ctx.send(f"**Deleted {len(deleted)} message(s)**", delete_after = 5)

	@commands.command(name= "/blacklist", aliases = ['/bl','/shutlist'],hidden=True,help="Shut some mfs so they can't invoke commands")
	@commands.is_owner()
	async def _blacklist(self, ctx, user : discord.User, *, reason : str = None):
		if reason is None:
			reason = "being a mf"
		self.bot.blacklist[str(user.id)] = reason
		await ctx.send(f"{cs.EMOJIS['greentick']} blacklisted {user} for {reason}")

	@commands.command(name='/forgive', aliases = ['/unblacklist', '/unbl'], hidden = True, help  = "forgive a good person who was once a mf")
	@commands.is_owner()
	async def _unbl(self, ctx, user : discord.User, *, reason : str = None):
		if reason is None:
			reason = "forgave"
		mf = self.bot.blacklist.get(str(user.id))
		if not mf:
			return await ctx.send(f"{user} is not blacklisted.")

		del self.bot.blacklist[str(user.id)]
		await ctx.send(f"{cs.EMOJIS['greentick']} forgave / unblacklisted {user} for {reason}")


def setup(bot):
	bot.add_cog(Owner(bot))