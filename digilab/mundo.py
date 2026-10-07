"""O mundo fisico minimo (V2; docs/TAREFA_V2_MUNDO_FISICO.md, etapa 2; MF-1 a MF-4 decididas em 2026-10-07).

Estende o MotorFrutas (digilab/frutas.py, que nao muda) por subclasse, como as frutas (N4) e a bola (A1) entraram; engine.py e
ambiente.py tambem nao mudam. Desligado (ConfigMundo.ligada False, o padrao): nenhuma rng nova, nenhum registro novo, nenhuma chave
nova em estado(), nem o embrulho da politica: o MotorFrutas byte a byte. Ligado, o mundo SUBSTITUI o cenario do N4 e da A1: frutas,
racao e bola sao objetos com posicao (ConfigFrutas.ligada e ConfigBola.ligada junto com o mundo levantam erro), e os gestos de hoje
(`alimentar`, `oferecer_fruta_<f>`, `por_bola`, `tirar_bola`) levantam erro: o gesto e o `deixar_*`.

O mapa (secao 3): 64 x 30 celulas de 16 subunidades; posicoes inteiras em subunidades (0 <= x < 1024, 0 <= y < 480), distancia
`isqrt(dx^2 + dy^2)`. Regioes por faixa de x (casa, jardim, campo, mata; ConfigMundo.layout); o pet nasce no ninho. Direcoes por uma
tabela inteira de 16 (DIR16, escala 1024; indice 0 = leste, crescendo no sentido anti-horario, com o norte em y menor).

O dono (secao 4): `deixar_comida(tipo, x, y)` (racao ou fruta) conta como contato, como o `alimentar` de hoje (zera o tempo sem
cuidado, soma um cuidado, gasta orcamento; o embrulho e o vinculo recebem `alimentar`); a fome so sobe quando o pet come.
`deixar_bola(x, y)` segue o `por_bola`: gasta orcamento e nao e contato. Os dois sao tipos novos do log (events.deixar_comida,
events.deixar_bola); so o `reproduzir_mundo` os entende. `DonoComLugar` troca o `alimentar` do dono sintetico pelo `deixar_comida`
no lugar do estilo (comedouro, perto, longe), com a rng propria `dono-lugar` (sem o braco: numeros comuns). `CanalMundo` impoe o
orcamento com os gestos; `simular_vida_mundo` e o `simular_vida` com ele.

O pet (secao 5): o cerebro escolhe a acao; nas decisoes de explorar, comer e brincar o motor monta os candidatos a alvo, sorteia um
`u` em [0, 2^16) da rng `alvo` (sempre nessas tres acoes: numeros comuns) e pergunta ao gancho opcional `escolher_alvo(acao,
candidatos, percepcao, u)` (None = o padrao do motor). O motor anda de uma vez, na decisao: alcance = velocidade x intervalo; energia
- custo x deslocamento, alem do efeito de sempre da acao. Ao chegar (raio de pegar 1 celula): comer come a comida do alvo; explorar
come a comida boa mais proxima no raio, com a fome abaixo de `fome_max_comer_achado` (MF-1); brincar com a bola sobe o humor e a bola
rola. Comer sem comida no alcance nao da fome: o mundo desfaz o +0,05 do `efeito_da_acao_do_pet` antes de qualquer cerebro observar
(MF-2). O alvo que ficou sem chegar vira o candidato `continuar` se a proxima decisao for a mesma acao.

O mundo (secao 6, MF-4): as arvores (quedas, recarga, ate 4 frutas no chao por arvore), a comida que amadurece, apodrece e some, e a
bola que rola, cada sorteio num fluxo proprio por `derivar_semente` (`mundo-arvores`, `mundo-bola`, `mundo-sujeira`), nunca na
`_rng_ambiente` do engine nem na rng do pet. As quedas nao dependem do pet: P0 e P1 da mesma semente veem as mesmas (G-NUMS).

A percepcao (secao 7, MF-3): `Observacao.mundo` = `PercepcaoMundo` (posicao, regiao, os objetos vistos a ate 6 celulas, o cheiro e a
direcao dele, o alvo pendente). A consequencia (secao 8): depois de andar, comer e brincar, o gancho opcional `consequencia_mundo(acao,
ocorrido, obs_depois)`, uma vez por decisao de explorar, comer ou brincar; o `fruta_comida` da E2 quando o pet come uma fruta; e o
cerebro observa a transicao com a observacao seguinte ja com tudo aplicado.

O que o motor registra para as medidas do plano (adendo 1, A1.8; as medidas sao do D): a posicao e a regiao a cada decisao
(`decisoes_mundo`), as trocas de regiao (`regioes`), as visitas as manchas das arvores com chegada e saida (`visitas`), as quedas
(`quedas`, do fluxo que nao depende do pet), os consumos (`consumos_mundo`), as comidas deixadas e as que sumiram.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Callable

from .ambiente import PoliticaInstintoBola
from .config import CONFIG_BOLA, CONFIG_DONOS, CONFIG_MUNDO, CONFIG_MUNDO_LIGADA, CONFIG_PADRAO, TICKS_POR_DIA, Config, ConfigMundo
from .config import ConfigDonos
from .donos import Visao
from .events import (ACOES_BOLA, ACOES_FRUTAS, FRUTAS, TIPOS_COMIDA_MUNDO, AcaoPet, AcaoUsuario, LogDeEventos, ler_deixar_bola,
                     ler_deixar_comida)
from .events import deixar_bola as evento_deixar_bola
from .events import deixar_comida as evento_deixar_comida
from .frutas import MotorFrutas
from .policy import Observacao, Transicao
from .protocol import derivar_semente
from .temperamento import NEUTRO, Temperamento
from .treino import CanalDeInteracao, OrcamentoExcedido, OrcamentoNaoConsumido, Vida

ESCALA_DIR = 1024
# as 16 direcoes em inteiros: (arred(1024 cos a), -arred(1024 sen a)), a = i x 22,5 graus; y cresce para o sul
DIR16 = ((1024, 0), (946, -392), (724, -724), (392, -946), (0, -1024), (-392, -946), (-724, -724), (-946, -392),
         (-1024, 0), (-946, 392), (-724, 724), (-392, 946), (0, 1024), (392, 946), (724, 724), (946, 392))
# as 8 do cheiro (secao 7): 1 a 8 = L, NE, N, NO, O, SO, S, SE (os indices pares do DIR16)
DIRECOES_CHEIRO = ("L", "NE", "N", "NO", "O", "SO", "S", "SE")
ACOES_COM_ALVO = (AcaoPet.EXPLORAR, AcaoPet.COMER, AcaoPet.BRINCAR)
ID_BOLA = 0
GESTOS_PROIBIDOS = (AcaoUsuario.ALIMENTAR,) + ACOES_BOLA + ACOES_FRUTAS


class MundoSemChave(RuntimeError):
    """Gesto do mundo (`deixar_*`) num motor com ConfigMundo.ligada = False."""


class GestoForaDoMundo(ValueError):
    """Gesto de hoje (`alimentar`, `oferecer_fruta_<f>`, `por_bola`, `tirar_bola`) numa vida com o mundo: o gesto e o `deixar_*`."""


# ================================================================== a conta inteira (a mesma no TS da etapa 5)
def div_arred(n: int, d: int) -> int:
    """n / d em inteiros, arredondado ao mais proximo, meio longe do zero (o mesmo de lobos.div_arred). d > 0."""
    if d <= 0:
        raise ValueError(f"divisor nao positivo: {d}")
    q, r = divmod(abs(n), d)
    if 2 * r >= d:
        q += 1
    return q if n >= 0 else -q


def distancia(dx: int, dy: int) -> int:
    return math.isqrt(dx * dx + dy * dy)


def no_mapa(x: int, y: int, cm: ConfigMundo) -> tuple[int, int]:
    """corta para dentro do mapa"""
    return min(cm.celulas_x * cm.sub - 1, max(0, x)), min(cm.celulas_y * cm.sub - 1, max(0, y))


def deslocar(x: int, y: int, direcao: int, comprimento: int, cm: ConfigMundo) -> tuple[int, int]:
    """o ponto a `comprimento` subunidades na direcao (0 a 15 do DIR16), cortado para dentro do mapa"""
    cx, cy = DIR16[direcao]
    return no_mapa(x + div_arred(cx * comprimento, ESCALA_DIR), y + div_arred(cy * comprimento, ESCALA_DIR), cm)


def passo_ate(x: int, y: int, tx: int, ty: int, alcance: int, cm: ConfigMundo) -> tuple[int, int]:
    """secao 5: chega em t se d <= alcance; senao anda `alcance` na direcao de t, cortado para dentro do mapa"""
    dx, dy = tx - x, ty - y
    d = distancia(dx, dy)
    if d <= alcance:
        return tx, ty
    return no_mapa(x + div_arred(dx * alcance, d), y + div_arred(dy * alcance, d), cm)


def centro_da_celula(celula: tuple, cm: ConfigMundo) -> tuple[int, int]:
    return celula[0] * cm.sub + cm.sub // 2, celula[1] * cm.sub + cm.sub // 2


def regiao_de(x: int, cm: ConfigMundo) -> int:
    """0 casa, 1 jardim, 2 campo, 3 mata (a ordem de layout.regioes)"""
    celula = x // cm.sub
    for i, (_, x0, x1) in enumerate(cm.layout.regioes):
        if x0 <= celula <= x1:
            return i
    raise ValueError(f"x fora de toda regiao: {x}")


def cheiro_em(x: int, y: int, fontes: list[tuple[int, int, int]], cm: ConfigMundo) -> int:
    """secao 7: a soma de A x (R - d) // R sobre as comidas boas com d < R; `fontes` = (x, y, A)"""
    raio = cm.raio_cheiro_celulas * cm.sub
    total = 0
    for fx, fy, a in fontes:
        d = distancia(fx - x, fy - y)
        if d < raio:
            total += a * (raio - d) // raio
    return total


