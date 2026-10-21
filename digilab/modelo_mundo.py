"""Os modelos do mundo do pet que pensa (J5; docs/TAREFA_V2_PET_QUE_PENSA.md, secao 2.1, etapa 1; desenho docs/futuro/pet_que_pensa.md).

Na etapa 1 os modelos so observam: o embrulho `PoliticaComModelo` os deixa aprender com a vida sem muda-la (G-OBS-MM). Na etapa 2 o
cerebro A com `ConfigLobos.g_plano` > 0 guarda os proprios modelos e o lobo `planejamento` os le (`lugar_de`, `previsao`, `desfecho_de`,
`arvores_vistas`, `posicao`); o embrulho continua para os bracos sem o planejador.

**O que os modelos veem (sem acesso privilegiado).** So a percepcao do pet:
- os receptores do corpo (`Observacao.corpo`, a `PercepcaoCorpo`, na escala S), todos os que existirem, na ordem dos campos;
- o que o mundo mostra (`Observacao.mundo`, a `PercepcaoMundo`): a posicao do pet e os `vistos` (o tipo, e se esta podre);
- o tipo do que o proprio pet comeu (o `comeu` da consequencia: so `tipo` e `situacao`).
Ficam de fora: o quimico, o `Estado`, o registro do mundo, o `efeito_frutas` do motor, a fruta de cada arvore no layout, a distancia
que o motor registra e o resto da consequencia. Os troncos nao estao nos `vistos`: a posicao de uma arvore vem do layout, mas so entra
no mapa depois que o pet a viu (o tronco a ate o raio da visao do mundo, a mesma conta dos `vistos`), na decisao e de onde o pet parou
depois de andar, como o motor. Com o mundo do J5 ligado (#290), a percepcao traz os `troncos` a vista, e eles sao conferidos contra essa
conta (diverge, falha alto). O modulo so importa `config` e `events`.

**O modelo do desfecho**, por tipo de comida (`racao`, `a`, `b`, `c` e `podre`, a comida podre de qualquer tipo) e por receptor: a
mudanca esperada da leitura ao comer, d_tr. Em cada consumo do `comer` que o pet percebe, `d_tr += div_arred((obs_r - d_tr) x
passo_desfecho, S)`, com obs = os receptores logo depois de comer menos os da decisao. O prior e 0 (o pet nao sabe nada).
- A energia do `comer` inclui o andar ate a comida: o componente da energia e corrigido pelo andar previsto, `div_arred(a x d, S)`.
- O "achou e comeu" do explorar nao atualiza o desfecho: o efeito do proprio explorar no corpo nao e separavel do da comida. Ele fica
  contado em `consumos_nao_usados`.
- A fruta na mao (o gancho `fruta_na_mao` do mundo do J5): o mesmo passo, com os receptores de depois menos os de antes (sem andar),
  contada em `consumos_mao`.

**O custo de andar previsto** (um inteiro): a mudanca esperada da leitura da energia por subunidade andada, x S. Aprende nas decisoes
de `comer` com deslocamento d > 0 (comer nao mexe na energia; o andar sim), com a amostra `div_arred((energia depois - energia antes) x
S, d)` e o mesmo passo do desfecho. d e a distancia percebida, da posicao da decisao a de depois (a raiz inteira, como a do mundo).

**O mapa da comida**, por lugar (as arvores do layout, na ordem dele, e o comedouro) e por tipo: a frequencia do que o pet viu la, na
escala S. Em cada decisao, cada comida madura dos `vistos` conta para o lugar ja visto mais perto dela, a ate `raio_ancora_celulas`
(empate: o primeiro na ordem dos lugares), com `m_t += div_arred((1[t = tipo] x S - m_t) x passo_mapa, S)` nos cinco tipos. A podre nao
conta como vista (a coluna dela so esquece). O prior e 0: o pet nao sabe o que cai onde. A mesma comida conta de novo em cada decisao em
que aparece (a letra da tarefa: "cada vez que uma comida madura aparece nos vistos").

**O congelamento (PP-8):** `congelar("mapa")` (o P1-plan-desfecho) e `congelar("desfecho", "mapa")` (o P1-plan-cong): daqui em diante
a parte nao aprende (o desfecho com o custo de andar; o mapa com os lugares vistos), e o que deixou de aprender fica em `ignoradas`.

**Os numeros.** So inteiros, nenhuma funcao transcendental e nenhuma rng (G-INT). Os modelos somam menos de `teto_modelo` inteiros
(G-TETO-MODELO): com R receptores e L lugares, `5 x R + 1 + L x 5`. No regime quimica (R = 5, L = 10): 25 + 1 + 50 = 76.
"""

