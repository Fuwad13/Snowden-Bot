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
		return bal

	async def get_user_inventory(self, player_id : int):
		data = await self.bot.db.fetchrow(""" SELECT * FROM snowden_bg where id = $1;  """, player_id)
		return data

	

	@commands.command(name = 'balance', aliases = ['bal', 'wallet'])
	@commands.guild_only()
	async def _bal(self, ctx, player: typing.Union[discord.User, discord.Member] = None):
		if not player:
			player_id = ctx.author.id
			player = ctx.author
		else:
			player_id = player.id

		flag = await self.check_if_exists(player_id)
		if not flag:
			return await ctx.send("You don't have any account yet, to create one , run the `start` command first!")
		data = await self.get_user_inventory(player_id)
		balance = data['balance']
		await ctx.send(f"{player}'s balance : **${balance}**")

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
		if amount > 100000:
			return await ctx.send("Maximum amount of gambling is **$100000**")

		view = bs.HeadsOrTails(ctx)

		embed = discord.Embed(title ='Coinflip', description = f"{ctx.author.name}, choose an option in next 15 seconds!", color = 0x2F3136)

		msg = await ctx.send(embed = embed , view = view)
		

		await view.wait()
		if view.value == True:
			won_or_lost = random.randint(0,1)
			if won_or_lost == 1:
				bal = await self.update_balance(player_id = ctx.author.id,amount =  amount, add = True)
				
				text = f"\U0001f38a **Congrats** {ctx.author.name},\nThe coin landed on **Heads!** You chose **Heads**, meaning that you've just won **${amount}**!! \n\nYour new balance is **${bal}** "
				embed.description = text
				await msg.edit(embed = embed , view = view)

			elif won_or_lost == 0:
				bal = await self.update_balance(player_id = ctx.author.id, amount = amount,add = False)
				
				text = f"\U0001f626 **\U0001f626 Aw snap,** {ctx.author.name},\nThe coin landed on **Tails** You chose **Heads**, meaning that you've just lost **${amount}**!\n\n Your new balance is **${bal}** "
				embed.description = text
				await msg.edit(embed = embed , view = view)
		
		elif view.value == False:
			won_or_lost = random.randint(0,1)
			if won_or_lost == 1:
				bal = await self.update_balance(player_id = ctx.author.id,amount = amount, add = True)
				
				text = f"\U0001f38a **Congrats** {ctx.author.name},\nThe coin landed on **Tails!** You chose **Tails**, meaning that you've just won **${amount}**!! \n\nYour new balance is **${bal}** "
				embed.description = text
				await msg.edit(embed = embed , view = view)

			elif won_or_lost == 0:
				bal = await self.update_balance(player_id = ctx.author.id,amount = amount, add =False)
				
				text = f"\U0001f626 **\U0001f626 Aw snap,** {ctx.author.name},\nThe coin landed on **Heads** You chose **Tails**, meaning that you've just lost **${amount}**!\n\n Your new balance is **${bal}** "
				embed.description = text
				await msg.edit(embed = embed , view = view)
		else:
			embed.description = "Timed out!"
			await msg.edit(embed = embed, view = view)
			
	@_cf.error
	async def _cf_error(self, ctx, error):
		if isinstance(error, commands.CommandOnCooldown):
			await ctx.send(f"You're on cooldown! Retry after `{round(error.retry_after, 2)}` seconds")

def setup(bot):
	bot.add_cog(Games(bot))

