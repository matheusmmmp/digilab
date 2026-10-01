"""Vinculo B, previsibilidade + desejo (docs/PLANO_ANALISE_V2_VINCULO.md): desligada, nada muda; ligada, o pedido nao
abre e a coerencia agrupa por (acao do pet, situacao do pet); replay reproduz; registro de parametros a parte, com o hash
da personalidade intacto; gabarito de paridade com a web reproduzivel."""
from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

from digilab.config import (CONFIG_VINCULO, CONFIG_VINCULO_B_LIGADA, CONFIG_VINCULO_SITUACAO,  # noqa: E402
                            ConfigVinculoSituacao)
from digilab.events import AcaoPet, AcaoUsuario, LogDeEventos  # noqa: E402
from digilab.evolucao import ovo  # noqa: E402
from digilab.policy import Observacao  # noqa: E402
from digilab.protocol import (PARAMETROS_VINCULO_B, PROTOCOLO_ARENA_V1_PERSONALIDADE, Status, hash_protocolo,  # noqa: E402
                              validar_parametros_vinculo_b, vinculo_b_nao_referendados)
from digilab.temperamento import sortear  # noqa: E402
from digilab.treino import reproduzir_com_feedback  # noqa: E402
from digilab.treino_vida import BRACOS_TREINO, fabricas_treino, simular_vida_treino  # noqa: E402
from digilab.vinculo import Vinculo, situacao_de  # noqa: E402
from exportar_gabarito_vinculo import SAIDA as GABARITO_WEB, gerar  # noqa: E402


def _obs(fome=0.9, higiene=0.9, energia=0.9, hora_tick=600):
    return Observacao(vetor_estado=(fome, higiene, energia, 0.5, 1.0, 0.0, 0.0, hora_tick / 1440), ticks_desde_cuidado=0, total_cuidados=0)


def _vida(braco, s, dias, cfg_b):
    esp, _ = ovo(s)
    return simular_vida_treino(braco, s, dias, esp, sortear(s), cfg_vinculo_situacao=cfg_b), esp


def test_desligada_e_byte_a_byte_o_vinculo_de_sempre():
    assert not CONFIG_VINCULO_SITUACAO.ligada
    for b in ("atencioso", "aleatorio"):
        v0, _ = _vida(b, 3101, 2, None)
        v1, _ = _vida(b, 3101, 2, CONFIG_VINCULO_SITUACAO)
        assert v0.motor.log.para_jsonl() == v1.motor.log.para_jsonl()
        assert v0.motor.vinculo.serie == v1.motor.vinculo.serie
        assert v0.motor.vinculo.para_dict() == v1.motor.vinculo.para_dict()
        assert "variante" not in v0.motor.vinculo.para_dict()
    assert Vinculo().cs is CONFIG_VINCULO_SITUACAO


def test_situacao_tres_bits_com_os_limiares_do_pet():
    cs = CONFIG_VINCULO_B_LIGADA
    assert situacao_de(_obs().vetor_estado, cs) == "000"
    assert situacao_de(_obs(fome=0.49).vetor_estado, cs) == "100"          # necessidade baixa: min(fome, higiene) < 0,5
    assert situacao_de(_obs(higiene=0.2, energia=0.2).vetor_estado, cs) == "110"
    assert situacao_de(_obs(hora_tick=1320).vetor_estado, cs) == "001"     # 22:00 e noite; 06:59 tambem; 07:00 nao
    assert situacao_de(_obs(hora_tick=419).vetor_estado, cs) == "001"
    assert situacao_de(_obs(hora_tick=420).vetor_estado, cs) == "000"
    # a hora vem do vetor (tick/1440) e e arredondada: nenhum tick do dia cai na hora errada
    assert all(situacao_de(_obs(hora_tick=t).vetor_estado, cs)[2] == ("1" if (t >= 1320 or t < 420) else "0") for t in range(1440))


