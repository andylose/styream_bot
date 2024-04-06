from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time, sys
import datetime 
from discord import Status, Activity, ActivityType
import discord
from discord.ext import commands, tasks


help_command = commands.DefaultHelpCommand(no_category = "Commands")
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, description = "[!]為前綴指令(*為需管理員權限)", help_command = help_command)
sent_links = set()
sys.stdout.reconfigure(encoding="utf-8")
tz = datetime.timezone(datetime.timedelta(hours = 8))
streamer = []


@bot.event
async def on_ready():
    print(f'{bot.user} 已上線')
    await read_links()
    await bot.change_presence(status=Status.online, activity=Activity(type=ActivityType.watching, name="Type !help"))

async def read_links():
    try:
        with open("link.txt", "r") as file:
            for line in file:
                streamer.append(line.strip())
    except FileNotFoundError:
        print("沒有直播鏈結")

@bot.command(brief="添加直播鏈結")
async def addlink(ctx, url):
    streamer.append(url)
    channel = bot.get_channel(1224746470930907279)
    await channel.send(f"已**添加**鏈結：{url}")
    await write_links(url)

async def write_links(url):
      with open("link.txt", "a") as file:
            file.write(url + "\n")

@bot.command(brief="查看所有直播鏈結")
async def showlinks(ctx):
    channel = bot.get_channel(1224746470930907279)
    if streamer:
        link_list = '\n'.join([f"{number + 1}. {link}" for number, link in enumerate(streamer)])
        await channel.send("目前已添加的鏈結：\n```" + link_list + "```")
    else:
        await channel.send("目前沒有任何鏈結")   

@bot.command(brief="刪除直播鏈結(使用showlink指令查詢鏈結編號)")
async def deletelink(ctx, number: int):
    if number > 0 and number <= len(streamer):
        deleted_link = streamer.pop(number - 1)
        channel = bot.get_channel(1224746470930907279)
        await channel.send(f"已**刪除**鏈結：{deleted_link}")
        await cover_links()
    else:
        channel = bot.get_channel(1224746470930907279)
        await channel.send("請提供有效的編號(可使用showlinks指令查詢編號)")

async def cover_links():
      with open("link.txt", "w") as file:
            for link in streamer:
                  file.write(link + "\n")

@bot.command(brief="*建立直播提及的身份組")
@commands.has_permissions(administrator=True)
async def RoleCreat(ctx):
    role = await ctx.guild.create_role(name="StreamMention", mentionable=True)
    await ctx.channel.send("StreamMention身分組已創建")

@bot.command(brief="*刪除直播提及的身份組")
@commands.has_permissions(administrator=True)
async def RoleRemove(ctx, role: discord.Role):
    if role.name == "StreamMention":
        await role.delete()
        await ctx.channel.send("StreamMention身分組已刪除")
    
    
def check_streaming(url):
      driver = webdriver.Chrome()
      link =""
      title =""
      name ="" 
      icon =""
      driver.get(url)
      try:
            live = driver.find_element(By.CSS_SELECTOR, "[aria-label='直播']")
            streaming = True
            action = ActionChains(driver)
            action.move_to_element_with_offset(live, -20, 20) 
            action.click()
            action.perform()
            time.sleep(3)
            title = driver.find_element(By.XPATH,"//body/ytd-app[1]/div[1]/ytd-page-manager[1]/ytd-watch-flexy[1]/div[5]/div[1]/div[1]/div[2]/ytd-watch-metadata[1]/div[1]/div[1]/h1[1]/yt-formatted-string[1]")
            link = driver.current_url
            name = driver.find_element(By.XPATH,'//*[@id="text"]/a')
            icon = driver.find_element(By.XPATH, "//*[@id='img']")
            icon_url = icon.get_attribute("src")

            return streaming, title.text, name.text, link, icon_url
      
      except:
            streaming = False  
            driver.quit()
            return False,None,None,None,None
      
def check_streaming(url):
      driver = webdriver.Chrome()
      link =""
      title =""
      name ="" 
      icon =""
      driver.get(url)
      try:
            live = driver.find_element(By.CSS_SELECTOR, "[aria-label='直播']")
            streaming = True
            action = ActionChains(driver)
            action.move_to_element_with_offset(live, -20, 20) 
            action.click()
            action.perform()
            time.sleep(3)
            title = driver.find_element(By.XPATH,"//body/ytd-app[1]/div[1]/ytd-page-manager[1]/ytd-watch-flexy[1]/div[5]/div[1]/div[1]/div[2]/ytd-watch-metadata[1]/div[1]/div[1]/h1[1]/yt-formatted-string[1]")
            link = driver.current_url
            name = driver.find_element(By.XPATH,'//*[@id="text"]/a')
            icon = driver.find_element(By.XPATH, "//*[@id='img']")
            icon_url = icon.get_attribute("src")

            return streaming, title.text, name.text, link, icon_url
      
      except:
            streaming = False  
            driver.quit()
            return False,None,None,None,None


