import discord
from discord import ui
from games_utils.items import ALL_ITEMS
class ConfirmOrCancel(ui.View):


	def __init__(self, ctx ,*,timeout = 60):
		super().__init__(timeout=timeout)
		
		self.value = None
		self.ctx = ctx

	async def on_timeout(self):
		pass

	async def interaction_check(self, intr):
		if not self.ctx.author == intr.user:
			await intr.response.send_message("Sorry, you can't interact to these buttons", ephemeral = True)
		return self.ctx.author == intr.user

	@ui.button(label = 'Confirm', style = discord.ButtonStyle.green)
	async def confirm_button(self, button, interaction):
		self.value = True
		self.stop()

	@ui.button(label = 'Cancel', style = discord.ButtonStyle.red)
	async def cancel_button(self, button, interaction):
		self.value = False
		self.stop()


class HeadsOrTails(ui.View):
	def __init__(self, ctx):
		self.ctx = ctx
		self.value = None
		super().__init__(timeout = 15)

	async def interaction_check(self, intr):
		if not intr.user == self.ctx.author:
			await intr.response.send_message(f"Sorry, only **{self.ctx.author.name}** can choose from these buttons!", ephemeral = True)

		return intr.user == self.ctx.author

	@ui.button(emoji = '\U0001f1ed', label = 'Heads', style = discord.ButtonStyle.green)
	async def heads_button(self, button, intr):
		self.clear_items()
		self.value = True
		self.stop()

	@ui.button(emoji = '\U0001f1f9',label = 'Tails', style = discord.ButtonStyle.blurple)
	async def tails_buttton(self, button, intr):
		self.clear_items()
		self.value = False
		self.stop()

class InventoryEmbeds(ui.View):
	"""View buttons for inventory embeds"""
	def __init__(self, ctx, embed1, embed2):
		self.ctx = ctx
		self.embed1 = embed1
		self.embed2 = embed2
		super().__init__(timeout=120)

	async def interaction_check(self, intr):
		if not intr.user == self.ctx.author:
			await intr.response.send_message(f"Sorry, only **{self.ctx.author.name}** can use these buttons!", ephemeral = True)

		return intr.user == self.ctx.author

	@ui.button(emoji = '<:previous:904438065420959784>', style = discord.ButtonStyle.gray)
	async def _previous(self, button, intr):
		self._next.disabled = False
		button.disabled = True
		await intr.message.edit(embed= self.embed1, view = self)

	@ui.button(emoji = '<:next:904437983988563988>', style = discord.ButtonStyle.gray)
	async def _next(self, button, intr):
		self._previous.disabled = False
		button.disabled = True
		await intr.message.edit(embed= self.embed2, view = self)

	@ui.button(emoji = '<:stop:904438127530225724>', style = discord.ButtonStyle.gray)
	async def _stop(self, button, intr):
		self.stop()
		await self.message.edit(view = self)
		await intr.message.delete(silent = True)


	async def on_timeout(self):
		
		for item in self.children:
			self.clear_items()
			
		await self.message.edit(view = self)
			

class BuyItem(ui.View):
	def __init__(self, ctx):
		self.ctx = ctx
		self.confirmation = False
		super().__init__(timeout=20)

	async def interaction_check(self, intr):
		if not intr.user == self.ctx.author:
			await intr.response.send_message(f"Sorry, only **{self.ctx.author.name}** can use this button!", ephemeral = True)

		return intr.user == self.ctx.author
	#add emoji later
	@ui.button(label = 'Buy', style= discord.ButtonStyle.green)
	async def _buy(self, button, intr):
		
		self.confirmation = True
		self.stop()

	@ui.button(label='Cancel', style=discord.ButtonStyle.red)
	async def _cancel(self, button, intr):
		
		self.confirmation = False
		self.stop()

	async def on_timeout(self):
		
		
		self.confirmation = False
		
class SellItem(ui.View):
	def __init__(self, ctx):
		self.ctx = ctx
		self.confirmation = False
		super().__init__(timeout=20)

	async def interaction_check(self, intr):
		if not intr.user == self.ctx.author:
			await intr.response.send_message(f"Sorry, only **{self.ctx.author.name}** can use this button!", ephemeral = True)

		return intr.user == self.ctx.author
	#add emoji later
	@ui.button(label = 'Sell', style= discord.ButtonStyle.green)
	async def _sell(self, button, intr):
		
		self.confirmation = True
		self.stop()

	@ui.button(label='Cancel', style=discord.ButtonStyle.red)
	async def _cancel(self, button, intr):
		
		self.confirmation = False
		self.stop()

	async def on_timeout(self):
		
		
		self.confirmation = False
	
class EquipItem(ui.View):
	def __init__(self, ctx):
		self.ctx = ctx
		self.confirmation = False
		super().__init__(timeout=20)

	async def interaction_check(self, intr):
		if not intr.user == self.ctx.author:
			await intr.response.send_message(f"Sorry, only **{self.ctx.author.name}** can use this button!", ephemeral = True)

		return intr.user == self.ctx.author
	#add emoji later
	@ui.button(label = 'Equip', style= discord.ButtonStyle.green)
	async def _eq(self, button, intr):
		
		self.confirmation = True
		self.stop()

	@ui.button(label='Cancel', style=discord.ButtonStyle.red)
	async def _cancel(self, button, intr):
		
		self.confirmation = False
		self.stop()

	async def on_timeout(self):
		
		
		self.confirmation = False		

