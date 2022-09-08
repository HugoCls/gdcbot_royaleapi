from discord.ext import commands
import pandas as pd
import discord
import socket
from discord.utils import get
import royaleapi
import os

client=commands.Bot(intents = discord.Intents.all(),command_prefix = '-')

@client.event
async def on_ready():
    print('BOT Gdc is ready.')

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound): # or discord.ext.commands.errors.CommandNotFound as you wrote
        await ctx.reply("Commande inconnue.")

@client.command()
async def cr_id(ctx,user_cr_id,user_disc_id=None):
    user_cr_id=royaleapi.nice_format(user_cr_id)
    if len(user_cr_id)>10:
        await ctx.reply('Wrong CR-id, sorry mate.')
    else:
        if user_disc_id==None:
            user_disc_id=str(ctx.author.id)
        
        df = pd.read_csv('clan.csv')
        
        afk_players,clan_dict=royaleapi.get_players()
        
        ids=clan_dict.keys()
        
        user_name='unspecified'
        if user_cr_id in ids:
            user_name=clan_dict[user_cr_id]['name']

        df2 = pd.DataFrame(list(zip([user_cr_id],[user_name], [user_disc_id])), columns =['CR id','Name','Discord'])
        
        df=df.append(df2,ignore_index=True)
        df.to_csv('clan.csv', encoding='utf-8')
        
        await ctx.reply(user_name+':<@'+str(user_disc_id)+'>, saved.')
    await ctx.message.delete()

@client.command()
async def clear(ctx):
    await ctx.message.delete()
    await ctx.channel.purge(limit=100)

@client.command()
async def Hello(ctx):
    user = get(client.get_all_members(), id=ctx.author.id)
    username='*'+user.name+'* '
    await ctx.reply('Hello there.',mention_author=False)
   # await ctx.message.delete()

@client.command()
async def gdc(ctx):
    L,clan_dict,medals,day=royaleapi.player_attacks()
    p=sum(len(L[i]) for i in range(4))
    
    embed = discord.Embed(title="War | "+str(day), colour=discord.Colour(0x3e038c),_provider='test')
    
    embed.set_thumbnail(url=ctx.author.avatar_url)
    L_stats=["<:sign:913172154269442048> Ultimate FR",
    "<:medals:1017445552859906148> "+str(medals),
    "<:decksremaining:1017445543108165713> "+str(p),
    "<:slots:1017445562779435169> "+str(len(L[3]))]
    
    #adding slots 
    
    embed.add_field(name=f"**Remaining Attacks**", value='\n'.join(L_stats), inline=False)
    
    
    for i in range(len(L)):
        if len(L[i])>=1:
            attacks="Attack"
            if i>=2:
                attacks+="s"
            embed.add_field(name=f"**"+str(i+1)+" "+attacks+"**", value='•'+'\n•'.join(L[i]), inline=False)
    
    await ctx.reply(embed=embed,mention_author=False)
    await ctx.message.delete()

@client.command()
async def ping(ctx):
    sentence1='| '
    sentence2=''
    afk_players,clan_dict,medals,day=royaleapi.get_players()
    for (player,remaining_attacks) in afk_players:
        if player in clan_dict.keys():
            sentence1+=clan_dict[player]['name']+' | '
            if clan_dict[player]['discord']!='':
                sentence2+=' <@'+str(clan_dict[player]["discord"])+'> '
    sentence=sentence1+sentence2+'\nIl vous reste des combats!'
    await ctx.reply(sentence)
    await ctx.message.delete()
    
@client.command()
async def check_disc(ctx):
    afk_players,clan_dict,medals,deck=royaleapi.get_players()
    cr_ids=clan_dict.keys()
    df=pd.read_csv('clan.csv')
    sentence=''

    count=0
    for cr_id in cr_ids:
        if cr_id not in list(df['CR id']):
            sentence+=clan_dict[cr_id]['name']+', '
            count+=1

    if sentence!='':
        if count>1:
            sentence+='ne sont pas dans la base de données.'
        else:
            sentence+="n'est pas dans la base de données."
    else:
        sentence='Tous les joueurs ont leur discord renseigné.'

    await ctx.reply(sentence)
    await ctx.message.delete()
    
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP
    
@client.command(pass_context=True)
async def getguild(ctx):
    hn = socket.gethostname()
    ip_address = socket.gethostbyname(hn)
    print(f"IP Address: {ip_address}")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    f=str(s.getsockname()[0])
    s.close()
    hn=str(socket.getfqdn())
    hn2=socket.gethostbyname(hn)
    
    ip4=get_ip()
    await ctx.reply('ip1: '+ip_address+' ip2: '+f+' ip3: '+hn2+' ip4: '+ip4)
    await ctx.message.delete()

def read_token():
    with open('token.txt','r') as f:
        lines=f.readlines()
        return(lines[0].strip())
"""
TOKEN=read_token()

client.run(TOKEN)
"""
client.run(os.environ['DISCORD_TOKEN'])
