import pyupbit
import time
import datetime
import functions
import pprint

MONEY = 5000
N = 3

# 계정 정보 불러오기
f = open("./account_information.txt")
lines = f.readlines()
access = lines[0].strip()
secret = lines[1].strip()
f.close()

# 로그인
my_upbit = pyupbit.Upbit(access=access, secret=secret)

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
            
            print("\033[31mGET: LIST\033[0m\a")
            # 코인 정보 리스트를 불러온다.
            today_coin_list = functions.calculate_all_target_price(N)
            print("\033[31mDONE\033[0m")
            
            pprint.pprint(today_coin_list)
            
            print("\033[31mADD: INFORMATION\033[0m")
            # 코인별 거래 확인용 체크란 생성
            for i in range(len(today_coin_list)):
                predicted_close_price = functions.calculate_predict_close_price(today_coin_list[i][0])
                print(predicted_close_price)
                
                today_coin_list[i].append(predicted_close_price)
                today_coin_list[i].append(0)
            print("\033[31mDONE\033[0m")
                
            pprint.pprint(today_coin_list)
        
        # 금일 09:10 ~ 명일 08:50 에만 거래 활성화
        if start_time + datetime.timedelta(seconds=600) < now < end_time - datetime.timedelta(seconds=600):
            # 코인별 정보 확인
            for i, e in enumerate(today_coin_list):
                # 코인별 정보 파싱
                market_code = e[0]
                target_price = e[1]
                predicted_close_price = e[3]
                is_trade = e[4]
                
                # 현재가 조회
                current_price = pyupbit.get_orderbook(ticker=market_code)["orderbook_units"][0]["ask_price"]
                
                # 조회 정보 확인
                print("================================")
                print(f"market_code:\t{market_code}")
                print(f"target_price:\t{target_price}")
                print(f"predicted_close_price:\t{predicted_close_price}")
                print(f"is_trade:\t{is_trade}")
                print(f"current_price:\t{current_price}\n")
                
                # 아직 거래가 이루어지지 않은 경우에 한해서 거래
                if is_trade == 0:
                    # 매수가 달성 시 (현재가 > 매수가)
                    if current_price > target_price:
                        my_krw = my_upbit.get_balance("KRW")
                        
                        print("\033[31m-=-매수가 달성!-=-\033[0m")
                        # 업비트 최소 거래 금액
                        if my_krw > MONEY:
                            # 매수 진행
                            my_upbit.buy_market_order(market_code, MONEY)
                            today_coin_list[i][4] = 1
                            print(f"체결: \033[35m{market_code}\033[0m")
                else:
                    print(f"\033[35m{market_code}\033[0m는 이미 체결된 코인입니다.")
        # 지정 시간 이탈 시 전량 매도
        else:
            for i, e in enumerate(today_coin_list):
                market_code = e[0]
                balance = my_upbit.get_balance(market_code)
                my_upbit.sell_market_order(market_code, balance)
        
        time.sleep(1)
        
    except Exception as e:
        print(e)
        time.sleep(1)
