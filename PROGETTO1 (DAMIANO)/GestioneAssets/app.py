from flask import Flask, request, jsonify, render_template, redirect, url_for
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)

def create_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DATABASE_HOST', '192.168.178.148'),
            port=os.getenv('DATABASE_PORT', 3308),
            database=os.getenv('DATABASE_NAME', 'asset_managment'),
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
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM dispositivi")
    dispositivi = cursor.fetchall()
    cursor.execute("SELECT * FROM dipendenti")
    dipendenti = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html', dispositivi=dispositivi, dipendenti=dipendenti)

@app.route('/dispositivi', methods=['GET', 'POST'])
def dispositivi():
    conn = create_db_connection()
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
    cursor.execute("SELECT * FROM dispositivi")
    dispositivi = cursor.fetchall()
    cursor.execute("SELECT * FROM dipendenti")
    dipendenti = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html', dispositivi=dispositivi, dipendenti=dipendenti)

@app.route('/presenze', methods=['POST'])
def presenze():
    conn = create_db_connection()
    cursor = conn.cursor(dictionary=True)
    id_dipendente = request.form['id']
    data_presenza = request.form['data_presenza']
    orario1_entrata = request.form['orario1_entrata']
    orario1_uscita = request.form['orario1_uscita']
    orario2_entrata = request.form['orario2_entrata']
    orario2_uscita = request.form['orario2_uscita']
    cursor.execute(
        """
        INSERT INTO presenze (id, data_presenza, orario1_entrata, orario1_uscita, orario2_entrata, orario2_uscita)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (id_dipendente, data_presenza, orario1_entrata, orario1_uscita, orario2_entrata, orario2_uscita)
    )
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/sede', methods=['GET'])
def sede():
    conn = create_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM dipendenti WHERE sede_azienda = %s", (request.args.get('sede'),))
    dipendenti = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html', dipendenti=dipendenti)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
