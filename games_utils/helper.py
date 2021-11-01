import discord
import random
import asyncpg
import games_utils.constants as cs
import time
import json
import games_utils.items as itm
import math

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
			c_exp : int = await self.bot.db.fetchval(""" SELECT exp FROM battlefield WHERE p_id = $1 ;""", player_id)
			n_exp = c_exp + amount
			await self.bot.db.execute(""" UPDATE battlefield SET exp = $1 WHERE p_id = $2; """, n_exp, player_id)

		elif add == False:
			c_exp :int= await self.bot.db.fetchval(""" SELECT exp FROM battlefield WHERE p_id = $1 ;""", player_id)
			n_exp= c_exp - amount
			await self.bot.db.execute(""" UPDATE battlefield SET exp = $1 WHERE p_id = $2; """, n_exp, player_id)
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
			bal :int = await self.bot.db.fetchval(""" SELECT balance FROM battlefield WHERE p_id = $1 ;""", player_id)
			bal = bal + amount
			await self.bot.db.execute(""" UPDATE battlefield SET balance = $1 WHERE p_id = $2; """, bal, player_id)

		elif add == False:
			bal :int = await self.bot.db.fetchval(""" SELECT balance FROM battlefield WHERE p_id = $1 ;""", player_id)
			bal = bal - amount
			await self.bot.db.execute(""" UPDATE battlefield SET balance = $1 WHERE p_id = $2; """, bal, player_id)
		return bal

	def get_item_data(self, item :str):
		data = itm.ALL_ITEMS[item]
		return data

	

	def get_inventory_value(self, rec):
		"""Returns the inventory value for a player"""
		value : int = 0
		inv_columns = ['common', 'rare', 'legendary', 'epic', 'mythic']
		
		for column_n in inv_columns:
			column = rec[column_n] 
			i_dict : dict = json.loads(column)
			for item, count in i_dict.items():
				unit_price = itm.ALL_ITEMS[str(item)]['sell_price']
				value = value + unit_price*count
		return value

	def get_inventory_items_str(self, rec):
		fields = {}
		inv_columns = ['common', 'rare', 'legendary', 'epic', 'mythic']
		c = 1
		for column_n in inv_columns:
			column = rec[column_n]
			i_dict : dict = json.loads(column)
			text = ""
			for item, count in i_dict.items():
				try:
					if item and count != 0:
						text+=f"{itm.ALL_ITEMS[str(item)]['emoji']} {itm.ALL_ITEMS[str(item)]['name']} `x{count}`\n"
				except: #keyerror
					pass
			fields[str(c)] = text
			c+=1
		return fields

	def get_chest_counts(self, rec):
		"""Returns a dictionary of the filtered items in the following format: {'item_name' : count}"""
		filtered_items = {'common_chest' : 0, 'rare_chest' : 0,'legendary_chest' : 0, 'epic_chest' : 0,'mythic_chest' : 0}
		inv_columns = ['common', 'rare', 'legendary', 'epic', 'mythic']
		for column_n in inv_columns:
			column = rec[column_n]
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
		"""Returns the record for a player from the battlefield table"""
		data = await self.bot.db.fetchrow(""" SELECT * FROM battlefield where p_id = $1;  """, player_id)
		
		return data

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
		inv_table = await self.get_player_data(player_id)
		rarity_tier :str = itm.ALL_ITEMS[_item]['rarity']
		t_dict  = json.loads(inv_table[rarity_tier])
		try:
			t_dict[_item]+=amount
		except KeyError:
			t_dict[_item] = amount
		t_json = json.dumps(t_dict)
		query = f"UPDATE battlefield SET {rarity_tier} = $1 WHERE p_id = $2;"
		await self.bot.db.execute(query, t_json, player_id)

	async def bulk_update_inventory(self,*, player_id : int, items_dict : dict):
		
		
		try:
			for item, count in items_dict.items():
				inv_table = await self.get_player_data(player_id)
				rarity_tier : str =  itm.ALL_ITEMS[str(item)]['rarity']
				t_dict = json.loads(inv_table[rarity_tier])
				try:
					if t_dict[str(item)] or t_dict[str(item)] == 0:
						t_dict[str(item)]+= int(count)
				except KeyError:
					t_dict[str(item)] = int(count)
				t_json = json.dumps(t_dict)
				query = f"UPDATE battlefield SET {rarity_tier} = $1 WHERE p_id = $2;"
				con = await self.bot.db.execute(query, t_json, player_id)
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

	

	def get_bar_emojis(self, _for : str ,current : int, _max : int):
		"""Returns the bar emoji str for current hp/armour/exp status"""
		unit = 100/_max
		percentage = math.ceil(current*unit)
		if "hp" in _for.lower():
			emoji_dict = cs.HP_EMOJIS
		elif "armour" in _for.lower() or "shield" in _for.lower():
			emoji_dict = cs.SHIELD_EMOJIS
		elif "exp" in _for.lower():
			emoji_dict = cs.EXP_EMOJIS

		if percentage > 90:
			bar = f"{emoji_dict['left_full']}{emoji_dict['middle_full']*3}{emoji_dict['right_full']}"
			return bar
		elif percentage > 80:
			bar = f"{emoji_dict['left_full']}{emoji_dict['middle_full']*3}{emoji_dict['right_half']}"
			return bar
		elif percentage > 70:
			bar = f"{emoji_dict['left_full']}{emoji_dict['middle_full']*3}{emoji_dict['right_empty']}"
			return bar
		elif percentage > 60:
			bar = f"{emoji_dict['left_full']}{emoji_dict['middle_full']*2}{emoji_dict['middle_half']}{emoji_dict['right_empty']}"
			return bar
		elif percentage > 50:
			bar = f"{emoji_dict['left_full']}{emoji_dict['middle_full']}{emoji_dict['middle_full']}{emoji_dict['middle_empty']}{emoji_dict['right_empty']}"
			return bar
		elif percentage > 40:
			bar = f"{emoji_dict['left_full']}{emoji_dict['middle_full']}{emoji_dict['middle_half']}{emoji_dict['middle_empty']}{emoji_dict['right_empty']}"
			return bar
		elif percentage > 30:
			bar = f"{emoji_dict['left_full']}{emoji_dict['middle_full']}{emoji_dict['middle_empty']}{emoji_dict['middle_empty']}{emoji_dict['right_empty']}"
			return bar
		elif percentage > 20:
			bar = f"{emoji_dict['left_full']}{emoji_dict['middle_half']}{emoji_dict['middle_empty']}{emoji_dict['middle_empty']}{emoji_dict['right_empty']}"
			return bar
		elif percentage > 10:
			bar = f"{emoji_dict['left_full']}{emoji_dict['middle_empty']}{emoji_dict['middle_empty']}{emoji_dict['middle_empty']}{emoji_dict['right_empty']}"
			return bar
		elif percentage > 0:
			bar = f"{emoji_dict['left_half']}{emoji_dict['middle_empty']}{emoji_dict['middle_empty']}{emoji_dict['middle_empty']}{emoji_dict['right_empty']}"
			return bar
	
	def get_equipments(self, rec):
		"""Returns the str of equipments ( weapon , armour)"""
		eq_column = rec['equipments']
		eq_dict : dict = json.loads(eq_column)

		return eq_dict['weapon'], eq_dict['armour']

	def get_item_count(self, rec, *, item_name : str ):
		rarity_tier : str = itm.ALL_ITEMS[item_name]['rarity'] 
		c_dict : dict = json.loads(rec[rarity_tier])
		try:
			if c_dict[item_name]:
				count : int = c_dict[item_name]

		except KeyError:
			count = 0
		
		return count

