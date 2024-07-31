from flask import Flask, request, jsonify, redirect, url_for
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
import mysql.connector

app = Flask(__name__)
app.config.from_object('config.Config')

mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)

# In-memory user store for simplicity
users = {'user@example.com': {'password': 'password123', 'id': 1, 'name': 'Example User'}}

class User(UserMixin):
    def __init__(self, id, email, name):
        self.id = id
        self.email = email
        self.name = name

@login_manager.user_loader
def load_user(user_id):
    for email, user_data in users.items():
        if user_data['id'] == int(user_id):
            return User(user_id, email, user_data['name'])
    return None

def get_db_connection():
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    user = users.get(email)
    
    if user and user['password'] == password:
        user_obj = User(user['id'], email, user['name'])
        login_user(user_obj)
        return jsonify({'message': 'Logged in successfully'}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/request-asset', methods=['POST'])
@login_required
def request_asset():
    data = request.json
    asset_type = data.get('asset_type')
    motivation = data.get('motivation')
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    if not all([asset_type, motivation, start_date, end_date]):
        return jsonify({'error': 'Missing data'}), 400

    # Update asset availability in the database
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        update_query = """
        UPDATE disspositivi
        SET disponibilità = 'ELABORAZIONE'
        WHERE dispositivo = %s AND disponibilità = 'Y'
        LIMIT 1
        """
        cursor.execute(update_query, (asset_type,))
        if cursor.rowcount == 0:
            return jsonify({'error': 'No available assets found'}), 404

        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    # Generate URL for the manager to accept the request
    accept_url = url_for('accept_request', asset_type=asset_type, _external=True)

    # Invia mail
    try:
        msg = Message(
            'Richiesta Asset',
            sender=app.config['MAIL_USERNAME'],
            recipients=['responsabile@example.com']
        )
        msg.body = f"""
        Tipo Asset: {asset_type}
        Motivazione: {motivation}
        Data Inizio: {start_date}
        Data Fine: {end_date}
        Richiedente: {current_user.name} ({current_user.email})

        Per accettare la richiesta, clicca sul seguente link:
        {accept_url}
        """
        mail.send(msg)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Richiesta inviata con successo'})

@app.route('/accept-request/<asset_type>', methods=['GET'])
def accept_request(asset_type):
    # Qui puoi implementare la logica per gestire l'accettazione della richiesta
    # Ad esempio, aggiornare lo stato della richiesta nel database
    return jsonify({'message': f'Richiesta per asset {dispositivo} accettata'})

@app.route('/get-assets/<asset_type>', methods=['GET'])
@login_required
def get_assets(asset_type):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT * FROM dispositivi
    WHERE dispositivo = %s
    """
    cursor.execute(query, (asset_type,))
    assets = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(assets)

if __name__ == '__main__':
    app.run(debug=True)
