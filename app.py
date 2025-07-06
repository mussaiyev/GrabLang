from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, jsonify, send_file
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
import json
from datetime import datetime
import stripe
from functools import wraps
import requests

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Email config
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_DEFAULT_SENDER=os.getenv('MAIL_USERNAME')
)
mail = Mail(app)

# Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Telegram config
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Admin login
ADMIN_USERNAME = 'mussaiyev'
ADMIN_PASSWORD = 'musa2003Zz@'

def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapped

def send_admin_email(order):
    msg = Message("\U0001F4C4 Новый заказ перевода", recipients=[app.config['MAIL_USERNAME']])
    msg.body = f"""
Новый заказ от: {order['name']} <{order['email']}>

Языки: {order['source_lang']} → {order['target_lang']}
Страниц: {order['pages']}
Дополнения: {order['addons'] or 'Нет'}
Сумма: {order['total']}
Дата: {order['date']}
Файлы:
{chr(10).join([url_for('uploaded_file', filename=f, _external=True) for f in order['files']]) if order['files'] else 'Нет файлов'}
"""
    mail.send(msg)

def send_telegram_message(order):
    message = f"\U0001F4DD Новый заказ!\n" \
              f"Имя: {order['name']}\n" \
              f"Email: {order['email']}\n" \
              f"Языки: {order['source_lang']} → {order['target_lang']}\n" \
              f"Страниц: {order['pages']}\n" \
              f"Дополнения: {order['addons'] or 'Нет'}\n" \
              f"Сумма: {order['total']}\n" \
              f"Дата: {order['date']}"
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        })
    except Exception as e:
        print(f"Ошибка Telegram: {e}")

def send_user_email(order, subject="\u2705 Your Translation Order Confirmation", body=None):
    msg = Message(subject, recipients=[order['email']])
    if not body:
        body = f"""
Hi {order['name']},

Thank you for your order!

- Source Language: {order['source_lang']}
- Target Language: {order['target_lang']}
- Pages: {order['pages']}
- Add-ons: {order['addons'] or 'None'}
- Total: {order['total']}
- Date: {order['date']}

Files:
{chr(10).join([url_for('uploaded_file', filename=f, _external=True) for f in order['files']]) if order['files'] else 'No files'}

-- GrabLang Team
"""
    msg.body = body
    mail.send(msg)

@app.route('/')
def home():
    return render_template('main.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/options', methods=['GET', 'POST'])
def options():
    if request.method == 'POST':
        session['addons'] = request.form.get('addons', '')
        session['total'] = request.form.get('total', '')
        session['page_count'] = request.form.get('page_count', '')
        session['source_lang'] = request.form.get('source_lang', '')
        session['target_lang'] = request.form.get('target_lang', '')
        return redirect('/payment')
    return render_template('options.html')

@app.route('/payment')
def payment():
    return render_template('payment.html',
                           total=session.get('total', '0.00'),
                           pages=session.get('page_count', ''),
                           source_lang=session.get('source_lang', ''),
                           target_lang=session.get('target_lang', ''),
                           STRIPE_PUBLISHABLE_KEY=os.getenv('STRIPE_PUBLISHABLE_KEY'))

@app.route('/success')
def success():
    return render_template('thankyou.html')

@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('documents')
    saved = []
    for f in files:
        if f and f.filename:
            filename = datetime.now().strftime('%Y%m%d_%H%M%S_') + '_' + f.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f.save(filepath)
            saved.append(filename)
    session['uploaded_files'] = saved
    return {'status': 'ok', 'files': saved}

@app.route('/create-payment-intent', methods=['POST'])
def create_payment_intent():
    try:
        data = request.get_json()
        amount = int(float(data['amount']))
        intent = stripe.PaymentIntent.create(amount=amount, currency='usd')
        return jsonify({'clientSecret': intent.client_secret})
    except Exception as e:
        return jsonify(error=str(e)), 403

@app.route('/finalize-order', methods=['POST'])
def finalize_order():
    data = request.get_json()
    order = {
        "name": data.get('fullName'),
        "email": data.get('email'),
        "source_lang": data.get('sourceLang'),
        "target_lang": data.get('targetLang'),
        "pages": data.get('pageCount'),
        "addons": data.get('addons'),
        "total": data.get('total'),
        "date": datetime.now().strftime('%Y-%m-%d %H:%M'),
        "files": session.get('uploaded_files', [])
    }
    orders = []
    if os.path.exists('orders.json'):
        with open('orders.json', 'r', encoding='utf-8') as f:
            try:
                orders = json.load(f)
            except:
                orders = []
    orders.append(order)
    with open('orders.json', 'w', encoding='utf-8') as f:
        json.dump(orders, f, indent=2, ensure_ascii=False)
    send_admin_email(order)
    send_user_email(order)
    send_telegram_message(order)
    return jsonify({"status": "ok"})

@app.route('/admin')
@login_required
def admin_panel():
    orders = []
    if os.path.exists('orders.json'):
        with open('orders.json', 'r', encoding='utf-8') as f:
            try:
                orders = json.load(f)
            except:
                orders = []
    month = datetime.now().strftime('%Y-%m')
    monthly_count = sum(1 for o in orders if o.get('date', '').startswith(month))
    total_revenue = sum(
        float(o['total'].replace('$', '').strip())
        for o in orders
        if 'total' in o and o['total'].replace('$', '').replace('.', '').isdigit()
    )
    return render_template('admin.html', orders=orders, monthly_count=monthly_count,
                           total_revenue=total_revenue, total_orders=len(orders))

@app.route('/clear_orders', methods=['POST'])
@login_required
def clear_orders():
    with open('orders.json', 'w', encoding='utf-8') as f:
        json.dump([], f)
    return redirect('/admin')

@app.route('/delete_order/<int:index>', methods=['POST'])
@login_required
def delete_order(index):
    if os.path.exists('orders.json'):
        with open('orders.json', 'r', encoding='utf-8') as f:
            try:
                orders = json.load(f)
            except:
                orders = []
        if 0 <= index < len(orders):
            del orders[index]
            with open('orders.json', 'w', encoding='utf-8') as f:
                json.dump(orders, f, indent=2, ensure_ascii=False)
    return redirect('/admin')

@app.route('/resend_status/<int:index>', methods=['POST'])
@login_required
def resend_status_email(index):
    if os.path.exists('orders.json'):
        with open('orders.json', 'r', encoding='utf-8') as f:
            try:
                orders = json.load(f)
            except:
                orders = []
    if 0 <= index < len(orders):
        order = orders[index]
        subject = "\U0001F4E6 Статус заказа"
        body = f"""
Здравствуйте, {order['name']}!

Ваш заказ по переводу {order['source_lang']} → {order['target_lang']} в работе.

Скоро вы получите результат.

С уважением,
GrabLang
"""
        send_user_email(order, subject=subject, body=body)
    return redirect('/admin')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect('/admin')
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect('/login')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/sitemap.xml')
def sitemap():
    return send_file('sitemap.xml', mimetype='application/xml')

if __name__ == '__main__':
    app.run(debug=True)
