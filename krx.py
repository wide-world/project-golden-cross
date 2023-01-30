import firebase_admin
import pandas

from firebase_admin import credentials
from firebase_admin import db
from pykrx import stock


# Firebase database 인증 및 앱 초기화
cred = credentials.Certificate('./mykey.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://golden-cross-25558-default-rtdb.firebaseio.com/'
})

ref = db.reference()  # db 위치 지정, 기본 가장 상단을 가르킴

tickers = stock.get_market_ticker_list()
for ticker in tickers:
    ma_20 = []
    ma_60 = []
    sum_20 = []
    sum_60 = []
    point = []  # golden cross point

    stock_name = stock.get_market_ticker_name(ticker)
    df = stock.get_market_ohlcv("20191004", "20230104", ticker)[['시가', '고가', '저가', '종가', '거래량']]
    df_close = stock.get_market_ohlcv("20191004", "20230104", ticker)[['종가']]
    df.reset_index(inplace=True)

    # 이동 평균선 합 구하기
    for i, cp in enumerate(df_close['종가']):
        if i == 0:
            ma_20.append(cp)
            ma_60.append(cp)
        else:
            ma_20.append(cp + ma_20[i - 1])
            ma_60.append(cp + ma_60[i - 1])

    # 이동 평균선 구하기
    for i, val in enumerate(ma_20):
        sum_20.append((ma_20[i] - ma_20[i - 20]) // 20)

    for i, val in enumerate(ma_60):
        sum_60.append((ma_60[i] - ma_60[i - 60]) // 60)

    # 골든 크로스, 데드 크로스 지점 저장
    flag = False
    for i in range(len(sum_20)):
        if sum_20[i] > sum_60[i]:
            if flag:
                point.append(0)
                continue
            else:
                point.append(1)
                flag = True
        else:
            point.append(0)
            flag = False

    df_date = []
    for d in df['날짜']:
        df_date.append(pandas.to_datetime(d).value)
    del df['날짜']

    point = point[60:]
    sum_20 = sum_20[60:]
    sum_60 = sum_60[60:]
    df_date = df_date[60:]
    df = df[60:]

    df.insert(0, '날짜', df_date)
    df.insert(1, '20이평선', sum_20)
    df.insert(2, '60이평선', sum_60)
    df['지점'] = point
    df.reset_index(inplace=True, drop=True)

    df.columns = ['date', 'ma20', 'ma60', 'open', 'high', 'low', 'close', 'volume', 'point']
    js = df.to_dict(orient='index')

    ref = db.reference('ticker/' + ticker)
    ref.update({'id': ticker})
    ref.update({'name': stock_name})
    for i in range(len(js)):
        ref.update({i: js[i]})
