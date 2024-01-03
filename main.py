import numpy as np
import pandas as pd
from aenum import Enum
from aenum import extend_enum
import discord
from discord.ext import commands
from discord.ext import tasks
from discord import app_commands
import os

counts = 10


charts = pd.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vRRPejhjYGUYtLWTfBRZLmzBgvEGAYHm4DdGb8thCfBXJJlL1RzjHSKd7pF_aX_7AqO0cYo6KzJ4knU/pub?output=csv')
print('charts')
scores = pd.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vSSJwU9zaPLWEweKlhJzYuHy-B5v3U4JP8UIzkMBe0SpZ07hzSFZC-zINPgJYH_yGUOkO7u1YpW47nv/pub?output=csv')
scores.fillna(0, inplace = True)
scores[scores.columns[1:]].astype(int)
print('scores')
equivs = pd.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vSSJwU9zaPLWEweKlhJzYuHy-B5v3U4JP8UIzkMBe0SpZ07hzSFZC-zINPgJYH_yGUOkO7u1YpW47nv/pub?output=csv')
print('equivs')
charts.reindex(['Charts', 'Tier', 'Max Score'])

#scores = pd.DataFrame({'Player': ['bap', 'bonk', 'ugly ass bitch']})
#equivs = pd.DataFrame({'Player': ['bap', 'bonk', 'ugly ass bitch']})
#charts = pd.DataFrame(index = ['Tier', 'Max Score'])


#charts = pd.read_csv('charts.csv')
#equivs = pd.read_csv('equivs.csv')
#scores = pd.read_csv('scores.csv')


charts.index = ['Tier', 'Max Score']
print(charts)

print(charts.columns.tolist())


def addChart(name, tier, maxscore): #MAKE THIS CHECK FOR NON-ENGLISH CHARACTERS AT SOME POINT
  print(charts.columns.values.tolist().count(name))
  if tier <= 0 or tier > 20:
      return("tier error")
  elif charts.columns.values.tolist().count(name) > 0:
      return('duplicate error')
  else:
    scores[name] = [0 for i in scores.index]
    equivs[name] = [0 for i in scores.index]
    charts[name] = [tier, maxscore]

def addPlayer(player): #also make this check for non-english characters at some point
  if len(scores[scores["Player"] == player].index) > 0:
    return('duplicate error')
  else:
    list = [player]
    list[1:] = ([0 for gonk in range(1,len(scores.columns))])
    scores.loc[len(scores.index)] = list
    equivs.loc[len(equivs.index)] = list

def equiv(score, maxscore, tier):
  C = tier
  a = 23
  b = C / ( np.exp(a) - 1)
  x = score / maxscore
  f = (C + b) * np.exp(-a * (1-x)) - b
  return(round((5 * f), 3))
  
def setScore(player, chart, score):
  if score > charts[chart]['Max Score'] or score < 0:
    return('score error')
  elif int(score) < scores[chart][scores.index[scores['Player'] == player].tolist()[0]] and score != 0:
    return('small score')
  else:
    scores.at[scores.index[scores['Player'] == player].tolist()[0], chart] = score

def removeScore(player, chart):
  if scores[chart][scores.index[scores['Player'] == player].tolist()[0]] == 0:
    return('no score error')
  else:
    setScore(player, chart, 0)

def editChart(oldchart, newchart, tier, maxscore):
  charts.rename(columns = {oldchart: newchart}, inplace = True)
  scores.rename(columns = {oldchart: newchart}, inplace = True)
  equivs.rename(columns = {oldchart: newchart}, inplace = True)
  charts[newchart] = [tier, maxscore]

def removeChart(chart):
  charts.drop(columns = [chart], inplace = True)
  scores.drop(columns = [chart], inplace = True)
  equivs.drop(columns = [chart], inplace = True)

