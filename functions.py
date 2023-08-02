import pyupbit
import numpy as np
import time
import pprint


def get_target_price(market_code: str, k: float) -> float:
    """k값(변동성 돌파 전략)으로 특정 코인의 매수가를 특정하는 함수

    Args:
        market_code (str): 특정 코인의 마켓코드 (KRW-BTC..)
        k (float): 변동성 돌파 전략에서의 k값

    Returns:
        float: k값을 기반으로 한 매수가
    """
    df = pyupbit.get_ohlcv(market_code, interval="day", count=2)
    target_price = df.iloc[0]["close"] + (df.iloc[0]["high"] - df.iloc[0]["low"]) * k
    return target_price


def get_k_value(market_code: str) -> tuple:
    """특정 코인의 k값을 찾는 함수

    Args:
        market_code (str): 특정 코인의 마켓코드 (KRW-BTC..)

    Returns:
        tuple: 특정 코인의 k값에 관한 정보 [k-value, ROR]
    """
    # 해당 코인의 31일간의 정보를 불러온다.
    df = pyupbit.get_ohlcv(market_code, count=7)
    df = df.drop("value", axis=1)

    # 0.01단위로 k값을 대입해보아 최적의 k값을 찾는다.
    maximum = [0, 0]
    for k in np.arange(0.1, 1.0, 0.01):
        # 부동 소수점 오차 제거
        k = round(k, 3)

        # 매수가 계산
        df["range"] = (df["high"] - df["low"]) * k
        df["target"] = df["open"] + df["range"].shift(1)

        # 수익률
        df["ROR"] = np.where(
            (df["high"] + df["close"]) / 2 > df["target"], df["close"] / df["target"], 1
        )

        # 최종 수익률
        final_ROR = df["ROR"].cumprod()[-1]

        # k값 갱신
        if final_ROR > maximum[1]:
            maximum[0] = k
            maximum[1] = final_ROR
    return tuple(maximum)


def calculate_all_target_price(x: int) -> list:
    """모든 코인에 대한 매수가 계산(소요시간: 약 30초(API GET))

    Args:
        x (int): 선택할 코인의 개수

    Returns:
        list: 과거 7일간의 ROR에 대한 상위 x개의 코인에 대한 k, 매수가, 과거 7일간의 ROR을 리스트 형태로 반환한다.
    """
    # KRW 단위 코인만 불러온다.
    all_tickers = pyupbit.get_tickers(fiat="KRW")

    # 리스트에 k, 매수가, 과거 7일간의 ROR을 담는다.
    target_price_list = []
    for market_code in all_tickers:
        k, expected_return = get_k_value(market_code)
        target_price = get_target_price(market_code, k)
        target_price_list.append([market_code, target_price, expected_return])

    # 과거 7일간의 ROR을 바탕으로 내림차순 정렬한다.
    target_price_list = sorted(target_price_list, key=lambda x: x[2], reverse=True)

    return target_price_list[:x]