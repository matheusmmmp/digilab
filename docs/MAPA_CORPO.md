# MAPA DO CORPO — fome, energia e as ações que as satisfazem (C0)

**Status: APROVADO pelo Matheus em 2026-11-18** ("Aprovado", no CHECKPOINT C1): o mapa e a prioridade da seção 8. Nenhum código mudou, e
nenhuma vida rodou para este documento.

Escrito em 2026-11-18 por Claude Code (Opus 5.5, sessão lateral da CORPO_ACOPLAMENTO), no branch `v3-corpo-mapa`, sobre a `origin/main` em
**`8c6d17ae`** (o merge do #996). As linhas citadas são desse commit. Os números de comportamento vêm da sonda da etapa 1 da
[TAREFA_V3_CORPO_ACOPLAMENTO.md](TAREFA_V3_CORPO_ACOPLAMENTO.md) (seção 9; o artefato `artifacts_v3_corpo_acoplamento/sonda.json`, sha256
`f4f5962c…`, 120 vidas nas sementes dos testes). Nenhum número novo foi medido aqui.

## 0. Que corpo é este

- **O corpo do jogo é o v11:** `CCO_V11` (`web/app/motor/constantes.ts:802-806`), montado em `web/app/motor/corpo.ts:112`. Ele liga a
  digestão, a vida, os drives novos, os gestos e o metabolismo. Ele não tem banheiro, paladar nem mundo. Sobre os padrões, ele troca:
  - o `tedio_sobe` para 900 e o `solidao_sobe` para 450;
  - o `estresse_divisor` para 128;
  - o gasto basal para 300 acordado e 150 dormindo;
  - o gasto das atividades para 4/5.
- **O espelho Python** não tem uma constante com esse nome: é a `CONFIG_CORPO_METABOLISMO` (`digilab/config.py:1776`) sobre a `ConfigCorpo`
  (`digilab/config.py:1520-1627`), com os mesmos campos trocados (o ponto vem de `experiments/exportar_gabarito_lobos.py:66,82-92`).
- **O corpo das vidas de pesquisa** (a C4, a VALUATION, a A1) é o mesmo, com o mundo: a bancada o monta em
  `experiments/bancada/nucleo.py:197-211`. Com o mundo, o pet come pelo mapa (`estimulo_consumo_mundo`), e não pela `AcaoPet.COMER`.
- **A paridade:** os valores do Python e do TS saem iguais em todas as tabelas abaixo. O Python foi conferido executando o `taxas_de` e o
  `grafo_do_corpo` com a config do v11, e o TS foi conferido pela leitura do código.
- **A chave da etapa 2** (a `ConfigAcoplamentoCorpo`, `digilab/config.py:1715-1742`; `web/app/motor/corpo.ts:125-126`) está desligada por
  padrão, e nada abaixo a supõe ligada.

## 1. Os químicos e o que o cérebro lê

Todos os químicos vão de 0 a C = 450 000. O receptor sai em [0, S], com S = 1 024 (`digilab/config.py:1539`).

| químico | o receptor | a leitura |
|---|---|---|
| fome | `fome` | o drive: S − q·S/C |
| cansaco | **`energia`** | S − q·S/C: o cansaço é a falta da energia (`digilab/corpo.py:1272-1285`; `web/app/motor/corpo.ts:1063-1073`) |
| tristeza | `humor` | o drive |
| desconforto | `higiene` | o drive. A sujeira é um contador do Estado, com emissor próprio |
| dano | `saude` | o drive |
| tedio, solidao, estresse, dor, susto | o nome do químico | a falta: q·S/C |
| alimento (o estômago), combustivel, reserva, vida | **nenhum** | o cérebro não lê o combustível |

**Os limiares que o cérebro usa:**
- **A energia baixa:** o receptor `energia` abaixo de `lambda_sono` = S/4 = 256 (`digilab/config.py:2985`;
  `web/app/motor/digibrain/constantes.ts:32`), ou seja, o cansaço acima de 3C/4.
- **A fome urgente:** a urgência do M-AFETO acima de `urgencia_lambda` = 512. A urgência é `clamp(a·falta + b·max(0, falta − λ), 0, S)`, com
  a = 512, b = 1 536 e λ = 512 (`digilab/digibrain/afeto.py:95-97`; `web/app/motor/digibrain/afeto.ts:69-71`; os valores em
  `digilab/config.py:2952-2954` e `web/app/motor/digibrain/constantes.ts:54-56`).
- **A privação** (uma sentinela, não um químico): a fome, o desconforto ou o cansaço acima de C − 0,15 C = 382 500
  (`digilab/corpo.py:468,1167`; `web/app/motor/corpo.ts:219,973`).
- **A falta de combustível:** o combustível abaixo de `falta_limiar` = C/4 = 112 500 (`digilab/config.py:1605`;
  `web/app/motor/constantes.ts:792`).

## 2. O que muda a cada tick

O grafo fica em `digilab/corpo.py:528-562` e em `web/app/motor/corpo.ts:588-617`. A ordem do tick (`digilab/corpo.py:1185-1249`;
`web/app/motor/corpo.ts:991-1035`) é:
1. a digestão;
2. a fase 1, somada e cortada em [0, C];
3. o armazenamento e a mobilização da reserva;
4. a fase 2, sobre os valores da fase 1;
5. as meias-vidas.

| emissor | químico | por tick | quando | Python | TS |
|---|---|---|---|---|---|
| `fome_tick` | fome | **+375** | sempre, acordado e dormindo | `corpo.py:529` | `corpo.ts:589` |
| `cansaco_dia` | cansaco | **+500** | acordado, de dia | `corpo.py:535` | `corpo.ts:595` |
| `cansaco_noite` | cansaco | **+900** | acordado, de noite (o tick do dia ≥ 1 320 ou < 420) | `corpo.py:534` | `corpo.ts:594` |
| `cansaco_dormindo` | cansaco | **−1 875** | dormindo | `corpo.py:533` | `corpo.ts:593` |
| `gasto_basal_acordado` | combustivel | **−300** | acordado | `corpo.py:545` | `corpo.ts:601` |
| `gasto_basal_dormindo` | combustivel | **−150** | dormindo | `corpo.py:546` | `corpo.ts:602` |
| **`falta_combustivel` (a ponte ME-1)** | **cansaco** | **+500** | o combustível abaixo de C/4 (fase 2) | `corpo.py:562` | `corpo.ts:616` |
| `desconforto_tick` | desconforto | +300 | sempre | `corpo.py:530` | `corpo.ts:590` |
| `desconforto_sujeira` | desconforto | +36 por sujeira | sempre | `corpo.py:531` | `corpo.ts:591` |
| `tristeza_tick` | tristeza | +375 | sempre | `corpo.py:532` | `corpo.ts:592` |
| `tedio_sobe`, `solidao_sobe` | tedio, solidao | +900, +450 | acordado | `corpo.py:539-540` | `corpo.ts:598-599` |
| `vida_tick` | vida | −11 | sempre | `corpo.py:538` | `corpo.ts:597` |
| `dano_privacao` / `dano_cura` | dano | +225 / −150 | com / sem privação (fase 2) | `corpo.py:548-549` | `corpo.ts:605-606` |
| `estresse_drives` | estresse | +Σ max(0, q − 337 500) / 128 sobre fome, desconforto, cansaco, tedio, solidao e dor | fase 2 | `corpo.py:552` | `corpo.ts:609` |

**A reserva:** acima de 3C/4, o combustível vai à reserva, até 375 por tick; abaixo de C/2, ele volta dela, até 375 por tick
(`digilab/config.py:1601-1604`). A vida começa com o combustível em C/2 e a reserva em C/4.

## 3. O que cada ação faz

Os valores saem do `taxas_de` (`digilab/corpo.py:430-447`; `web/app/motor/corpo.ts:188-203`) e da `ConfigCorpo`
(`digilab/config.py:1543-1547`). O combustível das atividades é o ME-3, com o fator 4/5 do v11.

**As ações do pet** (`acao_pet`: `digilab/corpo.py:867`; `web/app/motor/corpo.ts:886`):

| ação | fome | cansaco | combustivel | outros |
|---|---|---|---|---|
| ocioso, chamar_atencao, ir_tv | — | — | — | — |
| **dormir** | — (o `fome_tick` segue) | só pelo emissor `cansaco_dormindo` (−1 875 por tick) | só pelo basal dormindo (−150 por tick) | — |
| **comer** (sem mundo) | **−22 500**, pelo estômago | — | **+** pela digestão (seção 4) | — |
| **brincar** | — | **+9 000** | **−7 200** | tristeza −56 250; o tédio cai até −45 000 (−135 000 com a bola) |
| **explorar** | — | **+6 750** | **−5 400** | tristeza −4 500; o tédio cai até −90 000 |
| emburrar | — | — | — | tristeza +4 500 |

**As ações do dono** (`acao_dono`: `digilab/corpo.py:802`; `web/app/motor/corpo.ts:835`; o v11 aceita as cinco primeiras):

| ação | fome | cansaco | combustivel | outros |
|---|---|---|---|---|
| alimentar | −202 500, pelo estômago | — | + pela digestão | a sujeira, sorteada |
| **brincar (o dono)** | **+22 500** | **+36 000** | **−28 800** | tristeza −112 500; o tédio cai até −90 000 |
| limpar | — | — | — | desconforto −270 000 |
| acariciar | — | — | — | tristeza −27 000; solidão −180 000 e estresse −90 000, cada um × (C − susto)/C |
| tapa | — | — | — | dor +90 000, susto +180 000, estresse +45 000 |
| elogiar, repreender | — | — | — | só no Python: tristeza −45 000 e +54 000; o TS do v11 as recusa |

**Os estímulos do mundo:**
- **o pet come a ração madura:** −202 500 na fome, pelo estômago, como o alimentar do dono (`estimulo_consumo_mundo`:
  `digilab/corpo.py:931`; `web/app/motor/corpo.ts:928`);
- **a fruta madura:** −67 500 na fome, e a tristeza cai pelo efeito da fruta;
- **a comida podre:** a tristeza sobe 45 000;
- **o andar:** o cansaço sobe 75 por subunidade andada, e o combustível cai 4/5 disso (`estimulo_andar`: `digilab/corpo.py:918`;
  `web/app/motor/corpo.ts:916`; a taxa em `digilab/config.py:1830`);
- **a bola:** −67 500 na tristeza.

**As ações que mexem na fome e no cansaço ao mesmo tempo:**
- **Pelo caminho direto, só o brincar do dono:** +22 500 na fome e +36 000 no cansaço, no mesmo `_somar`.
- **Nenhuma ação do pet mexe nas duas diretamente.** O brincar e o explorar mexem no cansaço e no combustível; o comer mexe na fome e no
  combustível.
- **Pelo combustível, todas:**
  - toda ação que gasta combustível (o basal, as atividades, o andar) aproxima a ponte ME-1;
  - abaixo de C/4, a ponte soma +500 por tick no cansaço;
  - só o comer devolve o combustível, e só pela digestão.

## 4. A digestão

- **A comida vai ao estômago** (`digilab/corpo.py:523-526`; `web/app/motor/corpo.ts:582-587`): o −fome da ação vira +alimento.
- **A reação** (`digilab/corpo.py:514,989`; `web/app/motor/corpo.ts:573,947`) tira t = min(alimento, fome, o teto por tick) do alimento e da
  fome, e põe t no combustível (a conversão é 1/1).
- **Com a fome em zero, o alimento que sobra é descartado** (`digilab/corpo.py:1006-1008`; `web/app/motor/corpo.ts:965-968`).
- **O efeito:** o combustível só entra pelo que a fome deixou subir. O teto da conversão é o relógio da fome, 375 por tick, ou 1,200 C por
  dia.
- **A fome não lê o combustível (ME-5):** o pet não sente o déficit como fome.

## 5. O reflexo do sono

- **A regra:** a energia abaixo de `lambda_sono` dispara o reflexo, sem rng (`digilab/digibrain/arb.py:121-141`;
  `web/app/motor/digibrain/arb.ts:102-106`). Ele é avaliado uma vez por decisão, no M-ADAPT (`digilab/digibrain/adapt.py:352`;
  `web/app/motor/digibrain/adapt.ts:208`).
- **O efeito é um override, não um peso:** com o reflexo, o `escolher` pula o sorteio e pega a unidade `dormir`
  (`digilab/digibrain/arb.py:167-170`; `web/app/motor/digibrain/arb.ts:134-139`).
  - Os pesos do sorteio são `a + g_exp·ε` para a unidade com ativação a > 0, e 0 para as outras (`digilab/digibrain/arb.py:98-100`;
    `web/app/motor/digibrain/arb.ts:81`).
  - A fome urgente não entra na regra: o pet com a energia baixa e a fome urgente dorme.
- **Os desvios que já existem, atrás de chave:**
  - **o sono que segura:** o reflexo também vale com o pet dormindo e a energia abaixo de `lambda_acordar`, sem a fome urgente;
  - **o conserto da VALUATION** (`ConfigConsertoValuation.guarda_fome_reflexo`, `digilab/config.py:3352-3376`): a fome urgente tira o
    reflexo. Ele **só existe no Python**, e falhou na run (seção 6).
- **Quem mais lê o reflexo como certeza:** o M-ESTADO (`web/app/motor/digibrain/adapt.ts:235`), o decodificador da fala
  (`web/app/motor/digibrain/decodificador.ts:64-93`, com `margem = S`) e as sondas (`reflexo`, `decidiu = False`).

## 6. O acoplamento, com os valores

```
            jejum (o pet não come)
           /                       \
  fome_tick +375/tick          o combustível cai: basal 300 (150 dormindo),
  (o relógio da fome)          atividades 7 200 / 5 400, andar 60/subunidade
           |                                   |
  fome urgente (urgência > 512)        combustível < C/4 → a ponte ME-1
           |                           soma +500/tick no CANSAÇO
           |                                   |
           |                       energia < S/4 → o REFLEXO dorme (override)
           \                                   /
          as duas ao mesmo tempo: 0,759 das decisões com a energia baixa
          (0,635 na faixa da VALUATION; RESULTADO_V3_VALUATION_CONSERTO.md:54)
```

**O que a sonda da etapa 1 mediu** (a seção 9.2 da tarefa; `sonda.json`, `agregado.REL.todas`, as sementes dos testes):

| medida | valor |
|---|---|
| a fome urgente na energia baixa (a coincidência) | **0,759** (0,248 na energia boa) |
| a fonte que mais pôs cansaço na janela, nas decisões com as duas | a ponte ME-1 em **0,767**; o tempo acordado em 0,222; as atividades em 0,011; o andar em 0 |
| o combustível abaixo de C/4, nas decisões com as duas | **0,974** |
| a fome já urgente na entrada do trecho cansado | 0,993 |
| o cansaço que entra por dia | a ponte **0,829 C**, as atividades 0,634, o basal do dia 0,563, o da noite 0,526, o andar 0,279 |
| o combustível por dia | a digestão converte 1,041 C; 0,386 C de comida são descartados com a fome em zero |
| o teto da conversão contra a demanda | 1,200 contra 1,467 C por dia: **o déficit é de 0,267 C por dia, mesmo comendo tudo o que a fome deixa** |

**As três respostas que a C0 pede:**
- **Quando a fome cai** (o pet come), o combustível sobe pela digestão. O cansaço não cai direto, mas a ponte desliga quando o
  combustível passa de C/4, e o cansaço deixa de subir +500 por tick.
- **Quando a energia cai** (o cansaço sobe), a fome não muda: nenhum emissor lê o cansaço. O que muda é o comportamento: abaixo de S/4, o
  reflexo força o dormir, e o pet que dorme não come, então a fome segue subindo +375 por tick.
- **As ações que mexem nas duas:** diretamente, só o brincar do dono. Pelo combustível, todas as que gastam.

**A conclusão do mapa:** a coincidência é, sobretudo, uma causa comum. O jejum sobe a fome pelo relógio e sobe o cansaço pela ponte. Duas
peças fecham o laço:
- **o reflexo** é um override, então o pet com as duas dorme e não come;
- **a digestão** só converte o que a fome deixa, então o combustível não se recupera nem com o pet comendo o que pode.

## 7. As opções de redesenho

As C1 a C5 são as do pedido. A D e a E são da etapa 1 (a seção 10 da tarefa, opções D e E). A A, a B e a C de lá são a C1, a C2 e a C3
daqui. Comum a todas:
- cada uma entra atrás de uma chave desligada, com o gabarito das vidas de hoje gravado antes, num commit próprio;
- a mudança vai ao Python e ao TS juntos, com a paridade;
- ligada, ela não vale para a calibração do cuidado (E1 e E2) nem para o I-PAD da LONGE_GEOMETRIA (+0,071, que vem do sono) sem medir de
  novo.

O custo conta as linhas de código e os arquivos tocados, sem os testes e os gabaritos, que toda opção ganha.

| opção | o que muda | a predição, falsificável | o que o mapa diz antes de medir | custo |
|---|---|---|---|---|
| **C1. comer restaura a energia** | o consumo da comida madura também tira cansaço (um efeito novo no `estimulo_consumo_mundo` e no `comer`) | o pet resolve a tensão com uma ação: a coincidência cai, e o reflexo dispara menos depois de comer | trata o sintoma. Em 0,577 das decisões com as duas, a fome está no teto: falta a comida, não o efeito dela. O cansaço deixa de querer dizer "precisa dormir" | baixo: ~15 linhas, 4 arquivos (`config.py`, `corpo.py`, `corpo.ts`, `constantes.ts`) |
| **C2. dormir desacelera a fome** | o `fome_tick` vira dois emissores, acordado e dormindo, o dormindo menor | menos fome urgente ao acordar; a coincidência cai | **a premissa não vale:** o teto da conversão é o relógio da fome. Com metade da fome dormindo, ele cairia de 1,200 para cerca de 0,921 C por dia (1,2 × (1 − 0,465/2)), abaixo da demanda de 1,467: o déficit cresce, e a ponte liga mais | baixo: ~20 linhas, os mesmos 4 arquivos |
| **C3. uma ação "descansar + beliscar"** | uma `AcaoPet` nova, com metade do efeito do comer e do dormir | o pet com as duas escolhe a ação nova, e a privação e a exaustão caem juntas | não fecha o déficit, e só ajuda se houver comida perto. É a mais cara: muda o enum do log | **alto:** ~200+ linhas em 10+ arquivos (`digilab/events.py`, o enum do log, as unidades do M-ARB, o M-MEM, o M-IMPULSO, a web, o glossário, os gabaritos do cérebro); o `engine.py` não muda |
| **C4. desacoplar as taxas** | o brincar baixa a energia mas não a fome; o explorar baixa a fome mas não a energia | o pet que brinca não fica com fome, e a coincidência cai | **a premissa não vale hoje:** nenhuma ação do pet mexe na fome diretamente (seção 3). O caminho é o combustível (o ME-3: 7 200 e 5 400 por ação), e "desacoplar" seria tirar o gasto do ME-3, o que só esconde o gasto | baixo no código (~10 linhas, 3 arquivos); a leitura muda o metabolismo |
| **C5. o reflexo suave e o ajuste de `lambda_sono`** | o reflexo soma peso na unidade `dormir`, em vez de pular o sorteio; o `lambda_sono` vira um parâmetro da chave | com a fome urgente, o pet às vezes come em vez de dormir: as refeições sobem, e a exaustão sobe menos que no conserto da VALUATION | ataca o laço do comportamento, não a causa. O conserto da VALUATION (tirar o reflexo com a fome urgente) falhou: +0,106 nos episódios fechados e +0,195 na exaustão (`RESULTADO_V3_VALUATION_CONSERTO.md:34,37`). O suave é um meio-termo entre o reflexo e esse conserto, e pode cair entre os dois | médio: ~40 linhas em 6 arquivos (`arb.py`, `arb.ts`, `config.py`, `constantes.ts` do digibrain, `decodificador.ts`, as sondas); os gabaritos do cérebro ganham uma seção |
| **D. a falta de combustível sobe a fome, não o cansaço** | a ponte ME-1 troca de alvo: abaixo de C/4, +500 na fome em vez de +500 no cansaço | a coincidência cai, porque a maior fonte de cansaço some; a fome sobe mais quando o combustível falta, e o teto da conversão sobe com ela | **já está atrás da chave** (`ConfigAcoplamentoCorpo`, #995). Na sonda, as decisões com as duas caíram 30 % (0,150 → 0,105 das decisões), mas a fração condicional não (0,759 → 0,761), e o pet dormiu menos (0,465 → 0,375 dos ticks). **A run com o plano aprovado está rodando** (o `PLANO_ANALISE_V3_CORPO_ACOPLAMENTO.md`, faixa 100101…100505) | feito: 1 linha do grafo em cada língua |
| **E. a digestão converte a comida inteira** | o alimento vai ao combustível pela quantidade comida; a fome cai como hoje | o déficit quase fecha: 1,041 + 0,386 = 1,427 contra 1,467 C por dia; a ponte liga menos no pet que come | a ponte segue ligada no pet que não come (o `longe_fixo`). Fecha o déficit sem tirar a ponte, então combina com a D | médio: ~30 linhas, 4 arquivos; a contabilidade do metabolismo muda |

## 8. A prioridade (APROVADA no CHECKPOINT C1)

O critério é o triplo do pedido: o forrageio, o bem-estar (a privação e a exaustão) e o substrato social. A ordem vem do mapa e da sonda,
sem simular.

1. **A D, primeiro: a run já roda.** É a única que ataca a causa principal (a ponte, a classe de 0,767). O resultado dela decide o resto:
   - **se a D passar** (menos conflitos, sem piorar a privação, a exaustão e a taxa por episódio), as próximas se medem sobre ela;
   - **se ela falhar,** o plano da C1 mede as outras contra o corpo de hoje, e a D fica registrada como falha.
2. **A E, junto da D ou sobre ela.** A E fecha o déficit, e a D tira a ponte: são as duas pontas da causa comum. Sozinha, a E deixa a ponte
   ligada no pet que não come.
3. **A C5, como o braço do comportamento.** O reflexo em override é o que transforma a coincidência em sono (a V2 achou que ele troca 13
   intenções de comer por vida, `RESULTADO_V3_VALUATION.md:91`). O conserto duro falhou na exaustão; o suave é a forma ainda não medida.
   Ela não muda o corpo, e um braço C5 sobre a D separa o corpo do comportamento.
4. **A C1, só como controle do sintoma.** Ela pode até subir o forrageio, mas pelo caminho que a VALUATION mostrou perigoso: o pet descansa
   comendo, e o cansaço perde o sentido.
5. **A C2 e a C4: não testar.** As duas têm a premissa contra o mapa (a C2 aumenta o déficit; a C4 não tem o que desacoplar no caminho
   direto). Testá-las queima faixa numa predição que o mapa já nega.
6. **A C3: não testar agora.** É a mais cara (o enum do log), não fecha o déficit, e a D e a E fazem o mesmo papel mais barato.

**A recomendação para a C1:** braços D, D + E e D + C5, contra o corpo de hoje, se a run da D passar; ou E, C5 e C1 contra o corpo de hoje,
se ela falhar. **O custo de errar:** a ordem é uma leitura do mapa, não uma medida. Se a sonda estiver errada sobre a causa (ela não é
contrafactual, a seção 9.4 da tarefa), a C2 e a C4 descartadas podiam ter efeito.

## 9. O que o pedido traz e o mapa não confirma

Conferido em 2026-11-18 na `origin/main` (`8c6d17ae`):
- **A A1, a V2 e a V3 confirmam** (`RESULTADO_V3_BASELINE_TRIVIAL.md:47,69-70`; `RESULTADO_V3_VALUATION.md:7,42-47,64-65,91`;
  `RESULTADO_V3_VALUATION_CONSERTO.md:7,34,37,54`). Duas ressalvas:
  - o "0,715 > 0,645" junta duas runs com sementes diferentes, e o próprio resultado o chama "só descritivo" (`RESULTADO_V3_VALUATION.md:94`);
  - o "#973" é o merge do `v3-valuation-v5`, que levou a V2 até a V5 da VALUATION, e não a SOCIAL_PAR.
- **A SOCIAL_PAR A0 e B0 não têm resultado na `main`.** O que existe é o piloto (102101…102505, o registro D-SP-33): o B0 sai "inconclusivo
  por premissa" (a bola quase não é chutada). Os números "≈ 0", "~10 decisões até o reencontro", "P dorme em metade dos t0" e "a CO7 age
  em 0,5 %" não aparecem em nenhum documento da `main`. A run A0 rodou na máquina às 15:46 de 2026-11-18; o resultado dela, se existe, está
  fora da `main`.
- **"5 932 testes"** não aparece em nenhum documento. O #989 existe (o conserto do `test_fala_livre`).

## 10. O que este mapa não demonstra

- **Nenhuma predição da seção 7 foi medida,** fora a D (descritiva, na sonda da etapa 2) e o conserto da VALUATION (a run dele).
- **Os custos em linhas são estimativas** de quem leu o código, não contagens de um diff.
- **O corpo do jogo com um dono de verdade** não foi medido: a sonda usa os quatro donos da bancada.
- **O substrato social** (a bola chutada, o reencontro) não entra no mapa: nada no corpo de hoje o liga à fome ou à energia diretamente.
  O que o corpo pode mudar é o tempo livre: a fração das decisões fora do comer e do dormir.
