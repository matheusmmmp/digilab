"""M-MEM, a memoria minima: os episodios de alimentacao e de visita (docs/ESPEC_DIGIBRAIN_MODULAR.md, secoes 4.6 e 9). E memoria
episodica minima, e so isto: a memoria autobiografica consolidada e etapa planejada (docs/TAREFA_V2_MEMORIA_AUTOBIOGRAFICA.md), nao
resolvida aqui.

**A codificacao** (`codificar`, na consequencia):
  - todo consumo (o comer, o "achou e comeu" do explorar) vira episodio, de origem "consumo", com a classe comida;
  - toda chegada a um lugar lembrado sem comer vira episodio de origem "visita", com r = 0 e a classe "nao_havia";
  - cada episodio guarda: o id, a decisao (o relogio do pet), o lugar (a celula do pet), o ponto (a posicao dele, em subunidades), a regiao,
    a classe, as variacoes dos receptores, o r e o r_n da consequencia, a hora e a falta da fome antes;
  - cheio (N_ep), sai o episodio de menor |r|; no empate, o mais antigo (a decisao, depois o id).
**A recuperacao** (`recuperar`, na decisao):
  - a pista: a urgencia da fome acima de `lambda_busca` e nenhuma comida boa a vista;
  - o valor de cada lugar e o r_n do episodio mais recente naquele lugar (a visita vazia derruba o lugar; a regra "o mais recente do lugar
    manda" e escolha nossa, SEM FONTE);
  - volta o lugar de maior `mul(valor, S - min(S, div_arred(dist x S, D_max)))`, se positivo; os empates se desfazem pelo episodio mais
    recente e depois pelo lugar;
  - o termo `M[explorar, P] = mul(w_mem, valor)`, e o alvo e o `Alvo.ponto` do ponto do episodio (o M-ADAPT o entrega so em EXPLORAR).
Sem rng. A interface que a memoria consolidada herda (secao 9): `codificar`, `recuperar`, `consolidar` (nada no prototipo),
`termos_decisao` e `evidencia_faceta` (vazio no prototipo).

**A C4, M0 e M1** (docs/ESPEC_MEMORIA_AUTOBIOGRAFICA_DIGIBRAIN_MODULAR.md, secao 3; a subchave `memoria_autobio`, desligada por padrao):
  - **o episodio** (M0, `episodio_autobio`): um dicionario de inteiros, listas e cadeias, sem float, so com o que o cerebro recebeu: o
    `sens` da decisao, o `pm1` do `observar` (a posicao e a regiao), as leituras dos receptores antes e depois, o afeto (V e E) antes e
    depois da consequencia, os gestos do dono desde a decisao anterior, a unidade escolhida e o desfecho que o M-ADAPT ja le hoje (a
    classe comida, o "chegou" e o r da ida). Os campos da tabela 3.1; os da M3 (`rep`, `rec`, `memoria`) nascem 0, 0 e "recente";
  - **a significancia** sigma (3.2): o r_n da consequencia; na visita vazia, min(0, r da ida), com o r da ida o `r` da opcao do `ponto`
    que acabou nela (o acumulado do M-ESTADO), nunca positivo (C4-E1, MA-1);
  - **quando vira episodio** (3.3, ME-1), nesta ordem, sem rng: o consumo; a visita ao lugar lembrado sem comer; |sigma| >= `theta_sig`
    ou a maior leitura de dor, susto ou estresse depois >= `theta_afeto` (a origem "evento"). O resto nao vira episodio;
  - **a categoria** (3.4): [comportamento, classe, sinal de sigma], com a classe a comida no consumo, "nao_havia" na visita e, no
    evento, a classe do objeto da unidade ou "sem_alvo";
  - **onde fica:** na `recente`, uma lista propria, com capacidade `n_rec`; cheia, sai o de menor |sigma| (o peso da 4.3 com rep = rec =
    0), no empate o mais antigo (a decisao, depois o id). **Nenhuma decisao le a recente nas M0 e M1** (a M4 e etapa posterior): o lugar
    lembrado segue a lista de hoje (`episodios`), e a vida com a subchave sai com o mesmo log da vida sem ela;
  - **o tick** (a referencia ao log): o relogio do pet refeito da hora do dia da Observacao (`relogio`): o dia avanca quando a hora volta,
    tick = dia x TICKS_POR_DIA + a hora em ticks.
Desligada, nada disso existe (o estado interno e o de hoje). Sem rng."""
from __future__ import annotations

from ..config import CONFIG_DIGIBRAIN_INATOS, TICKS_POR_DIA, TIPOS_ALVO_DIGIBRAIN, ConfigDigibrainInatos, ConfigMundo
from ..modelo_mundo import raiz_inteira
from ..policies.lobos import div_arred
from ._comum import chave_json, mul

CLASSES_EPISODIO = ("racao", "a", "b", "c", "podre", "nao_havia")
ORIGENS = ("consumo", "visita")
# a C4 (secao 3.4): as classes e as origens do episodio completo
CLASSES_AUTOBIO = CLASSES_EPISODIO + ("bola", "sem_alvo")
ORIGENS_AUTOBIO = ("consumo", "visita", "evento")
AFETIVOS = ("dor", "susto", "estresse")             # os receptores do limiar `theta_afeto` (3.3)


