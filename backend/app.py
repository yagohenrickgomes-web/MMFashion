import os
import os
import re
from flask import Flask, jsonify, request, send_from_directory, redirect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from email_validator import validate_email, EmailNotValidError

from config import Config
from models import db, Cliente, Funcionario

bcrypt = Bcrypt()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address)

# Pasta raiz do projeto (uma acima de /backend) onde ficam index.html, /pages e /admin
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def senha_forte(senha):
    """Mínimo 8 caracteres, com letra e número. Retorna (ok, mensagem)."""
    if len(senha) < 8:
        return False, 'A senha precisa ter no mínimo 8 caracteres.'
    if not re.search(r'[A-Za-z]', senha) or not re.search(r'\d', senha):
        return False, 'A senha precisa ter letras e números.'
    return True, ''


def create_app():
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
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

    @app.route('/googlebb48457dd932da18.html')
    def google_site_verification():
        return send_from_directory(FRONTEND_DIR, 'googlebb48457dd932da18.html')

    # ============================================================
    # URLS LIMPAS (sem expor a estrutura de pastas /pages e /admin)
    # ============================================================
    @app.route('/login')
    def login_page():
        return send_from_directory(os.path.join(FRONTEND_DIR, 'pages'), 'login.html')

    @app.route('/carrinho')
    def carrinho_page():
        return send_from_directory(os.path.join(FRONTEND_DIR, 'pages'), 'carrinho.html')

    @app.route('/produto')
    def produto_page():
        return send_from_directory(os.path.join(FRONTEND_DIR, 'pages'), 'produto.html')

    @app.route('/admin')
    @app.route('/admin/')
    def admin_home():
        if not current_user.is_authenticated or not isinstance(current_user._get_current_object(), Funcionario):
            return redirect('/login?admin=1')
        return send_from_directory(os.path.join(FRONTEND_DIR, 'admin'), 'painel-admin.html')

    @app.route('/admin/produtos')
    def admin_produtos_page():
        if not current_user.is_authenticated or not isinstance(current_user._get_current_object(), Funcionario):
            return redirect('/login?admin=1')
        return send_from_directory(os.path.join(FRONTEND_DIR, 'admin'), 'produtos-admin.html')

    # Demais módulos do painel (todos exigem sessão de funcionário)
    _ADMIN_SUBPAGES = {
        'pedidos': 'pedidos.html',
        'categorias': 'categorias.html',
        'clientes': 'clientes.html',
        'estoque': 'estoque.html',
        'financeiro': 'financeiro.html',
        'relatorios': 'relatorios.html',
        'cupons': 'cupons.html',
        'funcionarios': 'funcionarios.html',
        'configuracoes': 'configuracoes.html',
    }

    def _make_admin_subpage_view(filename):
        def view():
            if not current_user.is_authenticated or not isinstance(current_user._get_current_object(), Funcionario):
                return redirect('/login?admin=1')
            return send_from_directory(os.path.join(FRONTEND_DIR, 'admin'), filename)
        return view

    for _slug, _filename in _ADMIN_SUBPAGES.items():
        app.add_url_rule(f'/admin/{_slug}', endpoint=f'admin_{_slug}', view_func=_make_admin_subpage_view(_filename))

    @app.route('/pages/<path:filename>')
    def pages(filename):
        return send_from_directory(os.path.join(FRONTEND_DIR, 'pages'), filename)

    @app.route('/admin/<path:filename>')
    def admin_pages(filename):
        # Todo o painel exige sessão de FUNCIONÁRIO autenticado.
        # Sem sessão válida, manda pra tela de login única (pages/login.html) —
        # não existe mais uma URL de login "escondida" só pro admin.
        if not current_user.is_authenticated or not isinstance(current_user._get_current_object(), Funcionario):
            return redirect('/pages/login.html?admin=1')

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
    # DIAGNÓSTICO TEMPORÁRIO — remova esta rota depois de confirmar
    # que o app está conectado no banco certo (não expõe senha).
    # ============================================================
    @app.route('/api/db-check')
    def db_check():
        from sqlalchemy import inspect
        try:
            insp = inspect(db.engine)
            tabelas = insp.get_table_names()
        except Exception as e:
            return jsonify({'erro': str(e)}), 500

        uri = app.config['SQLALCHEMY_DATABASE_URI']
        host_visivel = uri.split('@')[-1] if '@' in uri else uri  # esconde usuário/senha
        return jsonify({'conectado_em': host_visivel, 'tabelas_encontradas': tabelas})

    @app.route('/api/login', methods=['POST'])
    @limiter.limit('8 per minute')
    def login_unificado():
        """
        Login único usado pela tela pages/login.html.
        Primeiro verifica se o e-mail pertence a um FUNCIONÁRIO (admin/equipe);
        se não for, verifica se pertence a um CLIENTE da loja.
        Nunca existe cruzamento entre as duas tabelas — são contas completamente separadas.
        """
        data = request.get_json(silent=True) or {}
        email = (data.get('email') or '').strip().lower()
        senha = data.get('senha') or ''
        lembrar = bool(data.get('lembrar'))

        # 1) Tenta como FUNCIONÁRIO (equipe / administrativo)
        func = Funcionario.query.filter_by(email=email).first()
        if func and bcrypt.check_password_hash(func.senha_hash, senha):
            if not func.ativo:
                return jsonify({'erro': 'Este usuário está desativado.'}), 403
            login_user(func, remember=lembrar)
            return jsonify({
                'mensagem': 'Login realizado!',
                'nome': func.nome,
                'tipo': 'funcionario',
                'redirect': '/admin',
            })

        # 2) Tenta como CLIENTE (loja)
        cliente = Cliente.query.filter_by(email=email).first()
        if cliente and bcrypt.check_password_hash(cliente.senha_hash, senha):
            if not cliente.ativo:
                return jsonify({'erro': 'Esta conta está desativada. Fale com o suporte.'}), 403
            login_user(cliente, remember=lembrar)
            return jsonify({
                'mensagem': 'Login realizado!',
                'nome': cliente.nome,
                'tipo': 'cliente',
                'redirect': '/',
            })

        # Mesma mensagem pros dois casos — não dá pra descobrir se o e-mail existe ou não
        return jsonify({'erro': 'E-mail ou senha inválidos.'}), 401

    # ============================================================
    # AUTENTICAÇÃO — CLIENTES (loja) — cadastro continua separado do admin
    # ============================================================
    @app.route('/api/clientes/cadastro', methods=['POST'])
    @limiter.limit('5 per minute')  # evita bots criando várias contas em sequência
    def cadastro_cliente():
        data = request.get_json(silent=True) or {}
        nome = (data.get('nome') or '').strip()
        telefone = (data.get('telefone') or '').strip()
        email = (data.get('email') or '').strip().lower()
        senha = data.get('senha') or ''

        if not nome or len(nome) < 2:
            return jsonify({'erro': 'Informe seu nome completo.'}), 400
        if not telefone or len(re.sub(r'\D', '', telefone)) < 10:
            return jsonify({'erro': 'Informe um telefone válido com DDD.'}), 400

        try:
            email_info = validate_email(email, check_deliverability=False)
            email = email_info.normalized
        except EmailNotValidError:
            return jsonify({'erro': 'Informe um e-mail válido.'}), 400

        ok, msg = senha_forte(senha)
        if not ok:
            return jsonify({'erro': msg}), 400

        if Cliente.query.filter_by(email=email).first():
            return jsonify({'erro': 'Este e-mail já está cadastrado.'}), 400

        senha_hash = bcrypt.generate_password_hash(senha).decode('utf-8')
        cliente = Cliente(nome=nome, email=email, senha_hash=senha_hash, telefone=telefone)
        db.session.add(cliente)
        db.session.commit()
        return jsonify({'mensagem': 'Conta criada com sucesso!'}), 201

    @app.route('/api/clientes/login', methods=['POST'])
    @limiter.limit('8 per minute')  # trava tentativas de força bruta na senha
    def login_cliente():
        data = request.get_json(silent=True) or {}
        email = (data.get('email') or '').strip().lower()
        senha = data.get('senha') or ''

        cliente = Cliente.query.filter_by(email=email).first()

        # Mesma mensagem de erro pra e-mail inexistente ou senha errada —
        # evita que alguém descubra quais e-mails têm conta na loja
        if not cliente or not bcrypt.check_password_hash(cliente.senha_hash, senha):
            return jsonify({'erro': 'E-mail ou senha inválidos.'}), 401

        if not cliente.ativo:
            return jsonify({'erro': 'Esta conta está desativada. Fale com o suporte.'}), 403

        login_user(cliente, remember=bool(data.get('lembrar')))
        return jsonify({'mensagem': 'Login realizado!', 'nome': cliente.nome})

    # ============================================================
    # AUTENTICAÇÃO — PAINEL ADMINISTRATIVO
    # ============================================================
    @app.route('/api/admin/login', methods=['POST'])
    @limiter.limit('8 per minute')
    def login_admin():
        data = request.get_json(silent=True) or {}
        email = (data.get('email') or '').strip().lower()
        senha = data.get('senha') or ''

        func = Funcionario.query.filter_by(email=email).first()

        if not func or not bcrypt.check_password_hash(func.senha_hash, senha):
            return jsonify({'erro': 'E-mail ou senha inválidos.'}), 401

        if not func.ativo:
            return jsonify({'erro': 'Este usuário está desativado.'}), 403

        login_user(func, remember=bool(data.get('lembrar')))
        return jsonify({'mensagem': 'Login realizado!', 'nome': func.nome, 'permissao': func.permissao})

    @app.route('/api/logout', methods=['POST'])
    @login_required
    def logout():
        logout_user()
        return jsonify({'mensagem': 'Sessão encerrada.'})

    @app.route('/api/me')
    def me():
        if current_user.is_authenticated:
            tipo = 'funcionario' if isinstance(current_user._get_current_object(), Funcionario) else 'cliente'
            return jsonify({'autenticado': True, 'nome': current_user.nome, 'tipo': tipo})
        return jsonify({'autenticado': False})

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
