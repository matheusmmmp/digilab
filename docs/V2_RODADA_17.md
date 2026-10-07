# V2, rodada 17: o código do mundo físico e do corpo

Aberta em 2026-10-07 pelo coordenador, por decisão do Matheus ("segue com a recomendação"), depois do merge do plano do corpo (#211).

## 1. O que já está decidido

- **As tarefas:**
  - `docs/TAREFA_V2_MUNDO_FISICO.md` (#206), com MF-1 a MF-4 DECIDIDAS por este PR, todas como recomendado;
  - `docs/TAREFA_V2_CORPO_DRIVES.md` (#209), com CD-1 a CD-10 decididas no #210;
  - o plano do corpo, `docs/PLANO_ANALISE_V2_CORPO_DRIVES.md` (#211), com PCD-1 a PCD-7 decididas.
- **Ficam abertas:** as decisões do plano do mundo, PMF-1 a PMF-7 (seção 4). Elas só pesam na etapa 4 do mundo (a bancada), que vem por
  último.
- **Sementes:**
  - mundo: 31101…31505 para calibração e 32101…32505 para validação;
  - corpo: 33101…33505 para calibração e 34101…34505 para validação.
- **Regras de sempre:** um PR por etapa, com o relato no corpo; o merge é do Matheus; nenhuma run de pesquisa nesta rodada (os testes usam
  101…505); a chave desligada é a vida de hoje byte a byte; os pets v1 a v10 ficam iguais; o `engine.py` não muda.

## 2. A ordem

| passo | quem | o quê | depende de |
|---|---|---|---|
| 1 | **A** | gabaritos do mundo (etapa 1) e do corpo (etapa 0, com a auditoria dos escritores de drive), num PR só | — |
| 1 | **B** | a química dos drives de hoje (corpo, etapa 1): `corpo.py` puro, sem motor | — |
| 1 | **D** | as faixas 31101…34505 em `FAIXAS_RESERVADAS` | — |
| 2 | A | o mundo físico (mundo, etapa 2) | o passo 1 do A |
| 3 | A | o corpo no motor (corpo, etapa 2) | o passo 2 do A e a etapa 1 do B |
| 3 | B | o instinto e os cérebros no mundo (mundo, etapa 3) | o passo 2 do A |
| depois | A, B, D | os órgãos, o cérebro A no corpo, os drives novos e os gestos, a web e a bancada | a ordem das seções 9 e 14 das tarefas |

Os gabaritos vêm **antes** de qualquer mudança, num commit próprio, como nas rodadas anteriores. Em `config.py` só entram classes novas
no fim: o conflito entre o A e o B se resolve por acréscimo.

## 3. Os prompts

### 3.1 W-GABARITOS (chat A)

> Você é o worker A da V2 do DigiLab. Em D:\Trab\digilab\v2: git fetch origin; git worktree add ..\v2-gabaritos-r17 -b v2-gabaritos-r17
> origin/main. Leia docs/V2_RODADA_17.md, docs/TAREFA_V2_MUNDO_FISICO.md (seções 9 e 10) e docs/TAREFA_V2_CORPO_DRIVES.md (seções 2, 12 e
> 14). Faça só o passo 1 do A, sem mudar nenhum código de motor:
> - `tests/gabaritos/mundo_vidas_de_hoje.json`: vidas de hoje (P0, P1, P3 nos mundos padrao, bola, descasado, iguais_frutas), gravadas com
>   o código da main, por um script `tests/gabarito_mundo.py`, como os gabaritos das rodadas anteriores;
> - `tests/gabaritos/corpo_vidas_de_hoje.json`, pelo mesmo caminho (`tests/gabarito_corpo.py`), cobrindo os motores que o corpo vai tocar
>   (MotorComFeedback, MotorAmbiente, MotorFrutasMundo);
> - a auditoria da seção 2 do corpo: a lista de todo lugar que escreve um drive do `Estado` (arquivo, função, drive, valor), no corpo do PR.
> Teste que confere os dois gabaritos contra o código atual. Só as sementes dos testes. Entregue um PR e pare; o relato vai no corpo do PR.

### 3.2 W-CORPO-QUIMICA (chat B)

> Você é o worker B da V2 do DigiLab. Em D:\Trab\digilab\v2: git fetch origin; git worktree add ..\v2-corpo-quimica -b v2-corpo-quimica
> origin/main. Leia docs/V2_RODADA_17.md e docs/TAREFA_V2_CORPO_DRIVES.md inteiro (CD-1 a CD-10 decididas). Faça a etapa 1 da seção 14:
> - `digilab/corpo.py` novo: `Corpo` com os cinco químicos da seção 4, o tick na ordem de hoje, os estímulos de hoje convertidos, o dano
>   por receptor de privação, o corte em [0, C] e os receptores na escala S; em inteiros, C = 450000, sem motor e sem rng;
> - `ConfigCorpo` no fim de `config.py`, desligada por padrão, com as sub-chaves da seção 2 (só a base funciona nesta etapa; as outras
>   falham alto se ligadas);
> - `tests/test_corpo_quimica.py`: o G-HOJE (a) em malha aberta (com as mesmas ações forçadas, o drive lido pela química fica dentro da
>   tolerância da seção 3 em relação ao float de hoje, tick a tick), a derivação dos k_h, o exemplo do tick 660 da seção 3;
> - o exportador do gabarito para a paridade com o TS.
> Não toque em motor, `engine.py`, `lobos.py` nem na web. Só as sementes dos testes. Entregue um PR e pare; o relato vai no corpo do PR.

### 3.3 W-FAIXAS-R17 (chat D)

> Você é o worker D da V2 do DigiLab. Em D:\Trab\digilab\v2: git fetch origin; git worktree add ..\v2-faixas-r17 -b v2-faixas-r17
> origin/main. Leia docs/V2_RODADA_17.md, docs/PLANO_ANALISE_V2_MUNDO_FISICO.md (seção das sementes) e docs/PLANO_ANALISE_V2_CORPO_DRIVES.md
> (seção das sementes). Em `experiments/bancada_v2.py`, acrescente a `FAIXAS_RESERVADAS` as quatro faixas (31101…31505 e 32101…32505, mundo
> físico; 33101…33505 e 34101…34505, corpo), com a fonte, e os prefixos de unidade dos dois planos em `PREFIXOS_UNIDADES`, se o plano
> pedir unidades derivadas. O teste de faixas confere que nenhuma colide com as de antes nem com as configs de `experiments/configs/`. Nada
> mais. Entregue um PR e pare; o relato vai no corpo do PR.

## 4. Decisão aberta: PMF-2, o contraste primário do mundo

O plano do mundo (#206) usa como primário **P0 − P1ac**: o P1 acoplado em malha aberta ao cuidado do P0. A validação única mostrou que o
acoplado em malha aberta cuida pior que o original, porque o cuidado gravado não reage ao pet que o recebe. Comparar um P0 em malha fechada
com um P1 acoplado pode pôr no contraste a desvantagem do acoplado, e não o efeito do mundo.

A segunda revisão de literatura (`docs/referencias/F_REVISAO_V2_SEIS_PERGUNTAS.md`, P2) sustenta o risco (Church 1964; Kimmel e Terrant
1968, página 1). Ela também registra que a magnitude da objeção é contestada.

**Recomendação:** revisar o PMF-2 por adendo, antes da calibração, como o plano do corpo fez (PCD-3). Duas formas:
- **o primário em malha fechada** (P0 − P1, com o mesmo dono reagindo), mais o par acoplado à mesma fonte como secundário;
- **o acoplado recíproco** da revisão, com dois canais dentro do mesmo pet.

O adendo é do chat C, e só precisa estar pronto antes da etapa 4 do mundo.

**Custo de errar:** manter o primário como está pode dar uma diferença que vem do acoplado e ler essa diferença como efeito da busca.
