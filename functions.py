import pyupbit
import numpy as np
from prophet import Prophet
import time


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
    # 해당 코인의 200일간의 정보를 불러온다.
    df = pyupbit.get_ohlcv(market_code)
    df = df.drop("value", axis=1)

    # 보유시 수익률
    holding_return = df.iloc[-1, 3] / df.iloc[0, 0]

    # 0.01단위로 k값을 대입해보아 최적의 k값을 찾는다.
    maximum = [0, 0, 0]
    for k in np.arange(0.1, 1.0, 0.01):
        # 부동 소수점 오차 제거
        k = round(k, 3)

        # 매수가 계산
        df["range"] = (df["high"] - df["low"]) * k
        df["target"] = df["open"] + df["range"].shift(1)

        # 수익률
        df["ROR"] = np.where(df["high"] > df["target"], df["close"] / df["target"], 1)

        # 누적 수익률
        df["hpr"] = df["ROR"].cumprod()

        # 낙폭
        df["draw down"] = (df["hpr"] - df["hpr"].cummax()) / df["hpr"].cummax()
        # 최대 낙폭
        MDD = df["draw down"].min()

        # 최종 수익률
        final_ROR = df["ROR"].cumprod()[-1]

        # sharpe param
        df["sp"] = df["ROR"] - holding_return
        std_exp = df["sp"].mean()
        std_sp = df["sp"].std()

        # 샤프 지수
        sharpe_ratio = std_exp / std_sp

        # 선정 기준 설정
        value = sharpe_ratio + MDD * 25
        # print(f"k = {k},\tfinal_ROR = {final_ROR:.3f},\tMDD = {MDD:.3f},\t수치 = {value:.3f}")

        # k값 갱신
        if value > maximum[2] or maximum[2] == 0:
            maximum[0] = k
            maximum[1] = final_ROR
            maximum[2] = value
    # print(maximum)

    result: tuple = (maximum[0], maximum[1])
    return result


def calculate_all_target_price(x: int) -> list:
    """모든 코인에 대한 매수가 계산(소요시간: 약 30초(API GET))

    Args:
        x (int): 선택할 코인의 개수

    Returns:
        list: 과거 7일간의 ROR에 대한 상위 x개의 코인에 대한 k, 매수가, 과거 7일간의 ROR을 리스트 형태로 반환한다.
    """
    # KRW 단위 코인만 불러온다.
    all_tickers = pyupbit.get_tickers(fiat="KRW")

    # 리스트에 k, 매수가, 과거 200일간의 ROR을 담는다.
    target_price_list = []
    for i, market_code in enumerate(all_tickers):
        k, expected_return = get_k_value(market_code)
        target_price = get_target_price(market_code, k)
        target_price_list.append([market_code, target_price, expected_return])
        if i % 10 == 0:
            print(f"{i}: Get coin({market_code}) information")

    # 과거 200일간의 ROR을 바탕으로 내림차순 정렬한다.
    target_price_list = sorted(target_price_list, key=lambda x: x[2], reverse=True)

    return target_price_list[:x]


def calculate_predict_close_price(market_code: str) -> float:
    """Prophet모델 기반 종가 예측

    Args:
        market_code (str): 특정 코인의 마켓코드 (KRW-BTC..)

    Returns:
        float: 종가
    """
    predicted_close_price = 0
    # 60분 데이터 불러오기
    df = pyupbit.get_ohlcv(market_code, interval="minute60")

    # 데이터 정리
    df = df.reset_index()
    df["ds"] = df["index"]
    df["y"] = df["close"]
    data = df[["ds", "y"]]

    # 모델 객체 생성 및 학습
    prophet_model = Prophet()
    prophet_model.fit(data)

    # 24시간 이후를 예측
    future = prophet_model.make_future_dataframe(periods=24, freq="H")
    forecast = prophet_model.predict(future)

    # 최종 가격 추출
    closeDf = forecast[forecast["ds"] == forecast.iloc[-1]["ds"].replace(hour=9)]
    if len(closeDf) == 0:
        closeDf = forecast[forecast["ds"] == data.iloc[-1]["ds"].replace(hour=9)]
    closeValue = closeDf["yhat"].values[0]
    predicted_close_price = closeValue

    return predicted_close_price
