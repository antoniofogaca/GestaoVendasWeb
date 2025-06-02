from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class Empresa(db.Model):
    __tablename__ = 'empresas'
    
    id = db.Column(db.Integer, primary_key=True)
    cnpj = db.Column(db.String(18), unique=True, nullable=False)
    razao_social = db.Column(db.String(200), nullable=False)
    nome_fantasia = db.Column(db.String(200))
    endereco = db.Column(db.String(200))
    cidade = db.Column(db.String(100))
    uf = db.Column(db.String(2))
    cep = db.Column(db.String(10))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    ativa = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    usuarios = db.relationship('Usuario', backref='empresa_rel', lazy=True)
    produtos = db.relationship('Produto', backref='empresa_rel', lazy=True)
    clientes = db.relationship('Cliente', backref='empresa_rel', lazy=True)
    fornecedores = db.relationship('Fornecedor', backref='empresa_rel', lazy=True)
    vendedores = db.relationship('Vendedor', backref='empresa_rel', lazy=True)
    vendas = db.relationship('Venda', backref='empresa_rel', lazy=True)
    
    def __repr__(self):
        return f'<Empresa {self.razao_social}>'

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    nome_completo = db.Column(db.String(200))
    ativo = db.Column(db.Boolean, default=True)
    admin = db.Column(db.Boolean, default=False)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Permissões
    perm_vendas = db.Column(db.Boolean, default=True)
    perm_produtos = db.Column(db.Boolean, default=True)
    perm_clientes = db.Column(db.Boolean, default=True)
    perm_fornecedores = db.Column(db.Boolean, default=False)
    perm_financeiro = db.Column(db.Boolean, default=False)
    perm_relatorios = db.Column(db.Boolean, default=False)
    perm_caixa = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Usuario {self.username}>'

class Produto(db.Model):
    __tablename__ = 'produtos'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50))
    nome = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    preco_custo = db.Column(db.Numeric(10, 2), default=0)
    preco_venda = db.Column(db.Numeric(10, 2), nullable=False)
    estoque_atual = db.Column(db.Integer, default=0)
    estoque_minimo = db.Column(db.Integer, default=0)
    unidade = db.Column(db.String(10), default='UN')
    categoria = db.Column(db.String(100))
    ativo = db.Column(db.Boolean, default=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Produto {self.nome}>'

class Cliente(db.Model):
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(10), default='PF')  # PF ou PJ
    cpf_cnpj = db.Column(db.String(18))
    nome = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120))
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.String(200))
    cidade = db.Column(db.String(100))
    uf = db.Column(db.String(2))
    cep = db.Column(db.String(10))
    observacoes = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    vendas = db.relationship('Venda', backref='cliente_rel', lazy=True)
    
    def __repr__(self):
        return f'<Cliente {self.nome}>'

class Fornecedor(db.Model):
    __tablename__ = 'fornecedores'
    
    id = db.Column(db.Integer, primary_key=True)
    cnpj = db.Column(db.String(18))
    razao_social = db.Column(db.String(200), nullable=False)
    nome_fantasia = db.Column(db.String(200))
    contato = db.Column(db.String(100))
    email = db.Column(db.String(120))
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.String(200))
    cidade = db.Column(db.String(100))
    uf = db.Column(db.String(2))
    cep = db.Column(db.String(10))
    observacoes = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Fornecedor {self.razao_social}>'

class Vendedor(db.Model):
    __tablename__ = 'vendedores'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120))
    telefone = db.Column(db.String(20))
    comissao_percentual = db.Column(db.Numeric(5, 2), default=0)
    ativo = db.Column(db.Boolean, default=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    vendas = db.relationship('Venda', backref='vendedor_rel', lazy=True)
    
    def __repr__(self):
        return f'<Vendedor {self.nome}>'

class Venda(db.Model):
    __tablename__ = 'vendas'
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), nullable=False)
    data_venda = db.Column(db.DateTime, default=datetime.utcnow)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    vendedor_id = db.Column(db.Integer, db.ForeignKey('vendedores.id'))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    
    # Valores
    subtotal = db.Column(db.Numeric(10, 2), default=0)
    desconto = db.Column(db.Numeric(10, 2), default=0)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Status e forma de pagamento
    status = db.Column(db.String(20), default='FINALIZADA')  # PENDENTE, FINALIZADA, CANCELADA
    forma_pagamento = db.Column(db.String(50))  # DINHEIRO, CARTAO, PIX, etc
    observacoes = db.Column(db.Text)
    
    # Relacionamentos
    itens = db.relationship('ItemVenda', backref='venda_rel', lazy=True, cascade='all, delete-orphan')
    usuario = db.relationship('Usuario', backref='vendas_usuario')
    
    def __repr__(self):
        return f'<Venda {self.numero}>'

class ItemVenda(db.Model):
    __tablename__ = 'itens_venda'
    
    id = db.Column(db.Integer, primary_key=True)
    venda_id = db.Column(db.Integer, db.ForeignKey('vendas.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    desconto_item = db.Column(db.Numeric(10, 2), default=0)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Relacionamentos
    produto = db.relationship('Produto', backref='itens_venda')
    
    def __repr__(self):
        return f'<ItemVenda {self.produto.nome if self.produto else "N/A"}>'

class MovimentoCaixa(db.Model):
    __tablename__ = 'movimentos_caixa'
    
    id = db.Column(db.Integer, primary_key=True)
    data_movimento = db.Column(db.DateTime, default=datetime.utcnow)
    tipo = db.Column(db.String(10), nullable=False)  # ENTRADA, SAIDA
    categoria = db.Column(db.String(50))  # VENDA, PAGAMENTO, RECEBIMENTO, etc
    descricao = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    venda_id = db.Column(db.Integer, db.ForeignKey('vendas.id'))  # Se for movimento de venda
    
    # Relacionamentos
    usuario = db.relationship('Usuario', backref='movimentos_caixa')
    venda = db.relationship('Venda', backref='movimentos_caixa')
    
    def __repr__(self):
        return f'<MovimentoCaixa {self.descricao}>'

class ContaPagar(db.Model):
    __tablename__ = 'contas_pagar'
    
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    fornecedor_id = db.Column(db.Integer, db.ForeignKey('fornecedores.id'))
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    data_vencimento = db.Column(db.Date, nullable=False)
    data_pagamento = db.Column(db.Date)
    status = db.Column(db.String(20), default='PENDENTE')  # PENDENTE, PAGA, VENCIDA
    observacoes = db.Column(db.Text)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    fornecedor = db.relationship('Fornecedor', backref='contas_pagar')
    
    def __repr__(self):
        return f'<ContaPagar {self.descricao}>'

class ContaReceber(db.Model):
    __tablename__ = 'contas_receber'
    
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    data_vencimento = db.Column(db.Date, nullable=False)
    data_recebimento = db.Column(db.Date)
    status = db.Column(db.String(20), default='PENDENTE')  # PENDENTE, RECEBIDA, VENCIDA
    observacoes = db.Column(db.Text)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    venda_id = db.Column(db.Integer, db.ForeignKey('vendas.id'))  # Se for de uma venda
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    cliente = db.relationship('Cliente', backref='contas_receber')
    venda = db.relationship('Venda', backref='contas_receber')
    
    def __repr__(self):
        return f'<ContaReceber {self.descricao}>'
