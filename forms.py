from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, IntegerField, DecimalField, BooleanField, DateField, HiddenField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange
from wtforms.widgets import TextArea

class LoginForm(FlaskForm):
    empresa_cnpj = StringField('CNPJ da Empresa', validators=[DataRequired()], render_kw={'placeholder': '00.000.000/0000-00'})
    username = StringField('Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])

class EmpresaForm(FlaskForm):
    cnpj = StringField('CNPJ', validators=[DataRequired(), Length(min=14, max=18)], render_kw={'placeholder': '00.000.000/0000-00'})
    razao_social = StringField('Razão Social', validators=[DataRequired(), Length(max=200)])
    nome_fantasia = StringField('Nome Fantasia', validators=[Optional(), Length(max=200)])
    endereco = StringField('Endereço', validators=[Optional(), Length(max=200)])
    cidade = StringField('Cidade', validators=[Optional(), Length(max=100)])
    uf = SelectField('UF', choices=[
        ('', 'Selecione...'),
        ('AC', 'AC'), ('AL', 'AL'), ('AP', 'AP'), ('AM', 'AM'), ('BA', 'BA'),
        ('CE', 'CE'), ('DF', 'DF'), ('ES', 'ES'), ('GO', 'GO'), ('MA', 'MA'),
        ('MT', 'MT'), ('MS', 'MS'), ('MG', 'MG'), ('PA', 'PA'), ('PB', 'PB'),
        ('PR', 'PR'), ('PE', 'PE'), ('PI', 'PI'), ('RJ', 'RJ'), ('RN', 'RN'),
        ('RS', 'RS'), ('RO', 'RO'), ('RR', 'RR'), ('SC', 'SC'), ('SP', 'SP'),
        ('SE', 'SE'), ('TO', 'TO')
    ], validators=[Optional()])
    cep = StringField('CEP', validators=[Optional(), Length(max=10)], render_kw={'placeholder': '00000-000'})
    telefone = StringField('Telefone', validators=[Optional(), Length(max=20)])
    email = StringField('E-mail', validators=[Optional(), Email(), Length(max=120)])

class UsuarioForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired(), Length(max=64)])
    email = StringField('E-mail', validators=[DataRequired(), Email(), Length(max=120)])
    nome_completo = StringField('Nome Completo', validators=[Optional(), Length(max=200)])
    password = PasswordField('Senha', validators=[Optional()])
    admin = BooleanField('Administrador')
    ativo = BooleanField('Ativo', default=True)
    
    # Permissões
    perm_vendas = BooleanField('Vendas', default=True)
    perm_produtos = BooleanField('Produtos', default=True)
    perm_clientes = BooleanField('Clientes', default=True)
    perm_fornecedores = BooleanField('Fornecedores')
    perm_financeiro = BooleanField('Financeiro')
    perm_relatorios = BooleanField('Relatórios')
    perm_caixa = BooleanField('Caixa', default=True)

class ProdutoForm(FlaskForm):
    codigo = StringField('Código', validators=[Optional(), Length(max=50)])
    nome = StringField('Nome', validators=[DataRequired(), Length(max=200)])
    descricao = TextAreaField('Descrição', validators=[Optional()])
    preco_custo = DecimalField('Preço de Custo', validators=[Optional(), NumberRange(min=0)], places=2, default=0)
    preco_venda = DecimalField('Preço de Venda', validators=[DataRequired(), NumberRange(min=0)], places=2)
    estoque_atual = IntegerField('Estoque Atual', validators=[Optional(), NumberRange(min=0)], default=0)
    estoque_minimo = IntegerField('Estoque Mínimo', validators=[Optional(), NumberRange(min=0)], default=0)
    unidade = SelectField('Unidade', choices=[
        ('UN', 'Unidade'),
        ('KG', 'Quilograma'),
        ('LT', 'Litro'),
        ('MT', 'Metro'),
        ('CX', 'Caixa'),
        ('PC', 'Peça')
    ], default='UN')
    categoria = StringField('Categoria', validators=[Optional(), Length(max=100)])
    ativo = BooleanField('Ativo', default=True)

class ClienteForm(FlaskForm):
    tipo = SelectField('Tipo', choices=[('PF', 'Pessoa Física'), ('PJ', 'Pessoa Jurídica')], default='PF')
    cpf_cnpj = StringField('CPF/CNPJ', validators=[Optional(), Length(max=18)])
    nome = StringField('Nome/Razão Social', validators=[DataRequired(), Length(max=200)])
    email = StringField('E-mail', validators=[Optional(), Email(), Length(max=120)])
    telefone = StringField('Telefone', validators=[Optional(), Length(max=20)])
    endereco = StringField('Endereço', validators=[Optional(), Length(max=200)])
    cidade = StringField('Cidade', validators=[Optional(), Length(max=100)])
    uf = SelectField('UF', choices=[
        ('', 'Selecione...'),
        ('AC', 'AC'), ('AL', 'AL'), ('AP', 'AP'), ('AM', 'AM'), ('BA', 'BA'),
        ('CE', 'CE'), ('DF', 'DF'), ('ES', 'ES'), ('GO', 'GO'), ('MA', 'MA'),
        ('MT', 'MT'), ('MS', 'MS'), ('MG', 'MG'), ('PA', 'PA'), ('PB', 'PB'),
        ('PR', 'PR'), ('PE', 'PE'), ('PI', 'PI'), ('RJ', 'RJ'), ('RN', 'RN'),
        ('RS', 'RS'), ('RO', 'RO'), ('RR', 'RR'), ('SC', 'SC'), ('SP', 'SP'),
        ('SE', 'SE'), ('TO', 'TO')
    ], validators=[Optional()])
    cep = StringField('CEP', validators=[Optional(), Length(max=10)])
    observacoes = TextAreaField('Observações', validators=[Optional()])
    ativo = BooleanField('Ativo', default=True)

