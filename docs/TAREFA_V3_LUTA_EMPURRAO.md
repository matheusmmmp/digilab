# TAREFA V3 — LUTA_EMPURRAO (2026-11-06)

> **SUBSTITUÍDO** pela [`docs/TAREFA_V3_LUTA_POC.md`](TAREFA_V3_LUTA_POC.md) (2026-11-08): a luta do jogo é a simulação da POC. O combate por turnos saiu do jogo na LP4 (2026-11-10); este documento fica como registro.

Coordenador: o Gerente da missão SPRITES_GERACAO (Claude Code). Worker: Claude Code, Opus 5.5. Worktree e branch: `v3-luta-empurrao`.
Status: EM ANDAMENTO (as EMP-1 a EMP-8 DECIDIDAS pelo Matheus em 2026-11-06, pela recomendação; seção 8).

Categoria: arquitetura. Origem: Matheus, 2026-11-06. O pedido foi o empurrão de verdade no motor da luta em tempo real: quem leva o golpe
vai para trás e, no pesado, cai. Nas palavras dele:
- "quando um personagem vai fazer um golpe que necessita de movimentação, por exemplo, uma investida, ele efetua essa investida mesmo, e
  quando o outro tomar, ele tomar e ele cair para trás, né? O impacto da força, jogar ele para trás";
- depois de ver as duas opções (só no desenho, ou de verdade no motor): "Pode implementar o motor também dentro do de verdade no jogo."

## 1. Pergunta

Como pôr na luta em tempo real um empurrão que siga a força do golpe, com queda no golpe pesado, sem mudar nenhuma luta das versões de
hoje? E quanto isso muda o equilíbrio medido na rodada de 2026-10-30?

A tarefa é de produto (a trilha B, batalha), não uma hipótese de pesquisa. A medição de equilíbrio da etapa 4 segue o método da rodada
(`docs/PLANO_EQUILIBRIO_COMBATE_TR.md`).

## 2. Depende de

- **O motor da `main`:** `web/app/motor/combate_tr/` (`luta.ts`, `constantes_tr.ts`, `controlador.ts`, `adaptador.ts`) e a espec
  `docs/ESPEC_COMBATE_TR.md`. **Não há espelho no Python:** a luta em tempo real só existe no TS (o `digilab/` não tem `combate_tr`), então
  não há paridade a manter.
- **As decisões da seção 8**, antes da etapa 3.
- **A E1 da LUTA_EFEITOS** (`v3-luta-efeitos-e1`, o impacto, que inclui um empurrão **só visual** no alvo), antes da etapa 5. As duas
  mexem em `web/app/src/telas/lutar/palcoTR/desenhoTR.ts`. A etapa 5 começa depois do merge da E1, sobre ela.

## 3. Mudança mínima

### 3.1 O que o motor faz hoje (lido na `main` em 2026-11-06)

- **A investida já se desloca:** a arrancada vai a 500 px/s (v14; 420 na v13) até o contato (44 px entre os centros), e o golpe sai ali.
  Quando a defesa a apara, quem investiu volta ao `x0`, de onde saiu (`luta.ts`, `passoTR`).
- **O `empurrao` de hoje é de quem leva o dano corpo a corpo, não do atacante.** Em `aplicarDanos`, todo lado que recebeu dano marcado
  `cac` vai `empurrao` px para trás (`s.x -= rumo(l) * S.C.empurrao`, com `l` = quem recebe):
  - o alvo do golpe rápido, da finta, da investida e do pesado;
  - o atacante, quando o dano volta para ele (o parry da defesa contra o golpe rápido e o contra-golpe).

  A leitura anterior ("empurra o atacante") vinha do comentário da rodada ("afastava o atacante para fora do contato"), que descreve o
  efeito na distância, não o lado. Isso está registrado como achado (D-EMP-1, no registro).
- **Ele vale 6 px na v13 e 0 da v14 em diante** (`RELOGIO_V14`). Na fase 1 da rodada, com 6 px os pares defensivos ficavam no limite de
  tempo (o pior par a 100%; com 0, a 0,775). Ver `docs/EQUILIBRIO_COMBATE_TR.md`, fase 1.
