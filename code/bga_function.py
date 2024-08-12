from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import statistics
import re
import pandas as pd
import holoviews as hv



# define function
def get_player_info(driver, waiting_time, player_page_link, selected_game_name):
    # go to a player page
    driver.get(player_page_link)

    # wait 
    time.sleep(waiting_time)

    # handle case of player not exist because of banned or deleted
    try:
        driver.find_element(By.ID, 'player_name')
    except:
        return ['', '', '']   
        
    # name
    player_name = driver.find_element(By.ID, 'player_name').text
    # print(player_name)
    
    # languages
    player_language=[]
    for i in driver.find_elements(By.CLASS_NAME, 'langnormal'):
        player_language.append(i.text)
    
    # country
    # player_country = driver.find_element(By.CLASS_NAME, 'bga-flag').get_attribute('data-country')
    player_country = driver.find_element(By.ID, 'pagesection_publicinfos').find_elements(By.CLASS_NAME, 'row-value')[2].text.strip()
    # print(player_country )

    # reputation
    reputation = driver.find_element(By.CLASS_NAME, 'progressbar_label').find_element(By.CLASS_NAME, 'value').text
    
    #elo
    played_games = driver.find_elements(By.CLASS_NAME, 'palmares_game')

    for i in played_games:
        game_name = i.find_element(By.CLASS_NAME, 'gamename').text
        if game_name == selected_game_name:
            # print("game:",game_name)
            elo = i.find_element(By.CLASS_NAME, 'gamerank_value').text
            # print(elo)
    return [player_name, player_country, elo, player_language, reputation]



#define funtion
def get_table_info(driver, waiting_time, link):
    # go to a table page
    driver.get(link)
    time.sleep(waiting_time)
 
    # check if the table is cancelled  or abandoned
    # abandoned game example: 
    # https://boardgamearena.com/table?table=474084060
    # # cancelled game example: 
    # https://boardgamearena.com/table?table=477008316
    
    # get player name
    # players = []
    # players = driver.find_element(By.ID, 'player_stats_header').text.split(" ")
    
    ## return null if a game in progress
    if driver.find_element(By.ID, 'status_detailled').text  == 'Game in progress (Turn-based)':
        return ['in progress', '', [], '', '']
    
    
    players_name = []
    players_name_entries = driver.find_element(By.ID, 'game_result').find_elements(By.CLASS_NAME,'score-entry')
    for i in players_name_entries:
        # print(i.find_element(By.CLASS_NAME, 'playername').text)
        players_name.append(i.find_element(By.CLASS_NAME, 'playername').text)
        
    quit_player=''
    slow_player=''
    if driver.find_element(By.CLASS_NAME, 'game_abandonned').text != '':
        status = 'abandoned'
        # print(f"{link} abandoned(beyond max duration) because of {players_name[-1]}")
        slow_player = players_name[-1]
    elif driver.find_element(By.CLASS_NAME, 'game_cancelled').text != '':
        status = 'cancelled'
        # print(f"{link} cancelled(player left) because of {players_name[-1]}")
        quit_player = players_name[-1]
    else: 
        status = ''
          
    # get table time, excluding cancelled tables, including abandoned table
    if status == "cancelled":
        table_time= ""
    else:
        table_time = driver.find_element(By.ID, 'estimated_duration').text
    
    # get player number count
    number_players = len(players_name)    
    
    # get time spent by each player premiun needed
    each_time = []
    for i in range(number_players):
        # print(driver.find_element(By.CLASS_NAME, 'statstable').find_elements(By.TAG_NAME, 'td')[i+number_players].text)
        each_time.append(driver.find_element(By.CLASS_NAME, 'statstable').find_elements(By.TAG_NAME, 'td')[i+number_players].text)
    
    player_time = []
    for x, y in zip(players_name, each_time):
        player_time.append([x,y])
    return [status, table_time, player_time, quit_player, slow_player]

    
def transparent_background(image_file):
    from PIL import Image
    img = Image.open(image_file)
    rgba = img.convert('RGBA')
    datas = rgba.getdata()

    newData = []

    for item in datas:

       if item[0] == 255 and item[1] == 255 and item[2] == 255:
           newData.append((255, 255, 255, 0))
       else:
          newData.append(item)
    rgba.putdata(newData)
    
    # new_image_file = 't_' + image_file  
    # new_image_file = '../assets/t_' + re.findall("assets/(.*)",image_file)[0]
    new_image_file = re.findall("(.*assets)/(.*)",elo_file)[0][0] + \
    '/t_' + \
    re.findall("(.*assets)/(.*)",elo_file)[0][1]
    
    rgba.save(new_image_file, 'PNG')
    print('output image:', new_image_file)
    return new_image_file


