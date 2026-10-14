"""A bancada em módulos (rodada de saúde, etapa 3; docs/TAREFA_V2_SAUDE.md).

Parte o `experiments/bancada_v2.py` de um só arquivo no pacote `experiments/bancada/`, um módulo por assunto, **sem mudar uma linha de
lógica**: cada nó de topo (função, classe, constante) vai para o módulo do assunto dele com o TEXTO de antes, comentários incluídos. Só
as importações são refeitas: cada módulo importa da biblioteca e do `digilab` o que usa, e dos outros módulos do pacote o que precisa.

  python tools/dividir_bancada.py analisar    # o mapa nó -> módulo e as dependências entre os módulos
  python tools/dividir_bancada.py dividir     # escreve o pacote e a fachada (o bancada_v2.py de antes vira a fachada)
  python tools/dividir_bancada.py conferir    # a prova pela AST: todo nó de antes está, igual, num módulo (G-AST)

A fonte da verdade do "antes" é o `experiments/bancada_v2.py` do commit dado em `--base` (padrão: o arquivo do disco, antes da divisão).
O mapa (`MAPA`) diz o módulo de cada nome de topo; um nome que não está no mapa falha alto (um PR novo na bancada pede uma linha aqui).
"""
from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
FONTE = "experiments/bancada_v2.py"
PACOTE = "experiments/bancada"
PROVA = "docs/historico/bancada_mapa.json"

