######################################
#VACATION FINDER
#a discord bot that
#provides coronavirus articles and
#statistics of a given country. This
#way users can make informed and
#safe decisions should they travel there.
######################################
#AUTHORS: Thomas Ochs and Catherine Chu
######################################

#IMPORT STATEMENTS
import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
import pandas as pd


#CLASSES
#determines if the bots should be activated
#based on user response
class ResponseStatus:
    def __init__(self):
        self.bot_on = False
        self.enter_country = False

#originally intended to be more specific to city
#and country. The variables remain for future revision.
class Location:
    def __init__(self):
        self.city = ""
        self.country = ""

res_status = ResponseStatus()

#the command prefix will activate the robot
client = commands.Bot(command_prefix = "find!")

#determines if the bot is online
@client.event
async def on_ready():
    print("Bot is ready.")


@client.event
async def on_message(message):
    channel = message.channel
    #checks if the current message sent is from a user or
    #from the robot. if it's from a robot then no action
    #is necessary
    if message.author == client.user:
        return

    #checks for user input (discord robot commands)
    if res_status.enter_country:
        if "exit" in message.content.lower():
            await channel.send("```Exited.```")
            res_status.enter_country = False
            return
        elif "find!safe" in message.content.lower():
            await channel.send("```The bot has already been activated. If you wish to exit, type 'exit'.```")
            return
        else:
            res_status.enter_country = False
            #ensures the user input is in a format that the rest of the code will recognize
            res_status.country = message.content.capitalize()
            await channel.send("```Analyzing the country...```")
            await channel.send("```Articles for Reference```")
            #opens the wikipedia article that we want to get information from
            response = requests.get("https://en.wikipedia.org/wiki/Travel_restrictions_related_to_the_COVID-19_pandemic")
            #ensures that the url was able to be opened
            if response is not None:
                #parses through the website notes every time there is an occurance of "<li>"
                html = BeautifulSoup(response.text, 'html.parser')
                #makes a list containing all occurances of "<li>" in the website
                paragraphs = html.select("li")
                for para in paragraphs:
                    if ' ' in para:
                        #prints out text that has the name of the user input country in it
                        if res_status.country in para.text:
                            await channel.send(para.text)
        #Stores the url to the table that we want to access
        wiki_url = 'https://en.wikipedia.org/wiki/COVID-19_pandemic_by_country_and_territory#covid19-container'
        #specific id of the table in that wikipedia article so the web scraping
        #knows which table to look at
        table_id = "thetable"
        #ensures the user input is in a format that the rest of the code will recognize
        country = message.content.capitalize()
        webpage = requests.get(wiki_url)
        #parses through the wikipedia article and stops when it hits the table that
        #we want to gather information from
        soup = BeautifulSoup(webpage.text, "html.parser")
        country_table = soup.find('table', attrs={'id': table_id})
        #using pandas, a dataframe object is created using the information in the table
        #on the wikipedia page
        df = pd.read_html(str(country_table))
        #modifies the output of the dataframe object making it easier to read for the user
        pd.set_option('display.max_columns',1000)
        pd.set_option('display.max_rows', 1000)
        pd.set_option('display.min_rows',1000)
        pd.set_option('display.max_colwidth',30)
        pd.set_option('display.width', 1000)
        pd.set_option('expand_frame_repr', True)
        temp = df
        #creates another dataframe object that we can modify
        string = temp[0]
        possibilities = list()
        #finds all instances of the user input country in the table
        #and makes a list of occurances
        find_country = string.isin([country])
        allResults = find_country.any()
        #collects the data from the column from each occurance of the country in the table
        columns = list(allResults[allResults == True].index)
        for col in columns:
            rows = list(result[col][result[col] == True].index)
            for row in rows:
                #stores row and column of the user input country from the table
                possibilities.append((row, col))
        #if it was able to find the country
        if(len(possibilities) > 0):
            index = possibilities[0][0]
            #stores the string of the row the country was found in so we can find the
            #number of deaths, cases, and recoveries separately
            org_list = string.loc[index].tolist()
        else:
            index = 0
            #the default output if the user input a country that was not found in the table
            await channel.send("```Country is not in CDC database, so here's the most infected country```")
            value = len(string.loc[index][1]) - 3
            country = string.loc[index][1][:value].title()
        #stores the number of cases and deaths as ints so we can find the survival rate percentage
        cases = int(float(string.loc[index][2]))
        deaths = int(float(string.loc[index][3]))
        survival_rate = (deaths / cases) * 100
        #prints out the number of cases, deaths, and recoveries for the country
        await channel.send(f"```COVID-19 Cases for {country}: {cases}\n```"\
        f"```Deaths for {country} from COVID-19: {deaths}\n```"\
        f"```Number of People who Recovered from COVID-19: {string.loc[index][4]}\n```"\
        f"```Death / Cases = {survival_rate}%```")

        #according to the World Health Organization, of the COVID-19 cases, 3.4% resulted in death. depending on
        #the death rate of inputted country, the robot will encourage or discourage the user of certain actions.
        if survival_rate >= 5.0:
            await channel.send(f"```Heavy risk of contracting COVID-19. Traveling here is discouraged.```")
        elif survival_rate >= 3.4 and survival_rate < 5.0:
            await channel.send(f"```Moderate risk of contracting COVID-19. Travel with caution.```")
        else:
            await channel.send(f"```Small risk of contracting COVID-19. However, wearing PPE is still encouraged.```")
    await client.process_commands(message)


#the command find!safe will trigger the entire process
@client.command()
async def safe(ctx):
    res_status.bot_on = True
    await ctx.send("```Enter a country. We will determine how safe it is to travel there. Type exit```"\
    "``` if you want to exit the program.```")
    res_status.enter_country = True

client.run("NzI4NjQ5OTMyNzQ3MzA5MDY2.Xv9eWQ.pQJ1wRRxVzTA1nLKr6gKx6c3DHw")
