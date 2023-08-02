import pyupbit

# 계정 정보 불러오기
f = open("./account_information.txt")
lines = f.readlines()
access = lines[0].strip()
secret = lines[1].strip()
f.close()

# 로그인
my_upbit = pyupbit.Upbit(access=access, secret=secret)