# o módulo de cada nome de topo, na ordem de importação (as dependências na hora da definição só apontam para cima nesta lista)
MODULOS = {
    "faixas": "as sementes dos testes, as bases, as faixas reservadas e queimadas, os prefixos e as unidades derivadas",
    "mundos": "as condições, os mundos, os eventos do mundo, o corpo por regime, os efeitos das frutas e o calendário",
    "bracos": "os sinais e filtros, os pontos do aprendiz, os braços, os nós pendentes, a montagem e a PoliticaDoBraco",
    "vida": "a especificação e o resultado de uma vida, o filtro do log, as contagens e o resumo do motor",
    "regras_mundo": "o tapa na fruta X, as regras e os informantes do mundo, as vidas pelo mundo e o registro da medição",
    "medidas": "as medidas que não são métodos da Bancada: o banheiro, a rede de si, as sondas e as tabelas",
    "nucleo": "a classe Bancada, inteira (SA-4: partir em mixins é outra passada)",
    "config": "a validação da config, o teto de pesos, a rede da config e a bancada da config",
    "rodar": "gravar, o sha256, o meta, rodar e a linha de comando (main)",
    "grupo": "dois pets: a bancada do grupo",
    "passo0": "o passo 0 do corpo",
    "pet_que_pensa": "o pet que pensa (J5): a bancada",
}
MAPA = {
    "faixas": """SEMENTES_TESTE BASES_EXPERIMENTO_MAIOR BASES_N6 BASES_N7 BASES_COMPARACAO PREFIXOS_UNIDADES FAIXAS_QUEIMADAS
        FAIXAS_RESERVADAS unidades_derivadas na_faixa_reservada SementeSemPlano""",
    "mundos": """EVENTOS_DO_MUNDO Condicao CONDICOES Mundo MUNDOS LAYOUTS_FISICO mundo_de CONFIG_CORPO_QUIMICA REGIMES_CORPO
        SUBCHAVES_CORPO CONFIG_JULGAMENTO_FORA JULGAMENTOS efeitos_da_condicao MotorFrutasMundo CalendarioFrutas""",
    "bracos": """ACOES SINAIS PONTOS_APRENDIZ PONTO_PADRAO PONTO_N5_EXPERIMENTO CEREBROS INFORMACOES PEDIDOS GESTOS SINAIS_DO_DONO
        FILTROS FORA_DO_ORCAMENTO GESTOS_DONO Braco BRACOS BRACOS_BANHEIRO FONTES_IMPLEMENTADAS NOS_PENDENTES FILTROS_PENDENTES
        MODO_MEMORIA CONFIG_LOBOS_PADRAO NOMES_DRIVES NOVOS_W APRENDE_PELA_CONSEQUENCIA braco_de filtro_de desarranjo_n6 MONTAGENS
        MONTAGEM_PADRAO MONTAGEM_COMPLETA recebe_informacao braco_montado cfg_lobos_do_braco PoliticaDoBraco""",
    "vida": """ReplayDivergiu EspecVida VidaBancada filtrar_log contar_acoes contar_gestos_mundo contar_pedidos contar_informacoes
        resumo_motor _interno""",
    "regras_mundo": """fruta_tapa DonoTapaFruta RegraBola InformanteDoMundo InformanteAcoplado RegraFrutasComJulgador
        RegraFrutasComInformante RegraFrutasComPedinte _Espiao simular_vida_mundo CanalSemEnsino simular_vida_fisico
        sondar_metabolismo comeu_fruta_e2 _Registro _julgar""",
    "medidas": """MEDIDAS_TABELA receptores_novos_de medidas_banheiro_de tabela_banheiro percepcao_da_sonda do_braco
        PoliticaComRedeSemOrgaos sondar_quimicos sonda_ao_nascer _normalizar_cands rede_offline _resumo_pesos rede_de _estado_rede
        tabelas_braco_condicao tabela_dominancia _coluna MEDIDAS_FRUTAS MEDIDAS_MUNDO""",
    "nucleo": "Bancada",
    "config": """CHAVES_CONFIG validar_config cfg_lobos_do_ponto validar_teto_pesos conferir_teto_pesos cfg_rede_da_config
        bancada_da_config""",
    "rodar": "_gravar _dump _sha rodar meta main",
    "grupo": """ROTULO_RUIM ROTULO_EMBARALHA DECISOES_POR_DIA BRACO_DO_B JANELA_PRIMARIA_DIAS tipo_ruim desarranjo_dois_pets
        efeito_dois_pets MotorMundoTroca BracoGrupo BRACOS_GRUPO EspecGrupo VidaGrupo _RegistroGrupo _validar_espec_grupo _entradas
        _resumo_grupo CHAVES_CONFIG_GRUPO validar_config_grupo rodar_grupo""",
    "passo0": """PASSO0_MULTIPLICADORES PASSO0_FAIXA PASSO0_BRACO PASSO0_CAMPOS _escalar PASSO0_CHAVES_EXTRAS grade_passo0 pontos_passo0
        fracao_falta_passo0 escolha_passo0 _rodar_ponto_passo0 rodar_passo0""",
    "pet_que_pensa": """PLANO_PQP PREFIXO_PQP BASES_PET_QUE_PENSA ROTULO_X_PQP ROTULO_Y_PQP D_A_PQP JANELA_PQP N_MAO_PQP HORA_MUDANCA_PQP
        N_OPORTUNIDADES_PQP PROTOCOLOS_PQP CONGELA_PQP BracoPQP BRACOS_PQP braco_pqp fruta_x_pqp fruta_y_pqp efeitos_pqp
        MotorMundoMudanca PoliticaComModeloPQP RegraMudancaPQP EspecPQP VidaPQP _arvores_do_layout BancadaPQP _media _RegistroPQP
        _sem_modelos plano_da_vida fracao_plano_dias modelos_contra_o_real CHAVES_CONFIG_PQP validar_config_pqp bancada_pqp_da_config
        rodar_pqp""",
}
MODULO_DE = {nome: mod for mod, nomes in MAPA.items() for nome in nomes.split()}
# os nós sem nome próprio (asserts e ifs de módulo) vão com o nó de nome anterior; estes nomes de laço não são de topo
NOMES_DE_LACO = {"a", "b", "c", "f", "fonte"}


def ler_fonte(base: str | None) -> str:
    if base is None:
        return (RAIZ / FONTE).read_bytes().decode("utf-8")
    saida = subprocess.run(["git", "-C", str(RAIZ), "show", f"{base}:{FONTE}"], capture_output=True)
    if saida.returncode != 0:
        raise RuntimeError(saida.stderr.decode("utf-8", "replace"))
    return saida.stdout.decode("utf-8")


def definidos(n: ast.stmt) -> set[str]:
    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return {n.name}
    if isinstance(n, (ast.Import, ast.ImportFrom)):
        return {(a.asname or a.name).split(".")[0] for a in n.names}
    return {t.id for t in ast.walk(n) if isinstance(t, ast.Name) and isinstance(t.ctx, ast.Store)} - NOMES_DE_LACO


def usados(nos) -> set[str]:
    return {t.id for x in nos for t in ast.walk(x) if isinstance(t, ast.Name) and isinstance(t.ctx, ast.Load)}


