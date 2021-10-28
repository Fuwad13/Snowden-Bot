import discord
import random
import asyncpg
import games_utils.constants as cs
import time
import json
import games_utils.items as itm

class BattleFieldHelper:
	def __init__(self, bot):
		self.bot = bot

	async def check_if_exists(self, player_id : int):
		flag = False
		player = await self.bot.db.fetchval(""" SELECT p_id FROM battlefield WHERE p_id = $1 """, player_id)
		if player:
			flag = True
		else:
			flag = False
		return flag

	async def update_exp(self, *,player_id :int, amount : int, add :bool = True ):
		if add == True:
			c_exp : int = await self.bot.db.fetchval(""" SELECT exp FROM inventory WHERE p_id = $1 ;""", player_id)
			n_exp = c_exp + amount
			await self.bot.db.execute(""" UPDATE inventory SET exp = $1 WHERE p_id = $2; """, n_exp, player_id)

		elif add == False:
			c_exp :int= await self.bot.db.fetchval(""" SELECT exp FROM inventory WHERE p_id = $1 ;""", player_id)
			n_exp= c_exp - amount
			await self.bot.db.execute(""" UPDATE inventory SET exp = $1 WHERE p_id = $2; """, n_exp, player_id)
		return c_exp, n_exp

	def format_cooldown(self, seconds: int):
		d = int(seconds/86400)
		if d == 0:
			h = int(seconds/3600)
			m = int((seconds%3600)/60)
			s = seconds%60
			formatted = f"{h}:{m}:{s}"
		else:
			h = int((seconds%86400)/3600)
			m = int((seconds%3600)/60)
			s = seconds%60
			formatted = f"{d}d:{h}h:{m}m:{s}s"
		return formatted

	def get_level(self, exp : int) :
		level = int(0)
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
			bal :int = await self.bot.db.fetchval(""" SELECT balance FROM inventory WHERE p_id = $1 ;""", player_id)
			bal = bal + amount
			await self.bot.db.execute(""" UPDATE inventory SET balance = $1 WHERE p_id = $2; """, bal, player_id)

		elif add == False:
			bal :int = await self.bot.db.fetchval(""" SELECT balance FROM inventory WHERE p_id = $1 ;""", player_id)
			bal = bal - amount
			await self.bot.db.execute(""" UPDATE inventory SET balance = $1 WHERE p_id = $2; """, bal, player_id)
		return bal

	def get_item_data(self, item :str):
		data = itm.ALL_ITEMS[item]
		return data

	async def get_inventory_table(self, player_id :int):
		inv_table = await self.bot.db.fetchrow(""" SELECT * FROM inventory where p_id = $1; """, player_id)
		return inv_table

	def get_inventory_value(self, t2):
		value : int = 0
		for column in t2:
			if isinstance(column, int):
				continue
			i_dict : dict = json.loads(column)
			for item, count in i_dict.items():
				unit_price = itm.ALL_ITEMS[str(item)]['sell_price']
				value = value + unit_price*count
		return value

	def get_inventory_items_str(self, t2):
		fields = {}
		c = 1
		for column in t2:
			if isinstance(column, int):
				continue
			i_dict : dict = json.loads(column)
			text = ""
			for item, count in i_dict.items():
				try:
					if item and count != 0:
						text+=f"{itm.ALL_ITEMS[str(item)]['emoji']} {str(item).replace('_',' ')} x{count}\n"
				except: #keyerror
					pass
			fields[str(c)] = text
			c+=1
		return fields

	def get_chest_counts(self, t2):
		"""Returns a dictionary of the filtered items in the following format: {'item_name' : count}"""
		filtered_items = {'common_chest' : 0, 'rare_chest' : 0,'legendary_chest' : 0, 'epic_chest' : 0,'mythic_chest' : 0}
		for column in t2:
			if isinstance(column, int):
				continue
			i_dict : dict = json.loads(column)
			text = ""
			for item, count in i_dict.items():
				try:
					if item and 'chest' in str(item).lower():
						filtered_items[str(item)] = count
				except: #keyerror
					pass
			
			
		return filtered_items

	async def get_player_data(self, player_id : int):
		t1 = await self.bot.db.fetchrow(""" SELECT * FROM battlefield where p_id = $1;  """, player_id)
		t2 = await self.bot.db.fetchrow(""" SELECT * FROM inventory where p_id = $1;  """, player_id)
		return t1, t2

	async def get_opt_status(self, player_id: int):
		status : bool= await self.bot.db.fetchval(""" SELECT opt_status FROM battlefield where p_id = $1; """, player_id)
		return status
	async def set_opt_status(self, player_id :int, status : bool = True):
		if status:
			await self.bot.db.execute(""" UPDATE battlefield SET opt_status = true where p_id = $1;""", player_id)
			return True
		else:
			await self.bot.db.execute(""" UPDATE battlefield SET opt_status = false where p_id = $1;""", player_id)
			return False
	
	async def update_inventory(self,*,player_id : int, _item : str, amount : int):
		"""Update a player's inventory for one item"""
		inv_table = await self.get_inventory_table(player_id)
		rarity_tier :str = itm.ALL_ITEMS[_item]['rarity']
		t_dict  = json.loads(inv_table[rarity_tier])
		try:
			t_dict[_item]+=amount
		except KeyError:
			t_dict[_item] = amount
		t_json = json.dumps(t_dict)
		query = f"UPDATE inventory SET {rarity_tier} = $1 WHERE p_id = $2;"
		await self.bot.db.execute(query, t_json, player_id)

	async def bulk_update_inventory(self,*, player_id : int, items_dict : dict):
		inv_table = await self.get_inventory_table(player_id)
		try:
			for item, count in items_dict.items():
				rarity_tier : str =  itm.ALL_ITEMS[str(item)]['rarity']
				t_dict = json.loads(inv_table[rarity_tier])
				try:
					t_dict[str(item)]+= int(count)
				except KeyError:
					t_dict[str(item)] = int(count)
				t_json = json.dumps(t_dict)
				query = f"UPDATE inventory SET {rarity_tier} = $1 WHERE p_id = $2;"
				await self.bot.db.execute(query, t_json, player_id)
				return True
		except Exception as e:
			print(e)
			return False


	def can_opt_out(self, n_opt_out: int):
		if n_opt_out> int(time.time()):
			return False
		else:
			return True

	def level_up_rewards(self, n_lvl : int):
		pass

	def get_items(self, *, by : str, query : str):
		
		item_list = [str(k) for k, v in itm.ALL_ITEMS.items() if v[by] == query]
		
		return item_list

	def open_chest(self, chest : str):
		rarity_tier = chest.split('_')[0]
		item_list = self.get_items(by = 'rarity', query= rarity_tier)
		o_item = random.choice(item_list)
		return o_item




	