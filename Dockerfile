
# Python-nıń jeńil versiyasınan paydalanamız
FROM python:3.10-slim

# Konteyner ishinde islew papkasın ornatamız
WORKDIR /app

# Kitapxanalar dizimin kóshirip, olardı ornatamız
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Barlıq backend faylların konteynerge kóshiremiz
COPY . .

# Google Cloud Run ushın port
ENV PORT=8080

# Dástúrdi Gunicorn járdeminde iske túsiremiz (Tiykarǵı app.py faylına qarap)
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
