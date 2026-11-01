"""Gabarito da fidelidade da fala com a memoria autobiografica (C4, M6; docs/ESPEC_MEMORIA_AUTOBIOGRAFICA_DIGIBRAIN_MODULAR.md, 7.1):
cada caso e (fatos, fala) e o resultado da conferencia deterministica de `digilab_fala_livre/memoria_fala.py`. O espelho em
web/app/src/falaMemoria.ts e conferido contra este arquivo (web/app/test/fala_memoria.test.ts). Nenhuma LLM, nenhuma vida.

    python experiments/exportar_gabarito_fala_memoria.py      # grava web/app/test/gabaritos/fala_memoria_python.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab_fala_livre import memoria_fala as mf  # noqa: E402

ARQUIVO = RAIZ / "web" / "app" / "test" / "gabaritos" / "fala_memoria_python.json"

_E1 = {"id": "E1", "tipo": "estado", "texto": "fome alto"}
_M1 = {"id": "M1", "tipo": "memoria", "texto": "(curto prazo, bronca) o dono me repreendeu, ha 20 min"}
_SEM = {"id": "Q1", "tipo": mf.TIPO_SEM_LEMBRANCA, "texto": "nenhuma lembranca recuperada nesta decisao"}
_LEM = {"id": "Q1", "tipo": mf.TIPO_LEMBRANCA, "texto": "lembrei do episodio 4 (comer podre, negativo)"}
_DEC = {"id": "Q2", "tipo": mf.TIPO_DECIDIU, "texto": "a lembranca do episodio 4 (comer podre, negativo) mudou o que fiz agora"}
_ZSOBE = {"id": "Z1", "tipo": mf.TIPO_FACETA, "texto": "cautela comida subiu no dia 3 (episodios 4, 7)"}

# (nome, fatos, fala): as tres lacunas da auditoria, uma por uma, e os casos que a fala pode dizer
CASOS = (
    ("desligada_nao_confere", [_E1, _M1], "Lembrei do podre e fiquei mais cauteloso, porque lembrei."),
    ("lacuna1_lembranca_sem_registro", [_E1, _SEM], "Lembrei de comer aquilo podre."),
    ("lacuna1_lembranca_com_registro", [_E1, _LEM], "Lembrei que comi podre."),
    ("lacuna1_outro_episodio", [_E1, _LEM], "Lembrei de brincar com a bola."),
    ("lacuna2_causa_sem_sonda", [_E1, _M1, _LEM], "Evitei a fruta porque lembrei do podre."),
    ("lacuna2_causa_com_sonda", [_E1, _LEM, _DEC], "Evitei esse podre porque lembrei dele."),
    ("lacuna2_causa_por_fato_de_memoria_velha", [_E1, _M1, _SEM], "Fiquei esperando porque lembro da bronca."),
    ("lacuna3_faceta_com_registro", [_E1, _SEM, _ZSOBE], "Fiquei mais cauteloso com a comida."),
    ("lacuna3_faceta_sentido_contrario", [_E1, _SEM, _ZSOBE], "Fiquei menos cauteloso com a comida."),
    ("lacuna3_faceta_sem_registro", [_E1, _SEM], "Fiquei mais ousado, mais corajoso."),
    ("lacuna3_outra_faceta", [_E1, _SEM, _ZSOBE], "Fiquei mais apegado a voce."),
    ("negacao_nao_alega", [_E1, _SEM], "Nao lembro disso."),
    ("negacao_com_afirmacao", [_E1, _LEM, _DEC], "Nao lembro bem, mas fui comer porque lembrei do podre."),
    ("sem_alegacao", [_E1, _SEM], "Estou com fome, vamos comer?"),
)


def calcular() -> list[dict]:
    return [{"nome": n, "fatos": f, "fala": fala, "alegacoes": mf.conferir(fala, f)} for n, f, fala in CASOS]


def main() -> None:
    ARQUIVO.write_text(json.dumps({"versao": 1, "casos": calcular()}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("gravado", ARQUIVO)


if __name__ == "__main__":
    main()
