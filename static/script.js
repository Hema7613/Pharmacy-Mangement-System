// script.js (used by multi-page layout)
let cart = [];
let selectedCustomer = null;
let currentEmp = JSON.parse(localStorage.getItem('ph_emp') || 'null');

// common helpers
async function fetchJSON(url, opts){ const r = await fetch(url, opts); return r.json(); }

// ---------------- dashboard helpers are inline in that template ----------------

// ---------------- customers page helpers ----------------
async function loadCustomers(){
  const rows = await fetchJSON('/api/customer_stats');
  let html = '<table class="table"><tr><th>ID</th><th>Name</th><th>Phone</th><th>Total Bills</th></tr>';
  rows.forEach(c => html += `<tr><td>${c.customer_id}</td><td>${c.customer_name}</td><td>${c.phone}</td><td>${c.total_bills}</td></tr>`);
  html += '</table>'; document.getElementById('customersList') && (document.getElementById('customersList').innerHTML = html);
}

// add customer (on customers page)
async function addCustomerForm(){
  const name = document.getElementById('custName').value.trim();
  const phone = document.getElementById('custPhone').value.trim();
  if(!name){ alert('Name required'); return; }
  const d = await fetchJSON('/api/customers', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({customer_name:name, phone})});
  if(d.success){ alert('Added'); document.getElementById('custName').value=''; document.getElementById('custPhone').value=''; loadCustomers(); }
  else alert('Error: ' + (d.error||'unknown'));
}

// ---------------- employees page helpers ----------------
async function loadEmployees(){
  const rows = await fetchJSON('/api/employee_stats');
  let html = '<table class="table"><tr><th>ID</th><th>Name</th><th>Username</th><th>Total Bills</th></tr>';
  rows.forEach(e => html += `<tr><td>${e.emp_id}</td><td>${e.emp_name}</td><td>${e.username}</td><td>${e.total_bills}</td></tr>`);
  html += '</table>'; document.getElementById('employeesList') && (document.getElementById('employeesList').innerHTML = html);
}

async function addEmployeeForm(){
  const name = document.getElementById('empName').value.trim();
  const username = document.getElementById('empUser').value.trim();
  const password = document.getElementById('empPass').value.trim();
  if(!name||!username||!password){ alert('All fields required'); return; }
  const d = await fetchJSON('/api/employees', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({emp_name:name, username, password})});
  if(d.success){ alert('Added'); document.getElementById('empName').value=''; document.getElementById('empUser').value=''; document.getElementById('empPass').value=''; loadEmployees(); }
  else alert('Error: ' + (d.error||'unknown'));
}

// ---------------- medicines page helpers ----------------
async function loadMedicines(){
  const rows = await fetchJSON('/api/medicines');
  let html = '<table class="table table-sm"><tr><th>ID</th><th>Name</th><th>Qty</th><th>Price</th><th>Expiry</th></tr>';
  rows.forEach(r => html += `<tr><td>${r.medicine_id}</td><td>${r.medicine_name}</td><td>${r.quantity}</td><td>${r.price}</td><td>${r.expiry_date||''}</td></tr>`);
  html += '</table>'; document.getElementById('medList') && (document.getElementById('medList').innerHTML = html);
}

async function addMedicineForm(){
  const name = document.getElementById('medName').value.trim();
  const qty = parseInt(document.getElementById('medQty').value || 0);
  const price = parseFloat(document.getElementById('medPrice').value || 0);
  const expiry = document.getElementById('medExpiry').value || null;
  if(!name){ alert('Name required'); return; }
  const d = await fetchJSON('/api/medicines', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({medicine_name:name, quantity:qty, price:price, expiry_date: expiry})});
  if(d.success){ alert('Added'); document.getElementById('medName').value=''; document.getElementById('medQty').value=''; document.getElementById('medPrice').value=''; document.getElementById('medExpiry').value=''; loadMedicines(); }
  else alert('Error: ' + (d.error||'unknown'));
}

// ---------------- bills page helpers ----------------
async function loadBills(){
  const rows = await fetchJSON('/api/bills');
  let html = '<table class="table"><tr><th>ID</th><th>Customer</th><th>Employee</th><th>Total</th><th>Date</th><th>Invoice</th></tr>';
  rows.forEach(b => html += `<tr><td>${b.bill_id}</td><td>${b.customer_name||'WALK-IN'}</td><td>${b.emp_name||''}</td><td>${b.total_amount}</td><td>${b.bill_date}</td><td><a target="_blank" href="/api/invoice/${b.bill_id}" class="btn btn-sm btn-primary">Open</a></td></tr>`);
  html += '</table>'; document.getElementById('billsList') && (document.getElementById('billsList').innerHTML = html);
}

