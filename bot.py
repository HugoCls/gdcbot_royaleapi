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

        afk_players,clan_dict,medals,day=royaleapi.get_players()
        
        ids=clan_dict.keys()

        user_name='unspecified'
        if user_cr_id in ids:
            user_name=clan_dict[user_cr_id]['name']

        if user_cr_id in list(df['CR id']):
            user_index=df.loc[df['CR id']==user_cr_id].index[0]
            line=df.iloc[user_index]
            df=df.replace(line['Discord'],user_disc_id)
            df.to_csv('clan.csv', encoding='utf-8')

            await ctx.reply(user_name+':'+user_cr_id+':<@'+str(user_disc_id)+'>, replaced.')
        else:
            df2 = pd.DataFrame(list(zip([user_cr_id],[user_name], [user_disc_id])), columns =['CR id','Name','Discord'])

            df=df.append(df2,ignore_index=True)
            df.to_csv('clan.csv', encoding='utf-8')

            await ctx.reply(user_name+':'+user_cr_id+':<@'+str(user_disc_id)+'>, saved.')
    await ctx.message.delete()

@client.command()
async def clear(ctx):
    await ctx.message.delete()
    await ctx.channel.purge(limit=100)
    
@client.command()
async def get_members(ctx):
    members=ctx.message.guild.members
    ids=[]
    for member in members:
        ids.append(member.id)
    print(ids)

@client.command()
async def Hello(ctx):
    user = get(client.get_all_members(), id=ctx.author.id)
    username='*'+user.name+'* '

    await ctx.reply('Hello there.')
    await ctx.message.delete()


@client.command()
async def ping(ctx):
    L,clan_dict,medals,day=royaleapi.player_attacks()

    p=sum(len(L[i]) for i in range(4))
    embed = discord.Embed(title="War | "+str(day), colour=discord.Colour(0x3e038c))
    

    #embed.set_thumbnail(url=ctx.author.avatar_url)
    #embed.set_author(name='',icon_url=ctx.author.avatar_url)
    L_stats=["<:sign:913172154269442048> Ultimate FR",
    "<:medals:1017445552859906148> "+str(medals),
    "<:decksremaining:1017445543108165713> "+str(p),
    "<:slots:1017445562779435169> "+str(len(L[3]))] 
    embed.add_field(name=f"**Remaining Attacks**", value='\n'.join(L_stats), inline=False)
    
    for i in range(len(L)):
        L[i]=list(set(L[i]))
        
    for i in range(len(L)):
        if len(L[i])>=1:
            attacks="Attack"
            if i>=2:
                attacks=attacks+"s"
            embed.add_field(name=f"**"+str(i+1)+" "+attacks+"**", value='•'+'\n•'.join(L[i]), inline=False)
    await ctx.reply(embed=embed,mention_author=False)
    await ctx.message.delete()

@client.command()
async def check_disc(ctx,discord_id=None):
    afk_players,clan_dict,medals,deck=royaleapi.get_players()
    if discord_id!=None:
        players=clan_dict.keys()
        for player in players:
            if clan_dict[player]['discord']==discord_id:
                await ctx.reply(clan_dict[player]['name']+', est assigné à ce discord.')
                await ctx.message.delete()
                return(None)
        await ctx.reply('<@'+discord_id+"> n'a pas de compte CR associé.")
        await ctx.message.delete()
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

    sentence2='\n'
    
    count=0
    members=ctx.message.guild.members
    discord_ids=[]
    for member in members:
        discord_ids.append(member.id)
    
    players=clan_dict.keys()
    for player in players:
        if clan_dict[player]['discord']!='' and clan_dict[player]['discord'] not in discord_ids:
            sentence2+=clan_dict[player]['name']+', '
            count+=1

    if sentence2!='\n':
        if count<=1:
            sentence2+='a un mauvais discord renseigné.'
        else:
            sentence2+="ont un mauvais discord renseigné."
        await ctx.reply(sentence+sentence2)
    else:
        await ctx.reply(sentence)
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
