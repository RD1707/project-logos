"""
Analisador Linguístico - Gramática, Ortografia, Coesão e Coerência
"""
import re
from typing import List, Dict, Tuple
from loguru import logger
import language_tool_python

from app.models.schemas.correcao import ErroGramatical, AnaliseEstrutura


class LinguisticAnalyzer:
    """
    Analisa aspectos linguísticos da redação:
    - Gramática e ortografia (LanguageTool)
    - Estrutura (introdução, desenvolvimento, conclusão)
    - Coesão (conectivos, repetições)
    - Coerência (progressão temática)
    """

    def __init__(self):
        logger.info("Inicializando LinguisticAnalyzer")
        # Inicializar LanguageTool para português
        try:
            self.tool = language_tool_python.LanguageTool('pt-BR')
            logger.info("LanguageTool inicializado (pt-BR)")
        except Exception as e:
            logger.error(f"Erro ao inicializar LanguageTool: {str(e)}")
            self.tool = None

        # Lista de conectivos comuns em redações
        self.conectivos = [
            # Adição
            "além disso", "ademais", "também", "igualmente", "ainda", "assim como",
            # Oposição
            "porém", "contudo", "todavia", "entretanto", "no entanto", "mas",
            # Conclusão
            "portanto", "logo", "assim", "por conseguinte", "consequentemente",
            # Explicação
            "pois", "porque", "uma vez que", "visto que", "já que",
            # Exemplificação
            "por exemplo", "como", "tal como", "isto é", "ou seja",
            # Tempo
            "primeiramente", "em seguida", "posteriormente", "finalmente", "por fim"
        ]

    def analisar_completo(self, texto: str) -> Dict[str, any]:
        """
        Análise linguística completa

        Args:
            texto: Texto da redação

        Returns:
            Dict com todos os resultados da análise
        """
        logger.info("Iniciando análise linguística completa")

        # Análise de erros gramaticais
        erros_gramaticais, num_ortografia, num_gramatica = self._analisar_erros(texto)

        # Análise de estrutura
        analise_estrutura = self._analisar_estrutura(texto)

        resultado = {
            "erros_gramaticais": erros_gramaticais,
            "num_erros_ortografia": num_ortografia,
            "num_erros_gramatica": num_gramatica,
            "analise_estrutura": analise_estrutura
        }

        logger.info(
            f"Análise concluída - Erros: {len(erros_gramaticais)}, "
            f"Parágrafos: {analise_estrutura.num_paragrafos}"
        )

        return resultado

    def _analisar_erros(
        self,
        texto: str
    ) -> Tuple[List[ErroGramatical], int, int]:
        """
        Analisa erros gramaticais e ortográficos

        Returns:
            (lista_erros, num_ortografia, num_gramatica)
        """
        erros = []
        num_ortografia = 0
        num_gramatica = 0

        if not self.tool:
            logger.warning("LanguageTool não disponível")
            return erros, num_ortografia, num_gramatica

        try:
            matches = self.tool.check(texto)

            for match in matches:
                # Classificar tipo de erro
                categoria = match.ruleId.split("_")[0].lower()
                if "spell" in categoria or "orthography" in categoria:
                    tipo = "ortografia"
                    num_ortografia += 1
                else:
                    tipo = "gramática"
                    num_gramatica += 1

                erro = ErroGramatical(
                    tipo=tipo,
                    mensagem=match.message,
                    trecho=match.context,
                    sugestao=match.replacements[0] if match.replacements else None,
                    posicao_inicio=match.offset,
                    posicao_fim=match.offset + match.errorLength
                )
                erros.append(erro)

        except Exception as e:
            logger.error(f"Erro ao analisar gramática: {str(e)}")

        return erros, num_ortografia, num_gramatica

    def _analisar_estrutura(self, texto: str) -> AnaliseEstrutura:
        """
        Analisa estrutura da redação

        Returns:
            AnaliseEstrutura
        """
        # Dividir em parágrafos
        paragrafos = self._extrair_paragrafos(texto)
        num_paragrafos = len(paragrafos)

        # Detectar partes da redação
        tem_introducao = self._detectar_introducao(paragrafos)
        tem_desenvolvimento = num_paragrafos >= 3  # Pelo menos 2 parágrafos de desenvolvimento
        tem_conclusao = self._detectar_conclusao(paragrafos)

        # Analisar uso de conectivos
        uso_conectivos = self._analisar_conectivos(texto)

        # Calcular scores de coesão e coerência
        coesao_score = self._calcular_coesao(texto, paragrafos)
        coerencia_score = self._calcular_coerencia(paragrafos)

        return AnaliseEstrutura(
            tem_introducao=tem_introducao,
            tem_desenvolvimento=tem_desenvolvimento,
            tem_conclusao=tem_conclusao,
            num_paragrafos=num_paragrafos,
            uso_conectivos=uso_conectivos,
            coesao_score=coesao_score,
            coerencia_score=coerencia_score
        )

    def _extrair_paragrafos(self, texto: str) -> List[str]:
        """Extrai parágrafos do texto"""
        # Dividir por linha dupla ou ponto final + quebra
        paragrafos = re.split(r'\n\s*\n|\.\s*\n', texto)
        # Limpar e remover vazios
        paragrafos = [p.strip() for p in paragrafos if p.strip()]
        return paragrafos

    def _detectar_introducao(self, paragrafos: List[str]) -> bool:
        """Detecta se há introdução adequada"""
        if not paragrafos:
            return False

        primeiro_paragrafo = paragrafos[0].lower()

        # Palavras/expressões comuns em introduções
        indicadores = [
            "atualmente", "nos dias de hoje", "é sabido", "é notório",
            "a sociedade", "o brasil", "no contexto", "diante",
            "questão", "tema", "problema", "debate"
        ]

        # Se tiver algum indicador, considerar que tem introdução
        return any(ind in primeiro_paragrafo for ind in indicadores)

    def _detectar_conclusao(self, paragrafos: List[str]) -> bool:
        """Detecta se há conclusão adequada"""
        if len(paragrafos) < 2:
            return False

        ultimo_paragrafo = paragrafos[-1].lower()

        # Palavras/expressões comuns em conclusões
        indicadores = [
            "portanto", "logo", "assim", "dessa forma", "desse modo",
            "conclui-se", "concluo", "portanto", "por fim", "finalmente",
            "medidas", "solução", "proposta", "necessário", "deve-se"
        ]

        return any(ind in ultimo_paragrafo for ind in indicadores)

    def _analisar_conectivos(self, texto: str) -> str:
        """Analisa uso de conectivos"""
        texto_lower = texto.lower()

        # Contar conectivos encontrados
        conectivos_encontrados = [
            c for c in self.conectivos
            if c in texto_lower
        ]

        num_conectivos = len(conectivos_encontrados)

        if num_conectivos >= 8:
            return "excelente"
        elif num_conectivos >= 5:
            return "adequado"
        elif num_conectivos >= 3:
            return "suficiente"
        else:
            return "insuficiente"

    def _calcular_coesao(self, texto: str, paragrafos: List[str]) -> float:
        """
        Calcula score de coesão (0-1)
        Baseado em: uso de conectivos, repetições, progressão
        """
        score = 0.5  # Base

        # Bonus por conectivos
        texto_lower = texto.lower()
        num_conectivos = sum(1 for c in self.conectivos if c in texto_lower)
        conectivos_score = min(num_conectivos / 10.0, 0.3)
        score += conectivos_score

        # Penalidade por repetições excessivas
        palavras = texto_lower.split()
        if len(palavras) > 0:
            palavras_unicas = set(palavras)
            diversidade = len(palavras_unicas) / len(palavras)
            if diversidade < 0.4:
                score -= 0.2

        # Garantir entre 0 e 1
        return max(0.0, min(1.0, score))

    def _calcular_coerencia(self, paragrafos: List[str]) -> float:
        """
        Calcula score de coerência (0-1)
        Baseado em: estrutura, progressão temática
        """
        score = 0.5  # Base

        # Bonus por estrutura adequada
        if len(paragrafos) >= 4:
            score += 0.2
        elif len(paragrafos) >= 3:
            score += 0.1

        # Bonus por tamanho adequado dos parágrafos
        tamanhos = [len(p.split()) for p in paragrafos]
        if tamanhos:
            tamanho_medio = sum(tamanhos) / len(tamanhos)
            if 30 <= tamanho_medio <= 80:
                score += 0.1

        # Penalidade por parágrafos muito curtos
        paragrafos_curtos = sum(1 for t in tamanhos if t < 15)
        if paragrafos_curtos > len(paragrafos) / 2:
            score -= 0.2

        return max(0.0, min(1.0, score))


# Instância global
_analyzer_instance: LinguisticAnalyzer = None


def get_linguistic_analyzer() -> LinguisticAnalyzer:
    """Retorna instância global do analisador"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = LinguisticAnalyzer()
    return _analyzer_instance
