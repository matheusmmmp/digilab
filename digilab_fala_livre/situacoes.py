"""Situacoes reais para a avaliacao offline (TAREFA_FALA_LIVRE, secao 4).

Fonte: as 50 vidas de artifacts_treino/vidas (5 bracos x 10 ovos; personalidade completa + treino). Cada vida
e rejogada UMA vez do disco; em cada estagio (bebe, crianca, adolescente, adulto) sorteia-se um tick-alvo e a
primeira decisao do pet a partir dele vira uma situacao: 50 x 4 = 200. Para cada situacao guarda-se:
  - o estado do pet no formato de `fatos.fatos_de_estado` (para o modo livre);
  - o motivo da decisao, o estagio e o humor (para o modo moldura, `servidor/fala_llm.py`).
So LEITURA: o replay usa as mesmas fabricas do run_treino; nada e gravado no pet.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from digilab.events import LogDeEventos
from digilab.expressao import FATORES
from digilab.motivo import PoliticaComMotivo, indices_eventos_dono
from digilab.treino import reproduzir_com_feedback
from digilab.treino_vida import fabricas_treino
from digilab.temperamento import EIXOS, sortear
from digilab.evolucao import ovo

ESTAGIOS = ("bebe", "crianca", "adolescente", "adulto")
TICKS_POR_DIA = 24 * 60


def _hhmm(t: int) -> str:
    return f"dia {t // TICKS_POR_DIA + 1} {(t % TICKS_POR_DIA) // 60:02d}:{t % 60:02d}"


def _fator_txt(f: str) -> str:
    base = f.split("(", 1)[0]
    return FATORES.get(base, {}).get("marcador", base.replace("_", " "))


class _Captura(PoliticaComMotivo):
    """PoliticaComMotivo que tira uma foto do pet na primeira decisao a partir de cada tick-alvo."""

    def __init__(self, interna, indices, alvos: dict, ao_capturar):
        super().__init__(interna, indices)
        self.alvos = dict(alvos)          # estagio -> tick-alvo (sai quando capturado)
        self.ao_capturar = ao_capturar

    def agir(self, obs, rng):
        acao = super().agir(obs, rng)
        m = self.motivos[-1]
        for est, alvo in list(self.alvos.items()):
            if m.tick is not None and m.tick >= alvo:
                del self.alvos[est]
                self.ao_capturar(est, obs, m, list(self.motivos[-3:]))
        return acao


def situacoes_da_vida(caminho: Path, rng: random.Random) -> list[dict]:
    braco, s = caminho.stem.split("@")
    s = int(s)
    resumo = json.loads(caminho.with_name(f"{braco}@{s}.treino.json").read_text(encoding="utf-8"))
    log = LogDeEventos.de_jsonl(caminho.read_text(encoding="utf-8"))
    tr = resumo["treino"]["transicoes"]
    fim = max(e.tick for e in log)
    inicio = {"bebe": 0, "crianca": tr["crianca"]["tick"], "adolescente": tr["adolescente"]["tick"],
              "adulto": tr["adulto"]["tick"]}
    limites = {"bebe": inicio["crianca"], "crianca": inicio["adolescente"], "adolescente": inicio["adulto"], "adulto": fim}
    alvos = {e: rng.randrange(inicio[e], max(inicio[e] + 1, limites[e] - 30)) for e in ESTAGIOS}
    esp, _ = ovo(s)
    temp = sortear(s)
    fp, fm = fabricas_treino(s, esp, temp)
    guarda: dict = {}
    fotos: list[dict] = []

    def fab(c):
        p = _Captura(fp(c), indices_eventos_dono(log), alvos, foto)
        guarda["pol"] = p
        return p

    def fab_motor(politica, cfg, semente):
        m = fm(politica, cfg, semente)
        guarda["motor"] = m
        return m

    def foto(est, obs, motivo, recentes):
        motor, pol = guarda["motor"], guarda["pol"]
        e = motor._estado
        mem = pol.interna.memoria
        estado = {"fome": 1.0 - e.fome, "higiene": e.higiene, "energia": e.energia, "humor": e.humor, "saude": e.saude}
        if mem.eventos:
            from digilab.emocao import emocao_de
            t_ev, cat, _i, ref = mem.eventos[-1]
            estado["emocao"] = emocao_de(cat, temp, t_ev, ref).nome
        estado["fadiga"] = round(motor.treino.fadiga)
        estado["sobrecarga"] = round(motor.treino.sobrecarga)
        if e.sujeira > 0:
            estado["sujo"] = True
        forma = resumo["forma"]
        ident = {"estagio": est, "especie": esp}
        if est in ("adolescente", "adulto"):
            ident["linha"] = forma["linha"]
        if est == "adulto":
            ident["forma"] = forma["adulta"]
        memorias = [{"espaco": esp_, "categoria": x.categoria, "evento": {
            "demora": "o dono me deixou esperando", "bronca": "o dono me deu bronca", "elogio": "o dono me elogiou",
            "carinho": "o dono me fez carinho"}.get(x.categoria, x.categoria), "ha_min": max(0, e.tick - x.criada)}
                    for esp_, lst in (("curto", mem.curto), ("longo", mem.longo)) for x in lst][:8]
        d = motor.desejos[-1] if motor.desejos and motor.desejos[-1].intensidade > 0 else None
        motivos = []
        for mo in reversed(recentes):
            ref = next((log[i].tick for i in mo.evento_ref if 0 <= i < len(log)), None) if mo.evento_ref else None
            motivos.append({"acao": mo.acao.replace("_", " "), "fatores": [] if mo.exploracao else [_fator_txt(f) for f in mo.fatores],
                            **({"evento_ref": _hhmm(ref)} if ref is not None else {})})
        estado_pet = {"identidade": ident, "temperamento": {k: getattr(temp, k) for k in EIXOS}, "estado": estado,
                      "memorias": memorias, "motivos": motivos, "vinculo": max(0.0, min(1.0, motor.vinculo.valor)),
                      "gatilho": f"acabei de decidir: {motivo.acao.replace('_', ' ')}"}
        if est == "adulto" and resumo.get("carater_adulto"):
            estado_pet["carater"] = {k: max(-1.0, min(1.0, v)) for k, v in resumo["carater_adulto"].items()}
        if d is not None:
            estado_pet["desejo"] = {"tipo": d.tipo, "alvo": d.alvo.replace("_", " ")}
        fotos.append({"id": f"{braco}@{s}:{est}", "braco": braco, "ovo": s, "estagio": est, "tick": motivo.tick,
                      "estado_pet": estado_pet, "motivo": motivo.para_dict() if hasattr(motivo, "para_dict") else None,
                      "_motivo": motivo, "humor": obs.vetor_estado[3]})

    reproduzir_com_feedback(log, fab, semente=s, fabrica_motor=fab_motor)
    if {f["estagio"] for f in fotos} != set(ESTAGIOS):
        raise RuntimeError(f"{caminho.name}: faltou estagio {set(ESTAGIOS) - {f['estagio'] for f in fotos}}")
    return fotos


def coletar(pasta: Path, semente: int) -> list[dict]:
    rng = random.Random(semente)
    out = []
    for arq in sorted(pasta.glob("*@*.jsonl")):
        if arq.name.endswith(".treino.json"):
            continue
        out += situacoes_da_vida(arq, rng)
    return out