def editPlayer(playerold, playernew):
    equivs.at[equivs.index[scores['Player'] == playerold].tolist()[0], 'Player'] = playernew
    scores.at[scores.index[scores['Player'] == playerold].tolist()[0], 'Player'] = playernew

def removePlayer(player):
    scores.drop([equivs.index[scores['Player'] == player].tolist()[0]], inplace = True)
    equivs.drop([equivs.index[equivs['Player'] == player].tolist()[0]], inplace = True)
    scores.reset_index(inplace = True)
    equivs.reset_index(inplace = True)
    scores.drop(columns = ['index'], inplace = True)
    equivs.drop(columns = ['index'], inplace = True)

def playerStats(player):
  mean = 100 / counts
  count = counts
  weights = [round(2*mean - ( (2 * mean) / (count + 1) ) * i, 2) for i in range(1, count + 1)]
  zeros = [0 for i in range(0, len(charts.columns) - count)]
  weights = weights + zeros
  print(weights)
  print(len(weights))
  print(len(equivs.columns))
  stats = pd.DataFrame({
    'Charts': equivs.columns,
    'Equiv': equivs.iloc[equivs.index[equivs['Player'] == player].tolist()[0]] 
    #'Score': scores.iloc[scores.index[scores['Player'] == player].tolist()[0]]
    }).drop(index = 'Player').sort_values(by = 'Equiv', ascending = False)
  stats['Weights'] = weights
  #stats['Score'] = stats['Score'].apply(int)
  stats['Equiv'] = stats['Equiv'].apply(lambda x: round(x, 3))
  return(stats)

def chartStats(chart):
  return(pd.DataFrame({
    'Player': scores['Player'],
    'Score': scores[chart],
    'Equiv': equivs[chart]
  }))

def printdf(df):
  string = '```'
  print(df)
  lengths = [max(len(str(i)) for i in (df[col].tolist())) for col in df]
  for i in range(0,len(lengths)):
    lengths[i] = max(lengths[i], len(df.columns[i]))
  for i in range(0,len(lengths)):
    string = string + df.columns[i] + ' ' * (lengths[i] - len(df.columns[i]) + 2)
  string = string + "\n"
  for index, row in df.iterrows():
    i = 0
    for cell in row.tolist():
      string = string + str(cell) + ' ' * (lengths[i] - len(str(cell)) + 2)
      i += 1
    string = string + "\n"
  return(string + '```')

def weightedAverage(list, count):
  mean = 100 / count
  weights = [
    2*mean - ( (2 * mean) / (count + 1) ) * i for i in range(1, count + 1)
  ]
  return(sum([list[i] * (weights[i] / 100) for i in range (0, count)]))

def updateEquiv():
  for chart in charts:
    tier = charts[chart].values[0]
    maxscore = charts[chart].values[1]
    data = scores[chart].values
    for i in range(0, len(data)):
      equivs.at[i, chart] = round(equiv(scores[chart][i], maxscore, tier), 3)



def leaderboard():
  leaderboards = pd.DataFrame({
    'Position': [i for i in range(1,len(scores.index) + 1)],
    'Player': [0 for i in range(0, len(scores.index))], 'Rank': [0 for i in range(0,len(scores.index))]
  }, index = [i for i in range(0,len(scores.index))])
  for index, row in equivs.iterrows():
    leaderboards.iloc[index] = [1, row['Player'], weightedAverage(sorted(row.tolist()[1:], reverse = True), counts)]
  leaderboards = leaderboards.sort_values(by = 'Rank', ascending = False)
  leaderboards['Position'] = [i for i in range(1,len(scores.index) + 1)]
  return(leaderboards)

def save():
  scores.to_csv('scores.csv', index = False)
  charts.to_csv('charts.csv', index = False)
  equivs.to_csv('equivs.csv', index = False)


playerStats('jif')

updateEquiv()
  
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


def columntostring(list):
  string = ''
  for i in list.tolist():
    string += str(i) + '\n'
  return(string)

