from flask import Flask, render_template, request, redirect, url_for, session, flash, get_flashed_messages
import mysql.connector
import re
import bcrypt
import os
import datetime

app = Flask(__name__)
app.secret_key = 'il_tuo_segreto'

# Configurazione del database MySQL
db_config = {
    'host': os.getenv('MYSQL_HOST', '192.168.178.162'),
    'port': os.getenv('MYSQL_PORT', '3308'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'my-secret-pw'),
    'database': os.getenv('MYSQL_DATABASE', 'asset_management')
}

# Variabile globale per memorizzare l'orario di inizio pausa
pause_start_time = None

@app.route('/')
def home():
    if 'loggedin' in session:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Recupera l'ID del dipendente basato sull'email nella sessione
        cursor.execute('SELECT id FROM dipendenti WHERE email = %s', (session['email'],))
        dipendente = cursor.fetchone()

        if dipendente:
            dipendente_id = dipendente['id']

            # Query SQL aggiornata per includere gli orari di straordinario dalla tabella presenze
            query = '''
                SELECT p.*, d.nome AS dipendente_nome, d.cognome AS dipendente_cognome,
                       DATE_FORMAT(p.orario1_entrata, '%H:%i') AS orario1_entrata,
                       DATE_FORMAT(p.orario1_uscita, '%H:%i') AS orario1_uscita,
                       DATE_FORMAT(p.orario2_entrata, '%H:%i') AS orario2_entrata,
                       DATE_FORMAT(p.orario2_uscita, '%H:%i') AS orario2_uscita,
                       TIME_FORMAT(SEC_TO_TIME(
                           TIMESTAMPDIFF(SECOND, p.orario1_entrata, p.orario1_uscita) - COALESCE(p.orario_pausa * 60, 0)
                       ), '%H:%i') AS totale_ore_mattina,
                       TIME_FORMAT(SEC_TO_TIME(
                           TIMESTAMPDIFF(SECOND, p.orario1_entrata, p.orario1_uscita) +
                           TIMESTAMPDIFF(SECOND, p.orario2_entrata, p.orario2_uscita) - COALESCE(p.orario_pausa * 60, 0)
                       ), '%H:%i') AS totale_ore_giorno,
                       TIME_FORMAT(p.orario_inizio_straordinario, '%H:%i') AS straordinario_inizio,
                       TIME_FORMAT(p.orario_fine_straordinario, '%H:%i') AS straordinario_fine
                FROM presenze p
                JOIN dipendenti d ON p.id = d.id
                WHERE d.id = %s
                ORDER BY p.data_presenza DESC
            '''

            cursor.execute(query, (dipendente_id,))
            presenze = cursor.fetchall()

            # Debug: stampa le presenze
            for presenza in presenze:
                print(presenza)  # Aggiungi questa riga per debug

            cursor.close()
            conn.close()

            data_presenza = datetime.datetime.now().strftime('%Y-%m-%d')
            orario_entrata = datetime.datetime.now().strftime('%H:%M')
            orario_uscita = datetime.datetime.now().strftime('%H:%M')

            return render_template('home.html', email=session['email'], data_presenza=data_presenza, orario_entrata=orario_entrata, orario_uscita=orario_uscita, presenze=presenze)

    return redirect(url_for('login'))


# Pagina di login
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('SELECT * FROM login WHERE email = %s', (email,))
        account = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if account and bcrypt.checkpw(password, account['credenziali_accesso'].encode('utf-8')):
            session['loggedin'] = True
            session['email'] = account['email']
            return redirect(url_for('home'))
        else:
            msg = 'Login fallito, riprova.'
    
    return render_template('login.html', msg=msg)

# Logout
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('email', None)
    return redirect(url_for('login'))

