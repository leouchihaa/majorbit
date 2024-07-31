Create database asset_managment;

use asset_managment;

create table dipendenti (
id int auto_increment primary key,
nome varchar(100) not null,
cognome varchar(100) not null,
cod_fisc varchar(100) not null unique,
data_nascita date not null,
citta varchar(100) not null,
provincia varchar(2) not null,
via varchar(100) not null,
email varchar(100) not null unique,
telefono1 varchar(100) not null unique,
telefono2 varchar(100),
tipologia_contratto varchar(100) not null,
data_assunzione date not null,
scadenza_contratto date,
stipendio int,
ruolo varchar(100) not null,
sede_azienda varchar(100) not null
);

create table login (
email varchar(100) not null,
credenziali_accesso varchar(100) not null
);

create table dispositivi (
    dispositivo varchar(100) not null,
    srn_iccid varchar(100) primary key not null unique, 
    num_aziendale varchar(100) unique,
    data_acquisto date,
    scad_garanzia date,
    ram varchar(100),
	archiviazione varchar(100),
    processore varchar(100),
    os varchar(100),
    oper_telefonico varchar(100),
    modello varchar(100),
    stato varchar(100),
    disponibilita varchar(1) not null,
    note varchar(255)
);

create table veicoli (
marca varchar(100) not null,
targa varchar(100) primary key not null unique,
tipologia varchar(100) not null,
stato varchar(100) not null,
KM int not null,
motorizzazione varchar(100) not null,
colore varchar(100) not null,
data_immatricolazione date not null,
porte int not null,
cv int not null,
scad_assicurazione date not null,
scad_revisione date not null,
ultimo_tagliando date not null,
disponibilita varchar(1) not null,
note varchar (255)
);

create table concessioni (
id int,
srn_iccid varchar(100),
targa varchar(100),
data_inizio date,
data_fine date
);

create table presenze (
id int,
data_presenza date not null,
orario1_entrata time,
orario1_uscita time,
orario2_entrata time,
orario2_uscita time
);

CREATE VIEW presenze_con_totale_ore AS
SELECT
    id,
    data_presenza,
    orario1_entrata,
    orario1_uscita,
    orario2_entrata,
    orario2_uscita,
    TIME_TO_SEC(TIMEDIFF(orario1_uscita, orario1_entrata)) / 3600 +
    TIME_TO_SEC(TIMEDIFF(orario2_uscita, orario2_entrata)) / 3600 AS totale_ore
FROM
    presenze;

#carattere utilizzato sempre e solo minuscolo;
#per la colonna "disponibilita" i caratteri devono essere y(si) o n(no) (un solo carattere a disposizione)

#è stata creata una view per il "totale_ore":
#SELECT dipendenti.id, dipendenti.nome, presenze.orario1_entrata, presenze.data_presenza, presenze_con_totale_ore.totale_ore FROM dipendenti
#INNER JOIN presenze ON presenze.id = dipendenti.idINNER JOIN presenze_con_totale_ore ON presenze_con_totale_ore.id = dipendenti.id AND presenze_con_totale_ore.data_presenza = presenze.data_presenza
#WHERE presenze.data_presenza BETWEEN '2000-01-01' AND '2050-01-01';

#si raccomanda, in fase di sviluppo dell'applicativo, durante l'inserimento dati attraverso le query (es. python) si ricorda di inserirli anche alle tabelle connesse (es. dipendenti.email = login.email)
