import pyupbit


def get_target_price(market_code: str, k: float):
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
