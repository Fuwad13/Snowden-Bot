import aiohttp
import discord
import aiohttp
from discord.ext import commands


api_key = "ea5785a913a3474bc8ed46f7d862327f"
base_url = "http://api.openweathermap.org/data/2.5/weather?"


    

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["w"], name = 'weather', brief = 'Get current weather information for a city or location', help  = "Get current weather status of a city or location!")
    @commands.cooldown(1, 10, type=commands.BucketType.user)
    async def weather(self, ctx, *, city: str):
        city_name = city
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
                await ctx.message.reply(embed=embed, mention_author=False)
        else:
            await channel.send("City not found.")

    @weather.error
    async def weather_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            text = f"{ctx.author.mention} You're on cooldown!!\n"
            r = "Please retry this command after `{:.2f} seconds`!".format(
            	error.retry_after)
            await ctx.channel.send(text+r)
        else:
          await ctx.send(error)

    # @commands.command(aliases=["locateweather", "locatew", "lw"])
    # @commands.cooldown(1, 10, type=commands.BucketType.user)
    # async def lweather(self, ctx, lat, lon):
    #     latitude = str(lat)
    #     longitude = str(lon)
    #     complete_url = base_url + "lat="+latitude + \
    #         "&lon="+longitude+"&appid="+api_key+"&units=metric"
    #     rs = requests.get(complete_url)
    #     rjson = rs.json()
    #     thermo = u"\U0001f321"
    #     hum = u"\U0001f4a6"
    #     des = u"\U0001f505"
    #     pres = u"\U0001f4cd"
    #     wea = u"\U0001f326"
    #     feel = u"\U0001f912"
    #     sp = u"\U0001f300"
    #     channel = ctx.message.channel
    #     if rjson["cod"] != "404":
    #         async with channel.typing():
    #             y = rjson["main"]
    #             current_temperature_celcius = y["temp"]

    #             current_pressure = y["pressure"]
    #             current_humidity = y["humidity"]
    #             feels_like_celcius = y["feels_like"]
    #             z = rjson["weather"]
    #             icon_id = z[0]["icon"]
    #             icon_url = "http://openweathermap.org/img/wn/" + \
    #                 str(icon_id)+"@2x.png"
    #             wind = rjson["wind"]
    #             speed = wind["speed"]
    #             weather_description = z[0]["description"]
    #             weather_description = z[0]["description"]
    #             c_name = rjson["name"]

    #             embed = discord.Embed(title=f"{wea}Weather in {c_name}",
    #                                   color=0x90FF90,
    #                                   timestamp=ctx.message.created_at,)
    #             embed.set_author(icon_url=icon_url, name="Weather Updates")
    #             embed.add_field(
    #                 name=f"{des}Descripition", value=f"**{weather_description}**", inline=False)
    #             embed.add_field(
    #                 name=f"{thermo}Temperature(C)", value=f"**{current_temperature_celcius}°C**", inline=True)
    #             embed.add_field(
    #                 name=f"{feel}Feels like(C)", value=f"**{feels_like_celcius}°C**", inline=True)
    #             embed.add_field(
    #                 name=f"{hum}Humidity(%)", value=f"**{current_humidity}%**", inline=True)
    #             embed.add_field(
    #                 name=f"{sp}Wind speed(m/s)", value=f"**{speed} meter/second**", inline=True)
    #             embed.add_field(name=f"{pres}Atmospheric Pressure(hPa)",
    #                             value=f"**{current_pressure}hPa**", inline=True)
    #             embed.set_thumbnail(url="https://i.ibb.co/CMrsxdX/weather.png")
    #             embed.set_footer(text=f"Requested by {ctx.author.name}")
    #             await ctx.message.reply(embed=embed, mention_author=False)
    #     else:
    #         await channel.send("Location not found.")

    # @lweather.error
    # async def lweather_error(self, ctx, error):
    #     if isinstance(error, commands.CommandOnCooldown):
    #         text = f"{ctx.author.mention} You're on cooldown!!\n"
    #         r = "Please retry this command after `{:.2f} seconds`!".format(
    #         	error.retry_after)
    #         await ctx.channel.send(text+r)
	
	

def setup(bot):
	bot.add_cog(Weather(bot))
