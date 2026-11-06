# TAREFA V3 — LUTA_EMPURRAO (2026-11-06)

Coordenador: o Gerente da missão SPRITES_GERACAO (Claude Code). Worker: Claude Code, Opus 5.5. Worktree e branch: `v3-luta-empurrao`.
Status: PROPOSTA (os números da seção 8 ficam com o Matheus).

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

Os números abaixo são **PROPOSTOS, SEM FONTE** (nenhum vem de medição; a etapa 4 mede o efeito). Cada um vira decisão na seção 8.

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

Cada uma com a recomendação e o custo de errar. Todos os números são PROPOSTOS, SEM FONTE.

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
