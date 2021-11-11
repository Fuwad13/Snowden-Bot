import json
import discord 
from discord.ext import commands 

class AutoModeration(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener('on_message')
    async def chat_filtering(self, message):
        if (message.guild is None) or (message.author.bot ):
            return

    @commands.group(name = 'blacklist', aliases = ['bl'], slash_command = False, help = "The group command for blacklisting words for chat automoderation.", invoke_without_command = True)
    @commands.guild_only()
    @commands.has_permissions(manage_server = True)
    async def _blacklist(self, ctx):
        await ctx.send("Use the subcommands to add/remove blacklisted words")

    @_blacklist.command(name= 'add', aliases = ['append'], help = "add new word(s) to the blacklisted words, seperate words by spaces", slash_command = False)
    @commands.guild_only()
    @commands.has_permissions(manage_server = True)
    async def _bl_add(self, ctx, *, words : str):
        if len(words) < 3:
            return await ctx.send("Words must contain at least 3 characters")
        words_l = words.split(' ')
        n_l = [x for x in words_l if len(x) >= 3]
        bl_words = await self.bot.db.fetchval("select bl_words from guilds where guild_id = $1;", ctx.guild.id)
        p_l : list = json.loads(bl_words)
        p_l.extend(n_l)
        j_l = json.dumps(p_l)
        await self.bot.db.execute("Update guilds set bl_words = $1 where guild_id = $2;", j_l, ctx.guild.id)
        r_str = ", ".join(n_l)
        await ctx.send(f"Added these words to the blacklisted words :\n{r_str}")
        


def setup(bot):
    bot.add_cog(AutoModeration(bot))
