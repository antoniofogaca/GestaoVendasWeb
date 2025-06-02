from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app import app, db
from models import *
from forms import *
from auth import login_required, permission_required, get_current_user, get_current_empresa
from utils import *
from datetime import datetime, date
from sqlalchemy import func, and_, or_

@app.context_processor
def inject_user():
    return dict(current_user=get_current_user(), current_empresa=get_current_empresa())

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    # Carregar empresas para o dropdown
    empresas = Empresa.query.filter_by(ativa=True).all()
    form.empresa_id.choices = [(e.id, f"{e.nome_fantasia or e.razao_social} - {e.cnpj}") for e in empresas]
    form.empresa_id.choices.insert(0, (0, 'Selecione uma empresa...'))
    
    if form.validate_on_submit():
        empresa_id = form.empresa_id.data
        username = form.username.data.strip()
        password = form.password.data
        
        if empresa_id == 0:
            flash('Selecione uma empresa.', 'error')
            return render_template('login.html', form=form)
        
        # Buscar empresa
        empresa = Empresa.query.get(empresa_id)
        if not empresa or not empresa.ativa:
            flash('Empresa não encontrada ou desativada.', 'error')
            return render_template('login.html', form=form)
        
        # Buscar usuário
        user = Usuario.query.filter_by(username=username, empresa_id=empresa.id).first()
        
        if not user or not user.check_password(password):
            flash('Usuário ou senha incorretos.', 'error')
            return render_template('login.html', form=form)
        
        if not user.ativo:
            flash('Usuário desativado. Entre em contato com o administrador.', 'error')
            return render_template('login.html', form=form)
        
        # Login bem-sucedido
        session['user_id'] = user.id
        session['empresa_id'] = empresa.id
        session['username'] = user.username
        session['empresa_nome'] = empresa.razao_social
        
        flash(f'Bem-vindo, {user.nome_completo or user.username}!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('login.html', form=form, show_register_link=len(empresas) > 0)

@app.route('/cadastro-usuario/<int:empresa_id>', methods=['GET', 'POST'])
def cadastro_usuario(empresa_id):
    empresa = Empresa.query.get_or_404(empresa_id)
    form = CadastroUsuarioForm()
    form.empresa_id.data = empresa_id
    
    if form.validate_on_submit():
        if form.password.data != form.confirm_password.data:
            flash('As senhas não coincidem.', 'error')
            return render_template('cadastro_usuario.html', form=form, empresa=empresa)
        
        # Verificar se username já existe na empresa
        existing_user = Usuario.query.filter_by(username=form.username.data, empresa_id=empresa_id).first()
        if existing_user:
            flash('Nome de usuário já existe nesta empresa.', 'error')
            return render_template('cadastro_usuario.html', form=form, empresa=empresa)
        
        # Verificar se email já existe na empresa
        existing_email = Usuario.query.filter_by(email=form.email.data, empresa_id=empresa_id).first()
        if existing_email:
            flash('E-mail já cadastrado nesta empresa.', 'error')
            return render_template('cadastro_usuario.html', form=form, empresa=empresa)
        
        # Criar novo usuário
        user = Usuario(
            empresa_id=empresa_id,
            username=form.username.data,
            email=form.email.data,
            nome_completo=form.nome_completo.data,
            admin=False,
            ativo=True,
            # Permissões básicas para usuário comum
            perm_vendas=True,
            perm_produtos=True,
            perm_clientes=True,
            perm_caixa=True
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Usuário cadastrado com sucesso! Agora você pode fazer login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('cadastro_usuario.html', form=form, empresa=empresa)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso.', 'info')
    return redirect(url_for('login'))

@app.route('/cadastro-empresa', methods=['GET', 'POST'])
def cadastro_empresa():
    form = EmpresaForm()
    
    if form.validate_on_submit():
        cnpj = form.cnpj.data.replace('.', '').replace('/', '').replace('-', '')
        
        # Validar CNPJ
        if not validar_cnpj(cnpj):
            flash('CNPJ inválido. Verifique os dados informados.', 'error')
            return render_template('empresa/cadastro.html', form=form)
        
        # Verificar se empresa já existe
        if Empresa.query.filter_by(cnpj=cnpj).first():
            flash('Empresa já cadastrada com este CNPJ.', 'error')
            return render_template('empresa/cadastro.html', form=form)
        
        # Criar nova empresa
        empresa = Empresa(
            cnpj=cnpj,
            razao_social=form.razao_social.data,
            nome_fantasia=form.nome_fantasia.data,
            endereco=form.endereco.data,
            cidade=form.cidade.data,
            uf=form.uf.data,
            cep=form.cep.data.replace('-', '') if form.cep.data else None,
            telefone=form.telefone.data,
            email=form.email.data
        )
        
        db.session.add(empresa)
        db.session.flush()  # Para obter o ID da empresa
        
        # Criar usuário administrador padrão
        admin_user = Usuario(
            username='admin',
            email=form.email.data or 'admin@empresa.com',
            nome_completo='Administrador',
            empresa_id=empresa.id,
            admin=True,
            ativo=True,
            perm_vendas=True,
            perm_produtos=True,
            perm_clientes=True,
            perm_fornecedores=True,
            perm_financeiro=True,
            perm_relatorios=True,
            perm_caixa=True
        )
        admin_user.set_password('admin123')  # Senha padrão
        
        db.session.add(admin_user)
        db.session.commit()
        
        flash('Empresa cadastrada com sucesso! Use as credenciais: usuário "admin" e senha "admin123"', 'success')
        return redirect(url_for('login'))
    
    return render_template('empresa/cadastro.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    user = get_current_user()
    empresa = get_current_empresa()
    
    # Estatísticas básicas
    hoje = date.today()
    mes_atual = hoje.month
    ano_atual = hoje.year
    
    # Vendas do dia
    vendas_hoje = db.session.query(func.sum(Venda.total)).filter(
        func.date(Venda.data_venda) == hoje,
        Venda.empresa_id == empresa.id,
        Venda.status == 'FINALIZADA'
    ).scalar() or 0
    
    # Vendas do mês
    vendas_mes = db.session.query(func.sum(Venda.total)).filter(
        func.extract('month', Venda.data_venda) == mes_atual,
        func.extract('year', Venda.data_venda) == ano_atual,
        Venda.empresa_id == empresa.id,
        Venda.status == 'FINALIZADA'
    ).scalar() or 0
    
    # Total de produtos
    total_produtos = Produto.query.filter_by(empresa_id=empresa.id, ativo=True).count()
    
    # Total de clientes
    total_clientes = Cliente.query.filter_by(empresa_id=empresa.id, ativo=True).count()
    
    # Produtos com estoque baixo
    produtos_estoque_baixo = Produto.query.filter(
        Produto.empresa_id == empresa.id,
        Produto.ativo == True,
        Produto.estoque_atual <= Produto.estoque_minimo
    ).count()
    
    # Contas a pagar vencidas
    contas_pagar_vencidas = ContaPagar.query.filter(
        ContaPagar.empresa_id == empresa.id,
        ContaPagar.status == 'PENDENTE',
        ContaPagar.data_vencimento < hoje
    ).count()
    
    # Contas a receber vencidas
    contas_receber_vencidas = ContaReceber.query.filter(
        ContaReceber.empresa_id == empresa.id,
        ContaReceber.status == 'PENDENTE',
        ContaReceber.data_vencimento < hoje
    ).count()
    
    # Últimas vendas
    ultimas_vendas = Venda.query.filter_by(empresa_id=empresa.id)\
        .order_by(Venda.data_venda.desc()).limit(5).all()
    
    return render_template('dashboard.html',
                         vendas_hoje=vendas_hoje,
                         vendas_mes=vendas_mes,
                         total_produtos=total_produtos,
                         total_clientes=total_clientes,
                         produtos_estoque_baixo=produtos_estoque_baixo,
                         contas_pagar_vencidas=contas_pagar_vencidas,
                         contas_receber_vencidas=contas_receber_vencidas,
                         ultimas_vendas=ultimas_vendas)

# Rotas de Produtos
@app.route('/produtos')
@login_required
@permission_required('produtos')
def produtos_lista():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Produto.query.filter_by(empresa_id=session['empresa_id'])
    
    if search:
        query = query.filter(or_(
            Produto.nome.contains(search),
            Produto.codigo.contains(search),
            Produto.categoria.contains(search)
        ))
    
    produtos = query.order_by(Produto.nome).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('produtos/lista.html', produtos=produtos, search=search)

@app.route('/produtos/novo', methods=['GET', 'POST'])
@login_required
@permission_required('produtos')
def produto_novo():
    form = ProdutoForm()
    
    if form.validate_on_submit():
        produto = Produto(
            codigo=form.codigo.data,
            nome=form.nome.data,
            descricao=form.descricao.data,
            preco_custo=form.preco_custo.data,
            preco_venda=form.preco_venda.data,
            estoque_atual=form.estoque_atual.data,
            estoque_minimo=form.estoque_minimo.data,
            unidade=form.unidade.data,
            categoria=form.categoria.data,
            ativo=form.ativo.data,
            empresa_id=session['empresa_id']
        )
        
        db.session.add(produto)
        db.session.commit()
        
        flash('Produto cadastrado com sucesso!', 'success')
        return redirect(url_for('produtos_lista'))
    
    return render_template('produtos/form.html', form=form, title='Novo Produto')

@app.route('/produtos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@permission_required('produtos')
def produto_editar(id):
    produto = Produto.query.filter_by(id=id, empresa_id=session['empresa_id']).first_or_404()
    form = ProdutoForm(obj=produto)
    
    if form.validate_on_submit():
        form.populate_obj(produto)
        db.session.commit()
        
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('produtos_lista'))
    
    return render_template('produtos/form.html', form=form, title='Editar Produto', produto=produto)

@app.route('/produtos/<int:id>/excluir', methods=['POST'])
@login_required
@permission_required('produtos')
def produto_excluir(id):
    produto = Produto.query.filter_by(id=id, empresa_id=session['empresa_id']).first_or_404()
    produto.ativo = False
    db.session.commit()
    
    flash('Produto desativado com sucesso!', 'success')
    return redirect(url_for('produtos_lista'))

# Rotas de Clientes
@app.route('/clientes')
@login_required
@permission_required('clientes')
def clientes_lista():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Cliente.query.filter_by(empresa_id=session['empresa_id'])
    
    if search:
        query = query.filter(or_(
            Cliente.nome.contains(search),
            Cliente.cpf_cnpj.contains(search),
            Cliente.email.contains(search)
        ))
    
    clientes = query.order_by(Cliente.nome).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('clientes/lista.html', clientes=clientes, search=search)

@app.route('/clientes/novo', methods=['GET', 'POST'])
@login_required
@permission_required('clientes')
def cliente_novo():
    form = ClienteForm()
    
    if form.validate_on_submit():
        cliente = Cliente(
            tipo=form.tipo.data,
            cpf_cnpj=form.cpf_cnpj.data.replace('.', '').replace('/', '').replace('-', '') if form.cpf_cnpj.data else None,
            nome=form.nome.data,
            email=form.email.data,
            telefone=form.telefone.data,
            endereco=form.endereco.data,
            cidade=form.cidade.data,
            uf=form.uf.data,
            cep=form.cep.data.replace('-', '') if form.cep.data else None,
            observacoes=form.observacoes.data,
            ativo=form.ativo.data,
            empresa_id=session['empresa_id']
        )
        
        db.session.add(cliente)
        db.session.commit()
        
        flash('Cliente cadastrado com sucesso!', 'success')
        return redirect(url_for('clientes_lista'))
    
    return render_template('clientes/form.html', form=form, title='Novo Cliente')

@app.route('/clientes/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@permission_required('clientes')
def cliente_editar(id):
    cliente = Cliente.query.filter_by(id=id, empresa_id=session['empresa_id']).first_or_404()
    form = ClienteForm(obj=cliente)
    
    if form.validate_on_submit():
        form.populate_obj(cliente)
        if cliente.cpf_cnpj:
            cliente.cpf_cnpj = cliente.cpf_cnpj.replace('.', '').replace('/', '').replace('-', '')
        if cliente.cep:
            cliente.cep = cliente.cep.replace('-', '')
        
        db.session.commit()
        
        flash('Cliente atualizado com sucesso!', 'success')
        return redirect(url_for('clientes_lista'))
    
    return render_template('clientes/form.html', form=form, title='Editar Cliente', cliente=cliente)

# Rotas de Fornecedores
@app.route('/fornecedores')
@login_required
@permission_required('fornecedores')
def fornecedores_lista():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Fornecedor.query.filter_by(empresa_id=session['empresa_id'])
    
    if search:
        query = query.filter(or_(
            Fornecedor.razao_social.contains(search),
            Fornecedor.nome_fantasia.contains(search),
            Fornecedor.cnpj.contains(search)
        ))
    
    fornecedores = query.order_by(Fornecedor.razao_social).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('fornecedores/lista.html', fornecedores=fornecedores, search=search)

@app.route('/fornecedores/novo', methods=['GET', 'POST'])
@login_required
@permission_required('fornecedores')
def fornecedor_novo():
    form = FornecedorForm()
    
    if form.validate_on_submit():
        fornecedor = Fornecedor(
            cnpj=form.cnpj.data.replace('.', '').replace('/', '').replace('-', '') if form.cnpj.data else None,
            razao_social=form.razao_social.data,
            nome_fantasia=form.nome_fantasia.data,
            contato=form.contato.data,
            email=form.email.data,
            telefone=form.telefone.data,
            endereco=form.endereco.data,
            cidade=form.cidade.data,
            uf=form.uf.data,
            cep=form.cep.data.replace('-', '') if form.cep.data else None,
            observacoes=form.observacoes.data,
            ativo=form.ativo.data,
            empresa_id=session['empresa_id']
        )
        
        db.session.add(fornecedor)
        db.session.commit()
        
        flash('Fornecedor cadastrado com sucesso!', 'success')
        return redirect(url_for('fornecedores_lista'))
    
    return render_template('fornecedores/form.html', form=form, title='Novo Fornecedor')

# Rotas de Vendedores
@app.route('/vendedores')
@login_required
@permission_required('vendas')
def vendedores_lista():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Vendedor.query.filter_by(empresa_id=session['empresa_id'])
    
    if search:
        query = query.filter(Vendedor.nome.contains(search))
    
    vendedores = query.order_by(Vendedor.nome).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('vendedores/lista.html', vendedores=vendedores, search=search)

@app.route('/vendedores/novo', methods=['GET', 'POST'])
@login_required
@permission_required('vendas')
def vendedor_novo():
    form = VendedorForm()
    
    if form.validate_on_submit():
        vendedor = Vendedor(
            nome=form.nome.data,
            email=form.email.data,
            telefone=form.telefone.data,
            comissao_percentual=form.comissao_percentual.data,
            ativo=form.ativo.data,
            empresa_id=session['empresa_id']
        )
        
        db.session.add(vendedor)
        db.session.commit()
        
        flash('Vendedor cadastrado com sucesso!', 'success')
        return redirect(url_for('vendedores_lista'))
    
    return render_template('vendedores/form.html', form=form, title='Novo Vendedor')

# PDV - Ponto de Venda
@app.route('/pdv')
@login_required
@permission_required('vendas')
def pdv_index():
    produtos = Produto.query.filter_by(empresa_id=session['empresa_id'], ativo=True)\
        .order_by(Produto.nome).all()
    clientes = Cliente.query.filter_by(empresa_id=session['empresa_id'], ativo=True)\
        .order_by(Cliente.nome).all()
    vendedores = Vendedor.query.filter_by(empresa_id=session['empresa_id'], ativo=True)\
        .order_by(Vendedor.nome).all()
    
    return render_template('pdv/index.html', produtos=produtos, clientes=clientes, vendedores=vendedores)

@app.route('/pdv/finalizar-venda', methods=['POST'])
@login_required
@permission_required('vendas')
def pdv_finalizar_venda():
    data = request.get_json()
    
    try:
        # Criar nova venda
        venda = Venda(
            numero=gerar_numero_venda(session['empresa_id']),
            cliente_id=data.get('cliente_id') or None,
            vendedor_id=data.get('vendedor_id') or None,
            usuario_id=session['user_id'],
            empresa_id=session['empresa_id'],
            subtotal=data['subtotal'],
            desconto=data.get('desconto', 0),
            total=data['total'],
            forma_pagamento=data['forma_pagamento'],
            observacoes=data.get('observacoes', ''),
            status='FINALIZADA'
        )
        
        db.session.add(venda)
        db.session.flush()
        
        # Adicionar itens da venda
        for item_data in data['itens']:
            produto = Produto.query.get(item_data['produto_id'])
            if not produto:
                raise ValueError(f"Produto não encontrado: {item_data['produto_id']}")
            
            # Verificar estoque
            if produto.estoque_atual < item_data['quantidade']:
                raise ValueError(f"Estoque insuficiente para o produto: {produto.nome}")
            
            item = ItemVenda(
                venda_id=venda.id,
                produto_id=produto.id,
                quantidade=item_data['quantidade'],
                preco_unitario=item_data['preco_unitario'],
                desconto_item=item_data.get('desconto_item', 0),
                subtotal=item_data['subtotal']
            )
            
            db.session.add(item)
            
            # Atualizar estoque
            produto.estoque_atual -= item_data['quantidade']
        
        # Registrar movimento de caixa
        movimento = MovimentoCaixa(
            tipo='ENTRADA',
            categoria='VENDA',
            descricao=f'Venda {venda.numero}',
            valor=venda.total,
            usuario_id=session['user_id'],
            empresa_id=session['empresa_id'],
            venda_id=venda.id
        )
        
        db.session.add(movimento)
        db.session.commit()
        
        return jsonify({'success': True, 'numero_venda': venda.numero})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

# Caixa
@app.route('/caixa')
@login_required
@permission_required('caixa')
def caixa_index():
    hoje = date.today()
    
    # Movimentos do dia
    movimentos = MovimentoCaixa.query.filter(
        func.date(MovimentoCaixa.data_movimento) == hoje,
        MovimentoCaixa.empresa_id == session['empresa_id']
    ).order_by(MovimentoCaixa.data_movimento.desc()).all()
    
    # Totais
    total_entradas = db.session.query(func.sum(MovimentoCaixa.valor)).filter(
        func.date(MovimentoCaixa.data_movimento) == hoje,
        MovimentoCaixa.empresa_id == session['empresa_id'],
        MovimentoCaixa.tipo == 'ENTRADA'
    ).scalar() or 0
    
    total_saidas = db.session.query(func.sum(MovimentoCaixa.valor)).filter(
        func.date(MovimentoCaixa.data_movimento) == hoje,
        MovimentoCaixa.empresa_id == session['empresa_id'],
        MovimentoCaixa.tipo == 'SAIDA'
    ).scalar() or 0
    
    saldo = total_entradas - total_saidas
    
    return render_template('caixa/index.html',
                         movimentos=movimentos,
                         total_entradas=total_entradas,
                         total_saidas=total_saidas,
                         saldo=saldo)

# Financeiro - Contas a Pagar
@app.route('/financeiro/contas-pagar')
@login_required
@permission_required('financeiro')
def contas_pagar():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    
    query = ContaPagar.query.filter_by(empresa_id=session['empresa_id'])
    
    if status:
        query = query.filter_by(status=status)
    
    contas = query.order_by(ContaPagar.data_vencimento).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('financeiro/contas_pagar.html', contas=contas, status=status)

# Financeiro - Contas a Receber
@app.route('/financeiro/contas-receber')
@login_required
@permission_required('financeiro')
def contas_receber():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    
    query = ContaReceber.query.filter_by(empresa_id=session['empresa_id'])
    
    if status:
        query = query.filter_by(status=status)
    
    contas = query.order_by(ContaReceber.data_vencimento).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('financeiro/contas_receber.html', contas=contas, status=status)

# Relatórios
@app.route('/relatorios')
@login_required
@permission_required('relatorios')
def relatorios_index():
    return render_template('relatorios/index.html')

@app.route('/relatorios/vendas/pdf')
@login_required
@permission_required('relatorios')
def relatorio_vendas_pdf():
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    query = Venda.query.filter_by(empresa_id=session['empresa_id'])
    
    if data_inicio:
        query = query.filter(Venda.data_venda >= data_inicio)
    if data_fim:
        query = query.filter(Venda.data_venda <= data_fim)
    
    vendas = query.order_by(Venda.data_venda.desc()).all()
    
    colunas = {
        'Número': 'numero',
        'Data': 'data_venda',
        'Cliente': 'cliente_rel.nome',
        'Total': 'total',
        'Status': 'status'
    }
    
    empresa = get_current_empresa()
    return gerar_relatorio_pdf('Relatório de Vendas', vendas, colunas, empresa)

# Administração
@app.route('/admin/usuarios')
@login_required
def admin_usuarios():
    user = get_current_user()
    if not user.admin:
        flash('Acesso negado. Apenas administradores podem acessar esta área.', 'error')
        return redirect(url_for('dashboard'))
    
    usuarios = Usuario.query.filter_by(empresa_id=session['empresa_id']).order_by(Usuario.username).all()
    return render_template('admin/usuarios.html', usuarios=usuarios)

@app.route('/admin/usuarios/novo', methods=['GET', 'POST'])
@login_required
def admin_usuario_novo():
    user = get_current_user()
    if not user.admin:
        flash('Acesso negado.', 'error')
        return redirect(url_for('dashboard'))
    
    form = UsuarioForm()
    
    if form.validate_on_submit():
        # Verificar se username já existe na empresa
        existing_user = Usuario.query.filter_by(
            username=form.username.data,
            empresa_id=session['empresa_id']
        ).first()
        
        if existing_user:
            flash('Usuário já existe nesta empresa.', 'error')
            return render_template('admin/usuario_form.html', form=form, title='Novo Usuário')
        
        usuario = Usuario(
            username=form.username.data,
            email=form.email.data,
            nome_completo=form.nome_completo.data,
            admin=form.admin.data,
            ativo=form.ativo.data,
            empresa_id=session['empresa_id'],
            perm_vendas=form.perm_vendas.data,
            perm_produtos=form.perm_produtos.data,
            perm_clientes=form.perm_clientes.data,
            perm_fornecedores=form.perm_fornecedores.data,
            perm_financeiro=form.perm_financeiro.data,
            perm_relatorios=form.perm_relatorios.data,
            perm_caixa=form.perm_caixa.data
        )
        
        if form.password.data:
            usuario.set_password(form.password.data)
        else:
            usuario.set_password('123456')  # Senha padrão
        
        db.session.add(usuario)
        db.session.commit()
        
        flash('Usuário cadastrado com sucesso!', 'success')
        return redirect(url_for('admin_usuarios'))
    
    return render_template('admin/usuario_form.html', form=form, title='Novo Usuário')

# API endpoints para PDV
@app.route('/api/produtos/buscar')
@login_required
def api_produtos_buscar():
    term = request.args.get('term', '')
    
    produtos = Produto.query.filter(
        Produto.empresa_id == session['empresa_id'],
        Produto.ativo == True,
        or_(
            Produto.nome.contains(term),
            Produto.codigo.contains(term)
        )
    ).limit(10).all()
    
    return jsonify([{
        'id': p.id,
        'nome': p.nome,
        'codigo': p.codigo,
        'preco': float(p.preco_venda),
        'estoque': p.estoque_atual
    } for p in produtos])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