- **O desenho já segue o `x` do motor** (`desenhoTR.ts` lê `S.L[i].x`) e já tem o clipe `Stun` para o atordoamento (`atordoadoAte`).
- **A geometria:** o chão vai de 50 a 430 px (centro 240, meia largura 190). O golpe corpo a corpo só acerta em perto (≤ 62 px); o médio
  vai até 120 px (v14), e a investida só sai dele.

### 3.2 O desenho do empurrão

Os números abaixo são **DECIDIDOS pelo Matheus em 2026-11-06 (EMP-1 a EMP-8, seção 8), SEM FONTE**: nenhum vem de medição, e a etapa 4 mede o efeito.

**A força de cada golpe** (a distância que o alvo desliza para trás quando leva o golpe em cheio):

| golpe | dano base | empurrão | derruba? |
|---|---|---|---|
| golpe rápido, finta | 8 | **0 px** (o motor não empurra; o tranco fica só no desenho, a E1) | não |
| investida | 8 | **40 px** (do contato, 44, para 84: o médio) | **sim** |
| pesado | 25 | **60 px** (do contato para 104: o médio) | **sim** |
| disparo (projétil) | 6 × 6 | **0 px** | não |

- **Por que o golpe rápido fica em 0:** com 6 px, a fase 1 da rodada mostrou as lutas defensivas presas no limite de tempo. Com 0 no leve,
  a troca curta de golpes continua como hoje, e o empurrão aparece onde o Matheus o descreveu: na investida e no golpe forte.
- **O disparo fica em 0:** o multiplicador dele (6) foi calibrado sem empurrão, e a luta de longe não muda.

**A postura de quem leva o golpe:**

| o alvo está em | empurrão | queda |
|---|---|---|
| nada, andar, recuar, carregar, marcar, preparar o pesado | inteiro | sim, se o golpe derruba |
| defender | **metade** | **não** |
| defender contra a investida (aparada) | **nenhum**; quem investiu volta ao `x0`, como hoje | não |
| esquivar | o pesado e o disparo não acertam: nenhum. O golpe rápido acerta (como hoje), e empurra pelo seu valor (0) | não |
| contra-golpe | o alvo leva o golpe reduzido como na defesa: **metade**; o dano que volta empurra o atacante pela força do golpe rápido (0) | não |
| pele dura ativa | **metade** | **não** (a pele dura já impede a interrupção do preparo; aqui ela segura a queda) |

**A queda.** Quem cai fica atordoado por **62 passos (~1 s)**: perde a ação em curso e o preparo do pesado, como na interrupção de hoje, e
não decide até levantar. O desenho usa o clipe `Stun`. **Quem está caído pode levar golpe** (sem invulnerabilidade): com 60 px de
distância, quem derrubou leva ~0,9 s andando até o contato, e o golpe rápido sai 0,4 s depois do início. Só o disparo e a investida
chegam antes de ele levantar.

**O deslize.** O empurrão não é um salto. O motor desliza o alvo para trás em **10 passos (160 ms)**, a uma velocidade constante
(a distância ÷ 10 por passo), e o desenho só lê o `x`. Durante o deslize, o movimento próprio do alvo (andar, recuar) soma ao deslize.

**A borda.** Quem é empurrado contra a cerca **para nela, e o resto do empurrão se perde** (a cerca que existe hoje, `acomodar`). Encurralar
o rival vira tática: perto da cerca, o pesado não afasta.

**A sentinela, a interrupção e a investida que acerta:** nada muda nelas. A sentinela pronta continua travando o avanço de quem avança; o
golpe rápido continua interrompendo o preparo (atordoamento de 31 passos); a investida continua saindo no contato. Se o alvo já está
atordoado e cai, vale o fim mais tarde dos dois.

**O mesmo passo.** Os golpes do mesmo passo se resolvem contra o estado do começo do passo, como hoje; os dois lados podem ser empurrados ou
cair no mesmo passo.

### 3.3 A chave e a versão

- **A chave:** os números novos viajam no relógio (`RelogioTR`), em campos novos: a força de cada golpe, a queda e o deslize. Na v13 e na
  v14 (e nas versões que lutam como ela: a v15, a v16 do laboratório e a v17) eles ficam **desligados** (força 0, sem queda), e a luta sai
  byte a byte. O `empurrao` antigo (6 na v13, 0 na v14) continua como está e só vale nessas versões.
