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

	def get_cd_dict_from_rec(self, rec):
		column = rec['cooldowns']
		cd_dict : dict = json.loads(column)
		return cd_dict


	async def update_cooldowns(self, player_id : int, command_name : str ):
		cd_data = await self.bot.db.fetchval(""" SELECT cooldowns FROM battlefield WHERE p_id = $1; """, player_id)
		cd_dict = json.loads(cd_data)
		cd_dict[f'n_{command_name}'] = int(time.time()) + cs.COOLDOWNS[f'{command_name}']
		cd_json = json.dumps(cd_dict)
		await self.bot.db.execute(""" UPDATE battlefield SET cooldowns = $1 WHERE p_id = $2; """, cd_json, player_id)


	async def update_attack_or_heal_cd(self,*, player_id : int, command_name : str , item_used : str):
		"""Update attack or heal cooldown for the corresponding item used."""
		cd_data = await self.bot.db.fetchval(""" SELECT cooldowns FROM battlefield WHERE p_id = $1; """, player_id)
		cd_dict = json.loads(cd_data)
		cooldown_time : int= itm.ALL_ITEMS[item_used]['cooldown']
		cd_dict[f'n_{command_name}'] = int(time.time()) + cooldown_time
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
		"""This is just for showing the inv items"""
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

	def get_inv_items_dict_by_rarity(self, rec):
		"""This method is for getting the items of a  player's inventory.
		Returns a dict of the rarity based items."""
		inv_dict = {}
		inv_columns = ['common', 'rare', 'legendary', 'epic', 'mythic']
		for column_n in inv_columns:
			column = rec[column_n]
			i_dict : dict = json.loads(column)
			inv_dict[column_n] = i_dict
		return inv_dict

	def get_inv_all_items_dict(self, rec):
		"""this method returns a dict of all items and counts. eg : {'ak_47' : 4, '7_62mm' : 3}"""
		all_items_dict = {}
		inv_columns = ['common', 'rare', 'legendary', 'epic', 'mythic']
		for column_n in inv_columns:
			column = rec[column_n]
			i_dict : dict = json.loads(column)
			all_items_dict.update(i_dict)
		return all_items_dict

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
	#idk it may be helpful for later 
	def get_key_from_dict(self, d : dict , value ):
		for key, val in d.items():
			if val == value:
				return key

	def open_chest(self, chest : str):
		rarity_tier = chest.split('_')[0]
		# rarity_index = cs.RARITY_INDEX[rarity_tier]
		# random_number = random.randint(1,500)
		# if random_number == 420:
		# 	...
		# elif random_number in range(1,69) or random_number in range(70,420) or random_number in range(421,501):
		# 	...
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
		count = 0
		try:
			if c_dict[item_name]:
				count : int = c_dict[item_name]

		except KeyError:
			count = 0
		
		return count

	async def update_equipments(self,*, player_id : int, eq_dict : dict):
		"""update a players equipments"""
		rec = await self.get_player_data(player_id)
		eq_p_dict = json.loads(rec['equipments'])
		#later