class FornecedorForm(FlaskForm):
    cnpj = StringField('CNPJ', validators=[Optional(), Length(max=18)])
    razao_social = StringField('Razão Social', validators=[DataRequired(), Length(max=200)])
    nome_fantasia = StringField('Nome Fantasia', validators=[Optional(), Length(max=200)])
    contato = StringField('Contato', validators=[Optional(), Length(max=100)])
    email = StringField('E-mail', validators=[Optional(), Email(), Length(max=120)])
    telefone = StringField('Telefone', validators=[Optional(), Length(max=20)])
    endereco = StringField('Endereço', validators=[Optional(), Length(max=200)])
    cidade = StringField('Cidade', validators=[Optional(), Length(max=100)])
    uf = SelectField('UF', choices=[
        ('', 'Selecione...'),
        ('AC', 'AC'), ('AL', 'AL'), ('AP', 'AP'), ('AM', 'AM'), ('BA', 'BA'),
        ('CE', 'CE'), ('DF', 'DF'), ('ES', 'ES'), ('GO', 'GO'), ('MA', 'MA'),
        ('MT', 'MT'), ('MS', 'MS'), ('MG', 'MG'), ('PA', 'PA'), ('PB', 'PB'),
        ('PR', 'PR'), ('PE', 'PE'), ('PI', 'PI'), ('RJ', 'RJ'), ('RN', 'RN'),
        ('RS', 'RS'), ('RO', 'RO'), ('RR', 'RR'), ('SC', 'SC'), ('SP', 'SP'),
        ('SE', 'SE'), ('TO', 'TO')
    ], validators=[Optional()])
    cep = StringField('CEP', validators=[Optional(), Length(max=10)])
    observacoes = TextAreaField('Observações', validators=[Optional()])
    ativo = BooleanField('Ativo', default=True)

class VendedorForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(), Length(max=200)])
    email = StringField('E-mail', validators=[Optional(), Email(), Length(max=120)])
    telefone = StringField('Telefone', validators=[Optional(), Length(max=20)])
    comissao_percentual = DecimalField('Comissão (%)', validators=[Optional(), NumberRange(min=0, max=100)], places=2, default=0)
    ativo = BooleanField('Ativo', default=True)

class ContaPagarForm(FlaskForm):
    descricao = StringField('Descrição', validators=[DataRequired(), Length(max=200)])
    fornecedor_id = SelectField('Fornecedor', coerce=int, validators=[Optional()])
    valor = DecimalField('Valor', validators=[DataRequired(), NumberRange(min=0)], places=2)
    data_vencimento = DateField('Data de Vencimento', validators=[DataRequired()])
    data_pagamento = DateField('Data de Pagamento', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('PENDENTE', 'Pendente'),
        ('PAGA', 'Paga'),
        ('VENCIDA', 'Vencida')
    ], default='PENDENTE')
    observacoes = TextAreaField('Observações', validators=[Optional()])

class ContaReceberForm(FlaskForm):
    descricao = StringField('Descrição', validators=[DataRequired(), Length(max=200)])
    cliente_id = SelectField('Cliente', coerce=int, validators=[Optional()])
    valor = DecimalField('Valor', validators=[DataRequired(), NumberRange(min=0)], places=2)
    data_vencimento = DateField('Data de Vencimento', validators=[DataRequired()])
    data_recebimento = DateField('Data de Recebimento', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('PENDENTE', 'Pendente'),
        ('RECEBIDA', 'Recebida'),
        ('VENCIDA', 'Vencida')
    ], default='PENDENTE')
    observacoes = TextAreaField('Observações', validators=[Optional()])

class VendaForm(FlaskForm):
    cliente_id = SelectField('Cliente', coerce=int, validators=[Optional()])
    vendedor_id = SelectField('Vendedor', coerce=int, validators=[Optional()])
    forma_pagamento = SelectField('Forma de Pagamento', choices=[
        ('DINHEIRO', 'Dinheiro'),
        ('CARTAO_DEBITO', 'Cartão de Débito'),
        ('CARTAO_CREDITO', 'Cartão de Crédito'),
        ('PIX', 'PIX'),
        ('TRANSFERENCIA', 'Transferência'),
        ('CHEQUE', 'Cheque')
    ], validators=[DataRequired()])
    desconto = DecimalField('Desconto', validators=[Optional(), NumberRange(min=0)], places=2, default=0)
    observacoes = TextAreaField('Observações', validators=[Optional()])
