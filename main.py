import pyupbit
import time
import datetime
import functions
import pprint


def login_upbit() -> pyupbit.Upbit:
    f = open("./tmp.txt")
    lines = f.readlines()
    access = lines[0].strip()
    secret = lines[1].strip()
    f.close()
    return pyupbit.Upbit(access, secret)


# 프로그램 시작
print("==========================")
print("Welcome! Auto Coin Trader!")
print("==========================")
# 로그인
my_upbit = login_upbit()
print("\033[32m===== Login  Success =====\033[0m")

MONEY = 300000
N = 50

today_coin_list = []
while True:
    try:
        # 현재 datetime 객체 생성
        now = datetime.datetime.now()

        # 시작 시간과 끝 시간
        start_time = pyupbit.get_ohlcv("KRW-BTC", interval="day", count=1).index[0]
        end_time = start_time + datetime.timedelta(days=1)

        # 8:00~8:02 리스트를 불러온다. 임의의 확률로 리스트가 비어있는 경우도 확인한다.
        if (
            start_time - datetime.timedelta(hours=1)
            < now
            < start_time - datetime.timedelta(hours=1) + datetime.timedelta(minutes=2)
            or len(today_coin_list) == 0
        ):
            # 우선 리스트를 비운다.
            today_coin_list.clear()

            # 코인 정보 리스트를 불러온다.
            print("\033[31mGet Coins list\033[0m(at 30 seconds..)")
            today_coin_list = functions.calculate_all_target_price(N)
            print(f"mGet \033[31{N}\033[0m coins information")

            # 파일 경로
            file_path = './information.txt'
            # 파일 내용 비우기
            with open(file_path, 'w'):
                pass

            # 코인별 예측값 생성
            print("\033[31mAdd additional information(predicted close price..)\033[0m")
            for i in range(len(today_coin_list)):
                predicted_close_price = functions.calculate_predict_close_price(
                    today_coin_list[i][0]
                )
                today_coin_list[i].append(predicted_close_price)
                today_coin_list[i].append(0)

                # 매수 체결 가능성
                # 예측값이 매수가보다 낮은 경우 and 기대수익률이 0.5% 미만인 경우 0을 기록, txt파일에 저장
                buying_price = today_coin_list[i][1]
                if (
                    predicted_close_price <= buying_price
                    or (predicted_close_price / buying_price - 1) * 100 < 0.5
                ):
                    today_coin_list[i].append(0)
                # 아닌 경우 1을 기록
                else:
                    today_coin_list[i].append(1)
                    with open(file_path, 'a') as f:
                        f.write(str(today_coin_list[i]))

            print("\033[31mDONE\033[0m")
            time.sleep(20)

        # 금일 08:02 ~ 명일 07:55 에만 거래 활성화
        if (
            start_time - datetime.timedelta(hours=1) + datetime.timedelta(minutes=2)
            < now
            < end_time - datetime.timedelta(hours=1) - datetime.timedelta(minutes=5)
        ):
            # 코인별 정보 확인
            for i, e in enumerate(today_coin_list):
                # 코인별 정보 파싱
                market_code = e[0]
                target_price = e[1]
                predicted_close_price = e[3]
                is_trade = e[4]
                is_possible = e[5]

                # 매수 체결 가능성이 없는 경우 조회하지 않음
                if not is_possible:
                    continue

                ROR = ((predicted_close_price / target_price) - 1) * 100

                # 현재가 조회
                current_price = pyupbit.get_orderbook(ticker=market_code)[
                    "orderbook_units"
                ][0]["ask_price"]

                # 조회 정보 확인 코드
                # print("================================")
                # print(f"market_code:\t{market_code}")
                # print(f"target_price:\t{target_price}")
                # print(f"predicted_close_price:\t{predicted_close_price}")
                # print(f"is_trade:\t{is_trade}")
                # print(f"current_price:\t{current_price}\n")

                # 아직 거래가 이루어지지 않은 경우에 한해서 거래
                if is_trade == 0:
                    # 매수가 달성 시 (현재가 > 매수가), 예측 종가보다 낮은 경우 (현재가 < 예측 종가), ROR이 0.125% 이상인 경우 (업비트 수수료 0.05%), 현재가가 매수가의 +0.5% 미만인 경우
                    if (
                        target_price < current_price < target_price * 1.005
                        and current_price < predicted_close_price
                        and ROR >= 0.5
                    ):
                        my_krw = my_upbit.get_balance("KRW")

                        print(
                            f"\033[31mBuyout Reached\033[0m: \033[35m{market_code}\033[0m"
                        )
                        # 업비트 최소 거래 금액
                        if my_krw > MONEY and my_krw > 7000:
                            # 매수 진행
                            my_upbit.buy_market_order(market_code, MONEY)
                            today_coin_list[i][4] = 1
                            print(f"Sign: \033[35m{market_code}\033[0m")
                        else:
                            print("\033[41m-=-거래금액 불충족-=-\033[0m")
                    # else:
                    #     print(f"\033[34m매수가 미만\033[0m: \033[35m{market_code}\033[0m")
                # else:
                #     print(f"\033[35m{market_code}\033[0m는 이미 체결된 코인입니다.")
                time.sleep(0.25)
        # 지정 시간 이탈 시 전량 매도 후 프로그램 종료
        else:
            print("Market Finished")
            for i, e in enumerate(today_coin_list):
                market_code = e[0]
                balance = my_upbit.get_balance(market_code)
                my_upbit.sell_market_order(market_code, balance)

        time.sleep(1)

    except Exception as e:
        print(e)
        time.sleep(1)
