import pyupbit
import functions
import time

MONEY = 60000
N = 20


def login_upbit() -> pyupbit.Upbit:
    f = open("./tmp.txt")
    lines = f.readlines()
    access = lines[0].strip()
    secret = lines[1].strip()
    f.close()
    return pyupbit.Upbit(access, secret)


today_coin_list = []
today_coin_list.clear()

# 코인 정보 리스트를 불러온다.
print("\033[31mGet Coins list\033[0m(at 30 seconds..)")
today_coin_list = functions.calculate_all_target_price(N)
print(f"Get \033[31m{len(today_coin_list)}/{N}\033[0m coins information")

# 코인별 예측값 생성
print("\033[31mAdd additional information(predicted close price..)\033[0m")
for i in range(len(today_coin_list)):
    predicted_close_price = functions.calculate_predict_close_price(
        today_coin_list[i][0]
    )
    today_coin_list[i].append(predicted_close_price)
    today_coin_list[i].append(0)
print("\033[31mDONE\033[0m")

possible = []
print("|마켓코드\t|현재가\t\t|매수가\t\t|예측종가\t|가능성\t|")
print("|---------------|---------------|---------------|---------------|---|")
for i, e in enumerate(today_coin_list):
    # 현재가 조회
    current_price = pyupbit.get_orderbook(ticker=e[0])["orderbook_units"][0][
        "ask_price"
    ]
    if e[3] <= e[1]:
        check = "░░░"
    else:
        check = "▓▓▓"
        possible.append(f"|{e[0]:<10}\t|{current_price:<10}\t|{e[1]:<10.3f}\t|{e[3]:<10.3f}\t|  {check}  |")
    print(f"|{e[0]:<10}\t|{current_price:<10}\t|{e[1]:<10.3f}\t|{e[3]:<10.3f}\t|  {check}  |")
    time.sleep(0.125)

print("|===============|===============|===============|===============|===|")
for e in possible:
    print(e)