class AttackView(ui.View):
	def __init__(self, ctx):
		self.ctx = ctx
		self.confirmation = False
		super().__init__(timeout=20)

	async def interaction_check(self, intr):
		if not intr.user == self.ctx.author:
			await intr.response.send_message(f"Sorry, only **{self.ctx.author.name}** can use this button!", ephemeral = True)

		return intr.user == self.ctx.author
	#add emoji later
	@ui.button(label = 'Attack', style= discord.ButtonStyle.green)
	async def _att(self, button, intr):
		
		self.confirmation = True
		self.stop()

	@ui.button(label='Cancel', style=discord.ButtonStyle.red)
	async def _cancel(self, button, intr):
		
		self.confirmation = False
		self.stop()

	async def on_timeout(self):
		
		
		self.confirmation = False


class HealView(ui.View):
	def __init__(self, ctx):
		self.ctx = ctx
		self.confirmation = False
		super().__init__(timeout=20)

	async def interaction_check(self, intr):
		if not intr.user == self.ctx.author:
			await intr.response.send_message(f"Sorry, only **{self.ctx.author.name}** can use this button!", ephemeral = True)

		return intr.user == self.ctx.author
	#add emoji later
	@ui.button(label = 'Heal', style= discord.ButtonStyle.green)
	async def _heal_button(self, button, intr):
		
		self.confirmation = True
		self.stop()

	@ui.button(label='Cancel', style=discord.ButtonStyle.red)
	async def _cancel(self, button, intr):
		
		self.confirmation = False
		self.stop()

	async def on_timeout(self):
		
		
		self.confirmation = False

class Guide(ui.View):

	def __init__(self, ctx):
		self.ctx = ctx
		super().__init__(timeout=300)

	@ui.button(label="Guide", emoji= "\U00002139", style = discord.ButtonStyle.gray)
	async def guide_button(self, button, interaction):
		ctx = self.ctx
		
		text = f"""
\U00002139 Battlefield Guide

- If you haven't started playing yet, run the `{ctx.clean_prefix}start` command to get started.

- Use the following commands to get time based check-in rewards:
    `{ctx.clean_prefix}hourly`, `{ctx.clean_prefix}daily`, `{ctx.clean_prefix}weekly`, `{ctx.clean_prefix}monthly`,
	`{ctx.clean_prefix}work`, `{ctx.clean_prefix}loot` ....

- Use `{ctx.clean_prefix}inventory` to see you inventory, `{ctx.clean_prefix}equip <weapon/armour name>` to equip weapons/armours. 

- Use `{ctx.clean_prefix}opt` to toggle your *opt in* status. *Opted in* means you are able to attack other players and vice versa. *Opted out* means you can't attack others and vice versa.

- Use `{ctx.clean_prefix}attack <player>` to attack a player (you must be opted in and have a equipped weapon with necessary ammunition.)

- Use `{ctx.clean_prefix}heal <healing_item_name>` to heal and increase your healthpoints.

- Use `{ctx.clean_prefix}buy [amount] <item_name>` or `{ctx.clean_prefix}sell [amount] <item_name>` to buy/sell items. `{ctx.clean_prefix}trade <player>` to trade items with a player.

- Use `{ctx.clean_prefix}help Battlefield` for more fun and useful commands.

**If you still get confused feel free to join our support server and ask in the support channel.**

		"""
		await interaction.response.send_message(text, ephemeral=True)


class TradeConfirmView(ui.View):
	def __init__(self, player2):
		self.player2 = player2
		self.confirmation = False
		super().__init__(timeout=60)

	async def interaction_check(self, intr):
		if not intr.user == self.player2:
			await intr.response.send_message(f"Sorry, only **{self.player2}** can use this button!", ephemeral = True)

		return intr.user == self.player2
	#add emoji later
	@ui.button(label = 'Trade', style= discord.ButtonStyle.blurple)
	async def _tradebutton(self, button, intr):
		
		self.confirmation = True
		self.stop()

	@ui.button(label='Cancel', style=discord.ButtonStyle.red)
	async def _cancel(self, button, intr):
		
		self.confirmation = False
		self.stop()

	async def on_timeout(self):
		
		self.confirmation = False
	
class QuickFightConfirmation(ui.View):

	def __init__(self, ctx, player2):
		super().__init__(timeout=90)
		self.ctx = ctx
		self.player2 = player2
		self.accepted = False

	async def interaction_check(self, interaction: discord.Interaction):
		if not interaction.user == self.player2:
			await interaction.response.send_message(f"Sorry, only {self.player2.mention} can `accept` or `reject`!", ephemeral= True)
		return interaction.user == self.player2

	@ui.button(label = 'Accept', style= discord.ButtonStyle.blurple)
	async def accept_button(self, button, intr):
		self.accepted = True
		self.stop()

	@ui.button(label = 'Reject', style=discord.ButtonStyle.red)
	async def reject_button(self, button, intr):
		self.accepted = False
		self.stop()

	async def on_timeout(self):
		self.accepted = False
	
class QuickFightView(ui.View):

	def __init__(self, ctx, player1, player2):
		super().__init__(timeout=90)
		self.ctx = ctx
		self.player1 = player1
		self.player2 = player2
		self.turn = player1

	async def interaction_check(self, interaction: Interaction) -> bool:
		if not interaction.user == self.turn:
			...