- **A versão nova: a v18** (`VERSAO_PET` = 18; `RELOGIO_V18` = o da v14 mais o empurrão). Nenhum branch aberto reclama a 18 (conferido em
  2026-11-06). A v18 é a v17 (o cérebro trocável) com o empurrão; os pets v13 a v17 seguem vivos e lutam como hoje, e só os ovos novos
  nascem v18 (como na CV14-1).
- **O que NÃO muda:** `digilab/` (inteiro, inclusive o `engine.py`); as lutas, as assinaturas e os gabaritos v1 a v17; o combate por turnos;
  as listas, os fatores e as cartas da v14 (a v18 usa os mesmos); a E1 da LUTA_EFEITOS.

### 3.4 As etapas

Cada etapa num PR, com o merge pelo Matheus.

1. **A tarefa** (este documento, PR de arquitetura). Para aqui, até as decisões da seção 8.
2. **O gabarito das lutas de hoje**, num commit próprio, **antes** da mudança: um conjunto fixo de lutas v13 e v14 (pares de formas,
   líderes e NPCs, nas sementes de teste 101 a 505), com o resultado e um hash dos eventos passo a passo, e um teste que confere.
3. **O motor:** os campos novos no relógio, o deslize, a queda e a v18, com os testes:
   - o gabarito da etapa 2 passa sem regravar;
   - o determinismo (a mesma luta v18 dá o mesmo resultado) e o `combate_tr_sem_dom` (só `+ − × ÷`, `min` e `max`);
   - os casos da tabela 3.2 (o pesado empurra 60 e derruba; a defesa corta pela metade e segura a queda; a investida aparada não empurra;
     a cerca segura; o caído não decide até levantar);
   - um ovo novo nasce v18; o v17 abre e luta como antes.
4. **A medição de equilíbrio** com a v18, comparada com a v14 de hoje (seção 4). Se desequilibrar, volta ao Matheus com os números.
5. **O desenho:** quem leva o golpe segue o `x` do motor (o deslize), cai e levanta com o clipe `Stun` na queda, e a investida ganha rastro e
   poeira. O empurrão visual da E1 fica só no golpe sem empurrão de motor (o rápido e o disparo), para não somar dois empurrões. Antes do
   PR, capturas ou um GIF ao Matheus.

## 4. Experimento e gate (etapa 4)

- **O que mede:** todas as metas da rodada (as bancadas das fases 1 a 4, `web/app/scripts/equilibrio_tr/medir_tudo.py`), com a v18 contra a
  v14 de hoje, nas mesmas sementes e com o mesmo comando. A bancada ganha uma opção para o relógio v18.
- **As sementes:** as da calibração da rodada 2, **72101 a 72505** (DR2-2), já reservadas. É uma medição de calibração: se os números da
  seção 8 mudarem depois dela, mudam nessas sementes. As faixas de conferência (70101–70505 e 74101–74505) não são usadas.
- **A máquina:** no máximo 4 processos e uma run por vez (V3-D8). Antes da run, o plano da medição (o comando, as metas, o tempo estimado)
  vai no corpo do PR da etapa 3 ou num PR próprio.
- **O gate, PROPOSTO:**
  - nenhuma meta que passa na v14 hoje (na calibração) passa a falhar com a v18;
  - o T-1 (a duração da luta) e o T-2 (a fração de lutas no limite de tempo) são relatados lado a lado, mesmo que já falhem hoje;
  - se alguma meta piorar, a etapa para e volta ao Matheus com os números. Nenhum número da seção 8 é ajustado sem ele.
- **GPU:** não.

### 4.1 O plano da medição (registrado em 2026-11-06, antes da primeira luta da medição)

- **A faixa:** a calibração da rodada 2, `72101` a `72505`, já reservada em `experiments/bancada/faixas.py` (DR2-2). É o uso dela:
  calibração do equilíbrio do tempo real. Nenhuma faixa nova.
- **Os comandos** (em `web/app`, um depois do outro, cada um em no máximo 4 processos):
  1. antes: `python scripts/equilibrio_tr/medir_tudo.py --faixa calibracao2 --saida scripts/medicoes/equilibrio_tr/empurrao/antes`;
  2. depois: `python scripts/equilibrio_tr/medir_tudo.py --faixa calibracao2 --empurrao v18 --saida scripts/medicoes/equilibrio_tr/empurrao/depois`;
  3. a tabela: `python scripts/equilibrio_tr/resumo_metas.py scripts/medicoes/equilibrio_tr/empurrao/antes scripts/medicoes/equilibrio_tr/empurrao/depois`.
