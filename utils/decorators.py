import discord
from discord.ext import commands
from utils.errors import NotStartedPlaying, NotOptedIn



def has_started():
	async def predicate(ctx):
		flag = False
		player = await ctx.bot.db.fetchval(""" SELECT p_id FROM battlefield WHERE p_id = $1 """, ctx.author.id)
		if player:
			flag = True
			return flag
		else:
			flag = False
			raise NotStartedPlaying(f"{ctx.author} you haven't started playing Battlefield yet, run `{ctx.clean_prefix}start` to start playing!")
	return commands.check(predicate)


def is_opted():
	async def predicate(ctx):
		status : bool= await ctx.bot.db.fetchval(""" SELECT opt_status FROM battlefield where p_id = $1; """,ctx.author.id)
		if status:
			return True
		else:
			raise NotOptedIn(f"**You can't use this command if you are not opted in!**\nRun the `{ctx.clean_prefix}opt` to toggle your opt status.")

	return commands.check(predicate)

