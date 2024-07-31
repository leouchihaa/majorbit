from flask import Flask, request, jsonify, render_template
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)

def create_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DATABASE_HOST', '192.168.178.148'),
            port=os.getenv('DATABASE_PORT', 3308),
            database=os.getenv('DATABASE_NAME', 'asset_management'),
            user=os.getenv('DATABASE_USER', 'root'),
            password=os.getenv('DATABASE_PASSWORD', 'my-secret-pw')
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

@app.route('/')
def index():
    conn = create_db_connection()
    if conn is None:
        return "Errore di connessione al database", 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM dispositivi")
    dispositivi = cursor.fetchall()
    cursor.execute("SELECT * FROM dipendenti")
    dipendenti = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html', dispositivi=dispositivi, dipendenti=dipendenti)

@app.route('/dispositivi', methods=['GET', 'POST'])
def dispositivi_page():
    conn = create_db_connection()
    if conn is None:
        return "Errore di connessione al database", 500

    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        action = request.form['action']
        if action == 'aggiungi':
            dispositivo = request.form['dispositivo']
            srn_iccid = request.form['srn_iccid']
            num_aziendale = request.form['num_aziendale']
            data_acquisto = request.form['data_acquisto']
            scad_garanzia = request.form['scad_garanzia']
            ram = request.form['ram']
            archiviazione = request.form['archiviazione']
            processore = request.form['processore']
            os = request.form['os']
            oper_telefonico = request.form['oper_telefonico']
            modello = request.form['modello']
            stato = request.form['stato']
            disponibilita = request.form['disponibilita']
            note = request.form['note']
            cursor.execute(
                """
                INSERT INTO dispositivi (dispositivo, srn_iccid, num_aziendale, data_acquisto, scad_garanzia, ram, archiviazione, processore, os, oper_telefonico, modello, stato, disponibilita, note)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (dispositivo, srn_iccid, num_aziendale, data_acquisto, scad_garanzia, ram, archiviazione, processore, os, oper_telefonico, modello, stato, disponibilita, note)
            )
            conn.commit()
        elif action == 'elimina':
            srn_iccid = request.form['srn_iccid']
            cursor.execute("DELETE FROM dispositivi WHERE srn_iccid = %s", (srn_iccid,))
            conn.commit()
        elif action == 'modifica':
            srn_iccid = request.form['srn_iccid']
            nuovo_stato = request.form['nuovo_stato']
            cursor.execute("UPDATE dispositivi SET stato = %s WHERE srn_iccid = %s", (nuovo_stato, srn_iccid))
            conn.commit()
   
    # Filtraggio dei dispositivi
    query = "SELECT * FROM dispositivi WHERE 1=1"
    params = []
    
    dispositivo = request.args.get('dispositivo', '')
    srn_iccid = request.args.get('srn_iccid', '')
    num_aziendale = request.args.get('num_aziendale', '')
    data_acquisto = request.args.get('data_acquisto', '')
    scad_garanzia = request.args.get('scad_garanzia', '')
    ram = request.args.get('ram', '')
    archiviazione = request.args.get('archiviazione', '')
    processore = request.args.get('processore', '')
    os = request.args.get('os', '')
    oper_telefonico = request.args.get('oper_telefonico', '')
    modello = request.args.get('modello', '')
    stato = request.args.get('stato', '')
    disponibilita = request.args.get('disponibilita', '')

    if dispositivo:
        query += " AND dispositivo LIKE %s"
        params.append(f"%{dispositivo}%")
    if srn_iccid:
        query += " AND srn_iccid LIKE %s"
        params.append(f"%{srn_iccid}%")
    if num_aziendale:
        query += " AND num_aziendale LIKE %s"
        params.append(f"%{num_aziendale}%")
    if data_acquisto:
        query += " AND data_acquisto = %s"
        params.append(data_acquisto)
    if scad_garanzia:
        query += " AND scad_garanzia = %s"
        params.append(scad_garanzia)
    if ram:
        query += " AND ram LIKE %s"
        params.append(f"%{ram}%")
    if archiviazione:
        query += " AND archiviazione LIKE %s"
        params.append(f"%{archiviazione}%")
    if processore:
        query += " AND processore LIKE %s"
        params.append(f"%{processore}%")
    if os:
        query += " AND os LIKE %s"
        params.append(f"%{os}%")
    if oper_telefonico:
        query += " AND oper_telefonico LIKE %s"
        params.append(f"%{oper_telefonico}%")
    if modello:
        query += " AND modello LIKE %s"
        params.append(f"%{modello}%")
    if stato:
        query += " AND stato LIKE %s"
        params.append(f"%{stato}%")
    if disponibilita:
        query += " AND disponibilita LIKE %s"
        params.append(f"%{disponibilita}%")
    
    cursor.execute(query, params)
    dispositivi = cursor.fetchall()
    
    # Recupero dei dipendenti (già presente nel tuo codice)
    cursor.execute("SELECT * FROM dipendenti")
    dipendenti = cursor.fetchall()

    conn.close()
    return render_template('dispositivi.html', dispositivi=dispositivi, dipendenti=dipendenti)

@app.route('/dipendenti', methods=['GET', 'POST'])
def dipendenti_page():
    conn = create_db_connection()
    if conn is None:
        return "Errore di connessione al database", 500

    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        nome = request.form['nome']
        cognome = request.form['cognome']
        cod_fisc = request.form['cod_fisc']
        data_nascita = request.form['data_nascita']
        citta = request.form['citta']
        provincia = request.form['provincia']
        via = request.form['via']
        email = request.form['email']
        telefono1 = request.form['telefono1']
        telefono2 = request.form['telefono2']
        tipologia_contratto = request.form['tipologia_contratto']
        data_assunzione = request.form['data_assunzione']
        scadenza_contratto = request.form['scadenza_contratto']
        stipendio = request.form['stipendio']
        ruolo = request.form['ruolo']
        sede_azienda = request.form['sede_azienda']
        cursor.execute(
            """
            INSERT INTO dipendenti (nome, cognome, cod_fisc, data_nascita, citta, provincia, via, email, telefono1, telefono2, tipologia_contratto, data_assunzione, scadenza_contratto, stipendio, ruolo, sede_azienda)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (nome, cognome, cod_fisc, data_nascita, citta, provincia, via, email, telefono1, telefono2, tipologia_contratto, data_assunzione, scadenza_contratto, stipendio, ruolo, sede_azienda)
        )
        conn.commit()
    else:
        cognome = request.args.get('cognome', '')
        citta = request.args.get('citta', '')
        provincia = request.args.get('provincia', '')
        tipologia_contratto = request.args.get('tipologia_contratto', '')
        data_assunzione = request.args.get('data_assunzione', '')
        ruolo = request.args.get('ruolo', '')
        
        query = "SELECT * FROM dipendenti WHERE 1=1"
        params = []
        
        if cognome:
            query += " AND cognome LIKE %s"
            params.append(f"%{cognome}%")
        if citta:
            query += " AND citta LIKE %s"
            params.append(f"%{citta}%")
        if provincia:
            query += " AND provincia LIKE %s"
            params.append(f"%{provincia}%")
        if tipologia_contratto:
            query += " AND tipologia_contratto LIKE %s"
            params.append(f"%{tipologia_contratto}%")
        if data_assunzione:
            query += " AND data_assunzione = %s"
            params.append(data_assunzione)
        if ruolo:
            query += " AND ruolo LIKE %s"
            params.append(f"%{ruolo}%")
        
        cursor.execute(query, params)
        dipendenti = cursor.fetchall()

    conn.close()
    return render_template('dipendenti.html', dipendenti=dipendenti)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
