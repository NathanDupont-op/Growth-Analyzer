FROM python:3.9

WORKDIR /code

# 1. Copie des fichiers et installation des librairies Python
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 2. Installation des navigateurs ET des dépendances système (La clé du succès)
RUN playwright install --with-deps chromium

# 3. Copie du reste du code
COPY . /code

# 4. Lancement de l'app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
