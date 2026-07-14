import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    # Postgres local (mesmo padrão do projeto SagaCap Contratos)
    DB_USER = os.environ.get('DB_USER', 'postgres')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    DB_NAME = os.environ.get('DB_NAME', 'mmfashion')

    # Railway (e Heroku) às vezes fornecem DATABASE_URL vazia (variável existe mas sem valor,
    # quando a referência ao Postgres ainda não resolveu) ou no formato antigo "postgres://",
    # que o SQLAlchemy 2.x não aceita. Tratamos os dois casos aqui.
    _database_url = (os.environ.get('DATABASE_URL') or '').strip()
    if _database_url.startswith('postgres://'):
        _database_url = _database_url.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_DATABASE_URI = _database_url or (
        f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.environ.get('SECRET_KEY', 'troque-esta-chave-em-producao')

    # ============================================================
    # SEGURANÇA DE SESSÃO / COOKIES
    # ============================================================
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 7  # 7 dias ("lembrar de mim")
    SESSION_COOKIE_HTTPONLY = True                  # JS não consegue ler o cookie de sessão
    SESSION_COOKIE_SAMESITE = 'Lax'                 # protege contra CSRF básico
    # Em produção (HTTPS no Render) o cookie só trafega criptografado.
    # Em localhost (sem HTTPS) isso ficaria False pra não quebrar o teste.
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'

    # Limite de tentativas de login (proteção contra força bruta)
    RATELIMIT_STORAGE_URI = 'memory://'
