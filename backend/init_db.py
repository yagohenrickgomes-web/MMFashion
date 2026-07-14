"""
Cria todas as tabelas no PostgreSQL e um usuário admin inicial.
Rode uma única vez: python init_db.py
"""
from app import create_app, bcrypt
from models import db, Funcionario

app = create_app()

with app.app_context():
    print('Criando tabelas...')
    db.create_all()
    print('Tabelas criadas com sucesso!')

    # Cria o admin padrão só se ainda não existir nenhum
    if not Funcionario.query.filter_by(email='admin@mmfashion.com.br').first():
        senha_hash = bcrypt.generate_password_hash('mudar123').decode('utf-8')
        admin = Funcionario(
            nome='Administrador',
            email='admin@mmfashion.com.br',
            senha_hash=senha_hash,
            cargo='Administradora',
            permissao='admin',
        )
        db.session.add(admin)
        db.session.commit()
        print('Admin criado -> email: admin@mmfashion.com.br | senha: mudar123')
        print('IMPORTANTE: troque essa senha depois!')
    else:
        print('Admin já existia, nada foi alterado.')