def createEmbed(df, name, rows, position, sort, type = None):
  global embed
  if name == 'Leaderboard':
    embed = discord.Embed(title = name, description = f"Positions {1 + rows * (position - 1)} to {rows * (position - 1) + rows}", color = discord.Color.blue())
  if type == 'playerstats':
    embed = discord.Embed(title = name, description = f'placeholder\nScores {1 + rows * (position - 1)} to {rows * (position - 1) + rows}', color = discord.Color.blue())
  if type == 'chartstats':
    embed = discord.Embed(title = name, description = f'placeholder\nScores {1 + rows * (position - 1)} to {rows * (position - 1) + rows}', color = discord.Color.blue())
  for column in df:
    embed.add_field(name = column, value = columntostring(df.sort_values(by = sort, ascending = False)[column].iloc[ (rows * (position - 1)) : (rows * (position - 1)) + rows]), inline = True)


@tree.command(name = "charts", description = "Display raw chart data (mostly for debugging)", guild=discord.Object(id=516810661347459111)) 
async def chartdisp(interaction):
    await interaction.response.send_message(printdf(charts))

@tree.command(name = "scores", description = "Display raw score data (mostly for debugging)", guild=discord.Object(id=516810661347459111)) 
async def scoredisp(interaction):
  print(scores)
  await interaction.response.send_message(printdf(scores))

@tree.command(name = "setscore", description = "Submit a score", guild=discord.Object(id=516810661347459111)) 
async def botaddscore(interaction, player: str, chart: str, score: int):
  if setScore(player, chart, score) == 'score error':
    await interaction.response.send_message(':warning: Error: Invalid score')
  if setScore(player, chart, score) == 'small score':
    await interaction.response.send_message('Warning: Submitted score is lower than current score')
  else:
    addScore(player, chart, score)
    await interaction.response.send_message(f'Score successfully added: \n ` Player: {player} | Chart: {chart} | Score: {score}`')

@tree.command(name = "addchart", description = "Add a chart", guild=discord.Object(id=516810661347459111)) 
async def botaddchart(interaction, chartname: str, tier: int, maxscore: int):
  if addChart(chartname, tier, maxscore) == 'duplicate error':
    await interaction.response.send_message('Error: Chart already added')
  elif addChart(chartname, tier, maxscore) == 'tier error':
    await interaction.response.send_message('Error: Invalid tier')
  else:
    await interaction.response.send_message(f'Chart successfully added: \n ` Chart name: {chartname} | Tier: {tier} | Max score: {maxscore}`')

@tree.command(name = "addplayer", description = "Add a player", guild=discord.Object(id=516810661347459111)) 
async def botaddplayer(interaction, player: str):
  if addPlayer(player) == 'duplicate error':
      await interaction.response.send_message(f':warning: Error: Player `{player}` already exists')
  else:
    addPlayer(player)
    await interaction.response.send_message(f'Player `{player}` successfully added')

class playerstatsbutton(discord.ui.View):
  @discord.ui.button(label="", row=0, style=discord.ButtonStyle.primary, emoji="◀️")
  async def playerbutton_callback(self, interaction, button):
    global currentplayer
    global playerposition
    if playerposition != 1:
      playerposition -= 1
    createEmbed(playerStats(currentplayer), f'area', counts, playerposition, 'Equiv', 'playerstats')
    await playermessage.edit_original_response(embed=embed)
    await interaction.response.defer()

  @discord.ui.button(label="", row=0, style=discord.ButtonStyle.primary, emoji="▶️")
  async def playerbutton_callback2(self, interaction, button):
    global player
    global playerposition
    playerposition += 1
    createEmbed(playerStats(currentplayer), f'area', counts, playerposition, 'Equiv', 'playerstats')
    await playermessage.edit_original_response(embed=embed)
    await interaction.response.defer()


