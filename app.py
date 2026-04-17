from flask import Flask, request, jsonify, render_template, render_template_string, redirect, url_for
import mysql.connector
from flask_cors import CORS
from datetime import datetime, date

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

GST_RATE = 12.0
UPLOADED_SQL_PATH = "/mnt/data/dbms.txt"   # your uploaded SQL file path

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",   # set your MySQL password if any
        database="PharmacyDB",
        autocommit=False
    )

# ------------------ Pages (multi-page) ------------------
@app.route("/")
def root(): return redirect(url_for('login_page'))

@app.route("/login", methods=["GET"])
def login_page():
    return render_template("base.html", page="login")

@app.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")

@app.route("/customers")
def customers_page():
    return render_template("customers.html")

@app.route("/employees")
def employees_page():
    return render_template("employees.html")

@app.route("/medicines")
def medicines_page():
    return render_template("medicines.html")

@app.route("/bills")
def bills_page():
    return render_template("bills.html")

@app.route("/create_bill")
def create_bill_page():
    return render_template("create_bill.html")

# ------------------ API: auth ------------------
@app.route("/api/login", methods=["POST"])
def api_login():
    d = request.json or {}
    user = d.get("username",""); pwd = d.get("password","")
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT emp_id, emp_name FROM Employee WHERE username=%s AND password=%s", (user,pwd))
    row = cur.fetchone()
    cur.close(); db.close()
    if row:
        return jsonify({"success": True, "emp_id": row["emp_id"], "emp_name": row["emp_name"]})
    return jsonify({"success": False, "error":"invalid credentials"}), 401

# ------------------ API: summary & alerts ------------------
@app.route("/api/summary")
def api_summary():
    db = get_db(); cur = db.cursor()
    cur.execute("SELECT COUNT(*) FROM Customer"); customers = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Employee"); employees = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Medicine"); medicines = cur.fetchone()[0]
    try:
        cur.execute("SELECT COUNT(*) FROM LowStockView"); low = cur.fetchone()[0]
    except:
        low = 0
    try:
        cur.execute("SELECT COUNT(*) FROM ExpiredMedicineView"); expired = cur.fetchone()[0]
    except:
        expired = 0
    try:
        cur.execute("SELECT COUNT(*) FROM ExpiringSoonView"); soon = cur.fetchone()[0]
    except:
        soon = 0
    cur.close(); db.close()
    return jsonify({"customers": customers, "employees": employees, "medicines": medicines, "low_stock": low, "expired": expired, "expiring_soon": soon})

@app.route("/api/lowstock")
def api_lowstock():
    db = get_db(); cur = db.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM LowStockView")
        rows = cur.fetchall()
        for r in rows:
            if r.get("expiry_date"): r["expiry_date"] = r["expiry_date"].strftime("%Y-%m-%d")
    except:
        rows = []
    cur.close(); db.close(); return jsonify(rows)

@app.route("/api/expired")
def api_expired():
    db = get_db(); cur = db.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM ExpiredMedicineView")
        rows = cur.fetchall()
        for r in rows:
            if r.get("expiry_date"): r["expiry_date"] = r["expiry_date"].strftime("%Y-%m-%d")
    except:
        rows = []
    cur.close(); db.close(); return jsonify(rows)

@app.route("/api/expiring_soon")
def api_expiring_soon():
    db = get_db(); cur = db.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM ExpiringSoonView")
        rows = cur.fetchall()
        for r in rows:
            if r.get("expiry_date"): r["expiry_date"] = r["expiry_date"].strftime("%Y-%m-%d")
    except:
        rows = []
    cur.close(); db.close(); return jsonify(rows)

