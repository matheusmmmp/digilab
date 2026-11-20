# SÍNTESE DA EVIDÊNCIA — fase A4 (2026-11-17, Claude Code, Opus 5.5)

**O que é:** o que os resultados registrados, juntos, permitem concluir sobre o DigiBrain modular, e o que não permitem. **Nenhum resultado
novo:** este documento só reorganiza o que já está num `RESULTADO_*`, na auditoria da A0 ou no pré-registro da A3. Todo número tem o
artefato e o sha256 de onde sai; os rótulos **interpretação** marcam leituras que não são resultado de nenhuma regra escrita antes.

Tarefa: `docs/TAREFA_V3_EVIDENCIA.md`, fase A4. As fases: A0 (#942), A1 (#943), A2 (#952), A3 (#971, aberto). O pré-registro de cada
experimento, com o plano, as sementes e a regra de leitura, está em [`PREREGISTRO.md`](PREREGISTRO.md).

## 1. As três respostas

### 1.1 O modular vence uma baseline trivial nas mesmas células? **Não.** (A1)

- **O resultado:** REL − TRIV na taxa de fechamento por episódio de fome, nas 4 células do `longe_fixo`: **−0,083 [−0,128; −0,038]**, n = 200
  unidades, t = −3,63, classe **"< 0"**. A baseline vence. H refutada.
- **As secundárias vão no mesmo sentido:** comedouro −0,074 [−0,099; −0,049], longe sorteado −0,362 [−0,373; −0,351], n = 200 cada.
- **A baseline:** "come se fome < 0,4; dorme se energia < 0,1; brinca se tédio > 0,5 × S; senão explora", calibrada só nas sementes
  96101…96505; a validação rodou uma vez, nas 97101…97505.
- **De onde:** [`RESULTADO_V3_BASELINE_TRIVIAL.md`](RESULTADO_V3_BASELINE_TRIVIAL.md), seções 3 e 4;
  `artifacts_v3_baseline_trivial/validacao/resultado.json` `706a687a0b56dbee52b11710b3f906f84babc4a27ca2bf45613f630f9bf63b6c`.
- **Decidido:** o Matheus aceitou o "< 0" como saiu ("Aceitar e seguir A2", D-EV-A1-7); pelo pedido da tarefa, a poda (L5 da limpeza)
  passou a obrigatória.

**O que isso não demonstra:**
- que o modular é pior para o pet: a baseline vence vivendo no limite (privação em ~98 % das decisões, exaustão em todas as decisões da
  segunda semana, contra 0,38 e 0,24 do REL no `longe_fixo`; seção 5 do resultado). Isso é descritivo, pós hoc, sem gate;
- que esta baseline é a melhor política trivial: o ponto calibrado caiu na borda da grade em dois eixos (D-EV-A1-4);
- nada fora das 12 células da C4, do mundo do MVP e dos 14 dias; nada sobre o jogo web.

**Interpretação:** a medida primária da C1 à C4 (fechar o episódio de fome) premia uma regra de quatro linhas que passa fome o tempo todo.
Os ganhos da C1 e da C4 são ganhos do modular sobre versões dele mesmo, não sobre o problema. A escolha de uma medida de bem-estar como
primária seria um plano novo, não uma releitura desta run.

### 1.2 O aprendizado em vida muda o comportamento no jogo? **Sim, pouco.** (A2)

- **O resultado:** braço A (P1 e P2 ligados) contra braço B (desfecho e hábito zerados antes de cada leitura), o mesmo código, 200 sementes ×
  3 donos × 3 dias no motor TS. **9 das 15 medidas rejeitadas pelo Holm** (α = 0,05), classe **"muda"**. H confirmada.
- **O tamanho:** todas as diferenças abaixo de 0,01 da fração das decisões; a maior, o motivo `cheiro`, −0,0092 [−0,0112; −0,0071],
  n = 200. A distância de variação total entre as distribuições médias de ação é **0,0084** (descritivo, sem IC no artefato).
- **De onde:** [`RESULTADO_V3_ABLACAO_APRENDIZADO.md`](RESULTADO_V3_ABLACAO_APRENDIZADO.md), seção 3;
  `artifacts_v3_ablacao_aprendizado/run/resultado.json` `ced7c7932f0b423ebe9c4203ff15003a6bd347096fc885779ff7cd72161b3299`.
- **Decidido:** o CHECKPOINT A3, "Sim, seguir A3" (D-EV-A2-9): a A3 seguiu sem mudar nada, e a leitura de produto fica aqui, rotulada.

**O que isso não demonstra:**
- que o aprendizado é bom ou ruim para o pet (nenhuma medida de bem-estar ou de vínculo);
- qual das duas regras, P1 ou P2, produz a diferença (o braço B zera as duas);
- nada sobre a memória do lugar e a autobiográfica (M7, M8), ligadas nos dois braços;
- que um jogador nota a diferença: o plano não tem margem de relevância, e nenhuma foi criada depois.

**Interpretação:** 0,84 % da massa das ações muda de lugar. O efeito é real no motor; se é visível é uma pergunta de outra natureza, que o
plano do teste cego (`docs/PLANO_ANALISE_V3_LEGIBILIDADE.md`, PROPOSTO, decisões LG-1 a LG-6 abertas) foi escrito para responder.

### 1.3 O que foi replicado externamente? **Nada por um terceiro.** (A3)

- **A réplica da C4,** refeita do zero a partir do snapshot `a287ba20` pelo `tools/replicar_run.py`, na mesma máquina e pelo mesmo agente:
  **"divergiu"**, pelo critério escrito antes (D-EV-A3-2).
  - o `resultado.json` saiu **igual byte a byte** (`6f8c91d8e2b857194de1de00145a4da817efca76eb882bcd2d090dd3101cd6d3`);
  - o `medidas.json` não (`869ff397…` versionado, `479fecf0…` na réplica; 138 153 669 contra 138 151 421 bytes);
  - **causa provável, não provada:** os tempos de CPU e de relógio gravados por vida (`custo.vida_cpu`, `custo.vida_parede`), 14 400 de
    cada, os únicos campos de relógio do arquivo. A cópia da réplica foi apagada com a worktree; fechar pede uma nova réplica com
    `--manter` (D-EV-A3-5).
- **De onde:** [`PREREGISTRO.md`](PREREGISTRO.md), seção "A réplica da C4";
  `artifacts_v3_evidencia_a3/replica_c4.json` `e6f5a5db8268d0fbd379442b25267b9c6cb14204d530b19ad789def92d274250`.
- **As outras runs:** a C1 teve uma repetição interna depois de um conserto, com os mesmos logs; a GVN2 tem teste que refaz a leitura byte a
  byte. Nenhuma das oito foi refeita por alguém de fora (auditoria da A0, seção 1).

**O que isso não demonstra:**
- replicação externa: a mesma máquina, o mesmo Python 3.13.0, o mesmo agente; o que se mostrou é a **reprodutibilidade** do resultado a
  partir do código;
- que a run inteira da C4 se reproduz byte a byte;
- nada sobre a COOP A1, que não se refaz pelo repositório (as vidas não estão versionadas).

## 2. A tabela por hipótese

Os números das linhas C1 a COOP A1 saem da auditoria da A0 ([`AUDITORIA_EVIDENCIA.md`](AUDITORIA_EVIDENCIA.md), seção 1), que confere cada
sha256 contra o meta (`artifacts_v3_auditoria_evidencia/auditoria.json`
`c9a85f5f39ea8ae0a062662b314366cbc3af31699ece3fb5810dceba31ecf6b3`). Os `resultado.json` são citados pelo sha256 do blob na auditoria.

| experimento | o que foi testado | o resultado | permite concluir | não permite |
|---|---|---|---|---|
| **C1**, o longe regular | M3\* − M2, a taxa por episódio no `longe_fixo` | +0,0489 [+0,0355; +0,0624], n = 150, "> 0"; o sorteado −0,0106 [−0,0236; +0,0024], "indeterminado"; `resultado.json` `b1872745…` | com lugares fixos, a variante M3\* fecha mais episódios que a M2 | o ganho com lugares sorteados; nada contra uma baseline (ver A1) |
| **C2**, o crédito na intenção | M2c − M2, "ganhou, fica" | +0,0028 [−0,0003; +0,0060], n = 150, "≈ 0"; `5c7e51a5…` | a unidade de crédito do P2 não é a causa do problema do hábito | que nenhum crédito ajude |
| **C3**, redecidir por evento | M3\*R − M3\* no `longe_fixo` | +0,0124 [−0,0060; +0,0308], n = 150, "indeterminado"; `41869752…` | nada; a chave fica desligada | que o efeito seja nulo |
| **C4**, a memória autobiográfica | REL − SEM, − REC, − EMB (Holm) no `longe_fixo` | +0,0646 [+0,0515; +0,0778], +0,0560 [+0,0427; +0,0693], +0,0636 [+0,0507; +0,0764], n = 200 cada; guarda +0,1981; `6f8c91d8…` | a memória REL fecha mais episódios que as versões sem ela, com a ressalva do lugar lembrado (M-MEM) | que o REL vence uma política trivial (a A1 mostra que não); qual parte da memória explica o ganho (a D-C1-3 fechou descritiva) |
| **AN4**, o passeio | a guarda G-COMEDOURO-AN | −0,0263 [−0,0362; −0,0164], n = 200, "< 0", falha; MOV +0,0236; `70b7fc96…` | o passeio piora o comedouro; a chave fica desligada | o efeito do passeio com outro limiar ou raio |
| **GVN2**, o gosto visual | Spearman(Δ_I, dif_fica), descritivo | 0,823 [0,694; 0,886] na GV3 e 0,645 [0,485; 0,743] na GV3b; `leitura.json` `67eb6e8b…` | uma associação descritiva, que contradiz em parte a H5 | causa; sem correção para comparações múltiplas |
| **PET_VIVO**, a auditoria da escolha | a linha HA/HC/HP por grupo, pós hoc | "indeterminado" nos 6 grupos da C4; `auditoria.json` `3bb42d95…` | gerar hipóteses | confirmar qualquer uma |
| **COOP A1**, o irmão aleatório | EMERGE, DOSE, CUSTO | +0,0008 [−0,0014; +0,0039] e inclinação +0,0008 [−0,0014; +0,0039], n = 69, não confirmam; CUSTO +0,0009 [−0,0012; +0,0034], n = 80, confirma pela regra; `resultado_ad1.json` `d693f046…` | a cooperação não emerge com o irmão aleatório | nada além do registrado: as vidas não estão no git |
| **A1**, a baseline trivial | REL − TRIV no `longe_fixo` | −0,083 [−0,128; −0,038], n = 200, "< 0"; `706a687a…` | uma regra de quatro linhas fecha mais episódios que o REL | que o REL é pior para o pet; a melhor política trivial |
| **A2**, a ablação no jogo | A − B em 15 medidas (Holm) | 9 de 15 rejeitadas, todas < 0,01; TV 0,0084, n = 200; `ced7c793…` | o P1 e o P2 mudam o comportamento no jogo | relevância, bem-estar, qual regra |
| **A3**, a réplica da C4 | sha256 dos artefatos | `resultado.json` igual; `medidas.json` diverge (causa provável os tempos); `replica_c4.json` `e6f5a5db…` | o resultado da C4 se reproduz do código | replicação externa; a run inteira byte a byte |

## 3. O que os resultados, juntos, permitem concluir

1. **O método se sustenta no que foi auditado.** Nos oito experimentos, nenhum plano foi commitado depois da primeira vida (A0, seção 2c),
   com três casos não verificáveis pelo artefato (GVN2, PET_VIVO, COOP A1). As runs novas (A1, A2) gravam o comando e o SHA.
2. **Os mecanismos testados se comparam bem com versões do próprio modular** (C1, C4) e **mal com uma baseline trivial** (A1). As outras
   variantes (C2, C3, AN4) foram negativas ou indeterminadas, e as chaves ficaram desligadas.
3. **O aprendizado em vida tem efeito real no jogo, e pequeno** (A2).
4. **O resultado da C4 é reproduzível a partir do código**; não há replicação externa (A3).

## 4. O que não foi demonstrado

- que o modular é melhor que uma política trivial em qualquer medida com gate;
- que o modular é melhor **para o pet** (bem-estar, privação, exaustão): só há descritivos pós hoc (A1, seção 5);
- que o efeito do aprendizado é visível para o jogador (A2; o teste cego está só no papel);
- qualquer replicação por terceiro, em outra máquina ou outro ambiente;
- que a run inteira da C4 se reproduz byte a byte (a lacuna da A3);
- que os números da COOP A1 se refazem pelo repositório;
- qualquer coisa fora das células, dos donos sintéticos e das durações de cada run.

## 5. O que muda no veredito (interpretação)

Rotulado como interpretação: nenhuma regra escrita antes decide o que segue.

- **O diferencial não está na taxa de fechamento por episódio.** Nessa medida, a baseline vence. Se o produto quiser dizer que o modular
  cuida melhor de si, a medida tem de ser outra (bem-estar), definida num plano novo antes de rodar.
- **"Aprende em vida" é verdadeiro no motor, com efeito pequeno.** Para valer como diferencial de produto, falta mostrar que se vê (o teste
  cego) ou dar um canal que o mostre.
- **A poda (L5) é obrigatória** pela decisão do CHECKPOINT A2; o que podar não é decidido aqui.

## 6. O que fica para o Matheus (CHECKPOINT A4)

Esta síntese fecha o parecer. Nenhuma decisão nova é proposta aqui; as abertas que ela toca:
- o merge da A3 (#971);
- as LG-1 a LG-6 do teste cego de legibilidade;
- se vale fechar a lacuna da A3 (uma réplica com `--manter`, ~4 h) e se a medida primária das próximas runs passa a ser de bem-estar:
  ambas seriam planos novos.
