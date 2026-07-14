"""
Cria todas as tabelas no PostgreSQL e os dois usuários administrativos iniciais:
Melissa (proprietária) e Yago (desenvolvedor).

Rode uma única vez: python init_db.py

IMPORTANTE: as senhas abaixo são temporárias. Troque assim que possível.
"""
from app import create_app, bcrypt
from models import db, Funcionario

app = create_app()

# Senhas iniciais temporárias — troque após o primeiro login de cada uma.
ADMINS = [
    {
        'nome': 'Melissa Mel',
        'email': 'melissa@mmfashion.com.br',
        'senha': 'Melissa@2026',
        'cargo': 'Proprietária',
    },
    {
        'nome': 'Yago Gomes',
        'email': 'yago@mmfashion.com.br',
        'senha': 'YagoGomes@2026',
        'cargo': 'Desenvolvedor',
    },
]

with app.app_context():
    print('Criando tabelas...')
    db.create_all()
    print('Tabelas criadas com sucesso!')

    for dados in ADMINS:
        existente = Funcionario.query.filter_by(email=dados['email']).first()
        if existente:
            print(f"Já existe conta para {dados['email']}, nada foi alterado.")
            continue

        senha_hash = bcrypt.generate_password_hash(dados['senha']).decode('utf-8')
        func = Funcionario(
            nome=dados['nome'],
            email=dados['email'],
            senha_hash=senha_hash,
            cargo=dados['cargo'],
            permissao='admin',
        )
        db.session.add(func)
        db.session.commit()
        print(f"Conta criada -> {dados['nome']} | {dados['email']} | senha temporária: {dados['senha']}")

    print('\nIMPORTANTE: troque essas senhas assim que possível!')
