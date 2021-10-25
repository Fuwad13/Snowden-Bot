import discord
import asyncpg
import constants as cs
import time
import json

class BattleFieldHelper:
	def __init__(self, bot):
		self.bot = bot

	async def check_if_exists(self, player_id):
		flag = False
		player = await self.bot.db.fetchval(""" SELECT p_id FROM battlefield WHERE p_id = $1 """, player_id)
		if player:
			flag = True
		else:
			flag = False
		return flag

	async def update_exp(self, *,player_id :int, amount, add :bool = True ):
		if add == True:
			c_exp = await self.bot.db.fetchval(""" SELECT exp FROM battlefield WHERE p_id = $1 ;""", player_id)
			n_exp = int(c_exp) + amount
			await self.bot.db.execute(""" UPDATE battlefield SET exp = $1 WHERE p_id = $2; """, n_exp, player_id)

		elif add == False:
			c_exp = await self.bot.db.fetchval(""" SELECT exp FROM battlefield WHERE p_id = $1 ;""", player_id)
			n_exp = int(c_exp) - amount
			await self.bot.db.execute(""" UPDATE battlefield SET exp = $1 WHERE p_id = $2; """, n_exp, player_id)
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
			cd_data = await self.bot.db.fetchval(""" SELECT cooldowns FROM battlefield WHERE p_id = $1; """, player_id)
			return json.loads(cd_data)
		cd_data = await self.bot.db.fetchval(""" SELECT cooldowns FROM battlefield WHERE p_id = $1; """, player_id)
		cd_dict = json.loads(cd_data)
		return cd_dict[f'n_{command_name}']
		

	async def update_cooldowns(self, player_id : int, command_name : str ):
		cd_data = await self.bot.db.fetchval(""" SELECT cooldowns FROM battlefield WHERE p_id = $1; """, player_id)
		cd_dict = json.loads(cd_data)
		cd_dict[f'n_{command_name}'] = int(time.time()) + cs.COOLDOWNS[f'{command_name}']
		cd_json = json.dumps(cd_dict)
		await self.bot.db.execute(""" UPDATE battlefield SET cooldowns = $1 WHERE p_id = $2; """, cd_json, player_id)


	async def update_balance(self,*,player_id, amount : int, add : bool = True):
		if add == True:
			bal = await self.bot.db.fetchval(""" SELECT balance FROM battlefield WHERE p_id = $1 ;""", player_id)
			bal = int(bal) + amount
			await self.bot.db.execute(""" UPDATE battlefield SET balance = $1 WHERE p_id = $2; """, bal, player_id)

		elif add == False:
			bal = await self.bot.db.fetchval(""" SELECT balance FROM battlefield WHERE p_id = $1 ;""", player_id)
			bal = int(bal) - amount
			await self.bot.db.execute(""" UPDATE battlefield SET balance = $1 WHERE p_id = $2; """, bal, player_id)
		return bal

	async def get_player_inventory(self, player_id : int):
		data = await self.bot.db.fetchrow(""" SELECT * FROM battlefield where p_id = $1;  """, player_id)
		return data

	async def is_opted_in(self, player_id : int):
		pass

	async def toggle_opt(self, player_id: int):
		pass

	