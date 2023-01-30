import firebase_admin

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
    point = []      # golden cross point
    point2 = []     # death cross point

    df_close = stock.get_market_ohlcv("20191004", "20230104", ticker)[['종가']]
    df_close.reset_index(inplace=True)

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

    flag = False
    for i in range(len(sum_20)):
        if sum_20[i] < sum_60[i]:
            if flag:
                point2.append(0)
                continue
            else:
                point2.append(1)
                flag = True
        else:
            point2.append(0)
            flag = False

    point2 = point2[60:]
    df_close = df_close[60:]

    df_close['지점2'] = point2
    df_close.reset_index(inplace=True, drop=True)
    del df_close['날짜']
    del df_close['종가']
    df_close.columns = ['point2']
    js = df_close.values.tolist()
    for i in range(len(js)):
        ref = db.reference('ticker/' + ticker).child(str(i))
        ref.update({'point2': js[i][0]})
