# Usa l'immagine base di Python
FROM python:3.9

# Imposta la directory di lavoro
WORKDIR /app

# Copia i file requirements.txt e installa le dipendenze
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia il resto del codice dell'app
COPY . .

# Espone la porta su cui Flask sarà in esecuzione
EXPOSE 5000

# Comando per eseguire l'applicazione
CMD ["python", "appAsset_request.py"]
