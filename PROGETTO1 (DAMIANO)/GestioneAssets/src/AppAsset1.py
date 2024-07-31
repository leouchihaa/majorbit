from flask import Flask, request, jsonify, send_from_directory,render_template
from flask_mail import Mail, Message
import mysql.connector
import os

app = Flask(__name__)
app.config.from_object('config.Config')

mail = Mail(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("RichiestaAsset1.html")
    
    
@app.route('/request-asset', methods=['GET'])   
def get_db_connection():
    return mysql.connector.connect(
        host=app.config['192.168.178.148'],
        user=app.config['root'],
        password=app.config['my-secret-pw'],
        database=app.config['asset_managment']
    )



@app.route('/request-asset', methods=['POST'])
# Funzione richiesta asset #
def request_asset():
    data = request.json
    asset_type = data.get('asset_type')
    motivation = data.get('motivation')
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    if not all([asset_type, motivation, start_date, end_date]):
        return jsonify({'error': 'Missing data'}), 400

    # Invia mail #
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
        """
        mail.send(msg)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Richiesta inviata con successo'})

@app.route('/get-assets/<asset_type>', methods=['GET'])
# Funzione ottieni asset #
def get_assets(asset_type):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT * FROM assets
    WHERE asset_type = %s
    """
    cursor.execute(query, (asset_type,))
    assets = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return jsonify(assets)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
