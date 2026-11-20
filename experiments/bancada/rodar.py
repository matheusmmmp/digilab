"""A bancada da V2, módulo `rodar`.

Gravar, o sha256, o meta, rodar e a linha de comando (main).

Parte do pacote `experiments/bancada/` (rodada de saúde, etapa 3; docs/TAREFA_V2_SAUDE.md). O texto de cada definição é o de antes,
movido de `experiments/bancada_v2.py` sem mudança (tools/dividir_bancada.py; a prova pela AST em docs/historico/bancada_mapa.json).
O `experiments/bancada_v2.py` continua sendo a porta de entrada: ele reexporta todo nome daqui.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from itertools import product
from pathlib import Path

from digilab.protocol import ENGINE_SHA256_V0, sha256_engine

from . import RAIZ, sha256_do_pacote


# ------------------------------------------------------------------ orquestrador


def _gravar(caminho: Path, texto: str) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8", newline="\n")


def _dump(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _sha(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def rodar(cfg: dict, pasta: Path) -> dict:
    """Vidas de todos os bracos x donos x sementes (x genomas x mundos), gravadas e rejogadas do disco; os acoplados; as
    medidas por vida e as tabelas braco x condicao por dono e medida."""
    validar_config(cfg)
    bancada = bancada_da_config(cfg)
    dir_vidas = pasta / "vidas"
    vidas: dict[str, VidaBancada] = {}

    def guardar(v: VidaBancada) -> None:
        _gravar(dir_vidas / f"{v.nome}.jsonl", v.motor.log.para_jsonl())
        _gravar(dir_vidas / f"{v.nome}.politica.json", _interno(v.motor))
        bancada.conferir_replay(v, (dir_vidas / f"{v.nome}.jsonl").read_text(encoding="utf-8"))
        vidas[v.nome] = v

    if "unidades" in cfg:
        unidades = unidades_derivadas(cfg["unidades"]["bases"], int(cfg["unidades"]["k"]),
                                      cfg["unidades"].get("prefixo", "experimento-maior"))
        pares = [(u["genoma"], u["semente"]) for u in unidades]
    else:
        unidades = []
        pares = [(g, int(s)) for g in cfg.get("genomas", [None]) for s in cfg["sementes"]]
    da_unidade = {(u["genoma"], u["semente"]): {"base": u["base"], "k": u["k"]} for u in unidades}
    teto = None
    if validar_teto_pesos(cfg) is not None:      # o teto do plano: os pesos declarados sao os do maior cerebro dos bracos
        g0, s0 = pares[0]
        teto = conferir_teto_pesos(cfg, {
            f"{braco}/{mundo}": do_braco(bancada.politica(EspecVida(
                cfg["donos"][0], braco, s0, g0, mundo, lugar=cfg["lugares"][0] if mundo_de(mundo).fisico is not None else None))).cerebro
            for mundo in cfg.get("mundos", ["padrao"]) for braco in cfg["bracos"]})
    for (g, s), mundo, dono, braco in product(pares, cfg.get("mundos", ["padrao"]), cfg["donos"], cfg["bracos"]):
        for lugar in (cfg["lugares"] if mundo_de(mundo).fisico is not None else [None]):   # mundo fisico: a celula e dono x lugar
            guardar(bancada.vida(EspecVida(dono, braco, s, g, mundo, lugar=lugar)))
    origens = list(vidas.values())
    for a in cfg.get("acoplados", []):
        for v in origens:
            if v.espec.braco == a["origem"]:
                guardar(bancada.acoplar(v, a["destino"], a["filtro"]))
    # o piso do tempo ate aprender e o acerto do P0 na mesma celula (o prior herdado); sem P0 na config, o da propria vida
    medidas, piso, taxa_p0 = {}, {}, {}
    for nome, v in sorted(vidas.items()):
        if v.espec.braco == "P0" and v.origem is None:
            medidas[nome] = bancada.medir(v, cfg["sonda"])
            piso[v.espec.celula] = medidas[nome]["acerto_total"]
            if medidas[nome]["frutas"] is not None:
                taxa_p0[v.espec.celula] = medidas[nome]["frutas"]["taxa_fruta_ruim"]["total"]["taxa"]
    for nome, v in sorted(vidas.items()):
        if nome not in medidas:
            medidas[nome] = bancada.medir(v, cfg["sonda"], piso.get(v.espec.celula), taxa_p0.get(v.espec.celula))
    for nome, v in vidas.items():
        medidas[nome]["unidade"] = da_unidade.get((v.espec.genoma, v.espec.semente))
    tabelas = tabelas_braco_condicao(medidas, cfg["bootstrap"])
    _gravar(pasta / "medidas.json", _dump(medidas))
    _gravar(pasta / "tabelas.json", _dump(tabelas))
    _gravar(pasta / "dominancia.json", _dump(tabela_dominancia(medidas)))
    if any(m.get("banheiro") is not None for m in medidas.values()):
        _gravar(pasta / "banheiro.json", _dump(tabela_banheiro(medidas)))
    _gravar(pasta / "meta.json", _dump(meta(cfg) if teto is None else {**meta(cfg), "teto_pesos": teto}))
    return {"vidas": vidas, "medidas": medidas, "tabelas": tabelas}


def meta(cfg: dict) -> dict:
    if sha256_engine() != ENGINE_SHA256_V0:
        raise RuntimeError("engine.py mudou")
    rede = {} if "rede_de_si" not in cfg else {"cfg_rede": cfg_rede_da_config(cfg).__dict__,
                                                "rede_de_si_sha256": _sha(RAIZ / "digilab" / "rede_de_si.py")}
    return {"config": cfg, "ponto": cfg.get("ponto", PONTO_PADRAO), **rede,
            "cfg_lobos": cfg_lobos_do_ponto(cfg.get("ponto", PONTO_PADRAO), cfg.get("lobos")).__dict__,
            "python": platform.python_version(), "plataforma": platform.platform(),
            "engine_sha256": sha256_engine(), "lobos_sha256": _sha(RAIZ / "digilab" / "policies" / "lobos.py"),
            "config_sha256": _sha(RAIZ / "digilab" / "config.py"), "bancada_sha256": sha256_do_pacote(),
            "metrics_sha256": _sha(RAIZ / "digilab" / "metrics.py"), "mundo_sha256": _sha(RAIZ / "digilab" / "mundo.py"),
            "corpo_sha256": _sha(RAIZ / "digilab" / "corpo.py"), "motor_corpo_sha256": _sha(RAIZ / "digilab" / "motor_corpo.py")}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="bancada da V2: bracos P0-P3 sobre o mesmo aprendiz (docs/TAREFA_V2_BANCADA.md)")
    ap.add_argument("--config", required=True)
    ap.add_argument("--saida", required=True, help="pasta de saida (vidas/, medidas.json, tabelas.json, meta.json)")
    ap.add_argument("--passo0", action="store_true", help="o passo 0 da calibracao do corpo (A3.2b): os pontos e a escolha")
    ap.add_argument("--processos", type=int, default=1, help="so no --passo0: os pontos em paralelo")
    a = ap.parse_args(argv)
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    if a.passo0:
        r = rodar_passo0(cfg, Path(a.saida), a.processos)
        e = r["escolha"]
        print(f"passo 0: {e['nome']} ({'fechou' if e['fechou'] else 'nao fechou'}, fracao {e['fracao']:.4f}); em {a.saida}/passo0.json")
        return 0
    if cfg.get("tipo") == "pet_que_pensa":        # o pet que pensa (TAREFA_V2_PET_QUE_PENSA, etapa 4)
        r = rodar_pqp(cfg, Path(a.saida))
        print(f"{len(r['vidas'])} vidas do J5 rejogadas do disco bit a bit; medidas em {a.saida}")
        return 0
    if cfg.get("tipo") == "grupo":                # dois pets (TAREFA_V2_DOIS_PETS, etapa 5)
        r = rodar_grupo(cfg, Path(a.saida))
        print(f"{len(r['grupos'])} grupos rejogados do disco bit a bit; medidas em {a.saida}")
        return 0
    r = rodar(cfg, Path(a.saida))
    print(f"{len(r['vidas'])} vidas rejogadas do disco bit a bit; medidas e tabelas em {a.saida}")
    return 0


# os nomes de outros módulos do pacote que só rodam dentro das funções: importados depois das definições, para o pacote
# não ter importação circular (tools/dividir_bancada.py)
from .faixas import unidades_derivadas  # noqa: E402
from .mundos import mundo_de  # noqa: E402
from .bracos import PONTO_PADRAO  # noqa: E402
from .vida import EspecVida, _interno, VidaBancada  # noqa: E402
from .medidas import do_braco, tabela_banheiro, tabela_dominancia, tabelas_braco_condicao  # noqa: E402
from .config import (bancada_da_config, cfg_lobos_do_ponto, cfg_rede_da_config, conferir_teto_pesos, validar_config,  # noqa: E402
                     validar_teto_pesos)
from .grupo import rodar_grupo  # noqa: E402
from .passo0 import rodar_passo0  # noqa: E402
from .pet_que_pensa import rodar_pqp  # noqa: E402
