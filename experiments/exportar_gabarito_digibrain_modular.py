"""O gabarito do DigiBrain modular para a web (docs/TAREFA_V3_LAB_MODULAR.md, etapa LM0): vidas curtas do mundo (`longe_fixo` e comedouro) com o
cerebro modular na configuracao do laboratorio (secao 3 da tarefa), gravando por decisao a entrada e a saida de cada modulo, o motivo e uma
assinatura do estado. O TS (LM1 a LM4, `web/app/motor/digibrain/`) porta os modulos e confere contra estes arquivos.

A configuracao (o braco "REL" da C4, `run_v2_digibrain_prototipo.SUBCHAVES_C4`): `ConfigDigibrain` ligada com p1, p2, m_mem e persistencia
(os padroes), `cheiro_inato` e `intencao_cheiro` (o M3*, a C1) e `memoria_autobio` com `controle_mem = "rel"` (a C4). Ficam desligadas
`facetas_mem`, `redecidir_evento`, `credito_corrida`, `intencao_suspensa` e `modula_g_apr`. Os valores de partida sao os de
`ConfigDigibrainInatos` (PROPOSTOS), como estao. Nenhum numero nasce aqui.

**Como grava** (fora do pacote `digilab/digibrain/`, que nao muda): embrulha, na instancia do cerebro, os metodos dos modulos e os ganchos
do M-ADAPT. Uma chamada de modulo e gravada so quando feita direto pelo M-ADAPT (as contas internas, como o `habito` dentro do
`Impulso.unidades`, ficam dentro da saida do modulo que as chamou). Cada chamada guarda:
  - `m`: o modulo e o metodo (`sens.codificar`, `afeto.ler`, ..., `adapt.agir`);
  - `e`: a entrada (o que o TS recebe), `s`: a saida, nos tipos do JSON (tupla vira lista; o enum, o valor);
  - um argumento ou retorno que e o MESMO objeto de uma saida anterior da mesma decisao vira `{"$ref": "<modulo.metodo>"}` (a `sens` passa por
    seis modulos; gravar uma vez so). O exportador confere que o objeto nao mudou entre a saida e a referencia;
  - a rng de politica (so o M-ARB a recebe) vira o sha256 do estado dela antes (`e`) e depois (`rng_depois`);
  - o modulo e o objeto (a `plast` em `Impulso.unidades`, o `casa` do M-MEM) entram como o texto `<plast>` ou `<fn>`: o estado deles esta
    na assinatura.
Uma decisao `k` tem as chamadas em ordem: os gestos do dono desde a decisao anterior (`adapt.receber_acao_dono`), o `adapt.agir` e, dentro
dele, os modulos (o fechamento da decisao `k - 1`, que o M-ADAPT faz no comeco da `k`, vem primeiro: `afeto.consequencia`,
`plast.consequencia_p1`, `estado.consequencia`, `mem.codificar`, `adapt.episodio_autobio`, `mem.codificar_autobio`), depois os ganchos
`adapt.escolher_alvo`, `adapt.consequencia_corpo`, `adapt.observar` e `adapt.consequencia_mundo` da decisao `k`.

**A assinatura** (`assinatura`, por decisao, depois do `adapt.agir`): o sha256 (16 primeiros hex) do `estado_interno()` de cada modulo que o
tem (`sens`, `afeto`, `estado`, `mem`, `arb`, `plast`; o `impulso` nao guarda estado), em JSON com as chaves ordenadas. **O motivo**
(`motivo`): o `cerebro.motivos[k]` ao fim da vida, ja com a consequencia. Por vida: o sha256 do log do motor e o do estado interno inteiro
do cerebro (`estado`), os mesmos das impressoes de `tests/gabarito_habito_intencao.py`.

Sementes: as dos testes (101 a 505); nao sao vidas de pesquisa e nenhuma faixa e reservada. Os arquivos:
  - `digibrain_modular_constantes.json`: a `ConfigDigibrain`, a `ConfigDigibrainInatos`, os valores efetivos, e a cobertura das vidas;
  - `digibrain_modular_<lugar>.json.gz`: as vidas do lugar (`longe_fixo`, `comedouro`); cada uma passa de 10 MB, entao vai em .gz e o
    sha256 do texto original fica nas constantes (`arquivos`).

    python experiments/exportar_gabarito_digibrain_modular.py            # grava os tres arquivos
"""
from __future__ import annotations