def direcao_do_cheiro(x: int, y: int, fontes: list[tuple[int, int, int]], cm: ConfigMundo) -> tuple[int, int]:
    """(cheiro no centro, direcao): a direcao 1 a 8 em que o cheiro medido a 1 celula passa do centro, a maior vence e o empate fica
    com a ordem fixa; 0 sem gradiente. O ponto da medida nao e cortado ao mapa (so conta)."""
    centro = cheiro_em(x, y, fontes, cm)
    melhor, direcao = centro, 0
    for k in range(8):
        cx, cy = DIR16[2 * k]
        c = cheiro_em(x + div_arred(cx * cm.sub, ESCALA_DIR), y + div_arred(cy * cm.sub, ESCALA_DIR), fontes, cm)
        if c > melhor:
            melhor, direcao = c, k + 1
    return centro, direcao


# ================================================================== percepcao e alvos
@dataclass(frozen=True)
class PercepcaoMundo:
    """Secao 7. `vistos`: (id, tipo, dx, dy, d), em ordem de d, tipo e id, no maximo `max_vistos`; tipo = `racao`, `a`, `b`, `c`,
    o mesmo com `_podre`, ou `bola` (id 0). `cheiro` so das comidas boas; `direcao_cheiro` 0 a 8; `alvo_pendente` o tipo do alvo da
    decisao anterior que ficou sem chegar, ou None."""

    x: int
    y: int
    regiao: int
    vistos: tuple
    cheiro: int
    direcao_cheiro: int
    alvo_pendente: str | None


@dataclass(frozen=True)
class Alvo:
    """Um candidato a alvo (secao 5). tipo: `comida` (id), `bola` (id 0), `cheiro`, `vagar`, `casa`, `continuar` (de = o tipo do alvo
    antigo) ou `ponto` (so o cerebro, no explorar: um lugar lembrado)."""

    tipo: str
    x: int
    y: int
    id: int | None = None
    de: str | None = None

    @staticmethod
    def ponto(x: int, y: int) -> "Alvo":
        return Alvo("ponto", x, y)

    def objeto(self) -> str | None:
        """`comida` ou `bola` quando o alvo e um objeto (direto ou pelo continuar)"""
        t = self.de if self.tipo == "continuar" else self.tipo
        return t if t in ("comida", "bola") else None

    def para_dict(self) -> dict:
        return {"tipo": self.tipo, "x": self.x, "y": self.y, "id": self.id, "de": self.de}


