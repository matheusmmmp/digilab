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
    ou a maior subida de dor, susto ou estresse na decisao (corpo_depois - corpo_antes, so os aumentos) >= `theta_sig` (a origem
    "evento"). O resto nao vira episodio. O afeto e lido pela variacao, nao pelo nivel (o Matheus, 2026-11-01, no #530): o `theta_afeto`
    saiu do codigo;
  - **a categoria** (3.4): [comportamento, classe, sinal de sigma], com a classe a comida no consumo, "nao_havia" na visita e, no
    evento, a classe do objeto da unidade ou "sem_alvo";
  - **onde fica:** na `recente`, uma lista propria, com capacidade `n_rec`; cheia, sai o de menor |sigma| (o peso da 4.3 com rep = rec =
    0), no empate o mais antigo (a decisao, depois o id). **Nenhuma decisao le a recente nas M0 e M1** (a M4 e etapa posterior): o lugar
    lembrado segue a lista de hoje (`episodios`), e a vida com a subchave sai com o mesmo log da vida sem ela;
  - **o tick** (a referencia ao log): o relogio do pet refeito da hora do dia da Observacao (`relogio`): o dia avanca quando a hora volta,
    tick = dia x TICKS_POR_DIA + a hora em ticks.

**A C4, M2 e M3** (secoes 4 e 8 da mesma espec; mesma subchave):
  - **a lembranca** (M2, `lembrar`, ME-2): a cada decisao, o episodio das tres memorias de maior semelhanca com a pista, ou nenhum. A pista:
    a posicao de agora, as classes a vista, o cheiro, a noite e as faixas (quartos de S) dos receptores. `sim` = a media inteira,
    ponderada por `w_lugar`, `w_vista` e `w_corpo`, de `s_lugar` (a nota pela distancia ao ponto do episodio, a conta de hoje), `s_vista`
    (Jaccard sobre as classes, o cheiro e a noite; S se as duas sao vazias) e `s_corpo` (os receptores na mesma faixa). Volta o de maior
    `sim >= sim_min`; o empate: o maior |sigma|, depois o mais recente (a decisao, depois o id). Cada lembranca soma 1 em `rec`. A faixa
    do episodio e a da leitura guardada em `corpo_antes` (o episodio nao guarda a urgencia), e a da pista e a da leitura da Observacao.
    Nenhuma decisao le a lembranca ainda (a M4 e etapa posterior);
  - **o lugar pela soma** (MA-2): com a subchave, o valor do lugar P e a soma, cortada em [-S, S], do sigma dos episodios de consumo de
    comida boa (racao, a, b, c) e de visita em P, nas tres memorias, no lugar do "mais recente manda"; o ponto e o do mais recente;
  - **a consolidacao** (M3, `consolidar`): recente -> duradoura -> central, uma vez por dia do pet, na primeira decisao do dia novo; os
    passos e o registro estao em `consolidar`. A repeticao (`rep`) soma ao codificar um episodio de mesma categoria e mesmo lugar; o peso e
    `min(S, mul(|sigma|, S + rep x S/2 + rec x S/4))`.
Desligada, nada disso existe (o estado interno e o de hoje). Sem rng."""
from __future__ import annotations

from ..config import CONFIG_DIGIBRAIN_INATOS, TICKS_POR_DIA, TIPOS_ALVO_DIGIBRAIN, ConfigDigibrainInatos, ConfigMundo
from ..modelo_mundo import raiz_inteira
from ..policies.lobos import div_arred
from ._comum import chave_json, mul

COMIDAS_BOAS = ("racao", "a", "b", "c")             # as classes de comida boa (igual a `sens.COMIDAS_BOAS`; o mem.py nao importa o M-SENS)

CLASSES_EPISODIO = ("racao", "a", "b", "c", "podre", "nao_havia")
ORIGENS = ("consumo", "visita")
# a C4 (secao 3.4): as classes e as origens do episodio completo
CLASSES_AUTOBIO = CLASSES_EPISODIO + ("bola", "sem_alvo")
ORIGENS_AUTOBIO = ("consumo", "visita", "evento")
AFETIVOS = ("dor", "susto", "estresse")             # os receptores cuja subida conta para o `theta_sig` (3.3)


def _faixa(v: int, S: int) -> int:
    """a faixa em quartos de S: quantos limites (S/4, S/2, 3S/4) o valor alcanca"""
    return (v >= S // 4) + (v >= S // 2) + (v >= 3 * S // 4)


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
        subida = max((corpo_depois[r] - corpo_antes[r] for r in AFETIVOS if r in corpo_depois), default=0)   # a queda nao conta
        if abs(cons["r_n"]) < p.theta_sig and subida < p.theta_sig:
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
            self.duradoura: list[dict] = []
            self.central: list[dict] = []
            self.consolidacoes: list[dict] = []       # o registro de cada consolidacao (4.3)
            self.dia_consolidado = 0
            self.lembrancas = 0
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
        lugar = list(self.lugar_de(*ep["ponto"]))
        for e in self._guardados():                   # a repeticao: a mesma categoria no mesmo lugar (4.3)
            if e["categoria"] == ep["categoria"] and e["lugar"] == lugar:
                e["rep"] += 1
        if len(self.recente) >= self.p.n_rec:
            sai = min(self.recente, key=lambda e: (self.peso(e), e["decisao"], e["id"]))
            self.recente.remove(sai)
            self.saidas_autobio.append({"id": sai["id"], "sigma": sai["sigma"]})
        novo = {**ep, "id": self.proximo_id_autobio, "lugar": lugar, "ponto": list(ep["ponto"])}
        self.proximo_id_autobio += 1
        self.recente.append(novo)
        return novo["id"]

    # ------------------------------------------------------------ a C4, M2 e M3 (so com a `memoria_autobio`)
    def _guardados(self) -> list[dict]:
        """os episodios das tres memorias, na ordem recente, duradoura, central"""
        return self.recente + self.duradoura + self.central

    def peso(self, e: dict) -> int:
        """o peso afetivo do episodio (4.3): min(S, mul(|sigma|, S + rep x S/2 + rec x S/4))"""
        S = self.S
        return min(S, mul(abs(e["sigma"]), S + div_arred(e["rep"] * S, 2) + div_arred(e["rec"] * S, 4), S))

    def lembrar(self, sens: dict) -> dict:
        """a lembranca da decisao (M2, 4.1): {"recuperado" (o id ou None), "sim" (a maior, ou 0 sem episodio), "memoria", "sigma"}; soma 1
        em `rec` do lembrado"""
        if not self.autobio:
            raise RuntimeError("M-MEM: a lembranca so com a memoria_autobio")
        S, p = self.S, self.p
        x, y = sens["pos"]
        vista = {o["classe"] for o in sens["objetos"]}
        if sens["ha_cheiro"]:
            vista.add("cheiro")
        if sens["contexto"]["noite"] > 0:
            vista.add("noite")
        faixas = {r: _faixa(v, S) for r, v in sens["leitura"].items()}
        peso_total = p.w_lugar + p.w_vista + p.w_corpo
        melhor, chave_melhor = None, None
        for e in self._guardados():
            px, py = e["ponto"]
            dist = raiz_inteira((px - x) * (px - x) + (py - y) * (py - y))
            s_lugar = S - min(S, div_arred(dist * S, p.d_max))
            b = set(e["vista"]) | ({"cheiro"} if e["cheiro"] else set()) | ({"noite"} if e["noite"] else set())
            s_vista = S if not vista and not b else div_arred(len(vista & b) * S, len(vista | b))
            iguais = sum(1 for r, f in faixas.items() if r in e["corpo_antes"] and _faixa(e["corpo_antes"][r], S) == f)
            s_corpo = div_arred(iguais * S, len(faixas)) if faixas else S
            sim = div_arred(p.w_lugar * s_lugar + p.w_vista * s_vista + p.w_corpo * s_corpo, peso_total)
            chave = (sim, abs(e["sigma"]), e["decisao"], e["id"])
            if chave_melhor is None or chave > chave_melhor:
                melhor, chave_melhor = e, chave
        if melhor is None:
            return {"recuperado": None, "sim": 0, "memoria": None, "sigma": 0}
        sim = chave_melhor[0]
        if sim < p.sim_min:
            return {"recuperado": None, "sim": sim, "memoria": None, "sigma": 0}
        melhor["rec"] += 1
        self.lembrancas += 1
        return {"recuperado": melhor["id"], "sim": sim, "memoria": melhor["memoria"], "sigma": melhor["sigma"]}

    def termo_lembranca(self, lembranca: dict) -> dict | None:
        """o termo da lembranca (M4, 6.1): L = mul(w_lem, sigma) do episodio lembrado e a quem ele se aplica, ou None sem lembranca. Sem rng
        e sem mudar o estado (nao soma `rec`: quem somou foi o `lembrar`)"""
        if not self.autobio:
            raise RuntimeError("M-MEM: o termo da lembranca so com a memoria_autobio")
        if lembranca["recuperado"] is None:
            return None
        e = next(e for e in self._guardados() if e["id"] == lembranca["recuperado"])
        acao, tipo, _ = e["acao"]
        alvo = e["objeto"]["classe"] if e["objeto"] is not None else tipo       # a classe de alvo do episodio
        return {"id": e["id"], "L": mul(self.p.w_lem, e["sigma"], self.S), "acao": acao, "alvo": alvo, "lugar": tuple(e["lugar"]),
                "so_comportamento": e["classe"] == "sem_alvo"}

    def casa(self, termo: dict, unidade: dict) -> bool:
        """se a unidade da lista de agora tem a mesma acao do episodio lembrado (6.1): o mesmo comportamento e a mesma classe de alvo (para
        `ponto`, o mesmo lugar; para `sem_alvo`, o comportamento)"""
        if unidade["acao"] != termo["acao"]:
            return False
        if termo["so_comportamento"]:
            return True
        if unidade["tipo"] != termo["alvo"]:
            return False
        return unidade["tipo"] != "ponto" or self.lugar_de(*unidade["chave"][2]) == termo["lugar"]

    def valores_soma(self) -> dict:
        """lugar -> (a soma dos sigma, cortada em [-S, S], o episodio mais recente que a compoe): so consumo de comida boa e visita (MA-2)"""
        soma: dict = {}
        for e in self._guardados():
            if e["origem"] == "visita" or (e["origem"] == "consumo" and e["classe"] in COMIDAS_BOAS):
                lugar = tuple(e["lugar"])
                total, rep = soma.get(lugar, (0, None))
                if rep is None or (e["decisao"], e["id"]) > (rep["decisao"], rep["id"]):
                    rep = e
                soma[lugar] = (total + e["sigma"], rep)
        return {lugar: (max(-self.S, min(self.S, t)), e) for lugar, (t, e) in soma.items()}

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
        if self.autobio:                              # a C4 (MA-2): o valor do lugar e a soma dos sigma, nas tres memorias
            valores = self.valores_soma()
        else:
            valores = {lugar: (e["r_n"], e) for lugar, e in self.valores().items()}
        for lugar, (valor, e) in sorted(valores.items()):
            if valor <= 0:
                continue
            px, py = e["ponto"]
            dist = raiz_inteira((px - x) * (px - x) + (py - y) * (py - y))
            nota = mul(valor, S - min(S, div_arred(dist * S, p.d_max)), S)
            if nota <= 0:
                continue
            chave = (nota, e["decisao"], e["id"])
            if chave_melhor is None or chave > chave_melhor:
                melhor, chave_melhor = (lugar, e, nota, valor), chave
        if melhor is None:
            return nada
        lugar, e, nota, valor = melhor
        self.recuperacoes += 1
        return {"pista": True, "recuperado": e["id"], "lugar": list(lugar), "ponto": tuple(e["ponto"]), "valor": valor,
                "nota": nota, "M": mul(p.w_mem, valor, S)}

    # ------------------------------------------------------------ a interface da memoria consolidada (secao 9), vazia no prototipo
    def consolidar(self, decisao: int) -> dict | None:
        """a consolidacao diaria (M3, 4.3): so com a `memoria_autobio`, uma vez por dia do pet, na primeira decisao depois da virada do
        dia (o dia vem do `relogio`); devolve o registro (tambem guardado em `consolidacoes`) ou None. Sem rng. Ordem:
          1. recente -> duradoura: o episodio com mais de `janela_rec` decisoes sobe se rep >= 1, |sigma| >= `theta_dur` ou rec >= 1;
             senao e esquecido (sai, motivo `esquecido`);
          2. duradoura -> central: em cada categoria, o candidato e o de maior peso com rep >= `n_rep_central`; a central fica com um
             por categoria (o de maior peso entre o que ja estava e o candidato, no empate o mais antigo), as `n_cen` categorias de
             maior peso; quem sai da central volta a duradoura;
          3. a duradoura cheia descarta o de menor peso, no empate o mais antigo, ate caber em `n_dur`."""
        if not self.autobio or self.dia <= self.dia_consolidado:
            return None
        p = self.p
        self.dia_consolidado = self.dia
        reg = {"dia": self.dia, "decisao": decisao, "subiram": {"duradoura": [], "central": []}, "esquecidos": [], "voltaram": [],
               "por_capacidade": {"duradoura": []}}
        for e in sorted(self.recente, key=lambda e: (e["decisao"], e["id"])):
            if decisao - e["decisao"] <= p.janela_rec:
                continue
            self.recente.remove(e)
            if e["rep"] >= 1 or abs(e["sigma"]) >= p.theta_dur or e["rec"] >= 1:
                e["memoria"] = "duradoura"
                self.duradoura.append(e)
                reg["subiram"]["duradoura"].append(e["id"])
            else:
                reg["esquecidos"].append(e["id"])
        melhores: dict = {}                           # categoria -> o de maior peso entre a central e os candidatos
        for e in self.central + [e for e in self.duradoura if e["rep"] >= p.n_rep_central]:
            c = tuple(e["categoria"])
            chave = (self.peso(e), -e["decisao"], -e["id"])
            if c not in melhores or chave > melhores[c][0]:
                melhores[c] = (chave, e)
        nova = [e for _, e in sorted(melhores.values(), key=lambda t: t[0], reverse=True)[:p.n_cen]]
        ids_nova = {e["id"] for e in nova}
        for e in list(self.central):
            if e["id"] not in ids_nova:
                self.central.remove(e)
                e["memoria"] = "duradoura"
                self.duradoura.append(e)
                reg["voltaram"].append(e["id"])
        for e in nova:
            if e["memoria"] != "central":
                self.duradoura.remove(e)
                e["memoria"] = "central"
                self.central.append(e)
                reg["subiram"]["central"].append(e["id"])
        while len(self.duradoura) > p.n_dur:
            sai = min(self.duradoura, key=lambda e: (self.peso(e), e["decisao"], e["id"]))
            self.duradoura.remove(sai)
            reg["por_capacidade"]["duradoura"].append(sai["id"])
        self.consolidacoes.append(reg)
        return reg

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
                              "saidas": list(self.saidas_autobio), "relogio": {"dia": self.dia, "minuto": self.minuto},
                              "duradoura": [dict(e) for e in self.duradoura], "central": [dict(e) for e in self.central],
                              "consolidacoes": [dict(c) for c in self.consolidacoes], "lembrancas": self.lembrancas,
                              "dia_consolidado": self.dia_consolidado}
        return out
