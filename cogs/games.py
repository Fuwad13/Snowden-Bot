import discord
from discord import embeds
from discord import player
from discord.ext import commands
import asyncpg
import typing
import random

from discord.ext.commands.cooldowns import BucketType, Cooldown
from utils import buttons_and_selects as bs 
import json
import time
import humanize
from games_utils import helper
from games_utils.items import ALL_ITEMS
import games_utils.constants as cs

class BattleField(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.bfh = helper.BattleFieldHelper(bot)


	@commands.command(name = 'start', aliases = ['enter', 'init'], brief = "Creates an account for playing in Battlefield!", help = "Enter the `Snowden's BattleField` by creating an account!")
	@commands.guild_only()
	@commands.cooldown(1,10, type= BucketType.user)
	async def _start(self, ctx):
		player_id = ctx.author.id
		flag = await self.bfh.check_if_exists(player_id)
		if flag:
			return await ctx.send("**You already have an account, you can keep playing!**")
		await self.bot.db.execute(""" INSERT INTO battlefield (p_id, created_at) VALUES ($1, $2); """, player_id, int(ctx.message.created_at.timestamp()))
		await self.bot.db.execute(""" INSERT INTO inventory (p_id, common, rare) VALUES ($1, $2, $3); """, player_id, '{"police_vest_level_1" : 1}','{"rare_chest" : 1, "pain_killer" : 1 }')

		embed = discord.Embed(title = f"Hey {ctx.author.name}, \U0001f44b Welcome to Snowden's BattleField!!", description = f"You got **$500** and <:exp:896086434946097162>**100 EXP** as a reward for entering the battlefield!\nYou also got:\n• {cs.CHESTS_EMOJIS['rare']}`rare_chest x1`\n• {ALL_ITEMS['police_vest_level_1']['emoji']}`police_vest_level_1 x1`\n• {ALL_ITEMS['pain_killer']['emoji']}`pain_killer x1`\nHope you enjoy!", color = 0x2F3136)
		await ctx.reply(embed = embed)

	@commands.command(name= 'inventory', aliases = ['inv'], brief= "Shows player inventory", help = "Shows player inventory, only if the user has an account.")
	@commands.cooldown(1,5, type= BucketType.user)
	async def _inventory(self, ctx, player : typing.Union[discord.Member, discord.User] = None):
		if player is None:
			if ctx.message.reference:
				player = ctx.message.reference.resolved.author
			else:
				player = ctx.author
		player_id = player.id
		flag = await self.bfh.check_if_exists(player_id)
		if not flag:
			return await ctx.send(f"{player} hasn't started playing Battlefield yet, run `{ctx.clean_prefix}start` to start playing!")
		t1, t2 = await self.bfh.get_player_data(player_id)
		inv_value = self.bfh.get_inventory_value(t2)

		embed = discord.Embed(title = f"**__{player}'s Inventory__**",color = 0x2F3136)
		text = f"\U0001f3e6 **Balance**: ${t2['balance']}\n\U0001f4bc **Inv. value**: ${inv_value}\n\U00002728 **Player value**: ${t2['balance']+inv_value}\n\U0001f4c8 **Level**: {self.bfh.get_level(t2['exp'])}\n\U00002694 **Opt in status**: {cs.EMOJIS['toggle_on'] if t1['opt_status'] else cs.EMOJIS['toggle_off']}\n"
		embed.add_field(name='\U0001f4cb __Status/profile__', value=text)
		embed.add_field(name="\U00002764 __Health__", value=f"soon")
		embed.add_field(name="\U0001f6e1 __Shield__", value="soon")

		inv_items = self.bfh.get_inventory_items_str(t2)
		for r in inv_items.keys():
			if inv_items[r]:
				embed.add_field(name=f"{cs.RARITY[r].upper()}", value= inv_items[r])

		await ctx.send(embed= embed)


	@commands.command(name = 'items', aliases = ['item'], brief = "Gives you information about any game item(s)", help = "Gives you information about any game item(s). run `items [item_name]` to get information about a specific item.")
	@commands.cooldown(1,3, BucketType.user)
	async def _items(self, ctx, item_name : str = None):
		if not item_name:
			item_list = []
			for item in ALL_ITEMS.keys():
				pass

	@commands.command(name= 'opt', aliases = ['optin', 'optout', 'toggleopt'], help= "Toggle your `opt` status if available. You can't toggle your `opt` status if you are on cooldown!")
	@commands.cooldown(1,2,BucketType.user)
	async def opt(self, ctx):
		player_id = ctx.author.id
		flag = await self.bfh.check_if_exists(player_id)
		if not flag:
			return await ctx.send(f"{ctx.author} you haven't started playing Battlefield yet, run `{ctx.clean_prefix}start` to start playing!")
		opted_in = await self.bfh.get_opt_status(player_id)
		n_opt : int= await self.bfh.get_cooldown_data(player_id,'opt_in_toggle')
		c_opt = self.bfh.can_opt_out(n_opt)

		embed = discord.Embed(title=f"{cs.EMOJIS['toggle_on'] if opted_in else cs.EMOJIS['toggle_off']} {ctx.author}'s opt in status:",color = 0x2F3136)
		text =f"You're currently {'**Opted in**' if opted_in else '**Opted out**'}!\n"
		if not c_opt:
			text+=f"Seems like you are on cooldown! You need to wait `{humanize.precisedelta(n_opt-int(time.time()))}` before you can toggle your `opt status`"
			embed.description= text
			return await ctx.send(f"{ctx.author.mention} ->", embed = embed)
		text+=f"If you want to toggle your `opt status` then press `Confirm` or else press `Cancel` to cancel in the next **30s**!"
		embed.description = text
		view = bs.ConfirmOrCancel(ctx, timeout=30)
		view.msg = await ctx.send(f"{ctx.author.mention} ->", embed = embed, view = view)
		await view.wait()
		view.clear_items()
		if view.value == True:
			ch = await self.bfh.set_opt_status(player_id, not opted_in)
			if ch:
				await self.bfh.update_cooldowns(player_id, 'opt_in_toggle')
			embed.description+=f"\n{cs.EMOJIS['toggle_on'] if ch else cs.EMOJIS['toggle_off']} You've successfully toggled your `opt status`"
			await view.msg.edit(embed = embed, view = view)

		elif view.value == False:
			embed.description+=f"\n{cs.EMOJIS['redtick']} You chose to stay {'**Opted in**' if opted_in else '**Opted out**'}"
			await view.msg.edit(embed = embed, view = view)

		elif view.value == None:
			embed.description+=f"\n:warning: You took too long to respond!"
			await view.msg.edit(embed = embed, view = view)	

	@commands.command(name = 'coinflip', aliases =[ 'cf', 'coinf'], help = "Gamble on coinflip! Choose your option and see if your lucky!")
	@commands.cooldown(2,10, commands.BucketType.user)
	async def _cf(self, ctx, amount : int = 50):
		flag = await self.bfh.check_if_exists(ctx.author.id)
		if not flag:
			return await ctx.send(f"{ctx.author.mention},you haven't started playing Battlefield yet, run `{ctx.clean_prefix}start` to start playing!")
		balance = await self.bot.db.fetchval(""" SELECT balance FROM inventory where p_id = $1; """, ctx.author.id)
		if balance < amount:
			return await ctx.send("Looks like you don't have enough money to gamble on coinflip!")
		if amount > 10000 or amount < 50:
			return await ctx.send("Minimum amount of gambling is **$50** and Maximum amount of gambling is **$10000**")

		view = bs.HeadsOrTails(ctx)

		embed = discord.Embed(title =f'Coinflip- ${amount}', description = f"{ctx.author.name}, choose an option in next 15 seconds!", color = 0x2F3136)

		msg = await ctx.send(content = f"{ctx.author.mention} ->",embed = embed , view = view)
		

		await view.wait()
		if view.value == True:
			won_or_lost = random.randint(0,1)
			if won_or_lost == 1:
				g_exp = random.randint(40,50)
				c_exp, n_exp = await self.bfh.update_exp(player_id = ctx.author.id,amount= g_exp)
				bal = await self.bfh.update_balance(player_id = ctx.author.id,amount =  amount, add = True)
				
				c_lvl : int= self.bfh.get_level(c_exp)
				lvl_up = self.bfh.level_up_check(c_exp, n_exp)

				text = f"\U0001f38a **Congrats** {ctx.author.name},\nThe coin landed on **Heads!** You chose **Heads**, meaning that you've just won **${amount}**!! \n\nYour new balance is **${bal:,}**\nYou gained <:exp:896086434946097162>**{g_exp} exp from this coinflip**"
				if lvl_up:
					lvl_up_m = random.randint(100,200)*(c_lvl+1)

					text+=f"\n\U0001f389 You levelled up! `({c_lvl} -> {c_lvl+1})` and gained "
					await self.update_balance(player_id = ctx.author.id,amount =  lvl_up_m, add = True)
				embed.description = text
				await msg.edit(embed = embed , view = view)

			elif won_or_lost == 0:
				g_exp = random.randint(20,25)
				c_exp, n_exp = await self.bfh.update_exp(player_id = ctx.author.id,amount= g_exp)

				c_lvl : int = self.bfh.get_level(c_exp)
				lvl_up = self.bfh.level_up_check(c_exp, n_exp)

				bal = await self.bfh.update_balance(player_id = ctx.author.id, amount = amount,add = False)
				
				text = f"\U0001f626 **Aw snap,**{ctx.author.name},\nThe coin landed on **Tails** You chose **Heads**, meaning that you've just lost **${amount}**!\n\nYour new balance is **${bal:,}**\nYou gained <:exp:896086434946097162>**{g_exp} exp from this coinflip** "
				if lvl_up:
					lvl_up_m = random.randint(100,200)*(c_lvl+1)

					text+=f"\n\U0001f389 You levelled up! `({c_lvl} -> {c_lvl+1})` and gained **${lvl_up_m}**"
					await self.bfh.update_balance(player_id = ctx.author.id,amount =  lvl_up_m, add = True)
				embed.description = text
				await msg.edit(embed = embed , view = view)
		
		elif view.value == False:
			won_or_lost = random.randint(0,1)
			if won_or_lost == 1:
				g_exp = random.randint(40,50)
				c_exp, n_exp = await self.bfh.update_exp(player_id = ctx.author.id,amount= g_exp)
				bal = await self.bfh.update_balance(player_id = ctx.author.id,amount = amount, add = True)
				
				c_lvl : int = self.bfh.get_level(c_exp)
				lvl_up = self.bfh.level_up_check(c_exp, n_exp)

				text = f"\U0001f38a **Congrats** {ctx.author.name},\nThe coin landed on **Tails!** You chose **Tails**, meaning that you've just won **${amount}**!! \n\nYour new balance is **${bal:,}**\nYou gained <:exp:896086434946097162>**{g_exp} exp from this coinflip**  "
				if lvl_up:
					lvl_up_m = random.randint(100,200)*(c_lvl+1)
					text+=f"\n\U0001f389 You levelled up! `({c_lvl} -> {c_lvl+1})` and gained **${lvl_up_m}**"
					await self.bfh.update_balance(player_id = ctx.author.id,amount = lvl_up_m, add = True)
				embed.description = text
				await msg.edit(embed = embed , view = view)

			elif won_or_lost == 0:
				g_exp = random.randint(20,25)
				c_exp, n_exp = await self.bfh.update_exp(player_id = ctx.author.id,amount= g_exp)
				bal = await self.bfh.update_balance(player_id = ctx.author.id,amount = amount, add =False)
				
				c_lvl : int = self.bfh.get_level(c_exp)
				lvl_up = self.bfh.level_up_check(c_exp, n_exp)


				text = f"\U0001f626 **Aw snap,** {ctx.author.name},\nThe coin landed on **Heads** You chose **Tails**, meaning that you've just lost **${amount}**!\n\nYour new balance is **${bal:,}**\nYou gained <:exp:896086434946097162>**{g_exp} exp from this coinflip**  "
				if lvl_up:
					lvl_up_m = random.randint(100,200)*(c_lvl+1)
					text+=f"\n\U0001f389 You levelled up! `({c_lvl} -> {c_lvl+1})` and gained **${lvl_up_m}**"
					await self.update_balance(player_id = ctx.author.id,amount = lvl_up_m, add = True)
				embed.description = text
				await msg.edit(embed = embed , view = view)
		else:
			embed.description = "Timed out!"
			view.clear_items()
			await msg.edit(embed = embed, view = view)

	@commands.group(name= 'open', aliases = ['unbox', 'o', 'un'], brief= "Open chest(s) from your inventory", help= "Open chests to get random game items!Chances of getting items are based on their rarity.You might get items with higher tier rarity from a lower tier chest.", invoke_without_command= True)
	@commands.cooldown(1,5, BucketType.user)
	async def _open(self, ctx):
		player_id = ctx.author.id
		flag = await self.bfh.check_if_exists(player_id)
		if not flag:
			return await ctx.send(f"{ctx.author}, you haven't  started playing Battlefield yet, run `{ctx.clean_prefix}start` to start playing!")
		embed = discord.Embed(title = f"{ctx.author.name}, You currently have...", color = 0x2F3136)
		inv_table = await self.bot.db.fetchrow(""" SELECT * FROM inventory where p_id = $1;  """, player_id)
		chest_dict = self.bfh.get_chest_counts(inv_table)
		text= f"• {cs.CHESTS_EMOJIS['common']} x{chest_dict['common_chest']} `common chest(s)`\n• {cs.CHESTS_EMOJIS['rare']} x{chest_dict['rare_chest']} `rare chest(s)`\n• {cs.CHESTS_EMOJIS['legendary']} x{chest_dict['legendary_chest']} `legendary chest(s)`\n• {cs.CHESTS_EMOJIS['epic']} x{chest_dict['epic_chest']} `epic chest(s)`\n• {cs.CHESTS_EMOJIS['mythic']} x{chest_dict['mythic_chest']} `mythic chest(s)`\nuse `{ctx.clean_prefix}open [chest] [amount]` to open your chests to get random items!"
		embed.description= text
		await ctx.send(f"{ctx.author.mention} ->", embed = embed)

	@_open.command(name= 'common', aliases = ['c', 'cmn', 'com'], help= "Open common chest(s) from your inventory(if available).Specify the amount of chests if you want to open multiple chests at once")
	@commands.cooldown(1,5, BucketType.user)
	async def _common(self, ctx, amount : int = 1):
		player_id = ctx.author.id
		flag = await self.bfh.check_if_exists(player_id)
		if not flag:
			return await ctx.send(f"{ctx.author}, you haven't  started playing Battlefield yet, run `{ctx.clean_prefix}start` to start playing!")
		inv_table = await self.bfh.get_inventory_table(player_id)
		chest_counts : dict = self.bfh.get_chest_counts(inv_table)
		if chest_counts['common_chest'] < amount:
			return await ctx.send(f"{ctx.author.mention}, You don't have {amount} `common chest(s)`, sorry.")
		elif amount <= 0:
			return await ctx.send(f"{ctx.author.mention} dumbass.... specify a valid amount for opening chests.")
		embed = discord.Embed(title=f"<a:windows_loading:894852723726499852> Opening **{amount}** `common chest(s)` from your inventory.....",color = 0x2F3136)
		msg = await ctx.send(f"{ctx.author.mention} ->", embed = embed)
		if amount == 1:
			
			o_item = self.bfh.open_chest('common_chest')
			await self.bfh.update_inventory(player_id = player_id, _item = o_item,amount= 1)
			await self.bfh.update_inventory(player_id = player_id, _item = 'common_chest',amount= -1)
			embed.title= f"{cs.EMOJIS['greentick']} Opened **{amount}** `common chest` from your inventory. You got:"
			embed.description=f"• {ALL_ITEMS[o_item]['emoji']} x1 `{ALL_ITEMS[o_item]['name']}`"
			# add embed image later
			await msg.edit(embed= embed)
		elif amount > 1:
			items_dict = {}
			items_list = []
			for i in range(0, amount):
				o_item = self.bfh.open_chest('common_chest')
				items_list.append(o_item)
				try:
					if items_dict[o_item]:
						items_dict[o_item]+=1
				except KeyError:
					items_dict[o_item] = 1
			try:
				if items_dict['common_chest']:
					items_dict['common_chest']+=-amount
			except KeyError:
				items_dict['common_chest'] = -amount
			await self.bfh.bulk_update_inventory(player_id= player_id, items_dict= items_dict)
			r_list = [f"• {ALL_ITEMS[j]['emoji']} x1 `{ALL_ITEMS[j]['name']}`" for j in items_list]
			r_str = '\n'.join(r_list)
			embed.title = f"{cs.EMOJIS['greentick']} Opened **{amount}** `common chest(s)` from your inventory. You got:"
			embed.description = r_str
			await msg.edit(embed= embed)

	@_open.command(name= 'rare', aliases = ['r', 'rar'], help= "Open rare chest(s) from your inventory(if available).Specify the amount of chests if you want to open multiple chests at once")
	@commands.cooldown(1,5, BucketType.user)
	async def _rare(self, ctx, amount : int = 1):
		player_id = ctx.author.id
		flag = await self.bfh.check_if_exists(player_id)
		if not flag:
			return await ctx.send(f"{ctx.author}, you haven't  started playing Battlefield yet, run `{ctx.clean_prefix}start` to start playing!")
		inv_table = await self.bfh.get_inventory_table(player_id)
		chest_counts : dict = self.bfh.get_chest_counts(inv_table)
		if chest_counts['rare_chest'] < amount:
			return await ctx.send(f"{ctx.author.mention}, You don't have {amount} `rare chest(s)`, sorry.")
		elif amount <= 0:
			return await ctx.send(f"{ctx.author.mention} dumbass.... specify a valid amount for opening chests.")
		embed = discord.Embed(title=f"<a:windows_loading:894852723726499852> Opening **{amount}** `rare chest(s)` from your inventory.....",color = 0x2F3136)
		msg = await ctx.send(f"{ctx.author.mention} ->", embed = embed)
		if amount == 1:
			
			o_item = self.bfh.open_chest('rare_chest')
			await self.bfh.update_inventory(player_id = player_id, _item = o_item,amount= 1)
			await self.bfh.update_inventory(player_id = player_id, _item = 'rare_chest',amount= -1)
			embed.title= f"{cs.EMOJIS['greentick']} Opened **{amount}** `rare chest` from your inventory. You got:"
			embed.description=f"• {ALL_ITEMS[o_item]['emoji']} x1 `{ALL_ITEMS[o_item]['name']}`"
			# add embed image later
			await msg.edit(embed= embed)
		elif amount > 1:
			items_dict = {}
			items_list = []
			for i in range(0, amount):
				o_item = self.bfh.open_chest('rare_chest')
				items_list.append(o_item)
				try:
					if items_dict[o_item]:
						items_dict[o_item]+=1
				except KeyError:
					items_dict[o_item] = 1
			try:
				if items_dict['rare_chest']:
					items_dict['rare_chest']+=-amount
			except KeyError:
				items_dict['rare_chest'] = -amount
			await self.bfh.bulk_update_inventory(player_id= player_id, items_dict= items_dict)
			r_list = [f"• {ALL_ITEMS[j]['emoji']} x1 `{ALL_ITEMS[j]['name']}`" for j in items_list]
			r_str = '\n'.join(r_list)
			embed.title = f"{cs.EMOJIS['greentick']} Opened **{amount}** `rare chest(s)` from your inventory. You got:"
			embed.description = r_str
			await msg.edit(embed= embed)

	@_open.command(name= 'legendary', aliases = ['l', 'leg', 'le', 'legen'], help= "Open legendary chest(s) from your inventory(if available).Specify the amount of chests if you want to open multiple chests at once")
	@commands.cooldown(1,5, BucketType.user)
	async def _legendary(self, ctx, amount : int = 1):
		player_id = ctx.author.id
		flag = await self.bfh.check_if_exists(player_id)
		if not flag:
			return await ctx.send(f"{ctx.author}, you haven't  started playing Battlefield yet, run `{ctx.clean_prefix}start` to start playing!")
		inv_table = await self.bfh.get_inventory_table(player_id)
		chest_counts : dict = self.bfh.get_chest_counts(inv_table)
		if chest_counts['legendary_chest'] < amount:
			return await ctx.send(f"{ctx.author.mention}, You don't have {amount} `legendary chest(s)`, sorry.")
		elif amount <= 0:
			return await ctx.send(f"{ctx.author.mention} dumbass.... specify a valid amount for opening chests.")
		embed = discord.Embed(title=f"<a:windows_loading:894852723726499852> Opening **{amount}** `legendary chest(s)` from your inventory.....",color = 0x2F3136)
		msg = await ctx.send(f"{ctx.author.mention} ->", embed = embed)
		if amount == 1:
			
			o_item = self.bfh.open_chest('legendary_chest')
			await self.bfh.update_inventory(player_id = player_id, _item = o_item,amount= 1)
			await self.bfh.update_inventory(player_id = player_id, _item = 'legendary_chest',amount= -1)
			embed.title= f"{cs.EMOJIS['greentick']} Opened **{amount}** `legendary chest` from your inventory. You got:"
			embed.description=f"• {ALL_ITEMS[o_item]['emoji']} x1 `{ALL_ITEMS[o_item]['name']}`"
			# add embed image later
			await msg.edit(embed= embed)
		elif amount > 1:
			items_dict = {}
			items_list = []
			for i in range(0, amount):
				o_item = self.bfh.open_chest('legendary_chest')
				items_list.append(o_item)
				try:
					if items_dict[o_item]:
						items_dict[o_item]+=1
				except KeyError:
					items_dict[o_item] = 1
			try:
				if items_dict['legendary_chest']:
					items_dict['legendary_chest']+=-amount
			except KeyError:
				items_dict['legendary_chest'] = -amount
			await self.bfh.bulk_update_inventory(player_id= player_id, items_dict= items_dict)
			r_list = [f"• {ALL_ITEMS[j]['emoji']} x1 `{ALL_ITEMS[j]['name']}`" for j in items_list]
			r_str = '\n'.join(r_list)
			embed.title = f"{cs.EMOJIS['greentick']} Opened **{amount}** `legendary chest(s)` from your inventory. You got:"
			embed.description = r_str
			await msg.edit(embed= embed)

	@_open.command(name= 'epic', aliases = ['e', 'ep', 'epc'], help= "Open epic chest(s) from your inventory(if available).Specify the amount of chests if you want to open multiple chests at once")
	@commands.cooldown(1,5, BucketType.user)
	async def _epic(self, ctx, amount : int = 1):
		player_id = ctx.author.id
		flag = await self.bfh.check_if_exists(player_id)
		if not flag:
			return await ctx.send(f"{ctx.author}, you haven't  started playing Battlefield yet, run `{ctx.clean_prefix}start` to start playing!")
		inv_table = await self.bfh.get_inventory_table(player_id)
		chest_counts : dict = self.bfh.get_chest_counts(inv_table)
		if chest_counts['epic_chest'] < amount:
			return await ctx.send(f"{ctx.author.mention}, You don't have {amount} `epic chest(s)`, sorry.")
		elif amount <= 0:
			return await ctx.send(f"{ctx.author.mention} dumbass.... specify a valid amount for opening chests.")
		embed = discord.Embed(title=f"<a:windows_loading:894852723726499852> Opening **{amount}** `epic chest(s)` from your inventory.....",color = 0x2F3136)
		msg = await ctx.send(f"{ctx.author.mention} ->", embed = embed)
		if amount == 1:
			
			o_item = self.bfh.open_chest('epic_chest')
			await self.bfh.update_inventory(player_id = player_id, _item = o_item,amount= 1)
			await self.bfh.update_inventory(player_id = player_id, _item = 'epic_chest',amount= -1)
			embed.title= f"{cs.EMOJIS['greentick']} Opened **{amount}** `epic chest` from your inventory. You got:"
			embed.description=f"• {ALL_ITEMS[o_item]['emoji']} x1 `{ALL_ITEMS[o_item]['name']}`"
			# add embed image later
			await msg.edit(embed= embed)
		elif amount > 1:
			items_dict = {}
			items_list = []
			for i in range(0, amount):
				o_item = self.bfh.open_chest('epic_chest')
				items_list.append(o_item)
				try:
					if items_dict[o_item]:
						items_dict[o_item]+=1
				except KeyError:
					items_dict[o_item] = 1
			try:
				if items_dict['epic_chest']:
					items_dict['epic_chest']+=-amount
			except KeyError:
				items_dict['epic_chest'] = -amount
			await self.bfh.bulk_update_inventory(player_id= player_id, items_dict= items_dict)
			r_list = [f"• {ALL_ITEMS[j]['emoji']} x1 `{ALL_ITEMS[j]['name']}`" for j in items_list]
			r_str = '\n'.join(r_list)
			embed.title = f"{cs.EMOJIS['greentick']} Opened **{amount}** `epic chest(s)` from your inventory. You got:"
			embed.description = r_str
			await msg.edit(embed= embed)

	@_open.command(name= 'mythic', aliases = ['m', 'myth', 'mtc', 'mth', 'mc'], help= "Open mythic chest(s) from your inventory(if available).Specify the amount of chests if you want to open multiple chests at once")
	@commands.cooldown(1,5, BucketType.user)
	async def _mythic(self, ctx, amount : int = 1):
		player_id = ctx.author.id
		flag = await self.bfh.check_if_exists(player_id)
		if not flag:
			return await ctx.send(f"{ctx.author}, you haven't  started playing Battlefield yet, run `{ctx.clean_prefix}start` to start playing!")
		inv_table = await self.bfh.get_inventory_table(player_id)
		chest_counts : dict = self.bfh.get_chest_counts(inv_table)
		if chest_counts['mythic_chest'] < amount:
			return await ctx.send(f"{ctx.author.mention}, You don't have {amount} `mythic chest(s)`, sorry.")
		elif amount <= 0:
			return await ctx.send(f"{ctx.author.mention} dumbass.... specify a valid amount for opening chests.")
		embed = discord.Embed(title=f"<a:windows_loading:894852723726499852> Opening **{amount}** `mythic chest(s)` from your inventory.....",color = 0x2F3136)
		msg = await ctx.send(f"{ctx.author.mention} ->", embed = embed)
		if amount == 1:
			
			o_item = self.bfh.open_chest('mythic_chest')
			await self.bfh.update_inventory(player_id = player_id, _item = o_item,amount= 1)
			await self.bfh.update_inventory(player_id = player_id, _item = 'mythic_chest',amount= -1)
			embed.title= f"{cs.EMOJIS['greentick']} Opened **{amount}** `mythic chest` from your inventory. You got:"
			embed.description=f"• {ALL_ITEMS[o_item]['emoji']} x1 `{ALL_ITEMS[o_item]['name']}`"
			# add embed image later
			await msg.edit(embed= embed)
		elif amount > 1:
			items_dict = {}
			items_list = []
			for i in range(0, amount):
				o_item = self.bfh.open_chest('mythic_chest')
				items_list.append(o_item)
				try:
					if items_dict[o_item]:
						items_dict[o_item]+=1
				except KeyError:
					items_dict[o_item] = 1
			try:
				if items_dict['mythic_chest']:
					items_dict['mythic_chest']+=-amount
			except KeyError:
				items_dict['mythic_chest'] = -amount
			await self.bfh.bulk_update_inventory(player_id= player_id, items_dict= items_dict)
			r_list = [f"• {ALL_ITEMS[j]['emoji']} x1 `{ALL_ITEMS[j]['name']}`" for j in items_list]
			r_str = '\n'.join(r_list)
			embed.title = f"{cs.EMOJIS['greentick']} Opened **{amount}** `mythic chest(s)` from your inventory. You got:"
			embed.description = r_str
			await msg.edit(embed= embed)

	@commands.command(name = 'daily', aliases = ['d'])
	async def _daily(self, ctx):
		flag = await self.bfh.check_if_exists(ctx.author.id)
		if not flag:
			return await ctx.send(f"Hey **{ctx.author}**, you don't have an account yet. To create one, run the `{ctx.clean_prefix}start` command! Thanks ")
		#check for cooldown
		current_time = int(time.time())
		cd = await self.bfh.get_cooldown_data(ctx.author.id, 'daily')
		if current_time < int(cd):
			return await ctx.send(f"{ctx.author.mention} **You can get the daily rewards again in** `{humanize.precisedelta(cd - current_time)}`")
		reward = random.randint(200, 300)
		n_bal = await self.bfh.update_balance(player_id = ctx.author.id, amount = reward, add = True)
		await self.bfh.update_cooldowns(ctx.author.id, 'daily')
		c_exp, n_exp = await self.bfh.update_exp(player_id = ctx.author.id,amount= random.randint(150, 200))
		c_lvl = self.bfh.get_level(c_exp)
		lvl_up = self.bfh.level_up_check(c_exp, n_exp)
		text = f"{ctx.author.mention} , You got **${reward}** and <:exp:896086434946097162>**{n_exp-c_exp} EXP **as your daily check-in reward!\nYour new balace is **${n_bal:,}**"
		if lvl_up:
			lvl_up_m = random.randint(100,200)*(c_lvl+1)
			text += f"\n\n\U0001f389 Congrats! You levelled up! `({c_lvl} -> {c_lvl+1})` and gained **${lvl_up_m}**"
			await self.bfh.update_balance(player_id = ctx.author.id,amount = lvl_up_m, add = True)
		await ctx.send(text)

	@commands.command(name = 'hourly', aliases = ['h'])
	async def _hourly(self, ctx):
		flag = await self.bfh.check_if_exists(ctx.author.id)
		if not flag:
			return await ctx.send(f"Hey **{ctx.author}**, you don't have an account yet. To create one, run the `{ctx.clean_prefix}start` command! Thanks ")
		#check for cooldown
		current_time = int(time.time())
		cd = await self.bfh.get_cooldown_data(ctx.author.id, 'hourly')
		if current_time < int(cd):
			return await ctx.send(f"{ctx.author.mention} **You can get hourly rewards again in** `{humanize.precisedelta(cd - current_time)}`")
		reward = random.randint(50,75)
		n_bal = await self.bfh.update_balance(player_id = ctx.author.id, amount = reward, add = True)
		await self.bfh.update_cooldowns(ctx.author.id, 'hourly')
		c_exp, n_exp = await self.bfh.update_exp(player_id = ctx.author.id,amount= random.randint(50, 100))
		c_lvl = self.bfh.get_level(c_exp)
		lvl_up = self.bfh.level_up_check(c_exp, n_exp)
		text = f"{ctx.author.mention} , You got **${reward}** and <:exp:896086434946097162>**{n_exp-c_exp} EXP **as your hourly rewards!\nYour new balace is **${n_bal}**"
		if lvl_up:
			lvl_up_m = random.randint(100,200)*(c_lvl+1)
			text += f"\n\n\U0001f389 Congrats! You levelled up! `({c_lvl} -> {c_lvl+1})` and gained **${lvl_up_m}**"
			await self.bfh.update_balance(player_id = ctx.author.id,amount = lvl_up_m, add = True)
		await ctx.send(text)

	@commands.command(name = 'weekly', aliases = ['w'])
	async def _weekly(self, ctx):
		flag = await self.bfh.check_if_exists(ctx.author.id)
		if not flag:
			return await ctx.send(f"Hey **{ctx.author}**, you don't have an account yet. To create one, run the `{ctx.clean_prefix}start` command! Thanks ")
		#check for cooldown
		current_time = int(time.time())
		cd = await self.bfh.get_cooldown_data(ctx.author.id, 'weekly')
		if current_time < int(cd):
			return await ctx.send(f"{ctx.author.mention} **You can get the weekly rewards again in** `{humanize.precisedelta(cd - current_time)}`")
		reward = random.randint(800, 1000)
		n_bal = await self.bfh.update_balance(player_id = ctx.author.id, amount = reward, add = True)
		await self.bfh.update_cooldowns(ctx.author.id, 'weekly')
		c_exp, n_exp = await self.bfh.update_exp(player_id = ctx.author.id,amount= random.randint(400, 600))
		c_lvl = self.bfh.get_level(c_exp)
		lvl_up = self.bfh.level_up_check(c_exp, n_exp)
		text = f"{ctx.author.mention} , You got **${reward}** and <:exp:896086434946097162>**{n_exp-c_exp} EXP **as your weekly check-in reward!\nYour new balace is **${n_bal}**"
		if lvl_up:
			lvl_up_m = random.randint(100,200)*(c_lvl+1)
			text += f"\n\n\U0001f389 Congrats! You levelled up! `({c_lvl} -> {c_lvl+1})` and gained **${lvl_up_m}**"
			await self.bfh.update_balance(player_id = ctx.author.id,amount = lvl_up_m, add = True)
		await ctx.send(text)

	@commands.command(name = 'monthly', aliases = ['mon', 'm'])
	async def _monthly(self, ctx):
		flag = await self.bfh.check_if_exists(ctx.author.id)
		if not flag:
			return await ctx.send(f"Hey **{ctx.author}**, you don't have an account yet. To create one, run the `{ctx.clean_prefix}start` command! Thanks ")
		#check for cooldown
		current_time = int(time.time())
		cd = await self.bfh.get_cooldown_data(ctx.author.id, 'monthly')
		if current_time < int(cd):
			return await ctx.send(f"{ctx.author.mention} **You can get the monthly rewards again in** `{humanize.precisedelta(cd - current_time)}`")
		reward = random.randint(1500, 2000)
		n_bal = await self.bfh.update_balance(player_id = ctx.author.id, amount = reward, add = True)
		await self.bfh.update_cooldowns(ctx.author.id, 'monthly')
		c_exp, n_exp = await self.bfh.update_exp(player_id = ctx.author.id,amount= random.randint(450, 500))
		c_lvl = self.bfh.get_level(c_exp)
		lvl_up = self.bfh.level_up_check(c_exp, n_exp)
		text = f"{ctx.author.mention} , You got **${reward}** and <:exp:896086434946097162>**{n_exp-c_exp} EXP **as your monthly check-in reward!\nYour new balace is **${n_bal}**"
		if lvl_up:
			lvl_up_m = random.randint(100,200)*(c_lvl+1)
			text += f"\n\n\U0001f389 Congrats! You levelled up! `({c_lvl} -> {c_lvl+1})` and gained **${lvl_up_m}**"
			await self.bfh.update_balance(player_id = ctx.author.id,amount = lvl_up_m, add = True)
		await ctx.send(text)

	@commands.command(name = 'work', aliases = ['job', 'j'])
	async def work(self, ctx):
		flag = await self.bfh.check_if_exists(ctx.author.id)
		if not flag:
			return await ctx.send(f"Hey **{ctx.author}**, you don't have an account yet. To create one, run the `{ctx.clean_prefix}start` command! Thanks ")
		#check for cooldown
		current_time = int(time.time())
		cd = await self.bfh.get_cooldown_data(ctx.author.id, 'work')
		if current_time < int(cd):
			return await ctx.send(f"{ctx.author.mention} **You can get the monthly rewards again in** `{humanize.precisedelta(cd - current_time)}`")
		reward = random.randint(100, 150)
		n_bal = await self.bfh.update_balance(player_id = ctx.author.id, amount = reward, add = True)
		await self.bfh.update_cooldowns(ctx.author.id, 'work')
		c_exp, n_exp = await self.bfh.update_exp(player_id = ctx.author.id,amount= random.randint(100, 150))
		c_lvl = self.bfh.get_level(c_exp)
		lvl_up = self.bfh.level_up_check(c_exp, n_exp)
		text = f"{ctx.author.mention} , You earned **${reward}** and <:exp:896086434946097162>**{n_exp-c_exp} EXP **by working as a programmer(this is just a test, more things will be added soon)!\nYour new balace is **${n_bal}**"
		if lvl_up:
			lvl_up_m = random.randint(100,200)*(c_lvl+1)
			text += f"\n\n\U0001f389 Congrats! You levelled up! `({c_lvl} -> {c_lvl+1})` and gained **${lvl_up_m}**"
			await self.bfh.update_balance(player_id = ctx.author.id,amount = lvl_up_m, add = True)
		await ctx.send(text)

	

def setup(bot):
	bot.add_cog(BattleField(bot))