def na_definicao(n: ast.stmt) -> list:
    """O que roda na hora da definição (com `from __future__ import annotations`, as anotações não rodam): decoradores e defaults das
    funções; bases, decoradores e o corpo das classes, menos os corpos dos métodos; o nó inteiro nos outros casos."""
    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return n.decorator_list + n.args.defaults + [d for d in n.args.kw_defaults if d]
    if isinstance(n, ast.ClassDef):
        corpo = []
        for b in n.body:
            if isinstance(b, (ast.FunctionDef, ast.AsyncFunctionDef)):
                corpo += na_definicao(b)
            elif isinstance(b, ast.AnnAssign):
                corpo += [b.value] if b.value is not None else []
            else:
                corpo.append(b)
        return n.decorator_list + n.bases + [k.value for k in n.keywords] + corpo
    if isinstance(n, ast.AnnAssign):
        return [n.value] if n.value is not None else []
    return [n]


class Particao:
    """A fonte de antes, partida em nós: o cabeçalho (docstring, importações, RAIZ e sys.path), os nós de cada módulo (com o texto
    de antes, do fim do nó anterior até o fim do nó) e o bloco `if __name__ == "__main__"`."""

    def __init__(self, fonte: str) -> None:
        self.fonte = fonte
        self.linhas = fonte.splitlines(keepends=True)
        self.arvore = ast.parse(fonte)
        corpo = self.arvore.body
        self.importacoes = [n for n in corpo if isinstance(n, (ast.Import, ast.ImportFrom))]
        self.nomes_importados = {nome: n for n in self.importacoes for nome in definidos(n)}
        self.nos: list[tuple[str, ast.stmt, str]] = []          # (módulo, nó, texto)
        self.cabecalho: list[ast.stmt] = []
        self.principal: ast.stmt | None = None
        anterior_fim = 0
        modulo_anterior = None
        primeiro_no = None
        for n in corpo:
            texto = "".join(self.linhas[anterior_fim:n.end_lineno])
            anterior_fim = n.end_lineno
            if isinstance(n, (ast.Import, ast.ImportFrom)) or (primeiro_no is None and not self._e_no(n)):
                self.cabecalho.append(n)
                continue
            if self._e_principal(n):
                self.principal = n
                continue
            nomes = definidos(n)
            if nomes:
                mods = {MODULO_DE.get(x) for x in nomes}
                if None in mods:
                    raise KeyError(f"nome de topo sem módulo no MAPA: {sorted(x for x in nomes if x not in MODULO_DE)}")
                if len(mods) != 1:
                    raise ValueError(f"um nó com nomes em módulos diferentes: {sorted(nomes)}")
                mod = mods.pop()
            else:
                if modulo_anterior is None:
                    raise ValueError(f"nó sem nome antes de qualquer nó com nome (linha {n.lineno})")
                mod = modulo_anterior
            primeiro_no = primeiro_no or n
            self.nos.append((mod, n, texto))
            modulo_anterior = mod
        self.cauda = "".join(self.linhas[anterior_fim:])
        definidos_topo = [x for _, n, _ in self.nos for x in definidos(n)]
        sobra = set(MODULO_DE) - set(definidos_topo)
        if sobra:
            raise KeyError(f"nomes do MAPA que a fonte não define: {sorted(sobra)}")
        self.topo = set(definidos_topo)

    @staticmethod
    def _e_principal(n: ast.stmt) -> bool:
        return isinstance(n, ast.If) and ast.dump(n.test) == ast.dump(ast.parse('__name__ == "__main__"').body[0].value)

    @staticmethod
    def _e_no(n: ast.stmt) -> bool:
        """Os nós do cabeçalho que não são importação: a docstring, RAIZ e o sys.path.insert."""
        if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant):
            return False
        if isinstance(n, ast.Assign) and definidos(n) == {"RAIZ"}:
            return False
        if isinstance(n, ast.Expr) and "sys.path.insert" in ast.unparse(n):
            return False
        return True

    def dependencias(self) -> dict[str, dict[str, dict[str, set[str]]]]:
        """Por módulo: os nomes de outros módulos usados na definição (`definicao`) e só dentro de corpos de função (`chamada`)."""
        saida: dict[str, dict[str, dict[str, set[str]]]] = {m: {"definicao": {}, "chamada": {}} for m in MAPA}
        for mod, n, _ in self.nos:
            agora = usados(na_definicao(n)) & self.topo
            depois = (usados([n]) & self.topo) - agora
            for tipo, nomes in (("definicao", agora), ("chamada", depois)):
                for x in nomes - definidos(n):
                    outro = MODULO_DE[x]
                    if outro != mod:
                        saida[mod][tipo].setdefault(outro, set()).add(x)
        return saida

    def importados_usados(self, mod: str) -> set[str]:
        return usados([n for m, n, _ in self.nos if m == mod]) & set(self.nomes_importados)


