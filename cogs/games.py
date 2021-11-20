import discord
from discord import embeds
from discord import player
from discord.ext import commands
import asyncpg
import typing
import random
import asyncio
import difflib
from discord.ext.commands.cooldowns import BucketType, Cooldown
from utils import buttons_and_selects as bs 
import json
import time
import humanize
from games_utils import helper
from games_utils.helper import AttackEngine
from games_utils.items import ALL_ITEMS
import games_utils.constants as cs
from utils.decorators import has_started, is_opted, has_ref_started, can_attack
from utils.errors import NotStartedPlaying
from utils.context_managers import UserLock
class Battlefield(commands.Cog):
	"""Snowden's Battlefield cog"""
	def __init__(self, bot):
		self.bot = bot
		self.bfh = helper.BattleFieldHelper(bot)
		

	


	@commands.command(name = 'start', aliases = ['enter', 'init'], brief = "Creates an account for playing in Battlefield!", help = "Enter the `Snowden's BattleField` by creating an account!")
	@commands.guild_only()
	@commands.max_concurrency(1, BucketType.user)
	@commands.cooldown(1,10, type= BucketType.user)
	async def _start(self, ctx):
		if ctx.interaction is not None:
			await ctx.interaction.response.defer(ephemeral=True)
		player_id = ctx.author.id
		flag = await self.bfh.check_if_exists(player_id)
		if flag:
			return await ctx.send("**You already have an account, you can keep playing!**", view = bs.Guide(ctx))
		await self.bot.db.execute(""" INSERT INTO battlefield (p_id, created_at, common, rare) VALUES ($1, $2, $3, $4); """, player_id, int(ctx.message.created_at.timestamp()),'{"p92" : 1, "common_chest" : 2, "9mm" : 2}','{"rare_chest" : 1, "pain_killer" : 1 }' )
		

		embed = discord.Embed(title = f"Hey {ctx.author.name}, \U0001f44b Welcome to Snowden's BattleField!!", description = f"You got **$500** and <:exp:896086434946097162>**100 EXP** as a reward for entering the battlefield!\nYou also got:\n• {ALL_ITEMS['common_chest']['emoji']}`common chest x2`\n• {cs.CHESTS_EMOJIS['rare']}`rare chest x1`\n• {ALL_ITEMS['p92']['emoji']}`p92 x1`\n• {ALL_ITEMS['9mm']['emoji']}`9mm x2`\n• {ALL_ITEMS['pain_killer']['emoji']}`pain killer x1`\nHope you enjoy!", color = 0x2F3136)
		embed.set_footer(text = f"you can use {ctx.clean_prefix}start command later for getting guide how to play the game!")
		await ctx.reply(embed = embed, view = bs.Guide(ctx))

	@commands.command(name= 'inventory', aliases = ['inv'], brief= "Shows player inventory", help = "Shows player inventory, only if the user has an account.")
	@has_ref_started()
	@commands.max_concurrency(1, BucketType.user)
	@commands.cooldown(1,5, type= BucketType.user)
	async def _inventory(self, ctx, player : typing.Union[discord.Member, discord.User] = None):
		if ctx.interaction is not None:
			await ctx.interaction.response.defer(ephemeral=False)
		if player is None:
			if ctx.message.reference:
				player = ctx.message.reference.resolved.author
			else:
				player = ctx.author

		player_id = player.id
		flag = await self.bfh.check_if_exists(player_id)
		if not flag:
			raise NotStartedPlaying(f"**{player}** haven't started playing Battlefield yet,ask them to run `{ctx.clean_prefix}start` to start playing!")
		
		rec = await self.bfh.get_player_data(player_id)
		inv_value = self.bfh.get_inventory_value(rec)
		current_hp : int = rec['hp']
		current_sp : int = rec['sp']

		embed = discord.Embed(title = f"**__{player}'s Inventory__**",color = 0x2F3136)
		text = f"\U0001f3e6 **Balance** : ${rec['balance']}\n\U0001f4bc **Inv. value** : ${inv_value}\n\U00002728 **Player value** : ${rec['balance']+inv_value}\n\U0001f4c8 **Level**: {self.bfh.get_level(rec['exp'])}\n\U00002694 **Opt in status** : {cs.EMOJIS['toggle_on'] if rec['opt_status'] else cs.EMOJIS['toggle_off']}\n"
		embed.add_field(name='\U0001f4cb __Status/profile__', value=text, inline = False)
		embed.add_field(name="\U00002764 __Health__", value=f"{current_hp}/100\n{self.bfh.get_bar_emojis('hp', current_hp, 100)}")
		weap, sh = self.bfh.get_equipments(rec)
		if current_sp:
			sh_p = ALL_ITEMS[sh]['shield_points']
			shield_str = f"{current_sp}\n{self.bfh.get_bar_emojis('armour', current_sp, sh_p)}"
		else: 
			shield_str = 'Not equipped'
		
		embed.add_field(name="\U0001f6e1 __Armour__", value=shield_str)
		embed.add_field(name= ":toolbox: __Equipments__", value = f"**__Weapon__**: {ALL_ITEMS[weap]['emoji'] if weap else ' '}{ALL_ITEMS[weap]['name'] if weap else 'Not equipped'}\n\n**__Armour__**: {ALL_ITEMS[sh]['emoji'] if sh else ' '}{ALL_ITEMS[sh]['name'] if sh else 'Not equipped'}")
		embed2 = discord.Embed(title = f"**__{player}'s Inventory__** [items]",color = 0x2F3136)

		inv_items = self.bfh.get_inventory_items_str(rec)
		for r in inv_items.keys():
			if inv_items[r]:
				embed2.add_field(name=f"**{cs.RARITY[r].upper()}**", value= inv_items[r])
		view = bs.InventoryEmbeds(ctx,embed, embed2)

		view.message = await ctx.send(embed= embed, view = view)

	@commands.command(name= 'balance', aliases = ['bal', 'money'], help = "Shows your/ a player's balance")
	@commands.guild_only()
	@has_ref_started()
	@commands.cooldown(1,3, BucketType.user)
	async def _balance(self, ctx, player : typing.Union[discord.Member, discord.User]= None):
		if player is None:
			if ctx.message.reference:
				player = ctx.message.reference.resolved.author
			else:
				player = ctx.author
		player_id = player.id
		
		inv_table = await self.bfh.get_player_data(player_id)
		bal : int = inv_table['balance']
		await ctx.send(f"**{player}'s** balance: **${bal:,}**")

	@commands.command(name = 'profile', aliases = ['pro', 'prof'], help = "Shows a player's profile")
	@commands.guild_only()
	@has_ref_started()
	@commands.cooldown(1,3, BucketType.user)
	async def _profile(self, ctx, player : typing.Union[discord.Member, discord.User] = None):
		if player is None:
			if ctx.message.reference:
				player = ctx.message.reference.resolved.author
			else:
				player = ctx.author
		player_id = player.id
		await ctx.send("SOON")

	@commands.command(name = 'items', aliases = ['item'], brief = "Gives you information about any game item(s)", help = "Gives you information about any game item(s). run `items [item_name]` to get information about a specific item.")
	@commands.cooldown(1,3, BucketType.user)
	async def _items(self, ctx, *,item_name : str = None):
		if ctx.interaction is not None:
			await ctx.interaction.response.defer(ephemeral=False)
		if not item_name:
			item_list = []
			for item in ALL_ITEMS.keys():
				item_list.append(ALL_ITEMS[str(item)]['name'])
			r_str = ', '.join(item_list)
			embed = discord.Embed(title = "Snowden's Battlefield : All items ->", color =0x2F3136 )
			embed.description = f"`{r_str}`"
			return await ctx.send(f"{ctx.author.mention} ->", embed = embed)

		item_list = [str(item) for item in ALL_ITEMS.keys()]

		item_s_r = difflib.get_close_matches(item_name.lower(),item_list, n=1, cutoff=0.3)
		if len(item_s_r) == 0:
			return await ctx.send(f"No item named `{item_name}`found")
		item_name_n = item_s_r[0]
		try:
			item_dict = ALL_ITEMS[item_name_n]
		except KeyError:
			return await ctx.send(f"No item named `{item_name}`found")
		embed = discord.Embed(title = f"{item_dict['emoji']} **{item_dict['name']}**",  color =0x2F3136)
		embed.add_field(name= ":star2: __Rarity__", value = f"`{item_dict['rarity'].upper()}`", inline = False)
		if item_dict['type'] == 'weapon':
			embed.add_field(name=":boom: Damage", value = f"**{item_dict['damage']} hp** `(min-max)`\n`{item_dict['damage_type']}`")
			embed.add_field(name=":alarm_clock: Cooldown", value=f"**{self.bfh.format_cooldown(item_dict['cooldown'])}**")
			if item_dict['ammo']:
				embed.add_field(name=":placard: Ammunition", value = f"**{item_dict['ammo']}**")
			if item_dict['buy_price']:
				embed.add_field(name=":dollar: Buy price", value= f"**${item_dict['buy_price']}**")
			embed.add_field(name=":dollar: Sell price", value=f"**${item_dict['sell_price']}**")
			embed.set_thumbnail(url = self.bot.get_emoji(int(item_dict['emoji'].split(':')[-1][:-1:])).url)
			return await ctx.send(f"{ctx.author.mention} ->", embed = embed)
		if item_dict['type'] == 'healing':
			embed.add_field(name=":heart: Health Recover", value = f"**{item_dict['hp_recover']} hp** `(min-max)`")
			embed.add_field(name=":alarm_clock: Cooldown", value=f"**{self.bfh.format_cooldown(item_dict['cooldown'])}**")
			if item_dict['buy_price']:
				embed.add_field(name=":dollar: Buy price", value= f"**${item_dict['buy_price']}**")
			embed.add_field(name=":dollar: Sell price", value=f"**${item_dict['sell_price']}**")
			embed.set_thumbnail(url = self.bot.get_emoji(int(item_dict['emoji'].split(':')[-1][:-1:])).url)
			return await ctx.send(f"{ctx.author.mention} ->", embed = embed)
		if item_dict['type'] == 'armour':
			embed.add_field(name= ":shield: Armour Points", value=f"**{item_dict['shield_points']}**")
			if item_dict['buy_price']:
				embed.add_field(name=":dollar: Buy price", value= f"**${item_dict['buy_price']}**")
			embed.add_field(name=":dollar: Sell price", value=f"**${item_dict['sell_price']}**")
			embed.set_thumbnail(url = self.bot.get_emoji(int(item_dict['emoji'].split(':')[-1][:-1:])).url)
			return await ctx.send(f"{ctx.author.mention} ->", embed = embed)
		if item_dict["type"] == 'ammunition':
			embed.add_field(name= ":page_with_curl: Used by", value=f"{item_dict['used_by']}")
			embed.add_field(name=":dollar: Sell price", value=f"**${item_dict['sell_price']}**")
			embed.set_thumbnail(url = self.bot.get_emoji(int(item_dict['emoji'].split(':')[-1][:-1:])).url)
			return await ctx.send(f"{ctx.author.mention} ->", embed = embed)
		if item_dict['type'] == 'chest':
			embed.description = item_dict['description']
			if item_dict['buy_price']:
				embed.add_field(name=":dollar: Buy price", value= f"**${item_dict['buy_price']}**")
			embed.add_field(name=":dollar: Sell price", value=f"**${item_dict['sell_price']}**")
			embed.set_thumbnail(url = self.bot.get_emoji(int(item_dict['emoji'].split(':')[-1][:-1:])).url)
			return await ctx.send(f"{ctx.author.mention} ->", embed = embed)

	@commands.command(name= 'cooldowns', aliases = ['cd', 'cools','cool', 'cds'], help= "Get all battlefield command cooldowns for you/a player.")
	@commands.guild_only()
	@has_ref_started()
	@commands.cooldown(1,3, BucketType.user)
	async def _cooldowns(self, ctx, player : typing.Union[discord.Member, discord.User] = None):
		if ctx.interaction is not None:
			await ctx.interaction.response.defer(ephemeral=False)
		if player is None:
			if ctx.message.reference:
				player = ctx.message.reference.resolved.author
			else:
				player = ctx.author
		player_id = player.id
		
		cd_dict : dict = await self.bfh.get_cooldown_data(player_id)
		embed = discord.Embed(title = f"__{player}'s cooldowns:__",color =0x2F3136)
		now = int(time.time())
		for n_c, t in cd_dict.items():
			if 'equip' in str(n_c):
				embed.add_field(name=f"__equip__", value= f"**{'Available' if now >= t else self.bfh.format_cooldown(t-now)}**")
				break
			embed.add_field(name=f"__{str(n_c).split('n_', 1)[1]}__", value= f"**{'Available' if now >= t else self.bfh.format_cooldown(t-now)}**")
			
		embed.description = "Note: `equip` cooldown is applicable for weapon equipments only.\nArmour equipments have no cooldowns."
		await ctx.send(f"{ctx.author.mention} ->", embed = embed)


		
	
	@commands.command(name= 'opt', aliases = ['optin', 'optout', 'toggleopt', 'opt_in_toggle'], help= "Toggle your `opt` status if it's available.There is a 12h cooldown.")
	@commands.guild_only()
	@has_started()
	@commands.max_concurrency(1, BucketType.user)
	@commands.cooldown(1,5,BucketType.user)
	async def opt(self, ctx):
		if ctx.interaction is not None:
			await ctx.interaction.response.defer(ephemeral=False)
		player_id = ctx.author.id
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
	@has_started()
	@commands.max_concurrency(1, BucketType.user)
	@commands.cooldown(2,6, commands.BucketType.user)
	async def _cf(self, ctx, amount : int = 50):
		if ctx.interaction is not None:
			await ctx.interaction.response.defer(ephemeral=False)
		# flag = await self.bfh.check_if_exists(ctx.author.id)
		# if not flag:
		# 	return await ctx.send(f"{ctx.author.mention},you haven't started playing Battlefield yet, run `{ctx.clean_prefix}start` to start playing!")
		balance = await self.bot.db.fetchval(""" SELECT balance FROM battlefield where p_id = $1; """, ctx.author.id)
		if balance < amount:
			return await ctx.send("Looks like you don't have enough money to gamble on coinflip!")
		if amount > 50000 or amount < 50:
			return await ctx.send("Minimum amount of gambling is **$50** and Maximum amount of gambling is **$50000**")

		view = bs.HeadsOrTails(ctx)

		embed = discord.Embed(title =f'Coinflip- ${amount}', description = f"{ctx.author.name}, choose an option in next 15 seconds!", color = 0x2F3136)

		msg = await ctx.send(content = f"{ctx.author.mention} ->",embed = embed , view = view)
		

		await view.wait()
		if view.value == True:
			embed.description = f"<a:windows_loading:894852723726499852> The coin has been tossed.."
			await msg.edit(embed = embed , view = view)
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

					text+=f"\n\U0001f389 You levelled up! `({c_lvl} -> {c_lvl+1})` and gained **${lvl_up_m}**"
					await self.bfh.update_balance(player_id = ctx.author.id,amount =  lvl_up_m, add = True)
				embed.description = text
				await asyncio.sleep(2)
				await msg.edit(embed = embed)

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
				await asyncio.sleep(2)
				await msg.edit(embed = embed)
		
		elif view.value == False:
			embed.description = f"<a:windows_loading:894852723726499852> The coin has been tossed.."
			await msg.edit(embed = embed , view = view)
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
				await asyncio.sleep(2)
				await msg.edit(embed = embed)

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
					await self.bfh.update_balance(player_id = ctx.author.id,amount = lvl_up_m, add = True)
				embed.description = text
				await asyncio.sleep(2)
				await msg.edit(embed = embed)
		else:
			embed.description = "Timed out!"
			view.clear_items()
			await msg.edit(embed = embed, view = view)

	@commands.command(name= 'open', aliases = ['unbox', 'o', 'un'], brief= "Open chest(s) from your inventory", help= "Open chests to get random game items!Chances of getting items are based on their rarity.You might get items with higher tier rarity from a lower tier chest.")
	@has_started()
	@commands.max_concurrency(1, BucketType.user)
	@commands.cooldown(1,5, BucketType.user)
	async def _open(self, ctx, amount : typing.Optional[int] = 1,*, chest : str = None):
		if ctx.interaction is not None:
			await ctx.interaction.response.defer(ephemeral=False)
		player_id = ctx.author.id
		inv_table = await self.bfh.get_player_data(player_id)
		chest_dict : dict = self.bfh.get_chest_counts(inv_table)
		if chest is None:
			
			embed = discord.Embed(title = f"{ctx.author.name}, You currently have...", color = 0x2F3136)
			
			text= f"• {cs.CHESTS_EMOJIS['common']} x{chest_dict['common_chest']} `common chest(s)`\n• {cs.CHESTS_EMOJIS['rare']} x{chest_dict['rare_chest']} `rare chest(s)`\n• {cs.CHESTS_EMOJIS['legendary']} x{chest_dict['legendary_chest']} `legendary chest(s)`\n• {cs.CHESTS_EMOJIS['epic']} x{chest_dict['epic_chest']} `epic chest(s)`\n• {cs.CHESTS_EMOJIS['mythic']} x{chest_dict['mythic_chest']} `mythic chest(s)`\nuse `{ctx.clean_prefix}open [amount] [chest_name]` to open your chests to get random items!"
			embed.description= text
			return await ctx.send(f"{ctx.author.mention} ->", embed = embed)
		chest_list = ['common_chest', 'rare_chest', 'legendary_chest', 'epic_chest', 'mythic_chest']
		chest_s_r = difflib.get_close_matches(chest.lower(),chest_list, n=1, cutoff=0.3)
		if len(chest_s_r) == 0:
			return await ctx.send(f"No chest named `{chest}`found")
		chest_name_n= chest_s_r[0]
		if chest_dict[chest_name_n] < amount:
			return await ctx.send(f"{ctx.author.mention}, You don't have **{amount}x** `{ALL_ITEMS[chest_name_n]['name']}(s)` in your inventory, sorry.")
		elif amount <= 0:
			return await ctx.send(f"{ctx.author.mention} please specify a valid amount for opening chests.")
		elif amount >15:
			return await ctx.send(f"{ctx.author.mention}, Can't open more than 15 chests at once!")
		msg = await ctx.send(f"<a:windows_loading:894852723726499852> {ctx.author.mention} ->  Opening **{amount}x** `{ALL_ITEMS[chest_name_n]['name']}(s)` from your inventory.....")

		items_dict = {}
		items_list = []
		# randomize/ set chances of getting item later
		for i in range(0, amount):
			o_item = self.bfh.open_chest(chest_name_n)
			items_list.append(o_item)
			try:
				if items_dict[o_item]:
					items_dict[o_item]+=1
			except KeyError:
				items_dict[o_item] = 1
		try:
			if items_dict[chest_name_n]:
				items_dict[chest_name_n]+=-amount
		except KeyError:
			items_dict[chest_name_n] = -amount
		
		await self.bfh.bulk_update_inventory(player_id= player_id, items_dict= items_dict)
		r_list = [f"• {ALL_ITEMS[j]['emoji']} x1 `{ALL_ITEMS[j]['name']}`" for j in items_list]
		r_str = '\n'.join(r_list)
		await asyncio.sleep(2)
		await msg.edit(f"{cs.EMOJIS['greentick']} {ctx.author.mention} ->  Opened **{amount}x** `{ALL_ITEMS[chest_name_n]['name']}(s)` from your inventory. You got : \n{r_str}")

	@commands.command(name = 'daily', aliases = ['d'])
	@has_started()
	@commands.cooldown(1,3, BucketType.user)
	async def _daily(self, ctx):
		# flag = await self.bfh.check_if_exists(ctx.author.id)
		# if not flag:
		# 	return await ctx.send(f"Hey **{ctx.author}**, you don't have an account yet. To create one, run the `{ctx.clean_prefix}start` command! Thanks ")
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

		await self.bfh.update_inventory(player_id=ctx.author.id, _item = 'rare_chest', amount = 1)
		text = f"{ctx.author.mention} , You got **${reward}** and <:exp:896086434946097162>**{n_exp-c_exp} EXP and {cs.CHESTS_EMOJIS['rare']}`rare chest x1` **as your daily check-in reward!\nYour new balance is **${n_bal:,}**"
		if lvl_up:
			lvl_up_m = random.randint(100,200)*(c_lvl+1)
			text += f"\n\n\U0001f389 Congrats! You levelled up! `({c_lvl} -> {c_lvl+1})` and gained **${lvl_up_m}**"
			await self.bfh.update_balance(player_id = ctx.author.id,amount = lvl_up_m, add = True)
		await ctx.send(text)

	@commands.command(name = 'hourly', aliases = ['h'])
	@has_started()
	@commands.cooldown(1,3, BucketType.user)
	async def _hourly(self, ctx):
		if ctx.interaction is not None:
			await ctx.interaction.response.defer(ephemeral=False)
		# flag = await self.bfh.check_if_exists(ctx.author.id)
		# if not flag:
		# 	return await ctx.send(f"Hey **{ctx.author}**, you don't have an account yet. To create one, run the `{ctx.clean_prefix}start` command! Thanks ")
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
		await self.bfh.update_inventory(player_id=ctx.author.id, _item = 'common_chest', amount = 1)
		text = f"{ctx.author.mention} , You got **${reward}** and <:exp:896086434946097162>**{n_exp-c_exp} EXP and {cs.CHESTS_EMOJIS['common']}`common chest x1` **as your hourly rewards!\nYour new balance is **${n_bal:,}**"
		if lvl_up:
			lvl_up_m = random.randint(100,200)*(c_lvl+1)
			text += f"\n\n\U0001f389 Congrats! You levelled up! `({c_lvl} -> {c_lvl+1})` and gained **${lvl_up_m}**"
			await self.bfh.update_balance(player_id = ctx.author.id,amount = lvl_up_m, add = True)
		await ctx.send(text)

	@commands.command(name = 'weekly', aliases = ['w'])
	@has_started()
	@commands.cooldown(1,3, BucketType.user)
	async def _weekly(self, ctx):
		if ctx.interaction is not None:
			await ctx.interaction.response.defer(ephemeral=False)
		# flag = await self.bfh.check_if_exists(ctx.author.id)
		# if not flag:
		# 	return await ctx.send(f"Hey **{ctx.author}**, you don't have an account yet. To create one, run the `{ctx.clean_prefix}start` command! Thanks ")
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
		await self.bfh.update_inventory(player_id=ctx.author.id, _item = 'legendary_chest', amount = 1)
		text = f"{ctx.author.mention} , You got :\n• **${reward}**\n• <:exp:896086434946097162>**{n_exp-c_exp} EXP**\n• {cs.CHESTS_EMOJIS['legendary']}`legendary chest` **x1** as your weekly check-in reward!\nYour new balance is **${n_bal:,}**"
		if lvl_up:
			lvl_up_m = random.randint(100,200)*(c_lvl+1)
			text += f"\n\n\U0001f389 Congrats! You levelled up! `({c_lvl} -> {c_lvl+1})` and gained **${lvl_up_m:,}**"
			await self.bfh.update_balance(player_id = ctx.author.id,amount = lvl_up_m, add = True)
		await ctx.send(text)

	@commands.command(name = 'monthly', aliases = ['mon', 'm'])
	@has_started()
	@commands.cooldown(1,3, BucketType.user)
	async def _monthly(self, ctx):
		if ctx.interaction is not None:
			await ctx.interaction.response.defer(ephemeral=False)
		# flag = await self.bfh.check_if_exists(ctx.author.id)
		# if not flag:
		# 	return await ctx.send(f"Hey **{ctx.author}**, you don't have an account yet. To create one, run the `{ctx.clean_prefix}start` command! Thanks ")
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
		await self.bfh.update_inventory(player_id=ctx.author.id, _item = 'legendary_chest', amount = 2)
		text = f"{ctx.author.mention} -> You got :\n• **${reward}**\n• <:exp:896086434946097162>**{n_exp-c_exp} EXP**\n• {cs.CHESTS_EMOJIS['legendary']}`legendary chest` **x2** as your monthly check-in reward!\nYour new balance is **${n_bal:,}**"
		if lvl_up:
			lvl_up_m = random.randint(100,200)*(c_lvl+1)
			text += f"\n\n\U0001f389 Congrats! You levelled up! `({c_lvl} -> {c_lvl+1})` and gained **${lvl_up_m:,}**"
			await self.bfh.update_balance(player_id = ctx.author.id,amount = lvl_up_m, add = True)
		await ctx.send(text)

	@commands.command(name = 'work', aliases = ['job', 'j'])
	@has_started()
	@commands.cooldown(1,3, BucketType.user)
	async def work(self, ctx):
		if ctx.interaction is not None:
			await ctx.interaction.response.defer(ephemeral=False)
		# flag = await self.bfh.check_if_exists(ctx.author.id)
		# if not flag:
		# 	return await ctx.send(f"Hey **{ctx.author}**, you don't have an account yet. To create one, run the `{ctx.clean_prefix}start` command! Thanks ")
		#check for cooldown
		current_time = int(time.time())
		cd = await self.bfh.get_cooldown_data(ctx.author.id, 'work')
		if current_time < int(cd):
			return await ctx.send(f"{ctx.author.mention} **You can work again in** `{humanize.precisedelta(cd - current_time)}`")
		reward = random.randint(100, 150)
		n_bal = await self.bfh.update_balance(player_id = ctx.author.id, amount = reward, add = True)
		await self.bfh.update_cooldowns(ctx.author.id, 'work')
		c_exp, n_exp = await self.bfh.update_exp(player_id = ctx.author.id,amount= random.randint(100, 150))
		c_lvl = self.bfh.get_level(c_exp)
		lvl_up = self.bfh.level_up_check(c_exp, n_exp)
		await self.bfh.update_inventory(player_id=ctx.author.id, _item = 'common_chest', amount = 1)
		text = f"{ctx.author.mention} , You earned **${reward}** and <:exp:896086434946097162>**{n_exp-c_exp} EXP and {cs.CHESTS_EMOJIS['common']}`common chest x1` **by working as a programmer(this is just a test, more things will be added soon)!\nYour new balace is **${n_bal}**"
		if lvl_up:
			lvl_up_m = random.randint(100,200)*(c_lvl+1)
			text += f"\n\n\U0001f389 Congrats! You levelled up! `({c_lvl} -> {c_lvl+1})` and gained **${lvl_up_m}**"
			await self.bfh.update_balance(player_id = ctx.author.id,amount = lvl_up_m, add = True)
		await ctx.send(text)

	@commands.command(name = 'loot', aliases= ['l'], help= "soon")
	@is_opted()
	@commands.cooldown(1,10, BucketType.user)
	async def _loot(self, ctx):
		if ctx.interaction is not None:
			await ctx.interaction.response.defer(ephemeral=False)
		

	# @commands.command(name = 'shop', aliases= ['sh'], help= "soon")
	# @has_started()
	# @commands.cooldown(1,3, BucketType.user)
	# async def _shop(self, ctx, item_name : str, amount : int = 1):
	# 	pass

	@commands.command(name = 'buy', aliases= ['b'], help= "Buy an item using your balance. Some items are not buyable")
	@has_started()
	@commands.max_concurrency(1, BucketType.user)
	@commands.cooldown(1,3, BucketType.user)
	async def _buy(self, ctx,amount : typing.Optional[int] = 1,*, item_name : str):
		if ctx.interaction is not None:
			await ctx.interaction.response.defer(ephemeral=False)
		if amount <= 0:
			return await ctx.send(f"{ctx.author} -> please specify a valid amount of items.")
		item_list = [str(item) for item in ALL_ITEMS.keys()]

		item_s_r = difflib.get_close_matches(item_name.lower(),item_list, n=1, cutoff=0.3)
		if len(item_s_r) == 0:
			return await ctx.send(f"No item named `{item_name}`found")
		item_name_n= item_s_r[0]
		if not ALL_ITEMS[item_name_n]['buy_price']:
			return await ctx.send(f"**Sorry, {ALL_ITEMS[item_name_n]['emoji']}`{ALL_ITEMS[item_name_n]['name']}` is not buyable**")
		rec = await self.bfh.get_player_data(ctx.author.id)
		unit_price : int= ALL_ITEMS[item_name_n]['buy_price']
		total_price : int = unit_price*amount
		if rec['balance'] < total_price:
			return await ctx.send(f"{ctx.author.mention}, You don't enough money to buy **{amount}x** {ALL_ITEMS[item_name_n]['emoji']}`{ALL_ITEMS[item_name_n]['name']}`\n\nYou have **${rec['balance']}** but need **${total_price}** to buy them.")

		view = bs.BuyItem(ctx)
		msg = await ctx.send(f"{ctx.author.mention}, Do you want to buy **{amount}x** {ALL_ITEMS[item_name_n]['emoji']}`{ALL_ITEMS[item_name_n]['name']}` for **${total_price}**?\n\nIf yes press the `Buy` button or press the `Cancel` button to cancel.`(timeout=20s)`", view = view)
		await view.wait()
		view.clear_items()
		if not view.confirmation:
			return await msg.edit(f"{ctx.author.mention}, ~~Do you want to buy **{amount}x** {ALL_ITEMS[item_name_n]['emoji']}`{ALL_ITEMS[item_name_n]['name']}` for **${total_price}**?\n\nIf yes press the `Buy` button or press the `Cancel` button to cancel.`(timeout=20s)`~~\n**Cancelled**", view = view)
		else:
			await self.bfh.update_inventory(player_id=ctx.author.id, _item = item_name_n, amount = amount)
			await self.bot.db.execute("UPDATE battlefield SET balance = balance - $1 where p_id = $2;", total_price, ctx.author.id)

			await msg.edit(f"{ctx.author.mention} ->\n{cs.EMOJIS['greentick']} You bought **{amount}x** {ALL_ITEMS[item_name_n]['emoji']}`{ALL_ITEMS[item_name_n]['name']}` for **${total_price}**.", view = view)


	@commands.command(name = 'sell', aliases= ['s'], help= "Sell an item from your inventory.")
	@has_started()
	@commands.max_concurrency(1, BucketType.user)
	@commands.cooldown(1,3, BucketType.user)
	async def _sell(self, ctx,amount : typing.Optional[int] = 1,*, item_name : str):
		if ctx.interaction is not None:
			await ctx.interaction.response.defer(ephemeral=False)
		if amount <= 0:
			return await ctx.send(f"{ctx.author} -> please specify a valid amount of items.")
		item_list = [str(item) for item in ALL_ITEMS.keys()]

		item_s_r = difflib.get_close_matches(item_name.lower(),item_list, n=1, cutoff=0.3)
		if len(item_s_r) == 0:
			return await ctx.send(f"No item named `{item_name}`found")
		item_name_n= item_s_r[0]
		rec = await self.bfh.get_player_data(ctx.author.id)
		count = self.bfh.get_item_count(rec,item_name =  item_name_n)
		if count < amount:
			return await ctx.send(f"{ctx.author.mention}, You have **{count}x** {ALL_ITEMS[item_name_n]['emoji']}`{ALL_ITEMS[item_name_n]['name']}` only, you can't sell more than this amount of {ALL_ITEMS[item_name_n]['emoji']}`{ALL_ITEMS[item_name_n]['name']}`(s)")
		unit_price : int= ALL_ITEMS[item_name_n]['sell_price']
		total_price : int = unit_price*amount
		view = bs.SellItem(ctx)
		msg = await ctx.send(f"{ctx.author.mention}, Do you want to sell **{amount}x** {ALL_ITEMS[item_name_n]['emoji']}`{ALL_ITEMS[item_name_n]['name']}` from your inventory for **${total_price}**?\n\nIf yes press the `Sell` button or press the `Cancel` button to cancel.`(timeout=20s)`", view = view)
		await view.wait()
		view.clear_items()
		if not view.confirmation:
			return await msg.edit(f"{ctx.author.mention}, ~~Do you want to sell **{amount}x** {ALL_ITEMS[item_name_n]['emoji']}`{ALL_ITEMS[item_name_n]['name']}` from your inventory for **${total_price}**?\n\nIf yes press the `Sell` button or press the `Cancel` button to cancel.`(timeout=20s)`~~\n**Cancelled**", view = view)
		else:
			await self.bfh.update_inventory(player_id=ctx.author.id, _item = item_name_n, amount = -amount)
			await self.bot.db.execute("UPDATE battlefield SET balance = balance + $1 where p_id = $2;", total_price, ctx.author.id)

			await msg.edit(f"{ctx.author.mention} ->\n{cs.EMOJIS['greentick']} You sold **{amount}x** {ALL_ITEMS[item_name_n]['emoji']}`{ALL_ITEMS[item_name_n]['name']}` from your inventory for **${total_price}**.", view = view)


	@commands.command(name = 'trade', aliases= ['tr'], help= "Trade items with other players following trade guidelines and rules.")
	@has_started()
	@commands.max_concurrency(1, BucketType.user)
	@commands.cooldown(1,10, BucketType.user)
	async def _trade(self, ctx, player : discord.Member):
		if ctx.interaction is not None:
			await ctx.interaction.response.defer(ephemeral=False)
		player1 = ctx.author
		player2 = player
		flag = await self.bfh.check_if_exists(player2.id)
		if not flag:
			return await ctx.send(f"**{player2}** hasn't started playing battlefield yet! You can't trade with them before he starts playing")
		rec1 = await self.bfh.get_player_data(player1.id)
		rec2 = await self.bfh.get_player_data(player2.id)
		p1_level = self.bfh.get_level(rec1['exp'])
		p2_level = self.bfh.get_level(rec2['exp'])
		if p1_level < 4 or p2_level < 4:
			return await ctx.send(f"{player1} and {player2}, sorry , one/both of you two haven't reached **Level 4** yet. You can't trade with one another before both of you reach level 4!")
		view = bs.TradeConfirmView(player2)
		msg = await ctx.send(f"{player2.mention} -> {player1.mention} wants to trade with you?\nIf you want to trade with them then press **Trade** or press **Cancel** to cancel.`(timeout=60s)`", view = view)
		await view.wait()
		view.clear_items()
		if not view.confirmation:
			return await msg.edit(f"{player2.mention} -> {player1.mention} ~~wants to trade with you!\nIf you want to trade with them then press **Trade** or press **Cancel** to cancel.`(timeout=60s)`~~\n**Trade Cancelled**", view = view)
		elif view.confirmation:
			lock1 = UserLock(player1, "You can't use other commands while you are in an active trade!")
			lock2 = UserLock(player2, "You can't use other commands while you are in an active trade!")
			async with lock1(self.bot), lock2(self.bot):
				await msg.edit(view = view)
				value1 = 0
				value2 = 0
				p1_all_items = self.bfh.get_inv_all_items_dict(rec1)
				p2_all_items = self.bfh.get_inv_all_items_dict(rec2)
				p12_all_items_dict = {
					str(player1.id) : p1_all_items,
					str(player2.id) : p2_all_items
				}
				p1td = {}
				p2td = {}
				p12_tdict = {
					str(player1.id) : p1td,
					str(player2.id) : p2td
				}
				p12_tm = {
					str(player1.id) : 0,
					str(player2.id) : 0
				}
				p12rec = {
					str(player1.id) : rec1,
					str(player2.id) : rec2
				}
				embed = discord.Embed(color=0x2F3136,  title = "**__Trade menu__**")
				t_view = bs.Tradeview(ctx = ctx ,player1= player1, player2= player2, bfh = self.bfh, embed = embed)
				const_str = f" - To add items:\n ╰ `add <amount> <item_name>`\n - To remove items:\n ╰ `add <amount> <item_name>`\n - To add/remove cash money:\n ╰ `money +<amount>` | `money -<amount>`\n You can confirm the trade after the trade has been validated!\n"
				
				embed.description = const_str +f"** - Trade validated ?** : {cs.EMOJIS['greentick'] if t_view.validated else cs.EMOJIS['redtick']}"
				embed.add_field(name = f"__{player1}__", value = "\u2800", inline= False)
				embed.add_field(name = f"**Total value**:", value = f"${value1}", inline= False)
				embed.add_field(name = f"__{player2}__", value = "\u2800", inline= False)
				embed.add_field(name = f"**Total value**:", value = f"${value2}", inline= False)
				embed.set_footer(text=f"type proceed after both of you accept/confirm the trade by pressing the button!")
				await msg.edit(f"<a:greenDot:877638573099200512>**Trade ongoing between **{player1.mention} and {player2.mention}......", embed = embed, view = t_view)
				def check(message):
					auth_c : bool = (message.author == player1) or (message.author == player2)
					#msg_c : bool = message.content.startswith('add') or message.content.startswith('remove')
					return auth_c #and msg_c
				should_proceed = False
				while True:
					if t_view.cancelled:
						await msg.edit(content= f"{cs.EMOJIS['redtick']}**Trade cancelled by {t_view.cancelled_by}**", view = t_view)
						break
					elif t_view.confim_dict[str(player1.id)] and t_view.confim_dict[str(player2.id)]:
						t_view.clear_items()
						t_view.stop()

						await msg.edit(content= f"{cs.EMOJIS['greentick']}**Trade confirmed and is being processed!**", view = t_view)
						should_proceed = True
						break
					try:
						inp : discord.Message = await self.bot.wait_for('message', check = check, timeout=60.0)

					except asyncio.TimeoutError:
						t_view.clear_items()
						t_view.stop()
						await msg.edit(f"{cs.EMOJIS['redtick']} Trade cancelled due to timeout", view = t_view)
						break
					else:
						if inp.content.lower().startswith('add'):
							itm_am_name = inp.content[4:]
							try:
								amount = int(itm_am_name[0])
								if amount <= 0:
									continue
							except ValueError:
								continue
							else:
								item_inp = itm_am_name.split(' ',1)[-1]
								p_a_d = p12_all_items_dict.get(str(inp.author.id))
								item_res_l = difflib.get_close_matches(item_inp, p_a_d.keys(), n = 1, cutoff= 0.4 )
								if len(item_res_l) == 0:
									continue
								item_res = item_res_l[0]
								p_t_d = p12_tdict.get(str(inp.author.id))
								p_t_m : int = p12_tm.get(str(inp.author.id))
								if p_a_d[item_res] <= 0 :
									continue
								elif p_a_d[item_res] < amount:
									try:
										p_t_d[item_res] += p_a_d[item_res]
										p_a_d[item_res] = 0
									except KeyError:
										p_t_d[item_res] = p_a_d[item_res]
										p_a_d[item_res] = 0
								else:
									try:
										p_t_d[item_res] += amount
										p_a_d[item_res] -=amount
									except KeyError:
										p_t_d[item_res] = amount
										p_a_d[item_res] -=amount
								eph_str = ""
								for i, c in p_t_d.items():
									if c <=0:
										continue
									eph_str+=f"{ALL_ITEMS[i]['emoji']}`{ALL_ITEMS[i]['name']}` **x{c}**\n"
								eph_str+=f"\n**Cash Money**: ${p_t_m}"
								eph_val = self.bfh.get_value_from_dict(p_t_d) + p_t_m
								if inp.author == ctx.author:
									item_ind = 0
									val_ind = 1
								else:
									item_ind = 2
									val_ind = 3
								embed.set_field_at(item_ind,name = f"__{inp.author}__", value = eph_str, inline= False)
								embed.set_field_at(val_ind,name = f"**Total value**:", value = f"${eph_val}", inline= False)

						elif inp.content.lower().startswith('remove'):
							itm_am_name = inp.content[7:]
							try:
								amount = int(itm_am_name[0])
								if amount <= 0:
									continue
							except ValueError:
								continue
							else:
								p_a_d = p12_all_items_dict.get(str(inp.author.id))
								item_inp = itm_am_name.split(' ',1)[-1]
								p_t_d = p12_tdict.get(str(inp.author.id))
								if len(p_t_d) == 0:
									continue
								item_res_l = difflib.get_close_matches(item_inp, p_t_d.keys(), n = 1, cutoff= 0.4 )
								if len(item_res_l) == 0:
									continue
								item_res = item_res_l[0]
								p_t_m : int = p12_tm.get(str(inp.author.id))
								if p_t_d[item_res] <= 0 :
									continue
								elif p_t_d[item_res] < amount:
									p_a_d[item_res]+= p_t_d[item_res]
									p_t_d[item_res] = 0
								else:
									p_a_d[item_res]+= amount
									p_t_d[item_res] -= amount
								eph_str = ""
								for i, c in p_t_d.items():
									if c <=0:
										continue
									eph_str+=f"{ALL_ITEMS[i]['emoji']}`{ALL_ITEMS[i]['name']}` **x{c}**\n"
								eph_str+=f"\n**Cash Money**: ${p_t_m}"
								eph_val = self.bfh.get_value_from_dict(p_t_d) + p_t_m
								if inp.author == ctx.author:
									item_ind = 0
									val_ind = 1
								else:
									item_ind = 2
									val_ind = 3
								embed.set_field_at(item_ind,name = f"__{inp.author}__", value = eph_str, inline= False)
								embed.set_field_at(val_ind,name = f"**Total value**:", value = f"${eph_val}", inline= False)

						elif inp.content.lower().startswith('money'):
							
							try:
								in_amount = int(inp.content.split(' ')[-1])
								
							except ValueError as excp:
								print(excp)
								continue
							else:
								p_r = p12rec.get(str(inp.author.id))
								p_t_m : int = p12_tm.get(str(inp.author.id))
								if in_amount == 0:
									continue
								elif in_amount > 0 and in_amount > p_r['balance']:
									p12_tm[str(inp.author.id)] =p_r['balance']
								elif in_amount > 0 and in_amount <= p_r['balance']:
									p12_tm[str(inp.author.id)]+=in_amount
								elif in_amount < 0 and p_t_m == 0:
									continue
								elif in_amount < 0 and (p_t_m + in_amount) < 0:
									continue
								elif in_amount < 0 and (p_t_m + in_amount) >= 0:
									p12_tm[str(inp.author.id)]+=in_amount
								else:
									continue
								p_t_d = p12_tdict.get(str(inp.author.id))
								eph_str = ""
								for i, c in p_t_d.items():
									if c <=0:
										continue
									eph_str+=f"{ALL_ITEMS[i]['emoji']}`{ALL_ITEMS[i]['name']}` **x{c}**\n"
								eph_str+=f"\n**Cash Money**: ${p12_tm[str(inp.author.id)]}"
								eph_val = self.bfh.get_value_from_dict(p_t_d) + p12_tm[str(inp.author.id)]
								if inp.author == ctx.author:
									item_ind = 0
									val_ind = 1
								else:
									item_ind = 2
									val_ind = 3
								embed.set_field_at(item_ind,name = f"__{inp.author}__", value = eph_str, inline= False)
								embed.set_field_at(val_ind,name = f"**Total value**:", value = f"${eph_val}", inline= False)
						p1ttv = int(embed.fields[1].value.split('$',1)[-1])
						p2ttv = int(embed.fields[3].value.split('$',1)[-1])
						difference = abs(p1ttv - p2ttv)
						if p1ttv > 0 and p2ttv > 0 and difference < 10000:
							t_view.validated = True
							t_view.trade_confirm.disabled = False
						else:
							t_view.validated = False
							t_view.trade_confirm.disabled = True
						t_valid_str = f"** - Trade validated ?** : {cs.EMOJIS['greentick'] if t_view.validated else cs.EMOJIS['redtick']}"
						embed.description = const_str + t_valid_str
						await msg.edit(embed = embed, view = t_view)
				if should_proceed:
					p1inverted = self.bfh.invert_dict_values(p1td)
					p1finald = self.bfh.smart_dict_update(p1inverted, p2td)
					p2inverted = self.bfh.invert_dict_values(p2td)
					p2finald = self.bfh.smart_dict_update(p2inverted, p1td)
					await self.bfh.smart_bulk_upd_inv(player_id= player1.id, items_dict= p1finald)
					await self.bfh.smart_bulk_upd_inv(player_id= player2.id, items_dict= p2finald)
					p1finalbal = rec1['balance'] - p12_tm[str(player1.id)] + p12_tm[str(player2.id)]
					p2finalbal = rec2['balance'] - p12_tm[str(player2.id)] + p12_tm[str(player1.id)]
					await self.bot.db.execute("UPDATE battlefield SET balance = $1 WHERE p_id = $2;", p1finalbal, player1.id)
					await self.bot.db.execute("UPDATE battlefield SET balance = $1 WHERE p_id = $2;", p2finalbal, player2.id)
					await ctx.send(f"{cs.EMOJIS['greentick']} Trade has been processed for {player1} and {player2}")

	@commands.command(name= 'equip', aliases = ['eq', 'attach'], help = "Equip a weapon or armour from your inventory")
	@has_started()
	@commands.max_concurrency(1, BucketType.user)
	@commands.cooldown(1,5, BucketType.user)
	async def _equip(self, ctx,*, item_name : str):
		if ctx.interaction is not None:
			await ctx.interaction.response.defer(ephemeral=False)
		item_list = [str(item) for item in ALL_ITEMS.keys() if ALL_ITEMS[str(item)]['type'] == 'weapon' or ALL_ITEMS[str(item)]['type'] == 'armour']
		item_s_r = difflib.get_close_matches(item_name.lower(),item_list, n=1, cutoff=0.3)
		if len(item_s_r) == 0:
			return await ctx.send(f"`{item_name}` is not a valid item or this item can't not be equipped")
		item_name_n= item_s_r[0]
		item_type : str= ALL_ITEMS[item_name_n]['type']
		current_time = int(time.time())
		if item_type == 'weapon':
			cd = await self.bfh.get_cooldown_data(ctx.author.id, 'w_equip')
			if current_time < int(cd):
				return await ctx.send(f"{ctx.author.mention} ->**You're on cooldown!**\nYou can equip any new weapon again in `{humanize.precisedelta(cd - current_time)}`")
			rec = await self.bfh.get_player_data(ctx.author.id)
			current_weapon, _ = self.bfh.get_equipments(rec)
			extras = f"- Your current equipped weapon ({ALL_ITEMS[current_weapon]['emoji']}`{ALL_ITEMS[current_weapon]['name']}`) will be returned to your inventory." if current_weapon else ''
		elif item_type == 'armour':
			rec = await self.bfh.get_player_data(ctx.author.id)
			_ , current_armour = self.bfh.get_equipments(rec)
			extras = f"- Your current equipped armour ({ALL_ITEMS[current_armour]['emoji']}`{ALL_ITEMS[current_armour]['name']}`) will **NOT** be returned to your inventory." if current_armour else ''
		item_rarity : str = ALL_ITEMS[item_name_n]['rarity']
		
		count = self.bfh.get_item_count(rec, item_name = item_name_n)
		if count <=0 :
			return await ctx.send(f"{ctx.author.mention} -> You don't have any {ALL_ITEMS[item_name_n]['emoji']}`{ALL_ITEMS[item_name_n]['name']}` in your inventory to equip!")
		view = bs.EquipItem(ctx)

		msg = await ctx.send(f"{ctx.author.mention} -> Do you want to equip {ALL_ITEMS[item_name_n]['emoji']}`{ALL_ITEMS[item_name_n]['name']}` from your inventory?\n{extras}\nIf yes then press the *Equip* button or press the *Cancel* button to cancel. (`timeout = 20s`)", view = view)
		await view.wait()
		view.clear_items()
		if not view.confirmation:
			return await msg.edit(f"{ctx.author.mention} -> ~~Do you want to equip {ALL_ITEMS[item_name_n]['emoji']}`{ALL_ITEMS[item_name_n]['name']}` from your inventory?\n{extras}\nIf yes then press the *Equip* button or press the *Cancel* button to cancel. (`timeout = 20s`)~~\n**Cancelled**", view = view)
		elif view.confirmation:
		
			eq_dict : dict= json.loads(rec['equipments'])
			eq_dict[item_type] = item_name_n
			eq_json = json.dumps(eq_dict)
			inv_dict : dict = json.loads(rec[item_rarity])
			inv_dict[item_name_n]-=1
			
			if item_type == 'armour':
				inv_json = json.dumps(inv_dict)
				arm_points : int = ALL_ITEMS[item_name_n]['shield_points']
				query = f"UPDATE battlefield SET {item_rarity} = $1, equipments = $2 , sp = $3 WHERE p_id = $4;"
				await self.bot.db.execute(query, inv_json, eq_json, arm_points, ctx.author.id)
				return await msg.edit(f"{ctx.author.mention} -> {cs.EMOJIS['greentick']} You've equipped {ALL_ITEMS[item_name_n]['emoji']}`{ALL_ITEMS[item_name_n]['name']}` from you inventory.\nNow you have {arm_points} {self.bfh.get_bar_emojis('armour', 100,100)} `armour points`", view = view)

			else:
				
				if current_weapon:
					current_rarity : str = ALL_ITEMS[current_weapon]['rarity'] 
					
					if current_rarity == item_rarity:
						w_count_n = inv_dict.get(current_weapon, 0)
						inv_dict[current_weapon] = w_count_n + 1
						query = f"UPDATE battlefield SET {item_rarity} = $1, equipments = $2 WHERE p_id = $3;"
						inv_json = json.dumps(inv_dict)
						await self.bot.db.execute(query, inv_json, eq_json, ctx.author.id)
					else:
						current_inv_dict : dict = json.loads(rec[current_rarity])

						w_count = current_inv_dict.get(current_weapon, 0)
						current_inv_dict[current_weapon] = w_count + 1
						current_inv_json = json.dumps(current_inv_dict)
						query = f"UPDATE battlefield SET {item_rarity} = $1,{current_rarity} = $2, equipments = $3 WHERE p_id = $4;"
						inv_json = json.dumps(inv_dict)
						await self.bot.db.execute(query, inv_json,current_inv_json, eq_json, ctx.author.id)
					
					
					_extra_str = f"{ALL_ITEMS[current_weapon]['emoji']}`{ALL_ITEMS[current_weapon]['name']}` x1 was returned to your inventory."
				else:
					query = f"UPDATE battlefield SET {item_rarity} = $1, equipments = $2 WHERE p_id = $3;"
					inv_json = json.dumps(inv_dict)
					await self.bot.db.execute(query, inv_json, eq_json, ctx.author.id)
					_extra_str = f""

				await self.bfh.update_cooldowns(ctx.author.id, 'w_equip')
				return await msg.edit(f"{ctx.author.mention} -> {cs.EMOJIS['greentick']} You've equipped {ALL_ITEMS[item_name_n]['emoji']}`{ALL_ITEMS[item_name_n]['name']}` from your inventory.\n{_extra_str}", view = view)




	@commands.command(name = 'attack', aliases= ['a'], help= "Attack other players using your equipped weapon")
	@commands.guild_only()
	@can_attack()
	@commands.max_concurrency(1, BucketType.user)
	@commands.cooldown(1,5, BucketType.user)
	async def _attack(self, ctx, target : discord.Member):
		if ctx.interaction is not None:
			await ctx.interaction.response.defer(ephemeral=False)
		current_time = int(time.time())
		cd = await self.bfh.get_cooldown_data(ctx.author.id, 'attack')
		if current_time < int(cd):
			return await ctx.send(f"{ctx.author.mention} ->**You're on attack cooldown!**\nYou can attack again in `{humanize.precisedelta(cd - current_time)}`")
		target_id = target.id
		player_id = ctx.author.id
		if target == ctx.author:
			return await ctx.send("You can't attack yourself, L")

		flag_2 = await self.bfh.check_if_exists(target_id)
		if not flag_2:
			return await ctx.send(f"**{target}** hasn't started playing battlefield yet! You can't attack them before they starts playing and opt in!")
		
		t_rec = await self.bfh.get_player_data(target_id)
		if not t_rec['opt_status']:
			return await ctx.send(f"**{target}** is `not opted in` to the Battlefield currently, you can't attack them rn!")
		if t_rec['invisibility'] > int(time.time()):
			return await ctx.send(f"{ctx.author.mention} -> This player was attacked within the last 10 minutes. You can't attack them rn!")
		a_rec = await self.bfh.get_player_data(player_id)
		a_weapon , a_armour = self.bfh.get_equipments(a_rec)
		
		

		view = bs.AttackView(ctx)
		msg = await ctx.send(f"{ctx.author.mention} -> Do you want to attack **{target}** using your {ALL_ITEMS[str(a_weapon)]['emoji']}**{ALL_ITEMS[str(a_weapon)]['name']}**?\nIf yes then press the *Attack* button or press the *Cancel* button to cancel.(`timeout = 20s`)", view = view)
		await view.wait()
		view.clear_items()
		if not view.confirmation:
			return await msg.edit(f"{ctx.author.mention} -> ~~Do you want to attack **{target}** using your {ALL_ITEMS[str(a_weapon)]['emoji']}**{ALL_ITEMS[str(a_weapon)]['name']}**?\nIf yes then press the *Attack* button or press the *Cancel* button to cancel.(`timeout = 20s`)~~\n**Cancelled**", view = view)
		elif view.confirmation:


			attack_engine = AttackEngine(bot = self.bot, bfh = self.bfh,attacker = ctx.author, a_rec = a_rec, target = target, t_rec = t_rec)

			text = await attack_engine.attack()
			if 'killed' in text:
				await self.bfh.update_attack_or_heal_cd(player_id= player_id, command_name= 'attack', item_used=a_weapon)
				await msg.edit(f"{text}", view = view)
				
			await self.bfh.update_attack_or_heal_cd(player_id= player_id, command_name= 'attack', item_used=a_weapon)
			await msg.edit(f"{text}", view = view)

	@commands.command(name = 'heal', aliases= ['healing'], help= "heal/ increase your healthpoints using a healing item from your inventory.")
	@has_started()
	@commands.max_concurrency(1, BucketType.user)
	@commands.cooldown(1,3, BucketType.user)
	async def _heal(self, ctx,*, healing_item : str = None):
		if ctx.interaction is not None:
			await ctx.interaction.response.defer(ephemeral=False)
		player_id = ctx.author.id
		rec = await self.bfh.get_player_data(player_id)
		all_items_dict = self.bfh.get_inv_all_items_dict(rec)
		if healing_item is None:
			ava_heal_items = [str(i) for i , c in all_items_dict.items() if c > 0 and ALL_ITEMS[str(i)]['type'] == 'healing']
			if len(ava_heal_items) == 0:
				return await ctx.send(f"{ctx.author.mention} -> You don't have any healing items in your inventory! \nBuy any healing items and use `{ctx.clean_prefix}heal [healing_item]` to heal/increase your healthpoints.")
			h_str = ""
			for _item in ava_heal_items:
				h_str+=f"• {ALL_ITEMS[_item]['emoji']} **{all_items_dict[_item]}x** `{ALL_ITEMS[_item]['name']}`\n"
			return await ctx.send(f"{ctx.author.mention} -> You have the following healing item(s) in your inventory:\n{h_str}\nTo use a healing item, use `{ctx.clean_prefix}heal <healing_item>` to **heal/increase** your healthpoints.")
		

		healing_items_list = [str(hi) for hi in ALL_ITEMS.keys() if ALL_ITEMS[str(hi)]['type']=='healing']
		heal_s_r = difflib.get_close_matches(healing_item.lower(),healing_items_list, n=1, cutoff=0.3)
		if len(heal_s_r) == 0:
			return await ctx.send(f"No healing item named `{healing_item}`found")

		current_hp : int = rec['hp']
		cd_dict = self.bfh.get_cd_dict_from_rec(rec)
		if cd_dict['n_heal'] > int(time.time()):
			return await ctx.send(f"{ctx.author.mention}, You're on healing cooldown!\nYou can use any healing item again in `{humanize.precisedelta(cd_dict['n_heal']-int(time.time()))}`")
		heal_name_n= heal_s_r[0]
		count  : int = all_items_dict.get(heal_name_n, 0)
		if count <= 0:
			return await ctx.send(f"{ctx.author.mention} -> You don't have any {ALL_ITEMS[heal_name_n]['emoji']} `{ALL_ITEMS[heal_name_n]['name']}` in your inventory to use.")
		
		if current_hp == 100:
			return await ctx.send(f"{ctx.author} , You already have full healthpoints (100/100) {self.bfh.get_bar_emojis('hp', 100, 100)}\nNo need to use any healing item rn.")
		view = bs.HealView(ctx)
		msg = await ctx.send(f"{ctx.author.mention} -> You currently have {current_hp}/100 {self.bfh.get_bar_emojis('hp', current_hp, 100)} `hp`. \nDo you want to use {ALL_ITEMS[heal_name_n]['emoji']}**x1** `{ALL_ITEMS[heal_name_n]['name']}` to heal/increase your `hp`?\nIf yes , press the **Heal** button or press the **Cancel** button to cancel.`(timeout = 20s)`", view = view)
		await view.wait()
		view.clear_items()
		if not view.confirmation:
			return await msg.edit(f"{ctx.author.mention} -> ~~You currently have {current_hp}/100 {self.bfh.get_bar_emojis('hp', current_hp, 100)} `hp`. \nDo you want to use {ALL_ITEMS[heal_name_n]['emoji']}**x1** `{ALL_ITEMS[heal_name_n]['name']}` to heal/increase your `hp`?\nIf yes , press the **Heal** button or press the **Cancel** button to cancel.`(timeout = 20s)`~~\n**Cancelled**", view = view)

		elif view.confirmation:
			healing_range = ALL_ITEMS[heal_name_n]['hp_recover'].split('-')
			min_hp, max_hp = int(healing_range[0]),int(healing_range[1])
			healed = random.randint(min_hp, max_hp)
			if current_hp + healed >= 100:
				updated_hp = 100
			else:
				updated_hp = current_hp+healed

			updated_dict = {heal_name_n : -1}
			await self.bot.db.execute("UPDATE battlefield SET hp = $1 WHERE p_id = $2;", updated_hp, player_id)
			await self.bfh.bulk_update_inventory(player_id=player_id, items_dict= updated_dict)
			await self.bfh.update_attack_or_heal_cd(player_id=player_id, command_name='heal',item_used=heal_name_n)
			return await msg.edit(f"{ctx.author.mention} -> You used {ALL_ITEMS[heal_name_n]['emoji']}**x1** `{ALL_ITEMS[heal_name_n]['name']}` and healed yourself.\nNow you have {updated_hp}/100 {self.bfh.get_bar_emojis('hp', updated_hp, 100)} `hp`", view = view)


	@commands.command(name = 'quickfight', aliases = ['qf', 'quickf'], brief = "A quick fight mode without any attack or heal cooldowns", help = "A quick fight mode that has no cooldowns for attack or heal and no need to opt in. costs nothing from the inventory!")
	@commands.guild_only()
	@has_started()
	@commands.max_concurrency(1, BucketType.user)
	@commands.cooldown(1, 30, BucketType.user)
	async def quickfight(self, ctx, player : discord.Member):
		if ctx.interaction is not None:
			await ctx.interaction.response.defer(ephemeral=False)
		player1 = ctx.author
		player2 = player
		flag = await self.bfh.check_if_exists(player2.id)
		if not flag:
			return await ctx.send(f"**{player2}** hasn't started playing battlefield yet! You can't attack them before they starts playing!")

		view = bs.QuickFightConfirmation(ctx, player2)
		msg = await ctx.send(f"**{player2}**, {ctx.author.mention} has invited you to a quickfight match! \nYou have `90s` to **Accept** or **Reject** their invitation!", view = view)

		await view.wait()
		view.clear_items()
		if not view.accepted:
			return await msg.edit(f"~~**{player2}**, {ctx.author.mention} has invited you to a quickfight match! \nYou have `90s` to **Accept** or **Reject** their invitation!~~\n**Quickfight cancelled**", view = view)
		elif view.accepted:
			await msg.edit(f"Invite accepted! Now prepare for fight...", view = view)
			
			embed1 = discord.Embed(title= f"**{player1}**'s status:" ,color=0x2F3136, description= f"**__Healthpoints__**: 100/100 {self.bfh.get_bar_emojis('hp', 100, 100)}")
			embed2 = discord.Embed(title= f"**{player2}**'s status:" ,color=0x2F3136, description= f"**__Healthpoints__**: 100/100 {self.bfh.get_bar_emojis('hp', 100, 100)}")
			
			rn = random.randint(0,1)
			if rn == 1:
				player1, player2 = player1, player2
			elif rn == 0:
				player1, player2 = player2, player1

			qf_view = bs.QuickFightView(ctx = ctx,player1=player1, player2= player2, bfh = self.bfh, embed1= embed1, embed2=embed2)
			
			qf_msg = await ctx.send(f"{player1.mention}, It's your turn to `fight` or `heal`!", embeds = [embed1, embed2] ,view = qf_view)

	@commands.command(name = "trivia", aliases = ['tri'], help = "Answer trivia questions and earn money and exp from it.", hidden = True)
	@commands.guild_only()
	@commands.max_concurrency(1, BucketType.user)
	@commands.cooldown(1, 10, BucketType.user)
	async def trivia(self, ctx):
		url = "https://opentdb.com/api.php?amount=10&type=multiple"
		async with self.bot.session.get(url) as resp:
			js = await resp.json()
			if not js['response_code'] == 0:
				return await ctx.send(f"Something went wrong, can't get any questions for you rn.")
		

	@commands.command(name= 'players', aliases = ['player', 'activeplayers'], help = "Shows currently opted in players count and information", slash_command = False)
	@commands.guild_only()
	@commands.cooldown(1,3, BucketType.user)
	async def players(self, ctx):
		total_players = await self.bot.db.fetchval("SELECT count(*) FROM battlefield;")
		opted_list = len(await self.bot.db.fetch("SELECT p_id FROM battlefield WHERE opt_status = $1", True))
		embed = discord.Embed(title = "Player count for Snowden's Battlefield!", color = 0x2F3136)
		embed.description = f"**__Total players__**: {total_players}\n\n\n**__Opted in__**: {opted_list}"
		await ctx.send(embed = embed)

	@commands.command(name = "leaderboard", aliases = ['lb'], hidden = True, help = "Battlefield Leaderboard according to player values.")
	@commands.guild_only()
	@commands.cooldown(1,60, BucketType.user)
	async def leaderboard(self, ctx):
		...

	

def setup(bot):
	bot.add_cog(Battlefield(bot))