class AttackEngine:
	"""The base class for attack logics"""

	def __init__(self, *, bot,
				bfh : BattleFieldHelper , 
				attacker,
				a_rec, 
				target,
				t_rec):
		
		self.bot = bot
		self.bfh = bfh 
		self.attacker = attacker
		self.attacker_id = attacker.id
		self.a_rec = a_rec
		self.target = target
		self.target_id = target.id
		self.t_rec = t_rec

	def get_hp_plus_sp(self, rec):
		"""returns the sum of hp and sp"""
		hp_plus_sp : int = rec['hp'] + rec['sp']
		return hp_plus_sp

	async def loot(self,ctx):
		"""Algorithm for looting a killed player"""
		target_items_dict = self.bfh.get_inv_items_dict_by_rarity(self.t_rec)
		
	
	async def attack(self):
		"""Returns a string to be send corresponding to the damage done"""
		a_weapon , a_armour = self.bfh.get_equipments(self.a_rec)
		t_weapon, t_armour = self.bfh.get_equipments(self.t_rec)
		t_sp : int = self.t_rec['sp']
		attackable_t_hp = self.get_hp_plus_sp(self.t_rec)
		w_d_min, w_d_max = map(int,itm.ALL_ITEMS[str(a_weapon)]['damage'].split('-'))
		damage = random.randint(w_d_min, w_d_max)
		ammo_used = itm.ALL_ITEMS[str(a_weapon)]['ammo']
		invisibility = int(time.time()) + 600
		if damage >= attackable_t_hp:
			if t_armour:
				t_eq_dict = json.loads(self.t_rec['equipments'])
				t_eq_dict['armour'] = None
				t_eq_json = json.dumps(t_eq_dict)
				
				await self.bot.db.execute(""" UPDATE battlefield SET hp = 100, sp = 0, equipments = $1, invisibility = $2 WHERE p_id = $3;""",t_eq_json,invisibility, self.target_id)
				# implement looting stuffs later
				if ammo_used:
					ammo_dict = {ammo_used : -1 }
					await self.bfh.bulk_update_inventory(player_id=self.attacker_id, items_dict = ammo_dict)
				
				r_str = f"{self.attacker.mention} -> You Killed **{self.target}** with your {itm.ALL_ITEMS[str(a_weapon)]['emoji']}**{itm.ALL_ITEMS[str(a_weapon)]['name']}**(:boom:{damage} damage)\n\nPlease wait a few seconds before you can start looting the player's loot-crate."
				return r_str

			else:
				await self.bot.db.execute(""" UPDATE battlefield SET hp = 100, invisibility = $1 WHERE p_id = $2;""",invisibility, self.target_id)
				# implement looting stuffs later
				if ammo_used:
					ammo_dict = {ammo_used : -1 }
					await self.bfh.bulk_update_inventory(player_id=self.attacker_id, items_dict = ammo_dict)
				
				
				r_str = f"{self.attacker.mention} -> You Killed **{self.target}** with your {itm.ALL_ITEMS[str(a_weapon)]['emoji']}**{itm.ALL_ITEMS[str(a_weapon)]['name']}**(:boom:{damage} damage)\n\nLooting the killed player's inventory is being implemented, keep patience."
				return r_str
			# the case when target is killed
			
			
		elif damage < attackable_t_hp and not t_armour:
			# when target has no armour
			new_hp = attackable_t_hp - damage
			await self.bot.db.execute(""" UPDATE battlefield SET hp = $1, invisibility = $2  WHERE p_id = $3;""", new_hp,invisibility, self.target_id)
			if ammo_used:
				ammo_dict = {ammo_used : -1 }
				await self.bfh.bulk_update_inventory(player_id=self.attacker_id, items_dict = ammo_dict)
			
			
			r_str = f"{self.attacker.mention} -> Your {itm.ALL_ITEMS[str(a_weapon)]['emoji']}**{itm.ALL_ITEMS[str(a_weapon)]['name']}** dealt :boom: {damage} damage to **{self.target}**.\nThey now have {new_hp}/100 {self.bfh.get_bar_emojis('hp', new_hp, 100)} `health` remaining."
			return r_str
			
		elif damage < attackable_t_hp and t_armour and damage < t_sp:
			new_sp = t_sp - damage
			await self.bot.db.execute(""" UPDATE battlefield SET sp = $1, invisibility = $2 WHERE p_id = $3;""", new_sp,invisibility, self.target_id)
			if ammo_used:
				ammo_dict = {ammo_used : -1 }
				await self.bfh.bulk_update_inventory(player_id=self.attacker_id, items_dict = ammo_dict)
			
			
			r_str = f"{self.attacker.mention} -> Your {itm.ALL_ITEMS[str(a_weapon)]['emoji']}**{itm.ALL_ITEMS[str(a_weapon)]['name']}** dealt :boom: {damage} damage to **{self.target}'s** {itm.ALL_ITEMS[str(t_armour)]['emoji']}**{itm.ALL_ITEMS[str(t_armour)]['name']}**.\nThey now have {self.t_rec['hp']}/100 {self.bfh.get_bar_emojis('hp', self.t_rec['hp'], 100)} `health` and {new_sp}/{itm.ALL_ITEMS[str(t_armour)]['shield_points']} {self.bfh.get_bar_emojis('armour', new_sp, itm.ALL_ITEMS[str(t_armour)]['shield_points'])} `armour points` remaining."
			return r_str
			
		elif damage < attackable_t_hp and t_armour and damage >= t_sp:
			damage_l = damage - t_sp
			new_hp = self.t_rec['hp'] - damage_l
			t_eq_dict = json.loads(self.t_rec['equipments'])
			t_eq_dict['armour'] = None
			t_eq_json = json.dumps(t_eq_dict)
			await self.bot.db.execute(""" UPDATE battlefield SET hp = $1, sp = 0, equipments = $2, invisibility = $3 WHERE p_id = $4; """, new_hp, t_eq_json,invisibility, self.target_id)
			if ammo_used:
				ammo_dict = {ammo_used : -1 }
				await self.bfh.bulk_update_inventory(player_id=self.attacker_id, items_dict = ammo_dict)
			
			
			r_str = f"{self.attacker.mention} -> Your {itm.ALL_ITEMS[str(a_weapon)]['emoji']}**{itm.ALL_ITEMS[str(a_weapon)]['name']}** dealt :boom: {t_sp} damage to **{self.target}'s** {itm.ALL_ITEMS[str(t_armour)]['emoji']}**{itm.ALL_ITEMS[str(t_armour)]['name']}**. Their armour was broken and the rest :boom: {damage_l} damage was dealt to their `health`.\nThey now have {new_hp}/100 {self.bfh.get_bar_emojis('hp', new_hp, 100)} `health` remaining."
			return r_str

		else:
			#unknown case , still testing
			print("unknown error")
			print(damage)
			return "Unknown error occured"


class QuickFightEngine:

	def __init__(self, ctx,player1, player2):
		self.ctx = ctx
		self.player1 = player1
		self.player2 = player2


	async def start(self):
		...