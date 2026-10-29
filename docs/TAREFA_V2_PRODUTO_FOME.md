# TAREFA V2 — PRODUTO-FOME (2026-10-29)

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

- **O limiar do chamado de fome:** 0,45, o mesmo do `fome_moderada` do instinto (PROPOSTO, seção 9).
  - **Recomendação:** manter. É o único valor em que o chamado e o comer do pet andam juntos.
  - **Custo de errar:** com um limiar mais alto, volta o descompasso de hoje: chamado aberto, ração vista, pet que não come.
  - **Consequência:** o bebê quase não pede comida, porque a fome dele cai de 0,80 a ~0,65 nos 180 min sem cuidado. A fração de cuidado
    da evolução passa a pesar só a higiene e o carinho, a menos que o dono brinque muito (o brincar gasta fome).
- **Os chamados de higiene e de carinho:** têm o mesmo descompasso (seção 9).
  - **Recomendação:** uma tarefa própria, com o mesmo desenho do de fome.

## 9. Resumo da entrega (worker A, 2026-10-29)

- **As chaves no registro:** o evento novo `"p"` (`EventoProduto`, `motor/tipos.ts`) guarda as duas chaves do produto, `chamadoPelaFome` e
  `decisaoNaComida`.
  - Ele vai uma vez, no começo do registro, depois do ritmo e da origem, se houver, e antes de qualquer decisão, ação do dono ou avanço.
    `Motor.ligarProduto` grava o evento; o replay o lê.
  - O jogo grava as duas ligadas em todo ovo novo dos pets v12 (`src/produto.ts`, `ligarProduto`): o ovo novo, o do brasão, o filho do
    cruzamento e o pet de exemplo.
  - Os saves de antes não têm o evento e seguem com as duas desligadas. A vida deles não muda.
  - A pesquisa e os gabaritos nunca gravam o evento.
- **(a) o chamado de fome pela fome do corpo** (`Motor._chamadoFome`; o limiar é `CHAMADO_FOME_CORPO.limiar` = 0,45, PROPOSTO):
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
- **Interpretações e achados** em `docs/registro/2026-10.md` (PRODUTO-FOME).
