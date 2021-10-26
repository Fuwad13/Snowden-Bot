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
import constants as cs

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
		await ctx.send(embed = embed)

	@commands.command(name= 'inventory', aliases = ['inv'], brief= "Shows player inventory", help = "Shows player inventory, only if the user has an account.")
	@commands.cooldown(1,5, type= BucketType.user)
	async def _inventory(self, ctx, player : typing.Union[discord.Member, discord.User] = None):
		if player is None:
			if ctx.message.reference:
				player = ctx.message.reference.resolved.author.id
			else:
				player = ctx.author.id
		player_id = player.id
		flag = await self.bfh.check_if_exists(player_id)
		if not flag:
			return await ctx.send(f"{player} hasn't started playing Battlefield yet, run {ctx.clean_prefix}start to start playing!")
		t1, t2 = await self.bfh.get_player_data(player_id)
		inv_value = self.bfh.get_inventory_value(t2)
		embed = discord.Embed(title = f"**__{player}'s Inventory__**",color = 0x2F3136)
		text = f"\U0001f3e6 **Balance**: ${t2['balance']}\n\U0001f4bc **Inventory Value**: ${inv_value}\n\U0001f4c8 **Level**: {self.bfh.get_level(t2['exp'])}\n\U00002694 **Opt in status**: {cs.EMOJIS['greentick'] if t1['opt_status'] else cs.EMOJIS['redtick']}\n"
		embed.description = text
		await ctx.send(embed= embed)


	


def setup(bot):
	bot.add_cog(BattleField(bot))

