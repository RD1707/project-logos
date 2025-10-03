"""
Serviço de geração de PDF para correções
"""
from io import BytesIO
from datetime import datetime
from typing import Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, PageBreak, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from loguru import logger


class PDFService:
    """Serviço para gerar PDFs de correção"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Configura estilos customizados"""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

        # Texto normal
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=10
        ))

    def _add_header(self, canvas_obj, doc):
        """Adiciona cabeçalho nas páginas"""
        canvas_obj.saveState()
        canvas_obj.setFont('Helvetica-Bold', 10)
        canvas_obj.setFillColor(colors.HexColor('#1e40af'))
        canvas_obj.drawString(50, A4[1] - 40, "Redator ENEM - Correção Automática")
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(colors.grey)
        canvas_obj.drawRightString(A4[0] - 50, A4[1] - 40,
                                   f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        canvas_obj.line(50, A4[1] - 50, A4[0] - 50, A4[1] - 50)
        canvas_obj.restoreState()

    def _add_footer(self, canvas_obj, doc):
        """Adiciona rodapé nas páginas"""
        canvas_obj.saveState()
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(colors.grey)
        page_num = canvas_obj.getPageNumber()
        canvas_obj.drawCentredString(A4[0] / 2, 30, f"Página {page_num}")
        canvas_obj.restoreState()

    def _get_score_color(self, score: int, max_score: int = 200) -> colors.Color:
        """Retorna cor baseada no score"""
        percentage = score / max_score
        if percentage >= 0.8:
            return colors.HexColor('#16a34a')  # Verde
        elif percentage >= 0.6:
            return colors.HexColor('#ca8a04')  # Amarelo
        else:
            return colors.HexColor('#dc2626')  # Vermelho

    def gerar_pdf(self, correcao_data: Dict[str, Any]) -> BytesIO:
        """
        Gera PDF da correção

        Args:
            correcao_data: Dados completos da correção incluindo redação

        Returns:
            BytesIO com o PDF gerado
        """
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=50,
                leftMargin=50,
                topMargin=70,
                bottomMargin=50
            )

            # Container para elementos do PDF
            elements = []

            # Título
            title = Paragraph(
                "Correção de Redação ENEM",
                self.styles['CustomTitle']
            )
            elements.append(title)
            elements.append(Spacer(1, 0.2 * inch))

            # Informações da redação
            redacao = correcao_data.get('redacoes', {})
            if redacao.get('titulo'):
                titulo_redacao = Paragraph(
                    f"<b>Título:</b> {redacao['titulo']}",
                    self.styles['CustomBody']
                )
                elements.append(titulo_redacao)

            data_correcao = correcao_data.get('created_at', '')
            if isinstance(data_correcao, str):
                try:
                    data_obj = datetime.fromisoformat(data_correcao.replace('Z', '+00:00'))
                    data_formatada = data_obj.strftime('%d/%m/%Y às %H:%M')
                except:
                    data_formatada = data_correcao
            else:
                data_formatada = str(data_correcao)

            info_data = Paragraph(
                f"<b>Data da Correção:</b> {data_formatada}",
                self.styles['CustomBody']
            )
            elements.append(info_data)
            elements.append(Spacer(1, 0.3 * inch))

            # Score Total em destaque
            score_total = correcao_data.get('score_total', 0)
            score_color = self._get_score_color(score_total, 1000)

            score_data = [
                ['NOTA TOTAL', f'{score_total}/1000']
            ]
            score_table = Table(score_data, colWidths=[3*inch, 2*inch])
            score_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f3f4f6')),
                ('TEXTCOLOR', (0, 0), (0, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (1, 0), (1, 0), score_color),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (0, 0), 14),
                ('FONTSIZE', (1, 0), (1, 0), 20),
                ('PADDING', (0, 0), (-1, -1), 12),
                ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#1e40af')),
            ]))
            elements.append(score_table)
            elements.append(Spacer(1, 0.3 * inch))

            # Competências
            elements.append(Paragraph("Notas por Competência", self.styles['CustomHeading']))

            competencias_data = [
                ['Competência', 'Nota', 'Desempenho']
            ]

            for i in range(1, 6):
                nota = correcao_data.get(f'c{i}', 0)
                perc = (nota / 200) * 100
                comp_color = self._get_score_color(nota, 200)

                competencias_data.append([
                    f'Competência {i}',
                    f'{nota}/200',
                    f'{perc:.0f}%'
                ])

            comp_table = Table(competencias_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
            comp_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('PADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(comp_table)
            elements.append(Spacer(1, 0.3 * inch))

            # Confiança
            confianca = correcao_data.get('confianca', 0)
            confianca_perc = confianca * 100
            nivel_confianca = "Alta" if confianca > 0.85 else "Média" if confianca > 0.70 else "Baixa"

            confianca_text = Paragraph(
                f"<b>Confiança da Correção:</b> {confianca_perc:.1f}% ({nivel_confianca})",
                self.styles['CustomBody']
            )
            elements.append(confianca_text)
            elements.append(Spacer(1, 0.3 * inch))

            # Feedback Geral
            elements.append(Paragraph("Feedback Geral", self.styles['CustomHeading']))
            feedback_geral = correcao_data.get('feedback_geral', 'Sem feedback disponível')
            feedback_para = Paragraph(feedback_geral, self.styles['CustomBody'])
            elements.append(feedback_para)
            elements.append(Spacer(1, 0.3 * inch))

            # Análise Detalhada por Competência
            dados_completos = correcao_data.get('dados_completos', {})
            competencias = dados_completos.get('competencias', [])

            if competencias:
                elements.append(PageBreak())
                elements.append(Paragraph("Análise Detalhada por Competência",
                                        self.styles['CustomTitle']))
                elements.append(Spacer(1, 0.2 * inch))

                for comp in competencias:
                    # Título da competência
                    comp_titulo = Paragraph(
                        f"<b>Competência {comp['numero']}: {comp['nota']}/200</b>",
                        self.styles['CustomHeading']
                    )
                    elements.append(comp_titulo)

                    # Feedback
                    if comp.get('feedback'):
                        feedback = Paragraph(
                            f"<i>{comp['feedback']}</i>",
                            self.styles['CustomBody']
                        )
                        elements.append(feedback)

                    # Pontos fortes
                    if comp.get('pontos_fortes'):
                        elements.append(Paragraph("<b>Pontos Fortes:</b>",
                                                 self.styles['CustomBody']))
                        for pf in comp['pontos_fortes']:
                            pf_para = Paragraph(f"• {pf}", self.styles['CustomBody'])
                            elements.append(pf_para)

                    # Pontos a melhorar
                    if comp.get('pontos_melhorar'):
                        elements.append(Paragraph("<b>Pontos a Melhorar:</b>",
                                                 self.styles['CustomBody']))
                        for pm in comp['pontos_melhorar']:
                            pm_para = Paragraph(f"• {pm}", self.styles['CustomBody'])
                            elements.append(pm_para)

                    elements.append(Spacer(1, 0.2 * inch))

            # Texto da redação
            texto = redacao.get('texto', '')
            if texto:
                elements.append(PageBreak())
                elements.append(Paragraph("Texto da Redação", self.styles['CustomTitle']))
                elements.append(Spacer(1, 0.2 * inch))

                # Dividir texto em parágrafos
                paragrafos = texto.split('\n')
                for para_texto in paragrafos:
                    if para_texto.strip():
                        para = Paragraph(para_texto.strip(), self.styles['CustomBody'])
                        elements.append(para)

            # Gerar PDF
            doc.build(
                elements,
                onFirstPage=self._add_header_footer,
                onLaterPages=self._add_header_footer
            )

            buffer.seek(0)
            logger.info(f"PDF gerado com sucesso para correção {correcao_data.get('id')}")
            return buffer

        except Exception as e:
            logger.error(f"Erro ao gerar PDF: {str(e)}", exc_info=True)
            raise

    def _add_header_footer(self, canvas_obj, doc):
        """Adiciona cabeçalho e rodapé"""
        self._add_header(canvas_obj, doc)
        self._add_footer(canvas_obj, doc)


# Singleton
_pdf_service = None


def get_pdf_service() -> PDFService:
    """Retorna instância singleton do PDFService"""
    global _pdf_service
    if _pdf_service is None:
        _pdf_service = PDFService()
    return _pdf_service