# ================================================================== o embrulho da politica
class _PoliticaComMundo:
    """Embrulho do MotorMundo (so com a chave): antes de `agir` avanca o mundo e injeta `obs.mundo`; em `observar` aplica a consequencia
    do mundo ANTES de repassar a transicao (com a observacao seguinte refeita), e depois chama os ganchos. Delega o resto."""

    def __init__(self, politica, motor: "MotorMundo") -> None:
        self._pm = politica
        self._motor = motor

    def agir(self, obs: Observacao, rng: random.Random) -> AcaoPet:
        obs = replace(obs, mundo=self._motor._antes_da_decisao())
        self._motor._obs_decisao = obs
        return self._pm.agir(obs, rng)

    def observar(self, transicao: Transicao) -> None:
        m = self._motor
        ocorrido = m._consequencia(transicao.acao)
        obs_depois = replace(Observacao.de_estado(m._estado), mundo=m._perceber(m._estado.tick))
        self._pm.observar(Transicao(observacao=m._obs_decisao, acao=transicao.acao, observacao_seguinte=obs_depois,
                                    recompensa=transicao.recompensa))
        comeu = ocorrido["comeu"] if ocorrido is not None else None
        if comeu is not None and comeu["tipo"] in FRUTAS:
            aviso = getattr(self._pm, "fruta_comida", None)     # E2: os cerebros que ja o usam
            if aviso is not None:
                aviso(comeu["tipo"], obs_depois)
        if ocorrido is not None:
            gancho = getattr(self._pm, "consequencia_mundo", None)
            if gancho is not None:
                gancho(transicao.acao, ocorrido, obs_depois)

    def receber_acao_dono(self, acao: AcaoUsuario, tick: int) -> None:
        self._pm.receber_acao_dono(acao, tick)

    def estado_interno(self) -> dict:
        return self._pm.estado_interno()

    def __getattr__(self, nome: str):
        return getattr(self._pm, nome)


