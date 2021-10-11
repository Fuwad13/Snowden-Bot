import discord
from discord import embeds
from discord.ext import commands
import asyncpg
import typing
import random

from discord.ext.commands.cooldowns import Cooldown
from utils import buttons_and_selects as bs
from games_utils import constants as cs 
import json
import time
import humanize


class Games(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	# helper/utility functions

	async def check_if_exists(self, user_id):
		flag = False
		player = await self.bot.db.fetchval(""" SELECT id FROM snowden_bg WHERE id = $1 """, user_id)
		if player:
			flag = True
		else:
			flag = False
		return flag

	async def update_exp(self, *,player_id :int, amount, add :bool = True ):
		if add == True:
			c_exp = await self.bot.db.fetchval(""" SELECT exp FROM snowden_bg WHERE id = $1 ;""", player_id)
			n_exp = int(c_exp) + amount
			await self.bot.db.execute(""" UPDATE snowden_bg SET exp = $1 WHERE id = $2; """, n_exp, player_id)

		elif add == False:
			c_exp = await self.bot.db.fetchval(""" SELECT exp FROM snowden_bg WHERE id = $1 ;""", player_id)
			n_exp = int(c_exp) - amount
			await self.bot.db.execute(""" UPDATE snowden_bg SET exp = $1 WHERE id = $2; """, n_exp, player_id)
		return c_exp, n_exp

	def get_level(self, exp : int):
		level = 0
		for l, e in cs.EXP_LEVELS.items():

			if exp >= e:
				level +=1
				continue
			else:
				return level

	def level_up_check(self, c_exp: int, n_exp: int):
		c_lvl = self.get_level(c_exp)
		n_lvl = self.get_level(n_exp)
		if n_lvl>c_lvl:
			return True
		return False

	async def get_cooldown_data(self, player_id : int, command_name : str = None):
		if not command_name:
			cd_data = await self.bot.db.fetchval(""" SELECT cooldowns FROM snowden_bg WHERE id = $1; """, player_id)
			return json.loads(cd_data)
		cd_data = await self.bot.db.fetchval(""" SELECT cooldowns FROM snowden_bg WHERE id = $1; """, player_id)
		cd_dict = json.loads(cd_data)
		return cd_dict[f'n_{command_name}']
		

	async def update_cooldowns(self, player_id : int, command_name : str ):
		cd_data = await self.bot.db.fetchval(""" SELECT cooldowns FROM snowden_bg WHERE id = $1; """, player_id)
		cd_dict = json.loads(cd_data)
		cd_dict[f'n_{command_name}'] = int(time.time()) + cs.COOLDOWNS[f'{command_name}']
		cd_json = json.dumps(cd_dict)
		await self.bot.db.execute(""" UPDATE snowden_bg SET cooldowns = $1 WHERE id = $2; """, cd_json, player_id)


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


	# commands....

	@commands.command(name = 'profile')
	async def _profile(self, ctx, player : typing.Union[discord.User, discord.Member] = None):
		if not player:
			player_id = ctx.author.id
			player = ctx.author
		else:
			player_id = player.id

		flag = await self.check_if_exists(player_id)
		if not flag:
			return await ctx.send(f"**{player}** don't have any account yet, to create one , run the `{ctx.clean_prefix}start` command first!")
		data = await self.get_user_inventory(player_id)
		embed = discord.Embed(title = f"{player}'s Profile:", description = f"\U0001f3e6 Balance : **${float(data['balance'])}**\n<:exp:896086434946097162> Experience points : **{data['exp']}** EXP\n\U0001f4c8 Level : **{self.get_level(data['exp'])}**\nAccount created: <t:{data['created_at']}:f>")
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
			return await ctx.send(f"**{player}** doesn't have any account yet, to create one , run the `{ctx.clean_prefix}start` command first!")
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
		embed = discord.Embed(title = "Welcome to Snowden's BattleGround!!", description = f"**Congrats!! {ctx.author}**\nYou got **$2000.00** and <:exp:896086434946097162>**500 exp** as a reward for creating an account!", color = 0x2F3136)
		await ctx.send(embed = embed)

	@commands.command(name = 'coinflip', aliases =[ 'cf', 'coinf'])
	@commands.cooldown(2,10, commands.BucketType.user)
	async def _cf(self, ctx, amount : int = 500):
		flag = await self.check_if_exists(ctx.author.id)
		if not flag:
			return await ctx.send(f"Hey **{ctx.author}**, you don't have an account yet. To create one, run the `{ctx.clean_prefix}start` command! Thanks ")
		balance = await self.bot.db.fetchval(""" SELECT balance FROM snowden_bg where id = $1; """, ctx.author.id)
		if balance < amount:
			return await ctx.send("Looks like you don't have enough money to gamble in coinflip!")
		if amount > 100000 or amount < 500:
			return await ctx.send("Minimum amount of gambling is **$500**\nMaximum amount of gambling is **$100000**")

		view = bs.HeadsOrTails(ctx)

		embed = discord.Embed(title =f'Coinflip- ${amount}', description = f"{ctx.author.name}, choose an option in next 15 seconds!", color = 0x2F3136)

		msg = await ctx.send(embed = embed , view = view)
		

		await view.wait()
		if view.value == True:
			won_or_lost = random.randint(0,1)
			if won_or_lost == 1:
				g_exp = 50
				c_exp, n_exp = await self.update_exp(player_id = ctx.author.id,amount= 50)
				bal = await self.update_balance(player_id = ctx.author.id,amount =  amount, add = True)
				
				c_lvl = self.get_level(c_exp)
				lvl_up = self.level_up_check(c_exp, n_exp)

				text = f"\U0001f38a **Congrats** {ctx.author.name},\nThe coin landed on **Heads!** You chose **Heads**, meaning that you've just won **${amount}**!! \n\nYour new balance is **${bal}**\nYou gained <:exp:896086434946097162>**{g_exp} exp from this coinflip**"
				if lvl_up:
					text+=f"\n\U0001f389 You levelled up! `({c_lvl} -> {c_lvl+1})` and gained **$1000**"
					await self.update_balance(player_id = ctx.author.id,amount =  1000, add = True)
				embed.description = text
				await msg.edit(embed = embed , view = view)

			elif won_or_lost == 0:
				g_exp = 25
				c_exp, n_exp = await self.update_exp(player_id = ctx.author.id,amount= 25)

				c_lvl = self.get_level(c_exp)
				lvl_up = self.level_up_check(c_exp, n_exp)

				bal = await self.update_balance(player_id = ctx.author.id, amount = amount,add = False)
				
				text = f"\U0001f626 **Aw snap,**{ctx.author.name},\nThe coin landed on **Tails** You chose **Heads**, meaning that you've just lost **${amount}**!\n\nYour new balance is **${bal}**\nYou gained <:exp:896086434946097162>**{g_exp} exp from this coinflip** "
				if lvl_up:
					text+=f"\n\U0001f389 You levelled up! `({c_lvl} -> {c_lvl+1})` and gained **$1000**"
					await self.update_balance(player_id = ctx.author.id,amount =  1000, add = True)
				embed.description = text
				await msg.edit(embed = embed , view = view)
		
		elif view.value == False:
			won_or_lost = random.randint(0,1)
			if won_or_lost == 1:
				g_exp = 50
				c_exp, n_exp = await self.update_exp(player_id = ctx.author.id,amount= 50)
				bal = await self.update_balance(player_id = ctx.author.id,amount = amount, add = True)
				
				c_lvl = self.get_level(c_exp)
				lvl_up = self.level_up_check(c_exp, n_exp)

				text = f"\U0001f38a **Congrats** {ctx.author.name},\nThe coin landed on **Tails!** You chose **Tails**, meaning that you've just won **${amount}**!! \n\nYour new balance is **${bal}**\nYou gained <:exp:896086434946097162>**{g_exp} exp from this coinflip**  "
				if lvl_up:
					text+=f"\n\U0001f389 You levelled up! `({c_lvl} -> {c_lvl+1})` and gained **$1000**"
					await self.update_balance(player_id = ctx.author.id,amount =  1000, add = True)
				embed.description = text
				await msg.edit(embed = embed , view = view)

			elif won_or_lost == 0:
				g_exp = 25
				c_exp, n_exp = await self.update_exp(player_id = ctx.author.id,amount= 25)
				bal = await self.update_balance(player_id = ctx.author.id,amount = amount, add =False)
				
				c_lvl = self.get_level(c_exp)
				lvl_up = self.level_up_check(c_exp, n_exp)


				text = f"\U0001f626 **Aw snap,** {ctx.author.name},\nThe coin landed on **Heads** You chose **Tails**, meaning that you've just lost **${amount}**!\n\nYour new balance is **${bal}**\nYou gained <:exp:896086434946097162>**{g_exp} exp in this coinflip**  "
				if lvl_up:
					text+=f"\n\U0001f389 You levelled up! `({c_lvl} -> {c_lvl+1})` and gained **$1000**"
					await self.update_balance(player_id = ctx.author.id,amount =  1000, add = True)
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

	@commands.command(name = 'daily', aliases = ['d'])
	async def _daily(self, ctx):
		flag = await self.check_if_exists(ctx.author.id)
		if not flag:
			return await ctx.send(f"Hey **{ctx.author}**, you don't have an account yet. To create one, run the `{ctx.clean_prefix}start` command! Thanks ")
		#check for cooldown
		current_time = int(time.time())
		cd = await self.get_cooldown_data(ctx.author.id, 'daily')
		if current_time < int(cd):
			return await ctx.send(f"{ctx.author.mention} **You can get the daily rewards again in** `{humanize.precisedelta(cd - current_time)}`")
		reward = random.randint(2000, 4000)
		n_bal = await self.update_balance(player_id = ctx.author.id, amount = reward, add = True)
		await self.update_cooldowns(ctx.author.id, 'daily')
		c_exp, n_exp = await self.update_exp(player_id = ctx.author.id,amount= random.randint(250, 500))
		c_lvl = self.get_level(c_exp)
		lvl_up = self.level_up_check(c_exp, n_exp)
		text = f"{ctx.author.mention} , You got **${reward}** and <:exp:896086434946097162>**{n_exp-c_exp} EXP **as your daily check-in reward!\nYour new balace is **${n_bal}**"
		if lvl_up:
			text += f"\n\n\U0001f389 Congrats! You levelled up! `({c_lvl} -> {c_lvl+1})` and gained **$1000**"
			await self.update_balance(player_id = ctx.author.id,amount =  1000, add = True)
		await ctx.send(text)

	@commands.command(name = 'hourly', aliases = ['h'])
	async def _hourly(self, ctx):
		flag = await self.check_if_exists(ctx.author.id)
		if not flag:
			return await ctx.send(f"Hey **{ctx.author}**, you don't have an account yet. To create one, run the `{ctx.clean_prefix}start` command! Thanks ")
		#check for cooldown
		current_time = int(time.time())
		cd = await self.get_cooldown_data(ctx.author.id, 'hourly')
		if current_time < int(cd):
			return await ctx.send(f"{ctx.author.mention} **You can get hourly rewards again in** `{humanize.precisedelta(cd - current_time)}`")
		reward = random.randint(500,1500)
		n_bal = await self.update_balance(player_id = ctx.author.id, amount = reward, add = True)
		await self.update_cooldowns(ctx.author.id, 'hourly')
		c_exp, n_exp = await self.update_exp(player_id = ctx.author.id,amount= random.randint(100, 200))
		c_lvl = self.get_level(c_exp)
		lvl_up = self.level_up_check(c_exp, n_exp)
		text = f"{ctx.author.mention} , You got **${reward}** and <:exp:896086434946097162>**{n_exp-c_exp} EXP **as your hourly rewards!\nYour new balace is **${n_bal}**"
		if lvl_up:
			text += f"\n\n\U0001f389 Congrats! You levelled up! `({c_lvl} -> {c_lvl+1})` and gained **$1000**"
			await self.update_balance(player_id = ctx.author.id,amount =  1000, add = True)
		await ctx.send(text)

	@commands.command(name = 'weekly', aliases = ['w'])
	async def _weekly(self, ctx):
		flag = await self.check_if_exists(ctx.author.id)
		if not flag:
			return await ctx.send(f"Hey **{ctx.author}**, you don't have an account yet. To create one, run the `{ctx.clean_prefix}start` command! Thanks ")
		#check for cooldown
		current_time = int(time.time())
		cd = await self.get_cooldown_data(ctx.author.id, 'weekly')
		if current_time < int(cd):
			return await ctx.send(f"{ctx.author.mention} **You can get the weekly rewards again in** `{humanize.precisedelta(cd - current_time)}`")
		reward = random.randint(5000, 10000)
		n_bal = await self.update_balance(player_id = ctx.author.id, amount = reward, add = True)
		await self.update_cooldowns(ctx.author.id, 'weekly')
		c_exp, n_exp = await self.update_exp(player_id = ctx.author.id,amount= random.randint(1000, 1500))
		c_lvl = self.get_level(c_exp)
		lvl_up = self.level_up_check(c_exp, n_exp)
		text = f"{ctx.author.mention} , You got **${reward}** and <:exp:896086434946097162>**{n_exp-c_exp} EXP **as your weekly check-in reward!\nYour new balace is **${n_bal}**"
		if lvl_up:
			text += f"\n\n\U0001f389 Congrats! You levelled up! `({c_lvl} -> {c_lvl+1})` and gained **$1000**"
			await self.update_balance(player_id = ctx.author.id,amount =  1000, add = True)
		await ctx.send(text)

	@commands.command(name = 'monthly', aliases = ['mon', 'm'])
	async def _monthly(self, ctx):
		flag = await self.check_if_exists(ctx.author.id)
		if not flag:
			return await ctx.send(f"Hey **{ctx.author}**, you don't have an account yet. To create one, run the `{ctx.clean_prefix}start` command! Thanks ")
		#check for cooldown
		current_time = int(time.time())
		cd = await self.get_cooldown_data(ctx.author.id, 'monthly')
		if current_time < int(cd):
			return await ctx.send(f"{ctx.author.mention} **You can get the monthly rewards again in** `{humanize.precisedelta(cd - current_time)}`")
		reward = random.randint(20000, 30000)
		n_bal = await self.update_balance(player_id = ctx.author.id, amount = reward, add = True)
		await self.update_cooldowns(ctx.author.id, 'monthly')
		c_exp, n_exp = await self.update_exp(player_id = ctx.author.id,amount= random.randint(2000, 3500))
		c_lvl = self.get_level(c_exp)
		lvl_up = self.level_up_check(c_exp, n_exp)
		text = f"{ctx.author.mention} , You got **${reward}** and <:exp:896086434946097162>**{n_exp-c_exp} EXP **as your monthly check-in reward!\nYour new balace is **${n_bal}**"
		if lvl_up:
			text += f"\n\n\U0001f389 Congrats! You levelled up! `({c_lvl} -> {c_lvl+1})` and gained **$1000**"
			await self.update_balance(player_id = ctx.author.id,amount =  1000, add = True)
		await ctx.send(text)

	@commands.command(name = 'work', aliases = ['job', 'j'])
	async def work(self, ctx):
		flag = await self.check_if_exists(ctx.author.id)
		if not flag:
			return await ctx.send(f"Hey **{ctx.author}**, you don't have an account yet. To create one, run the `{ctx.clean_prefix}start` command! Thanks ")
		#check for cooldown
		current_time = int(time.time())
		cd = await self.get_cooldown_data(ctx.author.id, 'work')
		if current_time < int(cd):
			return await ctx.send(f"{ctx.author.mention} **You can get the monthly rewards again in** `{humanize.precisedelta(cd - current_time)}`")
		reward = random.randint(1000, 1500)
		n_bal = await self.update_balance(player_id = ctx.author.id, amount = reward, add = True)
		await self.update_cooldowns(ctx.author.id, 'work')
		c_exp, n_exp = await self.update_exp(player_id = ctx.author.id,amount= random.randint(150, 300))
		c_lvl = self.get_level(c_exp)
		lvl_up = self.level_up_check(c_exp, n_exp)
		text = f"{ctx.author.mention} , You earned **${reward}** and <:exp:896086434946097162>**{n_exp-c_exp} EXP **by working as a programmer(this is just a test, more things will be added soon)!\nYour new balace is **${n_bal}**"
		if lvl_up:
			text += f"\n\n\U0001f389 Congrats! You levelled up! `({c_lvl} -> {c_lvl+1})` and gained **$1000**"
			await self.update_balance(player_id = ctx.author.id,amount =  1000, add = True)
		await ctx.send(text)

	@commands.command(name = 'cooldowns', aliases = [ 'cooldown', 'cd'])
	@commands.cooldown(1, 10, type = commands.BucketType.user)
	async def _cooldowns(self, ctx, command: commands.Command = None):
		flag = await self.check_if_exists(ctx.author.id)
		if not flag:
			return await ctx.send(f"Hey **{ctx.author}**, you don't have an account yet. To create one, run the `{ctx.clean_prefix}start` command! Thanks ")
		embed = discord.Embed(title = f"Command Cooldowns for {ctx.author}:", color = 0x2F3136, timestamp = ctx.message.created_at)
		embed.set_author(icon_url=ctx.author.display_avatar.with_static_format('png'), name = f"{ctx.author.name}")


		if command:

			if not command in self.get_commands():
				return await ctx.send('This command is not a games category command!')

			cd = self.get_cooldown_data(ctx.author.id, str(command.name))
			current_time = int(time.time())
			if cd <= current_time:
				embed.description= f"`{ctx.clean_prefix}{command.name} :` **Available to run now!**"
				return await ctx.send(embed = embed)

			embed.description = f"`{ctx.clean_prefix}{command.name} :` **{humanize.precisedelta(cd - current_time)}** remaining to use again!"
			return await ctx.send(embed= embed)

				


def setup(bot):
	bot.add_cog(Games(bot))

