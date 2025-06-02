import re
from datetime import datetime
import csv
import io
from flask import make_response
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

def validar_cnpj(cnpj):
    """Valida CNPJ removendo caracteres especiais e verificando dígitos"""
    # Remove caracteres especiais
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    
    # Verifica se tem 14 dígitos
    if len(cnpj) != 14:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cnpj == cnpj[0] * 14:
        return False
    
    # Validação dos dígitos verificadores
    def calcular_digito(cnpj_base, pesos):
        soma = sum(int(cnpj_base[i]) * pesos[i] for i in range(len(pesos)))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto
    
    # Primeiro dígito verificador
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    digito1 = calcular_digito(cnpj[:12], pesos1)
    
    # Segundo dígito verificador
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    digito2 = calcular_digito(cnpj[:13], pesos2)
    
    return cnpj[-2:] == f"{digito1}{digito2}"

def validar_cpf(cpf):
    """Valida CPF removendo caracteres especiais e verificando dígitos"""
    # Remove caracteres especiais
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False
    
    # Validação dos dígitos verificadores
    def calcular_digito(cpf_base, pesos):
        soma = sum(int(cpf_base[i]) * pesos[i] for i in range(len(pesos)))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto
    
    # Primeiro dígito verificador
    pesos1 = list(range(10, 1, -1))
    digito1 = calcular_digito(cpf[:9], pesos1)
    
    # Segundo dígito verificador
    pesos2 = list(range(11, 1, -1))
    digito2 = calcular_digito(cpf[:10], pesos2)
    
    return cpf[-2:] == f"{digito1}{digito2}"

def formatar_cnpj(cnpj):
    """Formata CNPJ com pontuação"""
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    if len(cnpj) == 14:
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
    return cnpj

def formatar_cpf(cpf):
    """Formata CPF com pontuação"""
    cpf = re.sub(r'[^0-9]', '', cpf)
    if len(cpf) == 11:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    return cpf

def formatar_cep(cep):
    """Formata CEP com pontuação"""
    cep = re.sub(r'[^0-9]', '', cep)
    if len(cep) == 8:
        return f"{cep[:5]}-{cep[5:]}"
    return cep

def formatar_telefone(telefone):
    """Formata telefone com pontuação"""
    telefone = re.sub(r'[^0-9]', '', telefone)
    if len(telefone) == 11:  # Celular
        return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
    elif len(telefone) == 10:  # Fixo
        return f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
    return telefone

def formatar_moeda(valor):
    """Formata valor monetário"""
    if valor is None:
        return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def gerar_numero_venda(empresa_id):
    """Gera número sequencial para venda"""
    from models import Venda
    ultima_venda = Venda.query.filter_by(empresa_id=empresa_id).order_by(Venda.id.desc()).first()
    if ultima_venda:
        try:
            ultimo_numero = int(ultima_venda.numero.split('-')[1])
            proximo_numero = ultimo_numero + 1
        except:
            proximo_numero = 1
    else:
        proximo_numero = 1
    
    return f"VD-{proximo_numero:06d}"

def exportar_csv(dados, nome_arquivo, colunas):
    """Exporta dados para CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Escreve cabeçalhos
    writer.writerow(colunas.keys())
    
    # Escreve dados
    for item in dados:
        linha = []
        for campo in colunas.values():
            if hasattr(item, campo):
                valor = getattr(item, campo)
                if isinstance(valor, datetime):
                    valor = valor.strftime('%d/%m/%Y %H:%M')
                elif valor is None:
                    valor = ''
                linha.append(str(valor))
            else:
                linha.append('')
        writer.writerow(linha)
    
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename={nome_arquivo}.csv'
    
    return response

def gerar_relatorio_pdf(titulo, dados, colunas, empresa=None):
    """Gera relatório em PDF"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Centralizado
    )
    
    # Elementos do documento
    story = []
    
    # Cabeçalho da empresa
    if empresa:
        story.append(Paragraph(empresa.razao_social, title_style))
        if empresa.cnpj:
            story.append(Paragraph(f"CNPJ: {formatar_cnpj(empresa.cnpj)}", styles['Normal']))
        story.append(Spacer(1, 20))
    
    # Título do relatório
    story.append(Paragraph(titulo, title_style))
    story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    if dados:
        # Preparar dados da tabela
        dados_tabela = [list(colunas.keys())]  # Cabeçalhos
        
        for item in dados:
            linha = []
            for campo in colunas.values():
                if hasattr(item, campo):
                    valor = getattr(item, campo)
                    if isinstance(valor, datetime):
                        valor = valor.strftime('%d/%m/%Y')
                    elif valor is None:
                        valor = ''
                    linha.append(str(valor))
                else:
                    linha.append('')
            dados_tabela.append(linha)
        
        # Criar tabela
        tabela = Table(dados_tabela)
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(tabela)
    else:
        story.append(Paragraph("Nenhum registro encontrado.", styles['Normal']))
    
    # Gerar PDF
    doc.build(story)
    buffer.seek(0)
    
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={titulo.replace(" ", "_")}.pdf'
    
    return response
