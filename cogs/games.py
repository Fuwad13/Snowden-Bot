import discord
from discord.ext import commands
import asyncpg


class Games(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	
	@commands.command(name = 'start', aliases = ['create'], brief = 'Create an account to start your journey!')
	async def _start(self, ctx):
		await self.bot.db.execute(""" CREATE TABLE IF NOT EXISTS user_accounts (id bigint PRIMARY KEY, created_at bigint NOT NULL, snowflakes_bal bigint DEFAULT 0, inventory text NOT NULL);  """)
		user_id = await self.bot.db.fetchval(""" SELECT id FROM  user_accounts WHERE id = $1  ;""", ctx.author.id)
		if user_id:
			return await ctx.send("You already have an account! You can continue playing")
		else:

			await self.bot.db.execute(""" INSERT INTO user_accounts VALUES ($1, $2,$3, $4)  ;""", ctx.author.id, int(ctx.message.created_at.timestamp()), 0, "test_idklol")
			await ctx.send("Created your account, you can play now")

	@commands.command(name = 'inventory', aliases = ['inv'])
	async def _inv(self, ctx, user : discord.User = None):
		if not user:
			user = ctx.author

		data = await self.bot.db.fetchval(""" SELECT (id, created_at) FROM  user_accounts WHERE id = $1  ;""", ctx.author.id)
		await ctx.send(f"{data}")


def setup(bot):
	bot.add_cog(Games(bot))

