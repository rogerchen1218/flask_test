from flask import Flask, render_template, request, redirect
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

host = os.getenv('MYSQL_HOST')
user = os.getenv('MYSQL_USER')
password = os.getenv('MYSQL_PASSWORD')
database = os.getenv('MYSQL_DB')

# MySQL 資料庫配置
db_settings = {
    "host": host,
    "port": 3306,
    "user": user,
    "password": password,
    "db": database,
    "charset": "utf8"
}
conn = pymysql.connect(**db_settings)
cursor = conn.cursor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inventory')
def inventory():
    return render_template('inventory.html')

@app.route('/incoming', methods=['GET', 'POST'])
def incoming():
    if request.method == 'POST':
        commodity = request.form['commodity']
        quantity = request.form['quantity']
        price = request.form['price']
        spec = request.form['spec']
        supplier = request.form['supplier']
        date = request.form['date']
        storage = request.form['storage']
        ps = request.form['ps']

        cursor.execute(
            "INSERT INTO purchase (commodity, quantity, price, spec, supplier, date, storage, ps) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (commodity, quantity, price, spec, supplier, date, storage, ps)
        )
        conn.commit()
        return redirect('/incoming')
    return render_template('incoming.html')

@app.route('/outgoing', methods=['GET', 'POST'])
def outgoing():
    if request.method == 'POST':
        commodity_sale = request.form['commodity_sale']
        quantity_sale = request.form['quantity_sale']
        price_sale = request.form['price_sale']
        spec_sale = request.form['spec_sale']
        storage_sale = request.form['storage_sale']
        reserve_sale = request.form['reserve_sale']
        buyer = request.form['buyer']

        cursor.execute(
            "INSERT INTO sales (commodity_sale, quantity_sale, price_sale, spec_sale, storage_sale, reserve_sale, buyer) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (commodity_sale, quantity_sale, price_sale, spec_sale, storage_sale, reserve_sale, buyer)
        )
        conn.commit()
        return redirect('/outgoing')
    return render_template('outgoing.html')

@app.route('/stock')
def stock():
    # 接收篩選條件
    commodity = request.args.get('commodity', '')
    spec = request.args.get('spec', '')
    storage = request.args.get('storage', '')

    # SQL 查詢語句
    query = """
        SELECT p.commodity, p.spec, p.storage, 
               COALESCE(SUM(p.quantity), 0) - COALESCE(SUM(s.quantity_sale), 0) as total_quantity
        FROM purchase p
        LEFT JOIN sales s ON p.commodity = s.commodity_sale AND p.spec = s.spec_sale AND p.storage = s.storage_sale
        WHERE p.commodity LIKE %s AND p.spec LIKE %s AND p.storage LIKE %s
        GROUP BY p.commodity, p.spec, p.storage
    """

    # 使用通配符進行模糊搜尋
    search_commodity = f"%{commodity}%"
    search_spec = f"%{spec}%"
    search_storage = f"%{storage}%"

    cursor.execute(query, (search_commodity, search_spec, search_storage))
    stock_records = cursor.fetchall()

    return render_template('stock.html', stock_records=stock_records)



@app.route('/reservation')
def reservation():
    cursor.execute("SELECT * FROM sales WHERE reserve_sale = '是'")
    reservation_records = cursor.fetchall()
    return render_template('reservation.html', reservation_records=reservation_records)

if __name__ == '__main__':
    app.run(debug=True)
