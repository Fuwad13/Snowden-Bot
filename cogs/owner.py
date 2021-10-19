import discord
from discord.ext import commands


class Owner(commands.Cog):
	def __init__(self, bot):
		self.bot = bot


	@commands.command(name = 'dbexecute',aliases = ['dbexec'], hidden = True)
	@commands.is_owner()
	async def dbexec(self, ctx, query :str , *args):
		print('check')
		_id = int(*args)
		resp = await self.bot.db.execute(query, _id)
		await ctx.send(f"Database Query execution done! `{resp}`")


	

	


def setup(bot):
	bot.add_cog(Owner(bot))