# ------------------ API: customers/employees/medicines ------------------
@app.route("/api/customers", methods=["GET","POST"])
def api_customers():
    db = get_db(); cur = db.cursor(dictionary=True)
    if request.method == "GET":
        q = request.args.get("q","")
        if q:
            cur.execute("SELECT * FROM Customer WHERE customer_name LIKE %s OR phone LIKE %s ORDER BY customer_id DESC", (q+"%", q+"%"))
        else:
            cur.execute("SELECT * FROM Customer ORDER BY customer_id DESC")
        rows = cur.fetchall(); cur.close(); db.close(); return jsonify(rows)
    else:
        d = request.json or {}
        name = d.get("customer_name") or d.get("name")
        phone = d.get("phone")
        if not name:
            return jsonify({"error":"name required"}), 400
        cur.execute("INSERT INTO Customer (customer_name, phone) VALUES (%s,%s)", (name, phone))
        db.commit(); newid = cur.lastrowid
        cur.close(); db.close(); return jsonify({"success": True, "customer_id": newid})

@app.route("/api/employees", methods=["GET","POST"])
def api_employees():
    db = get_db(); cur = db.cursor(dictionary=True)
    if request.method == "GET":
        cur.execute("SELECT emp_id, emp_name, username FROM Employee ORDER BY emp_id DESC")
        rows = cur.fetchall(); cur.close(); db.close(); return jsonify(rows)
    else:
        d = request.json or {}
        if not (d.get("emp_name") and d.get("username") and d.get("password")):
            return jsonify({"error":"emp_name, username, password required"}), 400
        try:
            cur.execute("INSERT INTO Employee (emp_name, username, password) VALUES (%s,%s,%s)", (d["emp_name"], d["username"], d["password"]))
            db.commit(); new = cur.lastrowid
        except mysql.connector.Error as e:
            db.rollback(); cur.close(); db.close(); return jsonify({"error": str(e)}), 400
        cur.close(); db.close(); return jsonify({"success": True, "emp_id": new})

@app.route("/api/medicines", methods=["GET","POST"])
def api_medicines():
    db = get_db(); cur = db.cursor(dictionary=True)
    if request.method == "GET":
        q = request.args.get("q","")
        if q:
            cur.execute("SELECT * FROM Medicine WHERE medicine_name LIKE %s ORDER BY medicine_id DESC", (q+"%",))
        else:
            cur.execute("SELECT * FROM Medicine ORDER BY medicine_id DESC")
        rows = cur.fetchall()
        for r in rows:
            if r.get("expiry_date"): r["expiry_date"] = r["expiry_date"].strftime("%Y-%m-%d")
        cur.close(); db.close(); return jsonify(rows)
    else:
        d = request.json or {}
        if not d.get("medicine_name"):
            return jsonify({"error":"medicine_name required"}), 400
        cur.execute("INSERT INTO Medicine (medicine_name, quantity, price, expiry_date) VALUES (%s,%s,%s,%s)",
                    (d.get("medicine_name"), int(d.get("quantity",0)), float(d.get("price",0)), d.get("expiry_date")))
        db.commit(); mid = cur.lastrowid; cur.close(); db.close(); return jsonify({"success": True, "medicine_id": mid})

