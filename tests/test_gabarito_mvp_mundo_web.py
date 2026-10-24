"""O gabarito do laco do pet com o mundo para o MVP (web/app/test/gabaritos/mvp_mundo_python.json; docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md,
a etapa 0, para o G-PAR da etapa 1) esta em dia com o Python, byte a byte.
Se mudar o corpo, o mundo ou o laco do motor com eles, rode `python experiments/exportar_gabarito_mvp_mundo.py`: a etapa 1 do MVP confere
o TS contra este arquivo.

- O arquivo em disco e o que o exportador gera hoje, byte a byte (o G2 do lado Python do MVP).
- Ele cobre o laco: a comida posta pelo dono, o andar, o consumo com o estimulo no corpo e os receptores, em toda decisao.
- Gravar nao muda a vida: o motor que grava da o mesmo log e o mesmo resumo que o motor de hoje sem gravar.
Sementes: so as dos testes.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import exportar_gabarito_mvp_mundo as G  # noqa: E402

from digilab.config import CONFIG_PADRAO  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.motor_corpo import com_corpo  # noqa: E402
from digilab.mundo import DonoComLugar, MotorMundo, simular_vida_mundo  # noqa: E402

TEXTO = G.ARQUIVO.read_text(encoding="utf-8")
GRAVADO = json.loads(TEXTO)


def test_o_gabarito_esta_em_dia_byte_a_byte():
    assert TEXTO == json.dumps(G.gerar(), sort_keys=True, separators=(",", ":")) + "\n"


def test_o_gabarito_cobre_o_laco():
    vidas = GRAVADO["vidas"]
    assert [v["semente"] for v in vidas] == [101, 303, 404, 505] and all(v["semente"] in bv.SEMENTES_TESTE for v in vidas)
    assert {v["cerebro"] for v in vidas} == {"a_v11", "instinto"} and {v["lugar"] for v in vidas} == {"comedouro", "perto", "longe"}
    ops = [o for v in vidas for o in v["traco"]]
    dec = [o for o in ops if o["op"] == "decisao"]
    assert any(o["op"] == "deixar_comida" for o in ops)                          # a comida posta num lugar
    assert all("corpo_antes" in o and "corpo_depois" in o for o in dec)
    estimulos = [e[0] for o in dec for e in o["corpo_depois"]["estimulos"]]
    assert {"pet", "andar", "comida"} <= set(estimulos)
    com_comida = [o for o in dec if any(e[0] == "comida" for e in o["corpo_depois"]["estimulos"])]
    assert len(com_comida) >= 20 and all(o["ocorrido"]["comeu"] is not None for o in com_comida)
    # o consumo chega ao corpo: o quimico da fome cai na decisao em que o pet comeu a racao madura (o corpo do v11 nao tem a digestao: o
    # `alimento` fica em zero, e a racao tira da fome direto)
    racao = [o for o in com_comida if o["ocorrido"]["comeu"]["tipo"] == "racao" and o["ocorrido"]["comeu"]["situacao"] == "madura"]
    assert len(racao) >= 10 and all(o["corpo_antes"]["q"]["fome"] > 0 for o in racao)
    assert all(o["corpo_depois"]["q"]["fome"] < o["corpo_antes"]["q"]["fome"] for o in racao)
    assert all(o["corpo_antes"]["q"]["alimento"] == o["corpo_depois"]["q"]["alimento"] == 0 for o in racao)
    # o andar: decisoes com deslocamento
    assert sum(1 for o in dec if o["ocorrido"] and o["ocorrido"]["deslocamento"] > 0) >= 50
    # os receptores do corpo do v11 com o mundo (a curiosidade so existe com o mundo)
    receptores = set(dec[0]["corpo_antes"]["receptores"])
    assert {"fome", "energia", "humor", "curiosidade"} <= receptores


def test_gravar_nao_muda_a_vida():
    nome, cerebro, dono, lugar, s = G.VIDAS[0]
    gravada = GRAVADO["vidas"][0]
    b = G._bancada()
    espec = bv.EspecVida(dono, G.gl.BRACO_V11, s)
    cc = b.cfg_corpo_de(espec)
    fm = (lambda p, cfg, sem: com_corpo(MotorMundo)(p, cfg, sem, obediencia_desligada=True, cfg_mundo=G.CM,  # noqa: E731
                                                    cfg_corpo=cc))
    d = DonoComLugar(criar_dono(dono), lugar, s, dono, G.CM)
    m = simular_vida_mundo(dono, d, b.politica(espec, CONFIG_PADRAO), s, G.DIAS, 16 * G.DIAS, fm, rotulo_dono=dono).motor
    assert [e.para_dict() for e in m.log] == gravada["log"]
    resumo = m.resumo_mundo_fisico()
    del resumo["rngs"]
    assert json.loads(json.dumps(resumo)) == gravada["resumo"]
    assert dict(m.corpo.q) == gravada["corpo_fim"]["q"]
