import discord
from discord import embeds
from discord.ext import commands
import asyncpg
import typing
import random

from discord.ext.commands.cooldowns import Cooldown
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
	async def _start(self, ctx):
		player_id = ctx.author.id
		flag = await self.bfh.check_if_exists(player_id)
		if flag:
			return await ctx.send("**You already have an account, you can keep playing!**")
		await self.bot.db.execute(""" INSERT INTO battlefield (p_id, created_at) VALUES ($1, $2); """, player_id, int(ctx.message.created_at.timestamp()))
		await self.bot.db.execute(""" INSERT INTO inventory (p_id, common, rare, legendary, epic, mythic) VALUES ($1, $2, $3,$4, $4,$4); """, player_id, '{"police_vest_level_1" : 1}','{"rare_chest" : 1, "pain_killer" : 1 }', '{}')

		embed = discord.Embed(title = f"Hey {ctx.author.name}, \U0001f44b Welcome to Snowden's BattleField!!", description = f"**\nYou got **$500** and <:exp:896086434946097162>**100 EXP** as a reward for entering the battlefield!\nYou also got:\n{cs.CHESTS_EMOJIS['rare']}`rare_chest x1`\n{ALL_ITEMS['police_vest_level_1']['emoiji']}`police_vest_level_1 x1`\n{ALL_ITEMS['pain_killer']['emoji']}`pain_killer x1`\nHope you enjoy!", color = 0x2F3136)
		await ctx.send(embed = embed)


def setup(bot):
	bot.add_cog(BattleField(bot))

