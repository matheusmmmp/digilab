"""A bancada da V2 em módulos (rodada de saúde, etapa 3; docs/TAREFA_V2_SAUDE.md).

O `experiments/bancada_v2.py` de um arquivo só foi partido aqui, um módulo por assunto, sem mudar uma linha de lógica
(tools/dividir_bancada.py; a prova pela AST em docs/historico/bancada_mapa.json). A porta de entrada continua sendo o
`experiments/bancada_v2.py`, que reexporta todo nome do pacote: `import bancada_v2 as bv`, `bv.X` e `bv.X = ...` valem como antes.

  faixas.py         as sementes dos testes, as bases, as faixas reservadas e queimadas, os prefixos e as unidades derivadas
  mundos.py         as condições, os mundos, os eventos do mundo, o corpo por regime, os efeitos das frutas e o calendário
  bracos.py         os sinais e filtros, os pontos do aprendiz, os braços, os nós pendentes, a montagem e a PoliticaDoBraco
  vida.py           a especificação e o resultado de uma vida, o filtro do log, as contagens e o resumo do motor
  regras_mundo.py   o tapa na fruta X, as regras e os informantes do mundo, as vidas pelo mundo e o registro da medição
  medidas.py        as medidas que não são métodos da Bancada: o banheiro, a rede de si, as sondas e as tabelas
  nucleo.py         a classe Bancada, inteira (SA-4: partir em mixins é outra passada)
  config.py         a validação da config, o teto de pesos, a rede da config e a bancada da config
  rodar.py          gravar, o sha256, o meta, rodar e a linha de comando (main)
  grupo.py          dois pets: a bancada do grupo
  passo0.py         o passo 0 do corpo
  pet_que_pensa.py  o pet que pensa (J5): a bancada

A ordem de importação é a desta tabela. Cada módulo importa no topo só o que usa na hora da definição; o que só roda dentro das
funções é importado no fim do módulo, depois das definições, e assim o pacote não tem importação circular.

Um PR que mexe na bancada mexe no módulo do assunto. Um nome de topo novo pede uma linha no MAPA de tools/dividir_bancada.py só se a
divisão tiver de ser refeita (por exemplo, para absorver um PR que ainda mexeu no arquivo de um só).
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))


def sha256_do_pacote() -> str:
    """O sha256 do código da bancada, para o meta das runs: a fachada (`experiments/bancada_v2.py`) e todo `.py` deste pacote, em ordem
    de nome, cada um com o caminho relativo antes do conteúdo (mudar, tirar ou pôr um arquivo muda o sha256)."""
    import hashlib
    arquivos = [RAIZ / "experiments" / "bancada_v2.py", *sorted(Path(__file__).resolve().parent.glob("*.py"))]
    h = hashlib.sha256()
    for caminho in arquivos:
        h.update(caminho.relative_to(RAIZ).as_posix().encode("utf-8") + b"\0" + caminho.read_bytes() + b"\0")
    return h.hexdigest()


MODULOS = ("faixas", "mundos", "bracos", "vida", "regras_mundo", "medidas", "nucleo", "config", "rodar", "grupo", "passo0",
           "pet_que_pensa")

from . import faixas, mundos, bracos, vida, regras_mundo, medidas, nucleo  # noqa: E402,F401
from . import config, rodar, grupo, passo0, pet_que_pensa  # noqa: E402,F401


def instalar_fachada(fachada) -> None:
    """Põe na fachada (o módulo `bancada_v2`) todo nome de topo dos módulos, como era no arquivo de um só, e faz a atribuição na fachada
    valer também nos módulos: `bv.X = ...` (e o monkeypatch dos testes) troca X em todo módulo que tem o mesmo objeto com o mesmo nome,
    como trocava no arquivo de um só. Dois módulos com o mesmo nome para objetos diferentes falham alto."""
    import types
    modulos = [sys.modules[f"{__name__}.{m}"] for m in MODULOS]
    nada = object()
    for m in modulos:
        for nome, valor in vars(m).items():
            if nome.startswith("__") or nome in ("RAIZ", "sha256_do_pacote"):   # os nomes do __init__, não da bancada
                continue
            atual = fachada.__dict__.get(nome, nada)
            if atual is not nada and atual is not valor:
                raise RuntimeError(f"o nome {nome} tem dois objetos diferentes na bancada")
            fachada.__dict__[nome] = valor

    class Fachada(types.ModuleType):
        def __setattr__(self, nome, valor):
            if not nome.startswith("__"):
                antes = self.__dict__.get(nome, nada)
                for m in modulos:
                    if antes is not nada and m.__dict__.get(nome, nada) is antes:
                        setattr(m, nome, valor)
            super().__setattr__(nome, valor)

        def __delattr__(self, nome):
            antes = self.__dict__.get(nome, nada)
            for m in modulos:
                if antes is not nada and m.__dict__.get(nome, nada) is antes:
                    delattr(m, nome)
            super().__delattr__(nome)

    fachada.__class__ = Fachada
