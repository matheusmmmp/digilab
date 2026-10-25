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
`termos_decisao` e `evidencia_faceta` (vazio no prototipo)."""
from __future__ import annotations

from ..config import CONFIG_DIGIBRAIN_INATOS, ConfigDigibrainInatos, ConfigMundo
from ..modelo_mundo import raiz_inteira
from ..policies.lobos import div_arred
from ._comum import mul

CLASSES_EPISODIO = ("racao", "a", "b", "c", "podre", "nao_havia")
ORIGENS = ("consumo", "visita")


class Memoria:
    """o M-MEM (docstring do modulo)"""

    def __init__(self, cfg_mundo: ConfigMundo, inatos: ConfigDigibrainInatos | None = None) -> None:
        self.p = inatos or CONFIG_DIGIBRAIN_INATOS
        self.S = self.p.escala
        self.sub = cfg_mundo.sub
        self.episodios: list[dict] = []
        self.proximo_id = 0
        self.saidas: list[dict] = []          # os episodios que sairam por capacidade (id, |r|): o registro da PE-16
        self.recuperacoes = 0

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
        return {"episodios": [dict(e) for e in self.episodios], "proximo_id": self.proximo_id, "saidas": list(self.saidas),
                "recuperacoes": self.recuperacoes}
