Instalation guide 

1 Install requirments.txt pip install -r requirments.txt

2 create database in your database management system

3 Create .env file and add (DB_HOST, DB_PORT DB_USER, DB_PASS, DB_NAME, SECRET_KEY)

DBHOST - Host of your db - for local localhost
DB_PORT - Port of your db for postgresql - 5432
DB_USER - admin of db username
DB_PASS - admin of db password
DB_NAME - name of db you created before
SECRET_KEY - Key for crypting tokens( best practice use code which created on console with this command openssl rand -hex 32)

4 add alembic alembic init -t async alembic
  add initial migration alembic revision --autogenerate -m 'initial' and upgrade head alembic upgrade head
  in alembic .env add 
  from app.api.database.db_models import Base
  target_metadata = Base.metadata 
