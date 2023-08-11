import discord
import asyncio
import pyupbit
from datetime import datetime, timedelta

# discord bot token
DISCORD_TOKEN = (
    "YOUR DISCORD TOKEN"
)
# discord channel id (일반)
CHANNEL_ID = 1137546202708185182

# 업비트 로그인
f = open("./tmp.txt")
lines = f.readlines()
access = lines[0].strip()
secret = lines[1].strip()
f.close()
my_upbit = pyupbit.Upbit(access, secret)

# 디스코드 접근
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
client = discord.Client(intents=intents)


# 메시지 전송
async def send_message(msg: str):
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(msg)
    else:
        print("Cannot found channel")


# 특정 시간에 메시지를 전송한다.
async def send_message_at():
    current_time = datetime.now()
    if current_time.hour == 7 and current_time.minute == 58:
        current_krw = my_upbit.get_balance("KRW")
        task = asyncio.create_task(send_message(f"{current_time.year}년 {current_time.month}월 {current_time.day}일: 현재 보유 KRW는 {format(round(current_krw), ',')}원 입니다."))
        await task

    if current_time.hour == 8 and current_time.minute == 10:
        file_path = './information.txt'
        result = 'Today Information\n'
        with open(file_path, 'r') as f:
            content = f.read().split(']')
            for i, e in enumerate(content):
                if i == len(content) - 1:
                    break
                tmp = e.split(', ')
                market_code = tmp[0][2:-1]
                buying_price = float(tmp[1])
                ROR = tmp[2]
                predicted_price = float(tmp[3])
                result += f"```diff\n+ {market_code}\n{buying_price:<13.5f} ::>> {predicted_price:13.5f}({round((predicted_price / buying_price - 1) * 100, 3)})```"
        task = asyncio.create_task(send_message(result))
        await task
    await asyncio.sleep(59)


@client.event
async def on_ready():
    print(f"Success Login (로그인 정보: {client.user})")
    while True:
        task = asyncio.create_task(send_message_at())
        await task


@client.event
async def on_diconnect():
    print(f"{client.user}의 연결이 끊어졌습니다.")


client.run(DISCORD_TOKEN)