- **O que muda entre os dois:** só o `empurraoAlvo` do relógio (`--empurrao v18`, `scripts/equilibrio_tr/empurrao.ts`). As listas, os
  fatores, o aprendizado e as cartas são os da v14, nos dois (os da bancada de hoje). O "antes" roda de novo no código de hoje, em vez de
  reaproveitar a `r2_4b/`, para os dois lados saírem do mesmo código.
- **As metas:** as 29 da rodada (T-1 a T-5, F-1 a F-7, P-1 a P-4, G-1 a G-6, I-1 a I-5), lidas pelo `resumo_metas.py`.
- **O gate** (o da seção 4): nenhuma meta que passa no "antes" falha no "depois". O T-1 e o T-2 vão lado a lado. Se uma meta piorar, a
  etapa para e volta ao Matheus, sem mexer nos números da seção 8.
- **Os artefatos:** os JSON de cada bancada nas duas pastas e o `resumo.txt` com a tabela.

### 4.2 A segunda medição: a defesa sem empurrão (registrada em 2026-11-06, antes da primeira luta dela)

- **Por quê:** a primeira medição reprovou o gate (seção 9.1). O Matheus escolheu, nas palavras dele, "Testar defesa sem empurrão": a
  EMP-5 muda só na defesa (`defender`). O golpe que acerta a defesa não empurra nem derruba; o contra-golpe e a pele dura seguem cortando
  pela metade; a investida e o pesado seguem como nas EMP-1 a EMP-4 (desvio D-EMP-9).
- **O código:** `EMPURRAO_V18.defesa = 0` (o campo novo `defesa` do `EmpurraoAlvo`; `guarda` = 0,5 fica para o contra-golpe e a pele).
- **O comando** (em `web/app`, no máximo 4 processos, uma run): `python scripts/equilibrio_tr/medir_tudo.py --faixa calibracao2 --empurrao v18
  --saida scripts/medicoes/equilibrio_tr/empurrao/depois_defesa0`; a tabela:
  `python scripts/equilibrio_tr/resumo_metas.py scripts/medicoes/equilibrio_tr/empurrao/antes scripts/medicoes/equilibrio_tr/empurrao/depois_defesa0`.
- **O "antes":** o mesmo da 4.1 (`empurrao/antes/`, igual à `r2_4b`, D-EMP-6); não roda de novo, porque o código da v14 não mudou.
- **A faixa:** a mesma, `72101` a `72505` (calibração). Tempo estimado: ~7 min.
- **O gate:** o mesmo da seção 4; o pedido do Matheus nomeia F-3, G-2, G-3 e o teto do T-2. Se ainda falhar, a etapa para e volta com a
  tabela (meta, v14, v18 com a defesa sem empurrão, pior par).

### 4.3 A terceira medição: o contra-golpe também sem empurrão (registrada em 2026-11-06, antes da primeira luta dela)

- **Por quê:** a segunda medição ainda reprovou (seção 9.2). O Matheus escolheu, nas palavras dele, "Contra-golpe sem empurrão": a EMP-5
  ampliada ao contra-golpe. O golpe que acerta a defesa ou o contra-golpe não empurra nem derruba; a pele dura segue cortando pela metade
  (desvio D-EMP-11).
- **O código:** o fator `defesa` (0) passa a valer para o `defender` e o `contra_golpe`; o `guarda` (0,5) fica só para a pele dura.
- **O comando** (em `web/app`, no máximo 4 processos, uma run): `python scripts/equilibrio_tr/medir_tudo.py --faixa calibracao2 --empurrao v18
  --saida scripts/medicoes/equilibrio_tr/empurrao/depois_posturas0`; a tabela contra o mesmo `empurrao/antes/`, em `resumo_posturas0.txt`.
- **A faixa e o gate:** os da seção 4.2 (72101–72505; F-3, G-2, G-3 e o teto do T-2 nomeados). Se ainda falhar, a etapa para e volta com
  a tabela e uma leitura do que segura o duelista contra a muralha.