# ------------------ API: bills (list + create + details) ------------------
@app.route("/api/bills", methods=["GET"])
def api_bills():
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT b.bill_id, b.bill_date, b.total_amount,
               c.customer_name, c.customer_id, e.emp_name
        FROM Bill b
        LEFT JOIN Customer c ON b.customer_id = c.customer_id
        LEFT JOIN Employee e ON b.emp_id = e.emp_id
        ORDER BY b.bill_id DESC
    """)
    rows = cur.fetchall()
    for r in rows:
        if r.get("bill_date"): r["bill_date"] = r["bill_date"].strftime("%Y-%m-%d %H:%M:%S")
    cur.close(); db.close(); return jsonify(rows)

@app.route("/api/bill/<int:bill_id>", methods=["GET"])
def api_bill_details(bill_id):
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM Bill WHERE bill_id=%s", (bill_id,))
    bill = cur.fetchone()
    cur.execute("SELECT medicine_name, price, quantity, subtotal FROM BillDetails WHERE bill_id=%s", (bill_id,))
    items = cur.fetchall()
    cur.close(); db.close()
    return jsonify({"bill": bill, "items": items})

@app.route("/api/create_bill", methods=["POST"])
def api_create_bill():
    d = request.json or {}
    emp_id = d.get("emp_id")
    customer = d.get("customer", {})
    items = d.get("items", [])
    if not emp_id or not items:
        return jsonify({"error":"emp_id and items required"}), 400

    db = get_db(); cur = db.cursor(dictionary=True)
    try:
        # create or use customer
        if customer.get("customer_id"):
            cust_id = int(customer["customer_id"])
        else:
            cur.execute("INSERT INTO Customer (customer_name, phone) VALUES (%s,%s)", (customer.get("name"), customer.get("phone")))
            cust_id = cur.lastrowid

        # compute total and check stock (but do NOT update yet)
        total = 0.0
        for it in items:
            cur.execute("SELECT medicine_name, price, quantity FROM Medicine WHERE medicine_id=%s", (it["medicine_id"],))
            med = cur.fetchone()
            if not med:
                raise Exception(f"Medicine id {it['medicine_id']} not found")
            if med["quantity"] < int(it["qty"]):
                raise Exception(f"Insufficient stock for {med['medicine_name']}")
            price = float(med["price"]); subtotal = price * int(it["qty"])
            it["medicine_name"] = med["medicine_name"]; it["price"] = price; it["subtotal"] = subtotal
            total += subtotal

        # insert bill
        cur.execute("INSERT INTO Bill (customer_id, emp_id, total_amount) VALUES (%s,%s,%s)", (cust_id, emp_id, total))
        bill_id = cur.lastrowid

        # insert details AND update stock AFTER bill created
        for it in items:
            cur.execute("INSERT INTO BillDetails (bill_id, medicine_id, medicine_name, price, quantity, subtotal) VALUES (%s,%s,%s,%s,%s,%s)",
                        (bill_id, it["medicine_id"], it["medicine_name"], it["price"], int(it["qty"]), it["subtotal"]))
            cur.execute("UPDATE Medicine SET quantity = quantity - %s WHERE medicine_id=%s", (int(it["qty"]), it["medicine_id"]))

        db.commit()
    except Exception as e:
        db.rollback()
        cur.close(); db.close()
        return jsonify({"error": str(e)}), 400

    cur.close(); db.close()
    return jsonify({"success": True, "bill_id": bill_id})

# ------------------ API: employee_stats & customer_stats (no invoice lists) ------------------
@app.route("/api/employee_stats")
def api_employee_stats():
    db = get_db(); cur = db.cursor()
    cur.execute("""
        SELECT e.emp_id, e.emp_name, e.username,
               COUNT(b.bill_id) AS total_bills
        FROM Employee e
        LEFT JOIN Bill b ON e.emp_id = b.emp_id
        GROUP BY e.emp_id
        ORDER BY e.emp_id DESC
    """)
    rows = cur.fetchall()
    result = []
    for emp_id, emp_name, username, total_bills in rows:
        result.append({"emp_id": emp_id, "emp_name": emp_name, "username": username, "total_bills": int(total_bills or 0)})
    cur.close(); db.close(); return jsonify(result)

@app.route("/api/customer_stats")
def api_customer_stats():
    db = get_db(); cur = db.cursor()
    cur.execute("""
        SELECT c.customer_id, c.customer_name, c.phone,
               COUNT(b.bill_id) AS total_bills
        FROM Customer c
        LEFT JOIN Bill b ON c.customer_id = b.customer_id
        GROUP BY c.customer_id
        ORDER BY c.customer_id DESC
    """)
    rows = cur.fetchall()
    result = []
    for customer_id, customer_name, phone, total_bills in rows:
        result.append({"customer_id": customer_id, "customer_name": customer_name, "phone": phone, "total_bills": int(total_bills or 0)})
    cur.close(); db.close(); return jsonify(result)

# ------------------ INVOICE (print page) ------------------
INVOICE_TEMPLATE = """<!doctype html>
<html>
<head><meta charset="utf-8"><title>Invoice #{{bill.bill_id}}</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<style>body{font-family:Arial;padding:10px;background:#f7f7f7} .invoice{max-width:800px;margin:auto;background:#fff;padding:16px;border:1px solid #ddd} table{width:100%;border-collapse:collapse} th,td{padding:6px;border:1px solid #eee} .right{text-align:right}.center{text-align:center}.footer{margin-top:12px;text-align:center;color:#666}</style>
</head><body>
<div class="invoice">
  <div class="d-flex justify-content-between">
    <div><h4>Siri Medicals</h4><div>Shop No. 10, Main St.</div></div>
    <div class="text-end"><div><strong>Invoice:</strong> {{bill.bill_id}}</div><div><strong>Date:</strong> {{bill.bill_date}}</div><div><strong>Cashier:</strong> {{bill.emp_name}}</div></div>
  </div>
  <hr>
  <div><strong>Bill To:</strong><br>Customer ID: {{ bill.customer_id }}<br>{{ bill.customer_name or 'WALK-IN' }}<br>Phone: {{ bill.phone or 'N/A' }}</div>
  <table class="mt-3">
    <thead><tr><th>#</th><th>Item</th><th class="right">Price</th><th class="center">Qty</th><th class="right">Subtotal</th></tr></thead>
    <tbody>
    {% for it in items %}
      <tr>
        <td>{{ loop.index }}</td>
        <td>{{ it.medicine_name }}</td>
        <td class="right">{{ '%.2f'|format(it.price) }}</td>
        <td class="center">{{ it.quantity }}</td>
        <td class="right">{{ '%.2f'|format(it.subtotal) }}</td>
      </tr>
    {% endfor %}
    </tbody>
    <tfoot>
      <tr><td colspan="4" class="right">Subtotal</td><td class="right">{{ '%.2f'|format(bill.total_amount) }}</td></tr>
      <tr><td colspan="4" class="right">GST ({{gst_rate}}%)</td><td class="right">{{ '%.2f'|format(gst_amount) }}</td></tr>
      <tr class="fw-bold"><td colspan="4" class="right">Grand Total</td><td class="right">{{ '%.2f'|format(grand_total) }}</td></tr>
    </tfoot>
  </table>
  <div class="footer">Thank you for choosing <strong>Siri Medicals</strong>!</div>
  <div class="mt-2 no-print"><a class="btn btn-primary" href="javascript:window.print()">Print</a></div>
