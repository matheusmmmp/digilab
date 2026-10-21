"""A bancada da V2, módulo `faixas`.

As sementes dos testes, as bases, as faixas reservadas e queimadas, os prefixos e as unidades derivadas.

Parte do pacote `experiments/bancada/` (rodada de saúde, etapa 3; docs/TAREFA_V2_SAUDE.md). O texto de cada definição é o de antes,
movido de `experiments/bancada_v2.py` sem mudança (tools/dividir_bancada.py; a prova pela AST em docs/historico/bancada_mapa.json).
O `experiments/bancada_v2.py` continua sendo a porta de entrada: ele reexporta todo nome daqui.
"""
from __future__ import annotations

from digilab.protocol import derivar_semente


SEMENTES_TESTE = frozenset({101, 202, 303, 404, 505})


# ------------------------------------------------------------------ unidades derivadas (E3)

BASES_EXPERIMENTO_MAIOR = {"calibracao": (14101, 14202, 14303, 14404, 14505),
                           "validacao": (30101, 30202, 30303, 30404, 30505)}   # adendo 4.1: a 15101...15505 ficou queimada
BASES_N6 = {"calibracao": (19101, 19202, 19303, 19404, 19505), "validacao": (20101, 20202, 20303, 20404, 20505)}
BASES_N7 = {"calibracao": (21101, 21202, 21303, 21404, 21505), "validacao": (22101, 22202, 22303, 22404, 22505)}
BASES_COMPARACAO = {"calibracao": (28101, 28202, 28303, 28404, 28505), "validacao": (29101, 29202, 29303, 29404, 29505)}
# o prefixo das unidades derivadas de cada plano (regra E3): semente derivar_semente(prefixo, b, k), genoma
# derivar_semente(prefixo + "-genoma", b, k) (plano do N6, secao 12.2; plano do N7, secao 12.2; o da comparacao dos cerebros,
# PLANO_ANALISE_V2_COMPARACAO_CEREBROS, secao 6.2; o do mundo fisico, PLANO_ANALISE_V2_MUNDO_FISICO, secao 4; o do corpo,
# PLANO_ANALISE_V2_CORPO_DRIVES, secao 4; o do banheiro, PLANO_ANALISE_V2_BANHEIRO, secao 3; o dos dois pets, PLANO_ANALISE_V2_DOIS_PETS,
# secao 8; o da rede de si, PLANO_ANALISE_V2_REDE_DE_SI, secao 8; o do pet que pensa, PLANO_ANALISE_V2_PET_QUE_PENSA, secao 8; o da
# competicao entre as regras, PLANO_ANALISE_V2_V3_COMPETICAO, secao 4)
PREFIXOS_UNIDADES = ("experimento-maior", "n6", "n7", "comparacao-cerebros", "mundo", "corpo", "banheiro", "dois_pets", "rede_de_si",
                     "pet_que_pensa", "competicao")