@tree.command(name = "playerstats", description = "Check the stats of a player", guild=discord.Object(id=516810661347459111)) 
async def botplayerstats(interaction, player: str):
  global currentplayer
  currentplayer = player
  global playermessage
  global playerposition
  playermessage = interaction
  playerposition = 1
  #updateEquiv()
  #try:
  createEmbed(playerStats(player), f'Stats for {player}', counts, playerposition, 'Equiv', 'playerstats')
  global embed
  await interaction.response.send_message(embed = embed, view = playerstatsbutton())
  #except Exception:
  #await client.get_channel(517121809867603968).send('Oh no! The code crashed for absolutely no reason! Please run the command again.')


class chartstatsbutton(discord.ui.View):
  @discord.ui.button(label="", row=0, style=discord.ButtonStyle.primary, emoji="◀️")
  async def chartbutton_callback(self, interaction, button):
    global currentchart
    global chartposition
    if chartposition != 1:
      chartposition -= 1
      createEmbed(chartStats(currentchart), f'Info for {currentchart}', 20, chartposition, 'Score', 'chartstats')
    await chartmessage.edit_original_response(embed=embed)
    await interaction.response.defer()

  @discord.ui.button(label="", row=0, style=discord.ButtonStyle.primary, emoji="▶️")
  async def chartbutton_callback2(self, interaction, button):
    global currentchart
    global chartposition
    chartposition += 1
    createEmbed(chartStats(currentchart), f'Info for {currentchart}', 20, chartposition, 'Score', 'chartstats')
    await chartmessage.edit_original_response(embed=embed)
    await interaction.response.defer()


@tree.command(name = "chartstats", description = "Check the stats of a chart", guild=discord.Object(id=516810661347459111)) 
async def botchartstats(interaction, chart: str):
  #updateEquiv()
  global currentchart
  currentchart = chart
  global chartmessage
  global chartposition
  chartmessage = interaction
  chartposition = 1
  createEmbed(chartStats(chart), f'Info for {chart}', 20, chartposition, 'Score', 'chartstats')
  await interaction.response.send_message(embed = embed, view = chartstatsbutton())

class leaderboardbutton(discord.ui.View):
  @discord.ui.button(label="", row=0, style=discord.ButtonStyle.primary, emoji="◀️")
  async def button_callback(self, interaction, button):
    global leaderboardposition
    if leaderboardposition != 1:
      leaderboardposition -= 1
    createEmbed(leaderboard(), 'Leaderboard', 20, leaderboardposition, 'Rank')
    await leaderboardmessage.edit_original_response(embed=embed)
    await interaction.response.defer()

  @discord.ui.button(label="", row=0, style=discord.ButtonStyle.primary, emoji="▶️")
  async def button_callback2(self, interaction, button):
    global leaderboardposition
    leaderboardposition += 1
    createEmbed(leaderboard(), 'Leaderboard', 20, leaderboardposition, 'Rank')
    await leaderboardmessage.edit_original_response(embed=embed)
    await interaction.response.defer()

@tree.command(name = "leaderboard", description = "Search for charts", guild=discord.Object(id=516810661347459111)) 
async def leaderboarddisp(interaction):
  #updateEquiv()
  global leaderboardmessage
  global leaderboardposition
  leaderboardmessage = interaction
  leaderboardposition = 1
  createEmbed(leaderboard(), 'Leaderboard', 20, leaderboardposition, 'Rank')
  await leaderboardmessage.response.send_message(embed=embed, view = leaderboardbutton())

@tree.command(name = "search", description = "Check the leaderboard", guild=discord.Object(id=516810661347459111)) 
async def leaderboarddisp(interaction, search: str):
  string = ''
  for column in charts:
    if search.lower() in column:
      string += column
      string += '\n'
  if string == '':
    await interaction.response.send_message('fail')
  await interaction.response.send_message(string)