def analisar(p: Particao) -> None:
    dep = p.dependencias()
    ordem = list(MAPA)
    for mod in ordem:
        n = sum(1 for m, _, _ in p.nos if m == mod)
        linhas = sum(t.count("\n") for m, _, t in p.nos if m == mod)
        print(f"\n{mod}: {n} nós, {linhas} linhas")
        for tipo in ("definicao", "chamada"):
            for outro, nomes in sorted(dep[mod][tipo].items()):
                marca = "  ACIMA" if ordem.index(outro) < ordem.index(mod) else "  ABAIXO"
                print(f"  {tipo:9} <- {outro:13}{marca}: {', '.join(sorted(nomes))[:150]}")


LARGURA = 140
CABECA_MODULO = (
    '"""A bancada da V2, módulo `{mod}`.\n'
    "\n"
    "{tema_maiusculo}.\n"
    "\n"
    "Parte do pacote `experiments/bancada/` (rodada de saúde, etapa 3; docs/TAREFA_V2_SAUDE.md). O texto de cada definição é o de antes,\n"
    "movido de `experiments/bancada_v2.py` sem mudança (tools/dividir_bancada.py; a prova pela AST em docs/historico/bancada_mapa.json).\n"
    "O `experiments/bancada_v2.py` continua sendo a porta de entrada: ele reexporta todo nome daqui.\n"
    '"""\n'
    "from __future__ import annotations\n")
COMENTARIO_FIM = ("# os nomes de outros módulos do pacote que só rodam dentro das funções: importados depois das definições, para o pacote\n"
                  "# não ter importação circular (tools/dividir_bancada.py)\n")
COMENTARIO_FACHADA = (
    "# A bancada em módulos (rodada de saúde, etapa 3; docs/TAREFA_V2_SAUDE.md): o código está no pacote experiments/bancada/, um módulo por\n"
    "# assunto (a tabela em experiments/bancada/__init__.py). Este arquivo ficou como a porta de entrada: a docstring e as importações de\n"
    "# antes, iguais, e todo nome de topo do pacote, posto aqui pelo `instalar_fachada`. `import bancada_v2 as bv`, `bv.X` e `bv.X = ...`\n"
    "# valem como antes, e `python experiments/bancada_v2.py ...` também.\n"
    "if __package__:\n"
    "    from . import bancada as _pacote  # noqa: E402\n"
    "else:\n"
    "    import bancada as _pacote  # noqa: E402\n"
    "_pacote.instalar_fachada(sys.modules[__name__])\n")
# as únicas linhas que mudam, porque o arquivo mudou de lugar: o sha256 "da bancada" no meta (antes Path(__file__), que agora seria o
# rodar.py; passa a ser a fachada, o mesmo arquivo de antes). O RAIZ fica na fachada como era, e o pacote tem o dele (parents[2]).
TROCAS = {"meta": ('"bancada_sha256": _sha(Path(__file__))', '"bancada_sha256": _sha(RAIZ / "experiments" / "bancada_v2.py")')}


def _linha_import(n: ast.stmt, nomes: list[ast.alias], largura: int = LARGURA) -> str:
    """Uma importação com só os nomes dados, quebrada em LARGURA colunas, no estilo do arquivo de antes."""
    if isinstance(n, ast.Import):
        return "".join(f"import {ast.unparse(a)}\n" for a in nomes)
    cabeca = f"from {'.' * n.level}{n.module or ''} import "
    partes = [ast.unparse(a) for a in nomes]
    if len(cabeca) + len(", ".join(partes)) <= largura:
        return cabeca + ", ".join(partes) + "\n"
    recuo = " " * (len(cabeca) + 1)
    linhas, atual = [], cabeca + "("
    for k, parte in enumerate(partes):
        pedaco = parte + (", " if k + 1 < len(partes) else ")")
        if len(atual) + len(pedaco.rstrip()) > largura and atual not in (cabeca + "(", recuo):
            linhas.append(atual.rstrip())
            atual = recuo
        atual += pedaco
    linhas.append(atual)
    return "\n".join(linhas) + "\n"


