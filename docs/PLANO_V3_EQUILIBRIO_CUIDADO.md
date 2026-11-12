# PLANO_V3_EQUILIBRIO_CUIDADO: a rodada de equilíbrio do cuidado

Fase: V3. Coordenador: o Gerente da V3. Data: 2026-11-12. Estado: **plano, com as decisões EQ-1 a EQ-8 PROPOSTAS**. Nenhuma vida nem número
muda antes da aprovação do Matheus.

## 1. O pedido e o que entra

O Matheus pediu, em 2026-11-12: "pode fazer uma rodada de equilíbrio". As frentes deixaram números PROPOSTOS "para a rodada de equilíbrio"
(a regra de 2026-10: mecânica primeiro, equilíbrio no fim). O levantamento de 2026-11-12 achou esses itens espalhados nas tarefas e nos
registros. **O painel não tinha a lista.**

**Os nomes que confundem:**
- **a rodada da luta** (R2, R3, LP5, LP6) tem planos próprios e hoje está com a investigação do núcleo (`docs/PLANO_LUTA_NUCLEO.md`, aprovada
  em 2026-11-12);
- **o `EQUILIBRIO_GERAL.md`** é a rodada do V21, de 2026-09/10, já feita.

Esta rodada é a terceira, a do **dia a dia do pet**: comer, dormir, brincar, explorar e os Bits. Esses são os números que o jogador sente logo
no primeiro dia.

## 2. Os itens

Todos foram tirados do levantamento, com a referência no repositório.

| Bloco | Item | Hoje | Onde | O que se sente |
|---|---|---|---|---|
| **A, comida do bebê** | o pet só come a ração com a fome abaixo de 0,45; a do bebê fica acima, e a ração acumula no comedouro (2 no rápido, 8 no clássico) | medido em `test/produto_cuidado.test.ts` | `TAREFA_V2_PRODUTO_CUIDADO.md`; memória `web-pet-comida-chamado` | o dono põe comida, e o bebê não come |
| A | o Rookie com Alimentar a cada 2 h chega à saúde 0 | achado | registro 2026-11, ~2600 | o pet adoece mesmo bem cuidado |
| A | os chamados do bebê: fome 0,7, higiene 0,9, carinho 0,8 | PROPOSTOS | `CHAMADO_BEBE_CORPO` | quando ele chama |
| **B, sono, brincar e explorar** | o sono que segura: acorda acima de 90 % | PROPOSTO | `config.py` (`lambda_acordar`), D-SONO-1 | 15 cochilos em vez de 75 |
| B | o pet que o dono faz brincar quase só dorme: 1 explorar em 480 decisões | achado | D-MIT-G-3 | as Pegadas e o Conhecimento não andam |
| **C, bola** | a guarda da fome urgente no brincar (o G-BB-2 falhou por 1 chute no jogo) | falta a regra | D-BB2-3 | o pet faminto vai jogar bola |
| C | o lance de 2 a 3 células, a janela de 30 ticks e o `w_bola_do_dono` 4 S | PROPOSTOS | `config.py`, BOLA_BRINCAR | se o pet atende o Brincar |
| C | o pet quer a bola nova sozinho | não feito | BOLA_BRINCAR, seção 6 | a bola parada ganha vida |
| **D, árvore** | o galho (3 frutas, recarga de 240 min) e a queda natural da fruta | PROPOSTOS | `config.py`, ARVORE_SACODE | a comida da ilha |
| **E, Bits** | os ganhos (vitória, chamado, evolução, Tamer) e os preços (portão ★★ 150 e seguintes) | PROPOSTOS, SEM FONTE | `PLANO_V3_MOEDA.md` | a conta do plano ainda não foi feita: o 1º pet junta os 150 do portão ★★ antes de estar pronto para o Champion? |

**Fora desta rodada** (EQ-1): a luta, o corpo químico do Python (J2), o decodificador de conceitos, a cooperação, o MMO e as reações do
habitat (números visuais).

## 3. O método

O método é o do `CLAUDE.md`: plano registrado antes, calibração com as sementes dela, validação uma vez.

