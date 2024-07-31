INSERT INTO dipendenti (nome, cognome, cod_fisc, data_nascita, citta, provincia, via, email, telefono1, telefono2, tipologia_contratto, data_assunzione, scadenza_contratto, stipendio, ruolo, sede_azienda)
VALUES
('Mario', 'Rossi', 'RSSMRA80A01H501U', '1980-01-01', 'Milano', 'MI', 'Via Roma 1', 'mario.rossi@example.com', '1234567890', '0987654321', 'Tempo indeterminato', '2010-01-01', NULL, 3000, 'Manager', 'Milano'),
('Luigi', 'Verdi', 'VRDLGU85B02C352Y', '1985-02-02', 'Torino', 'TO', 'Corso Italia 2', 'luigi.verdi@example.com', '2345678901', '1098765432', 'Tempo determinato', '2015-02-02', '2025-02-02', 2500, 'Impiegato', 'Torino');


INSERT INTO login (email, credenziali_accesso)
VALUES
('mario.rossi@example.com', 'password123'),
('luigi.verdi@example.com', 'password456');

INSERT INTO dispositivi (dispositivo, srn_iccid, num_aziendale, data_acquisto, scad_garanzia, ram, archiviazione, processore, os, oper_telefonico, modello, stato, disponibilita, note)
VALUES
('Smartphone', '12345678901234567890', '12345', '2020-01-01', '2022-01-01', '4GB', '64GB', 'Snapdragon 855', 'Android', 'Vodafone', 'Samsung Galaxy S10', 'Nuovo', 'S', 'Nessuna nota'),
('Laptop', '09876543210987654321', '54321', '2019-05-05', '2021-05-05', '16GB', '512GB', 'Intel i7', 'Windows', 'TIM', 'Dell XPS 13', 'Usato', 'N', 'Nessuna nota');


INSERT INTO veicoli (marca, targa, tipologia, stato, KM, motorizzazione, colore, data_immatricolazione, porte, cv, scad_assicurazione, scad_revisione, ultimo_tagliando, disponibilita, note)
VALUES
('Fiat', 'AB123CD', 'Auto', 'Buono', 50000, 'Benzina', 'Bianco', '2018-03-03', 5, 100, '2023-03-03', '2024-03-03', '2023-01-01', 'S', 'Nessuna nota'),
('Ford', 'EF456GH', 'Furgone', 'Ottimo', 20000, 'Diesel', 'Blu', '2020-06-06', 3, 150, '2023-06-06', '2024-06-06', '2023-05-05', 'N', 'Nessuna nota');


INSERT INTO concessioni (id, srn_iccid, targa, data_inizio, data_fine)
VALUES
(1, '12345678901234567890', 'AB123CD', '2021-01-01', '2022-01-01'),
(2, '09876543210987654321', 'EF456GH', '2021-06-01', '2022-06-01');


INSERT INTO presenze (id, data_presenza, orario1_entrata, orario1_uscita, orario2_entrata, orario2_uscita)
VALUES
(1, '2024-07-15', '09:00:00', '13:00:00', '14:00:00', '18:00:00'),
(2, '2024-07-15', '08:30:00', '12:30:00', '13:30:00', '17:30:00');