### 4.4 A rodada curta do F-3 (registrada em 2026-11-06, antes da primeira luta dela)

- **Por quê:** a terceira medição deixou só o F-3 reprovado (seção 9.3). O Matheus decidiu, nas palavras dele (repassadas pela sessão de
  planejamento), "Tá, então faz uma rodada aí de equilíbrio só para arrumar essa questão" (desvio D-EMP-13).
- **O que fica:** as posturas sem empurrão (D-EMP-11), o pesado (60 px, derruba), a pele dura (metade), a queda (62 passos), o deslize.
- **As medições, em ordem, uma por vez, parando na primeira que fecha** (cada uma num commit próprio, com a constante trocada em
  `EMPURRAO_V18`; os valores ficam PROPOSTOS e SEM FONTE):
  - **A:** a investida empurra 20 px (era 40) e continua derrubando — saída `empurrao/r_a_inv20/`;
  - **B:** a investida empurra 40 px e não derruba — saída `empurrao/r_b_inv40_sem_queda/`;
  - **C:** a investida empurra 20 px e não derruba — saída `empurrao/r_c_inv20_sem_queda/`.
- **O comando** (em `web/app`, no máximo 4 processos): `python scripts/equilibrio_tr/medir_tudo.py --faixa calibracao2 --empurrao v18
  --saida scripts/medicoes/equilibrio_tr/empurrao/<saida>`; a tabela contra o mesmo `empurrao/antes/`, em `resumo_<saida>.txt`.
- **A faixa:** a calibração, 72101–72505. Tempo estimado: ~7 min por medição.
- **Fecha quando:** toda meta que passa no "antes" passa (o gate da seção 4). Se as três não fecharem, a rodada para e volta ao Matheus
  com a tabela. O pesado só entra se a leitura das três mostrar que o F-3 depende dele, e aí com um pedido novo.

## 5. Entrega

- Testes: em `web/app`, `npm test`, `npm run tipos` e `npm run e2e` (no máximo 4 processos); o e2e `e2e/luta_layout.spec.ts` na etapa 5.
- Registro: seção própria no fim de `docs/registro/2026-11.md` e uma linha no fim do índice `docs/REGISTRO_DESVIOS.md`, na ordem das
  seções. O resumo de cada etapa vai no corpo do PR e numa seção no fim deste documento.
- PR contra a `main` com o corpo no modelo de `.github/pull_request_template.md`, conferido com `python tools/verificar_relato.py` e
  `python tools/conferir_saude.py`. O merge é só do Matheus.
- Antes de cada PR de código que muda a tela, capturas ou um GIF da luta ao Matheus, e a aprovação dele.

## 6. Fora desta tarefa

- Mudar o `empurrao` antigo da v13 ou a v14 e as versões que lutam como ela.
- Recalibrar listas, fatores, cartas ou o disparo para a v18. Se a etapa 4 mostrar desequilíbrio, a recalibração é uma decisão do Matheus
  e uma tarefa (ou uma rodada) própria.
- Os efeitos da LUTA_EFEITOS (E1 a E5), a não ser o ponto de encontro da etapa 5.
- Sprites ou clipes novos; o som.

## 7. Critérios de aceitação

- **Desta etapa:** este documento na `main`, com a seção 8 respondida.
- **Da etapa 2:** o teste do gabarito das lutas de hoje passa na `main` antes do commit do motor.
- **Da etapa 3:** o gabarito da etapa 2 passa sem regravar; `git diff origin/main -- web/app/test/gabaritos/` não mostra gabarito antigo
  mudado; os testes da tabela 3.2 passam; `npm test` e `npm run tipos` passam, com as contagens no PR.
- **Da etapa 4:** o JSON de cada bancada em `web/app/scripts/medicoes/equilibrio_tr/empurrao/` (antes e depois), e a tabela das metas no
  PR.
- **Da etapa 5:** as capturas aprovadas pelo Matheus; o desenho passo a passo é o mesmo para a mesma luta.

## 8. Precisa do Matheus

