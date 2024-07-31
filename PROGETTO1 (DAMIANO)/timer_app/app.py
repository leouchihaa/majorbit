from flask import Flask, render_template, request, jsonify
import mysql.connector
from datetime import timedelta

app = Flask(__name__)

# Database configuration
db_config = {
    'user': 'root',       # Replace with your MySQL username
    'password': '12345',       # Replace with your MySQL password
    'host': '127.0.0.1',
    'database': 'timer_db'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save_time', methods=['POST'])
def save_time():
    data = request.get_json()
    recorded_time = data['recorded_time']

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        sql = "INSERT INTO timer_records (recorded_time) VALUES (%s)"
        cursor.execute(sql, (recorded_time,))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({"message": "Time recorded successfully"}), 200
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

if __name__ == '__main__':
    app.run(debug=True)
