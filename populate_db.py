#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para popular o banco de dados com dados de exemplo
"""

from app import app, db
from models import (
    Empresa, Usuario, Produto, Cliente, Fornecedor, 
    Vendedor, Venda, ItemVenda, ContaPagar, ContaReceber,
    MovimentoCaixa, Categoria, Servico, Banco
)
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from decimal import Decimal
import random

def create_sample_data():
    """Cria dados de exemplo para o sistema"""
    with app.app_context():
        # Limpar dados existentes (opcional)
        print("Criando dados de exemplo...")
        
        # 1. Empresa de exemplo
        empresa = Empresa.query.first()
        if not empresa:
            empresa = Empresa(
                cnpj='12.345.678/0001-90',
                razao_social='Empresa Demo Ltda',
                nome_fantasia='Demo ERP',
                endereco='Rua das Flores, 123',
                cidade='São Paulo',
                uf='SP',
                cep='01234-567',
                telefone='(11) 3456-7890',
                email='contato@demo.com.br'
            )
            db.session.add(empresa)
            db.session.commit()
        
        # 2. Usuário administrador
        admin_user = Usuario.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = Usuario(
                empresa_id=empresa.id,
                username='admin',
                email='admin@demo.com.br',
                nome_completo='Administrador do Sistema',
                password_hash=generate_password_hash('123456'),
                admin=True,
                ativo=True,
                perm_vendas=True,
                perm_produtos=True,
                perm_clientes=True,
                perm_fornecedores=True,
                perm_financeiro=True,
                perm_relatorios=True,
                perm_caixa=True,
                perm_compras=True
            )
            db.session.add(admin_user)
            db.session.commit()
        
        # 3. Categorias
        categorias_data = [
            'Eletrônicos', 'Roupas', 'Calçados', 'Casa e Jardim', 'Esportes',
            'Livros', 'Brinquedos', 'Automóveis', 'Saúde', 'Alimentação'
        ]
        
        categorias = []
        for nome in categorias_data:
            categoria = Categoria.query.filter_by(nome=nome, empresa_id=empresa.id).first()
            if not categoria:
                categoria = Categoria(
                    empresa_id=empresa.id,
                    nome=nome,
                    ativo=True
                )
                db.session.add(categoria)
                categorias.append(categoria)
        
        db.session.commit()
        
        # 4. Bancos
        bancos_data = [
            {'codigo': '001', 'nome': 'Banco do Brasil'},
            {'codigo': '033', 'nome': 'Santander'},
            {'codigo': '104', 'nome': 'Caixa Econômica Federal'},
            {'codigo': '237', 'nome': 'Bradesco'},
            {'codigo': '341', 'nome': 'Itaú'},
        ]
        
        for banco_data in bancos_data:
            banco = Banco.query.filter_by(codigo=banco_data['codigo'], empresa_id=empresa.id).first()
            if not banco:
                banco = Banco(
                    empresa_id=empresa.id,
                    codigo=banco_data['codigo'],
                    nome=banco_data['nome'],
                    agencia='1234',
                    conta='12345-6',
                    ativo=True
                )
                db.session.add(banco)
        
        db.session.commit()
        
        # 5. Produtos
        produtos_data = [
            {'nome': 'Smartphone Samsung Galaxy', 'preco': 899.99, 'categoria': 'Eletrônicos'},
            {'nome': 'Notebook Dell Inspiron', 'preco': 2299.99, 'categoria': 'Eletrônicos'},
            {'nome': 'Camiseta Polo', 'preco': 89.90, 'categoria': 'Roupas'},
            {'nome': 'Tênis Nike Air Max', 'preco': 299.99, 'categoria': 'Calçados'},
            {'nome': 'Mesa de Escritório', 'preco': 450.00, 'categoria': 'Casa e Jardim'},
            {'nome': 'Bicicleta Mountain Bike', 'preco': 1299.99, 'categoria': 'Esportes'},
            {'nome': 'Livro Python Programming', 'preco': 79.90, 'categoria': 'Livros'},
            {'nome': 'Boneca Barbie', 'preco': 49.99, 'categoria': 'Brinquedos'},
            {'nome': 'Pneu Aro 15', 'preco': 189.90, 'categoria': 'Automóveis'},
            {'nome': 'Vitamina C 1g', 'preco': 29.90, 'categoria': 'Saúde'},
            {'nome': 'Café Premium 500g', 'preco': 24.90, 'categoria': 'Alimentação'},
            {'nome': 'Tablet Apple iPad', 'preco': 1799.99, 'categoria': 'Eletrônicos'},
        ]
        
        for i, produto_data in enumerate(produtos_data, 1):
            categoria = Categoria.query.filter_by(nome=produto_data['categoria'], empresa_id=empresa.id).first()
            produto = Produto.query.filter_by(nome=produto_data['nome'], empresa_id=empresa.id).first()
            if not produto:
                produto = Produto(
                    empresa_id=empresa.id,
                    codigo=f'PROD{i:03d}',
                    nome=produto_data['nome'],
                    preco_custo=Decimal(str(produto_data['preco'] * 0.6)),
                    preco_venda=Decimal(str(produto_data['preco'])),
                    estoque_atual=random.randint(5, 100),
                    estoque_minimo=5,
                    unidade='UN',
                    categoria_id=categoria.id if categoria else None,
                    ativo=True
                )
                db.session.add(produto)
        
        db.session.commit()
        
        # 6. Serviços
        servicos_data = [
            {'nome': 'Instalação de Software', 'preco': 80.00},
            {'nome': 'Manutenção de Computador', 'preco': 120.00},
            {'nome': 'Consultoria em TI', 'preco': 150.00},
            {'nome': 'Backup de Dados', 'preco': 60.00},
            {'nome': 'Formatação de PC', 'preco': 90.00},
        ]
        
        for servico_data in servicos_data:
            servico = Servico.query.filter_by(nome=servico_data['nome'], empresa_id=empresa.id).first()
            if not servico:
                servico = Servico(
                    empresa_id=empresa.id,
                    nome=servico_data['nome'],
                    descricao=f"Serviço de {servico_data['nome'].lower()}",
                    preco=Decimal(str(servico_data['preco'])),
                    ativo=True
                )
                db.session.add(servico)
        
        db.session.commit()
        
        # 7. Clientes
        clientes_data = [
            {'nome': 'João Silva Santos', 'cpf': '123.456.789-01', 'email': 'joao@email.com'},
            {'nome': 'Maria Oliveira Costa', 'cpf': '987.654.321-02', 'email': 'maria@email.com'},
            {'nome': 'Pedro Souza Lima', 'cpf': '456.789.123-03', 'email': 'pedro@email.com'},
            {'nome': 'Ana Paula Ferreira', 'cpf': '789.123.456-04', 'email': 'ana@email.com'},
            {'nome': 'Carlos Eduardo Alves', 'cpf': '321.654.987-05', 'email': 'carlos@email.com'},
            {'nome': 'Empresa ABC Ltda', 'cnpj': '12.345.678/0001-91', 'email': 'contato@abc.com.br'},
            {'nome': 'Comercial XYZ S/A', 'cnpj': '98.765.432/0001-10', 'email': 'vendas@xyz.com.br'},
            {'nome': 'Distribuidora 123', 'cnpj': '45.678.912/0001-34', 'email': 'admin@dist123.com'},
            {'nome': 'Loja Virtual Online', 'cnpj': '78.912.345/0001-67', 'email': 'suporte@virtual.com'},
            {'nome': 'Supermercado Local', 'cnpj': '32.165.498/0001-89', 'email': 'compras@local.com'},
        ]
        
        for cliente_data in clientes_data:
            if 'cpf' in cliente_data:
                cliente = Cliente.query.filter_by(cpf_cnpj=cliente_data['cpf'], empresa_id=empresa.id).first()
                tipo = 'PF'
                cpf_cnpj = cliente_data['cpf']
            else:
                cliente = Cliente.query.filter_by(cpf_cnpj=cliente_data['cnpj'], empresa_id=empresa.id).first()
                tipo = 'PJ'
                cpf_cnpj = cliente_data['cnpj']
            
            if not cliente:
                cliente = Cliente(
                    empresa_id=empresa.id,
                    tipo=tipo,
                    cpf_cnpj=cpf_cnpj,
                    nome=cliente_data['nome'],
                    email=cliente_data['email'],
                    telefone=f'(11) 9{random.randint(1000,9999)}-{random.randint(1000,9999)}',
                    endereco=f'Rua {random.choice(["das Flores", "da Paz", "Principal", "Central"])}, {random.randint(1,999)}',
                    cidade='São Paulo',
                    uf='SP',
                    cep=f'{random.randint(10000,99999)}-{random.randint(100,999)}',
                    ativo=True
                )
                db.session.add(cliente)
        
        db.session.commit()
        
        # 8. Fornecedores
        fornecedores_data = [
            {'razao_social': 'Tech Solutions Ltda', 'cnpj': '11.222.333/0001-44'},
            {'razao_social': 'Distribuidora Nacional S/A', 'cnpj': '22.333.444/0001-55'},
            {'razao_social': 'Importadora Global', 'cnpj': '33.444.555/0001-66'},
            {'razao_social': 'Fábrica de Componentes', 'cnpj': '44.555.666/0001-77'},
            {'razao_social': 'Atacado Premium', 'cnpj': '55.666.777/0001-88'},
        ]
        
        for fornecedor_data in fornecedores_data:
            fornecedor = Fornecedor.query.filter_by(cnpj=fornecedor_data['cnpj'], empresa_id=empresa.id).first()
            if not fornecedor:
                fornecedor = Fornecedor(
                    empresa_id=empresa.id,
                    cnpj=fornecedor_data['cnpj'],
                    razao_social=fornecedor_data['razao_social'],
                    nome_fantasia=fornecedor_data['razao_social'].split()[0],
                    contato=f'Vendedor {random.choice(["João", "Maria", "Pedro", "Ana"])}',
                    email=f'vendas@{fornecedor_data["razao_social"].lower().replace(" ", "").replace("ltda", "").replace("s/a", "")}.com.br',
                    telefone=f'(11) 3{random.randint(100,999)}-{random.randint(1000,9999)}',
                    endereco=f'Av. Industrial, {random.randint(100,9999)}',
                    cidade='São Paulo',
                    uf='SP',
                    ativo=True
                )
                db.session.add(fornecedor)
        
        db.session.commit()
        
        # 9. Vendedores
        vendedores_data = [
            {'nome': 'Roberto Sales', 'comissao': 5.0},
            {'nome': 'Fernanda Vendas', 'comissao': 4.5},
            {'nome': 'Marcos Comercial', 'comissao': 6.0},
            {'nome': 'Juliana Negócios', 'comissao': 5.5},
            {'nome': 'André Representante', 'comissao': 4.0},
        ]
        
        for vendedor_data in vendedores_data:
            vendedor = Vendedor.query.filter_by(nome=vendedor_data['nome'], empresa_id=empresa.id).first()
            if not vendedor:
                vendedor = Vendedor(
                    empresa_id=empresa.id,
                    nome=vendedor_data['nome'],
                    email=f'{vendedor_data["nome"].lower().replace(" ", ".")}@demo.com.br',
                    telefone=f'(11) 9{random.randint(1000,9999)}-{random.randint(1000,9999)}',
                    comissao_percentual=Decimal(str(vendedor_data['comissao'])),
                    ativo=True
                )
                db.session.add(vendedor)
        
        db.session.commit()
        
        # 10. Vendas e Movimentações (últimos 30 dias)
        clientes = Cliente.query.filter_by(empresa_id=empresa.id).all()
        produtos = Produto.query.filter_by(empresa_id=empresa.id).all()
        vendedores = Vendedor.query.filter_by(empresa_id=empresa.id).all()
        
        for i in range(30):  # 30 vendas nos últimos 30 dias
            data_venda = datetime.now() - timedelta(days=i)
            
            # Criar venda
            venda = Venda(
                empresa_id=empresa.id,
                data_venda=data_venda,
                cliente_id=random.choice(clientes).id if clientes and random.choice([True, False]) else None,
                vendedor_id=random.choice(vendedores).id if vendedores and random.choice([True, False]) else None,
                forma_pagamento=random.choice(['DINHEIRO', 'CARTAO_DEBITO', 'CARTAO_CREDITO', 'PIX']),
                desconto=Decimal('0.00'),
                total=Decimal('0.00')
            )
            db.session.add(venda)
            db.session.flush()  # Para obter o ID da venda
            
            # Adicionar itens à venda
            num_itens = random.randint(1, 5)
            total_venda = Decimal('0.00')
            
            for _ in range(num_itens):
                produto = random.choice(produtos)
                quantidade = random.randint(1, 3)
                preco_unitario = produto.preco_venda
                subtotal = preco_unitario * quantidade
                total_venda += subtotal
                
                item = ItemVenda(
                    venda_id=venda.id,
                    produto_id=produto.id,
                    quantidade=quantidade,
                    preco_unitario=preco_unitario,
                    subtotal=subtotal
                )
                db.session.add(item)
            
            # Atualizar total da venda
            venda.total = total_venda
            
            # Criar movimentação de caixa
            movimento = MovimentoCaixa(
                empresa_id=empresa.id,
                data_movimento=data_venda,
                tipo='ENTRADA',
                descricao=f'Venda #{venda.id}',
                valor=total_venda,
                venda_id=venda.id
            )
            db.session.add(movimento)
        
        db.session.commit()
        
        # 11. Contas a Pagar
        fornecedores = Fornecedor.query.filter_by(empresa_id=empresa.id).all()
        for i in range(15):
            data_vencimento = datetime.now() + timedelta(days=random.randint(1, 60))
            valor = Decimal(str(random.uniform(500, 5000))).quantize(Decimal('0.01'))
            
            conta = ContaPagar(
                empresa_id=empresa.id,
                descricao=f'Fornecimento de mercadorias - {random.choice(["Janeiro", "Fevereiro", "Março"])}',
                fornecedor_id=random.choice(fornecedores).id if fornecedores else None,
                valor=valor,
                data_vencimento=data_vencimento.date(),
                status='PENDENTE' if random.choice([True, False]) else 'PAGA'
            )
            db.session.add(conta)
        
        # 12. Contas a Receber
        for i in range(20):
            data_vencimento = datetime.now() + timedelta(days=random.randint(1, 90))
            valor = Decimal(str(random.uniform(200, 3000))).quantize(Decimal('0.01'))
            
            conta = ContaReceber(
                empresa_id=empresa.id,
                descricao=f'Venda a prazo - {random.choice(["Parcela 1/3", "Parcela 2/3", "Parcela 3/3"])}',
                cliente_id=random.choice(clientes).id if clientes else None,
                valor=valor,
                data_vencimento=data_vencimento.date(),
                status=random.choice(['PENDENTE', 'RECEBIDA', 'VENCIDA'])
            )
            db.session.add(conta)
        
        db.session.commit()
        
        print("✅ Dados de exemplo criados com sucesso!")
        print(f"   - Empresa: {empresa.razao_social}")
        print(f"   - Usuário admin: admin / 123456")
        print(f"   - {len(produtos_data)} produtos cadastrados")
        print(f"   - {len(clientes_data)} clientes cadastrados")
        print(f"   - {len(fornecedores_data)} fornecedores cadastrados")
        print(f"   - {len(vendedores_data)} vendedores cadastrados")
        print(f"   - 30 vendas dos últimos 30 dias")
        print(f"   - 15 contas a pagar")
        print(f"   - 20 contas a receber")

if __name__ == '__main__':
    create_sample_data()