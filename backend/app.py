import os
from flask import Flask, jsonify, request, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_cors import CORS

from config import Config
from models import db, Cliente, Funcionario

bcrypt = Bcrypt()
login_manager = LoginManager()

# Pasta raiz do projeto (uma acima de /backend) onde ficam index.html, /pages e /admin
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def create_app():
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    CORS(app, supports_credentials=True)

    @login_manager.user_loader
    def load_user(user_id):
        tipo, real_id = user_id.split('-')
        if tipo == 'cliente':
            return Cliente.query.get(int(real_id))
        if tipo == 'funcionario':
            return Funcionario.query.get(int(real_id))
        return None

    # ============================================================
    # FRONT-END ESTÁTICO (index.html, /pages, /admin, /assets)
    # ============================================================
    @app.route('/')
    def home():
        return send_from_directory(FRONTEND_DIR, 'index.html')

    @app.route('/pages/<path:filename>')
    def pages(filename):
        return send_from_directory(os.path.join(FRONTEND_DIR, 'pages'), filename)

    @app.route('/admin/<path:filename>')
    def admin_pages(filename):
        return send_from_directory(os.path.join(FRONTEND_DIR, 'admin'), filename)

    @app.route('/assets/<path:filename>')
    def assets(filename):
        return send_from_directory(os.path.join(FRONTEND_DIR, 'assets'), filename)

    # ============================================================
    # ROTA DE TESTE
    # ============================================================
    @app.route('/api/ping')
    def ping():
        return jsonify({'status': 'ok', 'message': 'MM Fashion API rodando 🚀'})

    # ============================================================
    # AUTENTICAÇÃO — CLIENTES (loja)
    # ============================================================
    @app.route('/api/clientes/cadastro', methods=['POST'])
    def cadastro_cliente():
        data = request.get_json()
        if Cliente.query.filter_by(email=data.get('email')).first():
            return jsonify({'erro': 'Este e-mail já está cadastrado.'}), 400

        senha_hash = bcrypt.generate_password_hash(data['senha']).decode('utf-8')
        cliente = Cliente(
            nome=data['nome'],
            email=data['email'],
            senha_hash=senha_hash,
            telefone=data.get('telefone'),
        )
        db.session.add(cliente)
        db.session.commit()
        return jsonify({'mensagem': 'Conta criada com sucesso!', 'id': cliente.id}), 201

    @app.route('/api/clientes/login', methods=['POST'])
    def login_cliente():
        data = request.get_json()
        cliente = Cliente.query.filter_by(email=data.get('email')).first()

        if cliente and bcrypt.check_password_hash(cliente.senha_hash, data.get('senha', '')):
            login_user(cliente, remember=data.get('lembrar', False))
            return jsonify({'mensagem': 'Login realizado!', 'nome': cliente.nome})

        return jsonify({'erro': 'E-mail ou senha inválidos.'}), 401

    # ============================================================
    # AUTENTICAÇÃO — PAINEL ADMINISTRATIVO
    # ============================================================
    @app.route('/api/admin/login', methods=['POST'])
    def login_admin():
        data = request.get_json()
        func = Funcionario.query.filter_by(email=data.get('email')).first()

        if func and func.ativo and bcrypt.check_password_hash(func.senha_hash, data.get('senha', '')):
            login_user(func, remember=data.get('lembrar', False))
            return jsonify({'mensagem': 'Login realizado!', 'nome': func.nome, 'permissao': func.permissao})

        return jsonify({'erro': 'E-mail ou senha inválidos.'}), 401

    @app.route('/api/logout', methods=['POST'])
    @login_required
    def logout():
        logout_user()
        return jsonify({'mensagem': 'Sessão encerrada.'})

    @app.route('/api/me')
    def me():
        if current_user.is_authenticated:
            return jsonify({'autenticado': True, 'nome': current_user.nome})
        return jsonify({'autenticado': False})

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