# faixas queimadas: continuam reservadas e nao podem ser usadas para nada (adendo 4.1 do PLANO_ANALISE_V2_EXPERIMENTO_MAIOR)
FAIXAS_QUEIMADAS = ((15101, 15505, "a validacao antiga do experimento maior: run indevida parada em 2026-10-06 (PR #183)"),)
# faixas reservadas ou ja usadas no repositorio (fonte ao lado); o teste tambem varre experiments/configs/. Intervalos fechados.
FAIXAS_RESERVADAS = (
    (101, 1010, "testes (101...505) e ovos da personalidade (101...1010)"),
    (1101, 1505, "baterias do combate V2 (configs bateria_*)"),
    (2101, 2505, "validacao do combate V2"),
    (3101, 3505, "calibracao: V2.1, L1, vinculo B"),
    (4101, 4505, "validacao: V2.1, V21D, equilibrio, L1"),
    (5101, 5505, "validacao do vinculo B"),
    (6101, 6505, "A1, calibracao"), (7101, 7505, "A1, validacao"),
    (8101, 8505, "N3, calibracao"), (9101, 9505, "N3, validacao"),
    (10101, 10505, "N4, calibracao"), (11101, 11505, "N4, validacao"),
    (12101, 12505, "N5, calibracao (reservada)"), (13101, 13505, "N5, validacao (reservada)"),
    (14101, 14505, "experimento maior, bases da calibracao"),
    (15101, 15505, "QUEIMADA: experimento maior, a validacao antiga (adendo 4.1; run indevida parada em 2026-10-06, PR #183); nao usar"),
    (16101, 16505, "N11 cerebros, calibracao (ROADMAP_V2, secao 6; substituida pela C-8, nao usar)"),
    (17101, 17505, "N11 cerebros, validacao (ROADMAP_V2, secao 6; substituida pela C-8, nao usar)"),
    (18101, 18505, "revisao do aprendiz, so calibracao (V2_RODADA_5)"),
    (19101, 19505, "N6, calibracao (PLANO_ANALISE_V2_N6, N6-9)"), (20101, 20505, "N6, validacao (PLANO_ANALISE_V2_N6, N6-9)"),
    (21101, 21505, "N7, calibracao (PLANO_ANALISE_V2_N7, secao 12.1)"), (22101, 22505, "N7, validacao (PLANO_ANALISE_V2_N7, secao 12.1)"),
    (28101, 28505, "comparacao dos cerebros: calibracao de B e C e piloto (PLANO_ANALISE_V2_COMPARACAO_CEREBROS, C-8)"),
    (29101, 29505, "comparacao dos cerebros: validacao de A, B e C (PLANO_ANALISE_V2_COMPARACAO_CEREBROS, C-8)"),
    (30101, 30505, "experimento maior, bases da validacao (adendo 4.1 do PLANO_ANALISE_V2_EXPERIMENTO_MAIOR)"),
    (31101, 31505, "mundo fisico, calibracao e piloto do N (PLANO_ANALISE_V2_MUNDO_FISICO, secao 11, PMF-6)"),
    (32101, 32505, "mundo fisico, validacao (PLANO_ANALISE_V2_MUNDO_FISICO, secao 11, PMF-6)"),
    (33101, 33505, "corpo e drives, calibracao e piloto (PLANO_ANALISE_V2_CORPO_DRIVES, secao 10, PCD-7)"),
    (34101, 34505, "corpo e drives, validacao (PLANO_ANALISE_V2_CORPO_DRIVES, secao 10, PCD-7)"),
    (37101, 37505, "banheiro, calibracao e piloto (PLANO_ANALISE_V2_BANHEIRO, secao 10)"),
    (38101, 38505, "banheiro, validacao (PLANO_ANALISE_V2_BANHEIRO, secao 10)"),
    (39101, 39505, "dois pets, calibracao do K e piloto (PLANO_ANALISE_V2_DOIS_PETS, secao 8, PDP-6)"),
    (40101, 40505, "dois pets, validacao (PLANO_ANALISE_V2_DOIS_PETS, secao 8, PDP-6)"),
    (41101, 41505, "dois pets, adendo do degrau 1b, prevista (PLANO_ANALISE_V2_DOIS_PETS, secoes 8 e 10, PDP-6)"),
    (42101, 42505, "dois pets, adendo dos dois donos, prevista (PLANO_ANALISE_V2_DOIS_PETS, secoes 8 e 10, PDP-6)"),
    (43101, 43505, "rede de si, calibracao e piloto (PLANO_ANALISE_V2_REDE_DE_SI, secao 8, RS-6)"),
    (44101, 44505, "rede de si, validacao (PLANO_ANALISE_V2_REDE_DE_SI, secao 8, RS-6)"),
    (45101, 45505, "pet que pensa (J5), calibracao do g_plano e piloto (PLANO_ANALISE_V2_PET_QUE_PENSA, secao 8, PP-9)"),
    (46101, 46505, "pet que pensa (J5), validacao com a fruta ao lado, rodada em 2026-10-18 (PLANO_ANALISE_V2_PET_QUE_PENSA, secao 8, "
                   "PP-9; nao volta)"),
    (47101, 47505, "mundo com o alvo aprendido, piloto do N (PLANO_ANALISE_V2_MUNDO_ALVO, secao 12, PMA-7)"),
    (48101, 48505, "mundo com o alvo aprendido, validacao (PLANO_ANALISE_V2_MUNDO_ALVO, secao 12, PMA-7)"),
    (49101, 49505, "pet que pensa (J5) com o paladar, calibracao do ganho_gosto e do g_plano e piloto (PLANO_ANALISE_V2_PET_QUE_PENSA, "
                   "adendo 3, A3.5, PJ-5)"),
    (51101, 51505, "pet que pensa (J5) com a fruta ao lado da racao, calibracao do ganho_gosto e do g_plano e piloto "
                   "(PLANO_ANALISE_V2_PET_QUE_PENSA, adendo 5, A5.8, PJ5-6)"),
    (52101, 52505, "pet que pensa (J5), o piloto do adendo 7, rodado em 2026-10-19 (PLANO_ANALISE_V2_PET_QUE_PENSA, A7.8, PJ7-6; "
                   "nao volta)"),
    (53101, 53505, "pet que pensa (J5), reservada para a validacao do adendo 7 e nao usada; substituida pela 55101 (A8.9; nao volta)"),
    (54101, 54505, "pet que pensa (J5), o piloto do adendo 8 (as margens, o N e as premissas; PLANO_ANALISE_V2_PET_QUE_PENSA, A8.9, "
                   "PJ8-6)"),
    (55101, 55505, "pet que pensa (J5), a validacao do adendo 8 (PLANO_ANALISE_V2_PET_QUE_PENSA, A8.9, PJ8-6)"),
    (56101, 56505, "credito por canal ate o alvo (V3-9), o piloto (TAREFA_V2_V3_CREDITO_CANAL, CC-6, decidida pelo Matheus em 2026-10-21)"),
    (57101, 57505, "credito por canal ate o alvo (V3-9), a validacao (TAREFA_V2_V3_CREDITO_CANAL, CC-6, decidida pelo Matheus em "
                   "2026-10-21)"),
    (58101, 58505, "competicao entre as regras urgentes (V3-3/V3-4), o piloto e a calibracao (TAREFA_V2_V3_COMPETICAO, CR-6, decidida "
                   "pelo Matheus em 2026-10-21)"),
    (59101, 59505, "competicao entre as regras urgentes (V3-3/V3-4), a validacao (TAREFA_V2_V3_COMPETICAO, CR-6, decidida pelo Matheus em "
                   "2026-10-21)"),
    (50001, 50020, "analise de poder, piloto"), (60001, 60160, "confirmatoria"), (69001, 69001, "M1, gate G1"),
    (80001, 82004, "linhagem E1 (piloto, genomas e ambientes)"),
    (20260900, 20261800, "fala, voz, comando e bootstraps (sementes de 2026-09/10 e semente + i)"),
)


