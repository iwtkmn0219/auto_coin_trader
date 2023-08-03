import pyupbit
import time
import datetime
import functions
import pprint

MONEY = int(input("코인 당 가격을 입력하십시오.(원): "))
N = int(input("선별할 코인의 개수를 입력하십시오.(개): "))

print("로그인 하였습니다.")

def login_upbit() -> pyupbit.Upbit:
    # 로그인 정보 입력
    access = input()
    secret = input()
    return pyupbit.Upbit(access, secret)

# 프로그램 시작
print("==========================")
print("Welcome! Auto Coin Trader!")
print("==========================")
login_upbit()
print("\033[32m===== Login  Success =====\033[0m")
today_coin_list = []
while True:
    try:
        # 현재 datetime 객체 생성
        now = datetime.datetime.now()
        
        # 시작 시간과 끝 시간
        start_time = pyupbit.get_ohlcv("KRW-BTC", interval="day", count=1).index[0]
        end_time = start_time + datetime.timedelta(days=1)
        
        # 하루에 한 번 리스트를 불러온다. 임의의 확률로 리스트가 비어있는 경우도 확인한다.
        if start_time + datetime.timedelta(seconds=60) < now < start_time + datetime.timedelta(seconds=300) or len(today_coin_list) == 0:
            # 우선 리스트를 비운다.
            today_coin_list.clear()
            
            print("\033[31m코인의 리스트를 불러옵니다.(약30초 소요)\033[0m")
            # 코인 정보 리스트를 불러온다.
            today_coin_list = functions.calculate_all_target_price(N)
            print(f"\033[31m{N}개의 코인에 대한 정보를 불러왔습니다.\033[0m")
            
            pprint.pprint(today_coin_list)
            
            print("\033[31mADD INFORMATION AND PREDICT CLOSE PRICE\033[0m")
            # 코인별 거래 확인용 체크란 생성
            for i in range(len(today_coin_list)):
                predicted_close_price = functions.calculate_predict_close_price(today_coin_list[i][0])
                print(predicted_close_price)
                
                today_coin_list[i].append(predicted_close_price)
                today_coin_list[i].append(0)
            print("\033[31mDONE\033[0m")
                
            pprint.pprint(today_coin_list)
        
        # # 금일 09:10 ~ 명일 08:50 에만 거래 활성화
        # if start_time + datetime.timedelta(seconds=600) < now < end_time - datetime.timedelta(seconds=600):
        # 금일 09:00 ~ 금일 24:00 에만 거래 활성화
        if start_time < now < start_time + datetime.timedelta(hours=15):
            # 코인별 정보 확인
            for i, e in enumerate(today_coin_list):
                # 코인별 정보 파싱
                market_code = e[0]
                target_price = e[1]
                predicted_close_price = e[3]
                is_trade = e[4]
                
                # 현재가 조회
                current_price = pyupbit.get_orderbook(ticker=market_code)["orderbook_units"][0]["ask_price"]
                
                # # 조회 정보 확인 코드
                # print("================================")
                # print(f"market_code:\t{market_code}")
                # print(f"target_price:\t{target_price}")
                # print(f"predicted_close_price:\t{predicted_close_price}")
                # print(f"is_trade:\t{is_trade}")
                # print(f"current_price:\t{current_price}\n")
                
                # 아직 거래가 이루어지지 않은 경우에 한해서 거래
                if is_trade == 0:
                    # 매수가 달성 시 (현재가 > 매수가), 예측 종가보다 낮은 경우 (현재가 < 예측 종가)
                    if current_price > target_price and current_price < predicted_close_price:
                        my_krw = my_upbit.get_balance("KRW")
                        
                        print(f"\033[31m매수가 도달\033[0m: \033[35m{market_code}\033[0m")
                        # 업비트 최소 거래 금액
                        if my_krw > MONEY:
                            # 매수 진행
                            my_upbit.buy_market_order(market_code, MONEY)
                            today_coin_list[i][4] = 1
                            print(f"체결: \033[35m{market_code}\033[0m")
                        else:
                            print("\033[41m-=-거래금액 불충족-=-\033[0m")
                    # else:
                    #     print(f"\033[34m매수가 미만\033[0m: \033[35m{market_code}\033[0m")
                # else:
                #     print(f"\033[35m{market_code}\033[0m는 이미 체결된 코인입니다.")
                time.sleep(1)
        # 지정 시간 이탈 시 전량 매도 후 프로그램 종료
        else:
            print("시장 종료")
            for i, e in enumerate(today_coin_list):
                market_code = e[0]
                balance = my_upbit.get_balance(market_code)
                my_upbit.sell_market_order(market_code, balance)
            print("프로그램을 종료합니다")
            break
        
        time.sleep(1)
        
    except Exception as e:
        print(e)
        time.sleep(1)
