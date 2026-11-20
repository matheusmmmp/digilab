"""O descritivo D-COMIDA da DC4 (CONVERSA_PET; docs/PLANO_ANALISE_V3_CONVERSA_DC4.md, secao 6; sem gate, sem semente nova): as vidas do
LAB+F da run da DC3 (`artifacts_v3_conversa_dc3/run/`), refeitas, e o que o credito da fala de comida veria se fosse ate o pet comer.

**A primeira conferencia (falha alto, para tudo):** cada vida do LAB+F e refeita pelo `_vida` da DC3, o mesmo codigo da run (vivida,
gravada, rejogada do disco pelo G1 e conferida pelas falhas altas da secao 11 do plano da DC3). O log refeito tem de ser byte a byte o do
`vidas.tar.gz`, e o registro de medidas, igual ao do `medidas.json` daquela run (tirado so o `custo`, que e o relogio da maquina). Se uma
vida nao reproduzir, o D-COMIDA para e e relatado.

**A leitura, que nao muda nada:** durante a vida, um embrulho so le o corpo (`obs.corpo`) que o cerebro recebe em cada decisao e o corpo
de depois da acao de cada decisao (o do `consequencia_corpo`), e guarda o `DonoQueAtende` da vida. Nao toca em rng nem no aprendizado: o
log e as medidas saem iguais (a conferencia acima). A conta do r_n e a do `afeto.sigma_luta`, o mesmo r e r_n da `consequencia` sem mexer em
V nem em E; antes de usa-la, confere-se que ela devolve o r_n gravado de **toda** decisao fechada da vida (a fala ate o corpo da decisao
seguinte, A1.1 do adendo 1 da DC3; as outras ate o corpo de depois da acao).

**O que se mede**, por pedido atendido (o atendimento do `DonoQueAtende`; o da ultima decisao da vida fica fora, porque nao fecha):
- `decisoes_ate_cair` e `ticks_ate_cair`: da decisao do pedido ate a primeira decisao seguinte em que a urgencia do receptor do pedido
  (`fome` na comida, `solidao` na companhia) e menor que na decisao do pedido; None se nao cai ate o fim da vida (censurado);
- so na comida:
  - `come_na_janela`: o pet come dentro do intervalo que a fala credita hoje (do tick da decisao ate a decisao seguinte); a acao da propria
    decisao e a fala, entao isto so acontece se a comida chegar ao corpo sem a acao do pet;
  - `decisoes_ate_comer`: da decisao do pedido ate a primeira decisao seguinte cuja consequencia tem `comeu` (o pet comeu na acao dela);
  - `r_n_hoje`: o r_n gravado da fala (ate a decisao seguinte);
  - `r_n_ate_comer`: o r_n do mesmo corpo de antes ate o corpo de depois da acao em que o pet come; None se ele nao come ate o fim da vida.

Grava em `artifacts_v3_conversa_dc4/d_comida/`: `pedidos.jsonl` (um por pedido atendido), `resumo.json` (a conferencia e as contagens) e
`meta.json`. Uma vez; recusa gravar por cima. No maximo 4 processos (V3-D8).

    python experiments/d_comida_dc4.py --processos 4
"""
from __future__ import annotations

import argparse
import json
import platform
import statistics
import sys
import tarfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import run_v3_conversa_dc3 as d3  # noqa: E402
from bancada.rodar import _dump, _gravar, _sha  # noqa: E402
from digilab.config import CONFIG_PADRAO  # noqa: E402

RUN_DC3 = RAIZ / "artifacts_v3_conversa_dc3" / "run"
CONFIG_DC3 = RAIZ / "experiments" / "configs" / "v3_conversa_dc3" / "conversa_dc3.json"
SAIDA = RAIZ / "artifacts_v3_conversa_dc4" / "d_comida"
PLANO = "docs/PLANO_ANALISE_V3_CONVERSA_DC4.md"
MAX_PROCESSOS = 4                                   # V3-D8
RECEPTOR = {"fome": "fome", "solidao": "solidao"}    # o pedido -> o receptor cuja urgencia se olha (secao 6: comida e companhia)
FORA_DO_CAMPO = ("custo",)                           # o relogio da maquina, o unico campo do registro que nao se reproduz


# ------------------------------------------------------------------ a leitura (so le)
_CAPTURA: dict = {}


