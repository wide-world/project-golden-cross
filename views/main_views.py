import firebase_admin

from firebase_admin import credentials
from firebase_admin import db
from flask import Blueprint, render_template
from pykrx import stock

# Firebase database 인증 및 앱 초기화
cred = credentials.Certificate('./mykey.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://golden-cross-d33e0-default-rtdb.firebaseio.com/'
})

bp = Blueprint('main', __name__, url_prefix='/')
ref = db.reference().child('ticker')  # db 위치 지정, 기본 가장 상단을 가르킴


@bp.route('/', methods=('GET',))
def index():
    return render_template('index.html')


@bp.route('/help')
def help_page():
    return render_template('help.html')


@bp.route('/design')
def design_page():
    return render_template('design.html')


@bp.route('/api/')
def all_data():
    t_list = stock.get_market_ticker_list()
    return t_list


@bp.route('/api/<string:ticker>/')
def stock_data(ticker):
    data = ref.child(ticker).get()
    return data


@bp.route("/<string:ticker>", methods=['GET'])
def chart(ticker):
    return render_template("chart.html", ticker=ticker)

