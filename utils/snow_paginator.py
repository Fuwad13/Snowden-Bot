import discord 
from discord import ui 

class BasePaginator(ui.View):
	def __init__(self, ctx,items,*,timeout:int=180, disable_after=True, per_page: int=6):
		super().__init__(timeout= timeout)
		self.ctx = ctx
		self.disable_after= disable_after
		self.items= items
		self.per_page = per_page
		pages, left_over = divmod(len(items), per_page)
		if left_over:
			pages+=1
		self.max_pages = pages
		self.min_pages= 1

		def format_page(self, items, per_page):
			embed = discord.Embed(title=f"{Page {}" )
		

