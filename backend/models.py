from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# ============================================================
# CLIENTES (contas da loja)
# ============================================================
class Cliente(UserMixin, db.Model):
    __tablename__ = 'clientes'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(20))
    cpf = db.Column(db.String(14), unique=True)
    data_nascimento = db.Column(db.Date)
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    enderecos = db.relationship('Endereco', backref='cliente', cascade='all, delete-orphan')
    pedidos = db.relationship('Pedido', backref='cliente')
    favoritos = db.relationship('Favorito', backref='cliente', cascade='all, delete-orphan')

    def get_id(self):
        # Prefixo pra distinguir de Funcionario no Flask-Login (mesmo loader)
        return f'cliente-{self.id}'


class Endereco(db.Model):
    __tablename__ = 'enderecos'

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    apelido = db.Column(db.String(60))          # "Casa", "Trabalho"
    cep = db.Column(db.String(9))
    logradouro = db.Column(db.String(160))
    numero = db.Column(db.String(20))
    complemento = db.Column(db.String(80))
    bairro = db.Column(db.String(80))
    cidade = db.Column(db.String(80))
    estado = db.Column(db.String(2))
    principal = db.Column(db.Boolean, default=False)


# ============================================================
# CATÁLOGO
# ============================================================
class Categoria(db.Model):
    __tablename__ = 'categorias'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    categoria_pai_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=True)

    subcategorias = db.relationship('Categoria', backref=db.backref('pai', remote_side=[id]))
    produtos = db.relationship('Produto', backref='categoria')


class Produto(db.Model):
    __tablename__ = 'produtos'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(160), nullable=False)
    descricao = db.Column(db.Text)
    marca = db.Column(db.String(80))
    sku = db.Column(db.String(40), unique=True)
    codigo_barras = db.Column(db.String(40))

    preco = db.Column(db.Numeric(10, 2), nullable=False)
    preco_promocional = db.Column(db.Numeric(10, 2))
    peso_kg = db.Column(db.Numeric(6, 3))

    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'))
    fornecedor_id = db.Column(db.Integer, db.ForeignKey('fornecedores.id'))

    destaque = db.Column(db.Boolean, default=False)
    novo = db.Column(db.Boolean, default=False)
    em_promocao = db.Column(db.Boolean, default=False)
    ativo = db.Column(db.Boolean, default=True)

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    imagens = db.relationship('ImagemProduto', backref='produto', cascade='all, delete-orphan')
    variacoes = db.relationship('VariacaoProduto', backref='produto', cascade='all, delete-orphan')

    @property
    def estoque_total(self):
        return sum(v.quantidade for v in self.variacoes)


class ImagemProduto(db.Model):
    __tablename__ = 'imagens_produto'

    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    url = db.Column(db.String(300), nullable=False)
    principal = db.Column(db.Boolean, default=False)
    ordem = db.Column(db.Integer, default=0)


class VariacaoProduto(db.Model):
    """Cada combinação de cor/tamanho tem seu próprio estoque."""
    __tablename__ = 'variacoes_produto'

    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    cor = db.Column(db.String(40))
    tamanho = db.Column(db.String(10))
    sku_variacao = db.Column(db.String(50), unique=True)
    quantidade = db.Column(db.Integer, default=0)
    estoque_minimo = db.Column(db.Integer, default=5)


class Fornecedor(db.Model):
    __tablename__ = 'fornecedores'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(160), nullable=False)
    cnpj = db.Column(db.String(18))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(160))

    produtos = db.relationship('Produto', backref='fornecedor')


class Favorito(db.Model):
    __tablename__ = 'favoritos'

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('cliente_id', 'produto_id'),)


# ============================================================
# ESTOQUE
# ============================================================
class MovimentacaoEstoque(db.Model):
    __tablename__ = 'movimentacoes_estoque'

    id = db.Column(db.Integer, primary_key=True)
    variacao_id = db.Column(db.Integer, db.ForeignKey('variacoes_produto.id'), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)   # 'entrada' | 'saida'
    quantidade = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.String(160))                 # "Compra fornecedor", "Venda", "Ajuste"
    responsavel_id = db.Column(db.Integer, db.ForeignKey('funcionarios.id'))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    variacao = db.relationship('VariacaoProduto')


# ============================================================
# PEDIDOS / VENDAS
# ============================================================
class Pedido(db.Model):
    __tablename__ = 'pedidos'

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), unique=True, nullable=False)  # ex: MMF-2481
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    endereco_id = db.Column(db.Integer, db.ForeignKey('enderecos.id'))

    status = db.Column(db.String(20), default='processando')
    # processando | pago | em_transito | entregue | cancelado

    forma_pagamento = db.Column(db.String(30))    # pix, cartao, boleto
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    frete = db.Column(db.Numeric(10, 2), default=0)
    desconto = db.Column(db.Numeric(10, 2), default=0)
    total = db.Column(db.Numeric(10, 2), nullable=False)

    cupom_id = db.Column(db.Integer, db.ForeignKey('cupons.id'), nullable=True)
    codigo_rastreio = db.Column(db.String(60))
    transportadora = db.Column(db.String(60))

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    itens = db.relationship('ItemPedido', backref='pedido', cascade='all, delete-orphan')


class ItemPedido(db.Model):
    __tablename__ = 'itens_pedido'

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    variacao_id = db.Column(db.Integer, db.ForeignKey('variacoes_produto.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Numeric(10, 2), nullable=False)  # preço no momento da compra

    variacao = db.relationship('VariacaoProduto')


class Cupom(db.Model):
    __tablename__ = 'cupons'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(30), unique=True, nullable=False)
    tipo = db.Column(db.String(10), nullable=False)   # 'percentual' | 'valor'
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    validade = db.Column(db.Date)
    uso_maximo = db.Column(db.Integer)
    usos = db.Column(db.Integer, default=0)
    ativo = db.Column(db.Boolean, default=True)

    pedidos = db.relationship('Pedido', backref='cupom')


# ============================================================
# ADMINISTRATIVO / FUNCIONÁRIOS
# ============================================================
class Funcionario(UserMixin, db.Model):
    __tablename__ = 'funcionarios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    cargo = db.Column(db.String(60))
    permissao = db.Column(db.String(20), default='usuario')  # 'admin' | 'usuario'
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def get_id(self):
        return f'funcionario-{self.id}'


class LancamentoFinanceiro(db.Model):
    __tablename__ = 'financeiro'

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(10), nullable=False)  # 'receita' | 'despesa'
    categoria = db.Column(db.String(60))              # "Venda", "Frete", "Fornecedor", "Marketing"
    descricao = db.Column(db.String(200))
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    data = db.Column(db.Date, default=datetime.utcnow)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=True)