def test_ligada_nao_abre_pedido_e_agrupa_a_coerencia_por_situacao():
    v = Vinculo(CONFIG_VINCULO, CONFIG_VINCULO_B_LIGADA)
    v.decisao(_obs(fome=0.1), AcaoPet.CHAMAR_ATENCAO, 600, None)
    assert v.pedidos == [] and v.situacao_atual == "100"
    v.acao_dono(AcaoUsuario.ALIMENTAR, 615, AcaoPet.CHAMAR_ATENCAO, 0)
    assert v.serie == [] and v.valor == CONFIG_VINCULO.inicial                 # cuidado nao e amostra na B
    # brincar descansado (000) elogiado; brincar cansado (010) repreendido: situacoes diferentes, sem amostra de coerencia
    v.decisao(_obs(), AcaoPet.BRINCAR, 630, None)
    v.acao_dono(AcaoUsuario.ELOGIAR, 645, AcaoPet.BRINCAR, 1)
    v.decisao(_obs(energia=0.1), AcaoPet.BRINCAR, 660, None)
    v.acao_dono(AcaoUsuario.REPREENDER, 675, AcaoPet.BRINCAR, 2)
    assert [c for _, _, c, _ in v.serie] == []
    # de novo brincar descansado elogiado: mesma situacao, mesmo sinal -> amostra 1
    v.decisao(_obs(), AcaoPet.BRINCAR, 690, None)
    v.acao_dono(AcaoUsuario.ELOGIAR, 705, AcaoPet.BRINCAR, 3)
    assert [c for _, _, c, _ in v.serie] == ["coerencia"]
    assert v.valor == CONFIG_VINCULO.inicial + CONFIG_VINCULO.alfa * (1.0 - CONFIG_VINCULO.inicial)
    assert sorted(v.feedbacks) == ["brincar|000", "brincar|010"]
    assert v.para_dict()["variante"] == "b"
    # o vinculo de hoje, com as mesmas chamadas, agrupa so pela acao e pune o sinal trocado
    h = Vinculo()
    h.decisao(_obs(), AcaoPet.BRINCAR, 630, None)
    h.acao_dono(AcaoUsuario.ELOGIAR, 645, AcaoPet.BRINCAR, 1)
    h.decisao(_obs(energia=0.1), AcaoPet.BRINCAR, 660, None)
    h.acao_dono(AcaoUsuario.REPREENDER, 675, AcaoPet.BRINCAR, 2)
    assert [(c, round(val, 6)) for _, val, c, _ in h.serie] == [("coerencia", round(0.5 + 0.1 * (0.0 - 0.5), 6))]


def test_desejo_ajustes_pausa_e_teto_continuam_na_variante_b():
    v = Vinculo(CONFIG_VINCULO, CONFIG_VINCULO_B_LIGADA)
    from digilab.desejo import Desejo
    v.decisao(_obs(), AcaoPet.OCIOSO, 600, Desejo(600, "vontade", "comer", 0.8))
    v.acao_dono(AcaoUsuario.ALIMENTAR, 630, AcaoPet.OCIOSO, 0)
    assert [c for _, _, c, _ in v.serie] == ["desejo"]
    v.ajustar(640, "forcar", -0.05, 1)
    v._amostra(650, "pausa", 1.0, 1.0, None)
    v.limitar(660, 0.6, "sombria")
    assert [c for _, _, c, _ in v.serie] == ["desejo", "forcar", "pausa"] and v.teto == 0.6


def test_vida_b_roda_sem_pedido_e_o_replay_reproduz():
    for b in BRACOS_TREINO:
        v, esp = _vida(b, 3202, 2, CONFIG_VINCULO_B_LIGADA)
        m = v.motor
        assert m.vinculo.cs.ligada and m.vinculo.pedidos == []
        assert "atendimento" not in {c for _, _, c, _ in m.vinculo.serie}
        fp, fm = fabricas_treino(3202, esp, sortear(3202), cfg_vinculo_situacao=CONFIG_VINCULO_B_LIGADA)
        r = reproduzir_com_feedback(LogDeEventos.de_jsonl(m.log.para_jsonl()), fp, semente=3202, fabrica_motor=fm)
        assert r.vinculo.serie == m.vinculo.serie and r.vinculo.para_dict() == m.vinculo.para_dict()
        assert r.estado() == m.estado() and r.resumo_treino() == m.resumo_treino()


def test_registro_de_parametros_a_parte_e_hash_da_personalidade_intacto():
    validar_parametros_vinculo_b()
    assert set(PARAMETROS_VINCULO_B) == {"ConfigVinculoSituacao.ligada", "ConfigVinculoSituacao.limiar_necessidade",
                                         "ConfigVinculoSituacao.limiar_energia"}
    assert PARAMETROS_VINCULO_B["ConfigVinculoSituacao.ligada"].status is Status.DECIDIDO
    assert sorted(vinculo_b_nao_referendados()) == ["ConfigVinculoSituacao.limiar_energia", "ConfigVinculoSituacao.limiar_necessidade"]
    assert sorted(asdict(CONFIG_VINCULO)) == ["alfa", "inicial", "janela_coerencia_ticks", "janela_desejo_ticks", "janela_latencia_ticks",
                                              "peso_atendimento", "peso_coerencia", "peso_desejo"]
    assert hash_protocolo(PROTOCOLO_ARENA_V1_PERSONALIDADE).startswith("d986ff1b9308")
    assert ConfigVinculoSituacao().limiar_necessidade == 0.5 and ConfigVinculoSituacao().limiar_energia == 0.25


def test_gabarito_de_paridade_com_a_web_e_reproduzivel_e_esta_em_disco():
    g = gerar()
    assert g["hoje"]["final"]["pedidos_pendentes"] != [] or g["hoje"]["final"]["n_amostras_por_componente"].get("atendimento")
    assert "atendimento" not in g["b"]["final"]["n_amostras_por_componente"] and g["b"]["final"]["pedidos_pendentes"] == []
    assert any("|" in k for k in g["b"]["final"]["chaves_feedback"])
    assert g["hoje"]["valores"] != g["b"]["valores"]
    em_disco = json.loads(GABARITO_WEB.read_text(encoding="utf-8"))
    assert em_disco == g, "gabarito desatualizado: python experiments/exportar_gabarito_vinculo.py"