def time_converstion(table_times):
    converted_table_times = []
    # print(table_times[:4])
    for i in table_times:
        # print(i)
        if re.findall('days', i):
            day = float(re.findall('(.*) days',i)[0])
            # print(i,">",day)
            converted_table_times.append(day)
        elif re.findall('mn',i):
            minute = int(re.findall('(.*) mn',i)[0])
            # print(round(minute/1440,1),"minutes > days")
            day = round(minute/1440,1)
            converted_table_times.append(day)
            # print(i,">", day)
        elif re.findall('h',i):
            hour = int(re.findall('(.*)h(.*)',i)[0][0])
            minute = int(re.findall('(.*)h(.*)',i)[0][1])
            # print(round((hour*60 + minute)/1440,1), "hour&minute > day")
            day = round((hour*60 + minute)/1440,1)
            converted_table_times.append(day)
            # print(i,">", day)
        elif re.findall(':',i):  #56:40
            hour = int(re.findall("(.*):(.*)" ,i)[0][0])
            minute = int(re.findall("(.*):(.*)" ,i)[0][1])
            day = round((hour*60 + minute)/1440,1)
            converted_table_times.append(day)
            # print(i,">", day)
    return converted_table_times



def bga_in_bgg():
    # scraping all bga game
    for count in range(1,38):
    # for count in range(1,3):
        link = 'https://boardgamegeek.com/boardgamefamily/70360/digital-implementations-board-game-arena/linkeditems/boardgamefamily?sort=yearpublished&pageid=' + str(count)
        # print("===")
        # print(link)
        # print("===")
        driver.get(link)
        time.sleep(10)
        for entry in driver.find_elements(By.CLASS_NAME, 'summary-item'):
            game_name = entry.find_element(By.CLASS_NAME, 'summary-item-title').text
            game_rating = entry.find_element(By.CLASS_NAME,'rating-angular').text[-3:]

            try:
                game_rank = entry.find_element(By.CLASS_NAME,'fs-sm').find_element(By.CLASS_NAME,'ng-binding').text
            except:
                game_rank = 'n/a'

            game_num_rating = entry.find_elements(By.CLASS_NAME,'outline-item')[0].find_element(By.CLASS_NAME,'ng-binding').text
            game_weight = entry.find_elements(By.CLASS_NAME,'outline-item')[1].find_element(By.CLASS_NAME,'ng-binding').text
            game_link = 'https://boardgamegeek.com' + entry.find_element(By.CLASS_NAME, 'summary-item-title').find_element(By.TAG_NAME,'a').get_attribute('ng-href')

            print(f'{game_name}, {game_rank}, {game_rating}, {game_num_rating}, {game_weight}, {game_link}')
    return None

    

def PlayerRankingChart(GameName):
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt

    # Setup data
    data = pd.read_csv('../assets/csv/result.csv')     
    game_data = data[data['game'] == GameName].sort_values(by='point', ascending=True)
    acc_game_data = game_data.groupby('player')['point'].sum().sort_values(ascending=False)
    selected_data = pd.DataFrame({'player':acc_game_data.index, 'point':acc_game_data.values})    
    selected_data["player.Upper"] = selected_data["player"].str.upper()
    selected_data = selected_data.sort_values(['point', 'player.Upper'], ascending=[True,False])
    
    
    
    # Setup plot size.
    # fig, ax = plt.subplots()
    vertical_size = len(selected_data) / 3.5
    fig, ax = plt.subplots(figsize=(5,vertical_size))
    

    # Create grid
    # Zorder tells it which layer to put it on. We are setting this to 1 and our data to 2 so the grid is behind the data.
    ax.grid(which="major", axis='x', color='#758D99', alpha=0.6, zorder=1)

    # Remove splines. Can be done one at a time or can slice with a list.
    ax.spines[['top','right','bottom']].set_visible(False)

    # Make left spine slightly thicker
    ax.spines['left'].set_linewidth(1.1)
    ax.margins(y=0)


    # Plot data
    ax.barh(selected_data['player'], selected_data['point'], color='#006BA2', zorder=2)

    # Reformat x-axis tick labels
    ax.xaxis.set_tick_params(labeltop=True,      # Put x-axis labels on top
                             labelbottom=False,  # Set no x-axis labels on bottom
                             bottom=False,       # Set no ticks on bottom
                             labelsize=11,       # Set tick label size
                             pad=-1)             # Lower tick labels a bit

    # Reformat y-axis tick labels
    ax.set_yticklabels(selected_data['player'],      # Set labels again
                       ha = 'left')              # Set horizontal alignment to left
    ax.yaxis.set_tick_params(pad=100,            # Pad tick labels so they don't go over y-axis
                             labelsize=9,       # Set label size
                             bottom=False)       # Set no ticks on bottom/left

    # Add in title and subtitle
    # FigName = GameName.replace(" ","") + 'Ranking.png'
    FigName = '../assets/' + GameName.replace(" ","") + 'Ranking.png'

    plt.savefig(FigName, transparent=True, bbox_inches='tight')
    
    top_country = game_data.groupby('country')['point'].sum().sort_values(ascending=False)
    print(GameName)
    # print(GameName," Region ranking: ", end='')

    print(f'🥇{top_country.index[0]}({top_country.iloc[0]}) 🥈{top_country.index[1]}({top_country.iloc[1]}) 🥉{top_country.index[2]}({top_country.iloc[2]})')
    print(top_country.head())

    return None