# ================================================================== o motor
class MotorMundo(MotorFrutas):
    def __init__(self, *a, cfg_mundo: ConfigMundo | None = None, efeito_frutas: dict | None = None, **kw) -> None:
        super().__init__(*a, **kw)
        self.cmf = cfg_mundo or CONFIG_MUNDO
        if not self.cmf.ligada:
            if efeito_frutas is not None:
                raise ValueError("efeito_frutas so existe com o mundo ligado")
            return                                     # desligado: o MotorFrutas byte a byte (nem embrulho)
        if self.cf.ligada or self.cb.ligada:
            raise ValueError("o mundo substitui o cenario do N4 e da A1: ConfigFrutas e ConfigBola desligadas com ConfigMundo.ligada")
        if self.ce.ligada or self.cl.ligada:
            raise ValueError("o mundo minimo roda sem educacao e sem lesoes (a morte fica desligada, plano secao 2)")
        efeito = {f: 0.0 for f in FRUTAS} if efeito_frutas is None else dict(efeito_frutas)
        if set(efeito) != set(FRUTAS):
            raise ValueError(f"efeito_frutas precisa de {FRUTAS}: {sorted(efeito)}")
        self.efeito_frutas = efeito
        cm, sub = self.cmf, self.cmf.sub
        self._alcance = cm.velocidade * self.cfg.intervalo_decisao_ticks
        self._raio_pegar = cm.raio_pegar_celulas * sub
        self._raio_visao = cm.raio_visao_celulas * sub
        self._raio_mancha = cm.raio_mancha_celulas * sub
        semente = self.semente
        self._rng_arvores = random.Random(derivar_semente("mundo-arvores", semente))
        self._rng_bola = random.Random(derivar_semente("mundo-bola", semente))
        self._rng_sujeira = random.Random(derivar_semente("mundo-sujeira", semente))
        self._rng_alvo = random.Random(derivar_semente("alvo", semente))
        self.pet = centro_da_celula(cm.layout.ninho, cm)
        self.comedouro = centro_da_celula(cm.layout.comedouro, cm)
        bx, by = centro_da_celula(cm.layout.bola_inicio, cm)
        self.bola_mundo = {"x0": bx, "y0": by, "x1": bx, "y1": by, "t0": 0, "d": 0}
        nomes = [r[0] for r in cm.layout.regioes]
        self.arvores: list[dict] = []
        for ident, x, y, fruta in cm.layout.arvores:
            if fruta not in FRUTAS:
                raise ValueError(f"arvore {ident} com fruta desconhecida: {fruta!r}")
            ax, ay = centro_da_celula((x, y), cm)
            nome = nomes[regiao_de(ax, cm)]
            if nome == "jardim":
                p = cm.p_queda_jardim * cm.mult_queda
            elif nome == "mata":
                p = cm.p_queda_mata * cm.mult_queda
            else:
                raise ValueError(f"arvore {ident} fora do jardim e da mata: {nome}")
            self.arvores.append({"id": ident, "x": ax, "y": ay, "fruta": fruta, "regiao": nome, "p": p, "recarga_ate": 0})
        self.comidas: dict[int, dict] = {}
        self._prox_id = ID_BOLA + 1
        self._passo_mundo = 0
        self._pendente: dict | None = None             # {"acao", "alvo"}: o alvo que ficou sem chegar
        self._fome_antes = 0.0
        self._percepcao: PercepcaoMundo | None = None
        self._obs_decisao: Observacao | None = None
        self._manchas_abertas: dict[str, dict] = {}
        # os registros (derivados; o replay reconstroi tudo)
        self.quedas: list[dict] = []
        self.consumos_mundo: list[dict] = []
        self.sumidas: list[dict] = []
        self.deixadas: list[dict] = []
        self.bolas_deixadas: list[dict] = []
        self.rolagens: list[dict] = []
        self.decisoes_mundo: list[dict] = []
        self.regioes: list[dict] = []
        self.visitas: list[dict] = []
        self.politica = _PoliticaComMundo(self.politica, self)

    # ------------------------------------------------------------ a comida e a bola no tempo
    def _prazo_maduro(self, tipo: str) -> int:
        return self.cmf.maduro_racao_min if tipo == "racao" else self.cmf.maduro_fruta_min

    def situacao(self, comida: dict, tick: int) -> str | None:
        """`madura`, `podre`, ou None (sumiu), pela idade (secao 6)"""
        idade = tick - comida["tick_posta"]
        m = self._prazo_maduro(comida["tipo"])
        if idade < m:
            return "madura"
        if idade < m + self.cmf.prazo_podre_min:
            return "podre"
        return None

    def bola_em(self, tick: int) -> tuple[int, int]:
        """a bola anda `atrito` subunidades por tick ate parar no ponto final"""
        b = self.bola_mundo
        if b["d"] == 0 or tick >= b["t0"] + -(-b["d"] // self.cmf.atrito):
            return b["x1"], b["y1"]
        andou = self.cmf.atrito * (tick - b["t0"])
        return b["x0"] + div_arred((b["x1"] - b["x0"]) * andou, b["d"]), b["y0"] + div_arred((b["y1"] - b["y0"]) * andou, b["d"])

    def _nova_comida(self, tipo: str, x: int, y: int, tick: int, origem: str) -> dict:
        c = {"id": self._prox_id, "tipo": tipo, "x": x, "y": y, "tick_posta": tick, "origem": origem}
        self._prox_id += 1
        self.comidas[c["id"]] = c
        return c

    def _remover_sumidas(self, tick: int) -> None:
        for c in [c for c in self.comidas.values() if self.situacao(c, tick) is None]:
            del self.comidas[c["id"]]
            fim = c["tick_posta"] + self._prazo_maduro(c["tipo"]) + self.cmf.prazo_podre_min
            self.sumidas.append({**c, "sumiu_em": fim})

    def _atualizar_mundo(self, tick: int) -> None:
        """os passos do mundo ate o tick (secao 6): em cada um, cada arvore fora da recarga sorteia a queda no fluxo `mundo-arvores`.
        Os sorteios nao dependem do pet; so quantas frutas cabem no chao dependem (o excesso nao cai)."""
        cm, rng = self.cmf, self._rng_arvores
        ate = tick // cm.passo_mundo_ticks
        while self._passo_mundo < ate:
            self._passo_mundo += 1
            tk = self._passo_mundo * cm.passo_mundo_ticks
            for arv in self.arvores:
                if tk < arv["recarga_ate"]:
                    continue
                if rng.random() >= arv["p"]:
                    continue
                n = rng.randint(cm.frutas_por_queda_min, cm.frutas_por_queda_max)
                pontos = [deslocar(arv["x"], arv["y"], rng.randrange(16), rng.randrange(cm.raio_queda_celulas * cm.sub + 1), cm)
                          for _ in range(n)]
                no_chao = sum(1 for c in self.comidas.values()
                              if c["origem"] == arv["id"] and self.situacao(c, tk) is not None)
                cabem = max(0, cm.max_frutas_por_arvore - no_chao)
                ids = [self._nova_comida(arv["fruta"], x, y, tk, arv["id"])["id"] for x, y in pontos[:cabem]]
                self.quedas.append({"tick": tk, "arvore": arv["id"], "sorteadas": n, "pontos": pontos, "colocadas": ids})
                arv["recarga_ate"] = tk + cm.recarga_min
        self._remover_sumidas(tick)

    # ------------------------------------------------------------ percepcao
    def _fontes_de_cheiro(self, tick: int) -> list[tuple[int, int, int]]:
        cm = self.cmf
        return [(c["x"], c["y"], cm.cheiro_racao if c["tipo"] == "racao" else cm.cheiro_fruta)
                for c in self.comidas.values() if self.situacao(c, tick) == "madura"]

    def _perceber(self, tick: int) -> PercepcaoMundo:
        """Pura (nao sorteia nem muda nada): o que o pet percebe agora."""
        x, y = self.pet
        vistos = []
        for c in self.comidas.values():
            sit = self.situacao(c, tick)
            if sit is None:
                continue
            dx, dy = c["x"] - x, c["y"] - y
            d = distancia(dx, dy)
            if d <= self._raio_visao:
                vistos.append((c["id"], c["tipo"] if sit == "madura" else c["tipo"] + "_podre", dx, dy, d))
        bx, by = self.bola_em(tick)
        d = distancia(bx - x, by - y)
        if d <= self._raio_visao:
            vistos.append((ID_BOLA, "bola", bx - x, by - y, d))
        vistos.sort(key=lambda v: (v[4], v[1], v[0]))
        cheiro, direcao = direcao_do_cheiro(x, y, self._fontes_de_cheiro(tick), self.cmf)
        pend = self._pendente["alvo"].tipo if self._pendente is not None else None
        return PercepcaoMundo(x, y, regiao_de(x, self.cmf), tuple(vistos[:self.cmf.max_vistos]), cheiro, direcao, pend)

    def _antes_da_decisao(self) -> PercepcaoMundo:
        """Chamado pelo embrulho logo antes de `agir`: o mundo anda ate o tick e o pet percebe."""
        t = self._estado.tick
        self._atualizar_mundo(t)
        self._percepcao = self._perceber(t)
        self._fome_antes = self._estado.fome
        return self._percepcao

    # ------------------------------------------------------------ os alvos
    def _alvo_cheiro(self, p: PercepcaoMundo) -> Alvo:
        x, y = deslocar(p.x, p.y, 2 * (p.direcao_cheiro - 1), self.cmf.passo_cheiro_celulas * self.cmf.sub, self.cmf)
        return Alvo("cheiro", x, y)

    def _continuar(self, acao: AcaoPet) -> Alvo | None:
        pend = self._pendente
        if pend is None or pend["acao"] is not acao:
            return None
        velho: Alvo = pend["alvo"]
        if velho.tipo == "comida":
            c = self.comidas.get(velho.id)
            return None if c is None else Alvo("continuar", c["x"], c["y"], velho.id, "comida")
        if velho.tipo == "bola":
            bx, by = self.bola_em(self._estado.tick)
            return Alvo("continuar", bx, by, ID_BOLA, "bola")
        return Alvo("continuar", velho.x, velho.y, None, velho.tipo)

    def candidatos(self, acao: AcaoPet, u: int) -> list[Alvo]:
        """secao 5, a tabela das sub-decisoes"""
        p, cm = self._percepcao, self.cmf
        cands: list[Alvo] = []
        if acao is AcaoPet.COMER:
            cands += [Alvo("comida", p.x + dx, p.y + dy, i) for i, tipo, dx, dy, _ in p.vistos if tipo != "bola"]
            if p.direcao_cheiro:
                cands.append(self._alvo_cheiro(p))
        elif acao is AcaoPet.EXPLORAR:
            if p.direcao_cheiro:
                cands.append(self._alvo_cheiro(p))
            faixa = cm.vagar_max_celulas - cm.vagar_min_celulas + 1
            vx, vy = deslocar(p.x, p.y, u % 16, (cm.vagar_min_celulas + (u // 16) % faixa) * cm.sub, cm)
            cands.append(Alvo("vagar", vx, vy))
            cands.append(Alvo("casa", *self.comedouro))
        elif acao is AcaoPet.BRINCAR:
            cands += [Alvo("bola", p.x + dx, p.y + dy, i) for i, tipo, dx, dy, _ in p.vistos if tipo == "bola"]
        else:
            raise ValueError(f"acao sem alvo: {acao}")
        cont = self._continuar(acao)
        if cont is not None:
            cands.append(cont)
        return cands

    def alvo_padrao(self, acao: AcaoPet, cands: list[Alvo]) -> Alvo | None:
        """o que o instinto usa (secao 5). Nunca escolhe comida podre."""
        p = self._percepcao
        if acao is AcaoPet.COMER:
            podres = {i for i, tipo, *_ in p.vistos if tipo.endswith("_podre")}
            for a in cands:                                  # os vistos ja vem em ordem de d, tipo, id
                if a.tipo == "comida" and a.id not in podres:
                    return a
            return next((a for a in cands if a.tipo == "cheiro"), None)
        if acao is AcaoPet.EXPLORAR:
            cont = next((a for a in cands if a.tipo == "continuar"), None)
            if cont is not None:
                return cont
            if p.direcao_cheiro and p.cheiro > self.cmf.limiar_cheiro_explorar:
                return next(a for a in cands if a.tipo == "cheiro")
            return next(a for a in cands if a.tipo == "vagar")
        return next((a for a in cands if a.tipo == "bola"), None)

    def _validar_alvo(self, acao: AcaoPet, alvo: Alvo, cands: list[Alvo]) -> None:
        if alvo in cands:
            return
        if acao is AcaoPet.EXPLORAR and alvo.tipo == "ponto" and alvo.id is None and alvo.de is None:
            if type(alvo.x) is int and type(alvo.y) is int and no_mapa(alvo.x, alvo.y, self.cmf) == (alvo.x, alvo.y):
                return
            raise ValueError(f"ponto fora do mapa ou nao inteiro: ({alvo.x!r}, {alvo.y!r})")
        raise ValueError(f"alvo fora dos candidatos de {acao.value}: {alvo}")

    # ------------------------------------------------------------ a consequencia
    def _comer_mundo(self, ident: int, como: str, tick: int) -> dict:
        c = self.comidas.pop(ident)
        sit = self.situacao(c, tick)
        e = self._estado
        fome, humor, sujeira = e.fome, e.humor, e.sujeira
        if sit == "madura" and c["tipo"] == "racao":
            fome = min(1.0, fome + self.cfg.ganho_alimentar)
            if self._rng_sujeira.random() < self.cfg.prob_sujeira_pos_refeicao:
                sujeira = min(self.cfg.sujeira_maxima, sujeira + 1)
        elif sit == "madura":
            fome = min(1.0, fome + self.cmf.nutricao_fruta)
            humor = min(1.0, max(0.0, humor + self.efeito_frutas[c["tipo"]]))
        else:
            humor = min(1.0, max(0.0, humor + self.cmf.efeito_podre))
        self._estado = replace(e, fome=fome, humor=humor, sujeira=sujeira)
        reg = {"tick": tick, "id": c["id"], "tipo": c["tipo"], "origem": c["origem"], "tick_posta": c["tick_posta"],
               "situacao": sit, "como": como, "fome_antes": e.fome, "humor_antes": e.humor, "fome_depois": fome,
               "humor_depois": humor}
        self.consumos_mundo.append(reg)
        return reg

    def _rolar_bola(self, tick: int) -> None:
        cm = self.cmf
        bx, by = self.bola_em(tick)
        direcao = self._rng_bola.randrange(16)
        celulas = self._rng_bola.randint(cm.bola_min_celulas, cm.bola_max_celulas)
        if self.cmf.layout.regioes[regiao_de(bx, cm)][0] == "campo":
            celulas *= cm.mult_bola_campo
        x1, y1 = deslocar(bx, by, direcao, celulas * cm.sub, cm)
        self.bola_mundo = {"x0": bx, "y0": by, "x1": x1, "y1": y1, "t0": tick, "d": distancia(x1 - bx, y1 - by)}
        self.rolagens.append({"tick": tick, "de": (bx, by), "para": (x1, y1), "direcao": direcao, "celulas": celulas})

    def _consequencia(self, acao: AcaoPet) -> dict | None:
        """Chamado pelo embrulho em `observar`, antes do cerebro: anda, come, brinca, desfaz o +0,05 do comer (MF-2) e registra."""
        tick = self._estado.tick
        x0, y0 = self.pet
        regiao_antes = regiao_de(x0, self.cmf)
        alvo = None
        ocorrido = None
        if acao in ACOES_COM_ALVO:
            u = self._rng_alvo.randrange(1 << 16)               # sempre nas tres acoes: numeros comuns
            cands = self.candidatos(acao, u)
            escolher = getattr(self._pm_cerebro(), "escolher_alvo", None)
            alvo = escolher(acao, list(cands), self._percepcao, u) if escolher is not None else None
            if alvo is None:
                alvo = self.alvo_padrao(acao, cands)
            else:
                self._validar_alvo(acao, alvo, cands)
            x1, y1 = (x0, y0) if alvo is None else passo_ate(x0, y0, alvo.x, alvo.y, self._alcance, self.cmf)
            desloc = distancia(x1 - x0, y1 - y0)
            self.pet = (x1, y1)
            e = self._estado
            if acao is AcaoPet.COMER:
                e = replace(e, fome=self._fome_antes)               # MF-2: comer so da fome com comida
            energia_antes = e.energia
            if desloc:
                e = replace(e, energia=max(0.0, e.energia - self.cmf.custo_energia_por_subunidade * desloc))
            self._estado = e
            chegou = alvo is not None and distancia(alvo.x - x1, alvo.y - y1) <= self._raio_pegar
            comeu = None
            bola = False
            if chegou and acao is AcaoPet.COMER and alvo.objeto() == "comida":
                comeu = self._comer_mundo(alvo.id, "comer", tick)
            elif chegou and acao is AcaoPet.EXPLORAR and self._estado.fome < self.cmf.fome_max_comer_achado:
                perto = sorted((distancia(c["x"] - x1, c["y"] - y1), c["tipo"], c["id"]) for c in self.comidas.values()
                               if self.situacao(c, tick) == "madura")
                perto = [p for p in perto if p[0] <= self._raio_pegar]
                if perto:
                    comeu = self._comer_mundo(perto[0][2], "achou", tick)
            elif chegou and acao is AcaoPet.BRINCAR and alvo.objeto() == "bola":
                self._estado = replace(self._estado, humor=min(1.0, self._estado.humor + self.cmf.ganho_humor_bola))
                self._rolar_bola(tick)
                bola = True
            if alvo is not None and not chegou:
                base = alvo if alvo.tipo != "continuar" else Alvo(alvo.de, alvo.x, alvo.y, alvo.id)
                self._pendente = {"acao": acao, "alvo": base}
            else:
                self._pendente = None
            ocorrido = {"acao": acao.value, "u": u, "alvo": None if alvo is None else alvo.para_dict(), "de": (x0, y0),
                        "para": (x1, y1), "deslocamento": desloc, "energia_gasta": energia_antes - self._estado.energia,
                        "chegou": chegou, "comeu": comeu, "brincou_com_bola": bola}
        else:
            self._pendente = None
        self._registrar_decisao(tick, acao, (x0, y0), regiao_antes, alvo, ocorrido)
        return ocorrido

    def _pm_cerebro(self):
        """o que esta embaixo do embrulho do mundo (os ganchos do cerebro passam pelos embrulhos de baixo)"""
        return self.politica._pm

    def _registrar_decisao(self, tick: int, acao: AcaoPet, antes: tuple, regiao_antes: int, alvo: Alvo | None,
                           ocorrido: dict | None) -> None:
        x1, y1 = self.pet
        regiao = regiao_de(x1, self.cmf)
        for v in self._manchas_abertas.values():               # as decisoes tomadas de dentro da mancha
            v["decisoes"] += 1
        dentro = {a["id"] for a in self.arvores if distancia(a["x"] - x1, a["y"] - y1) <= self._raio_mancha}
        for ident in [i for i in self._manchas_abertas if i not in dentro]:
            v = self._manchas_abertas.pop(ident)
            v["saida"] = tick
            self.visitas.append(v)
        for ident in sorted(dentro - set(self._manchas_abertas)):
            self._manchas_abertas[ident] = {"arvore": ident, "chegada": tick, "saida": None, "decisoes": 0}
        if regiao != regiao_antes:
            self.regioes.append({"tick": tick, "de": regiao_antes, "para": regiao})
        self.decisoes_mundo.append({
            "tick": tick, "acao": acao.value, "regra": getattr(self._pm_cerebro(), "ultima_regra", None),
            "antes": antes, "regiao_antes": regiao_antes, "x": x1, "y": y1, "regiao": regiao,
            "alvo": None if alvo is None else alvo.tipo,
            "chegou": None if ocorrido is None else ocorrido["chegou"],
            "deslocamento": 0 if ocorrido is None else ocorrido["deslocamento"],
            "energia_gasta": 0.0 if ocorrido is None else ocorrido["energia_gasta"],
            "comeu": None if ocorrido is None or ocorrido["comeu"] is None else ocorrido["comeu"]["id"],
            "brincou_com_bola": False if ocorrido is None else ocorrido["brincou_com_bola"],
            "manchas": sorted(dentro)})

    # ------------------------------------------------------------ o dono
    def _aplicar_acao_usuario(self, acao: AcaoUsuario) -> None:
        if self.cmf.ligada and acao in GESTOS_PROIBIDOS:
            raise GestoForaDoMundo(f"{acao.value} numa vida com o mundo: use deixar_comida/deixar_bola")
        super()._aplicar_acao_usuario(acao)

    def deixar_comida(self, tipo: str, x: int, y: int) -> None:
        if not self.cmf.ligada:
            raise MundoSemChave("deixar_comida com ConfigMundo.ligada = False")
        evento = evento_deixar_comida(self._estado.tick, tipo, x, y)     # valida tipo e posicao antes do log
        self._log.anexar(evento)
        self._aplicar_deixar_comida(*ler_deixar_comida(evento))

    def deixar_bola(self, x: int, y: int) -> None:
        if not self.cmf.ligada:
            raise MundoSemChave("deixar_bola com ConfigMundo.ligada = False")
        evento = evento_deixar_bola(self._estado.tick, x, y)
        self._log.anexar(evento)
        self._aplicar_deixar_bola(*ler_deixar_bola(evento))

    def _aplicar_deixar_comida(self, tipo: str, x: int, y: int) -> None:
        if not self.cmf.ligada:
            raise MundoSemChave("deixar_comida com ConfigMundo.ligada = False")
        if tipo not in TIPOS_COMIDA_MUNDO or no_mapa(x, y, self.cmf) != (x, y):
            raise ValueError(f"deixar_comida invalido: {tipo!r} ({x}, {y})")
        tick = self._estado.tick
        c = self._nova_comida(tipo, x, y, tick, "dono")
        self.deixadas.append({"tick": tick, "id": c["id"], "tipo": tipo, "x": x, "y": y, "pet": self.pet})
        # contato, como o alimentar de hoje: zera o tempo sem cuidado, soma um cuidado, vinculo e politica recebem `alimentar`
        self._contato(AcaoUsuario.ALIMENTAR, tick)

    def _aplicar_deixar_bola(self, x: int, y: int) -> None:
        if not self.cmf.ligada:
            raise MundoSemChave("deixar_bola com ConfigMundo.ligada = False")
        if no_mapa(x, y, self.cmf) != (x, y):
            raise ValueError(f"deixar_bola fora do mapa: ({x}, {y})")
        tick = self._estado.tick
        self._n_eventos += 1                     # e um evento do log, mas NAO e contato (o por_bola de hoje)
        self.bola_mundo = {"x0": x, "y0": y, "x1": x, "y1": y, "t0": tick, "d": 0}
        self.bolas_deixadas.append({"tick": tick, "x": x, "y": y})

    # ------------------------------------------------------------ leitura
    def estado(self) -> dict:
        d = super().estado()
        if not self.cmf.ligada:
            return d                             # desligado: o estado() do MotorFrutas, sem chave nova
        t = self._estado.tick
        d["mundo"] = {"pet": self.pet, "regiao": self.cmf.layout.regioes[regiao_de(self.pet[0], self.cmf)][0],
                      "bola": self.bola_em(t),
                      "comidas": sum(1 for c in self.comidas.values() if self.situacao(c, t) is not None)}
        return d

    def resumo_mundo_fisico(self) -> dict:
        """tudo o que o mundo guarda (o G1 compara isto bit a bit)"""
        return {"pet": self.pet, "bola": dict(self.bola_mundo), "comidas": [dict(c) for c in self.comidas.values()],
                "prox_id": self._prox_id, "passo_mundo": self._passo_mundo,
                "arvores": [dict(a) for a in self.arvores],
                "pendente": None if self._pendente is None else {"acao": self._pendente["acao"].value,
                                                                 "alvo": self._pendente["alvo"].para_dict()},
                "rngs": [r.getstate() for r in (self._rng_arvores, self._rng_bola, self._rng_sujeira, self._rng_alvo)],
                "quedas": self.quedas, "consumos": self.consumos_mundo, "sumidas": self.sumidas, "deixadas": self.deixadas,
                "bolas_deixadas": self.bolas_deixadas, "rolagens": self.rolagens, "decisoes": self.decisoes_mundo,
                "regioes": self.regioes, "visitas": self.visitas,
                "manchas_abertas": [dict(v) for v in self._manchas_abertas.values()]}


# ================================================================== replay
def reproduzir_mundo(log: LogDeEventos, politica_fabrica: Callable, cfg: Config | None = None, semente: int = 42,
                     fabrica_motor: Callable | None = None, ate_tick: int | None = None) -> MotorMundo:
    """O replay que entende os eventos do mundo (`deixar_comida`, `deixar_bola`). `ate_tick`: para antes do primeiro evento nesse
    tick (corta o avanco que o atravessa), como o reproduzir_educacao. Evento desconhecido levanta erro; luta, origem, fala e
    decisao externa tambem: o mundo minimo roda sem educacao e sem lesoes."""
    cfg = cfg or CONFIG_PADRAO
    if fabrica_motor is None:
        raise ValueError("reproduzir_mundo precisa da fabrica do MotorMundo")
    motor = fabrica_motor(politica_fabrica(cfg), cfg, semente)
    if not isinstance(motor, MotorMundo):
        raise TypeError(f"a fabrica devolveu {type(motor).__name__}, nao MotorMundo")
    for evento in log:
        if ate_tick is not None and evento.tick >= ate_tick:
            break
        if evento.tipo == "avanco":
            motor._avancar(int(evento.valor) if ate_tick is None else min(int(evento.valor), ate_tick - evento.tick))
        elif evento.tipo == "acao_usuario":
            motor._aplicar_acao_usuario(AcaoUsuario(evento.valor))
        elif evento.tipo == "deixar_comida":
            motor._aplicar_deixar_comida(*ler_deixar_comida(evento))
        elif evento.tipo == "deixar_bola":
            motor._aplicar_deixar_bola(*ler_deixar_bola(evento))
        else:
            raise ValueError(f"tipo de evento desconhecido no log do mundo: {evento.tipo!r}")
    motor._log = LogDeEventos([e for e in log if ate_tick is None or e.tick < ate_tick])
    return motor


def fabricas_mundo(cfg_mundo: ConfigMundo | None = None, politica_fabrica: Callable | None = None,
                   temperamento: Temperamento = NEUTRO, especie: str = "brasa", efeito_frutas: dict | None = None, **kw):
    """(fabrica da politica, fabrica do motor) de uma vida com o mundo, no desenho do plano (secao 2): obediencia, educacao, lesoes,
    frutas e bola desligadas. A politica padrao e o instinto com o gancho vazio do dono (o instinto do mundo e do chat B, etapa 3).
    Reusadas no replay."""
    cm = cfg_mundo or CONFIG_MUNDO_LIGADA
    fp = politica_fabrica or (lambda cfg=None: PoliticaInstintoBola(cfg, CONFIG_BOLA))  # noqa: E731
    fm = (lambda politica, cfg, s: MotorMundo(politica, cfg, s, temperamento, especie, obediencia_desligada=True,  # noqa: E731
                                              cfg_mundo=cm, efeito_frutas=efeito_frutas, **kw))
    return fp, fm


# ================================================================== o dono
@dataclass(frozen=True)
class DeixarComida:
    tipo: str
    x: int
    y: int


@dataclass(frozen=True)
class DeixarBola:
    x: int
    y: int


ESTILOS_LUGAR = ("comedouro", "perto", "longe")


class DonoComLugar:
    """Embrulha um dono sintetico (secao 4): o `alimentar` vira `deixar_comida("racao", x, y)` no lugar do estilo. A rng do lugar e
    `derivar_semente("dono-lugar", semente, rotulo_dono)`, sem o braco: P0 e P1 sorteiam os mesmos desvios. Um sorteio fixo por
    `alimentar` em cada estilo (perto e longe: direcao e distancia; comedouro: nenhum)."""

    def __init__(self, base, estilo: str, semente: int, rotulo_dono: str, cfg_mundo: ConfigMundo | None = None) -> None:
        if estilo not in ESTILOS_LUGAR:
            raise ValueError(f"estilo de lugar desconhecido: {estilo!r} (opcoes: {ESTILOS_LUGAR})")
        self.base = base
        self.estilo = estilo
        self.nome = getattr(base, "nome", rotulo_dono)
        self.cmf = cfg_mundo or CONFIG_MUNDO_LIGADA
        self._rng = random.Random(derivar_semente("dono-lugar", semente, rotulo_dono))
        self.lugares: list[dict] = []

    def lugar(self, estado: dict) -> tuple[int, int]:
        m = estado.get("mundo")
        if m is None:
            raise ValueError("o DonoComLugar precisa do estado() do MotorMundo ligado (chave `mundo`)")
        cm = self.cmf
        if self.estilo == "comedouro":
            return centro_da_celula(cm.layout.comedouro, cm)
        px, py = m["pet"]
        direcao = self._rng.randrange(16)
        if self.estilo == "perto":
            r = self._rng.randrange(cm.perto_max_celulas * cm.sub + 1)
        else:
            r = self._rng.randint(cm.longe_min_celulas * cm.sub, cm.longe_max_celulas * cm.sub)
        return deslocar(px, py, direcao, r, cm)

    def decidir(self, visao: Visao, rng: random.Random) -> list:
        saida = []
        for acao in self.base.decidir(visao, rng):
            if acao is AcaoUsuario.ALIMENTAR:
                x, y = self.lugar(visao.estado)
                self.lugares.append({"tick": visao.estado["tick"], "x": x, "y": y, "pet": visao.estado["mundo"]["pet"]})
                saida.append(DeixarComida("racao", x, y))
            else:
                saida.append(acao)
        return saida


class CanalMundo(CanalDeInteracao):
    """O CanalDeInteracao com os gestos do mundo: `DeixarComida` e `DeixarBola` gastam orcamento como qualquer acao do dono."""

    def aplicar(self, acoes: list, passo: int, passos_totais: int) -> None:
        minimo, maximo = self.limites(passo, passos_totais)
        if len(acoes) > maximo:
            raise OrcamentoExcedido(f"passo {passo}: dono pediu {len(acoes)} interacoes, maximo {maximo} "
                                    f"(gasto {self.gasto}/{self.orcamento})")
        if len(acoes) < minimo:
            raise OrcamentoNaoConsumido(f"passo {passo}: dono fez {len(acoes)} interacoes, minimo {minimo} "
                                        f"para fechar o orcamento")
        for acao in acoes:
            if isinstance(acao, DeixarComida):
                self.motor.deixar_comida(acao.tipo, acao.x, acao.y)
            elif isinstance(acao, DeixarBola):
                self.motor.deixar_bola(acao.x, acao.y)
            elif isinstance(acao, AcaoUsuario):
                aceita = getattr(self.motor, "aceita", None)
                if aceita is not None and not aceita(acao):
                    self.rejeitados += 1
                    continue
                self.motor.observar(acao)
            else:
                raise TypeError(f"acao invalida vinda do dono: {acao!r}")
            self.gasto += 1


def simular_vida_mundo(braco: str, dono, politica, semente: int, dias: int, orcamento: int, fabrica_motor: Callable,
                       cfg: Config | None = None, cfg_donos: ConfigDonos | None = None, rotulo_dono: str | None = None) -> Vida:
    """treino.simular_vida com o CanalMundo: o dono (embrulhado pelo DonoComLugar) deixa a comida e a bola pelos gestos do mundo, que
    gastam o orcamento. A rng do dono e a de sempre (`dono`, semente, rotulo)."""
    cfg = cfg or CONFIG_PADRAO
    cfg_donos = cfg_donos or CONFIG_DONOS
    total = dias * TICKS_POR_DIA
    if total % cfg_donos.passo_ticks != 0:
        raise ValueError("duracao nao e multipla do passo do dono")
    passos = total // cfg_donos.passo_ticks
    motor = fabrica_motor(politica, cfg, semente)
    if not isinstance(motor, MotorMundo) or not motor.cmf.ligada:
        raise ValueError("simular_vida_mundo precisa do MotorMundo com o mundo ligado")
    rng_dono = random.Random(derivar_semente("dono", semente, rotulo_dono or braco))
    canal = CanalMundo(motor, orcamento, cfg_donos.max_interacoes_por_passo)
    for passo in range(passos):
        motor.avancar(cfg_donos.passo_ticks)
        minimo, maximo = canal.limites(passo, passos)
        visao = Visao(estado=motor.estado(), passo=passo, passos_totais=passos, orcamento=orcamento, gasto=canal.gasto,
                      minimo_obrigatorio=minimo, maximo_permitido=maximo)
        canal.aplicar(dono.decidir(visao, rng_dono), passo, passos)
    canal.fechar()
    return Vida(braco=braco, semente_coorte=semente, motor=motor, interacoes=canal.gasto)
