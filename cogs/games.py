import discord
from discord import embeds
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
			return await ctx.send(f"{player} hasn't started playing Battlefield yet, run {ctx.clean_prefix}start to start playing!")
		t1, t2 = await self.bfh.get_player_data(player_id)
		inv_value = self.bfh.get_inventory_value(t2)

		embed = discord.Embed(title = f"**__{player}'s Inventory__**",color = 0x2F3136)
		text = f"\U0001f3e6 **Balance**: ${t2['balance']}\n\U0001f4bc **Inventory Value**: ${inv_value}\n\U00002728 **Player value**: {t2['balance']+inv_value}\n\U0001f4c8 **Level**: {self.bfh.get_level(t2['exp'])}\n\U00002694 **Opt in status**: {cs.EMOJIS['greentick'] if t1['opt_status'] else cs.EMOJIS['redtick']}\n"
		embed.add_field(name='Status/profile', value=text)
		embed.add_field(name="\U00002764 Health", value=f"soon")
		embed.add_field(name="\U0001f6e1 Shield", value="soon")

		inv_items = self.bfh.get_inventory_items(t2)
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
		player_id = ctx.author
		flag = await self.bfh.check_if_exists(player_id)
		if not flag:
			return await ctx.send(f"{ctx.author} hasn't started playing Battlefield yet, run {ctx.clean_prefix}start to start playing!")
		opted_in = await self.bfh.get_opt_status(player_id)
		n_opt : int= await self.bfh.get_cooldown_data(player_id,'n_opt_in_toggle')
		c_opt = self.bfh.can_opt_out(n_opt)

		embed = discord.Embed(title=f"{cs.EMOJIS['toggle_on'] if opted_in else cs.EMOJIS['toggle_off']} {ctx.author}'s opt in status:",color = 0x2F3136)
		text =f"You're currently {'**Opted in**' if opted_in else '**Opted out**'}!\n"
		if not c_opt:
			text+=f"Seems like you are on cooldown! You need to wait `{humanize.precisedelta(n_opt-int(time.time()))}` before you can toggle your `opt status`"
			embed.description= text
			return await ctx.send(f"{ctx.author.mention} ->", embed = embed)
		text+=f"If you want to toggle your `opt status` then press `Confirm` or else press `Cancel` to cancel in next **30s**!"
		embed.description = text
		view = bs.ConfirmOrCancel(ctx, timeout=30)
		view.msg = await ctx.send(f"{ctx.author.mention} ->", embed = embed, view = view)
		await view.wait()
		view.clear_items()
		if view.value == True:
			ch = await self.bfh.set_opt_status(player_id, not opted_in)
			embed.description+=f"\n{cs.EMOJIS['toggle_on'] if ch else cs.EMOJIS['toggle_off']} You've successfully toggled your `opt status`"
			await view.msg.edit(embed = embed, view = view)

		elif view.value == False:
			embed.description+=f"\n{cs.EMOJIS['redtick']} You chose to stay {'**Opted in**' if opted_in else '**Opted out'}"
			await view.msg.edit(embed = embed, view = view)

		elif view.value == None:
			embed.description+=f"\n:warning: You took too long to respond!"
			await view.msg.edit(embed = embed, view = view)	



	@commands.group(name= 'open', aliases = ['unbox', 'o'], brief= "Open chest(s) from your inventory", help= "Open chests to get random game items!Chances of getting items are based on their rarity.You might get items with higher tier rarity from a lower tier chest.", invoke_without_command= True)
	@commands.cooldown(1,2, BucketType.user)
	async def _open(self, ctx):
		pass


	

def setup(bot):
	bot.add_cog(BattleField(bot))

