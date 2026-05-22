import sqlite3
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import os
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'supersecretkey'
DATABASE = 'database.db'

# Admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD_HASH = generate_password_hash('admin123')

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS slots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                time_slot TEXT NOT NULL,
                booked_by TEXT DEFAULT NULL,
                is_booked INTEGER DEFAULT 0
            )
        ''')
        
        # Check if slots already exist
        count = conn.execute('SELECT COUNT(*) FROM slots').fetchone()[0]
        if count == 0:
            initial_slots = [
                ('Friday, 3 July 2026', '9:00am–10:00am'),
                ('Friday, 3 July 2026', '10:30am–11:30am'),
                ('Friday, 3 July 2026', '12:00pm–1:00pm'),
                ('Friday, 3 July 2026', '1:30pm–2:30pm'),
                ('Friday, 3 July 2026', '3:00pm–4:00pm'),
                ('Friday, 3 July 2026', '4:00pm–5:00pm'),
                ('Monday, 13 July 2026', '9:00am–10:00am'),
                ('Monday, 13 July 2026', '10:30am–11:30am'),
                ('Monday, 13 July 2026', '12:00pm–1:00pm'),
                ('Monday, 13 July 2026', '1:30pm–2:30pm'),
                ('Monday, 13 July 2026', '3:00pm–4:00pm'),
                ('Monday, 13 July 2026', '4:00pm–5:00pm')
            ]
            conn.executemany('INSERT INTO slots (date, time_slot) VALUES (?, ?)', initial_slots)
        conn.commit()

@app.route('/')
def index():
    with get_db() as conn:
        # Sorting by date and then by the time_slot string. 
        # Since the time slots are consistent (9:00am, 10:30am, etc.), 
        # a simple ASC sort on the string should work, but we can refine if needed.
        slots = conn.execute('SELECT * FROM slots ORDER BY date ASC, id ASC').fetchall()
    
    # Group slots by date
    grouped_slots = {}
    for slot in slots:
        if slot['date'] not in grouped_slots:
            grouped_slots[slot['date']] = []
        grouped_slots[slot['date']].append(slot)
    
    return render_template('index.html', grouped_slots=grouped_slots)

@app.route('/book/<int:slot_id>', methods=['GET', 'POST'])
def book(slot_id):
    with get_db() as conn:
        slot = conn.execute('SELECT * FROM slots WHERE id = ?', (slot_id,)).fetchone()
    
    if not slot or slot['is_booked']:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        if full_name:
            with get_db() as conn:
                conn.execute('UPDATE slots SET booked_by = ?, is_booked = 1 WHERE id = ?', (full_name, slot_id))
                conn.commit()
            return render_template('confirmation.html', name=full_name, date=slot['date'], time=slot['time_slot'], venue='Room C2B')
    
    return render_template('book.html', slot=slot)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['admin_logged_in'] = True
            return redirect(url_for('admin_panel'))
        else:
            return "Invalid credentials", 401
            
    # Always show login page when accessing /admin directly
    return render_template('admin_login.html')

@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))
    
    with get_db() as conn:
        booked_slots = conn.execute('SELECT * FROM slots WHERE is_booked = 1').fetchall()
        available_slots = conn.execute('SELECT * FROM slots WHERE is_booked = 0').fetchall()
    
    return render_template('admin_panel.html', booked_slots=booked_slots, available_slots=available_slots)

@app.route('/admin/cancel/<int:slot_id>')
def cancel_booking(slot_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))
    
    with get_db() as conn:
        conn.execute('UPDATE slots SET booked_by = NULL, is_booked = 0 WHERE id = ?', (slot_id,))
        conn.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/add_slot', methods=['POST'])
def add_slot():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))
    
    date = request.form.get('date')
    time_slot = request.form.get('time_slot')
    if date and time_slot:
        with get_db() as conn:
            conn.execute('INSERT INTO slots (date, time_slot) VALUES (?, ?)', (date, time_slot))
            conn.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_slot/<int:slot_id>')
def delete_slot(slot_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))
    
    with get_db() as conn:
        conn.execute('DELETE FROM slots WHERE id = ?', (slot_id,))
        conn.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/export')
def export_data():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))
    
    with get_db() as conn:
        df = pd.read_sql_query('SELECT booked_by as Name, date as Date, time_slot as "Time Slot" FROM slots WHERE is_booked = 1', conn)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Bookings')
    output.seek(0)
    
    return send_file(output, download_name='bookings.xlsx', as_attachment=True)

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
