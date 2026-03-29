# app.py - نظام سوبر ماركت متكامل
from flask import Flask, render_template_string, request, redirect, session, jsonify, send_file
from datetime import datetime
import json
import os
import hashlib
import io

app = Flask(__name__)
app.secret_key = 'super-secret-key-2024'

DATA_FILE = 'supermarket_data.json'

# ============ دوال البيانات ============
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'users': [
            {'username': 'admin', 'password': hashlib.md5(b'admin123').hexdigest(), 'role': 'admin', 'name': 'المدير'},
            {'username': 'cashier', 'password': hashlib.md5(b'cashier123').hexdigest(), 'role': 'cashier', 'name': 'الكاشير'}
        ],
        'products': [
            {'id': 1, 'barcode': '111', 'name': 'ماء 1.5لتر', 'price': 2.5, 'cost': 1.5, 'quantity': 50},
            {'id': 2, 'barcode': '222', 'name': 'بسكويت', 'price': 3, 'cost': 2, 'quantity': 30},
            {'id': 3, 'barcode': '333', 'name': 'عصير تفاح', 'price': 4, 'cost': 2.5, 'quantity': 25},
            {'id': 4, 'barcode': '444', 'name': 'حليب', 'price': 5, 'cost': 3.5, 'quantity': 40},
            {'id': 5, 'barcode': '555', 'name': 'شوكولاتة', 'price': 2, 'cost': 1.2, 'quantity': 60}
        ],
        'sales': [],
        'expenses': []
    }

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ============ قالب رئيسي ============
TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
    <title>{{ title }} - سوبر ماركت</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:#f0f2f5;padding:10px;font-family:'Segoe UI',Tahoma}
        .header{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;padding:12px;border-radius:12px;margin-bottom:10px}
        .user-bar{display:flex;justify-content:space-between;align-items:center;margin-top:8px}
        .logout-btn{background:rgba(255,255,255,0.2);padding:5px 12px;border-radius:20px;color:#fff;text-decoration:none;font-size:12px}
        .menu{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:10px}
        .menu a{background:#fff;padding:8px;border-radius:8px;text-decoration:none;color:#333;font-size:12px;flex:1;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,0.1)}
        .card{background:#fff;padding:12px;border-radius:12px;margin-bottom:10px;box-shadow:0 1px 3px rgba(0,0,0,0.1)}
        .card h3{color:#667eea;margin-bottom:10px;font-size:14px;border-right:3px solid #667eea;padding-right:8px}
        input,select,textarea,button{width:100%;padding:10px;margin:5px 0;border:1px solid #ddd;border-radius:8px;font-size:14px}
        button{background:#27ae60;color:#fff;border:none;cursor:pointer;font-weight:bold}
        button:hover{opacity:0.9}
        .btn-danger{background:#e74c3c}
        .btn-warning{background:#f39c12}
        .btn-info{background:#3498db}
        table{width:100%;border-collapse:collapse;font-size:12px}
        th,td{padding:8px;border-bottom:1px solid #eee;text-align:center}
        th{background:#667eea;color:#fff}
        .total{font-size:20px;font-weight:bold;text-align:center;padding:10px;background:#f8f9fa;border-radius:8px;margin:10px 0}
        .product-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(100px,1fr));gap:8px;max-height:300px;overflow-y:auto}
        .product-btn{background:#f8f9fa;padding:8px;border-radius:8px;text-align:center;font-size:11px;cursor:pointer;border:1px solid #e0e0e0}
        .product-btn:active{background:#e0e0e0}
        .cart-item{display:flex;justify-content:space-between;align-items:center;padding:8px;border-bottom:1px solid #eee;font-size:12px;gap:5px;flex-wrap:wrap}
        .cart-item span{flex:1}
        .stats{display:flex;gap:10px;margin-bottom:10px}
        .stat{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;padding:10px;border-radius:10px;flex:1;text-align:center}
        .stat-num{font-size:22px;font-weight:bold}
        .low-stock{color:#e74c3c;font-weight:bold}
        .in-stock{color:#27ae60}
        .print-btn{background:#3498db;margin-top:10px}
        @media (max-width:600px){
            .cart-item{font-size:11px}
            .product-btn{font-size:10px}
            .stat-num{font-size:18px}
        }
    </style>
</head>
<body>
    {% if user %}
    <div class="header">
        <div>🏪 نظام السوبر ماركت</div>
        <div class="user-bar">
            <span>👤 {{ user.name }} ({{ 'مدير' if user.role=='admin' else 'كاشير' }})</span>
            <span>📅 {{ now }}</span>
            <a href="/logout" class="logout-btn">🚪 خروج</a>
        </div>
    </div>
    <div class="menu">
        <a href="/">🏠 الرئيسية</a>
        <a href="/pos">💰 نقطة البيع</a>
        <a href="/products">📦 المخزن</a>
        <a href="/reports">📊 التقارير</a>
        {% if user.role == 'admin' %}
        <a href="/expenses">💸 المصروفات</a>
        <a href="/users">👥 المستخدمين</a>
        <a href="/backup">💾 نسخ احتياطي</a>
        {% endif %}
    </div>
    {% endif %}
    {{ content|safe }}
</body>
</html>
'''

def render_page(content, title="الرئيسية"):
    return render_template_string(TEMPLATE, user=session.get('user'), content=content, title=title, now=datetime.now().strftime('%H:%M'))

# ============ صفحة تسجيل الدخول ============
LOGIN_PAGE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تسجيل الدخول</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}
        .login-box{background:#fff;padding:30px;border-radius:20px;width:100%;max-width:350px;text-align:center}
        h2{color:#667eea;margin-bottom:20px}
        input{width:100%;padding:12px;margin:8px 0;border:1px solid #ddd;border-radius:10px}
        button{width:100%;padding:12px;background:#667eea;color:#fff;border:none;border-radius:10px;margin-top:10px}
        .info{margin-top:15px;color:#666;font-size:12px}
        .error{color:red;margin-top:10px}
    </style>
</head>
<body>
    <div class="login-box">
        <h2>🏪 نظام السوبر ماركت</h2>
        <form method="post">
            <input type="text" name="username" placeholder="اسم المستخدم" required>
            <input type="password" name="password" placeholder="كلمة المرور" required>
            <button type="submit">تسجيل الدخول</button>
        </form>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        <div class="info">👤 admin / admin123 | 👤 cashier / cashier123</div>
    </div>
</body>
</html>
'''

# ============ الصفحة الرئيسية ============
@app.route('/')
def home():
    if 'user' not in session:
        return redirect('/login')
    data = load_data()
    today = datetime.now().strftime('%Y-%m-%d')
    today_sales = sum(s['total'] for s in data['sales'] if s['date'].startswith(today))
    low_stock = [p for p in data['products'] if p['quantity'] < 10]
    total_products = len(data['products'])
    total_sales = sum(s['total'] for s in data['sales'])
    
    low_html = ""
    for p in low_stock[:5]:
        low_html += f'<div style="padding:5px; border-bottom:1px solid #eee">⚠️ {p["name"]}: {p["quantity"]} وحدة</div>'
    if low_html == "":
        low_html = '<div>✅ جميع المنتجات متوفرة</div>'
    
    content = f'''
    <div class="stats">
        <div class="stat"><div class="stat-num">{today_sales:.1f}</div>مبيعات اليوم</div>
        <div class="stat"><div class="stat-num">{len(low_stock)}</div>منتجات منخفضة</div>
        <div class="stat"><div class="stat-num">{total_products}</div>إجمالي المنتجات</div>
    </div>
    <div class="card">
        <h3>⚠️ تنبيهات المخزون المنخفض</h3>
        {low_html}
    </div>
    <div class="card">
        <h3>📊 إحصائيات سريعة</h3>
        <p>💰 إجمالي المبيعات الكلي: {total_sales:.2f} ريال</p>
        <p>📈 عدد الفواتير: {len(data["sales"])}</p>
        <p>📦 إجمالي المنتجات: {total_products}</p>
    </div>
    '''
    return render_page(content)

# ============ تسجيل الدخول ============
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = load_data()
        pwd = hashlib.md5(request.form['password'].encode()).hexdigest()
        for u in data['users']:
            if u['username'] == request.form['username'] and u['password'] == pwd:
                session['user'] = u
                return redirect('/')
        return render_template_string(LOGIN_PAGE, error='بيانات غير صحيحة')
    return render_template_string(LOGIN_PAGE, error=None)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ============ نقطة البيع (مطورة) ============
@app.route('/pos', methods=['GET', 'POST'])
def pos():
    if 'user' not in session:
        return redirect('/login')
    
    data = load_data()
    cart = session.get('cart', {})
    total = sum(item['price'] * item['qty'] for item in cart.values())
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            barcode = request.form.get('barcode')
            for p in data['products']:
                if p['barcode'] == barcode:
                    if p['quantity'] <= 0:
                        return jsonify({'ok': False, 'msg': 'المنتج غير متوفر'})
                    if barcode in cart:
                        cart[barcode]['qty'] += 1
                    else:
                        cart[barcode] = {'id': p['id'], 'name': p['name'], 'price': p['price'], 'qty': 1}
                    session['cart'] = cart
                    return jsonify({'ok': True, 'total': sum(i['price'] * i['qty'] for i in cart.values())})
            return jsonify({'ok': False, 'msg': 'منتج غير موجود'})
        
        elif action == 'update':
            barcode = request.form.get('barcode')
            qty = int(request.form.get('qty', 1))
            if barcode in cart and qty > 0:
                cart[barcode]['qty'] = qty
                session['cart'] = cart
            return jsonify({'ok': True})
        
        elif action == 'remove':
            barcode = request.form.get('barcode')
            if barcode in cart:
                del cart[barcode]
                session['cart'] = cart
            return jsonify({'ok': True})
        
        elif action == 'checkout':
            paid = float(request.form.get('paid', 0))
            customer = request.form.get('customer', '')
            if paid >= total:
                # إنشاء الفاتورة
                invoice_id = len(data['sales']) + 1
                invoice = {
                    'id': invoice_id,
                    'number': f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'user': session['user']['username'],
                    'customer': customer,
                    'items': cart.copy(),
                    'total': total,
                    'paid': paid,
                    'change': paid - total
                }
                data['sales'].append(invoice)
                
                # تحديث المخزون
                for barcode, item in cart.items():
                    for p in data['products']:
                        if p['barcode'] == barcode:
                            p['quantity'] -= item['qty']
                
                save_data(data)
                session['cart'] = {}
                
                # حفظ الفاتورة كملف نصي للطباعة
                invoice_text = generate_invoice_text(invoice)
                with open(f'invoice_{invoice["number"]}.txt', 'w', encoding='utf-8') as f:
                    f.write(invoice_text)
                
                return jsonify({'ok': True, 'change': paid - total, 'invoice_id': invoice_id, 'invoice_number': invoice['number']})
            return jsonify({'ok': False, 'msg': 'المبلغ غير كاف'})
    
    # عرض المنتجات
    products_html = ""
    for p in data['products']:
        stock_class = 'low-stock' if p['quantity'] < 10 else 'in-stock'
        products_html += f'''
        <button class="product-btn" onclick="addProduct('{p['barcode']}')">
            <strong>{p['name'][:15]}</strong><br>
            <span style="color:#27ae60">{p['price']} ريال</span><br>
            <span class="{stock_class}">المتبقي: {p['quantity']}</span>
        </button>
        '''
    
    # عرض السلة
    cart_html = ""
    for b, i in cart.items():
        cart_html += f'''
        <div class="cart-item">
            <span style="flex:2">{i['name']}</span>
            <span>{i['price']}</span>
            <span><input type="number" value="{i['qty']}" min="1" style="width:50px;padding:5px" onchange="updateQty('{b}', this.value)"></span>
            <span>{i['price'] * i['qty']:.2f}</span>
            <button onclick="removeItem('{b}')" style="width:40px;background:#e74c3c">✖</button>
        </div>
        '''
    
    if cart_html == "":
        cart_html = '<div style="text-align:center;padding:20px">🛒 السلة فارغة</div>'
    
    content = f'''
    <div class="card">
        <h3>🔍 مسح الباركود</h3>
        <input type="text" id="barcode" placeholder="امسح الباركود أو اكتبه" autofocus>
    </div>
    
    <div class="card">
        <h3>🛒 سلة المشتريات</h3>
        <div class="cart-item" style="background:#667eea;color:#fff;font-weight:bold">
            <span style="flex:2">المنتج</span><span>السعر</span><span>الكمية</span><span>الإجمالي</span><span></span>
        </div>
        <div id="cartItems">{cart_html}</div>
        <div class="total">الإجمالي: {total:.2f} ريال</div>
    </div>
    
    <div class="card">
        <h3>💳 إتمام البيع</h3>
        <input type="text" id="customer" placeholder="اسم العميل (اختياري)">
        <input type="number" id="paid" placeholder="المبلغ المدفوع">
        <button onclick="checkout()">💰 إنهاء الفاتورة</button>
        <div id="result" style="margin-top:10px;text-align:center"></div>
    </div>
    
    <div class="card">
        <h3>📦 المنتجات</h3>
        <input type="text" id="search" placeholder="بحث بالاسم أو الباركود..." style="margin-bottom:8px">
        <div class="product-grid" id="productsGrid">
            {products_html}
        </div>
    </div>
    
    <script>
        function addProduct(barcode) {{
            fetch('/pos', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
                body: 'action=add&barcode=' + barcode
            }})
            .then(r => r.json())
            .then(d => {{
                if(d.ok) location.reload();
                else alert(d.msg);
            }});
        }}
        
        function updateQty(barcode, qty) {{
            fetch('/pos', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
                body: 'action=update&barcode=' + barcode + '&qty=' + qty
            }})
            .then(() => location.reload());
        }}
        
        function removeItem(barcode) {{
            fetch('/pos', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
                body: 'action=remove&barcode=' + barcode
            }})
            .then(() => location.reload());
        }}
        
        function checkout() {{
            let paid = document.getElementById('paid').value;
            let customer = document.getElementById('customer').value;
            if(!paid) {{ alert('أدخل المبلغ المدفوع'); return; }}
            
            fetch('/pos', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
                body: 'action=checkout&paid=' + paid + '&customer=' + customer
            }})
            .then(r => r.json())
            .then(d => {{
                if(d.ok) {{
                    let msg = '✅ تمت الفاتورة بنجاح!\\nرقم الفاتورة: ' + d.invoice_number + '\\nالباقي: ' + d.change + ' ريال';
                    alert(msg);
                    document.getElementById('result').innerHTML = '<div style="background:#27ae60;color:#fff;padding:10px;border-radius:8px">' + msg.replace(/\\n/g,'<br>') + '</div>';
                    location.reload();
                }} else alert(d.msg);
            }});
        }}
        
        document.getElementById('barcode').addEventListener('keypress', function(e) {{
            if(e.key === 'Enter') {{
                addProduct(this.value);
                this.value = '';
            }}
        }});
        
        document.getElementById('search').addEventListener('input', function() {{
            let search = this.value.toLowerCase();
            document.querySelectorAll('.product-btn').forEach(btn => {{
                let text = btn.innerText.toLowerCase();
                btn.style.display = text.includes(search) ? '' : 'none';
            }});
        }});
    </script>
    '''
    return render_page(content, "نقطة البيع")

def generate_invoice_text(invoice):
    """توليد نص الفاتورة للطباعة"""
    text = "=" * 40 + "\n"
    text += "         سوبر ماركت\n"
    text += "=" * 40 + "\n"
    text += f"رقم الفاتورة: {invoice['number']}\n"
    text += f"التاريخ: {invoice['date']}\n"
    text += f"الكاشير: {invoice['user']}\n"
    if invoice['customer']:
        text += f"العميل: {invoice['customer']}\n"
    text += "-" * 40 + "\n"
    text += f"{'المنتج':<20} {'الكمية':<8} {'السعر':<8} {'الإجمالي':<8}\n"
    text += "-" * 40 + "\n"
    for item in invoice['items'].values():
        text += f"{item['name'][:18]:<20} {item['qty']:<8} {item['price']:<8} {item['price']*item['qty']:<8.2f}\n"
    text += "-" * 40 + "\n"
    text += f"{'الإجمالي':<36} {invoice['total']:.2f}\n"
    text += f"{'المدفوع':<36} {invoice['paid']:.2f}\n"
    text += f"{'الباقي':<36} {invoice['change']:.2f}\n"
    text += "=" * 40 + "\n"
    text += "     شكراً لزيارتكم\n"
    text += "=" * 40
    return text

# ============ المخزن وإدارة المنتجات ============
@app.route('/products', methods=['GET', 'POST'])
def products():
    if 'user' not in session:
        return redirect('/login')
    
    data = load_data()
    
    if request.method == 'POST' and session['user']['role'] == 'admin':
        new_id = max([p['id'] for p in data['products']] + [0]) + 1
        new_product = {
            'id': new_id,
            'barcode': request.form.get('barcode'),
            'name': request.form.get('name'),
            'price': float(request.form.get('price', 0)),
            'cost': float(request.form.get('cost', 0)),
            'quantity': int(request.form.get('quantity', 0))
        }
        data['products'].append(new_product)
        save_data(data)
        return redirect('/products')
    
    # حذف منتج
    delete_id = request.args.get('delete')
    if delete_id and session['user']['role'] == 'admin':
        data['products'] = [p for p in data['products'] if p['id'] != int(delete_id)]
        save_data(data)
        return redirect('/products')
    
    add_form = ""
    if session['user']['role'] == 'admin':
        add_form = '''
        <div class="card">
            <h3>➕ إضافة منتج جديد</h3>
            <form method="post">
                <input name="barcode" placeholder="الباركود" required>
                <input name="name" placeholder="اسم المنتج" required>
                <input name="price" placeholder="سعر البيع" step="0.01" required>
                <input name="cost" placeholder="سعر الشراء" step="0.01" required>
                <input name="quantity" placeholder="الكمية" value="0">
                <button>➕ إضافة المنتج</button>
            </form>
        </div>
        '''
    
    products_html = ""
    for p in data['products']:
        color = 'red' if p['quantity'] < 10 else 'green'
        delete_btn = ''
        if session['user']['role'] == 'admin':
            delete_btn = f'<td><a href="/products?delete={p["id"]}" onclick="return confirm(\'هل تريد حذف {p["name"]}؟\')" style="color:#e74c3c">🗑️</a></td>'
        products_html += f'''
        <tr>
            <td>{p['barcode']}</td>
            <td>{p['name']}</td>
            <td>{p['price']:.2f}</td>
            <td style="color:{color};font-weight:bold">{p['quantity']}</td>
            <td>{'⚠️ منخفض' if p['quantity'] < 10 else '✅ متوفر'}</td>
            {delete_btn}
        </tr>
        '''
    
    if products_html == "":
        products_html = '<tr><td colspan="5">لا توجد منتجات</td></tr>'
    
    content = add_form + f'''
    <div class="card">
        <h3>📦 المخزن - إدارة المنتجات</h3>
        <input type="text" id="search" placeholder="🔍 بحث بالباركود أو الاسم..." style="margin-bottom:8px">
        <div style="overflow-x:auto">
            <table>
                <thead>
                    <tr><th>الباركود</th><th>الاسم</th><th>السعر</th><th>الكمية</th><th>الحالة</th>{'<th></th>' if session["user"]["role"]=="admin" else ''}</tr>
                </thead>
                <tbody id="productsTable">
                    {products_html}
                </tbody>
            </table>
        </div>
    </div>
    <script>
        document.getElementById('search').addEventListener('input', function() {{
            let s = this.value.toLowerCase();
            document.querySelectorAll('#productsTable tr').forEach(row => {{
                let text = row.innerText.toLowerCase();
                row.style.display = text.includes(s) ? '' : 'none';
            }});
        }});
    </script>
    '''
    return render_page(content, "المخزن")

# ============ المصروفات ============
@app.route('/expenses', methods=['GET', 'POST'])
def expenses():
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect('/')
    
    data = load_data()
    
    if request.method == 'POST':
        new_expense = {
            'id': len(data['expenses']) + 1,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'desc': request.form.get('desc'),
            'amount': float(request.form.get('amount', 0)),
            'user': session['user']['username']
        }
        data['expenses'].append(new_expense)
        save_data(data)
        return redirect('/expenses')
    
    expenses_html = ""
    for e in reversed(data['expenses'][-20:]):
        expenses_html += f'<tr><td>{e["date"]}</td><td>{e["desc"]}</td><td style="color:red">{e["amount"]:.2f}</td><td>{e["user"]}</td></tr>'
    
    if expenses_html == "":
        expenses_html = '<tr><td colspan="4">لا توجد مصروفات</td></tr>'
    
    content = f'''
    <div class="card">
        <h3>➕ إضافة مصروف جديد</h3>
        <form method="post">
            <input name="desc" placeholder="الوصف" required>
            <input name="amount" placeholder="المبلغ" step="0.01" required>
            <button>➕ إضافة المصروف</button>
        </form>
    </div>
    
    <div class="card">
        <h3>💸 سجل المصروفات</h3>
        <div style="overflow-x:auto">
            <table>
                <thead><tr><th>التاريخ</th><th>الوصف</th><th>المبلغ</th><th>بواسطة</th></tr></thead>
                <tbody>{expenses_html}</tbody>
            </table>
        </div>
    </div>
    '''
    return render_page(content, "المصروفات")

# ============ التقارير المتقدمة ============
@app.route('/reports')
def reports():
    if 'user' not in session:
        return redirect('/login')
    
    data = load_data()
    
    # حساب الأرباح والخسائر
    total_sales = sum(s['total'] for s in data['sales'])
    total_expenses = sum(e['amount'] for e in data['expenses'])
    
    # حساب تكلفة المبيعات
    cost_of_sales = 0
    for sale in data['sales']:
        for item in sale['items'].values():
            for p in data['products']:
                if p['name'] == item['name']:
                    cost_of_sales += p['cost'] * item['qty']
                    break
    
    gross_profit = total_sales - cost_of_sales
    net_profit = gross_profit - total_expenses
    
    # مبيعات اليوم
    today = datetime.now().strftime('%Y-%m-%d')
    today_sales = [s for s in data['sales'] if s['date'].startswith(today)]
    today_total = sum(s['total'] for s in today_sales)
    
    # أفضل المنتجات مبيعاً
    product_sales = {}
    for sale in data['sales']:
        for item in sale['items'].values():
            if item['name'] not in product_sales:
                product_sales[item['name']] = {'qty': 0, 'total': 0}
            product_sales[item['name']]['qty'] += item['qty']
            product_sales[item['name']]['total'] += item['price'] * item['qty']
    
    top_products = sorted(product_sales.items(), key=lambda x: x[1]['qty'], reverse=True)[:5]
    
    top_html = ""
    for name, data in top_products:
        top_html += f'<div style="display:flex;justify-content:space-between;padding:8px;border-bottom:1px solid #eee"><span>{name}</span><span>{data["qty"]} وحدة</span><span>{data["total"]:.2f} ريال</span></div>'
    
    # آخر الفواتير
    invoices_html = ""
    for s in reversed(data['sales'][-10:]):
        invoices_html += f'''
        <tr>
            <td>{s['number']}</td>
            <td>{s['date'][:16]}</td>
            <td>{s['user']}</td>
            <td>{s['customer'] or '-'}</td>
            <td>{s['total']:.2f}</td>
            <td><a href="/print_invoice/{s['id']}" target="_blank" style="color:#3498db">🖨️</a></td>
        </tr>
        '''
    
    if invoices_html == "":
        invoices_html = '<tr><td colspan="6">لا توجد فواتير</td></tr>'
    
    content = f'''
    <div class="stats">
        <div class="stat" style="background:#27ae60"><div class="stat-num">{total_sales:.2f}</div>إجمالي المبيعات</div>
        <div class="stat" style="background:#e74c3c"><div class="stat-num">{total_expenses:.2f}</div>إجمالي المصروفات</div>
    </div>
    <div class="stats">
        <div class="stat" style="background:#3498db"><div class="stat-num">{cost_of_sales:.2f}</div>تكلفة المبيعات</div>
        <div class="stat" style="background:#f39c12"><div class="stat-num">{gross_profit:.2f}</div>الربح الإجمالي</div>
    </div>
    <div class="card" style="background:linear-gradient(135deg,#667eea,#764ba2);color:#fff">
        <div style="font-size:28px;font-weight:bold;text-align:center">{net_profit:.2f} ريال</div>
        <div style="text-align:center">صافي الربح (المبيعات - التكلفة - المصروفات)</div>
    </div>
    
    <div class="card">
        <h3>📊 إحصائيات اليوم</h3>
        <p>📅 مبيعات اليوم: {len(today_sales)} فاتورة</p>
        <p>💰 قيمة مبيعات اليوم: {today_total:.2f} ريال</p>
    </div>
    
    <div class="card">
        <h3>🏆 أفضل المنتجات مبيعاً</h3>
        {top_html or '<div>لا توجد مبيعات بعد</div>'}
    </div>
    
    <div class="card">
        <h3>📋 آخر الفواتير</h3>
        <div style="overflow-x:auto">
            <table>
                <thead><tr><th>رقم الفاتورة</th><th>التاريخ</th><th>الكاشير</th><th>العميل</th><th>الإجمالي</th><th></th></tr></thead>
                <tbody>{invoices_html}</tbody>
            </table>
        </div>
    </div>
    '''
    return render_page(content, "التقارير")

# ============ طباعة الفاتورة ============
@app.route('/print_invoice/<int:invoice_id>')
def print_invoice(invoice_id):
    data = load_data()
    invoice = None
    for s in data['sales']:
        if s['id'] == invoice_id:
            invoice = s
            break
    
    if not invoice:
        return "الفاتورة غير موجودة"
    
    text = generate_invoice_text(invoice)
    return f'<pre style="font-family:monospace;direction:ltr;text-align:left;background:#fff;padding:20px">{text}</pre><br><button onclick="window.print()" style="width:200px">🖨️ طباعة</button>'

# ============ المستخدمين ============
@app.route('/users', methods=['GET', 'POST'])
def users():
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect('/')
    
    data = load_data()
    
    if request.method == 'POST':
        new_user = {
            'username': request.form.get('username'),
            'password': hashlib.md5(request.form.get('password').encode()).hexdigest(),
            'role': request.form.get('role', 'cashier'),
            'name': request.form.get('name', request.form.get('username'))
        }
        data['users'].append(new_user)
        save_data(data)
        return redirect('/users')
    
    # حذف مستخدم
    delete_user = request.args.get('delete')
    if delete_user:
        data['users'] = [u for u in data['users'] if u['username'] != delete_user]
        save_data(data)
        return redirect('/users')
    
    users_html = ""
    for u in data['users']:
        if u['username'] != session['user']['username']:
            users_html += f'''
            <div class="cart-item">
                <span style="flex:2"><strong>{u['username']}</strong><br><small>{u['name']}</small></span>
                <span>{'مدير' if u['role'] == 'admin' else 'كاشير'}</span>
                <span><a href="/users?delete={u['username']}" onclick="return confirm('حذف المستخدم؟')" style="color:#e74c3c">حذف</a></span>
            </div>
            '''
    
    content = f'''
    <div class="card">
        <h3>➕ إضافة مستخدم جديد</h3>
        <form method="post">
            <input name="username" placeholder="اسم المستخدم" required>
            <input type="password" name="password" placeholder="كلمة المرور" required>
            <input name="name" placeholder="الاسم الكامل">
            <select name="role">
                <option value="cashier">كاشير</option>
                <option value="admin">مدير</option>
            </select>
            <button>➕ إضافة مستخدم</button>
        </form>
    </div>
    
    <div class="card">
        <h3>👥 قائمة المستخدمين</h3>
        <div class="cart-item" style="background:#667eea;color:#fff">
            <span style="flex:2">المستخدم</span><span>الدور</span><span></span>
        </div>
        {users_html or '<div style="text-align:center;padding:20px">لا يوجد مستخدمين آخرين</div>'}
    </div>
    '''
    return render_page(content, "المستخدمين")

# ============ النسخ الاحتياطي ============
@app.route('/backup')
def backup():
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect('/')
    
    import shutil
    backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    shutil.copy(DATA_FILE, backup_name)
    
    backups = []
    for f in os.listdir('.'):
        if f.startswith('backup_') and f.endswith('.json'):
            backups.append(f)
    backups.sort(reverse=True)
    
    backups_html = ""
    for b in backups[:10]:
        backups_html += f'''
        <div class="cart-item">
            <span>{b}</span>
            <span><a href="/restore/{b}" onclick="return confirm('استعادة النسخة؟')" style="color:#27ae60">استعادة</a></span>
            <span><a href="/download/{b}" style="color:#3498db">تحميل</a></span>
        </div>
        '''
    
    content = f'''
    <div class="card">
        <h3>💾 إنشاء نسخة احتياطية</h3>
        <a href="/backup"><button>📀 إنشاء نسخة جديدة</button></a>
    </div>
    
    <div class="card">
        <h3>📀 النسخ المتاحة</h3>
        <div class="cart-item" style="background:#667eea;color:#fff">
            <span>اسم الملف</span><span></span><span></span>
        </div>
        {backups_html or '<div style="text-align:center;padding:20px">لا توجد نسخ احتياطية</div>'}
    </div>
    '''
    return render_page(content, "النسخ الاحتياطي")

@app.route('/restore/<filename>')
def restore(filename):
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect('/')
    
    import shutil
    if os.path.exists(filename):
        shutil.copy(filename, DATA_FILE)
        return '<script>alert("تمت الاستعادة بنجاح");window.location="/backup"</script>'
    return redirect('/backup')

@app.route('/download/<filename>')
def download(filename):
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect('/')
    
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    print("=" * 50)
    print("🏪 نظام السوبر ماركت - النسخة المتكاملة")
    print("=" * 50)
    print("📱 افتح المتصفح على: http://localhost:8080")
    print("👤 admin / admin123  (مدير)")
    print("👤 cashier / cashier123  (كاشير)")
    print("=" * 50)
    app.run(host='0.0.0.0', port=8080, debug=False)