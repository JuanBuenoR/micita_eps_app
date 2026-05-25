cd micita_eps_app
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations accounts citas
python manage.py migrate
python populate_synthetic_data.py
python manage.py runserver