def _import_do_pacote(origem: str, nomes: set[str], fim: bool) -> str:
    alias = [ast.alias(name=x) for x in sorted(nomes, key=lambda s: (s.lstrip("_").lower(), s))]
    largura = LARGURA - len("  # noqa: E402") if fim else LARGURA
    texto = _linha_import(ast.ImportFrom(module=origem, names=alias, level=1), alias, largura)
    return texto.replace("\n", "  # noqa: E402\n", 1) if fim else texto


def gerar(p: Particao) -> dict[str, str]:
    """O texto de cada arquivo novo: os módulos e a fachada (o __init__ é escrito à mão e conferido por teste)."""
    dep = p.dependencias()
    arquivos: dict[str, str] = {}
    for mod, tema in MODULOS.items():
        nos = [(n, t) for m, n, t in p.nos if m == mod]
        usados_mod = usados([n for n, _ in nos])
        biblioteca, digilab = "", ""
        for imp in p.importacoes:
            if isinstance(imp, ast.ImportFrom) and imp.module == "__future__":
                continue
            nomes = [a for a in imp.names if (a.asname or a.name).split(".")[0] in usados_mod]
            if not nomes:
                continue
            if isinstance(imp, ast.ImportFrom) and (imp.module or "").startswith("digilab"):
                digilab += _linha_import(imp, nomes)
            else:
                biblioteca += _linha_import(imp, nomes)
        bloco = biblioteca + ("\n" if biblioteca and digilab else "") + digilab
        topo = dep[mod]["definicao"]
        pacote = ("from . import RAIZ\n" if "RAIZ" in usados_mod else "")
        pacote += "".join(_import_do_pacote(o, topo[o], fim=False) for o in MODULOS if o in topo)
        texto = CABECA_MODULO.format(mod=mod, tema_maiusculo=tema[0].upper() + tema[1:]) + "\n" + bloco + ("\n" + pacote if pacote else "")
        corpo = "".join(t for _, t in nos).lstrip("\n")
        for nome, (antes, depois) in TROCAS.items():
            if any(nome in definidos(n) for n, _ in nos):
                if corpo.count(antes) != 1:
                    raise ValueError(f"a troca de {nome} não acha o texto de antes uma vez só")
                corpo = corpo.replace(antes, depois)
        texto += "\n\n" + corpo
        chamada = {o: ns - topo.get(o, set()) for o, ns in dep[mod]["chamada"].items()}
        fim = [o for o in MODULOS if chamada.get(o)]
        if fim:
            texto += "\n\n" + COMENTARIO_FIM + "".join(_import_do_pacote(o, chamada[o], fim=True) for o in fim)
        arquivos[f"{PACOTE}/{mod}.py"] = texto
    arquivos[FONTE] = fachada(p)
    return arquivos


def fachada(p: Particao) -> str:
    """O bancada_v2.py novo: a docstring e o bloco de importações de antes (com o RAIZ e o sys.path), iguais, e a instalação dos nomes."""
    fim_cabecalho = max(n.end_lineno for n in p.cabecalho)
    principal = "".join(p.linhas[p.principal.lineno - 1:p.principal.end_lineno])
    return "".join(p.linhas[:fim_cabecalho]) + "\n" + COMENTARIO_FACHADA + "\n\n" + principal


def dividir(p: Particao) -> None:
    for rel, texto in gerar(p).items():
        caminho = RAIZ / rel
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_bytes(texto.encode("utf-8"))
        print("escrito:", rel)


def nos_do_modulo(texto: str) -> list[ast.stmt]:
    """Os nós de topo de um módulo novo, sem a docstring e sem as importações."""
    corpo = ast.parse(texto).body
    if corpo and isinstance(corpo[0], ast.Expr) and isinstance(corpo[0].value, ast.Constant):
        corpo = corpo[1:]
    return [n for n in corpo if not isinstance(n, (ast.Import, ast.ImportFrom))]