def unidades_derivadas(bases, k_por_base: int, prefixo: str = "experimento-maior") -> list[dict]:
    """E3 (plano do experimento maior, secao 8.1): a unidade k da base b tem semente derivar_semente(prefixo, b, k) e genoma
    derivar_semente(prefixo + "-genoma", b, k), k = 0..K-1; o prefixo e o do plano (PREFIXOS_UNIDADES: "experimento-maior", o
    padrao; "n6"; "n7"; "comparacao-cerebros"; "mundo"; "corpo"; "banheiro"; "dois_pets"; "rede_de_si"). Falha alto com K < 1, base repetida, prefixo desconhecido ou colisao."""
    if prefixo not in PREFIXOS_UNIDADES:
        raise ValueError(f"prefixo das unidades {prefixo!r}: so {PREFIXOS_UNIDADES}")
    if k_por_base < 1:
        raise ValueError("K precisa ser >= 1")
    bases = list(bases)
    if len(set(bases)) != len(bases):
        raise ValueError(f"base repetida: {bases}")
    out = [{"base": b, "k": k, "semente": derivar_semente(prefixo, b, k),
            "genoma": derivar_semente(f"{prefixo}-genoma", b, k)} for b in bases for k in range(k_por_base)]
    valores = [u["semente"] for u in out] + [u["genoma"] for u in out]
    if len(set(valores)) != len(valores):
        raise ValueError("colisao entre sementes e genomas derivados")
    return out


def na_faixa_reservada(valor: int) -> str | None:
    for lo, hi, fonte in FAIXAS_RESERVADAS:
        if lo <= valor <= hi:
            return fonte
    return None


class SementeSemPlano(RuntimeError):
    pass
