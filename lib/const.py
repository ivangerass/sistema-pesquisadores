"""Constantes do sistema — listas de valores dos dropdowns."""

APROVACAO = ["APROVADO", "RESERVA", "ELIMINADO", "PENDENTE"]

STATUS_GRUPO = [
    "ADICIONADO AO GRUPO",
    "MENSAGEM ENVIADA",
    "A ADICIONAR",
    "A REMOVER",
    "WPP NAO RECONHECIDO",
    "FORA DO GRUPO",
]

DECISOES = [
    "APROVADO",
    "APROVADO C/ OBS",
    "AJUSTES SIMPLES",
    "AJUSTES IMPORTANTES",
    "ADVERTÊNCIA FINAL",
    "ELIMINADO",
    "AUDITORIA PENDENTE",
    "TITULAR (a ativar)",
    "PENDENTE",
]

RODADAS = ["R1", "R2", "R3", "R4", "R5"]

STATUS_PAGAMENTO = [
    "A definir",
    "LIBERADO",
    "PAGO",
    "SUSPENSO",
    "BLOQUEADO (audit. pendente)",
]


def cor_decisao(d: str) -> str:
    """Retorna cor (CSS) para uma decisão."""
    if d in ("ELIMINADO", "ADVERTÊNCIA FINAL"):
        return "#C00000"
    if d in ("AJUSTES IMPORTANTES", "AUDITORIA PENDENTE"):
        return "#BF8F00"
    if d in ("APROVADO", "APROVADO C/ OBS"):
        return "#548235"
    return "#404040"


def cor_risco(r: str) -> str:
    if r == "SEM COBERTURA":
        return "#C00000"
    if r == "BAIXO":
        return "#BF8F00"
    return "#548235"
