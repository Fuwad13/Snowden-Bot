import discord
from discord.ext import commands
from utils.errors import NotStartedPlaying



def has_started():
	async def predicate(ctx):
		flag = False
		player = await ctx.bot.db.fetchval(""" SELECT p_id FROM battlefield WHERE p_id = $1 """, ctx.author.id)
		if player:
			flag = True
			return flag
		else:
			flag = False
			raise NotStartedPlaying(f"You haven't started playing Battlefield yet! run `{ctx.clean_prefix}start` to start playing.")
	return commands.check(predicate)