**DECIDIDAS pelo Matheus em 2026-11-06, todas pela recomendação.** As palavras dele foram "Aceito todas", em resposta à pergunta "Aceita as
recomendações das EMP-1 a EMP-8 como estão?", com a tabela das oito na frente. Ele respondeu na sessão de planejamento da missão
SPRITES_GERACAO, e o Gerente repassou a resposta ao worker com as palavras literais. Os números seguem SEM FONTE.

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| **EMP-1** | quanto empurra cada golpe | **golpe rápido e finta 0, investida 40 px, pesado 60 px, disparo 0** | com o leve acima de 0, a troca curta separa os dois e as listas defensivas voltam a ficar no limite de tempo (a fase 1 da rodada viu isso com 6 px). Com o pesado muito curto (menos de ~20 px), o empurrão quase não se vê; muito longo (mais de ~120 px), o alvo sai do médio e a luta vira de longe |
| **EMP-2** | o que derruba e por quanto tempo | **o pesado e a investida derrubam, 62 passos (~1 s)** | só o pesado: a investida, que é o exemplo do próprio pedido, não derruba. Queda longa (2 s ou mais) dá ao disparo e à investida um tiro de graça e pune demais quem leva; curta (menos de ~0,5 s) não se vê |
| **EMP-3** | quem está caído pode levar golpe? | **pode** (sem invulnerabilidade) | com invulnerabilidade, a regra fica mais justa, mas é uma regra a mais no motor e no desenho (piscar), e o derrubar perde valor. Sem ela, as listas de longe ganham um tiro no caído |
| **EMP-4** | a borda | **a cerca segura; o resto do empurrão se perde** | com o resto voltando no atacante (como nos jogos de luta), o encurralado escapa melhor, mas o atacante passa a ser empurrado pelo próprio golpe, o que o pedido não descreve |
| **EMP-5** | as posturas (a tabela da seção 3.2) | **defesa, contra-golpe e pele dura: metade e sem queda; investida aparada: nada; esquiva: como o dano** | se a defesa não segurar a queda, o pesado contra a defesa vira melhor do que hoje, e as listas defensivas perdem |
| **EMP-6** | o deslize no motor ou o salto | **deslize de 10 passos (160 ms)** no motor | com o salto, o motor fica mais simples, mas o desenho precisa inventar o meio do caminho, e o que se vê deixa de ser o `x` do motor |
| **EMP-7** | a versão | **a v18**, e os pets v13 a v17 seguem vivos lutando como hoje; só os ovos novos nascem v18 | trocar a luta dos pets que já existem mudaria lutas já jogadas, o que a regra de uma versão por mecânica proíbe |
| **EMP-8** | a medição e o gate (a seção 4) | **calibração 72101–72505, v18 contra v14; se uma meta que passa piorar, volta ao Matheus** | sem medir, a v18 entra com o equilíbrio desconhecido. Recalibrar sozinho iria contra a regra dos números PROPOSTOS |

## 9. Resultado

### 9.1 A medição de equilíbrio (etapa 4, 2026-11-06): o gate reprova

Rodada pelo plano 4.1, na calibração 72101–72505, com 4 processos (cerca de 7 min por lado). Os artefatos estão em
`web/app/scripts/medicoes/equilibrio_tr/empurrao/`: as pastas `antes/` e `depois/`, os dois logs e o `resumo.txt`.

**Três metas que passam hoje falham com a v18,** e o gate da seção 4 reprova:

| meta | antes (v14) | depois (v18) |
|---|---|---|
| F-3 | passa (o duelista vence 3 formas) | falha (o duelista vence 1) |
| G-2 | passa | falha: o Tortomon (`npc_tier2_sentinela`), pior forma o guardião, 0,83 |
| G-3 | passa: a Liga de 0,43 a 0,72 | falha: de 0,22 a 0,95, com o duelista, a muralha e o tita fora |

**O T-2 piora muito,** embora já falhasse hoje:
- o total de lutas no limite de tempo vai de 0,012 para 0,054;
- o pior par vai de duelista × sentinela, 0,145, para **duelista × muralha, 0,93**.

**O que melhora ou fica igual:**
- o T-1 (a luta média vai de 33,9 s para 36,7 s, e segue falhando);
- o T-3, o T-4, o T-5, o P-1, o P-2, o P-4, o G-4, o G-5, o G-6 e o I-2 continuam passando;
- o F-1 tem menos formas fora (duas, contra quatro).

As outras falhas de hoje seguem falhando. A tabela inteira está no `resumo.txt`.