// ---------------- create bill page helpers ----------------
function prepareCreateBillPage(){
  cart = []; selectedCustomer = null; refreshCartUI();
}

async function searchCustomerForBill(){
  const q = document.getElementById('custSearch').value.trim();
  if(!q){ document.getElementById('custSearchResults').innerHTML = ''; return; }
  const rows = await fetchJSON('/api/customers?q=' + encodeURIComponent(q));
  let html = rows.map(r => `<div class="p-2 border" style="cursor:pointer" onclick="selectCustomer(${r.customer_id}, '${r.customer_name}', '${r.phone}')">${r.customer_name} (${r.phone})</div>`).join('');
  document.getElementById('custSearchResults').innerHTML = html;
}

function selectCustomer(id, name, phone){
  selectedCustomer = { customer_id:id, name, phone };
  document.getElementById('custSearchResults').innerHTML = `<div class="alert alert-success">Selected: ${name} (${phone})</div>`;
}

async function addCustomerFromBill(){
  const name = document.getElementById('newCustName').value.trim();
  const phone = document.getElementById('newCustPhone').value.trim();
  if(!name){ alert('Name required'); return; }
  const d = await fetchJSON('/api/customers', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({customer_name:name, phone})});
  if(d.success){ selectedCustomer = { customer_id: d.customer_id, name, phone }; alert('Added & Selected'); document.getElementById('newCustName').value=''; document.getElementById('newCustPhone').value=''; }
  else alert('Error: ' + (d.error||'unknown'));
}

async function searchMedicineForBill(){
  const q = document.getElementById('medSearch').value.trim();
  if(!q){ document.getElementById('medSearchResults').innerHTML = ''; return; }
  const rows = await fetchJSON('/api/medicines?q=' + encodeURIComponent(q));
  let html = rows.map(m => `<div class="p-2 border" style="cursor:pointer" onclick="addToCartPrompt(${m.medicine_id}, '${m.medicine_name.replace(/'/g, "\\'")}', ${m.price}, ${m.quantity})">${m.medicine_name} — ₹${m.price} (stock:${m.quantity})</div>`).join('');
  document.getElementById('medSearchResults').innerHTML = html;
}

function addToCartPrompt(medicine_id, name, price, stock){
  const qtyStr = prompt(`Enter qty for ${name} (stock: ${stock})`, "1");
  if(!qtyStr) return;
  const qty = parseInt(qtyStr);
  if(isNaN(qty) || qty<=0){ alert('Invalid qty'); return; }
  if(qty > stock){ alert('Insufficient stock'); return; }
  cart.push({ medicine_id, medicine_name: name, price: parseFloat(price), qty: qty, subtotal: parseFloat(price)*qty });
  refreshCartUI();
}

function refreshCartUI(){
  const tbody = document.getElementById('cartBody');
  if(!tbody) return;
  let html = '';
  let total = 0;
  cart.forEach((it, idx) => {
    html += `<tr><td>${it.medicine_name}</td><td>${it.qty}</td><td>₹ ${it.price.toFixed(2)}</td><td>₹ ${it.subtotal.toFixed(2)}</td><td><button class="btn btn-sm btn-danger" onclick="removeFromCart(${idx})">Remove</button></td></tr>`;
    total += it.subtotal;
  });
  tbody.innerHTML = html;
  const el = document.getElementById('cartTotal'); if(el) el.textContent = total.toFixed(2);
}

function removeFromCart(i){ cart.splice(i,1); refreshCartUI(); }

async function createBillFromUI(){
  if(!currentEmp){ alert('Please login first (use /login)'); return; }
  if(cart.length === 0){ alert('Cart empty'); return; }
  const payload = { emp_id: currentEmp.emp_id, customer: (selectedCustomer ? { customer_id: selectedCustomer.customer_id } : {}), items: cart.map(it => ({medicine_id: it.medicine_id, qty: it.qty})) };
  const d = await fetchJSON('/api/create_bill', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
  if(d.success){
    alert('Bill created: ' + d.bill_id);
    window.open('/api/invoice/' + d.bill_id, '_blank');
    cart = []; selectedCustomer = null; refreshCartUI();
    // refresh lists
    loadMedicines(); loadBills(); loadEmployees(); loadCustomers();
  } else {
    alert('Error: ' + (d.error || 'unknown'));
  }
}