import gzip
import hashlib
import json
import random
import sys
from dataclasses import asdict, fields, is_dataclass, replace
from enum import Enum
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import run_v2_digibrain_prototipo as orq  # noqa: E402
from bancada.regras_mundo import simular_vida_fisico  # noqa: E402

from digilab.config import CONFIG_DIGIBRAIN_INATOS, CONFIG_DIGIBRAIN_LIGADA, CONFIG_PADRAO  # noqa: E402
from digilab.digibrain import adapt as adapt_mod  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.mundo import DonoComLugar  # noqa: E402

PASTA = RAIZ / "web" / "app" / "test" / "gabaritos"
PREFIXO = "digibrain_modular_"
ARQUIVO_CONSTANTES = PASTA / f"{PREFIXO}constantes.json"
BRACO = "REL"                                     # o M3* com a memoria_autobio, controle_mem = "rel" (SUBCHAVES_C4)
LUGARES = ("longe_fixo", "comedouro")
DONOS = ("atencioso", "relapso")                  # o atencioso (come) e o relapso (deixa de cuidar: o P2 e a lembranca)
SEMENTES = (101, 202)                             # as dos testes
DIAS = 4

# o que cada modulo expoe ao M-ADAPT: (atributo do cerebro.m, metodos gravados)
METODOS = {
    "sens": ("codificar",),
    "afeto": ("ler", "drives", "consequencia"),
    "arb": ("reflexo", "escolher"),
    "estado": ("contexto", "escolhida", "consequencia"),
    "impulso": ("unidades",),
    "plast": ("montar", "consequencia_p1", "creditar"),
    "mem": ("relogio", "consolidar", "lembrar", "termo_lembranca", "recuperar", "codificar", "codificar_autobio",
            "classes_com_positivo"),
}
GANCHOS = ("agir", "escolher_alvo", "consequencia_corpo", "observar", "consequencia_mundo", "receber_acao_dono")
ASSINADOS = ("sens", "afeto", "estado", "mem", "arb", "plast")


def config_laboratorio():
    """a ConfigDigibrain do laboratorio: a do braco REL da C4 (a mesma que a avaliacao rodou)"""
    return orq.config_do_braco(BRACO, conserto=True)


def _sha(texto: str, n: int = 64) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:n]


