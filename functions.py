import pyupbit
import numpy as np


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


def get_k_value(market_code: str) -> float:
    """특정 코인의 k값을 찾는 함수

    Args:
        market_code (str): 특정 코인의 마켓코드 (KRW-BTC..)

    Returns:
        float: 특정 코인의 k값
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
    return maximum[0]
