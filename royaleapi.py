from requests_html import HTMLSession
from bs4 import BeautifulSoup
import pandas as pd

def get_session():
    session=HTMLSession()
    r=session.get('https://royaleapi.com/clan/UURJ9CG/war/race')
    return(r)

def get_players(r=get_session()):
    text=r.text
    soup=BeautifulSoup(text,'html.parser')
    
    players=soup.find_all('td',class_="player_name")
    
    clan_dict={}
    afk_players=[]
    for player in players:
        name=player.find_all('a',class_='player_name force_single_line_hidden')[0].get_text().strip('\n')
        
        attacks=player.find_all('div',class_='value_bg decks_used_today')[0].get_text().strip('\n')
        
        cr_id='#'+player.find_all('a',href=True)[0]['href'].strip('/player/').strip('/battles')
           
        #print(name,':',cr_id,':',attacks)
        clan_dict[cr_id]={"name":name,"discord":""}
        
        if int(attacks)<4:
            afk_players.append(cr_id)
    clan_dict=add_discords(clan_dict)
    return(afk_players,clan_dict)

def add_discords(clan_dict):
    df=pd.read_csv('clan.csv')
    ids=clan_dict.keys()
    for i in range(len(df)):
        line=df.iloc[i]
        if line['CR id'] in ids:
            clan_dict[line['CR id']]['discord']=line['Discord']
    return(clan_dict)

def nice_format(cr_id):
    L=[]
    for i in range(len(cr_id)):
        L.append(cr_id[i])
    while True:
        j=0
        for i in range(len(L)):
            if L[i]=="#":
                del(L[i])
                j=1
                break
        if j==0:
            break
    final_id=["#"]
    for i in range(len(L)):
        final_id.append(L[i])
    new_id=''.join(e for e in final_id)
    return(new_id)

def write_csv():
    afk_players,clan_dict=get_players()
    L_cr_ids=list(clan_dict.keys())
    L_names=[]
    for i in range(len(L_cr_ids)):
        cr_id=L_cr_ids[i]
        name=clan_dict[cr_id]['name']
        L_names.append(name)
    
    L_discord_ids=['' for i in range(len(L_names))]

    df = pd.DataFrame(list(zip(L_cr_ids,L_names, L_discord_ids)), columns =['CR id','Name','Discord'])
    
    df.to_csv('empty_clan.csv', encoding='utf-8')
    return(df)