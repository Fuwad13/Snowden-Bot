import discord
from discord import embeds
from discord.ext import commands
import asyncpg
import typing
import random
from utils import buttons_and_selects as bs


class Games(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	async def check_if_exists(self, user_id):
		flag = False
		player = await self.bot.db.fetchval(""" SELECT id FROM snowden_bg WHERE id = $1 """, user_id)
		if player:
			flag = True
		else:
			flag = False
		return flag

	async def update_balance(self,*,player_id, amount, add : bool = True):
		if add == True:
			bal = await self.bot.db.fetchval(""" SELECT balance FROM snowden_bg WHERE id = $1 ;""", player_id)
			bal = bal + amount
			await self.bot.db.execute(""" UPDATE snowden_bg SET balance = $1 WHERE id = $2; """, bal, player_id)

		elif add == False:
			bal = await self.bot.db.fetchval(""" SELECT balance FROM snowden_bg WHERE id = $1 ;""", player_id)
			bal = bal - amount
			await self.bot.db.execute(""" UPDATE snowden_bg SET balance = $1 WHERE id = $2; """, bal, player_id)

	async def get_user_inventory(self, player : typing.Union[discord.User, discord.Member]):
		data = await self.bot.db.fetchrow(""" SELECT * FROM snowden_bg where id = $1;  """, player.id)
		return data

		
	
		

	@commands.command(name = 'start')
	async def _start(self, ctx):
		user_id = ctx.author.id
		await self.bot.db.execute(""" CREATE TABLE IF NOT EXISTS snowden_bg ( id bigint PRIMARY KEY, created_at bigint NOT NULL, balance bigint); """)

		flag = await self.check_if_exists(user_id)
		if flag:
			return await ctx.send("**You already have an account, you can keep playing**")
		await self.bot.db.execute(""" INSERT INTO snowden_bg VALUES ($1, $2, $3); """, user_id, int(ctx.message.created_at.timestamp()), float(1000))
		embed = discord.Embed(title = "Welcome to Snowden's BattleGround!!", description = "**Congrats!!**\nYou got **$1000** as a reward for creating an account!", color = 0x2F3136)
		await ctx.send(embed = embed)

	@commands.command(name = 'coinflip', aliases =[ 'cf', 'coinf'])
	@commands.cooldown(2,10, commands.BucketType.user)
	async def _cf(self, ctx, amount : int = 500):
		flag = await self.check_if_exists(ctx.author.id)
		if not flag:
			return await ctx.send("You don't have any account yet, to create one , run the `start` command first!")
		balance = await self.bot.db.fetchval(""" SELECT balance FROM snowden_bg where id = $1; """, ctx.author.id)
		if balance < amount:
			return await ctx.send("Looks like you don't have enough money to gamble in coinflip!")

		view = bs.HeadOrTail(ctx)

		embed = discord.Embed(title ='Coinflip', description = f"{ctx.author.name}, choose an option in next 15 seconds!", color = 0x2F3136)

		msg = await ctx.send(embed = embed , view = view)
		

		await view.wait()
		if view.value == True:
			won_or_lost = random.randint(0,1)
			if won_or_lost == 1:
				await self.update_balance(player_id = ctx.author.id,amount =  amount, add = True)
				
				text = f"\U0001f38a **Congrats** {ctx.author.name},\nYou just won **${amount}** doing coinflip gambling! "
				embed.description = text
				await msg.edit(embed = embed , view = view)

			elif won_or_lost == 0:
				await self.update_balance(player_id = ctx.author.id, amount = amount,add = False)
				
				text = f"**Aw snap,** {ctx.author.name},\nYou just lost **${amount}** doing coinflip gambling! "
				embed.description = text
				await msg.edit(embed = embed , view = view)
		
		elif view.value == False:
			won_or_lost = random.randint(0,1)
			if won_or_lost == 1:
				await self.update_balance(player_id = ctx.author.id,amount = amount, add = True)
				
				text = f"\U0001f38a **Congrats** {ctx.author.name},\nYou just won **${amount}** doing coinflip gambling! "
				embed.description = text
				await msg.edit(embed = embed , view = view)

			elif won_or_lost == 0:
				await self.update_balance(player_id = ctx.author.id,amount = amount, add =False)
				
				text = f"**Aw snap,** {ctx.author.name},\nYou just lost **${amount}** doing coinflip gambling! "
				embed.description = text
				await msg.edit(embed = embed , view = view)
		else:
			embed.description = "Timed out!"
			await msg.edit(embed = embed, view = view)
			


def setup(bot):
	bot.add_cog(Games(bot))

