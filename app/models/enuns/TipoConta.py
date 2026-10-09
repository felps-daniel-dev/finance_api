from enum import StrEnum


class TipoConta(StrEnum):
    CORRENTE = "CORRENTE",
    CARTEIRA = "CARTEIRA",
    CAIXA    = "CAIXA"