# Registrazione nuovo dipendente
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        email = request.form['email']
        nome = request.form['nome']
        cognome = request.form['cognome']
        sesso = request.form['sesso']
        codicefiscale = request.form['cod_fisc']
        data_nascita = request.form['data_nascita']
        citta = request.form['citta']
        provincia = request.form['provincia']
        via = request.form['via']
        telefono = request.form['telefono']
        tipologia_contratto = request.form['tipologia_contratto']
        data_assunzione = request.form['data_assunzione']
        ruolo = request.form['ruolo']
        sede_azienda = request.form['sede_azienda']
        stipendio = request.form['stipendio']
        reparto = request.form['reparto']
        password = request.form['password'].encode('utf-8')
        
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        
        try:
            with mysql.connector.connect(**db_config) as conn:
                with conn.cursor() as cursor:
                    # Controlla se l'email esiste già
                    cursor.execute('SELECT * FROM dipendenti WHERE email = %s FOR UPDATE', (email,))
                    email_exists = cursor.fetchone()
                    
                    if email_exists:
                        msg = "L'email esiste già."
                    elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                        msg = 'Indirizzo email non valido.'
                    elif not re.match(r'[A-Za-z0-9]+', password.decode('utf-8')):
                        msg = 'La password deve contenere solo caratteri e numeri.'
                    elif not email or not nome or not cognome or not data_nascita or not citta or not provincia or not via or not telefono or not tipologia_contratto or not data_assunzione or not ruolo or not sede_azienda or not password or not codicefiscale or not stipendio or not reparto:
                        msg = 'Compila tutti i campi.'
                    else:
                        # Inserisci i dati nel database
                        cursor.execute('INSERT INTO dipendenti (nome, cognome, sesso, cod_fisc, email, data_nascita, citta, provincia, via, telefono1, tipologia_contratto, data_assunzione, ruolo, sede_azienda, stipendio, reparto) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                                       (nome, cognome, sesso, codicefiscale, email, data_nascita, citta, provincia, via, telefono, tipologia_contratto, data_assunzione, ruolo, sede_azienda, stipendio, reparto))
                        cursor.execute('INSERT INTO login (email, credenziali_accesso) VALUES (%s, %s)', 
                                       (email, hashed_password.decode('utf-8')))
                        conn.commit()
                        msg = 'Registrazione avvenuta con successo!'
                        return redirect(url_for('login'))
        except mysql.connector.Error as err:
            print(f"Errore durante la registrazione: {err}")
            msg = "Errore durante la registrazione, riprova più tardi."
    
    return render_template('register.html', msg=msg)

@app.route('/aggiungi_entrata', methods=['POST'])
def aggiungi_entrata():
    if 'loggedin' in session:
        email = session['email']
        data_presenza = request.form['data_presenza']
        orario_entrata = request.form['orario_entrata']
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM dipendenti WHERE email = %s', (email,))
        dipendente_id = cursor.fetchone()[0]
        cursor.execute('SELECT orario1_entrata, orario2_entrata, orario1_uscita FROM presenze WHERE id = %s AND data_presenza = %s', (dipendente_id, data_presenza))
        presenze = cursor.fetchone()
        if presenze:
            orario1_entrata, orario2_entrata, orario1_uscita = presenze
            if orario1_entrata is not None and orario2_entrata is not None:
                flash('Entrambe le entrate per oggi sono già state inserite.', 'error')
            elif orario1_entrata is not None and orario1_uscita is None:
                flash('Devi registrare l\'uscita prima di poter inserire una seconda entrata.', 'error')
            elif orario1_entrata is not None:
                cursor.execute('UPDATE presenze SET orario2_entrata = %s WHERE id = %s AND data_presenza = %s', (orario_entrata, dipendente_id, data_presenza))
                flash('Secondo orario di entrata inserito con successo.', 'success')
            else:
                cursor.execute('UPDATE presenze SET orario1_entrata = %s WHERE id = %s AND data_presenza = %s', (orario_entrata, dipendente_id, data_presenza))
                flash('Primo orario di entrata inserito con successo.', 'success')
        else:
            cursor.execute('INSERT INTO presenze (id, data_presenza, orario1_entrata) VALUES (%s, %s, %s)', (dipendente_id, data_presenza, orario_entrata))
            flash('Primo orario di entrata inserito con successo.', 'success')
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/aggiungi_uscita', methods=['POST'])
def aggiungi_uscita():
    if 'loggedin' in session:
        email = session['email']
        data_presenza = request.form['data_presenza']
        orario_uscita = request.form['orario_uscita']
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM dipendenti WHERE email = %s', (email,))
        dipendente_id = cursor.fetchone()[0]
        cursor.execute('SELECT orario1_uscita, orario2_uscita, orario1_entrata, orario2_entrata FROM presenze WHERE id = %s AND data_presenza = %s', (dipendente_id, data_presenza))
        presenze = cursor.fetchone()
        if presenze:
            orario1_uscita, orario2_uscita, orario1_entrata, orario2_entrata = presenze
            if orario1_uscita is not None and orario2_uscita is not None:
                flash('Entrambe le uscite per oggi sono già state inserite.', 'error')
            elif orario1_entrata is None:
                flash('Devi registrare l\'entrata prima di poter inserire un\'uscita.', 'error')
            elif orario1_uscita is not None and orario2_entrata is None:
                flash('Devi registrare la seconda entrata prima di poter inserire una seconda uscita.', 'error')
            elif orario1_uscita is not None:
                cursor.execute('UPDATE presenze SET orario2_uscita = %s WHERE id = %s AND data_presenza = %s', (orario_uscita, dipendente_id, data_presenza))
                flash('Secondo orario di uscita inserito con successo.', 'success')
            else:
                cursor.execute('UPDATE presenze SET orario1_uscita = %s WHERE id = %s AND data_presenza = %s', (orario_uscita, dipendente_id, data_presenza))
                flash('Primo orario di uscita inserito con successo.', 'success')
        else:
            flash('Devi registrare un\'entrata prima di poter inserire un\'uscita.', 'error')
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/toggle_pausa', methods=['POST'])
def toggle_pausa():
    global pause_start_time

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    email = session.get('email')
    if not email:
        flash('Nessun utente loggato!', 'error')
        cursor.close()
        conn.close()
        return redirect(url_for('home'))

    today_date = datetime.datetime.now().date()

    # Recupera l'ID del dipendente
    cursor.execute('SELECT id FROM dipendenti WHERE email = %s', (email,))
    dipendente = cursor.fetchone()
    if not dipendente:
        flash('Dipendente non trovato!')
        cursor.close()
        conn.close()
        return redirect(url_for('home'))

    dipendente_id = dipendente[0]  # Usa l'indice 0 per accedere all'ID

    if pause_start_time is None:
        # Controlla se è già stata registrata l'entrata e verifica gli orari
        cursor.execute('''
            SELECT orario1_entrata, orario1_uscita, orario2_entrata, orario2_uscita
            FROM presenze
            WHERE id = %s AND data_presenza = %s
            ''', (dipendente_id, today_date))
        presenze = cursor.fetchone()

        if presenze:
            orario1_entrata, orario1_uscita, orario2_entrata, orario2_uscita = presenze
            
            # Condizioni per permettere la pausa
            if orario1_entrata is None:
                flash('Devi registrare l\'entrata del primo turno prima di iniziare la pausa!', 'error')
                cursor.close()
                conn.close()
                return redirect(url_for('home'))
            
            if orario1_uscita is not None and orario2_entrata is None:
                flash('Devi registrare l\'entrata del secondo turno prima di iniziare la pausa!', 'error')
                cursor.close()
                conn.close()
                return redirect(url_for('home'))

            if orario2_uscita is not None:
                flash('La pausa non può essere registrata dopo la seconda uscita!', 'error')
                cursor.close()
                conn.close()
                return redirect(url_for('home'))

            # Inizio pausa
            pause_start_time = datetime.datetime.now()
            flash('Pausa iniziata!', 'success')
        else:
            flash('Nessuna registrazione di presenza trovata per oggi!', 'error')
    
    else:
        # Fine pausa
        pausa_end_time = datetime.datetime.now()
        pausa_duration = (pausa_end_time - pause_start_time).total_seconds() / 60
        
        if pausa_duration < 1:
            flash('Non puoi fermare la pausa prima di 1 minuto. Attendi un minuto per fermare la pausa.', 'error')
            # Mantieni la pausa avviata
            cursor.close()
            conn.close()
            return redirect(url_for('home'))
        
        pause_start_time = None

        # Aggiorna la pausa nel database
        cursor.execute('''
            UPDATE presenze
            SET orario_pausa = COALESCE(orario_pausa, 0) + %s
            WHERE id = %s AND data_presenza = %s
            ''', (pausa_duration, dipendente_id, today_date))
        conn.commit()
        flash('Pausa terminata e registrata!', 'success')

    cursor.close()
    conn.close()
    return redirect(url_for('home'))
    
    
@app.route('/aggiungi_orario_straordinario_inizio', methods=['POST'])
def aggiungi_orario_straordinario_inizio():
    if 'loggedin' in session:
        email = session['email']
        data_presenza = request.form['data_presenza']
        orario_inizio_straordinario = datetime.datetime.now().strftime('%H:%M')
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Recupera l'ID del dipendente
        cursor.execute('SELECT id FROM dipendenti WHERE email = %s', (email,))
        dipendente_id = cursor.fetchone()[0]

        # Verifica se esiste una registrazione per il giorno specificato
        cursor.execute('SELECT orario1_entrata, orario1_uscita, orario2_entrata, orario2_uscita, orario_inizio_straordinario FROM presenze WHERE id = %s AND data_presenza = %s', (dipendente_id, data_presenza))
        presenze = cursor.fetchone()

        if presenze:
            orario1_entrata, orario1_uscita, orario2_entrata, orario2_uscita, orario_inizio = presenze

            if orario_inizio is not None:
                flash('Orario di inizio straordinario già registrato per oggi.', 'error')
            elif orario1_entrata is None:
                flash('Devi registrare l\'entrata 1 prima di poter aggiungere l\'orario straordinario.', 'error')
            elif orario1_uscita is None and orario2_entrata is None:
                flash('Devi registrare l\'uscita 1 o l\'entrata 2 prima di poter aggiungere l\'orario straordinario.', 'error')
            elif orario2_uscita is None and orario1_uscita is not None:
                flash('Devi registrare l\'uscita 2 prima di poter aggiungere l\'orario straordinario.', 'error')
            else:
                cursor.execute('UPDATE presenze SET orario_inizio_straordinario = %s WHERE id = %s AND data_presenza = %s', (orario_inizio_straordinario, dipendente_id, data_presenza))
                flash('Orario di inizio straordinario inserito con successo.', 'success')
        else:
            cursor.execute('INSERT INTO presenze (id, data_presenza, orario_inizio_straordinario) VALUES (%s, %s, %s)', (dipendente_id, data_presenza, orario_inizio_straordinario))
            flash('Orario di inizio straordinario inserito con successo.', 'success')

        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('home'))
    return redirect(url_for('login'))



