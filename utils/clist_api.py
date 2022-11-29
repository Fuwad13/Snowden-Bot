import aiohttp
import datetime as dt
import json

from discord.ext import commands

C_BASE_URL = "https://clist.by/api/v1/contest/"
C_CREDENTIALS = "username=fuwad2&api_key=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"
# credential stuffs
# https://clist.by/api/v1/contest//?username=fuwad2&api_key=f4caba195a30836df60a2d40d4136fe08243bf3c

# errors
class ClistApiError(commands.CommandError):
    """Base class for all API related errors."""

    def __init__(self, message : str = None):
        super().__init__(message or 'Clist API error')


class ClientError(ClistApiError):
    """An error caused by a request to the API failing."""

    def __init__(self):
        super().__init__('Error connecting to Clist API')


class Round:
    def __init__(self, round):
        self.id = round['id']
        self.name = round['event']
        self.start_time = dt.datetime.strptime(
            round['start'], '%Y-%m-%dT%H:%M:%S')
        self.duration = dt.timedelta(seconds=round['duration'])
        self.url = round['href']
        self.website = round['resource']['name']
        self.website_id = round['resource']['id']

    def __str__(self):
        st = "ID = " + str(self.id) + ", "
        st += "Name = " + self.name + ", "
        st += "Start_time = " + str(self.start_time) + ", "
        st += "Duration = " + str(self.duration) + ", "
        st += "URL = " + self.url + ", "
        st += "Website = " + self.website + ", "
        st += "Website_id = " + str(self.website_id) + ", "
        st = "(" + st[:-2] + ")"
        return st

    def is_desired(
            self,
            website_allowed_patterns,
            website_disallowed_patterns):
        for disallowed_pattern in website_disallowed_patterns[self.website]:
            if disallowed_pattern in self.name.lower():
                return False

        for allowed_pattern in website_allowed_patterns[self.website]:
            if allowed_pattern in self.name.lower():
                return True
        return False

    def __repr__(self):
        return "Round - " + self.name




async def _query_api():

    """gets the data from the api and returns the json data of contests found"""
    contests_start_time = dt.datetime.utcnow() - dt.timedelta(days=2)
    contests_start_time_string = contests_start_time.strftime(
        "%Y-%m-%dT%H%%3A%M%%3A%S")
    url = C_BASE_URL + '?limit=200&start__gte=' + \
        contests_start_time_string + '&' + C_CREDENTIALS
    
    try:
        async with aiohttp.ClientSession() as cl_session:
            async with cl_session.get(url) as response:
                if response.status != 200:
                    raise ClistApiError
                data = await response.json() # type : dict
                return data['objects'] # type : list
    except Exception as e:
        raise ClientError from e



     

    