class _DonoQueAtendeGuardado(d3.DonoQueAtende):
    """o mesmo dono que atende da DC3; so guarda a si mesmo para a leitura"""

    def __init__(self, base, motivos) -> None:
        super().__init__(base, motivos)
        if "atende" in _CAPTURA:
            raise RuntimeError("dois donos que atendem na mesma vida")
        _CAPTURA["atende"] = self


_fabricas_dc3 = d3.fabricas


def _fabricas_que_leem(braco, dono, semente, dias, orcamento_por_dia, cfg_fala=None):
    """as fabricas da DC3; o primeiro registro (o da vida; o do replay do G1 vem depois) ganha um embrulho que so le o corpo"""
    fp0, fm = _fabricas_dc3(braco, dono, semente, dias, orcamento_por_dia, cfg_fala)

    def fp(cfg=None):
        registro = fp0(cfg)
        if "registro" not in _CAPTURA:
            _CAPTURA.update(registro=registro, pc_decisao=[], pc_acao=[])
            agir, consequencia = registro.agir, registro.consequencia_corpo

            def agir_e_ler(obs, rng):
                _CAPTURA["pc_decisao"].append(obs.corpo)
                return agir(obs, rng)

            def consequencia_e_ler(acao, ocorrido, obs_depois):
                _CAPTURA["pc_acao"].append(obs_depois.corpo)
                return consequencia(acao, ocorrido, obs_depois)

            registro.agir, registro.consequencia_corpo = agir_e_ler, consequencia_e_ler
        return registro

    return fp, fm


def ligar_leitura() -> None:
    """troca, no modulo da DC3, as fabricas e o dono que atende pelos que leem; so no processo que refaz as vidas (a `tarefa` chama, em
    cada processo filho), nunca no import, para nao mexer em quem so importa este modulo"""
    d3.fabricas = _fabricas_que_leem
    d3.DonoQueAtende = _DonoQueAtendeGuardado


# ------------------------------------------------------------------ as conferencias
def _sem_custo(rec: dict) -> dict:
    return {k: v for k, v in json.loads(_dump(rec)).items() if k not in FORA_DO_CAMPO}


def conferir_r_n(c, pc_decisao: list, pc_acao: list) -> None:
    """a conta do `sigma_luta` sobre os corpos lidos devolve o r_n gravado de toda decisao fechada (falha alto)"""
    ms, recs = c.motivos, c.m.sens.receptores
    if len(pc_decisao) != len(ms) or len(pc_acao) != len(ms):
        raise RuntimeError(f"a leitura tem {len(pc_decisao)} corpos de decisao e {len(pc_acao)} de acao para {len(ms)} decisoes")
    for m in ms:
        k, cons = m["k"], m["consequencia"]
        if cons is None:
            continue
        fim = pc_decisao[k + 1] if m["acao"] == d3.FALA else pc_acao[k]
        r_n = c.m.afeto.sigma_luta(pc_decisao[k], fim, recs)["r_n"]
        if r_n != cons["r_n"]:
            raise RuntimeError(f"a conta do r_n na decisao {k} da {r_n}, o gravado e {cons['r_n']}")


# ------------------------------------------------------------------ as medidas de uma vida
def pedidos_da_vida(c, atende, pc_decisao: list, pc_acao: list) -> list[dict]:
    """um registro por pedido atendido de comida ou companhia (secao 6); o da ultima decisao fica fora"""
    ms, recs = c.motivos, c.m.sens.receptores
    passo_t = CONFIG_PADRAO.intervalo_decisao_ticks
    n = len(ms)
    comeu_em = [m["consequencia"] is not None and m["consequencia"]["comeu"] is not None for m in ms]
    out = []
    for a in atende.atendimentos:
        k, conteudo = a["k"], a["conteudo"]
        if conteudo not in RECEPTOR or k + 1 >= n:
            continue
        rec = RECEPTOR[conteudo]
        u0 = ms[k]["afeto"]["urgencias"][rec]
        cai = next((j for j in range(k + 1, n) if ms[j]["afeto"]["urgencias"][rec] < u0), None)
        p = {"k": k, "dia": k * passo_t // d3.TICKS_POR_DIA + 1, "conteudo": conteudo, "urgencia": u0,
             "decisoes_ate_cair": None if cai is None else cai - k, "ticks_ate_cair": None if cai is None else (cai - k) * passo_t}
        if conteudo == "fome":
            come = next((j for j in range(k + 1, n) if comeu_em[j]), None)
            p.update({"come_na_janela": comeu_em[k],
                      "decisoes_ate_comer": None if come is None else come - k,
                      "r_n_hoje": ms[k]["consequencia"]["r_n"],
                      "r_n_ate_comer": None if come is None else c.m.afeto.sigma_luta(pc_decisao[k], pc_acao[come], recs)["r_n"]})
        out.append(p)
    return out