from __future__ import annotations

from dataclasses import fields

from .config import CONFIG_MODELO_MUNDO_LIGADA, ConfigModeloMundo, ConfigMundo
from .events import FRUTAS, AcaoPet

TIPOS = ("racao",) + FRUTAS + ("podre",)        # as colunas do desfecho e do mapa
TIPOS_MADUROS = ("racao",) + FRUTAS             # o que conta como visto no mapa
COMEDOURO = "comedouro"

# Status dos campos da ConfigModeloMundo (conferido por teste). Todos PROPOSTOS, sem fonte, nenhum referendado (PP-6).
PARAMETROS_MODELO_MUNDO: dict[str, tuple[str, str]] = {
    "ligada": ("DECIDIDO", "PQ-6: os modelos num modulo proprio; na etapa 1 so observam, por um embrulho somente leitura"),
    "escala": ("PROPOSTO", "S do cerebro A e dos receptores do corpo (TAREFA_V2_CORPO_DRIVES, secao 10)"),
    "passo_desfecho": ("PROPOSTO", "PP-6: S/4, sem fonte"),
    "passo_mapa": ("PROPOSTO", "PP-6: S/8, sem fonte"),
    "raio_ancora_celulas": ("PROPOSTO", "PP-6: 2 celulas, sem fonte"),
    "teto_modelo": ("PROPOSTO", "PP-6: 200 inteiros, sem fonte (no regime quimica a conta e 76)"),
}


def div_arred(n: int, d: int) -> int:
    """n / d em inteiros, arredondado ao mais proximo, meio longe do zero. d > 0. A mesma conta de corpo.div_arred e lobos.div_arred
    (conferido por teste); copiada para os modelos nao dependerem do corpo nem do cerebro."""
    if d <= 0:
        raise ValueError(f"divisor nao positivo: {d}")
    q, r = divmod(abs(n), d)
    if 2 * r >= d:
        q += 1
    return q if n >= 0 else -q


def raiz_inteira(n: int) -> int:
    """A raiz quadrada inteira (o piso), por Newton em inteiros: a mesma de math.isqrt (conferido por teste), sem importar `math`."""
    if type(n) is not int or n < 0:
        raise ValueError(f"raiz inteira de {n!r}")
    if n < 2:
        return n
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x


def dentro(dx: int, dy: int, raio: int) -> bool:
    """raiz_inteira(dx^2 + dy^2) <= raio, sem a raiz: a conta do `d <= raio` dos `vistos` do mundo."""
    return dx * dx + dy * dy < (raio + 1) * (raio + 1)