Pela EMP-8, a etapa para aqui e volta ao Matheus, e nenhum número da seção 8 foi mexido. O desenho (etapa 5) foi escrito enquanto a medição
rodava e está no branch, mas o GIF e o PR de código esperam a decisão.

### 9.2 A segunda medição, a defesa sem empurrão (2026-11-06): o gate ainda reprova

Na mesma calibração (72101–72505), contra o mesmo "antes" (seção 4.2). Artefatos em
`web/app/scripts/medicoes/equilibrio_tr/empurrao/depois_defesa0/`, o log ao lado e a tabela em `resumo_defesa0.txt`.

| meta | v14 (hoje) | v18, EMP-5 original | v18, a defesa sem empurrão |
|---|---|---|---|
| F-3 | passa (o duelista vence 3 formas) | falha (1) | falha (1) |
| G-2 | passa | falha (Tortomon, 0,83) | **passa** |
| G-3 | passa (0,43 a 0,72) | falha (0,22 a 0,95; duelista, muralha e tita fora) | falha (0,24 a 0,91; duelista e tita fora) |
| T-2 no limite (total; pior par) | 0,012; duelista × sentinela 0,145 | 0,054; duelista × muralha 0,93 | 0,054; duelista × muralha 0,92 |
| T-1 (já falha hoje) | 33,9 s | 36,7 s | 36,9 s |

- Tirar o empurrão da defesa conserta o G-2 e tira a muralha da lista do G-3, mas quase não mexe no duelista: o F-3 e o par duelista ×
  muralha no limite ficam iguais. As outras metas que passavam continuam passando.
- Uma leitura, sem medição: a muralha luta sobretudo com o contra-golpe (`motor/bots.ts`, a primeira regra dela), que segue empurrando
  pela metade; o duelista, que abre com a investida, é quem mais sofre com o empurrão de ida e volta. Nada foi ajustado; volta ao Matheus.

### 9.3 A terceira medição, a defesa e o contra-golpe sem empurrão (2026-11-06): só o F-3 reprova

Na mesma calibração (72101–72505), contra o mesmo "antes" (seção 4.3). Artefatos em
`web/app/scripts/medicoes/equilibrio_tr/empurrao/depois_posturas0/`, o log ao lado e a tabela em `resumo_posturas0.txt`.

| meta | v14 (hoje) | v18, a defesa sem empurrão | v18, a defesa e o contra-golpe sem empurrão |
|---|---|---|---|
| F-3 | passa (o duelista vence 3 formas) | falha (1) | **falha (1)** |
| G-2 | passa | passa | passa |
| G-3 | passa (0,43 a 0,72) | falha (0,24 a 0,91) | **passa (0,37 a 0,85; ninguém fora)** |
| T-2 no limite (total; pior par) | 0,012; duelista × sentinela 0,145 | 0,054; duelista × muralha 0,92 | 0,015; duelista × sentinela 0,13 (duelista × muralha 0,09) |
| T-1 (já falha hoje) | 33,9 s | 36,9 s | 34,8 s |

- Todas as outras metas que passam hoje continuam passando; o F-3 é a única que passa a falhar.
- **O duelista contra as outras formas** (a fração de vitórias dele na matriz dos adultos): emboscador 0,74 → 0,09; Titã 0,838 → 0,195;
  muralha 0,063 → 0,07; vigia 0,805 → 0,698. Ele vencia o emboscador, o vigia e o Titã; agora só o vigia.
- **Uma leitura, sem medição:** o duelista vive da investida (do médio, `motor/bots.ts`), e a investida agora empurra o rival 40 px e o
  derruba, o que o leva de volta ao médio. Contra o emboscador, que recua e atira do médio (o disparo ×6 da v14), o empurrão entrega a
  distância que ele quer. Contra o Titã, a pele dura segura a queda e corta o empurrão pela metade, e o Titã segue com o pesado de perto.
  O que segurava o duelista contra a muralha (o empurrão do contra-golpe, que o tirava do alcance e virava luta por tempo) saiu com esta
  troca. Nada foi ajustado; volta ao Matheus.

### 9.4 A rodada curta do F-3, medição A (a investida 20 px, 2026-11-06): o F-3 passa, o G-2 falha por pouco

Artefatos em `web/app/scripts/medicoes/equilibrio_tr/empurrao/r_a_inv20/`, a tabela em `resumo_r_a_inv20.txt`.