def _texto(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def paraj(v):
    """o valor nos tipos do JSON: dataclass em dict, tupla em lista, enum no valor, modulo e funcao em texto"""
    if v is None or isinstance(v, (bool, int, float, str)):
        return v
    if isinstance(v, Enum):
        return v.value
    if is_dataclass(v) and not isinstance(v, type):
        return {f.name: paraj(getattr(v, f.name)) for f in fields(v)}
    if isinstance(v, dict):
        return {str(k): paraj(x) for k, x in v.items()}
    if isinstance(v, (list, tuple, set, frozenset)):
        return [paraj(x) for x in (sorted(v) if isinstance(v, (set, frozenset)) else v)]
    if isinstance(v, random.Random):
        return "rng:" + _sha(_texto(paraj(v.getstate())), 16)
    if callable(v):
        return "<fn>"
    return f"<{type(v).__name__.lower()}>"


def _obs_enxuta(obs) -> dict:
    """a Observacao so com o que o modular le: o vetor de estado, os ticks desde o cuidado, o corpo e o mundo"""
    return {"vetor_estado": paraj(obs.vetor_estado), "ticks_desde_cuidado": obs.ticks_desde_cuidado, "corpo": paraj(obs.corpo),
            "mundo": paraj(obs.mundo)}


class Gravador:
    """embrulha o cerebro de uma vida e junta as chamadas por decisao"""

    def __init__(self, cerebro) -> None:
        self.c = cerebro
        self.chamadas: dict[int, list] = {}
        self.assinaturas: dict[int, dict] = {}
        self.prof = 0
        self.refs: dict[int, tuple] = {}              # id(objeto) -> (rotulo, texto, objeto): as saidas da decisao em curso
        for nome, metodos in METODOS.items():
            modulo = getattr(cerebro.m, nome)
            for metodo in metodos:
                setattr(modulo, metodo, self._embrulhar(f"{nome}.{metodo}", getattr(modulo, metodo), 1, nome))
        for gancho in GANCHOS:
            setattr(cerebro, gancho, self._embrulhar(f"adapt.{gancho}", getattr(cerebro, gancho), 0, "adapt"))
        self._episodio_original = adapt_mod.episodio_autobio
        adapt_mod.episodio_autobio = self._embrulhar("adapt.episodio_autobio", self._episodio_original, 1, "adapt")

    def soltar(self) -> None:
        adapt_mod.episodio_autobio = self._episodio_original

    # ------------------------------------------------------------ o registro de uma chamada
    def _k(self, rotulo: str) -> int:
        k = self.c.k
        if rotulo == "adapt.agir" or rotulo == "adapt.receber_acao_dono":
            return k
        if rotulo.startswith("adapt."):
            return k - 1
        return k                                      # o modulo chamado dentro do agir (k ainda nao andou: so anda no fim dele)

    def _ref(self, v):
        """o objeto igual a uma saida anterior da decisao vira a referencia (conferida)"""
        if isinstance(v, (dict, list)) and id(v) in self.refs:
            rotulo, texto, obj = self.refs[id(v)]
            if _texto(paraj(v)) != texto:
                raise RuntimeError(f"o objeto de {rotulo} mudou entre a saida e a referencia")
            return {"$ref": rotulo}
        return None

    def _entrada(self, rotulo: str, args: tuple, kwargs: dict):
        itens = [*args, *[kwargs[k] for k in sorted(kwargs)]]
        out = []
        for v in itens:
            r = self._ref(v)
            if r is not None:
                out.append(r)
            elif rotulo == "adapt.agir" and not isinstance(v, random.Random) and hasattr(v, "corpo"):
                out.append(_obs_enxuta(v))
            elif rotulo == "adapt.escolher_alvo" and hasattr(v, "vistos"):
                out.append("<percepcao>")             # a mesma do agir
            elif rotulo == "adapt.consequencia_corpo" and hasattr(v, "corpo"):
                out.append({"corpo": paraj(v.corpo)})
            elif rotulo == "adapt.consequencia_mundo" and hasattr(v, "mundo"):
                out.append({"mundo": paraj(v.mundo)})
            elif rotulo == "adapt.observar" and hasattr(v, "observacao_seguinte"):
                out.append({"acao": paraj(v.acao), "mundo": paraj(v.observacao_seguinte.mundo)})
            else:
                out.append(paraj(v))
        return out

    def _embrulhar(self, rotulo: str, original, nivel: int, modulo: str):
        def f(*args, **kwargs):
            registrar = self.prof == nivel
            if not registrar:
                return original(*args, **kwargs)
            k = self._k(rotulo)
            if rotulo == "adapt.agir":
                self.refs = {}
            reg = {"m": rotulo, "e": self._entrada(rotulo, args, kwargs)}
            rng_antes = [(_sha(_texto(paraj(v.getstate())), 16)) for v in (*args, *kwargs.values()) if isinstance(v, random.Random)]
            self.chamadas.setdefault(k, []).append(reg)
            self.prof += 1
            try:
                ret = original(*args, **kwargs)
            finally:
                self.prof -= 1
            if rng_antes:
                reg["rng_antes"] = rng_antes
                reg["rng_depois"] = [_sha(_texto(paraj(v.getstate())), 16) for v in (*args, *kwargs.values())
                                     if isinstance(v, random.Random)]
            reg["s"] = paraj(ret)
            if isinstance(ret, (dict, list)):
                self.refs[id(ret)] = (rotulo, _texto(reg["s"]), ret)
            if isinstance(ret, tuple):
                for i, x in enumerate(ret):
                    if isinstance(x, (dict, list)):
                        self.refs[id(x)] = (f"{rotulo}[{i}]", _texto(paraj(x)), x)
            if rotulo == "adapt.agir":
                self.assinaturas[k] = self.assinar()
            return ret
        return f

    def assinar(self) -> dict:
        m = self.c.m
        return {nome: _sha(_texto(paraj(getattr(m, nome).estado_interno())), 16) for nome in ASSINADOS}


def viver(dono: str, lugar: str, semente: int, gravar: bool = True, inatos=None):
    """a vida: (o motor, o cerebro, o gravador). Sem `gravar`, a mesma vida sem o embrulho (o gravador e None): o teste confere que o
    Gravador nao a muda. `inatos` (LM4, so o arquivo dos fins): os valores de partida de outra `ConfigDigibrainInatos`; None, os de hoje"""
    fp, fm = orq.fabricas(BRACO, dono, semente, DIAS, orq.ORCAMENTO_POR_DIA, conserto=True, inatos=inatos)
    registro = fp(CONFIG_PADRAO)
    cerebro = orq.cerebro_de(registro)
    g = Gravador(cerebro) if gravar else None
    try:
        d = DonoComLugar(criar_dono(dono), lugar, semente, dono, orq.CM)
        motor, _ = simular_vida_fisico(d, registro, semente, DIAS, orq.ORCAMENTO_POR_DIA * DIAS, dono, fm)
    finally:
        if g is not None:
            g.soltar()
    return motor, cerebro, g


def _vida(dono: str, lugar: str, semente: int) -> tuple[dict, dict]:
    """(a vida gravada, a cobertura dela)"""
    motor, cerebro, g = viver(dono, lugar, semente)
    n = len(cerebro.motivos)
    decisoes = []
    for k in range(n):
        decisoes.append({"k": k, "chamadas": g.chamadas.get(k, []), "assinatura": g.assinaturas[k], "motivo": paraj(cerebro.motivos[k])})
    extras = sorted(set(g.chamadas) - set(range(n)))
    if extras:
        raise RuntimeError(f"chamadas fora das decisoes: {extras}")
    vida = {"braco": BRACO, "dono": dono, "lugar": lugar, "semente": semente, "dias": DIAS, "decisoes": decisoes,
            "log": hashlib.sha256(motor.log.para_jsonl().encode("utf-8")).hexdigest(),
            "estado": hashlib.sha256(_texto(paraj(cerebro.estado_interno())).encode("utf-8")).hexdigest(),
            "assinatura_final": g.assinar()}
    return vida, cobertura_da_vida(cerebro)


def cobertura_da_vida(c) -> dict:
    ms = c.motivos
    return {
        "decisoes": len(ms),
        "acoes": sorted({m["acao"] for m in ms}),
        "reflexo": sum(1 for m in ms if m["reflexo"]),
        "habito_p2": sum(1 for m in ms if any(u["termos"]["habito"] for u in m["unidades"])),
        "incentivo_p1": sum(1 for m in ms if any(u["termos"]["incentivo"] for u in m["unidades"])),
        "persistencia": sum(1 for m in ms if any(u["termos"]["persistencia"] for u in m["unidades"])),
        "memoria_recuperada": sum(1 for m in ms if m["memoria"] and m["memoria"]["recuperado"]),
        "lembranca_com_termo": sum(1 for m in ms if m["lembranca"]["L"] is not None),
        "lembranca_sem": sum(1 for m in ms if m["lembranca"]["L"] is None),
        "lembranca_sondas_sem_lembranca": sum(1 for m in ms if "sem_lembranca" in _texto(m["sondas"])),
        "lugar_lembrado_alvo": sum(1 for m in ms if m.get("alvo", {}).get("do_mem")),
        "consolidacoes": sum(1 for m in ms if m["consolidacao"] is not None),
        "episodios_autobio": sum(1 for m in ms if (m["consequencia"] or {}).get("autobio") is not None),
        "episodios_m_mem": sum(1 for m in ms if (m["consequencia"] or {}).get("episodio") is not None),
        "fins": sorted({f["motivo"] for m in ms for f in m["fins"]}),
        "busca_entregue": sum(1 for m in ms if m.get("busca_entregue")),
        "gestos_do_dono": sum(len(m["gestos"]) for m in ms),
    }


def constantes() -> dict:
    cd = config_laboratorio()
    return {"versao": 1, "braco": BRACO,
            "config_digibrain": asdict(cd), "config_digibrain_inatos": paraj(asdict(CONFIG_DIGIBRAIN_INATOS)),
            "ligadas": sorted(k for k, v in asdict(cd).items() if v is True), "desligadas": sorted(
                k for k, v in asdict(cd).items() if v is False),
            "metodos_gravados": {k: list(v) for k, v in METODOS.items()}, "ganchos": list(GANCHOS),
            "vidas": [{"dono": d, "lugar": lg, "semente": s, "dias": DIAS} for lg in LUGARES for d in DONOS for s in SEMENTES]}


def gerar() -> dict:
    """{nome do conteudo: dict}: as vidas de cada lugar e as constantes (com a cobertura)"""
    cfg = constantes()
    if config_laboratorio() != replace(CONFIG_DIGIBRAIN_LIGADA, **orq.SUBCHAVES_C4[BRACO]):
        raise RuntimeError("a config do laboratorio nao e a do braco REL")
    out, cobertura = {}, []
    for lugar in LUGARES:
        vidas = []
        for dono in DONOS:
            for semente in SEMENTES:
                vida, cob = _vida(dono, lugar, semente)
                vidas.append(vida)
                cobertura.append({"dono": dono, "lugar": lugar, "semente": semente, **cob})
        out[f"{PREFIXO}{lugar}.json"] = {"versao": 1, "braco": BRACO, "lugar": lugar, "vidas": vidas}
    cfg["cobertura"] = cobertura
    out[ARQUIVO_CONSTANTES.name] = cfg
    return out


def texto_do_arquivo(conteudo: dict) -> str:
    return json.dumps(conteudo, sort_keys=True, separators=(",", ":")) + "\n"


def arquivos(conteudos: dict | None = None) -> dict[str, bytes]:
    """{nome no disco: bytes}. As vidas de cada lugar passam de 10 MB: vao em .gz (mtime 0, nivel 9) e o sha256 do texto original, de
    antes do gzip, fica nas constantes (`arquivos`). O que o teste compara e o texto original, nao os bytes do gzip."""
    conteudos = conteudos or gerar()
    constantes_ = conteudos[ARQUIVO_CONSTANTES.name]
    out, resumo = {}, {}
    for nome, c in conteudos.items():
        if nome == ARQUIVO_CONSTANTES.name:
            continue
        bruto = texto_do_arquivo(c).encode("utf-8")
        resumo[nome] = {"sha256": hashlib.sha256(bruto).hexdigest(), "bytes": len(bruto), "gz": nome + ".gz"}
        out[nome + ".gz"] = gzip.compress(bruto, compresslevel=9, mtime=0)
    constantes_["arquivos"] = resumo
    out[ARQUIVO_CONSTANTES.name] = texto_do_arquivo(constantes_).encode("utf-8")
    return out


def texto_original(nome: str, dados: bytes) -> bytes:
    """o texto do arquivo, sem o gzip"""
    return gzip.decompress(dados) if nome.endswith(".gz") else dados


def gravar(dados: dict[str, bytes]) -> None:
    for nome, b in dados.items():
        (PASTA / nome).write_bytes(b)


# ---------------------------------------------------------------------------------------------------------------------------------------
# LM1: as leituras do M-PLAST dentro do `Impulso.unidades` (`habito` e `incentivo`). O gabarito da LM0 nao as guarda (ficam dentro da saida do
# impulso), e o incentivo nao se reconstroi so dos termos (mul(incentivo, prox) perde o incentivo). Arquivo a parte: o das vidas da LM0 nao muda.
ARQUIVO_LEITURAS_PLAST = f"{PREFIXO}leituras_plast.json.gz"


def _leituras_da_vida(dono: str, lugar: str, semente: int) -> list:
    """por decisao k, as chamadas do `plast.habito(b, z)` e do `plast.incentivo(pc, classe, drives)` na ordem em que o impulso as fez"""
    fp, fm = orq.fabricas(BRACO, dono, semente, DIAS, orq.ORCAMENTO_POR_DIA, conserto=True)
    registro = fp(CONFIG_PADRAO)
    cerebro = orq.cerebro_de(registro)
    por_k: dict[int, list] = {}
    plast = cerebro.m.plast
    for metodo in ("habito", "incentivo"):
        original = getattr(plast, metodo)

        def f(*args, _o=original, _m=metodo):
            r = _o(*args)
            por_k.setdefault(cerebro.k, []).append({"m": f"plast.{_m}", "e": [paraj(a) for a in args], "s": r})
            return r
        setattr(plast, metodo, f)
    d = DonoComLugar(criar_dono(dono), lugar, semente, dono, orq.CM)
    simular_vida_fisico(d, registro, semente, DIAS, orq.ORCAMENTO_POR_DIA * DIAS, dono, fm)
    return [{"k": k, "chamadas": por_k.get(k, [])} for k in range(len(cerebro.motivos))]


def leituras_plast() -> bytes:
    """o gz (mtime 0, nivel 9) das leituras do M-PLAST das mesmas oito vidas do gabarito, na mesma ordem"""
    vidas = [{"dono": d, "lugar": lg, "semente": s, "decisoes": _leituras_da_vida(d, lg, s)}
             for lg in LUGARES for d in DONOS for s in SEMENTES]
    return gzip.compress(texto_do_arquivo({"versao": 1, "braco": BRACO, "vidas": vidas}).encode("utf-8"), compresslevel=9, mtime=0)


# ---------------------------------------------------------------------------------------------------------------------------------------
# LM4: o log das oito vidas (para o G-PAR-VIDA rejogar a vida inteira no laco do TS). O gabarito da LM0 grava o sha256 do log, nao o log: o TS
# precisa dos eventos do dono (os avancos, os gestos e a racao deixada) para rodar a mesma vida. Arquivo a parte; os da LM0 nao mudam.
ARQUIVO_LOGS = f"{PREFIXO}logs.json.gz"


def _log_da_vida(dono: str, lugar: str, semente: int) -> dict:
    """os eventos do log do motor da vida (tick, tipo, valor) e o sha256 do `para_jsonl`, o mesmo `log` do gabarito da vida"""
    motor, _, _ = viver(dono, lugar, semente, gravar=False)
    return {"dono": dono, "lugar": lugar, "semente": semente, "dias": DIAS, "log": [ev.para_dict() for ev in motor.log],
            "log_sha256": hashlib.sha256(motor.log.para_jsonl().encode("utf-8")).hexdigest()}


def logs() -> bytes:
    """o gz (mtime 0, nivel 9) dos logs das mesmas oito vidas do gabarito, na mesma ordem"""
    vidas = [_log_da_vida(d, lg, s) for lg in LUGARES for d in DONOS for s in SEMENTES]
    return gzip.compress(texto_do_arquivo({"versao": 1, "braco": BRACO, "vidas": vidas}).encode("utf-8"), compresslevel=9, mtime=0)


if __name__ == "__main__":
    if "--logs" in sys.argv:                          # so o arquivo da LM4; os da LM0 e da LM1 ficam como estao
        b = logs()
        (PASTA / ARQUIVO_LOGS).write_bytes(b)
        print(f"{PASTA / ARQUIVO_LOGS} ({len(b) / 1024 / 1024:.2f} MiB)")
        sys.exit(0)
    if "--leituras-plast" in sys.argv:                # so o arquivo da LM1; os da LM0 ficam como estao
        b = leituras_plast()
        (PASTA / ARQUIVO_LEITURAS_PLAST).write_bytes(b)
        print(f"{PASTA / ARQUIVO_LEITURAS_PLAST} ({len(b) / 1024 / 1024:.2f} MiB)")
        sys.exit(0)
    dados = arquivos()
    gravar(dados)
    for nome, b in dados.items():
        print(f"{PASTA / nome} ({len(b) / 1024 / 1024:.2f} MiB, {len(texto_original(nome, b)) / 1024 / 1024:.2f} MiB sem gzip)")
