
import discord
from discord.ext import commands, tasks

from bs4 import BeautifulSoup
import requests
import time
#import datetime
#import random

intents = discord.Intents.all()
embed = discord.Embed()
client = discord.Client(intents=intents)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

def crawl():
    NoticeTitle = []
    Links = []
    Date = []

    for i in range(0,2):
        num=i*10
        url=requests.get(f"https://www.skku.edu/skku/campus/skk_comm/notice01.do?mode=list&&articleLimit=10&article.offset={num}", headers=headers)
        soup=BeautifulSoup(url.text, "html.parser")
        all=soup.find_all('dt', "board-list-content-title")

        for dt in all:
            a_tag=dt.find('a')
            href = a_tag.attrs['href']
            if a_tag:
                text_within_a=a_tag.get_text(strip=True)
                NoticeTitle.append(text_within_a)
                Links.append('https://www.skku.edu/skku/campus/skk_comm/notice01.do'+href)

        
        date = soup.find_all('dd',class_="board-list-content-info")
        for dd in date:
            datedate = dd.find_all('li')[2].get_text()
            Date.append(datedate)
    
    return NoticeTitle, Links, Date
    

app = commands.Bot(command_prefix='!',intents= intents)



@app.event
async def on_ready():
    print(app.user.name, 'has connected to Discord!')
    await app.change_presence(status=discord.Status.do_not_disturb,activity=None)
    print("ready")


@app.command("공지사항")
async def 공지사항(ctx):
    await ctx.send('잠시만 기다려주세요...')
    NoticeTitle, Links, Date = crawl()
    message = []
    for i in range(20):
        #Notice = NoticeTitle[i]
        #Link = Links[i]
        embed.description = f"{i+1}. [{NoticeTitle[i]}]({Links[i]}) 게시일 : {Date[i]}"
        message.append(embed.description+'\n')
    #print(message)
    embed.description = ('\n'.join(message))
    await ctx.send(embed=embed)

@app.command('공지키워드')
async def 공지키워드(ctx):
    NoticeTitle, Links, Date = crawl()
    await ctx.send('알림 받고 싶은 키워드를 입력해주세요')
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    msg = await app.wait_for('message', check=check)

    await ctx.send(f'키워드 : {msg.content}')
    message = []
    for i in range(20):
        embed.description = f"{i+1}. [{NoticeTitle[i]}]({Links[i]}) 게시일 : {Date[i]}"
        if msg.content in embed.description:
            message.append(embed.description+'\n')
    #print(message)
    embed.description = ('\n'.join(message))
    await ctx.send(embed=embed)

@app.command('공지그만받기')
async def 공지그만받기(ctx):
    await ctx.send('공지를 그만받습니다')
    global stopNotice
    stopNotice = False


@app.command('자동공지설정')
async def 자동공지설정(ctx):
    global stopNotice
    stopNotice = True
    await ctx.send('키워드를 입력해주세요. 모두 받으시려면 전체공지를 입력해주세요')
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    msg = await app.wait_for('message', check=check)

    if msg.content == '전체공지':
        await ctx.send('공지사항 10개를 1시간마다 받습니다')
        while stopNotice == True:
            message = []
            NoticeTitle, Links, Date = crawl()
            for i in range(10):
                embed.description = f"{i+1}. [{NoticeTitle[i]}]({Links[i]}) 게시일 : {Date[i]}"
                message.append(embed.description+'\n')
            embed.description = ('\n'.join(message))
            await ctx.send(embed=embed)
            time.sleep(5)


    else:
        await ctx.send(f'키워드 {msg.content}에 대한 공지사항을 1시간마다 받습니다')
        while stopNotice == True:
            message = []
            NoticeTitle, Links, Date = crawl()
            for i in range(10):
                embed.description = f"{i+1}. [{NoticeTitle[i]}]({Links[i]}) 게시일 : {Date[i]}"
                if msg.content in embed.description:
                    message.append(embed.description+'\n')
            embed.description = ('\n'.join(message))
            await ctx.send(embed=embed)
            if stopNotice:
                False
            time.sleep(5)

'''@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("현재 지원하는 명령어 : !공지사항, !공지키워드, !자동공지설정, !공지그만받기")
'''

app.run('Your Token Here')