def tarefa(cfg: dict, unidade: dict, esperado: dict, logs: str, pasta: str) -> list[dict]:
    """as 8 vidas do LAB+F de uma unidade: refeitas, conferidas contra a run da DC3 e medidas"""
    ligar_leitura()
    out = []
    for dono, modo in d3.CELULAS:
        _CAPTURA.clear()
        rec = d3._vida(cfg, d3.TRATADO, modo, dono, unidade, pasta)
        nome = f"{dono}_{modo}_{unidade['semente']}.jsonl"
        feito = Path(pasta) / "vidas" / d3.TRATADO / nome
        if feito.read_bytes() != (Path(logs) / nome).read_bytes():
            raise RuntimeError(f"{rec['vida']}: o log refeito nao e o do vidas.tar.gz")
        feito.unlink()
        if _sem_custo(rec) != _sem_custo(esperado[rec["vida"]]):
            raise RuntimeError(f"{rec['vida']}: as medidas refeitas nao sao as do medidas.json da DC3")
        c = d3.orq.cerebro_de(_CAPTURA["registro"])
        conferir_r_n(c, _CAPTURA["pc_decisao"], _CAPTURA["pc_acao"])
        atende = _CAPTURA.get("atende")
        if (atende is None) != (modo == d3.IGNORA):
            raise RuntimeError(f"{rec['vida']}: o dono que atende {'faltou' if atende is None else 'sobrou'}")
        pedidos = [] if atende is None else pedidos_da_vida(c, atende, _CAPTURA["pc_decisao"], _CAPTURA["pc_acao"])
        out.append({"vida": rec["vida"], "dono": dono, "modo": modo, "semente": unidade["semente"], "pedidos": pedidos})
    return out


# ------------------------------------------------------------------ o resumo
def _dist(vs: list) -> dict:
    ok = sorted(v for v in vs if v is not None)
    q = statistics.quantiles(ok, n=10) if len(ok) >= 2 else None
    return {"n": len(vs), "censurados": len(vs) - len(ok), "media": statistics.fmean(ok) if ok else None,
            "mediana": statistics.median(ok) if ok else None, "p90": None if q is None else q[8]}


def _sinal(v: int) -> int:
    return (v > 0) - (v < 0)


def _sinais(vs: list) -> dict:
    ok = [v for v in vs if v is not None]
    return {"n": len(ok), "nenhum": len(vs) - len(ok), "media": statistics.fmean(ok) if ok else None,
            "positivo": sum(v > 0 for v in ok), "zero": sum(v == 0 for v in ok), "negativo": sum(v < 0 for v in ok)}


def resumir(pedidos: list[dict]) -> dict:
    out = {}
    for conteudo in RECEPTOR:
        ps = [p for p in pedidos if p["conteudo"] == conteudo]
        r = {"pedidos": len(ps), "ticks_ate_cair": _dist([p["ticks_ate_cair"] for p in ps])}
        if conteudo == "fome":
            ambos = [p for p in ps if p["r_n_ate_comer"] is not None]
            r.update({"come_na_janela": sum(p["come_na_janela"] for p in ps),
                      "come_na_decisao_seguinte": sum(p["decisoes_ate_comer"] == 1 for p in ps),
                      "decisoes_ate_comer": _dist([p["decisoes_ate_comer"] for p in ps]),
                      "r_n_hoje": _sinais([p["r_n_hoje"] for p in ps]),
                      "r_n_ate_comer": _sinais([p["r_n_ate_comer"] for p in ps]),
                      "pareado": {"n": len(ambos),
                                  "sinal_muda": sum(_sinal(p["r_n_hoje"]) != _sinal(p["r_n_ate_comer"]) for p in ambos),
                                  "de_nao_positivo_a_positivo": sum(p["r_n_hoje"] <= 0 < p["r_n_ate_comer"] for p in ambos),
                                  "media_hoje": statistics.fmean(p["r_n_hoje"] for p in ambos) if ambos else None,
                                  "media_ate_comer": statistics.fmean(p["r_n_ate_comer"] for p in ambos) if ambos else None}})
        out[conteudo] = r
    return out


