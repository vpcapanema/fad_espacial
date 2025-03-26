from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import cm

def gerar_relatorio_upload(nome_arquivo, tamanho_bytes, epsg, quantidade, sucesso, caminho_destino):
    criterios = [
        ("Arquivo ZIP importado corretamente", True),
        ("Tamanho do arquivo (bytes)", tamanho_bytes < 100000000),
        ("EPSG convertido para 4326", epsg == 4326),
        ("Feições carregadas com sucesso", quantidade > 0),
        ("Erro durante o upload", not sucesso)
    ]

    c = canvas.Canvas(caminho_destino, pagesize=A4)
    width, height = A4
    y = height - 50

    # Faixa azul com cabeçalho FAD
    c.setFillColorRGB(0.0, 0.25, 0.5)
    c.rect(0, y - 20, width, 40, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, y, "FAD - Ferramenta de Análise Dinamizada")
    y -= 60

    # Título centralizado
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, y, "Relatório de Upload da Geometria")
    y -= 30

    # Metadados
    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Nome do Arquivo: {nome_arquivo}")
    y -= 20
    c.drawString(50, y, f"Data e Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    y -= 20
    c.drawString(50, y, f"EPSG Detectado: {epsg if epsg else 'Não identificado'}")
    y -= 20
    c.drawString(50, y, f"Quantidade de Feições: {quantidade}")
    y -= 30

    # Tabela de critérios
    data = [["Critério Avaliado", "Resultado"]]
    for nome, status in criterios:
        simbolo = "✔️" if status else "❌"
        cor = colors.green if status else colors.red
        data.append([nome, (simbolo, cor)])

    table = Table([[linha[0], linha[1][0]] for linha in data], colWidths=[12*cm, 3*cm])
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#DCE6F1")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.black),
    ])

    for i in range(1, len(data)):
        bg = colors.whitesmoke if i % 2 == 0 else colors.lightgrey
        style.add('BACKGROUND', (0, i), (-1, i), bg)
        style.add('TEXTCOLOR', (1, i), (1, i), data[i][1][1])

    table.setStyle(style)
    table.wrapOn(c, width, height)
    table.drawOn(c, 50, y - 20 - (20 * len(data)))

    # Mensagem final
    y_final = y - 40 - (20 * len(data))
    c.setFont("Helvetica-Bold", 13)
    resultado = sucesso
    msg_final = "UPLOAD CONCLUÍDO COM SUCESSO" if resultado else "FALHA NO UPLOAD - VERIFIQUE OS CRITÉRIOS ACIMA"
    cor_final = colors.darkgreen if resultado else colors.darkred
    c.setFillColor(cor_final)
    c.drawCentredString(width / 2, y_final, msg_final)

    c.save()
