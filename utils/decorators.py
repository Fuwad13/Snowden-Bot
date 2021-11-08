import discord
from discord.ext import commands
from utils.errors import NotStartedPlaying, NotOptedIn, NoWeaponEquipped, NotEnoughAmmo
import json
from games_utils.items import ALL_ITEMS


def has_started():
	async def predicate(ctx):
		
		player = await ctx.bot.db.fetchval(""" SELECT p_id FROM battlefield WHERE p_id = $1 """, ctx.author.id)
		if player:
			return True
		else:
			raise NotStartedPlaying(f"**{ctx.author}**, you haven't started playing Battlefield yet, run `{ctx.clean_prefix}start` to start playing!")
	return commands.check(predicate)

def has_ref_started():
	async def predicate(ctx):
		if ctx.message.reference:
			p_id = ctx.message.reference.resolved.author.id
			player = await ctx.bot.db.fetchval(""" SELECT p_id FROM battlefield WHERE p_id = $1 """, p_id)
			if player:
			
				return True
			else:
				
				raise NotStartedPlaying(f"**{ctx.message.reference.resolved.author}** haven't started playing Battlefield yet,ask him to run `{ctx.clean_prefix}start` to start playing!")
		else:
			
			player = await ctx.bot.db.fetchval(""" SELECT p_id FROM battlefield WHERE p_id = $1 """, ctx.author.id)
			if player:
				return True
			else:
				raise NotStartedPlaying(f"**{ctx.author}**, you haven't started playing Battlefield yet, run `{ctx.clean_prefix}start` to start playing!")
		
		
	return commands.check(predicate)

def is_opted():
	async def predicate(ctx):
		status : bool= await ctx.bot.db.fetchval(""" SELECT opt_status FROM battlefield where p_id = $1; """,ctx.author.id)
		if status == True:
			return True
		elif status == False:
			raise NotOptedIn(f"**{ctx.author}**, You can't use this command if you are not opted in!\nRun the `{ctx.clean_prefix}opt` to toggle your opt status.")
		else:
			raise NotStartedPlaying(f"**{ctx.author}**, you haven't started playing Battlefield yet, run `{ctx.clean_prefix}start` to start playing!")

	return commands.check(predicate)

def has_equipped_weapon():
	async def predicate(ctx):
		rec = await ctx.bot.db.fetchrow(""" SELECT * FROM battlefield where p_id = $1;""", ctx.author.id)
		try:

			eq_dict = json.loads(rec['equipments'])
		except TypeError:
			raise NotStartedPlaying(f"**{ctx.author}**, you haven't started playing Battlefield yet, run `{ctx.clean_prefix}start` to start playing!")
			
		weapon = eq_dict['weapon']
		if not weapon:
			raise NoWeaponEquipped(f"You haven't equipped any weapon yet to use for attacking. use `{ctx.clean_prefix}equip <weapon_name>` to equip a weapon.")

		else:
			ammo : str = ALL_ITEMS[str(weapon)]['ammo']
			if not ammo:
				return True
			ammo_rarity : str= ALL_ITEMS[ammo]['rarity']
			c_dict = json.loads(rec[ammo_rarity])
			count = 0
			try:
				if c_dict[ammo]:
					count : int = c_dict[ammo]

			except KeyError:
				count = 0
			if count <= 0:
				raise NotEnoughAmmo(f"You don't have enough ammo (`{ammo}`) for your equipped weapon to use.You can get them by opening chests or trading with other players.")
			else:
				return True

	return commands.check(predicate)