def run_schedule():
    driver = webdriver.Chrome()
    driver.get("https://hololive.hololivepro.com/en/schedule")
    time.sleep(2)

    Stitles = driver.find_elements(By.CLASS_NAME, "txt")
    Snames = driver.find_elements(By.CLASS_NAME, "name")
    Time = driver.find_elements(By.CLASS_NAME, "start")
    playings = driver.find_elements(By.CLASS_NAME, "start.now")

    play_count = len(playings)
    schedule = ""

    for title, name, times in zip(Stitles, Snames, Time):
        title_text = title.text
        name_text = name.text
        time_text = times.text

        if play_count > 0 and title_text and name_text:
            schedule += "\n> **[直播中]** " + time_text + " - < ** *" + name_text + "* ** >\n> " + title_text + "\n"
            play_count -= 1
        elif title_text and name_text:
            schedule += '\n> '+ time_text + " - < ** *" + name_text + "* ** > \n> " + title_text + "\n"

    driver.quit()
    return schedule

#手動           
@bot.command(brief="查詢行程表")
async def schedule(ctx):
    channel = bot.get_channel(1224746470930907279) 
    await channel.send("查詢中🔄️",delete_after=1)
    schedule_message = run_schedule()
    embed = discord.Embed(title="行程表", description=schedule_message, color=0xb0e0e6)
    role = discord.utils.get(ctx.guild.roles, name="StreamMention")
    if role:
        await channel.send(role.mention)
    await channel.send(embed=embed)

@bot.command(brief="查詢直播")
async def stream(ctx):
    channel = bot.get_channel(1224746470930907279)
    await channel.send("查詢中🔄️",delete_after=1)
    cheak = True
    role = discord.utils.get(ctx.guild.roles, name="StreamMention")
    for url in streamer:
        is_streaming, title, name, link, icon= check_streaming(url)
        if link not in sent_links and is_streaming == True:

            embed = discord.Embed(
                title=title,
                description=name +" 開始直播了",
                color=0xff0000
            )
            cheak = False
            sent_links.add(link)
            embed.set_author(name=name, icon_url=icon)
            if role:
                await channel.send(role.mention)
            await channel.send(" 鏈結: " + link)
            await channel.send(embed=embed)
            
        else:
                continue   
    if cheak :    
            await channel.send("目前無任何直播")

#自動
@tasks.loop(minutes=5)
async def streaming(ctx):
      channel = bot.get_channel(1224746470930907279)
      role = discord.utils.get(ctx.guild.roles, name="StreamMention")
      for url in streamer:
            is_streaming, title, name, link, icon = check_streaming(url)
            if link not in sent_links and is_streaming == True:
                if role:
                    await channel.send(role.mention)
                embed = discord.Embed(
                    title=title,
                    description=name +" 開始直播了",
                    color=0xff0000
                )
                sent_links.add(link)
                embed.set_author(name=name, icon_url=icon)
                await channel.send(" 鏈結: " + link)
                await channel.send(embed=embed)
            else:
                 continue      


@tasks.loop(seconds=60)  
async def schedule_once_day(ctx):
    now = datetime.datetime.now(tz)
    role = discord.utils.get(ctx.guild.roles, name="StreamMention")
    if now.hour == 0 and now.minute == 0:
        channel = bot.get_channel(1224746470930907279) 
        schedule_message = run_schedule()
        if role:
            await channel.send(role.mention)
        embed = discord.Embed(title="行程表", description=schedule_message, color=0xb0e0e6)
        await channel.send(embed=embed)

#行程表&直播開關
@bot.command(brief="*開始自動傳送直播通知")
@commands.has_permissions(administrator=True)
async def startstream(ctx):
    channel = bot.get_channel(1224746470930907279)
    await channel.send("已**開始**直播通知")
    streaming.start()
    
    
@bot.command(brief="*停止自動傳送直播通知")  
@commands.has_permissions(administrator=True)
async def stopstream(ctx):
    streaming.stop()
    channel = bot.get_channel(1224746470930907279)
    await channel.send("已**停止**直播通知")

@bot.command(brief="*開啟自動傳送行程表")
@commands.has_permissions(administrator=True)
async def startschedule(ctx):
    schedule_once_day.start()
    channel = bot.get_channel(1224746470930907279)
    await channel.send("已**開始**行程表")
    
@bot.command(brief="*停止自動傳送行程")  
@commands.has_permissions(administrator=True)
async def stopschedule(ctx):
    schedule_once_day.stop()
    channel = bot.get_channel(1224746470930907279)
    await channel.send("已**停止**行程表")


@bot.command(brief="*關閉機器人")
@commands.has_permissions(administrator=True)
async def off(ctx):
    await ctx.send("正在關閉")
    print("OFF")
    await bot.close() 

bot.run("MTIxNjc1NTc4NDU5MjEzNDE0NA.Gg3UE8.F9XMxhQmVAfNQ0dg19MKpb-rT9ZmqH05fu6c20")



