import pyupbit
import functions
import time

MONEY = 200000
N = 50


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
print("|마켓코드\t|k-value\t|과거수익률(%)\t|기대수익률(%)\t|매수가(원)\t|매수상한가(원)\t|현재가(원)\t|예측종가(원)\t|가능성\t|")
print(
    "|---------------|---------------|---------------|---------------|---------------|---------------|---------------|---------------|-------|"
)
for i, e in enumerate(today_coin_list):
    # 현재가 조회
    current_price = pyupbit.get_orderbook(ticker=e[0])["orderbook_units"][0][
        "ask_price"
    ]
    k_value, past_ROR = functions.get_k_value(e[0])
    past_ROR = (past_ROR - 1) * 100
    # 예측 데이터 기반 기대수익률
    ROR = (e[3] / e[1] - 1) * 100
    if e[3] <= e[1] or ROR <= 0.5:
        check = "░░░"
    else:
        check = "▓▓▓"
        possible.append(
            f"|{e[0]:<10}\t|{k_value:<10.5f}\t|{past_ROR:<10.5f}\t|{ROR:<10.3f}\t|{e[1]:<10.5f}\t|{e[1] * 1.005:<10.5f}\t|{current_price:<10}\t|{e[3]:<10.5f}\t|  {check}  |"
        )
    print(
        f"|{e[0]:<10}\t|{k_value:<10.5f}\t|{past_ROR:<10.5f}\t|{ROR:<10.3f}\t|{e[1]:<10.5f}\t|{e[1] * 1.005:<10.5f}\t|{current_price:<10}\t|{e[3]:<10.5f}\t|  {check}  |"
    )
    time.sleep(0.125)

print(
    "|===============|===============|===============|===============|===============|===============|===============|===============|=======|"
)
for e in possible:
    print(e)
