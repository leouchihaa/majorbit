# Usa un'immagine base Python
FROM python:3.12

# Imposta la directory di lavoro
WORKDIR /app

# Copia i file requirements.txt e installa le dipendenze
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copia il resto del codice dell'applicazione
COPY . /app

# Espone la porta
EXPOSE 5000

# Comando per avviare l'applicazione
CMD ["python", "AppAsset1.py"]