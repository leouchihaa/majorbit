from flask import Flask, request, jsonify, send_from_directory
import pymysql
from datetime import datetime

app = Flask(__name__, static_url_path='', static_folder='static')

# Configure MySQL connection
db = pymysql.connect(host='localhost',
                     user='root',
                     password='Salsa',
                     database='Leonardo',
                     cursorclass=pymysql.cursors.DictCursor)

# Serve the HTML file
@app.route('/')
def serve_html():
    return send_from_directory(app.static_folder, 'index.html')

# Endpoint to fetch data from Accounts and Devices tables
@app.route('/data', methods=['GET'])
def get_data():
    cursor = db.cursor()
    account_query = 'SELECT * FROM Accounts'
    device_query = 'SELECT * FROM Devices'

    cursor.execute(account_query)
    accounts = cursor.fetchall()

    cursor.execute(device_query)
    devices = cursor.fetchall()

    return jsonify({'accounts': accounts, 'devices': devices})

# Endpoint to fetch data from Attendance table
@app.route('/attendance', methods=['GET'])
def get_attendance():
    cursor = db.cursor()
    attendance_query = 'SELECT * FROM Attendance'

    cursor.execute(attendance_query)
    attendance = cursor.fetchall()

    return jsonify({'attendance': attendance})

# Endpoint to handle clock-in and clock-out actions
@app.route('/attendance', methods=['POST'])
def update_attendance():
    data = request.json
    id = data.get('id', 1)  # Default id to 1 for simplicity
    action = data['action']
    timestamp = datetime.now()

    cursor = db.cursor()

    if action == 'clock-in':
        clock_in_query = 'INSERT INTO Attendance (id, name, clockIn) SELECT id, name, %s FROM Accounts WHERE id = %s'
        cursor.execute(clock_in_query, (timestamp, id))
        db.commit()
        return 'Clocked in successfully'

    elif action == 'clock-out':
        clock_out_query = 'UPDATE Attendance SET clockOut = %s WHERE id = %s AND clockOut IS NULL'
        cursor.execute(clock_out_query, (timestamp, id))
        db.commit()
        return 'Clocked out successfully'

    else:
        return 'Invalid action', 400

if __name__ == '__main__':
    app.run(port=3000)
