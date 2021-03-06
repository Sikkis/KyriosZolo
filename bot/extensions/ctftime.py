import discord
import io
import logging
import re
import requests
import feedparser

from colorthief import ColorThief
from discord.ext import commands
from urllib.request import urlopen
from exceptions import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Ctf(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def ctftime(self, ctx):
        self.guild = ctx.guild
        self.gid = ctx.guild.id

        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid command passed.  Use !help.')

    @ctftime.command()
    async def upcoming(self, ctx):
        default_image = 'https://pbs.twimg.com/profile_images/2189766987/ctftime-logo-avatar_400x400.png'
        upcoming_url = 'https://ctftime.org/api/v1/events/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0',
        }

        def rgb2hex(r, g, b):
            tohex = '#{:02x}{:02x}{:02x}'.format(r, g, b)
            return tohex

        limit = '3'
        response = requests.get(upcoming_url, headers=headers, params=limit)
        data = response.json()

        for num in range(0, int(limit)):
            ctf_title = data[num]['title']
            (ctf_start, ctf_end) = (data[num]['start'].replace('T', ' ').split('+', 1)[0] + ' UTC', data[num]['finish'].replace('T', ' ').split('+', 1)[0] + ' UTC')
            (ctf_start, ctf_end) = (re.sub(':00 ', ' ', ctf_start), re.sub(':00 ', ' ', ctf_end))
            dur_dict = data[num]['duration']
            (ctf_hours, ctf_days) = (str(dur_dict['hours']), str(dur_dict['days']))
            ctf_link = data[num]['url']
            ctf_image = data[num]['logo']
            ctf_format = data[num]['format']
            ctf_place = data[num]['onsite']

            if ctf_place == False:
                ctf_place = 'Online'
            else:
                ctf_place = 'Onsite'

            fd = urlopen(default_image)
            f = io.BytesIO(fd.read())
            color_thief = ColorThief(f)
            rgb_color = color_thief.get_color(quality=49)
            hexed = str(rgb2hex(rgb_color[0], rgb_color[1], rgb_color[2])).replace('#', '')
            f_color = int(hexed, 16)
            embed = discord.Embed(title=ctf_title, description=ctf_link, color=f_color)

            if ctf_image != '':
                embed.set_thumbnail(url=ctf_image)
            else:
                embed.set_thumbnail(url=default_image)

            embed.add_field(name='Duration', value=((ctf_days + ' days, ') + ctf_hours) + ' hours', inline=True)
            embed.add_field(name='Format', value=(ctf_place + ' ') + ctf_format, inline=True)
            embed.add_field(name='─' * 23, value=(ctf_start + ' -> ') + ctf_end, inline=True)
            await ctx.channel.send(embed=embed)

    @ctftime.command()
    async def writeups(self, ctx, *params):
        writeups_url = 'https://ctftime.org/writeups/rss/'
        try:
            news_feed = feedparser.parse(writeups_url)
            limit = 3
            if len(params) == 1:
                limit = int(params[0])
            if limit > len(news_feed.entries):
                limit = len(news_feed.entries)
            for i in range(limit):
                entry = news_feed.entries[i]
                writeup_title = entry['title']
                writeup_url = entry['original_url']
                embed = discord.Embed(title=writeup_title,url=writeup_url, color=231643)
                await ctx.channel.send(embed=embed)
        except ValueError:
            await ctx.channel.send('Έλεος μάθε να μετράς τστστσ. For this command you have to provide an int number')
        except Exception as e:
            logger.error(e)
            await ctx.channel.send('Κατι εν εδούλεψε... Θέλεις ξανα δοκιμασε, θέλεις μεν δοκιμάσεις! Στα @@ μου.')


def setup(bot):
    bot.add_cog(Ctf(bot))