</div>
</body></html>"""

@app.route("/api/invoice/<int:bill_id>")
def api_invoice(bill_id):
    db = get_db(); cur = db.cursor(dictionary=True)
    cur.execute("""
      SELECT b.bill_id, b.bill_date, b.total_amount, b.customer_id, c.customer_name, c.phone, e.emp_name
      FROM Bill b
      LEFT JOIN Customer c ON b.customer_id = c.customer_id
      LEFT JOIN Employee e ON b.emp_id = e.emp_id
      WHERE b.bill_id = %s
    """, (bill_id,))
    bill = cur.fetchone()
    if not bill:
        cur.close(); db.close(); return "Bill not found", 404
    if isinstance(bill.get("bill_date"), (datetime, date)):
        bill["bill_date"] = bill["bill_date"].strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("SELECT medicine_name, price, quantity, subtotal FROM BillDetails WHERE bill_id=%s", (bill_id,))
    items = cur.fetchall()
    subtotal = float(bill["total_amount"] or 0.0)
    gst_amount = round(subtotal * (GST_RATE/100.0), 2)
    grand_total = round(subtotal + gst_amount, 2)
    cur.close(); db.close()
    return render_template_string(INVOICE_TEMPLATE, bill=bill, items=items, gst_rate=GST_RATE, gst_amount=gst_amount, grand_total=grand_total)

# ------------------ uploaded sql info ------------------
@app.route("/api/uploaded_sql_info")
def uploaded_sql_info():
    return jsonify({"path": UPLOADED_SQL_PATH, "exists": True})

if __name__ == "__main__":
    app.run(debug=True)