def rodar(processos: int, pasta_trabalho: Path) -> dict:
    if processos > MAX_PROCESSOS:
        raise ValueError(f"no maximo {MAX_PROCESSOS} processos (V3-D8)")
    if SAIDA.exists():
        raise FileExistsError(f"{SAIDA} ja existe: o D-COMIDA roda uma vez")
    inicio = time.time()
    cfg = json.loads(CONFIG_DC3.read_text(encoding="utf-8"))
    meta_dc3 = json.loads((RUN_DC3 / "meta.json").read_text(encoding="utf-8"))
    for nome, sha in meta_dc3["artefatos_sha256"].items():
        if _sha(RUN_DC3 / nome) != sha:
            raise RuntimeError(f"o {nome} da DC3 nao e o que a run gravou")
    medidas = json.loads((RUN_DC3 / "medidas.json").read_text(encoding="utf-8"))
    logs = pasta_trabalho / "logs_dc3"
    with tarfile.open(RUN_DC3 / "vidas.tar.gz") as t:
        membros = [m for m in t.getmembers() if m.isfile() and m.name.startswith(f"vidas/{d3.TRATADO}/")]
        logs.mkdir(parents=True, exist_ok=False)
        for m in membros:
            (logs / Path(m.name).name).write_bytes(t.extractfile(m).read())
    unidades = meta_dc3["unidades"]
    esperadas = len(unidades) * len(d3.CELULAS)
    if len(membros) != esperadas:
        raise RuntimeError(f"o vidas.tar.gz tem {len(membros)} vidas do {d3.TRATADO}, eram {esperadas}")
    tarefas = []
    for u in unidades:
        esp = {v: medidas[v] for v in (f"{d3.TRATADO}|{mo}|{do}|{u['semente']}" for do, mo in d3.CELULAS)}
        tarefas.append((tarefa, (cfg, u, esp, str(logs), str(pasta_trabalho / "refeitas"))))
    vidas = [v for s in d3.orq.rc._executar(tarefas, processos) for v in s]
    if len(vidas) != esperadas:
        raise RuntimeError(f"{len(vidas)} vidas refeitas, eram {esperadas}")
    pedidos = [{"vida": v["vida"], "dono": v["dono"], **p} for v in vidas for p in v["pedidos"]]
    resumo = {"plano": PLANO, "secao": 6, "descritivo": "D-COMIDA, sem gate; um descritivo a mais sobre a run da DC3, ja lida",
              "conferencia": {"vidas_refeitas": len(vidas), "logs_iguais_ao_tar": len(vidas), "medidas_iguais": len(vidas),
                              "r_n_gravado_reproduzido_em_toda_decisao_fechada": True,
                              "campos_fora_da_comparacao": list(FORA_DO_CAMPO)},
              "vidas_com_dono_que_atende": sum(v["modo"] == d3.ATENDE for v in vidas),
              "todos": resumir(pedidos),
              "por_dono": {d: resumir([p for p in pedidos if p["dono"] == d]) for d in d3.DONOS}}
    SAIDA.mkdir(parents=True)
    with (SAIDA / "pedidos.jsonl").open("w", encoding="utf-8", newline="\n") as f:
        for p in pedidos:
            f.write(json.dumps(p, ensure_ascii=False, sort_keys=True) + "\n")
    _gravar(SAIDA / "resumo.json", _dump(resumo))
    meta = {"plano": PLANO, "plano_sha256": _sha(RAIZ / PLANO), "run_dc3": "artifacts_v3_conversa_dc3/run",
            "run_dc3_sha256": {n: _sha(RUN_DC3 / n) for n in ("medidas.json", "meta.json", "vidas.tar.gz")},
            "codigo_dc3_hoje_vs_run": {k: {"run": meta_dc3["sha256"].get(k), "hoje": v} for k, v in d3.sha_dos_arquivos().items()
                                        if meta_dc3["sha256"].get(k) != v},
            "script_sha256": _sha(Path(__file__)), "processos": processos, "python": platform.python_version(),
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(inicio)),
            "fim": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()), "duracao_s": time.time() - inicio,
            "artefatos_sha256": {n: _sha(SAIDA / n) for n in ("pedidos.jsonl", "resumo.json")}}
    _gravar(SAIDA / "meta.json", _dump(meta))
    return resumo


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="o D-COMIDA da DC4 (secao 6): o replay das vidas do LAB+F da DC3")
    ap.add_argument("--processos", type=int, default=1)
    ap.add_argument("--trabalho", required=True, help="a pasta temporaria dos logs (fora do repositorio)")
    a = ap.parse_args(argv)
    print(json.dumps(rodar(a.processos, Path(a.trabalho))["todos"], indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