1. **E0, o retrato de hoje.** Uma bancada mede, no motor do jogo, um dia típico de cada estágio (bebê, In-Training, Rookie) com três donos
   roteirizados:
   - o atento: atende cada chamado;
   - o médio: atende a cada 2 h;
   - o relapso: atende a cada 6 h.

   As medidas, os números que o jogador sente:
   - quanto da ração posta é comida;
   - o tempo com fome alta;
   - a saúde no fim do dia;
   - os cochilos e a energia ao acordar;
   - as decisões de explorar e de brincar;
   - os chutes por lance;
   - os Bits por dia, e o dia em que o pet junta o portão ★★ contra o dia em que ele fica pronto para o Champion.

   O E0 não muda nada: é só o retrato, com os pets de hoje (o grupo v31 e o ovo de um pet v32).
2. **As metas (EQ-3).** Para cada medida, uma faixa-alvo escrita antes, por exemplo "o atento nunca deixa o bebê com fome alta por mais de
   1 h". Os números são PROPOSTOS e vão ao Matheus com o retrato.
3. **E1, a calibração.** Ajustar os itens da seção 2 até as metas, só nas sementes de calibração. As regras novas entram atrás de chave,
   primeiro no Python quando a regra é do cérebro ou do corpo, e depois no TS com a paridade:
   - a guarda da fome urgente no brincar;
   - o bebê come com a fome dele.
4. **E2, a validação única.** Uma vez, numa faixa de sementes nova, com os gates escritos no plano de análise.
5. **E3, a versão.** Os números novos entram juntos numa versão nova de pet (EQ-6). Os pets de hoje não mudam.

## 4. As decisões

- **EQ-1, o escopo:** os blocos A a E da seção 2. A luta fica com a investigação do núcleo, e o corpo químico do Python, a cooperação, o MMO e
  os números visuais ficam fora. **Recomendo.** O custo de errar é baixo: o que ficar de fora entra numa rodada própria.
- **EQ-2, a ordem:**
  1. A, a comida do bebê, que é o que pior se sente no começo;
  2. B, o sono, o brincar e o explorar;
  3. C, a bola;
  4. E, os Bits;
  5. D, a árvore.

  Cada bloco passa pelo E0, E1 e E2 junto com os outros, mas o retrato sai nessa ordem.
- **EQ-3, as metas:** escritas no plano de análise antes do E0 rodar, com o retrato do E0 ao lado. O Matheus aprova as metas antes da
  calibração.
- **EQ-4, os donos roteirizados:** o atento, o médio e o relapso, como acima. O relapso mostra o castigo, e o atento mostra o teto.
- **EQ-5, as sementes:**
  - uma faixa de calibração nova e uma de validação nova, pedidas e gravadas em `experiments/bancada/faixas.py` antes da primeira vida;
  - proposta: a 93101…93505 para a calibração e a 94101…94505 para a validação, se estiverem livres;
  - no máximo 4 processos, e uma run de pesquisa por vez.
- **EQ-6, uma versão só no fim:** todos os números novos entram juntos numa versão nova, para o grupo e para o ovo de um pet, e não uma versão
  por item. Até lá, as chaves ficam desligadas.
- **EQ-7, as regras novas que esta rodada pode criar,** só estas duas:
  - a guarda da fome urgente no brincar (C);
  - o bebê comer com a fome dele (A).

  Qualquer outra regra nova volta ao Matheus.
- **EQ-8, o pet quer a bola nova sozinho:** fica fora desta rodada, porque é uma mecânica nova, não um número. Se o Matheus quiser, ganha uma
  tarefa própria.

## 5. A entrega

- **PR 1:** este plano.
- **PR 2:** o plano de análise (`docs/PLANO_ANALISE_V3_EQUILIBRIO_CUIDADO.md`), com as faixas no `faixas.py`, a bancada do E0 e o retrato,
  com a tabela das metas para aprovar.
- **PR 3:** a calibração (E1), por bloco, com as chaves desligadas.
- **PR 4:** a validação única (E2) e a versão nova (E3).

## 6. Precisa do Matheus

**Recomendo aprovar as EQ-1 a EQ-8 como estão.** A pergunta que mais muda o trabalho é a EQ-1: deixar a luta fora. Ela é o que mais reprova
hoje:
- a Liga, a Torre e a Fábrica com 0 títulos;
- 81 % das vidas paradas no Champion;
- 7 NPCs reprovados.

Mas ela já tem a investigação do núcleo aprovada, e misturar as duas rodadas trava as duas.