@app.route('/aggiungi_orario_straordinario_fine', methods=['POST'])
def aggiungi_orario_straordinario_fine():
    if 'loggedin' in session:
        email = session['email']
        data_presenza = request.form['data_presenza']
        orario_fine_straordinario = datetime.datetime.now().strftime('%H:%M')
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Recupera l'ID del dipendente
        cursor.execute('SELECT id FROM dipendenti WHERE email = %s', (email,))
        dipendente_id = cursor.fetchone()[0]

        # Verifica se esiste una registrazione per il giorno specificato
        cursor.execute('SELECT orario_inizio_straordinario, orario_fine_straordinario, orario1_entrata, orario1_uscita, orario2_entrata, orario2_uscita FROM presenze WHERE id = %s AND data_presenza = %s', (dipendente_id, data_presenza))
        presenze = cursor.fetchone()

        if presenze:
            orario_inizio, orario_fine, orario1_entrata, orario1_uscita, orario2_entrata, orario2_uscita = presenze

            if orario_fine is not None:
                flash('Orario di fine straordinario già registrato per oggi.', 'error')
            elif orario_inizio is None:
                flash('Devi prima registrare l\'orario di inizio straordinario.', 'error')
            elif orario1_entrata is None and orario_inizio is not None:
                # Permetti l'inserimento di orario_fine_straordinario anche se orario1_entrata non è registrato
                cursor.execute('UPDATE presenze SET orario_fine_straordinario = %s WHERE id = %s AND data_presenza = %s', (orario_fine_straordinario, dipendente_id, data_presenza))
                flash('Orario di fine straordinario inserito con successo.', 'success')
            elif orario1_entrata is None:
                flash('Devi registrare l\'entrata 1 prima di poter aggiungere l\'orario di fine straordinario.', 'error')
            elif orario1_uscita is None and orario2_entrata is None:
                flash('Devi registrare l\'uscita 1 o l\'entrata 2 prima di poter aggiungere l\'orario di fine straordinario.', 'error')
            elif orario2_uscita is None and orario1_uscita is not None:
                flash('Devi registrare l\'uscita 2 prima di poter aggiungere l\'orario di fine straordinario.', 'error')
            else:
                cursor.execute('UPDATE presenze SET orario_fine_straordinario = %s WHERE id = %s AND data_presenza = %s', (orario_fine_straordinario, dipendente_id, data_presenza))
                flash('Orario di fine straordinario inserito con successo.', 'success')
        else:
            flash('Non hai registrato l\'orario di inizio straordinario per oggi.', 'error')

        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('home'))
    return redirect(url_for('login'))








if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=11000)