def _sinal(v: int) -> int:
    return (v > 0) - (v < 0)


def episodio_autobio(sens: dict, pm1, recs: tuple, l0: list, l1: list, afeto_antes: dict, cons: dict, gestos: list, unidade: dict,
                     desfecho: dict, k: int, tick: int, p: ConfigDigibrainInatos) -> dict | None:
    """o episodio completo (M0) do evento, ou None se ele nao vira episodio (M1); a docstring do modulo. `desfecho` = {"comeu": a classe
    da comida comida ou None, "chegou": chegou ao `ponto` da unidade, "r_ida": o r da opcao do `ponto` que acabou nesta consequencia (so
    na chegada)}"""
    acao, tipo, ident = unidade["chave"]
    corpo_antes, corpo_depois = dict(zip(recs, l0)), dict(zip(recs, l1))
    if desfecho["comeu"] is not None:
        origem, classe, sigma, ponto = "consumo", desfecho["comeu"], cons["r_n"], (pm1.x, pm1.y)
    elif tipo == "ponto" and desfecho["chegou"]:
        if type(desfecho["r_ida"]) is not int:
            raise ValueError(f"M-MEM: a visita sem o r da ida: {desfecho!r}")
        origem, classe, sigma, ponto = "visita", "nao_havia", min(0, desfecho["r_ida"]), tuple(ident)
    else:
        afetivo = max((corpo_depois[r] for r in AFETIVOS if r in corpo_depois), default=0)
        if abs(cons["r_n"]) < p.theta_sig and afetivo < p.theta_afeto:
            return None
        origem, classe, sigma, ponto = "evento", "sem_alvo", cons["r_n"], (pm1.x, pm1.y)
    o = unidade["objeto"]                             # o item do `sens` da decisao (a comida, a bola) ou None
    objeto = None if o is None else {"id": o["id"], "classe": o["classe"]}
    if objeto is not None and origem == "evento":
        classe = objeto["classe"]
    visita = origem == "visita"
    vistas = {o["classe"] for o in sens["objetos"]}
    return {"decisao": k, "tick": tick, "ponto": ponto, "regiao": pm1.regiao,
            "vista": [c for c in TIPOS_ALVO_DIGIBRAIN if c in vistas], "cheiro": bool(sens["ha_cheiro"]),
            "noite": sens["contexto"]["noite"] > 0, "acao": chave_json(unidade["chave"]), "objeto": objeto,
            "dono": [g[0] for g in gestos], "outro": None, "corpo_antes": corpo_antes, "corpo_depois": corpo_depois,
            "delta": {r: b - a for r, a, b in zip(recs, l0, l1)},
            "V_antes": afeto_antes["V"], "V_depois": cons["V"], "E_antes": afeto_antes["E"], "E_depois": cons["E"],
            "r": 0 if visita else cons["r"], "r_n": 0 if visita else cons["r_n"], "sigma": sigma,
            "classe": classe, "origem": origem, "categoria": [acao, classe, _sinal(sigma)],
            "fome_antes": sens["falta"].get("fome"), "hora": sens["minuto"], "rep": 0, "rec": 0, "memoria": "recente"}