- **F-3 passa:** o duelista vence 2 formas (o emboscador, 0,74, e o vigia, 0,723); o Titã fica em 0,253.
- **G-2 falha:** no Tortomon (`npc_tier2_sentinela`), os pets sem treino vencem 0,31 (o teto é 0,3; no "antes", 0,265); o "com" (0,94) e
  o pior (0,89) passam.
- G-3 passa (0,40 a 0,81); T-2 0,014 no total, pior par duelista × sentinela 0,135; T-1 35,1 s. As outras metas que passam hoje passam.
- Não fecha; segue a medição B (seção 4.4).

### 9.5 A rodada curta do F-3, medição B (a investida 40 px sem derrubar, 2026-11-06): o F-3 e o G-2 falham

Artefatos em `web/app/scripts/medicoes/equilibrio_tr/empurrao/r_b_inv40_sem_queda/`, a tabela em `resumo_r_b_inv40_sem_queda.txt`.

- **F-3 falha:** o duelista vence 1 forma (o emboscador, 0,685); o vigia cai para 0,233 (era 0,805 hoje), o Titã fica em 0,208.
- **G-2 falha:** no Tortomon, os pets sem treino vencem 0,31 (teto 0,3), como na A.
- G-3 passa (0,37 a 0,80); T-2 0,016 no total, pior par duelista × sentinela 0,18; T-1 35,2 s.
- Não fecha; segue a medição C (seção 4.4).

### 9.6 A rodada curta do F-3, medição C (a investida 20 px sem derrubar, 2026-11-06): a rodada não fecha

Artefatos em `web/app/scripts/medicoes/equilibrio_tr/empurrao/r_c_inv20_sem_queda/`, a tabela em `resumo_r_c_inv20_sem_queda.txt`.

| meta | v14 (hoje) | posturas sem empurrão (9.3) | A: investida 20 px | B: 40 px sem derrubar | C: 20 px sem derrubar |
|---|---|---|---|---|---|
| F-3 (vitórias do duelista) | passa (3) | falha (1) | **passa (2)** | falha (1) | falha (0) |
| G-2 (Tortomon sem treino, teto 0,3) | passa (0,265) | passa (0,2975) | falha (0,31) | falha (0,31) | falha (0,31) |
| G-3 | passa | passa | passa | passa | passa |
| T-2 total; pior par | 0,012; duelista × sentinela 0,145 | 0,015; 0,13 | 0,014; 0,135 | 0,016; 0,18 | 0,015; 0,18 |
| T-1 (já falha hoje) | 33,9 s | 34,8 s | 35,1 s | 35,2 s | 34,5 s |

- O duelista contra o emboscador, o vigia e o Titã: hoje 0,74 / 0,805 / 0,838; A 0,74 / 0,723 / 0,253; B 0,685 / 0,233 / 0,208; C 0,045 /
  0,355 / 0,238. **A queda da investida é o que ainda faz o duelista vencer:** sem ela (B, C), ele perde o vigia, e com 20 px sem queda,
  também o emboscador.
- O G-2 falha nas três pelo mesmo número: contra o Tortomon (que recua), os pets sem treino vencem 0,31 (brigão 0,19 e colosso 0,17 sem
  treino; hoje 0,10 e 0,09). Com as posturas sem empurrão e a investida 40 px, era 0,2975. São ~5 lutas em 400 acima do teto.
- As três medições combinadas não fecharam; a rodada para e volta ao Matheus (seção 4.4). Nada foi ajustado além do plano.

### 9.7 A decisão: a medição A (2026-11-07)

- O Matheus decidiu, nas palavras dele (repassadas pela sessão de planejamento), "Aceitar a A". O motor volta à versão A: a investida
  empurra 20 px e derruba; a defesa e o contra-golpe não são empurrados; a pele dura corta pela metade; o pesado fica em 60 px e derruba.
- O G-2 em 0,31 (o Tortomon contra os pets sem treino, teto 0,3) fica aceito e vai para a rodada de equilíbrio do fim. Todos os números
  do empurrão seguem PROPOSTOS e SEM FONTE (calibrados só nas sementes 72101–72505; nenhuma validação rodou).
- Os números da v18 são os da medição A (seção 9.4; `empurrao/r_a_inv20/`).