def conferir(p: Particao, base: str) -> dict:
    """G-AST: cada nó de antes está, na mesma ordem, no módulo do mapa, com a AST igual (salvo as TROCAS, declaradas); a fachada tem a
    docstring, as importações e o `if __name__` de antes. Devolve o mapa (gravado em docs/historico/bancada_mapa.json)."""
    falhas, nos = [], []
    for mod in MODULOS:
        novos = nos_do_modulo((RAIZ / PACOTE / f"{mod}.py").read_bytes().decode("utf-8"))
        antigos = [(n, t) for m, n, t in p.nos if m == mod]
        if len(novos) != len(antigos):
            falhas.append(f"{mod}: {len(antigos)} nós antes, {len(novos)} depois")
            continue
        for (velho, _), novo in zip(antigos, novos):
            nome = ",".join(sorted(definidos(velho))) or type(velho).__name__
            igual = ast.dump(velho) == ast.dump(novo)
            troca = next((k for k in TROCAS if k in definidos(velho)), None)
            if not igual and troca is None:
                falhas.append(f"{mod}: o nó {nome} (linha {velho.lineno} antes) mudou")
            nos.append({"nome": nome, "modulo": mod, "linhas_antes": f"{velho.lineno}-{velho.end_lineno}",
                        "igual": igual, **({"troca": TROCAS[troca][1]} if troca and not igual else {})})
    texto_fachada = (RAIZ / FONTE).read_bytes().decode("utf-8")
    nova = ast.parse(texto_fachada).body
    velhos = [n for n in p.cabecalho] + [p.principal]
    achados = [n for n in nova if any(ast.dump(n) == ast.dump(v) for v in velhos)]
    if len(achados) != len(velhos):
        falhas.append(f"a fachada não tem o cabeçalho e o `if __name__` de antes ({len(achados)} de {len(velhos)} nós)")
    antes, depois = nomes_do_modulo_antes(p.fonte), nomes_da_fachada()
    if antes != depois:
        falhas.append(f"G-NOMES: só antes {sorted(antes - depois)[:10]}; só depois {sorted(depois - antes)[:10]}")
    if falhas:
        raise SystemExit("G-AST FALHA:\n  " + "\n  ".join(falhas))
    fonte = p.fonte.encode("utf-8")
    import hashlib
    return {"base": {"commit": base, "arquivo": FONTE, "sha256": hashlib.sha256(fonte).hexdigest(), "linhas": len(p.linhas)},
            "modulos": MODULOS, "nos": nos,
            "trocas": {k: {"antes": a, "depois": d} for k, (a, d) in TROCAS.items()},
            "nomes": sorted(antes)}


# os nomes que a fachada tem a mais, por construção (o pacote que ela importa)
NOMES_DA_FACHADA = {"_pacote"}


def nomes_do_modulo_antes(fonte: str) -> set[str]:
    """G-NOMES: os nomes do módulo de antes, importado de verdade (de uma cópia num diretório temporário), sem os dunder."""
    import importlib.util
    import tempfile
    sys.path.insert(0, str(RAIZ))
    with tempfile.TemporaryDirectory() as pasta:
        caminho = Path(pasta) / "bancada_v2_antes.py"
        caminho.write_bytes(fonte.encode("utf-8"))
        spec = importlib.util.spec_from_file_location("bancada_v2_antes", caminho)
        modulo = importlib.util.module_from_spec(spec)
        sys.modules["bancada_v2_antes"] = modulo
        try:
            spec.loader.exec_module(modulo)
        finally:
            del sys.modules["bancada_v2_antes"]
    return {n for n in vars(modulo) if not n.startswith("__")}


def nomes_da_fachada() -> set[str]:
    sys.path.insert(0, str(RAIZ / "experiments"))
    import importlib
    fachada = importlib.import_module("bancada_v2")
    return {n for n in vars(fachada) if not n.startswith("__")} - NOMES_DA_FACHADA


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("comando", choices=["analisar", "dividir", "conferir"])
    ap.add_argument("--base", default=None, help="o commit do bancada_v2.py de antes (padrão: o arquivo do disco, só para analisar e dividir)")
    args = ap.parse_args()
    particao = Particao(ler_fonte(args.base))
    if args.comando == "analisar":
        analisar(particao)
    elif args.comando == "dividir":
        dividir(particao)
    else:
        if args.base is None:
            raise SystemExit("conferir precisa de --base: o commit do bancada_v2.py de antes")
        mapa = conferir(particao, args.base)
        (RAIZ / PROVA).write_bytes((json.dumps(mapa, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
        n_iguais = sum(1 for x in mapa["nos"] if x["igual"])
        print(f"G-AST passa: {len(mapa['nos'])} nós de topo nos {len(MODULOS)} módulos, {n_iguais} com a AST igual, "
              f"{len(mapa['nos']) - n_iguais} com a troca declarada; a fachada tem o cabeçalho e o `if __name__` de antes")