class Memoria:
    """o M-MEM (docstring do modulo)"""

    def __init__(self, cfg_mundo: ConfigMundo, inatos: ConfigDigibrainInatos | None = None, autobio: bool = False) -> None:
        self.p = inatos or CONFIG_DIGIBRAIN_INATOS
        self.S = self.p.escala
        self.sub = cfg_mundo.sub
        self.episodios: list[dict] = []
        self.proximo_id = 0
        self.saidas: list[dict] = []          # os episodios que sairam por capacidade (id, |r|): o registro da PE-16
        self.recuperacoes = 0
        self.autobio = autobio
        if autobio:                                   # a C4 (desligada, nenhum campo novo)
            self.recente: list[dict] = []
            self.proximo_id_autobio = 0
            self.saidas_autobio: list[dict] = []      # os que sairam da recente por capacidade (id, sigma)
            self.dia, self.minuto = 0, None

    def lugar_de(self, x: int, y: int) -> tuple[int, int]:
        return x // self.sub, y // self.sub

    def codificar(self, ep: dict) -> int:
        """guarda o episodio (os campos da docstring, sem o id) e devolve o id"""
        if ep["classe"] not in CLASSES_EPISODIO or ep["origem"] not in ORIGENS:
            raise ValueError(f"M-MEM: episodio {ep!r}")
        if ep["origem"] == "visita" and (ep["r"] != 0 or ep["classe"] != "nao_havia"):
            raise ValueError("M-MEM: a visita sem comida tem r = 0 e a classe nao_havia")
        if len(self.episodios) >= self.p.n_ep:
            sai = min(self.episodios, key=lambda e: (abs(e["r"]), e["decisao"], e["id"]))
            self.episodios.remove(sai)
            self.saidas.append({"id": sai["id"], "r": sai["r"]})
        novo = {**ep, "id": self.proximo_id, "lugar": list(self.lugar_de(*ep["ponto"])), "ponto": list(ep["ponto"])}
        self.proximo_id += 1
        self.episodios.append(novo)
        return novo["id"]

    # ------------------------------------------------------------ a C4, M0 e M1 (so com a `memoria_autobio`)
    def relogio(self, minuto: int) -> int:
        """o tick da decisao pelo relogio do pet: o dia avanca quando a hora do dia volta (a docstring do modulo)"""
        if not self.autobio:
            raise RuntimeError("M-MEM: o relogio do episodio so com a memoria_autobio")
        if type(minuto) is not int or not 0 <= minuto < TICKS_POR_DIA:
            raise ValueError(f"M-MEM: a hora do dia {minuto!r}")
        if self.minuto is not None and minuto < self.minuto:
            self.dia += 1
        self.minuto = minuto
        return self.dia * TICKS_POR_DIA + minuto

    def codificar_autobio(self, ep: dict) -> int:
        """guarda o episodio completo (de `episodio_autobio`) na recente e devolve o id"""
        if not self.autobio:
            raise RuntimeError("M-MEM: o episodio completo so com a memoria_autobio")
        if ep["classe"] not in CLASSES_AUTOBIO or ep["origem"] not in ORIGENS_AUTOBIO:
            raise ValueError(f"M-MEM: episodio {ep!r}")
        if ep["origem"] == "visita" and (ep["sigma"] > 0 or ep["classe"] != "nao_havia"):
            raise ValueError("M-MEM: a visita sem comida tem sigma <= 0 e a classe nao_havia")
        if len(self.recente) >= self.p.n_rec:
            sai = min(self.recente, key=lambda e: (abs(e["sigma"]), e["decisao"], e["id"]))
            self.recente.remove(sai)
            self.saidas_autobio.append({"id": sai["id"], "sigma": sai["sigma"]})
        novo = {**ep, "id": self.proximo_id_autobio, "lugar": list(self.lugar_de(*ep["ponto"])), "ponto": list(ep["ponto"])}
        self.proximo_id_autobio += 1
        self.recente.append(novo)
        return novo["id"]

    def valores(self) -> dict:
        """lugar -> o episodio mais recente nele (a decisao, depois o id)"""
        out: dict = {}
        for e in self.episodios:
            lugar = tuple(e["lugar"])
            atual = out.get(lugar)
            if atual is None or (e["decisao"], e["id"]) > (atual["decisao"], atual["id"]):
                out[lugar] = e
        return out

    def recuperar(self, sens: dict, afeto: dict) -> dict:
        """a recuperacao da decisao: {"pista", "recuperado" (o id ou None), "lugar", "ponto", "valor", "M"}"""
        S, p = self.S, self.p
        pista = afeto["urgencias"].get("fome", 0) > p.lambda_busca and sens["conjuncoes"]["comida_vista"] == 0
        nada = {"pista": pista, "recuperado": None, "lugar": None, "ponto": None, "valor": 0, "M": 0}
        if not pista:
            return nada
        x, y = sens["pos"]
        melhor, chave_melhor = None, None
        for lugar, e in sorted(self.valores().items()):
            valor = e["r_n"]
            if valor <= 0:
                continue
            px, py = e["ponto"]
            dist = raiz_inteira((px - x) * (px - x) + (py - y) * (py - y))
            nota = mul(valor, S - min(S, div_arred(dist * S, p.d_max)), S)
            if nota <= 0:
                continue
            chave = (nota, e["decisao"], e["id"])
            if chave_melhor is None or chave > chave_melhor:
                melhor, chave_melhor = (lugar, e, nota), chave
        if melhor is None:
            return nada
        lugar, e, nota = melhor
        self.recuperacoes += 1
        return {"pista": True, "recuperado": e["id"], "lugar": list(lugar), "ponto": tuple(e["ponto"]), "valor": e["r_n"],
                "nota": nota, "M": mul(p.w_mem, e["r_n"], S)}

    # ------------------------------------------------------------ a interface da memoria consolidada (secao 9), vazia no prototipo
    def consolidar(self, decisao: int) -> None:
        return None

    def termos_decisao(self, recuperacao: dict | None) -> dict:
        """o termo M de cada unidade: no prototipo, so o do lugar recuperado"""
        if recuperacao is None or recuperacao["recuperado"] is None:
            return {}
        return {("explorar", "ponto", tuple(recuperacao["ponto"])): recuperacao["M"]}

    def evidencia_faceta(self, nome: str) -> list:
        return []

    def estado_interno(self) -> dict:
        out = {"episodios": [dict(e) for e in self.episodios], "proximo_id": self.proximo_id, "saidas": list(self.saidas),
               "recuperacoes": self.recuperacoes}
        if self.autobio:                              # a C4 (desligada, o estado e o de hoje, byte a byte)
            out["autobio"] = {"recente": [dict(e) for e in self.recente], "proximo_id": self.proximo_id_autobio,
                              "saidas": list(self.saidas_autobio), "relogio": {"dia": self.dia, "minuto": self.minuto}}
        return out
