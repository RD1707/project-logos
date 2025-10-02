"""
Gerador de Feedback - Cria feedback personalizado por competência
"""
from typing import Dict, List
from loguru import logger

from app.models.schemas.correcao import Competencia, ErroGramatical, AnaliseEstrutura


class FeedbackGenerator:
    """
    Gera feedback detalhado para cada competência do ENEM
    """

    def gerar_feedback_competencia(
        self,
        numero: int,
        nota: int,
        texto: str,
        erros_gramaticais: List[ErroGramatical],
        analise_estrutura: AnaliseEstrutura
    ) -> Competencia:
        """
        Gera feedback para uma competência específica

        Args:
            numero: Número da competência (1-5)
            nota: Nota da competência (0-200)
            texto: Texto da redação
            erros_gramaticais: Lista de erros identificados
            analise_estrutura: Análise da estrutura

        Returns:
            Competencia com feedback completo
        """
        if numero == 1:
            return self._feedback_c1(nota, erros_gramaticais)
        elif numero == 2:
            return self._feedback_c2(nota, texto, analise_estrutura)
        elif numero == 3:
            return self._feedback_c3(nota, analise_estrutura)
        elif numero == 4:
            return self._feedback_c4(nota, analise_estrutura)
        elif numero == 5:
            return self._feedback_c5(nota, texto)
        else:
            raise ValueError(f"Competência inválida: {numero}")

    def _feedback_c1(
        self,
        nota: int,
        erros: List[ErroGramatical]
    ) -> Competencia:
        """
        Competência 1: Domínio da norma culta da língua portuguesa
        """
        num_erros = len(erros)

        # Feedback baseado na nota
        if nota >= 180:
            nivel = "Excelente"
            feedback = "Demonstra pleno domínio da norma culta da língua portuguesa."
        elif nota >= 160:
            nivel = "Muito Bom"
            feedback = "Demonstra bom domínio da norma culta, com poucos desvios gramaticais."
        elif nota >= 140:
            nivel = "Bom"
            feedback = "Demonstra domínio adequado da norma culta, mas com alguns desvios."
        elif nota >= 120:
            nivel = "Regular"
            feedback = "Demonstra domínio mediano da norma culta, com vários desvios."
        else:
            nivel = "Insuficiente"
            feedback = "Apresenta muitos desvios gramaticais que prejudicam a compreensão."

        # Pontos fortes
        pontos_fortes = []
        if num_erros < 3:
            pontos_fortes.append("Poucos erros gramaticais identificados")
        if nota >= 160:
            pontos_fortes.append("Boa estruturação de períodos")
            pontos_fortes.append("Uso adequado da pontuação")

        # Pontos a melhorar
        pontos_melhorar = []
        if num_erros > 5:
            pontos_melhorar.append(f"Foram identificados {num_erros} erros gramaticais")

        # Contar tipos de erros
        erros_ortografia = [e for e in erros if e.tipo == "ortografia"]
        erros_gramatica = [e for e in erros if e.tipo == "gramática"]

        if erros_ortografia:
            pontos_melhorar.append(f"Atenção a {len(erros_ortografia)} erros de ortografia")
        if erros_gramatica:
            pontos_melhorar.append(f"Revisar {len(erros_gramatica)} desvios gramaticais")

        # Trechos destacados
        trechos_destacados = []
        for erro in erros[:3]:  # Mostrar até 3 exemplos
            trechos_destacados.append({
                "texto": erro.trecho,
                "tipo": "erro",
                "explicacao": f"{erro.tipo.capitalize()}: {erro.mensagem}"
            })

        feedback_detalhado = (
            f"{nivel} - {feedback} "
            f"Foram identificados {num_erros} desvios gramaticais/ortográficos."
        )

        return Competencia(
            numero=1,
            nota=nota,
            feedback=feedback_detalhado,
            pontos_fortes=pontos_fortes,
            pontos_melhorar=pontos_melhorar,
            trechos_destacados=trechos_destacados
        )

    def _feedback_c2(
        self,
        nota: int,
        texto: str,
        estrutura: AnaliseEstrutura
    ) -> Competencia:
        """
        Competência 2: Compreensão da proposta e aplicação de conceitos
        """
        if nota >= 180:
            nivel = "Excelente"
            feedback = "Desenvolve muito bem o tema com argumentação consistente e repertório sociocultural produtivo."
        elif nota >= 160:
            nivel = "Muito Bom"
            feedback = "Desenvolve bem o tema com boa argumentação e repertório adequado."
        elif nota >= 140:
            nivel = "Bom"
            feedback = "Desenvolve o tema de forma adequada, com argumentação suficiente."
        elif nota >= 120:
            nivel = "Regular"
            feedback = "Desenvolve o tema de forma mediana, argumentação pode ser aprimorada."
        else:
            nivel = "Insuficiente"
            feedback = "Apresenta desenvolvimento superficial do tema."

        pontos_fortes = []
        if estrutura.tem_introducao:
            pontos_fortes.append("Boa apresentação do tema na introdução")
        if nota >= 160:
            pontos_fortes.append("Argumentação consistente")

        pontos_melhorar = []
        if not estrutura.tem_introducao:
            pontos_melhorar.append("Desenvolver melhor a introdução contextualizando o tema")
        if nota < 160:
            pontos_melhorar.append("Aprofundar a argumentação com mais repertório sociocultural")

        return Competencia(
            numero=2,
            nota=nota,
            feedback=f"{nivel} - {feedback}",
            pontos_fortes=pontos_fortes,
            pontos_melhorar=pontos_melhorar,
            trechos_destacados=[]
        )

    def _feedback_c3(
        self,
        nota: int,
        estrutura: AnaliseEstrutura
    ) -> Competencia:
        """
        Competência 3: Seleção, relação e organização de informações
        """
        if nota >= 180:
            nivel = "Excelente"
            feedback = "Apresenta informações muito bem selecionadas, relacionadas e organizadas em defesa do ponto de vista."
        elif nota >= 160:
            nivel = "Muito Bom"
            feedback = "Apresenta informações bem selecionadas e organizadas em defesa do ponto de vista."
        elif nota >= 140:
            nivel = "Bom"
            feedback = "Apresenta informações adequadamente selecionadas e organizadas."
        else:
            nivel = "Regular"
            feedback = "A seleção e organização de informações pode ser aprimorada."

        pontos_fortes = []
        if estrutura.tem_desenvolvimento:
            pontos_fortes.append("Boa organização do desenvolvimento")
        if estrutura.num_paragrafos >= 4:
            pontos_fortes.append("Estrutura bem dividida em parágrafos")

        pontos_melhorar = []
        if estrutura.num_paragrafos < 3:
            pontos_melhorar.append("Desenvolver mais parágrafos para melhor organizar as ideias")
        if nota < 160:
            pontos_melhorar.append("Melhorar a relação entre as informações apresentadas")

        return Competencia(
            numero=3,
            nota=nota,
            feedback=f"{nivel} - {feedback}",
            pontos_fortes=pontos_fortes,
            pontos_melhorar=pontos_melhorar,
            trechos_destacados=[]
        )

    def _feedback_c4(
        self,
        nota: int,
        estrutura: AnaliseEstrutura
    ) -> Competencia:
        """
        Competência 4: Mecanismos linguísticos (coesão)
        """
        uso_conectivos = estrutura.uso_conectivos

        if nota >= 180:
            nivel = "Excelente"
            feedback = "Articula muito bem as partes do texto com uso diversificado de conectivos."
        elif nota >= 160:
            nivel = "Muito Bom"
            feedback = "Articula bem as partes do texto com uso adequado de conectivos."
        elif nota >= 140:
            nivel = "Bom"
            feedback = "Articula as partes do texto com uso suficiente de recursos coesivos."
        else:
            nivel = "Regular"
            feedback = "A articulação entre as partes do texto pode ser melhorada."

        pontos_fortes = []
        if uso_conectivos in ["excelente", "adequado"]:
            pontos_fortes.append(f"Uso {uso_conectivos} de conectivos")
        if estrutura.coesao_score >= 0.7:
            pontos_fortes.append("Boa coesão textual")

        pontos_melhorar = []
        if uso_conectivos in ["insuficiente", "suficiente"]:
            pontos_melhorar.append("Utilizar mais conectivos para articular melhor as ideias")
        if estrutura.coesao_score < 0.6:
            pontos_melhorar.append("Evitar repetições excessivas de palavras")

        return Competencia(
            numero=4,
            nota=nota,
            feedback=f"{nivel} - {feedback}",
            pontos_fortes=pontos_fortes,
            pontos_melhorar=pontos_melhorar,
            trechos_destacados=[]
        )

    def _feedback_c5(
        self,
        nota: int,
        texto: str
    ) -> Competencia:
        """
        Competência 5: Proposta de intervenção
        """
        texto_lower = texto.lower()

        # Detectar elementos da proposta
        tem_agente = any(palavra in texto_lower for palavra in [
            "governo", "estado", "ministério", "sociedade", "escola", "mídia"
        ])
        tem_acao = any(palavra in texto_lower for palavra in [
            "deve", "precisa", "necessário", "criar", "implementar", "promover"
        ])
        tem_meio = any(palavra in texto_lower for palavra in [
            "através", "por meio", "mediante", "com", "usando"
        ])

        if nota >= 180:
            nivel = "Excelente"
            feedback = "Elabora muito bem proposta de intervenção completa, detalhada e articulada à discussão."
        elif nota >= 160:
            nivel = "Muito Bom"
            feedback = "Elabora bem proposta de intervenção relacionada ao tema e articulada à discussão."
        elif nota >= 140:
            nivel = "Bom"
            feedback = "Elabora proposta de intervenção relacionada ao tema."
        else:
            nivel = "Regular"
            feedback = "Proposta de intervenção pode ser mais detalhada e completa."

        pontos_fortes = []
        if tem_agente:
            pontos_fortes.append("Identifica agente(s) responsável(is) pela ação")
        if tem_acao:
            pontos_fortes.append("Apresenta ação(ões) a serem realizadas")
        if tem_meio:
            pontos_fortes.append("Detalha meio(s) de execução")

        pontos_melhorar = []
        if not tem_agente:
            pontos_melhorar.append("Especificar quem deve executar a proposta")
        if not tem_acao:
            pontos_melhorar.append("Detalhar as ações concretas a serem tomadas")
        if not tem_meio:
            pontos_melhorar.append("Explicar como a proposta será executada")
        if nota < 160:
            pontos_melhorar.append("Melhorar a articulação da proposta com a discussão desenvolvida")

        return Competencia(
            numero=5,
            nota=nota,
            feedback=f"{nivel} - {feedback}",
            pontos_fortes=pontos_fortes,
            pontos_melhorar=pontos_melhorar,
            trechos_destacados=[]
        )

    def gerar_feedback_geral(
        self,
        score_total: int,
        competencias: List[Competencia],
        confianca: float
    ) -> str:
        """
        Gera feedback geral sobre a redação

        Args:
            score_total: Nota total
            competencias: Lista de competências avaliadas
            confianca: Nível de confiança da correção

        Returns:
            Feedback geral em texto
        """
        # Classificar nota
        if score_total >= 900:
            nivel = "Excelente"
        elif score_total >= 800:
            nivel = "Muito Bom"
        elif score_total >= 700:
            nivel = "Bom"
        elif score_total >= 600:
            nivel = "Regular"
        else:
            nivel = "Precisa Melhorar"

        # Identificar melhor e pior competência
        melhor_comp = max(competencias, key=lambda c: c.nota)
        pior_comp = min(competencias, key=lambda c: c.nota)

        feedback = (
            f"Sua redação obteve nota {score_total}/1000 (nível {nivel}). "
            f"Seu melhor desempenho foi na Competência {melhor_comp.numero} ({melhor_comp.nota}/200). "
            f"A Competência {pior_comp.numero} ({pior_comp.nota}/200) pode ser aprimorada. "
        )

        if confianca < 0.70:
            feedback += "Recomenda-se validação da correção por um professor."

        return feedback

    def gerar_resumo_avaliacao(self, score_total: int) -> str:
        """Gera resumo breve da avaliação"""
        if score_total >= 900:
            return f"Nota {score_total}/1000 - Nível Excelente"
        elif score_total >= 800:
            return f"Nota {score_total}/1000 - Nível Muito Bom"
        elif score_total >= 700:
            return f"Nota {score_total}/1000 - Nível Bom"
        elif score_total >= 600:
            return f"Nota {score_total}/1000 - Nível Regular"
        else:
            return f"Nota {score_total}/1000 - Precisa Melhorar"
