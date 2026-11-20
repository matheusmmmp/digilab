# TAREFA V2 — PRODUTO-FOME (2026-10-29)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Coordenador: Gerente (Claude Code). Worker: A (Claude Code, Opus 5.5). Worktree e branch: `v2-produto-fome`. Status: ENTREGUE.

Categoria: implementacao. Origem: Matheus, 2026-10-29: o Gerente reproduziu no jogo web (a `main` em 0a27d97, o pet v12 com o mundo) a
ração posta a ~4 células do Koromon com o chamado "fome" aberto, e o pet escolhendo brincar, ficar à toa ou chamar atenção; o Matheus
autorizou dois consertos de produto.

## 1. Pergunta

Por que o pet não vai à ração que vê, e a tela pede comida com o pet saciado? Não vem de uma hipótese do `docs/PLANO_V2_PESQUISA.md`: é
um conserto do produto jogável.

As três causas que o Gerente achou:
1. o instinto (`web/app/motor/lobos.ts`, `agirInstinto`) só come com a fome abaixo de 0,45; o pet estava em 0,675;
2. o chamado de fome do bebê abre pelo relógio (`CHAMADO_BEBE`, `motor/motor.ts`, `_chamados`), sem olhar a fome do corpo;
3. o pet decide a cada 15 min de jogo, e com chamado aberto o tempo cai para 1x (`src/tempo.ts`): até 15 min de relógio sem reagir à
   comida.

## 2. Depende de

Nada além da `main`.

## 3. Mudança mínima

- **(a) o chamado de fome pela fome do corpo:**
  - ele abre quando a fome do corpo pede, e não pelo relógio;
  - a higiene e o carinho ficam como estão. Se o mesmo descompasso aparecer neles, só se relata.
- **(b) a decisão na comida:**
  - pôr comida no chão (`porRacaoEm`, `deixar_comida`) provoca uma decisão do pet já no próximo passo;
  - o cérebro A e a política não mudam, só o momento da decisão.
- **As chaves:** as duas mudanças ficam atrás de chaves do produto, ligadas no jogo web e desligadas na pesquisa. Os gabaritos e as
  vidas da pesquisa saem byte a byte. O laço do Python que existir ganha a mesma chave, desligada.
- **Fronteiras:** o cérebro A, a v12 da pesquisa e o `engine.py` não mudam. Se o conserto exigir mexer neles, parar e relatar.

## 4. Experimento e gate (se houver run)

Nenhuma run. A máquina rodava a avaliação da L-2 até ~20h10, com 4 processos: só testes focados até lá.

## 5. Entrega

- **Testes:**
  - um que reproduz o caso: a ração vista, a fome alta e o chamado só quando a fome pede;
  - um que mostra a decisão imediata ao pôr a ração;
  - os gabaritos existentes passam sem mudar.
- **No navegador:** um print do pet indo à ração.
- **O PR:** o relato vai no corpo; o merge é do Matheus.

## 6. Fora desta tarefa

- O limiar dos chamados de higiene e de carinho (só relatado).
- A velocidade do tempo com chamado aberto (`src/tempo.ts`).
- O instinto e o cérebro (o 0,45 do `fome_moderada`).

## 7. Critérios de aceitação

- `web/app/test/produto_fome.test.ts` e `web/app/test/decisao_na_comida.test.ts` passam.
- Os gabaritos de hoje não mudam e os testes deles passam: `v12_jogo_ts.json`, `mvp_produto_python.json` e `mvp_mundo_python.json`.
- `tests/test_decisao_na_comida.py` passa.
- O `engine.py` não muda.

## 8. Precisa do Matheus

- **O limiar do chamado de fome: DECIDIDO, 0,45** (Matheus, 2026-10-29, pelo Gerente).
  - O Matheus decidiu ciente de que o bebê quase não chama mais por fome.
  - O intervalo de 30 min e a janela de 15 min seguem como hoje.
  - O efeito medido está na seção 9.
- **Os chamados de higiene e de carinho:** têm o mesmo descompasso (seção 9). Ficam como estão, só no relato.
  - **Recomendação:** uma tarefa própria, com o mesmo desenho do de fome.
  - **Por que importa:** com a chave, um dono que nunca alimenta, mas atende higiene e carinho, cria um bebê sereno (seção 9).

## 9. Resumo da entrega (worker A, 2026-10-29)

- **As chaves no registro:** o evento novo `"p"` (`EventoProduto`, `motor/tipos.ts`) guarda as duas chaves do produto, `chamadoPelaFome` e
  `decisaoNaComida`.
  - Ele vai uma vez, no começo do registro, depois do ritmo e da origem, se houver, e antes de qualquer decisão, ação do dono ou avanço.
    `Motor.ligarProduto` grava o evento; o replay o lê.
  - O jogo grava as duas ligadas em todo ovo novo dos pets v12 (`src/produto.ts`, `ligarProduto`): o ovo novo, o do brasão, o filho do
    cruzamento e o pet de exemplo.
  - Os saves de antes não têm o evento e seguem com as duas desligadas. A vida deles não muda.
  - A pesquisa e os gabaritos nunca gravam o evento.
- **(a) o chamado de fome pela fome do corpo** (`Motor._chamadoFome`; o limiar é `CHAMADO_FOME_CORPO.limiar` = 0,45, DECIDIDO pelo Matheus em 2026-10-29):
  - **abre** no bebê quando a fome fica abaixo do limiar, no máximo um a cada 30 min (o intervalo de hoje). Assim, um chamado perdido não
    reabre a cada janela;
  - **fecha como atendido** quando o dono alimenta (como hoje) ou quando a fome volta ao limiar. Nos v12, ela só sobe comendo a ração
    que o dono deixou;
  - **fecha como perdido** quando a janela de 15 min passa (como hoje);
  - **só mexe no chamado:** com a chave, o estado, o mundo e o cérebro do pet saem iguais aos de sem ela.
