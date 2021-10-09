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

	async def update_column(self, *,player_id :int, c_name : str, value, add :bool = True ):
		if c_name == 'balance' or c_name == 'exp':
			if add == True:
				val = await self.bot.db.fetchval(""" SELECT $1 FROM snowden_bg WHERE id = $2 ;""", c_name,player_id)
				val = (float(val) if c_name ==  'balance' else int(val)) + value
				await self.bot.db.execute(""" UPDATE snowden_bg SET $1 = $2 WHERE id = $3; """, c_name,val, player_id)

			elif add == False:
				val = await self.bot.db.fetchval(""" SELECT $1 FROM snowden_bg WHERE id = $2 ;""", c_name,player_id)
				val = (float(val) if c_name ==  'balance' else int(val)) - value
				await self.bot.db.execute(""" UPDATE snowden_bg SET $1 = $2 WHERE id = $3; """, c_name,val, player_id)
			return val
		val = await self.bot.db.fetchval("SELECT $1 FROM snowde_bg WHERE id = $2;", c_name, player_id)




	async def update_balance(self,*,player_id, amount, add : bool = True):
		if add == True:
			bal = await self.bot.db.fetchval(""" SELECT balance FROM snowden_bg WHERE id = $1 ;""", player_id)
			bal = float(bal) + amount
			await self.bot.db.execute(""" UPDATE snowden_bg SET balance = $1 WHERE id = $2; """, bal, player_id)

		elif add == False:
			bal = await self.bot.db.fetchval(""" SELECT balance FROM snowden_bg WHERE id = $1 ;""", player_id)
			bal = float(bal) - amount
			await self.bot.db.execute(""" UPDATE snowden_bg SET balance = $1 WHERE id = $2; """, bal, player_id)
		return bal

	async def get_user_inventory(self, player_id : int):
		data = await self.bot.db.fetchrow(""" SELECT * FROM snowden_bg where id = $1;  """, player_id)
		return data

	
	@commands.command(name = 'profile')
	async def _profile(self, ctx, player : typing.Union[discord.User, discord.Member] = None):
		if not player:
			player_id = ctx.author.id
			player = ctx.author
		else:
			player_id = player.id

		flag = await self.check_if_exists(player_id)
		if not flag:
			return await ctx.send(f"{player} don't have any account yet, to create one , run the `start` command first!")
		data = await self.get_user_inventory(player_id)
		embed = discord.Embed(title = f"{player}'s Profile:", description = f"Balance : **${float(data['balance'])}**\nAccount created: <t:{data['created_at']}:f> (<t:{data['created_at']}:R>)\nExperience points : <:exp:896086434946097162> {data['exp']} exp")
		await ctx.send(embed = embed)
	

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
			return await ctx.send(f"{player} don't have any account yet, to create one , run the `start` command first!")
		data = await self.get_user_inventory(player_id)
		balance = data['balance']
		await ctx.send(f"{player}'s balance : **${balance}**")

	@commands.command(name = 'start')
	async def _start(self, ctx):
		user_id = ctx.author.id
		

		flag = await self.check_if_exists(user_id)
		if flag:
			return await ctx.send("**You already have an account, you can keep playing**")
		await self.bot.db.execute(""" INSERT INTO snowden_bg (id, created_at) VALUES ($1, $2); """, user_id, int(ctx.message.created_at.timestamp()))
		embed = discord.Embed(title = "Welcome to Snowden's BattleGround!!", description = f"**Congrats!! {ctx.author}**\nYou got **$2500.00** and <:exp:896086434946097162>**500 exp*** as a reward for creating an account!", color = 0x2F3136)
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
		if amount > 100000 or amount < 500:
			return await ctx.send("Minimum amount of gambling is **$500**\nMaximum amount of gambling is **$100000**")

		view = bs.HeadsOrTails(ctx)

		embed = discord.Embed(title ='Coinflip', description = f"{ctx.author.name}, choose an option in next 15 seconds!", color = 0x2F3136)

		msg = await ctx.send(embed = embed , view = view)
		

		await view.wait()
		if view.value == True:
			won_or_lost = random.randint(0,1)
			if won_or_lost == 1:
				g_exp = 50
				exp = await self.update_column(player_id = ctx.author.id, c_name= 'exp',value= 50)
				bal = await self.update_balance(player_id = ctx.author.id,amount =  amount, add = True)
				
				text = f"\U0001f38a **Congrats** {ctx.author.name},\nThe coin landed on **Heads!** You chose **Heads**, meaning that you've just won **${amount}**!! \n\nYour new balance is **${bal}**\nYou gained <:exp:896086434946097162>**{g_exp} exp**  "
				embed.description = text
				await msg.edit(embed = embed , view = view)

			elif won_or_lost == 0:
				g_exp = 25
				exp = await self.update_column(player_id = ctx.author.id, c_name= 'exp',value= 25)


				bal = await self.update_balance(player_id = ctx.author.id, amount = amount,add = False)
				
				text = f"\U0001f626 **Aw snap,**{ctx.author.name},\nThe coin landed on **Tails** You chose **Heads**, meaning that you've just lost **${amount}**!\n\n Your new balance is **${bal}**\nYou gained <:exp:896086434946097162>**{g_exp} exp** "
				embed.description = text
				await msg.edit(embed = embed , view = view)
		
		elif view.value == False:
			won_or_lost = random.randint(0,1)
			if won_or_lost == 1:
				g_exp = 50
				exp = await self.update_column(player_id = ctx.author.id, c_name= 'exp',value= 50)
				bal = await self.update_balance(player_id = ctx.author.id,amount = amount, add = True)
				
				text = f"\U0001f38a **Congrats** {ctx.author.name},\nThe coin landed on **Tails!** You chose **Tails**, meaning that you've just won **${amount}**!! \n\nYour new balance is **${bal}**\nYou gained <:exp:896086434946097162>**{g_exp} exp**  "
				embed.description = text
				await msg.edit(embed = embed , view = view)

			elif won_or_lost == 0:
				g_exp = 25
				exp = await self.update_column(player_id = ctx.author.id, c_name= 'exp',value= 25)
				bal = await self.update_balance(player_id = ctx.author.id,amount = amount, add =False)
				
				text = f"\U0001f626 **Aw snap,** {ctx.author.name},\nThe coin landed on **Heads** You chose **Tails**, meaning that you've just lost **${amount}**!\n\n Your new balance is **${bal}**\nYou gained <:exp:896086434946097162>**{g_exp} exp**  "
				embed.description = text
				await msg.edit(embed = embed , view = view)
		else:
			embed.description = "Timed out!"
			view.clear_items()
			await msg.edit(embed = embed, view = view)
			
	@_cf.error
	async def _cf_error(self, ctx, error):
		if isinstance(error, commands.CommandOnCooldown):
			await ctx.send(f"You're on cooldown! Retry after `{round(error.retry_after, 2)}` seconds")

def setup(bot):
	bot.add_cog(Games(bot))