@tree.command(name = "save", description = "(Temporary) Saves the current datasets", guild=discord.Object(id=516810661347459111)) 
async def botsave(interaction):
  updateEquiv()
  save()
  await interaction.response.send_message('saved')

@tree.command(name = "removescore", description = "Removes a score from the dataset", guild=discord.Object(id=516810661347459111)) 
async def botremovescore(interaction, player: str, chart: str):
  if removeScore(player, chart) == 'no score error':
    await interaction.response.send_message("Error: score doesn't exist")
  else:
    removeScore(player, chart)
    await interaction.response.send_message('Score has been removed')

@tree.command(name = "editchart", description = "Edits a charts data", guild=discord.Object(id=516810661347459111)) 
async def boteditchart(interaction, chart: str, name: str, tier: int, maxscore: int):
  editChart(chart, name, tier, maxscore)
  await interaction.response.send_message(f'Chart has been edited. New data for {chart}: `Name: {name} | Tier: {tier} | Max score: {maxscore}`')

#THE /SAY COMMAND
#@tree.command(name = "say", description = "Send a message", guild=discord.Object(id=516810661347459111)) 
#async def say(interaction, channel: int, message: str):
  #await client.get_channel(channel).send(message)
  #await client.get_channel(channel).send(message)

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=516810661347459111))
    print("we out here letting it linger")
    await client.get_channel(517121809867603968).send('we out here letting it linger')

@client.event
async def on_message(message):
  if message.content == 'a':
    await message.channel.send('geometry dash')
  if message.content == 'geometry dash':
    await message.channel.send('a** **')
  if message.content[:3] == 'say':
    list = message.content[3:].split(', ')
    await client.get_channel(int(list[0])).send(list[1])




#@tasks.loop(minutes = 20)
#async def yeahwoochannelmesasage():
    #await client.get_channel('1131910034008313866').send("Bot here to tell you that it's time to move the probe down and left one pixel. The current front pixel (in white) should be the new rear pixel (in dark blue).")
    #await client.get_channel(1131910034008313866).send("Bot here to tell you that it's time to move the probe down and left one pixel. The current front pixel (in white) should be the new rear pixel (in dark blue).")

#joinmessage = True
#@client.event
#async def on_guild_join(guild = 1131713223796719636):
    #if joinmessage != False:
        #await client.get_channel(1131713224362958880).send("Welcome!!! \n For anyone just joining here is the current focus and plan. \n Please check ⁠updates  to see the time window from our bot. We are moving the probe across the screen every twenty minutes. If you are new please do not spend pixels to move the probe, we have people assigned to this task already. \n During downtime we are moving around the embers around the fire, they ONLY GO AS HIGH as the BOTTOM of giants deep, any higher looks kinda meh. Please don't add too many stars. \n Also every 40 minutes we will be changing the orbit of the orbital probe cannon, the new template will be posted at that time")

#optimize playerstats, chartstats, and leaderboard PLEASE (remove updateEquiv)
#make everything not case sensitive
#remaining commands: removescore, editchart, removechart, editplayer, removeplayer (all of these will need exception handling)
#make addscore setscore instead, removes the need for editscore
#commands that need exception handling: all of them
#also still need to make headers for playerstats (include leaderboard position) and chartstats, and leaderboards (after customization is implemented)
#also still need to make playerstats, chartstats, and leaderboards customizeable
#add weights to playerstats
#for setscore, add the whole "are you sure you wanna change this score its lower than the last one" thing
#also make account linking a thing, probably the last step
#transpose the display of charts so more charts can be viewed
#because of the "testing purposes" incident youre gonna have to readd exception handling to addchart later
#migrate to vs because repl is gonk
#maybe make setscore say when you submit a top (count) score
#make equiv update when a score is set so that updateEquiv() isn't required

#jif suggestion: add ranks (do this like divisions and just give them names like "gm")

516810661347459111
token = os.environ['DISCORD_BOT_SECRET']
client.run(token)