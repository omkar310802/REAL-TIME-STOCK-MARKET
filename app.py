from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'stockintel-secret-key-2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stockintel.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ─── Models ───────────────────────────────────────────────────────────────────

class User(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email    = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created  = db.Column(db.DateTime, default=datetime.utcnow)

class Portfolio(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ticker     = db.Column(db.String(20), nullable=False)
    company    = db.Column(db.String(100))
    quantity   = db.Column(db.Float, nullable=False)
    buy_price  = db.Column(db.Float, nullable=False)
    added_on   = db.Column(db.DateTime, default=datetime.utcnow)

class Alert(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ticker     = db.Column(db.String(20), nullable=False)
    target     = db.Column(db.Float, nullable=False)
    alert_type = db.Column(db.String(10), nullable=False)  # 'above' or 'below'
    triggered  = db.Column(db.Boolean, default=False)
    created    = db.Column(db.DateTime, default=datetime.utcnow)

# ─── Simulated Stock Data ─────────────────────────────────────────────────────

BASE_STOCKS = {
    'RELIANCE':   {'name': 'Reliance Industries', 'base': 2874.50, 'sector': 'Energy'},
    'TCS':        {'name': 'Tata Consultancy Services', 'base': 4012.75, 'sector': 'IT'},
    'INFY':       {'name': 'Infosys Ltd', 'base': 1892.40, 'sector': 'IT'},
    'HDFCBANK':   {'name': 'HDFC Bank Ltd', 'base': 1745.60, 'sector': 'Banking'},
    'ICICIBANK':  {'name': 'ICICI Bank Ltd', 'base': 1289.30, 'sector': 'Banking'},
    'BHARTIARTL': {'name': 'Bharti Airtel Ltd', 'base': 1634.20, 'sector': 'Telecom'},
    'WIPRO':      {'name': 'Wipro Ltd', 'base': 298.15, 'sector': 'IT'},
    'SBIN':       {'name': 'State Bank of India', 'base': 812.40, 'sector': 'Banking'},
    'HINDUNILVR': {'name': 'Hindustan Unilever', 'base': 2345.80, 'sector': 'FMCG'},
    'MARUTI':     {'name': 'Maruti Suzuki India', 'base': 12480.00, 'sector': 'Auto'},
    'BAJFINANCE': {'name': 'Bajaj Finance Ltd', 'base': 7123.50, 'sector': 'Finance'},
    'AXISBANK':   {'name': 'Axis Bank Ltd', 'base': 1178.90, 'sector': 'Banking'},
    'LT':         {'name': 'Larsen & Toubro', 'base': 3589.20, 'sector': 'Infrastructure'},
    'SUNPHARMA':  {'name': 'Sun Pharma Industries', 'base': 1654.30, 'sector': 'Pharma'},
    'TITAN':      {'name': 'Titan Company Ltd', 'base': 3421.60, 'sector': 'Consumer'},
}

def get_live_price(ticker):
    """Simulate live price with small random variation."""
    if ticker not in BASE_STOCKS:
        return None
    base = BASE_STOCKS[ticker]['base']
    variation = random.uniform(-0.03, 0.03)
    price = round(base * (1 + variation), 2)
    prev  = round(base, 2)
    chg   = round(price - prev, 2)
    pct   = round((chg / prev) * 100, 2)
    vol   = round(random.uniform(0.5, 10.0), 1)
    signal = 'BUY' if pct > 0.5 else ('SELL' if pct < -0.5 else 'HOLD')
    return {
        'ticker':  ticker,
        'name':    BASE_STOCKS[ticker]['name'],
        'sector':  BASE_STOCKS[ticker]['sector'],
        'price':   price,
        'prev':    prev,
        'change':  chg,
        'change_pct': pct,
        'volume':  f'{vol}M',
        'signal':  signal,
        'high':    round(price * 1.012, 2),
        'low':     round(price * 0.988, 2),
    }

def get_all_stocks():
    return [get_live_price(t) for t in BASE_STOCKS]

def generate_history(ticker, points=30):
    if ticker not in BASE_STOCKS:
        return []
    base = BASE_STOCKS[ticker]['base']
    prices, p = [], base * 0.92
    for _ in range(points):
        p += random.uniform(-base * 0.008, base * 0.01)
        prices.append(round(p, 2))
    prices[-1] = BASE_STOCKS[ticker]['base']
    return prices

# ─── Auth Routes ──────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email    = request.form['email'].strip()
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('register.html')
        user = User(username=username, email=email,
                    password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id']   = user.id
            session['username']  = user.username
            return redirect(url_for('dashboard'))
        flash('Invalid credentials.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ─── Main Dashboard ───────────────────────────────────────────────────────────

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

# ─── API Endpoints ────────────────────────────────────────────────────────────

@app.route('/api/stocks')
def api_stocks():
    return jsonify(get_all_stocks())

@app.route('/api/stock/<ticker>')
def api_stock(ticker):
    data = get_live_price(ticker.upper())
    if not data:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(data)

@app.route('/api/history/<ticker>')
def api_history(ticker):
    rng    = request.args.get('range', '1M')
    points = {'1D': 12, '1W': 7, '1M': 30, '3M': 90}.get(rng, 30)
    prices = generate_history(ticker.upper(), points)
    if rng == '1D':
        from datetime import datetime, timedelta
        base = datetime.now().replace(hour=9, minute=15, second=0)
        labels = [(base + timedelta(minutes=i*30)).strftime('%H:%M') for i in range(points)]
    elif rng == '1W':
        labels = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][:points]
    elif rng == '1M':
        labels = [f'{i+1} May' for i in range(points)]
    else:
        labels = [f'Week {i+1}' for i in range(points)]
    return jsonify({'labels': labels, 'prices': prices})

@app.route('/api/market_summary')
def api_market_summary():
    stocks  = get_all_stocks()
    gainers = [s for s in stocks if s['change'] > 0]
    losers  = [s for s in stocks if s['change'] < 0]
    sectors = {}
    for s in stocks:
        sec = s['sector']
        if sec not in sectors:
            sectors[sec] = []
        sectors[sec].append(s['change_pct'])
    sector_perf = {k: round(sum(v)/len(v), 2) for k, v in sectors.items()}
    return jsonify({
        'nifty':       {'value': 24783.45, 'change': 1.24},
        'sensex':      {'value': 81340.22, 'change': 0.91},
        'gainers':     len(gainers),
        'losers':      len(losers),
        'total':       len(stocks),
        'sector_perf': sector_perf,
    })

# ─── Portfolio API ────────────────────────────────────────────────────────────

@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    holdings = Portfolio.query.filter_by(user_id=session['user_id']).all()
    result = []
    for h in holdings:
        live = get_live_price(h.ticker)
        cur_price = live['price'] if live else h.buy_price
        pnl = (cur_price - h.buy_price) * h.quantity
        result.append({
            'id':         h.id,
            'ticker':     h.ticker,
            'company':    h.company,
            'quantity':   h.quantity,
            'buy_price':  h.buy_price,
            'cur_price':  cur_price,
            'pnl':        round(pnl, 2),
            'pnl_pct':    round((pnl / (h.buy_price * h.quantity)) * 100, 2),
            'invested':   round(h.buy_price * h.quantity, 2),
            'current':    round(cur_price * h.quantity, 2),
        })
    return jsonify(result)

@app.route('/api/portfolio', methods=['POST'])
def add_portfolio():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    data    = request.json
    ticker  = data.get('ticker', '').upper()
    qty     = float(data.get('quantity', 0))
    buy_p   = float(data.get('buy_price', 0))
    company = BASE_STOCKS.get(ticker, {}).get('name', ticker)
    if not ticker or qty <= 0 or buy_p <= 0:
        return jsonify({'error': 'Invalid data'}), 400
    h = Portfolio(user_id=session['user_id'], ticker=ticker, company=company,
                  quantity=qty, buy_price=buy_p)
    db.session.add(h)
    db.session.commit()
    return jsonify({'success': True, 'id': h.id})

@app.route('/api/portfolio/<int:hid>', methods=['DELETE'])
def delete_portfolio(hid):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    h = Portfolio.query.filter_by(id=hid, user_id=session['user_id']).first()
    if not h:
        return jsonify({'error': 'Not found'}), 404
    db.session.delete(h)
    db.session.commit()
    return jsonify({'success': True})

# ─── Alerts API ──────────────────────────────────────────────────────────────

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    alerts = Alert.query.filter_by(user_id=session['user_id']).all()
    result = []
    for a in alerts:
        live = get_live_price(a.ticker)
        cur  = live['price'] if live else 0
        triggered = (a.alert_type == 'above' and cur >= a.target) or \
                    (a.alert_type == 'below' and cur <= a.target)
        result.append({
            'id':         a.id,
            'ticker':     a.ticker,
            'target':     a.target,
            'alert_type': a.alert_type,
            'triggered':  triggered,
            'cur_price':  cur,
        })
    return jsonify(result)

@app.route('/api/alerts', methods=['POST'])
def add_alert():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    data   = request.json
    ticker = data.get('ticker', '').upper()
    target = float(data.get('target', 0))
    atype  = data.get('alert_type', 'above')
    if not ticker or target <= 0:
        return jsonify({'error': 'Invalid data'}), 400
    a = Alert(user_id=session['user_id'], ticker=ticker, target=target, alert_type=atype)
    db.session.add(a)
    db.session.commit()
    return jsonify({'success': True, 'id': a.id})

@app.route('/api/alerts/<int:aid>', methods=['DELETE'])
def delete_alert(aid):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    a = Alert.query.filter_by(id=aid, user_id=session['user_id']).first()
    if not a:
        return jsonify({'error': 'Not found'}), 404
    db.session.delete(a)
    db.session.commit()
    return jsonify({'success': True})

# ─── Init & Run ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)


