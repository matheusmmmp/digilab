"""Bateria do combate V2.1 (arvore de evolucao integrada ao combate).

    python experiments/run_bateria_v21.py --config experiments/configs/bateria_v21_canonico.json

Gates (limiares em ConfigBateriaV21, todos PROPOSTOS):
  E1 sem arquetipo dominante: nenhum dos 8 adultos vence todos os outros;
     equilibrio simetrico com suporte >= 4. Matriz agregada sobre as especies
     ativas, os dois lados sempre da MESMA especie.
  E2 sem especie dominante: mesmo arquetipo e estilo dos dois lados, variando
     so a especie; nenhuma especie vence todas as outras (matriz agregada sobre
     os arquetipos). A matriz especie x arquetipo vai em matriz_especie_arquetipo.json.
  E3 tecnica usada e respondivel: cada tecnica em >= 5% das decisoes dos
     arquetipos da linha (partidas do E1); e a resposta declarada (regra no topo
     da lista do oponente) reduz a taxa de vitoria de quem usa a tecnica.
  E4 estagio importa sem esmagar: adulto x adolescente da mesma linha (mesma
     especie, mesmo carater) com taxa em [0.60, 0.85], por forma adulta.
  E5 robustez: cada numero de tecnica/passiva perturbado em +-10% (inteiros:
     arredonda; se nao mudar, +-1) mantem E1 na maioria das perturbacoes.
  G1-G7 da base: lidos de artifacts_combate_v2/gates.json, com a checagem de
     que os fontes da base nao mudaram (hash das regras igual ao gravado).

Codigo de saida: 0 APROVADA, 2 REPROVADA.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import statistics
import sys
from dataclasses import asdict, replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

from digilab.combate_v2.v21 import bots as _bots  # noqa: E402
from digilab.combate_v2.v21.bots import ADOLESCENTES, ADULTOS, FORMAS, RESPOSTAS, RESPOSTAS_V21C, com_resposta  # noqa: E402
from digilab.combate_v2.v21.catalogo import LINHA_DA_FORMA, LINHAS, carater_canonico  # noqa: E402
from digilab.combate_v2.v21.gambits import PESADO_AUTOMATICO  # noqa: E402
from digilab.combate_v2.v21.partida import Lutador, jogar, reproduzir  # noqa: E402
from digilab.combate_v2.v21.regras import ACOES_ESCOLHIVEIS, TECNICAS, Regras  # noqa: E402
from digilab.config import (CAMPOS_TECNICA_PASSIVA_V21, CONFIG_BATERIA_V21, CONFIG_CATALOGO,  # noqa: E402
                            CONFIG_COMBATE_V2, CONFIG_COMBATE_V21)
from digilab.metrics import equilibrio_simetrico, matriz_taxas, suporte  # noqa: E402
from digilab.protocol import ENGINE_SHA256_V0, derivar_semente, sha256_engine  # noqa: E402
from run_arena import _imports_externos  # noqa: E402
from run_bateria_combate import hashes as hashes_base  # noqa: E402

CHAVES = {"descricao", "saida", "sementes_calibracao", "sementes_validacao", "conjunto", "regras_base", "regras_v21",
          "respostas_v21c", "gates_v2c", "escala",
          "partidas_por_par_por_semente", "registro_calibracao", "pular_e5"}
TECNICA_DA_LINHA = {l: CONFIG_CATALOGO.arquetipos_adolescente[l]["tecnica"] for l in LINHAS}

# escala de stats (TAREFA_PLANILHA_PROGRESSAO, Parte C): "escala": true no config liga a ConfigEscala em todos os
# lutadores. Entre adultos sem treino a razao E_A/E_B e 1 exata (a luta e a de sempre); muda o E4 (entre estagios).
ESCALA = None


def lutador_adulto(*a, **k):
    return _bots.lutador_adulto(*a, **k, escala=ESCALA)


def lutador_adolescente(*a, **k):
    return _bots.lutador_adolescente(*a, **k, escala=ESCALA)


def _dump(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True)


def _gravar(caminho: Path, texto: str) -> None:
    caminho.write_text(texto, encoding="utf-8", newline="\n")


def carregar(caminho: Path) -> dict:
    cfg = json.loads(caminho.read_text(encoding="utf-8"))
    extras = set(cfg) - CHAVES
    if extras:
        raise KeyError(f"chaves desconhecidas no config da bateria V2.1: {sorted(extras)}")
    for k in ("saida", "sementes_calibracao", "sementes_validacao", "conjunto", "partidas_por_par_por_semente"):
        if k not in cfg:
            raise KeyError(f"config da bateria V2.1 sem {k!r}")
    if set(cfg["sementes_calibracao"]) & set(cfg["sementes_validacao"]):
        raise ValueError("sementes de calibracao e validacao se sobrepoem")
    if cfg["conjunto"] not in ("calibracao", "validacao"):
        raise ValueError(f"conjunto invalido: {cfg['conjunto']!r}")
    if cfg["partidas_por_par_por_semente"] % 2:
        raise ValueError("partidas por par precisa ser par (lados trocados na metade)")
    return cfg


def regras_de(cfg_json: dict) -> Regras:
    """V2.1 original, ou V21C: "regras_base" = campos de ConfigCombateV2C (C1-C4) e "regras_v21" = campos de
    ConfigCombateV21C (marca_fragil, hp_base, hp_por_vigor...). TAREFA_CORRECAO_COMBATE, Etapa 3."""
    from digilab.config import ConfigCombateV2C, ConfigCombateV21C, ConfigCombateV21D, ConfigCombateV21E
    base, v21 = CONFIG_COMBATE_V2, CONFIG_COMBATE_V21
    if "regras_base" in cfg_json:
        extras = set(cfg_json["regras_base"]) - set(ConfigCombateV2C.__dataclass_fields__)
        if extras:
            raise KeyError(f"regras_base desconhecidas: {sorted(extras)}")
        base = ConfigCombateV2C(**{**asdict(CONFIG_COMBATE_V2), **cfg_json["regras_base"]})
    if "regras_v21" in cfg_json:
        extras = set(cfg_json["regras_v21"]) - set(ConfigCombateV21E.__dataclass_fields__)
        if extras:
            raise KeyError(f"regras_v21 desconhecidas: {sorted(extras)}")
        # V21D (reequilibrio, docs/EQUILIBRIO_RODADA1.md) so quando o config pede uma chave dela, e V21E (equilibrio
        # geral, docs/EQUILIBRIO_GERAL.md) so quando pede uma chave dela: as configs V21C e V21D continuam montando a
        # classe de antes, com o mesmo asdict e o mesmo config_sha256
        chaves = set(cfg_json["regras_v21"])
        classe = ConfigCombateV21E if chaves - set(ConfigCombateV21D.__dataclass_fields__) \
            else ConfigCombateV21D if chaves - set(ConfigCombateV21C.__dataclass_fields__) else ConfigCombateV21C
        v21 = classe(**{**asdict(CONFIG_COMBATE_V21), **cfg_json["regras_v21"]})
    return Regras(base=base, v21=v21)


def hashes(cfg_json: dict) -> dict:
    fontes = sorted((RAIZ / "digilab" / "combate_v2" / "v21").glob("*.py"))
    h = hashlib.sha256()
    for f in fontes:
        h.update(f.name.encode() + b"\0" + f.read_bytes().replace(b"\r\n", b"\n") + b"\0")
    semantico = {k: v for k, v in cfg_json.items() if k not in ("saida", "descricao")}
    r = regras_de(cfg_json)
    carga = {"base": asdict(r.base), "v21": asdict(r.v21),
             "catalogo": asdict(CONFIG_CATALOGO), "bateria": asdict(CONFIG_BATERIA_V21), "json": semantico}
    if cfg_json.get("escala"):                  # so com a escala: os hashes das runs antigas nao mudam
        from digilab.config import CONFIG_ESCALA_LIGADA
        carga["escala"] = asdict(CONFIG_ESCALA_LIGADA)
    return {"regras_sha256": h.hexdigest(), "arquivos_regras": [f.name for f in fontes],
            "config_sha256": hashlib.sha256(json.dumps(carga, sort_keys=True, default=list).encode()).hexdigest()}


def partidas_par(a: Lutador, b: Lutador, rotulo: str, sementes: list[int], n: int, r: Regras):
    """N partidas por semente, lados trocados na metade; pontos do ponto de vista de `a`."""
    for s in sementes:
        for k in range(n):
            sp = derivar_semente("bateria-v21", rotulo, s, a.nome, b.nome, k)
            if k < n // 2:
                p = jogar(a, b, sp, r)
                yield s, p, p.pontos_a, 0
            else:
                p = jogar(b, a, sp, r)
                yield s, p, 1.0 - p.pontos_a, 1


def contar_decisoes(p, contagem: dict) -> None:
    for ev in p.log:
        if ev["tipo"] != "turno":
            continue
        for nome, acao, motivo in ((p.nome_a, ev["a"], ev["ma"]), (p.nome_b, ev["b"], ev["mb"])):
            if motivo != PESADO_AUTOMATICO:
                contagem.setdefault(nome, {}).setdefault(acao, 0)
                contagem[nome][acao] += 1


def round_robin_arquetipos(especies, sementes, n, r: Regras, cfg21, rotulo="e1", guardar=None):
    """E1: 8 formas, os dois lados da mesma especie. Devolve confrontos (forma, forma, pts)."""
    confrontos = []
    for esp in especies:
        lut = {f: lutador_adulto(f, esp, cfg21) for f in FORMAS}
        for i, fa in enumerate(FORMAS):
            for fb in FORMAS[i:]:
                for s, p, pts, _ in partidas_par(lut[fa], lut[fb], f"{rotulo}|{esp}", sementes, n, r):
                    confrontos.append((fa, fb, pts))
                    if guardar is not None:
                        guardar(esp, fa, fb, s, p, pts)
    return confrontos


def avaliar_e1(taxa: dict, cb) -> tuple[bool, dict]:
    eq = equilibrio_simetrico(taxa, list(FORMAS), cb.iteracoes_fictitious_play)
    sup = suporte(eq["estrategia"], cb.peso_minimo_suporte)
    dominantes = [x for x in FORMAS if all(taxa[x][y] > 0.5 for y in FORMAS if y != x)]
    return (not dominantes and len(sup) >= cb.suporte_minimo_e1), {
        "dominantes": dominantes, "suporte": sup, "estrategia": eq["estrategia"]}


def gates_v21c(gate, r, cfg21, especies, sementes, n, e5, conf_e1, linhas_csv) -> None:
    """Gates da Etapa 2 levados a V2.1 (TAREFA_CORRECAO_COMBATE, Etapa 3) + checagem do guardiao."""
    from digilab.config import CONFIG_BATERIA_V2C, CONFIG_BATERIA_COMBATE
    from digilab.combate_v2.v21.catalogo import Forma, LINHA_DA_FORMA, perfil
    cv = CONFIG_BATERIA_V2C
    # G6b: mesmo arquetipo e especie, condicao 1,05 x 0,95 (a faixa da condicao do cuidado)
    g6b = {}
    for f in FORMAS:
        vals = []
        for esp in especies:
            base = lutador_adulto(f, esp, cfg21)
            fo = Forma(esp, "adulto", "sereno", LINHA_DA_FORMA[f], f)
            fav = Lutador(f"{f}@{esp}#fav", perfil(fo, None, carater_canonico(f), 1.0 + cv.variacao_hp_g6b, cfg21, escala=ESCALA), base.gambits, base.epsilon)
            des = Lutador(f"{f}@{esp}#des", perfil(fo, None, carater_canonico(f), 1.0 - cv.variacao_hp_g6b, cfg21, escala=ESCALA), base.gambits, base.epsilon)
            vals += [x for _, _, x, _ in partidas_par(fav, des, "g6b", sementes, cv.partidas_g6b_por_semente, r)]
        g6b[f] = sum(vals) / len(vals)
    pior = max(g6b, key=g6b.get)
    gate("G6b_espelho_condicao", g6b[pior] <= cv.taxa_max_g6b,
         f"mesmo arquetipo e especie, condicao {1 + cv.variacao_hp_g6b} x {1 - cv.variacao_hp_g6b}: favorecido ate {g6b[pior]:.3f} "
         f"({pior}); media {sum(g6b.values()) / len(g6b):.3f} (<= {cv.taxa_max_g6b})", {"taxa_favorecido": g6b})
    # G8: o E1 continua valendo em >= 80% das perturbacoes (as do E5)
    if e5:
        frac = sum(v["e1_ok"] for v in e5.values()) / len(e5)
        gate("G8_robustez", frac >= cv.fracao_min_g8, f"E1 vale em {frac:.3f} das {len(e5)} perturbacoes do E5 (>= {cv.fracao_min_g8})",
             {"fracao": frac})
    # G9: decisividade com epsilon 0,2 entre arquetipos (agregado nas especies)
    conf = []
    for esp in especies:
        lut = {f: replace(lutador_adulto(f, esp, cfg21), epsilon=max(0.2, CONFIG_COMBATE_V2.epsilon_bots)) for f in FORMAS}
        for i, fa in enumerate(FORMAS):
            for fb in FORMAS[i + 1:]:
                conf += [(fa, fb, x) for _, _, x, _ in partidas_par(lut[fa], lut[fb], f"g9|{esp}", sementes,
                                                                    cv.partidas_g9_por_semente, r)]
    tx = matriz_taxas(conf)
    pares = [(a, b) for i, a in enumerate(FORMAS) for b in FORMAS[i + 1:]]
    frac02 = sum(tx[a][b] < cv.extremo_g9 or tx[a][b] > 1 - cv.extremo_g9 for a, b in pares) / len(pares)
    tx05 = matriz_taxas(conf_e1)
    frac05 = sum(tx05[a][b] < cv.extremo_g9 or tx05[a][b] > 1 - cv.extremo_g9 for a, b in pares) / len(pares)
    # guardiao: bloquear muito e esperado; os confrontos com guardiao nao podem passar do limite do G4
    lim = CONFIG_BATERIA_COMBATE.fracao_max_limite_turnos
    com_g = [l for l in linhas_csv if l[0] == "e1" and any(x.split("@")[0] in ("espelho", "muralha") for x in (l[3], l[4]))]
    frac_g = sum(l[7] == "limite" for l in com_g) / len(com_g)
    gate("guardiao_limite_turnos", frac_g < lim,
         f"confrontos do E1 com espelho ou muralha: {frac_g:.3f} no limite de turnos (< {lim}, o do G4)", {"fracao": frac_g, "partidas": len(com_g)})
    gate("G9_decisividade", frac02 <= cv.fracao_max_g9,
         f"pares de arquetipos com taxa < {cv.extremo_g9} ou > {1 - cv.extremo_g9}: epsilon base {frac05:.3f}; epsilon 0,2 {frac02:.3f} "
         f"(<= {cv.fracao_max_g9})", {"eps_base": frac05, "eps_02": frac02})


def perturbacoes(p: float, v21=CONFIG_COMBATE_V21) -> list[tuple[str, str, object, object]]:
    saida = []
    for campo in CAMPOS_TECNICA_PASSIVA_V21:
        v = getattr(v21, campo)
        for sinal, rot in ((-1, "-"), (1, "+")):
            if isinstance(v, int):
                novo = round(v * (1 + sinal * p))
                if novo == v:
                    novo = v + sinal
                novo = max(1, novo) if campo.startswith(("turnos", "recarga")) else max(0, novo)
            else:
                novo = v * (1 + sinal * p)
            saida.append((campo, rot, v, novo))
    return saida


def executar(caminho_cfg: Path) -> int:
    cfg = carregar(caminho_cfg)
    cb = CONFIG_BATERIA_V21
    saida = Path(cfg["saida"])
    if not saida.is_absolute():
        saida = RAIZ / saida
    saida.mkdir(parents=True, exist_ok=True)
    externos = sorted(_imports_externos(RAIZ / "digilab"))
    if externos:
        raise RuntimeError(f"digilab usa imports fora da stdlib: {externos}")
    if sha256_engine() != ENGINE_SHA256_V0:
        raise RuntimeError("engine.py alterado")

    sementes = list(cfg["sementes_" + cfg["conjunto"]])
    n = cfg["partidas_por_par_por_semente"]
    especies = list(CONFIG_CATALOGO.especies_ativas)
    r = regras_de(cfg)
    cfg21 = r.v21
    gates = []
    global ESCALA
    if cfg.get("escala"):
        from digilab.config import CONFIG_ESCALA_LIGADA
        ESCALA = CONFIG_ESCALA_LIGADA
        print("escala LIGADA (ConfigEscala)", flush=True)

    def gate(nome, ok, msg, valores):
        gates.append({"gate": nome, "ok": bool(ok), "mensagem": msg, "valores": valores})
        print(f"  [{'ok' if ok else 'REPROVA'}] {nome}: {msg}", flush=True)

    # ------------------------------------------------------------ E1
    linhas_csv, amostra, decisoes, turnos, fins = [], [], {}, [], {"ko": 0, "limite": 0}
    espelho = {f: [] for f in FORMAS}
    passo = max(1, (len(especies) * 36 * n * len(sementes)) // 200)
    cont = [0]

    def guardar(esp, fa, fb, s, p, pts):
        contar_decisoes(p, decisoes)
        turnos.append(p.turnos)
        fins[p.motivo_fim] += 1
        if fa == fb:
            espelho[fa].append(p.pontos_a)
        linhas_csv.append(["e1", esp, s, p.nome_a, p.nome_b, p.semente, p.pontos_a, p.motivo_fim, p.turnos,
                           repr(p.estado_final.lados[0].hp), repr(p.estado_final.lados[1].hp)])
        if cont[0] % passo == 0 and len(amostra) < 200:
            amostra.append((esp, p))
        cont[0] += 1

    print("E1 ...", flush=True)
    conf_e1 = round_robin_arquetipos(especies, sementes, n, r, cfg21, guardar=guardar)
    taxa_arq = matriz_taxas(conf_e1)
    ok_e1, val_e1 = avaliar_e1(taxa_arq, cb)
    _gravar(saida / "matriz_arquetipos.json", _dump({
        "unidade": "pontos medios da linha contra a coluna (empate = 0.5); os dois lados da mesma especie; "
                   "agregado sobre as especies ativas",
        "especies": especies, "sementes": sementes, "partidas_por_par_por_semente": n, "taxa": taxa_arq,
        "n_partidas": len(conf_e1),
    }))
    _gravar(saida / "equilibrio.json", _dump({**val_e1, "peso_minimo_suporte": cb.peso_minimo_suporte}))
    gate("E1_sem_arquetipo_dominante", ok_e1,
         (f"nenhum arquetipo vence todos; suporte {val_e1['suporte']} (>= {cb.suporte_minimo_e1})" if ok_e1 else
          f"FALHOU: dominantes {val_e1['dominantes']}; suporte {val_e1['suporte']} (precisa >= {cb.suporte_minimo_e1})"),
         val_e1)

    # ------------------------------------------------------------ E2
    print("E2 ...", flush=True)
    conf_e2, por_forma = [], {}
    for f in FORMAS:
        lut = {e: lutador_adulto(f, e, cfg21) for e in especies}
        conf_f = []
        for i, ea in enumerate(especies):
            for eb in especies[i:]:
                for _, p, pts, _ in partidas_par(lut[ea], lut[eb], f"e2|{f}", sementes, n, r):
                    conf_f.append((ea, eb, pts))
        por_forma[f] = matriz_taxas(conf_f)
        conf_e2 += conf_f
    taxa_esp = matriz_taxas(conf_e2)
    dom_esp = [e for e in especies if all(taxa_esp[e][o] > 0.5 for o in especies if o != e)]
    dom_por_forma = {f: [e for e in especies if all(m[e][o] > 0.5 for o in especies if o != e)]
                     for f, m in por_forma.items()}
    _gravar(saida / "matriz_especie_arquetipo.json", _dump({
        "unidade": "pontos medios da especie da linha contra a da coluna, mesmo arquetipo e estilo dos dois lados",
        "agregada": taxa_esp, "por_arquetipo": por_forma,
        "media_por_especie_e_arquetipo": {f: {e: sum(m[e][o] for o in especies) / len(especies) for e in especies}
                                          for f, m in por_forma.items()},
        "dominante_por_arquetipo_informativo": dom_por_forma,
    }))
    gate("E2_sem_especie_dominante", not dom_esp,
         f"especie que vence todas as outras (agregado sobre arquetipos): {dom_esp or 'nenhuma'}; "
         f"por arquetipo (informativo): { {f: d for f, d in dom_por_forma.items() if d} or 'nenhuma'}",
         {"dominantes": dom_esp, "dominante_por_arquetipo": dom_por_forma})

    # ------------------------------------------------------------ E3
    print("E3 ...", flush=True)
    uso = {}
    for f in FORMAS:
        tot = sum(sum(decisoes[f"{f}@{e}"].values()) for e in especies)
        tec = TECNICA_DA_LINHA[LINHA_DA_FORMA[f]]
        usos = sum(decisoes[f"{f}@{e}"].get(tec, 0) for e in especies)
        uso[f] = {"tecnica": tec, "fracao": usos / tot if tot else 0.0,
                  "por_acao": {a.value: sum(decisoes[f"{f}@{e}"].get(a.value, 0) for e in especies) / tot
                               for a in ACOES_ESCOLHIVEIS}}
    pouco_usadas = sorted(f for f, u in uso.items() if u["fracao"] < cb.fracao_min_tecnica)
    resposta = {}
    for tec in TECNICAS:
        usuarios = [f for f in FORMAS if TECNICA_DA_LINHA[LINHA_DA_FORMA[f]] == tec]
        pts_orig, pts_resp = [], []
        for esp in especies:
            for u in usuarios:
                eu = lutador_adulto(u, esp, cfg21)
                for op in FORMAS:
                    base = lutador_adulto(op, esp, cfg21, nome=f"{op}@{esp}#op")
                    resp = lutador_adulto(op, esp, cfg21, gambits=com_resposta(_bots.gambits_adulto(op, cfg21), tec, RESPOSTAS_V21C if cfg.get("respostas_v21c") else None), nome=f"{op}@{esp}#resp")
                    pts_orig += [x for _, _, x, _ in partidas_par(eu, base, f"e3|{tec}", sementes,
                                                                  cb.partidas_e3_por_semente, r)]
                    pts_resp += [x for _, _, x, _ in partidas_par(eu, resp, f"e3|{tec}", sementes,
                                                                  cb.partidas_e3_por_semente, r)]
        o, s_ = sum(pts_orig) / len(pts_orig), sum(pts_resp) / len(pts_resp)
        resposta[tec] = {"usuarios": usuarios, "taxa_sem_resposta": o, "taxa_com_resposta": s_,
                         "reducao": o - s_, "regras_resposta": [x.para_dict() for x in RESPOSTAS[tec]]}
    sem_resposta = sorted(t for t, v in resposta.items() if not v["reducao"] > 0.0)
    _gravar(saida / "uso_tecnicas.json", _dump({"uso_nas_partidas_do_e1": uso, "resposta_declarada": resposta}))
    gate("E3_tecnica_usada_e_respondivel", not pouco_usadas and not sem_resposta,
         f"tecnica abaixo de {cb.fracao_min_tecnica} das decisoes: {pouco_usadas or 'nenhuma'}; "
         f"resposta que NAO reduz a taxa do usuario: {sem_resposta or 'nenhuma'}; "
         + ", ".join(f"{t} {v['taxa_sem_resposta']:.3f}->{v['taxa_com_resposta']:.3f}" for t, v in resposta.items()),
         {"fracao_tecnica": {f: u["fracao"] for f, u in uso.items()}, "pouco_usadas": pouco_usadas,
          "resposta": {t: {k: v[k] for k in ("taxa_sem_resposta", "taxa_com_resposta", "reducao")}
                       for t, v in resposta.items()}, "sem_resposta_efetiva": sem_resposta})

    # ------------------------------------------------------------ E4
    print("E4 ...", flush=True)
    e4 = {}
    for f in FORMAS:
        linha = LINHA_DA_FORMA[f]
        pts = []
        for esp in especies:
            ad = lutador_adulto(f, esp, cfg21)
            adol = lutador_adolescente(linha, esp, carater_canonico(f), cfg21)
            pts += [x for _, _, x, _ in partidas_par(ad, adol, "e4", sementes, cb.partidas_e4_por_semente, r)]
        e4[f] = sum(pts) / len(pts)
    if ESCALA is None:
        fora_e4 = {f: t for f, t in e4.items() if not cb.taxa_min_e4 <= t <= cb.taxa_max_e4}
        gate("E4_estagio_importa_sem_esmagar", not fora_e4,
             f"adulto x adolescente da mesma linha: fora de [{cb.taxa_min_e4}, {cb.taxa_max_e4}]: "
             f"{ {f: round(t, 3) for f, t in fora_e4.items()} or 'nenhum'}",
             {"taxa_por_forma": e4, "fora": fora_e4})
    else:
        # E4 na escala (redefinido pelo Matheus): a evolucao sempre importa. Adulto SEM treino x adolescente da mesma
        # linha sem treino e com o treino maximo do estagio (uniforme): o adulto vence >= taxa_min_e4 nos dois; sem teto
        from digilab.config import STATS_V21
        tr = {k: ESCALA.treino_e4 / len(STATS_V21) for k in STATS_V21}
        e4t = {}
        for f in FORMAS:
            pts = []
            for esp in especies:
                ad = lutador_adulto(f, esp, cfg21)
                adol = lutador_adolescente(LINHA_DA_FORMA[f], esp, carater_canonico(f), cfg21, treino=tr)
                pts += [x for _, _, x, _ in partidas_par(ad, adol, "e4t", sementes, cb.partidas_e4_por_semente, r)]
            e4t[f] = sum(pts) / len(pts)
        baixo = {f"{f} (sem treino)": t for f, t in e4.items() if t < ESCALA.taxa_min_e4}
        baixo |= {f"{f} (+{ESCALA.treino_e4:g})": t for f, t in e4t.items() if t < ESCALA.taxa_min_e4}
        gate("E4_escala_estagio_importa", not baixo,
             f"adulto sem treino x adolescente (sem treino e com +{ESCALA.treino_e4:g}): abaixo de {ESCALA.taxa_min_e4}: "
             f"{ {k: round(t, 3) for k, t in baixo.items()} or 'nenhum'}; menor {min(list(e4.values()) + list(e4t.values())):.3f}",
             {"taxa_sem_treino": e4, "taxa_adolescente_treinado": e4t, "abaixo": baixo})

    # ------------------------------------------------------------ E5
    e5 = {}
    if cfg.get("pular_e5"):
        gate("E5_robustez", False, "PULADO (pular_e5 no config): nao vale como aprovacao", {})
    else:
        print("E5 ...", flush=True)
        for campo, rot, de, para in perturbacoes(cb.perturbacao_e5, r.v21):
            rp = Regras(base=r.base, v21=replace(r.v21, **{campo: para}))
            conf = round_robin_arquetipos(especies, sementes, cb.partidas_e5_por_semente, rp, rp.v21, rotulo="e5")
            ok, val = avaliar_e1(matriz_taxas(conf), cb)
            e5[f"{campo}{rot}"] = {"de": de, "para": para, "e1_ok": ok, "suporte": val["suporte"],
                                   "dominantes": val["dominantes"]}
        passaram = sum(v["e1_ok"] for v in e5.values())
        gate("E5_robustez", passaram > len(e5) / 2,
             f"E1 mantido em {passaram}/{len(e5)} perturbacoes de +-{cb.perturbacao_e5:.0%}; falham: "
             f"{[k for k, v in e5.items() if not v['e1_ok']] or 'nenhuma'}",
             {"passaram": passaram, "total": len(e5), "por_perturbacao": e5})
    _gravar(saida / "robustez_e5.json", _dump(e5))

    # ------------------------------------------------------------ sanidade (replay e espelhos)
    with (saida / "partidas.csv").open("w", encoding="utf-8", newline="") as fcsv:
        w = csv.writer(fcsv, lineterminator="\n")
        w.writerow(["bloco", "especie", "semente_conjunto", "lado_a", "lado_b", "semente_partida", "pontos_a",
                    "fim", "turnos", "hp_a", "hp_b"])
        w.writerows(linhas_csv)
    _gravar(saida / "amostra_replay.jsonl", "".join(p.para_jsonl() for _, p in amostra))
    logs, atual = [], []
    for linha in (saida / "amostra_replay.jsonl").read_text(encoding="utf-8").splitlines():
        ev = json.loads(linha)
        if ev["tipo"] == "cabecalho" and atual:
            logs.append(atual)
            atual = []
        atual.append(ev)
    if atual:
        logs.append(atual)
    for (esp, _), log in zip(amostra, logs):
        fa, fb = log[0]["a"].split("@")[0], log[0]["b"].split("@")[0]
        reproduzir(log, lutador_adulto(fa, esp, cfg21), lutador_adulto(fb, esp, cfg21), r)
    vies = {f: sum(v) / len(v) for f, v in espelho.items() if v}
    med = statistics.median(turnos)
    frac_lim = fins["limite"] / len(turnos)
    gate("sanidade_informativo", len(logs) == len(amostra),
         f"{len(logs)} partidas rejogadas do disco bit a bit; pontos do lado 0 nos espelhos "
         f"{ {f: round(v, 3) for f, v in vies.items()} }; mediana de turnos {med}; "
         f"{frac_lim:.3f} no limite de turnos",
         {"replay_partidas": len(logs), "pontos_lado0_espelho": vies, "mediana_turnos": med,
          "fracao_limite": frac_lim, "fins": fins})

    # ------------------------------------------------------------ base G1-G7
    if "regras_base" in cfg:
        # V21C: a base e a V2C; vale a validacao dela (G6b do atirador aceito como excecao pelo Matheus)
        vb = json.loads((RAIZ / "artifacts_combate_v2c" / "validacao_bots" / "gates.json").read_text(encoding="utf-8"))
        ok_base = set(vb["falharam"]) <= {"G6b_espelho_condicao"}
        gate("G1_G9_base_v2c", ok_base,
             f"base V2C (artifacts_combate_v2c/validacao_bots): {vb['status']}, falharam {vb['falharam']} "
             f"(G6b do atirador aceito como excecao: docs/REGISTRO_DESVIOS.md)",
             {"falharam": vb["falharam"]})
    else:
        base_gates = json.loads((RAIZ / "artifacts_combate_v2" / "gates.json").read_text(encoding="utf-8"))
        base_cfg = json.loads((RAIZ / "experiments" / "configs" / "bateria_canonico.json").read_text(encoding="utf-8"))
        base_intacta = hashes_base(base_cfg)["regras_sha256"] == base_gates["hashes"]["regras_sha256"]
        gate("G1_G7_base", base_intacta,
             f"fontes da base {'INTACTOS' if base_intacta else 'ALTERADOS'} (hash igual ao de artifacts_combate_v2); "
             f"status gravado da base: {base_gates['status']} (falharam {base_gates['falharam']}; reprovacao "
             f"registrada em docs/REGISTRO_DESVIOS.md, nao reavaliada aqui)",
             {"status_base": base_gates["status"], "falharam_base": base_gates["falharam"], "fontes_intactos": base_intacta})

    if cfg.get("gates_v2c"):
        gates_v21c(gate, r, cfg21, especies, sementes, n, e5, conf_e1, linhas_csv)

    aprovada = all(g["ok"] for g in gates if g["gate"] not in ("sanidade_informativo",))
    registro = None
    if cfg.get("registro_calibracao"):
        registro = json.loads((RAIZ / cfg["registro_calibracao"]).read_text(encoding="utf-8"))
    resumo = {
        "status": "APROVADA" if aprovada else "REPROVADA",
        "falharam": [g["gate"] for g in gates if not g["ok"] and g["gate"] != "sanidade_informativo"],
        "gates": gates, "conjunto": cfg["conjunto"], "sementes": sementes,
        "sementes_calibracao": cfg["sementes_calibracao"], "sementes_validacao": cfg["sementes_validacao"],
        "partidas_por_par_por_semente": n, "especies": especies, "hashes": hashes(cfg),
        "config_combate_v21": asdict(cfg21), "config_base": asdict(r.base), "config_bateria_v21": asdict(CONFIG_BATERIA_V21),
        "registro_calibracao": registro,
        "avisos": ["todos os numeros de ConfigCombateV21, ConfigCatalogo e ConfigBateriaV21 sao PROPOSTOS",
                   "pre-condicoes da especificacao nao cumpridas: ver docs/REGISTRO_DESVIOS.md"]
                  + ([] if cfg["conjunto"] == "validacao" else ["conjunto de CALIBRACAO: nao e a run canonica"]),
        "ambiente": {"python": platform.python_version(), "plataforma": platform.platform()},
    }
    arquivos = ["matriz_arquetipos.json", "matriz_especie_arquetipo.json", "uso_tecnicas.json", "equilibrio.json",
                "robustez_e5.json", "partidas.csv", "amostra_replay.jsonl"]
    resumo["artefatos_sha256"] = {a: hashlib.sha256((saida / a).read_bytes()).hexdigest() for a in arquivos}
    _gravar(saida / "gates.json", _dump(resumo))
    print(f"bateria V2.1 {resumo['status']}  conjunto {cfg['conjunto']}  saida {saida}")
    return 0 if aprovada else 2


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Bateria do combate V2.1")
    ap.add_argument("--config", required=True, type=Path)
    return executar(ap.parse_args(argv).config)


if __name__ == "__main__":
    sys.exit(main())
