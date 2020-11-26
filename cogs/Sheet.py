# every lounge is different so this file will probably
# have to be completely rewritten for each server.
# my implementation is here as an example; gspread is only
# needed if you get MMR from a spreadsheet.

# The important part is that the function returns False
# if a player's MMR can't be found,
# and returns the player's MMR otherwise

import discord
from discord.ext import commands
import aiohttp

rt_website_url = "https://mariokartboards.com/lounge/json/player.php?type=rt&name="
ct_website_url = "https://mariokartboards.com/lounge/json/player.php?type=ct&name="


class Sheet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    async def mmr(self, member: discord.Member, is_rt=True):
        name = member.display_name.lower().replace(" ", "")
        full_url = rt_website_url if is_rt else ct_website_url
        full_url += name
        
        #Takes a list of players, returns that list of player's matched to their player IDs
        data = None
        try:
            data = await self.getJSONData(full_url)
        except: #numerous failure types can occur, but they all mean the same thing: we didn't get out data
            return False
        
        if self.data_is_corrupt(data):
            return False
        
        return data[0]["current_mmr"]
    
    async def getJSONData(self, full_url):
        async with aiohttp.ClientSession() as session:
            async with session.get(full_url) as r:
                if r.status == 200:
                    js = await r.json()
                    return js
    
    def data_is_corrupt(self, jsonData):
        if jsonData == None:
            print("Bad request to Lounge API... Data was None.")
            return True
        if "error" in jsonData:
            print("Bad request to Lounge API... Error in data.")
            return True
        if not isinstance(jsonData, list):
            print("Bad request to Lounge API... Data was not a list.")
            return True
        
        if len(jsonData) != 1:
            return True
        
        playerData = jsonData[0]
        if not isinstance(playerData, dict):
            return True
        
        if "current_mmr" not in playerData or not isinstance(playerData["current_mmr"], int):
            return True
        
        return playerData["current_mmr"] < 0
        

def setup(bot):
    bot.add_cog(Sheet(bot))