def lugares_do_layout(cm: ConfigMundo) -> tuple[tuple[str, int, int], ...]:
    """(nome, x, y) em subunidades, no centro da celula: as arvores na ordem do layout e o comedouro. A fruta de cada arvore no layout NAO
    entra (os modelos nao a leem)."""
    centro = lambda c: (c[0] * cm.sub + cm.sub // 2, c[1] * cm.sub + cm.sub // 2)  # noqa: E731
    lugares = [(ident,) + centro((x, y)) for ident, x, y, _fruta in cm.layout.arvores]
    lugares.append((COMEDOURO,) + centro(cm.layout.comedouro))
    return tuple(lugares)


def n_valores(R: int, L: int) -> int:
    """A contagem dos modelos com R receptores e L lugares (a docstring do modulo)."""
    return len(TIPOS) * R + 1 + L * len(TIPOS)


class ModeloMundo:
    """O modelo do desfecho, o custo de andar e o mapa da comida (docstring do modulo). `decisao(obs)` uma vez por decisao, na ordem da
    vida; `consequencia(acao, ocorrido, obs_depois)` quando o mundo a entrega (explorar, comer, brincar)."""

    def __init__(self, cfg: ConfigModeloMundo | None, cfg_mundo: ConfigMundo) -> None:
        self.cfg = cfg or CONFIG_MODELO_MUNDO_LIGADA
        if not self.cfg.ligada:
            raise ValueError("ModeloMundo com a ConfigModeloMundo desligada")
        if not cfg_mundo.ligada:
            raise ValueError("ModeloMundo sem o mundo fisico (ConfigMundo desligada): o mapa e das arvores do mundo")
        self.S = self.cfg.escala
        self.lugares = lugares_do_layout(cfg_mundo)
        self.raio_visao = cfg_mundo.raio_visao_celulas * cfg_mundo.sub
        self.raio_ancora = self.cfg.raio_ancora_celulas * cfg_mundo.sub
        self.receptores: tuple | None = None          # o layout dos receptores, fixado na primeira decisao
        self.desfecho: dict | None = None             # tipo -> [d_r por receptor]
        self.andar = 0                                # a mudanca da energia por subunidade andada, x S
        self.mapa: dict = {nome: [0] * len(TIPOS) for nome, _x, _y in self.lugares}
        self.lugares_vistos: dict = {}                # nome -> a decisao (k) em que o pet viu o lugar pela primeira vez
        self.k = 0                                    # as decisoes ja vividas (o relogio do pet)
        self._decisao = None                          # (k, leituras, x, y) da decisao em curso
        self.consumos = {t: 0 for t in TIPOS}         # os consumos do `comer` que atualizaram o desfecho
        self.consumos_nao_usados = {t: 0 for t in TIPOS}   # os "achou e comeu" do explorar (nao atualizam o desfecho)
        self.amostras_andar = 0
        self.vistas_ancoradas = 0                     # as comidas vistas que contaram para um lugar
        self.vistas_soltas = 0                        # as comidas vistas longe de todo lugar ja visto
        self.consumos_mao = {t: 0 for t in TIPOS}     # a fruta na mao (etapa 3, do A), um consumo do desfecho como o do comer
        self.congelados: tuple = ()                   # PP-8: as partes congeladas ("desfecho", com o andar; "mapa", com os lugares)
        self.ignoradas = {"desfecho": 0, "mapa": 0}   # as atualizacoes que o congelamento deixou de fazer

    # ---------------------------------------------------------- o layout e as leituras
    def _montar(self, pc) -> None:
        self.receptores = tuple(f.name for f in fields(pc) if getattr(pc, f.name) is not None)
        total = n_valores(len(self.receptores), len(self.lugares))
        if total >= self.cfg.teto_modelo:
            raise ValueError(f"modelos do mundo com {len(self.receptores)} receptores e {len(self.lugares)} lugares: {total} inteiros, "
                             f"teto {self.cfg.teto_modelo} (G-TETO-MODELO)")
        self.desfecho = {t: [0] * len(self.receptores) for t in TIPOS}

    def leituras(self, pc) -> list[int]:
        """Os receptores do layout, inteiros em [0, S]; um receptor a mais ou a menos que no layout falha alto."""
        presentes = tuple(f.name for f in fields(pc) if getattr(pc, f.name) is not None)
        if presentes != self.receptores:
            raise ValueError(f"modelos do mundo: receptores {presentes}, layout {self.receptores}")
        ls = [getattr(pc, r) for r in self.receptores]
        for r, v in zip(self.receptores, ls):
            if type(v) is not int or not 0 <= v <= self.S:
                raise ValueError(f"modelos do mundo: receptor {r!r} fora de inteiros em [0, {self.S}]: {v!r}")
        return ls

    @staticmethod
    def _percepcoes(obs) -> tuple:
        pc, pm = getattr(obs, "corpo", None), getattr(obs, "mundo", None)
        if pc is None:
            raise RuntimeError("modelos do mundo: Observacao sem o corpo (os modelos leem os receptores; precisa do MotorCorpo)")
        if pm is None:
            raise RuntimeError("modelos do mundo: Observacao sem o mundo (o mapa le os vistos; precisa do MotorMundo ligado)")
        return pc, pm

    def _passo(self, valor: int, alvo: int, passo: int) -> int:
        return valor + div_arred((alvo - valor) * passo, self.S)

    def _ver_lugares(self, pm, k: int) -> None:
        """Os lugares a ate o raio da visao de onde o pet esta (a conta dos `vistos`). Com o mundo do J5 ligado, a percepcao traz os
        `troncos` a vista (#290): eles tem de ser exatamente as arvores que esta conta ve, na mesma posicao (diverge, falha alto). Sem
        eles (o mundo sem a chave do J5), so a conta. O mapa congelado nao aprende lugar novo (PP-8)."""
        x, y = pm.x, pm.y
        troncos = getattr(pm, "troncos", ())
        if getattr(pm, "orientacao", None) is not None:
            # a P4 (P4-2): a percepcao veio dos sensores do contrato (o cone e a oclusao). As arvores vistas sao os troncos dela; o
            # comedouro, que nao e objeto da percepcao, fica com a conta do raio (o acesso privilegiado da posicao, W-3)
            arvores = {nome: (lx, ly) for nome, lx, ly in self.lugares if nome != COMEDOURO}
            vistas = set()
            for ident, dx, dy, _d in troncos:
                if ident not in arvores or arvores[ident] != (x + dx, y + dy):
                    raise RuntimeError(f"modelos do mundo: tronco {ident!r} em ({x + dx}, {y + dy}) fora do layout dos modelos")
                vistas.add(ident)
            for nome, lx, ly in self.lugares:
                ve = nome in vistas if nome != COMEDOURO else dentro(lx - x, ly - y, self.raio_visao)
                if nome not in self.lugares_vistos and ve:
                    if "mapa" in self.congelados:
                        self.ignoradas["mapa"] += 1
                    else:
                        self.lugares_vistos[nome] = k
            return
        if troncos:
            arvores = {nome: (lx, ly) for nome, lx, ly in self.lugares if nome != COMEDOURO}
            por_conta = {nome for nome, (lx, ly) in arvores.items() if dentro(lx - x, ly - y, self.raio_visao)}
            na_percepcao = set()
            for ident, dx, dy, _d in troncos:
                if ident not in arvores or arvores[ident] != (x + dx, y + dy):
                    raise RuntimeError(f"modelos do mundo: tronco {ident!r} em ({x + dx}, {y + dy}) fora do layout dos modelos")
                na_percepcao.add(ident)
            if na_percepcao != por_conta:
                raise RuntimeError(f"modelos do mundo: troncos a vista {sorted(na_percepcao)} e a conta do raio {sorted(por_conta)}")
        for nome, lx, ly in self.lugares:
            if nome not in self.lugares_vistos and dentro(lx - x, ly - y, self.raio_visao):
                if "mapa" in self.congelados:
                    self.ignoradas["mapa"] += 1
                else:
                    self.lugares_vistos[nome] = k

    def congelar(self, *partes: str) -> None:
        """PP-8: daqui em diante a parte nao aprende mais (o desfecho com o custo de andar; o mapa com os lugares vistos). As
        atualizacoes que deixam de acontecer ficam contadas em `ignoradas`."""
        for parte in partes:
            if parte not in ("desfecho", "mapa"):
                raise ValueError(f"modelos do mundo: parte {parte!r}; so 'desfecho' e 'mapa'")
        self.congelados = tuple(sorted(set(self.congelados) | set(partes)))

    # ---------------------------------------------------------- a decisao: o mapa
    def decisao(self, obs) -> None:
        """Uma decisao: os lugares que o pet passa a ver e as comidas maduras vistas, cada uma no lugar ja visto mais perto dela."""
        pc, pm = self._percepcoes(obs)
        if self.receptores is None:
            self._montar(pc)
        ls = self.leituras(pc)
        x, y = pm.x, pm.y
        self._ver_lugares(pm, self.k)
        for _ident, tipo, dx, dy, _d in pm.vistos:
            if tipo not in TIPOS_MADUROS:
                continue
            px, py = x + dx, y + dy
            melhor, d2_melhor = None, None
            for nome, lx, ly in self.lugares:
                if nome not in self.lugares_vistos or not dentro(lx - px, ly - py, self.raio_ancora):
                    continue
                d2 = (lx - px) * (lx - px) + (ly - py) * (ly - py)
                if d2_melhor is None or d2 < d2_melhor:
                    melhor, d2_melhor = nome, d2
            if melhor is None:
                self.vistas_soltas += 1
                continue
            if "mapa" in self.congelados:
                self.ignoradas["mapa"] += 1
                continue
            m = self.mapa[melhor]
            for i, t in enumerate(TIPOS):
                m[i] = self._passo(m[i], self.S if t == tipo else 0, self.cfg.passo_mapa)
            self.vistas_ancoradas += 1
        self._decisao = (self.k, ls, x, y)
        self.k += 1

    # ---------------------------------------------------------- a consequencia: o desfecho e o andar
    def consequencia(self, acao: AcaoPet, ocorrido: dict, obs_depois) -> None:
        """A consequencia de explorar, comer ou brincar (o gancho `consequencia_mundo`), da decisao em curso. Do `ocorrido` so o `comeu`
        (tipo e situacao: o que o pet comeu); a distancia e a do proprio pet, pela posicao percebida."""
        if self._decisao is None or self._decisao[0] != self.k - 1:
            raise RuntimeError("modelos do mundo: consequencia sem a decisao dela (a ordem decisao -> consequencia quebrou)")
        pc, pm = self._percepcoes(obs_depois)
        k, l0, x0, y0 = self._decisao
        l1 = self.leituras(pc)
        self._ver_lugares(pm, k)                          # o que se ve de onde o pet parou (o motor ve os troncos ai tambem)
        comeu = ocorrido.get("comeu")
        tipo = None
        if comeu is not None:
            if comeu["situacao"] == "podre":
                tipo = "podre"
            elif comeu["situacao"] == "madura" and comeu["tipo"] in TIPOS_MADUROS:
                tipo = comeu["tipo"]
            else:
                raise ValueError(f"modelos do mundo: comida desconhecida {comeu['tipo']!r}, {comeu['situacao']!r}")
        if acao is not AcaoPet.COMER:
            if tipo is not None:
                self.consumos_nao_usados[tipo] += 1
            return
        d = raiz_inteira((pm.x - x0) * (pm.x - x0) + (pm.y - y0) * (pm.y - y0))
        ie = self.receptores.index("energia") if "energia" in self.receptores else None
        if d > 0 and ie is not None:
            if "desfecho" in self.congelados:
                self.ignoradas["desfecho"] += 1
            else:
                amostra = div_arred((l1[ie] - l0[ie]) * self.S, d)
                self.andar = self._passo(self.andar, amostra, self.cfg.passo_desfecho)
                self.amostras_andar += 1
        if tipo is not None:
            delta = [b - a for a, b in zip(l0, l1)]
            if ie is not None:
                delta[ie] -= div_arred(self.andar * d, self.S)
            self.consumo(tipo, delta)

    def consumo(self, tipo: str, delta: list[int]) -> None:
        """Um consumo percebido (o do `comer`; a fruta na mao da etapa 3 entra por aqui): o desfecho do tipo anda em direcao a `delta`."""
        if tipo not in TIPOS:
            raise ValueError(f"modelos do mundo: tipo {tipo!r}")
        if len(delta) != len(self.receptores) or any(type(v) is not int for v in delta):
            raise ValueError(f"modelos do mundo: delta {delta!r} fora do layout {self.receptores}")
        if "desfecho" in self.congelados:
            self.ignoradas["desfecho"] += 1
            return
        dt = self.desfecho[tipo]
        for i, v in enumerate(delta):
            dt[i] = self._passo(dt[i], v, self.cfg.passo_desfecho)
        self.consumos[tipo] += 1

    def na_mao(self, tipo: str, obs_antes, obs_depois) -> None:
        """A fruta na mao (o gancho `fruta_na_mao` do mundo do J5): o pet come onde esta, sem decisao e sem andar. O desfecho anda em
        direcao aos receptores de depois menos os de antes, inteiros (nada de energia a corrigir). Nao e uma decisao: o relogio dos
        modelos (k) e a decisao em curso nao mudam."""
        if tipo not in TIPOS_MADUROS:
            raise ValueError(f"modelos do mundo: fruta na mao {tipo!r}")
        pc0, _ = self._percepcoes(obs_antes)
        pc1, _ = self._percepcoes(obs_depois)
        if self.receptores is None:
            self._montar(pc0)
        l0, l1 = self.leituras(pc0), self.leituras(pc1)
        congelado = "desfecho" in self.congelados
        self.consumo(tipo, [b - a for a, b in zip(l0, l1)])
        if not congelado:
            self.consumos[tipo] -= 1                      # o consumo do comer e o da mao contam em separado
            self.consumos_mao[tipo] += 1

    # ---------------------------------------------------------- as consultas do planejador (etapa 2)
    def lugar_de(self, x: int, y: int) -> str | None:
        """O lugar ja visto mais perto de (x, y), a ate `raio_ancora_celulas` (empate: o primeiro na ordem dos lugares), ou None: a
        mesma ancora das comidas vistas."""
        melhor, d2_melhor = None, None
        for nome, lx, ly in self.lugares:
            if nome not in self.lugares_vistos or not dentro(lx - x, ly - y, self.raio_ancora):
                continue
            d2 = (lx - x) * (lx - x) + (ly - y) * (ly - y)
            if d2_melhor is None or d2 < d2_melhor:
                melhor, d2_melhor = nome, d2
        return melhor

    def posicao(self, lugar: str) -> tuple[int, int]:
        for nome, lx, ly in self.lugares:
            if nome == lugar:
                return lx, ly
        raise KeyError(f"modelos do mundo: lugar {lugar!r}")

    def arvores_vistas(self) -> list[str]:
        """as arvores ja vistas, na ordem do layout (o comedouro fora)"""
        return [nome for nome, _x, _y in self.lugares if nome != COMEDOURO and nome in self.lugares_vistos]

    def previsao(self, lugar: str | None) -> dict[str, int]:
        """p(tipo | lugar) na escala S: a linha do mapa, sem normalizar (um lugar pouco visto preve pouco). Sem lugar, nada."""
        if lugar is None:
            return {}
        return {t: m for t, m in zip(TIPOS, self.mapa[lugar]) if m != 0}

    def desfecho_de(self, tipo: str) -> dict[str, int]:
        """o desfecho previsto do tipo, por receptor"""
        return dict(zip(self.receptores, self.desfecho[tipo]))

    # ---------------------------------------------------------- leituras
    def n_valores(self) -> int:
        if self.receptores is None:
            raise RuntimeError("modelos do mundo sem layout: nenhuma decisao ainda")
        return sum(len(v) for v in self.desfecho.values()) + 1 + sum(len(v) for v in self.mapa.values())

    def para_dict(self) -> dict:
        """Tudo o que os modelos guardam (o replay o refaz bit a bit, G1)."""
        return {"receptores": None if self.receptores is None else list(self.receptores), "k": self.k,
                "desfecho": self.desfecho, "andar": self.andar, "mapa": self.mapa, "lugares_vistos": self.lugares_vistos,
                "decisao": None if self._decisao is None else list(self._decisao[:1]) + [list(self._decisao[1])]
                + list(self._decisao[2:]),
                "consumos": self.consumos, "consumos_nao_usados": self.consumos_nao_usados, "amostras_andar": self.amostras_andar,
                "vistas_ancoradas": self.vistas_ancoradas, "vistas_soltas": self.vistas_soltas, "consumos_mao": self.consumos_mao,
                "congelados": list(self.congelados), "ignoradas": self.ignoradas}


class PoliticaComModelo:
    """O embrulho somente leitura (etapa 1): entrega aos modelos a observacao de cada decisao (antes do cerebro escolher; os modelos nao
    tocam na rng) e a consequencia do mundo, e repassa ao cerebro todo o resto por `__getattr__`. O `consequencia_mundo` existe sempre
    (os modelos precisam dele) e so chega ao cerebro se ele o tem; o estado interno e o do cerebro (os modelos ficam em `modelo`)."""

    def __init__(self, interna, cfg_mundo: ConfigMundo, cfg: ConfigModeloMundo | None = None) -> None:
        self._interna = interna
        self.modelo = ModeloMundo(cfg or CONFIG_MODELO_MUNDO_LIGADA, cfg_mundo)

    def agir(self, obs, rng):
        self.modelo.decisao(obs)
        return self._interna.agir(obs, rng)

    def consequencia_mundo(self, acao, ocorrido: dict, obs_depois) -> None:
        self.modelo.consequencia(acao, ocorrido, obs_depois)
        gancho = getattr(self._interna, "consequencia_mundo", None)
        if gancho is not None:
            gancho(acao, ocorrido, obs_depois)

    def fruta_na_mao(self, tipo: str, obs_antes, obs_depois) -> None:
        """a fruta na mao (o mundo do J5): o desfecho aprende; o cerebro so a recebe se tem o gancho (a G-SEM-CREDITO e dele)"""
        self.modelo.na_mao(tipo, obs_antes, obs_depois)
        gancho = getattr(self._interna, "fruta_na_mao", None)
        if gancho is not None:
            gancho(tipo, obs_antes, obs_depois)

    def estado_interno(self) -> dict:
        return self._interna.estado_interno()

    def __getattr__(self, nome: str):
        interna = self.__dict__.get("_interna")
        if interna is None:
            raise AttributeError(nome)
        return getattr(interna, nome)