- **(b) a decisão na comida:**
  - `MotorCorpoMundo.decidirNaComida` (TS) e `ConfigDecisaoNaComida` (Python, `digilab/config.py`, desligada; `digilab/mundo.py`,
    `_aplicar_deixar_comida`) fazem a mesma coisa: a comida que o dono deixa adianta a próxima decisão para o tick de agora;
  - a decisão seguinte conta o intervalo de 15 dali;
  - o `engine.py` não muda: o motor só escreve o `_proxima_decisao` que o laço já lê.
- **A paridade:** `web/app/test/gabaritos/decisao_na_comida_python.json`, gravado por `experiments/exportar_gabarito_decisao_na_comida.py`.
  - São duas sementes, 101 e 202, cada uma com a chave ligada e desligada. O dono é um roteiro com a ração no meio do intervalo: o dono
    sintético age no passo de 15 ticks, que é o tick das decisões, e ali a chave não muda nada.
  - O TS reproduz as quatro vidas decisão a decisão.
- **O caso no navegador:** um Rookie com fome 0,36, acordado, 1 min depois de uma decisão (a semente 101, o tick 1006).
  - A ração vai para "perto do pet", a 2 células, e no minuto seguinte o pet já decidiu: come e anda até ela (a fome vai a 0,81).
  - Sem a chave, a decisão seguinte só viria no tick 1020, 14 min de jogo depois. No 1x com chamado aberto, são 14 min de relógio.
  - Um bebê de 30 min (fome 0,775): sem a chave, a tela mostra "Chamado: fome"; com a chave, nenhum chamado.
- **O mesmo descompasso, só relatado:** o chamado de higiene abre pelo relógio com a higiene entre 0,92 e 0,96 e a sujeira 0. O de carinho
  abre com o humor entre 0,67 e 0,99. São as sementes 101, 202 e 303, nos 180 min do bebê sem cuidado.
- **O efeito no bebê** (pedido do Gerente;
  `web/app/test/efeito_chamado_fome.json`, de `web/app/test/medir_chamado_fome.ts`):
  - **as vidas:** as sementes 101, 202 e 303, nos dois ritmos, com seis donos de roteiro (SEM FONTE). Os números saem iguais nas três
    sementes;
  - **a fração de cuidado** é a dos chamados do bebê atendidos na janela; com 0,8 ou mais, a criança é a serena, e abaixo, a arisca
    (`CAT.limiarCuidado`). O `test/produto_fome.test.ts` confere que o arquivo está em dia e que o efeito é este:

| ritmo | dono | chamados de fome, hoje → com a chave | fração de cuidado (ramo), hoje → com a chave |
|---|---|---|---|
| rápido (180 min) | nada | 5 → 0 | 0 (arisco) → 0 (arisco) |
| rápido | atende tudo na hora, ou 10 min depois | 5 → 0 | 1 (sereno) → 1 (sereno) |
| rápido | brinca na 1ª hora e atende tudo | 5 → 0 | 1 (sereno) → 1 (sereno) |
| rápido | só alimenta | 5 → 0 | 0,5 (arisco) → 0 (arisco) |
| rápido | atende tudo, menos a fome | 5 → 0 | 0,5 (arisco) → **1 (sereno)** |
| clássico (360 min) | nada | 11 → 0 | 0 (arisco) → 0 (arisco) |
| clássico | atende tudo na hora, ou 10 min depois | 11 → 0 | 1 (sereno) → 1 (sereno) |
| clássico | brinca na 1ª hora e atende tudo | 11 → 4 | 1 (sereno) → 1 (sereno) |
| clássico | só alimenta | 11 → 0 | 0,478 (arisco) → 0 (arisco) |
| clássico | atende tudo, menos a fome | 11 → 0 | 0,522 (arisco) → **1 (sereno)** |

  - **no rápido,** a chave nunca abre o chamado de fome, nem com o dono brincando;
  - **no clássico,** só abre com o dono brincando muito na primeira hora (4 chamados, todos com a fome abaixo de 0,45);
  - **a fração de cuidado** passa a depender só da higiene e do carinho. Quem atende tudo fica igual. Quem só alimenta cai a 0. Quem nunca
    alimenta, mas atende higiene e carinho, sobe a 1 e cria um bebê sereno;
  - **sem chamado, o bebê sem comida não morre no estágio:** a fome chega a ~0,65 no rápido e a ~0,50 no clássico.
- **Interpretações e achados** em `docs/registro/2026-10.md` (PRODUTO-FOME).

## 10. A passagem à v13 (worker A, 2026-10-30)

- **Por quê:** antes do merge, a `main` (53fd005) recebeu o COMBATE-TR. Os ovos novos são v13, e os v12 não abrem mais (o descarte 6;
  D-9, Matheus, 2026-10-29). A seção 9 fala dos ovos v12: na `main`, leia v13.
- **As chaves:** valem para os ovos v13 novos, com o evento `"p"` só no começo do registro deles. Os saves v13 de antes não têm o evento
  e não mudam; nenhum pet que já existe passa a ter a regra.
- **O conflito:** o `"fl"` (a fala dos v7–v10) saiu da `main` e não volta. A conferência `versao < 12` saiu do `Motor._produto`: só a
  v13 abre.
- **O efeito no bebê:** refeito na v13, as 72 vidas saem iguais (a tabela da seção 9 vale).
- **O desvio:** em `docs/registro/2026-10.md` (PRODUTO-FOME na v13).
