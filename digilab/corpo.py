"""O corpo do Creatures 3 por baixo dos drives (V2, W-CORPO-QUIMICA e W-CORPO-DIGESTAO; docs/TAREFA_V2_CORPO_DRIVES.md, secao 14).

Etapa 1: a quimica dos drives de hoje, sem orgao (secao 4). Cinco quimicos guardam a FALTA de cada drive, em inteiros de [0, C]:

    fome         -> fome      (o drive lido e (C - q) / C)
    desconforto  -> higiene
    cansaco      -> energia
    tristeza     -> humor
    dano         -> saude

Os numeros sao os de hoje, convertidos para a escala C = 450000 (CD-1): o mmc dos denominadores das taxas de hoje, entao toda taxa e
todo efeito de hoje viram inteiros exatos. A conversao confere isso ao montar as taxas e falha alto se um numero sair da grade.

Etapa 3, o orgao 1 (secao 5, sub-chave `digestao`): a comida (a racao, o comer, a nutricao da fruta) entra como o quimico `alimento`, e
a reacao da digestao tira `alimento` e a mesma quantidade de `fome`, ate `taxa_digestao` por tick. Na taxa C (CD-3) tudo passa no mesmo
tick, e a fome lida e a de hoje. O que sobra no estomago quando a fome chega a 0 e descartado: e o corte de hoje (a fome nao passa de 1).
O corpo expoe quanto digeriu em cada tick (a vontade do banheiro, docs/TAREFA_V2_BANHEIRO.md, secao 3, sobe com ele).

Etapa 4, o orgao 2 (secao 6, sub-chave `vida`): o quimico `vida` comeca em C ao nascer e decai `vida_decaimento` por tick. Receptores sobre
a Vida mudam o estagio nos limiares C - v x tick_do_estagio, com os ticks de estagio de hoje (as duracoes da ConfigEvolucaoPesquisa, as
mesmas de treino_stats.estagio_no_tick): o estagio pela Vida e o de hoje, tick a tick. A Vida nao mata nesta etapa (em 0, fica em 0) e
nao tem receptor para o cerebro.

Os estimulos do mundo fisico (digilab/mundo.py; para o A ligar o MotorMundo no MotorCorpo): o andar (`estimulo_andar`, o custo de hoje,
1/6000 de energia por subunidade, e 75 em C), as comidas do mapa (`estimulo_consumo_mundo`: a racao deixada, a fruta madura e a podre,
com os numeros da ConfigMundo) e a MF-2 (`acao_pet(..., com_mundo=True)`: no mundo, comer nao da fome por si; a comida vem do mapa). A
sujeira depois da racao continua sorteada pelo mundo (o fluxo `mundo-sujeira`), no Estado.

Componente puro: nao e motor, nao sorteia (nenhuma rng), nao le o cerebro. A sujeira e o sono continuam estados do `Estado` (o motor
sorteia a sujeira como hoje); o corpo so os le. Quem liga o corpo ao motor e o A (etapa 2, `MotorCorpo`).

Por que a vida com o corpo nao sai byte a byte igual a de hoje (secao 3): os limiares de hoje caem sobre a grade inteira. A fome que
parte de 0,80 chega a 0,25 exato no tick 660 em inteiros, e o float de hoje passa um pouco abaixo. Por isso o G-HOJE e, aqui, em malha
aberta (as mesmas acoes forcadas, tick a tick), e a malha fechada fica com o plano.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from .config import CONFIG_EVOLUCAO_PESQUISA, CONFIG_PADRAO, TICKS_POR_DIA, Config, ConfigCorpo, ConfigEvolucaoPesquisa, ConfigMundo
from .events import FRUTAS, TIPOS_COMIDA_MUNDO, AcaoPet, AcaoUsuario
from .state import Estado

QUIMICOS = ("fome", "desconforto", "cansaco", "tristeza", "dano")
DRIVE_DO_QUIMICO = {"fome": "fome", "desconforto": "higiene", "cansaco": "energia", "tristeza": "humor", "dano": "saude"}
QUIMICOS_DA_PRIVACAO = ("fome", "desconforto", "cansaco")       # Estado.em_privacao: fome, higiene e energia (humor nao conta)
ORGAO_DIGESTAO = ("alimento",)                                    # sem receptor para o cerebro (secao 5)
ORGAO_VIDA = ("vida",)                                            # sem receptor para o cerebro (secao 6)
ESTAGIOS = ("bebe", "crianca", "adolescente", "adulto")           # os de treino_stats.estagio_no_tick, na ordem


def quimicos_de(cc: ConfigCorpo) -> tuple[str, ...]:
    """Os quimicos que o corpo tem com estas chaves: os cinco de hoje e os de cada orgao ligado."""
    return QUIMICOS + (ORGAO_DIGESTAO if cc.digestao else ()) + (ORGAO_VIDA if cc.vida else ())


TOLERANCIA_GRADE = 1e-6                                           # quanto um numero de hoje x C pode fugir de um inteiro (so erro de float)

# Status dos campos da ConfigCorpo (conferido por teste). Todos PROPOSTOS, nenhum referendado.
PARAMETROS_CORPO: dict[str, tuple[str, str]] = {
    "ligada": ("PROPOSTO", "TAREFA_V2_CORPO_DRIVES, secao 2: a quimica dos drives de hoje (etapa 1)"),
    "digestao": ("PROPOSTO", "secao 5, etapa 3 (orgao 1, W-CORPO-DIGESTAO)"),
    "vida": ("PROPOSTO", "secao 6, etapa 4 (orgao 2, W-CORPO-DIGESTAO)"),
    "drives_novos": ("PROPOSTO", "secao 7, etapa 6; falha alto nesta etapa"),
    "gestos": ("PROPOSTO", "secao 8, etapa 6; falha alto nesta etapa"),
    "escala": ("DECIDIDO", "CD-1: C = 450000, o mmc dos denominadores das taxas de hoje (#210)"),
    "escala_receptor": ("PROPOSTO", "= S do cerebro A (2**ConfigLobos.bits_ponto_fixo), secao 3"),
    "bits_meia_vida": ("PROPOSTO", "secao 3: k_h na escala 2**16"),
    "pet_brincar_cansaco": ("PROPOSTO", "o literal de policy.efeito_da_acao_do_pet (energia -0,02) x C"),
    "pet_explorar_cansaco": ("PROPOSTO", "o literal de policy.efeito_da_acao_do_pet (energia -0,015) x C"),
    "pet_explorar_tristeza": ("PROPOSTO", "o literal de policy.efeito_da_acao_do_pet (humor +0,01) x C"),
    "pet_comer_fome": ("PROPOSTO", "o literal de policy.efeito_da_acao_do_pet (fome +0,05) x C"),
    "pet_emburrar_tristeza": ("PROPOSTO", "o literal de policy.efeito_da_acao_do_pet (humor -0,01) x C"),
    "k_meia_vida_susto": ("PROPOSTO", "secao 8: meia-vida 30, sem fonte; k pela regra da secao 3"),
    "k_meia_vida_dor": ("PROPOSTO", "secao 8: meia-vida 60, sem fonte; k pela regra da secao 3"),
    "k_meia_vida_estresse": ("PROPOSTO", "secao 7: meia-vida 1440, sem fonte; k pela regra da secao 3"),
    "taxa_digestao": ("DECIDIDO", "CD-3: C, tudo no mesmo tick (a fome de hoje); a digestao lenta so com o plano (#210)"),
    "vida_decaimento": ("PROPOSTO", "secao 6: C // (28 dias x 1440), a vida mais longa da pesquisa (o bloco de duracoes do adendo 3)"),
}


# ------------------------------------------------------------------ inteiros

def div_arred(n: int, d: int) -> int:
    """n / d em inteiros, arredondado ao mais proximo, meio longe do zero. d > 0. A mesma conta de lobos.div_arred (conferido por teste);
    copiada para o corpo nao depender de um cerebro."""
    if d <= 0:
        raise ValueError(f"divisor nao positivo: {d}")
    q, r = divmod(abs(n), d)
    if 2 * r >= d:
        q += 1
    return q if n >= 0 else -q


def na_grade(x: float, escala: int, nome: str) -> int:
    """x * escala como inteiro exato. Um numero de hoje fora da grade falha alto (a CD-1 diz que nenhum fica fora)."""
    v = x * escala
    r = int(round(v))
    if abs(v - r) > TOLERANCIA_GRADE:
        raise ValueError(f"{nome} = {x!r} nao cai na grade de {escala}: {v!r}")
    return r


def k_meia_vida(h: int, bits: int = 16) -> int:
    """A constante da meia-vida h (secao 3): arred(2**bits * (1 - 2**(-1/h))). So para derivar e conferir as constantes da ConfigCorpo;
    o tick nunca a chama (nenhuma funcao transcendental no tick)."""
    if h <= 0:
        raise ValueError(f"meia-vida nao positiva: {h}")
    return int((2 ** bits) * (1.0 - 2.0 ** (-1.0 / h)) + 0.5)


def passo_meia_vida(q: int, k: int, bits: int = 16) -> int:
    """Um tick de decaimento (secao 3): q - max(1, div_arred(q * k, 2**bits)) enquanto q > 0. O minimo de 1 impede que uma concentracao
    pequena fique presa."""
    if q <= 0:
        return 0
    return max(0, q - max(1, div_arred(q * k, 2 ** bits)))


# ------------------------------------------------------------------ taxas

@dataclass(frozen=True)
class TaxasCorpo:
    """Os numeros de hoje na escala C, com o sinal da falta (positivo = o drive piora). Montados de Config e ConfigCorpo por taxas_de."""

    fome_por_tick: int
    desconforto_por_tick: int
    desconforto_por_sujeira: int
    tristeza_por_tick: int
    cansaco_acordado: int
    cansaco_noite: int
    cansaco_dormindo: int                    # negativo: dormir descansa
    dano_privacao: int
    dano_cura: int                           # negativo
    limiar_privacao: int                     # privacao: algum quimico da privacao acima disto (o 0,15 de hoje)
    dono: dict                               # AcaoUsuario -> {quimico: delta}
    pet: dict                                # AcaoPet -> {quimico: delta}


def taxas_de(cfg: Config, cc: ConfigCorpo) -> TaxasCorpo:
    C = cc.escala
    g = lambda x, nome: na_grade(x, C, nome)  # noqa: E731
    dono = {
        AcaoUsuario.ALIMENTAR: {"fome": -g(cfg.ganho_alimentar, "ganho_alimentar")},
        AcaoUsuario.LIMPAR: {"desconforto": -g(cfg.ganho_limpar, "ganho_limpar")},
        AcaoUsuario.BRINCAR: {"tristeza": -g(cfg.ganho_brincar_humor, "ganho_brincar_humor"),
                              "cansaco": g(cfg.custo_brincar_energia, "custo_brincar_energia"),
                              "fome": g(cfg.custo_brincar_fome, "custo_brincar_fome")},
        AcaoUsuario.ACARICIAR: {"tristeza": -g(cfg.ganho_elogiar * 0.6, "ganho_elogiar * 0.6")},
        AcaoUsuario.ELOGIAR: {"tristeza": -g(cfg.ganho_elogiar, "ganho_elogiar")},
        AcaoUsuario.REPREENDER: {"tristeza": g(cfg.custo_repreender, "custo_repreender")},
    }
    pet = {
        AcaoPet.OCIOSO: {}, AcaoPet.DORMIR: {}, AcaoPet.CHAMAR_ATENCAO: {},
        AcaoPet.BRINCAR: {"tristeza": -g(cfg.humor_por_tick_brincando * cfg.intervalo_decisao_ticks, "humor do brincar"),
                          "cansaco": cc.pet_brincar_cansaco},
        AcaoPet.EXPLORAR: {"cansaco": cc.pet_explorar_cansaco, "tristeza": cc.pet_explorar_tristeza},
        AcaoPet.COMER: {"fome": cc.pet_comer_fome},
        AcaoPet.EMBURRAR: {"tristeza": cc.pet_emburrar_tristeza},
    }
    if set(pet) != set(AcaoPet):
        raise ValueError(f"acoes do pet sem efeito no corpo: {sorted(a.value for a in set(AcaoPet) - set(pet))}")
    return TaxasCorpo(
        fome_por_tick=g(cfg.decaimento_fome, "decaimento_fome"),
        desconforto_por_tick=g(cfg.decaimento_higiene, "decaimento_higiene"),
        desconforto_por_sujeira=g(cfg.decaimento_higiene * cfg.penalidade_higiene_por_sujeira, "penalidade_higiene_por_sujeira"),
        tristeza_por_tick=g(cfg.decaimento_humor, "decaimento_humor"),
        cansaco_acordado=g(cfg.decaimento_energia, "decaimento_energia"),
        cansaco_noite=g(cfg.decaimento_energia * cfg.multiplicador_noturno, "decaimento_energia * multiplicador_noturno"),
        cansaco_dormindo=-g(cfg.energia_por_tick_dormindo, "energia_por_tick_dormindo"),
        dano_privacao=g(cfg.dano_saude_por_tick, "dano_saude_por_tick"),
        dano_cura=-g(cfg.cura_saude_por_tick, "cura_saude_por_tick"),
        limiar_privacao=C - g(cfg.limiar_privacao, "limiar_privacao"),
        dono=dono,
        pet=pet,
    )


# ------------------------------------------------------------------ orgao 2: os limiares da Vida

def ticks_de_estagio(cfg_evo: ConfigEvolucaoPesquisa) -> tuple[int, int, int]:
    """Os ticks em que o estagio de hoje muda (treino_stats.estagio_no_tick): fim do bebe, da crianca e do adolescente."""
    t1 = cfg_evo.dur_bebe_min
    t2 = t1 + cfg_evo.dur_crianca_min
    return t1, t2, t2 + cfg_evo.dur_adolescente_min


def limiares_estagio(cc: ConfigCorpo, cfg_evo: ConfigEvolucaoPesquisa) -> tuple[int, ...]:
    """Os limiares dos receptores de estagio: C - v x T para cada tick de estagio T. Um limiar que nao fica acima de 0 falha alto: a Vida
    acabaria antes do estagio e o receptor nunca o veria."""
    lim = tuple(cc.escala - cc.vida_decaimento * t for t in ticks_de_estagio(cfg_evo))
    if any(x <= 0 for x in lim):
        raise ValueError(f"a Vida acaba antes de um estagio: limiares {lim} (v = {cc.vida_decaimento}, ticks {ticks_de_estagio(cfg_evo)})")
    return lim


# ------------------------------------------------------------------ o corpo

class Corpo:
    """A quimica dos drives de hoje e os orgaos ligados. `q` guarda cada quimico em [0, C] (a falta, nos de hoje). Nao sorteia; a sujeira
    e o sono vem do Estado."""

    def __init__(self, q: dict[str, int], cfg: Config | None = None, cc: ConfigCorpo | None = None,
                 cfg_evo: ConfigEvolucaoPesquisa | None = None) -> None:
        self.cfg = cfg or CONFIG_PADRAO
        self.cfg_evo = cfg_evo or CONFIG_EVOLUCAO_PESQUISA
        self.cc = cc or ConfigCorpo(ligada=True)
        if not self.cc.ligada:
            raise ValueError("Corpo com ConfigCorpo desligada: com a chave desligada o corpo nao existe")
        self.quimicos = quimicos_de(self.cc)
        if set(q) != set(self.quimicos):
            raise ValueError(f"quimicos do corpo: esperava {self.quimicos}, veio {sorted(q)}")
        for nome, v in q.items():
            if not isinstance(v, int) or isinstance(v, bool) or not 0 <= v <= self.cc.escala:
                raise ValueError(f"concentracao de {nome} fora de [0, {self.cc.escala}] ou nao inteira: {v!r}")
        self.C = self.cc.escala
        self.S = self.cc.escala_receptor
        self.t = taxas_de(self.cfg, self.cc)
        self.q = {nome: q[nome] for nome in self.quimicos}
        # orgao 1: o que passou do estomago para a fome (no tick corrente, no ultimo tick fechado e no total) e o que se descartou
        self.digerido_tick = 0
        self.digerido_no_tick = 0
        self.digerido_total = 0
        self.descartado_total = 0
        # orgao 2: os limiares dos receptores de estagio sobre a Vida
        self.limiares_estagio = limiares_estagio(self.cc, self.cfg_evo) if self.cc.vida else ()

    @classmethod
    def de_estado(cls, estado: Estado, cfg: Config | None = None, cc: ConfigCorpo | None = None,
                  cfg_evo: ConfigEvolucaoPesquisa | None = None) -> Corpo:
        """O corpo de um Estado de hoje (o do nascimento, por exemplo). Cada drive tem de cair na grade de C. A Vida e a do tick do
        Estado (C no nascimento)."""
        cc = cc or ConfigCorpo(ligada=True)
        C = cc.escala
        q = {nome: na_grade(1.0 - getattr(estado, drive), C, f"Estado.{drive}") for nome, drive in DRIVE_DO_QUIMICO.items()}
        if cc.digestao:
            q["alimento"] = 0                    # o Estado de hoje nao tem estomago: comeca vazio
        if cc.vida:
            q["vida"] = max(0, C - cc.vida_decaimento * estado.tick)
        return cls(q, cfg, cc, cfg_evo)

    # ---------------------------------------------------------- estimulos

    def _somar(self, deltas: dict[str, int]) -> None:
        for nome, d in deltas.items():
            self.q[nome] = min(self.C, max(0, self.q[nome] + d))

    def _efeito(self, deltas: dict[str, int], comida: bool) -> None:
        """Os deltas de uma acao; com a digestao, o que a comida tira da fome vai para o estomago."""
        if comida and self.cc.digestao:
            self._somar({k: v for k, v in deltas.items() if k != "fome"})
            self._ingerir(-deltas["fome"])
        else:
            self._somar(deltas)

    def acao_dono(self, acao: AcaoUsuario) -> None:
        """O efeito de state.aplicar_acao_usuario nos drives. A sujeira (limpar, e o sorteio do alimentar) e o sono (o brincar acorda)
        continuam no Estado, com o motor. Acao fora das seis de hoje falha alto: as outras sao estimulos proprios ou de outra etapa.
        A racao (alimentar) e comida; o custo de fome do brincar do dono nao."""
        if acao not in self.t.dono:
            raise ValueError(f"acao do dono sem estimulo no corpo nesta etapa: {acao.value}")
        self._efeito(self.t.dono[acao], acao is AcaoUsuario.ALIMENTAR)

    def acao_pet(self, acao: AcaoPet, com_mundo: bool = False) -> None:
        """O efeito de policy.efeito_da_acao_do_pet nos drives, na decisao, antes do tick. O sono (dormir) fica no Estado. O comer e
        comida. Com o mundo fisico (MF-2): comer nao da fome por si (o mundo desfaz o +0,05 antes de qualquer cerebro ver); a comida vem do
        mapa, pelo `estimulo_consumo_mundo`."""
        if com_mundo and acao is AcaoPet.COMER:
            return
        self._efeito(self.t.pet[acao], acao is AcaoPet.COMER)

    def estimulo_bola(self, ganho_humor: float) -> None:
        """Brincar com a bola no cenario (MotorAmbiente, A1): humor + ganho_humor_bola."""
        self._somar({"tristeza": -na_grade(ganho_humor, self.C, "ganho_humor_bola")})

    def estimulo_fruta(self, nutricao: float, efeito_humor: float) -> None:
        """Comer uma fruta (MotorFrutas, N4): fome + nutricao e humor + o efeito da fruta (E2). Sem a digestao (etapa 3), direto na fome."""
        self._efeito({"fome": -na_grade(nutricao, self.C, "nutricao"),
                      "tristeza": -na_grade(efeito_humor, self.C, "efeito_humor")}, True)

    # ---------------------------------------------------------- o mundo fisico
    def estimulo_andar(self, deslocamento: int, custo_por_subunidade: float) -> None:
        """O andar do mundo fisico (mundo.MotorMundo._consequencia): energia - custo x deslocamento, alem do efeito da acao. O custo de hoje
        (1/6000 por subunidade) e 75 em C; um custo fora da grade falha alto. `deslocamento` em subunidades, inteiro >= 0."""
        if type(deslocamento) is not int or deslocamento < 0:
            raise ValueError(f"deslocamento precisa ser inteiro >= 0: {deslocamento!r}")
        k = na_grade(custo_por_subunidade, self.C, "custo_energia_por_subunidade")
        if deslocamento:
            self._somar({"cansaco": k * deslocamento})

    def estimulo_consumo_mundo(self, tipo: str, situacao: str, cfg_mundo: ConfigMundo, efeito_fruta: float = 0.0) -> None:
        """Comer uma comida do mapa (mundo.MotorMundo._comer_mundo), pelo `comer` ou pelo "achou e comeu" do explorar:
        - racao madura: fome + ganho_alimentar (a mesma racao do alimentar de hoje; comida, com a digestao);
        - fruta madura: fome + nutricao_fruta e humor + o efeito da fruta (`efeito_fruta`, o do mundo; 0 nas frutas iguais);
        - podre (racao ou fruta): humor + efeito_podre, sem fome.
        Tipo ou situacao fora disso falha alto."""
        if tipo not in TIPOS_COMIDA_MUNDO:
            raise ValueError(f"comida do mundo desconhecida: {tipo!r}")
        if situacao == "podre":
            self._somar({"tristeza": -na_grade(cfg_mundo.efeito_podre, self.C, "efeito_podre")})
        elif situacao != "madura":
            raise ValueError(f"situacao da comida desconhecida: {situacao!r}")
        elif tipo == "racao":
            self._efeito(self.t.dono[AcaoUsuario.ALIMENTAR], True)
        elif tipo in FRUTAS:
            self.estimulo_fruta(cfg_mundo.nutricao_fruta, efeito_fruta)
        else:                                                      # pragma: no cover - TIPOS_COMIDA_MUNDO = racao + FRUTAS
            raise ValueError(f"comida sem estimulo: {tipo!r}")

    # ---------------------------------------------------------- orgao 1: a digestao

    def _ingerir(self, quantidade: int) -> None:
        """A comida vai ao estomago (cortado em C) e a digestao anda na hora, com o que resta da taxa do tick."""
        if quantidade < 0:
            raise ValueError(f"comida negativa: {quantidade}")
        self.q["alimento"] = min(self.C, self.q["alimento"] + quantidade)
        self._digerir()

    def _digerir(self) -> None:
        """A reacao da secao 5: t = min(alimento, fome, o que resta de taxa_digestao no tick); tira t do alimento e da fome. Com a fome em
        0 e comida no estomago, o resto e descartado (o corte de hoje: a fome nao passa de 1)."""
        t = min(self.q["alimento"], self.q["fome"], self.cc.taxa_digestao - self.digerido_tick)
        if t > 0:
            self.q["alimento"] -= t
            self.q["fome"] -= t
            self.digerido_tick += t
            self.digerido_total += t
        if self.q["fome"] == 0 and self.q["alimento"] > 0:
            self.descartado_total += self.q["alimento"]
            self.q["alimento"] = 0

    # ---------------------------------------------------------- o tick

    def em_privacao(self) -> bool:
        """O receptor de privacao: algum de fome, desconforto e cansaco acima de C - 0,15 C (Estado.em_privacao de hoje)."""
        return any(self.q[nome] > self.t.limiar_privacao for nome in QUIMICOS_DA_PRIVACAO)

    def passo(self, antes: Estado) -> None:
        """Um tick, na ordem de state.avancar_um_tick. `antes` e o Estado no comeco do tick: a sujeira, o sono e a hora vem dele.
        1) fome, desconforto, tristeza e cansaco; 2) o motor sorteia a sujeira (fora daqui); 3) o corte; 4) o dano pelo receptor."""
        t = self.t
        if self.cc.digestao:
            self._digerir()                       # o que ficou no estomago, com o que resta da taxa deste tick
        cansaco = t.cansaco_dormindo if antes.dormindo else (
            t.cansaco_noite if self.cfg.e_noite(antes.tick % TICKS_POR_DIA) else t.cansaco_acordado)
        self._somar({
            "fome": t.fome_por_tick,
            "desconforto": t.desconforto_por_tick + t.desconforto_por_sujeira * antes.sujeira,
            "tristeza": t.tristeza_por_tick,
            "cansaco": cansaco,
        })
        self._somar({"dano": t.dano_privacao if self.em_privacao() else t.dano_cura})
        if self.cc.digestao:
            self.digerido_no_tick = self.digerido_tick          # o tick fechou: a taxa volta inteira no proximo
            self.digerido_tick = 0
        if self.cc.vida:
            self.q["vida"] = max(0, self.q["vida"] - self.cc.vida_decaimento)   # nao mata: em 0, fica em 0

    # ---------------------------------------------------------- leituras

    def drives(self) -> dict[str, float]:
        """Os drives de hoje lidos da quimica: (C - q) / C (a divisao IEEE e exata, igual no Python e no TS)."""
        return {DRIVE_DO_QUIMICO[nome]: (self.C - self.q[nome]) / self.C for nome in QUIMICOS}

    def no_estado(self, estado: Estado) -> Estado:
        """O Estado com os cinco drives trocados pela leitura da quimica (o que o MotorCorpo vai fazer a cada tick, etapa 2)."""
        return replace(estado, **self.drives())

    def falta(self, nome: str) -> int:
        """A falta de um quimico na escala S do cerebro: div_arred(q * S, C)."""
        return div_arred(self.q[nome] * self.S, self.C)

    def receptores(self) -> dict[str, int]:
        """O que o pet sente dos drives de hoje, na escala S: o drive lido, S - falta (secao 10). Nesta etapa todos tem receptor."""
        return {DRIVE_DO_QUIMICO[nome]: self.S - self.falta(nome) for nome in QUIMICOS}

    def estagio(self) -> str:
        """Os receptores de estagio sobre a Vida (so com o orgao 2): o estagio e o numero de limiares que a Vida ja cruzou. Com a Vida
        em C - v x tick, cruzar C - v x T e o mesmo que tick >= T: o estagio de hoje, exato. Nao vai ao cerebro."""
        if not self.cc.vida:
            raise ValueError("estagio pela Vida sem o orgao 2 (ConfigCorpo.vida desligada)")
        return ESTAGIOS[sum(1 for limiar in self.limiares_estagio if self.q["vida"] <= limiar)]

    def para_dict(self) -> dict:
        d = {"q": dict(self.q)}
        if self.cc.digestao:
            d["digestao"] = {"digerido_no_tick": self.digerido_no_tick, "digerido_total": self.digerido_total,
                             "descartado_total": self.descartado_total}
        if self.cc.vida:
            d["estagio"] = self.estagio()
        return d
