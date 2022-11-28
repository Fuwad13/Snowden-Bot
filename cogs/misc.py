import discord
import aiohttp
from discord.ext import commands
from discord.ext.commands import BucketType


class Miscellanous(commands.Cog):
	"""Miscellanous cog"""
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name = 'tounix', aliases = ['2uinx', 'tu'], slash_command = False, help= "Get unix timestamp from datetime. Datetime example = 2020/11/25 12:56:54" )
	@commands.cooldown(1, 5, BucketType.user)
	async def _tounix(self, ctx, *, datetime : str):
		datetime = datetime.replace('-', '/')
		datetime = datetime.replace('.', '/')
		base_url = "https://showcase.api.linx.twenty57.net/UnixTime/tounixtimestamp?datetime="
		url = base_url+datetime
		async with self.bot.session.get(url) as resp:
			try:
				js = await resp.json()
				
			except Exception as e:
				raise commands.BadArgument(f"Invalid datetime given. Please provide a valid datetime, thanks.")
			else:
				err = js.get('Error')
				if err:
					return await ctx.send(f"**Error**: {err}")

				ts = js['UnixTimeStamp']
				await ctx.send(f"Unix timestamp : `{ts}`\n\n`<t:{ts}:t>` -> <t:{ts}:t>\n`<t:{ts}:T>` -> <t:{ts}:T>\n`<t:{ts}>`    -> <t:{ts}>\n`<t:{ts}:F>` -> <t:{ts}:F>\n`<t:{ts}:d>` -> <t:{ts}:d>\n`<t:{ts}:D>` -> <t:{ts}:D>\n`<t:{ts}:R>` -> <t:{ts}:R>\n")

	@commands.command(name = 'todatetime', aliases = ['todate', 'td'], slash_command = False, help= "Get datetime from timestamp.")
	@commands.cooldown(1, 5, BucketType.user)
	async def _todate(self, ctx, timestamp : int):
		t_str = str(timestamp)
		base_url = "https://showcase.api.linx.twenty57.net/UnixTime/fromunixtimestamp?unixtimestamp="
		url = base_url+t_str
		async with self.bot.session.get(url) as resp:
			try:
				js = await resp.json()
				
			except Exception as e:
				raise commands.BadArgument(f"Invalid timestamp given. Please provide a valid timestamp, thanks.")
			else:
				err = js.get('Error')
				if err:
					return await ctx.send(f"**Error**: {err}")

				ts = js['Datetime']
				await ctx.send(f"**{ts}** UTC")

	@commands.command(aliases=["wea"], name = 'weather', brief = 'Get current weather information for a city or location')
	@commands.cooldown(1, 10, type=commands.BucketType.user)
	async def weather(self, ctx, *, city: str):
		city_name = city
		api_key = "ea5785a913a3474bc8ed46f7d862327f"
		base_url = "http://api.openweathermap.org/data/2.5/weather?"
		complete_url = base_url + "appid=" + api_key + "&q=" + city_name+"&units=metric"
		async with aiohttp.ClientSession() as session:
			async with session.get(complete_url) as res:
				x = await res.json()
		#response = requests.get(complete_url)
		
		thermo = u"\U0001f321"
		hum = u"\U0001f4a6"
		des = u"\U0001f505"
		pres = u"\U0001f4cd"
		wea = u"\U0001f326"
		feel = u"\U0001f912"
		sp = u"\U0001f300"
		channel = ctx.message.channel
		if x["cod"] != "404":
			async with channel.typing():
				y = x["main"]
				current_temperature_celcius = y["temp"]

				current_pressure = y["pressure"]
				current_humidity = y["humidity"]
				feels_like_celcius = y["feels_like"]
				z = x["weather"]
				icon_id = z[0]["icon"]
				icon_url = "http://openweathermap.org/img/wn/" + \
					str(icon_id)+"@2x.png"
				wind = x["wind"]
				speed = wind["speed"]
				weather_description = z[0]["description"]
				weather_description = z[0]["description"]
				c_name = x["name"]
				embed = discord.Embed(title=f"{wea}Weather in {c_name}",
									color=0x90FF90,
									timestamp=ctx.message.created_at,)
				embed.set_author(icon_url=icon_url, name="Weather Updates")
				embed.add_field(
					name=f"{des}Descripition", value=f"**{weather_description}**", inline=False)
				embed.add_field(
					name=f"{thermo}Temperature(C)", value=f"**{current_temperature_celcius}°C**", inline=True)
				embed.add_field(
					name=f"{feel}Feels like(C)", value=f"**{feels_like_celcius}°C**", inline=True)
				embed.add_field(
					name=f"{hum}Humidity(%)", value=f"**{current_humidity}%**", inline=True)
				embed.add_field(
					name=f"{sp}Wind speed(m/s)", value=f"**{speed} meter/second**", inline=True)
				embed.add_field(name=f"{pres}Atmospheric Pressure(hPa)",
								value=f"**{current_pressure}hPa**", inline=True)
				embed.set_thumbnail(url="https://i.ibb.co/CMrsxdX/weather.png")
				embed.set_footer(text=f"Requested by {ctx.author.name}")
				return await ctx.reply(embed=embed, mention_author=False)
		else:
			await ctx.send("City not found.", ephemeral = True)
	

	


async def setup(bot):
	await bot.add_cog(Miscellanous(bot))
