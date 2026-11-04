# TAREFA V3 — ACOES_NOVAS: o passo 3 da "Vida do pet", ações novas no cérebro (2026-11-04)

Coordenador: Gerente da V3 (Claude Code, Opus 5.5). Worker do papel: Claude Code, Opus 5.5, worktree e branch `v3-acoes-novas`.
Status: ABERTA, **só no papel**. Nenhum código, nenhuma vida e nenhum número novo de jogo; as decisões AN-1 a AN-7 (seção 8) são do Matheus.

Categoria: arquitetura. Origem: Matheus, 2026-11-04: o pet fica parado e não faz nada; o Matheus quer mais ações e movimento, sem treino por clique (2026-11-04).

**O pedido, nas palavras do Gerente:** o jogador precisa se entusiasmar e criar vínculo, e o pet "fica sempre parado". A frente "Vida do
pet" tem três passos: (1) o pet se move na vista (PR #561, aberto); (2) cada ação com uma cena visível, só na vista; (3) ações novas no
cérebro, que é esta tarefa. **A regra do Matheus que vale em toda a tarefa:** o aprendizado nunca pode ser baseado em o dono clicar carinho
ou tapa como recompensa ou punição, como era na v1.

**De onde parte:** a pesquisa de referências `docs/futuro/vida_do_pet_referencias.md` (PR #560, ainda fora da `main`; lida do branch
`origin/v3-vida-pet-ref`), seção 5.2: partir do modular, não do A; o vaguear primeiro; o seguir o dono só depois de um evento de presença
do dono; o toque com lugar no corpo depois.

**O que mudou no mesmo dia (#562, na `main` em `d0f7f17`):** o modular virou o cérebro padrão dos ovos novos (a **v17**, a v15 com o cérebro
trocável pelo evento `cb` do registro), e o A ficou selecionável em Ajustes › Laboratório. O custo de errar da pesquisa (5.2.1, "amarrar a
vida do pet a um cérebro que ainda não é o padrão") deixou de valer: o passeio, portado, chega ao pet normal do jogo, e não só ao de teste.
Isso pesa a favor da guarda (AN-1) e muda a versão do porte (AN-7).

## 0. Os cinco pontos

| ponto | resposta |
|---|---|
| a capacidade | o pet com o modular (o v17 e o de teste) sai para passear sozinho quando o corpo pede (o tédio, a curiosidade), com um destino que segura por algumas decisões, e volta às necessidades quando elas apertam |
| o marco que desbloqueia | o Matheus vê, num pet com o modular, o pet andar até um lugar e voltar, sem clicar nada, e o painel do modular mostra "passeio" com o motivo |
| a evidência | o G-PAR e o G-PAR-VIDA do passeio no espelho TS; o G2 (a chave desligada deixa o Python e o jogo byte a byte); a guarda G-COMEDOURO-AN no plano próprio (seção 4) |
| as dependências reais | o laboratório do modular e o cérebro primário na `main` (LM0 a LM5b; #562); as AN-1 a AN-7 decididas; o plano `PLANO_ANALISE_V3_ACOES_NOVAS.md` antes de qualquer vida |
| se o gate falhar | a subchave fica desligada, os pets seguem como hoje, e o resultado negativo é registrado como está |

## 1. Pergunta

**Um passeio sem alvo de necessidade, disparado pelo tédio e pela curiosidade que o corpo já tem, faz o pet com o DigiBrain modular se
mover mais e de forma legível, sem piorar o cuidado das necessidades perto do comedouro?**

- **De onde vem:** do pedido do Matheus (o "pet parado") e da recomendação 5.2.2 da pesquisa de referências. Não vem de uma hipótese do
  `docs/PLANO_V2_PESQUISA.md`: é uma mecânica do produto (`docs/PRODUTO_VISAO.md`), com o método da pesquisa porque mexe no cérebro.
- **O que não pergunta:** se o passeio aumenta o apego do jogador. Isso não se mede no Python, e a literatura verificada não traz estudo
  sobre qual mecânica aumenta o apego a um pet virtual (a pesquisa de referências, seção 6, "Não localizado").

## 2. Depende de

- **Na `main`, já:** o pacote `digilab/digibrain/` com a C4 (o braço REL); o laboratório do modular inteiro no jogo, o pet de teste v16
  (`docs/TAREFA_V3_LAB_MODULAR.md`, LM0 a LM5b); o modular como cérebro padrão dos ovos novos, a v17 (`docs/TAREFA_V3_CEREBRO_PRIMARIO.md`, #562).
- **Fora da `main`, e não bloqueia o papel:** a pesquisa de referências (PR #560) e o passo 1, o pet que se move na vista (PR #561). O
  marco da seção 0 (o Matheus vê o pet andar) precisa do passo 1 na `main`; o código do Python não precisa.
- **As decisões AN-1 a AN-7** (seção 8).
- **A vez em `digilab/digibrain/`:** o pacote é arquivo disputado (`docs/PAINEL_V3.md`, seção 3: uma missão por vez). A AN2 só começa sem
  outra missão da trilha C aberta nele.

### 2.1 O que já existe (lido no código da `main` em `a7c000f`; o #562 conferido em `d0f7f17`)

**O vaguear já existe no modular, como a unidade `explorar/vagar`.** O passo 3 não cria um verbo; ele muda como o verbo que já existe dura.

| peça | o que existe | onde |
|---|---|---|
| a unidade | o M-IMPULSO monta, em toda decisão, a unidade `explorar/vagar` (tipo de alvo `vagar`), ao lado do `explorar/cheiro` e do `explorar/ponto` (o lugar lembrado) | `digilab/digibrain/impulso.py`, `Impulso.alvos`; `TIPOS_ALVO_DIGIBRAIN` em `digilab/config.py` |
| o que a dispara | o W0 do `explorar` (PROPOSTO, SEM FONTE): viés S/8, **`u_tedio` S, `u_curiosidade` S**, F S/2, `fome_sem_comida` S/2, `u_energia` −2S. O tédio e a curiosidade já empurram o explorar | `ConfigDigibrainInatos.w0`, `digilab/config.py` |
| a exploração no sorteio | o M-AFETO dá o ganho `g_exp = clamp(e0 + mul(beta_T, tédio) − mul(beta_U, max u), 0, e_max)`, que o M-ARB soma às ativações positivas (`w = a + mul(g_exp, epsilon)`): o tédio abre o sorteio, e uma urgência alta o fecha | `digilab/digibrain/afeto.py`; `digilab/digibrain/arb.py`, `Arbitragem.pesos` |
| o tédio e a curiosidade no corpo | os drives da etapa 6 (`drives_novos`): o tédio sobe por tick acordado e cai com a variedade (bola, brincar, explorar, o dono brincar); a curiosidade só existe com o mundo físico e cai com a novidade. O modular roda com o corpo do v11 (a etapa 6 inteira, `CCO_V11`) e o mundo do produto | `digilab/corpo.py` (`NOVOS`, `ATIVIDADES`); `web/app/motor/constantes.ts`, `CCO_V11`; `experiments/run_v2_digibrain_prototipo.py` |
| o ponto do vagar | o motor sorteia, **a cada decisão**, um ponto a 4 a 12 células numa de 16 direções, pelo `u` da decisão (`vagar_min_celulas`, `vagar_max_celulas`) | `digilab/mundo.py`, `MotorMundo.candidatos` |
| a duração | **o vagar é opção de uma decisão só:** sem intenção I\*, sem compromisso C, sem persistência e sem frustração. A cada decisão o ponto é outro | `digilab/digibrain/estado.py`, docstring do módulo |
| a intenção com alvo fixo | o lugar lembrado (`explorar/ponto`) já é intenção: o ponto fixo, entregue ao motor como `Alvo.ponto`, com a meta "chegou ao lugar" (`ocorrido["chegou"]`), os fins `meta`, `trocou`, `sumiu`, `desistiu` e a persistência `h = mul(w_pers, C)` | `digilab/digibrain/estado.py`; `digilab/digibrain/adapt.py`, `escolher_alvo` |
| os gestos do dono | o M-ADAPT só os registra; **nenhum módulo os recebe como sinal**: o corpo os sente pelos receptores (a D-B do `PLANO_V2_PESQUISA`) | `digilab/digibrain/adapt.py`, docstring e `receber_acao_dono` |
| no jogo | o espelho TS de todos os módulos, com o G-PAR-VIDA em 5 376 decisões (LM4), no pet de teste v16; desde o #562, também o cérebro padrão dos ovos novos (v17), com o A selecionável pelo evento `cb` | `web/app/motor/digibrain/`; `docs/TAREFA_V3_LAB_MODULAR.md`, seção 14; `docs/TAREFA_V3_CEREBRO_PRIMARIO.md` |

**A leitura** [HIPÓTESE, SEM FONTE]: com o ponto novo a cada decisão, o vaguear de hoje é um zigue-zague de passos curtos em direções
sorteadas, e não um passeio que o jogador lê como "foi até ali". Quanto o vagar é escolhido no modular **não foi medido**: é a AN0.

**O achado do E0 que pesa aqui** (`docs/futuro/v3_espaco_acoes.md`, seção 0, [HIPÓTESE] do próprio documento): somar verbos sem abrir a
arbitragem dá opções quase nunca escolhidas. No modular a arbitragem já é um sorteio entre unidades (não a prioridade fixa do A), e a
V3-10 do mesmo documento recomenda "ações novas como ações com alvo, não membros do `AcaoPet`". O passeio segue as duas: nenhum membro
novo no `AcaoPet`, nenhuma unidade nova no M-IMPULSO.

## 3. Mudança mínima

### 3.1 O passeio: o vagar que segura o destino

Atrás de uma subchave nova da `ConfigDigibrain`, **`passeio`, desligada** (o nome é a AN-2):

1. **O que o dispara não muda.** O passeio começa quando o M-ARB escolhe a unidade `explorar/vagar`, que já tem o tédio e a curiosidade no
   W0 e o `g_exp` no sorteio (2.1). **Nenhum peso novo** (AN-3).
2. **O destino fica.** Na decisão em que o vagar é escolhido sem um passeio em curso, o M-ADAPT recebe do motor o candidato `vagar` daquela
   decisão (o ponto que o motor já sorteia) e o M-ESTADO abre a intenção I\* = (`explorar`, `passeio`, (x, y)). Nas decisões seguintes, a
   unidade do passeio em curso entra no lugar do `explorar/vagar` com o mesmo ponto, e o M-ADAPT o entrega ao motor como `Alvo.ponto(x, y)`,
   o caminho que o lugar lembrado já usa (`adapt.escolher_alvo`). O motor não muda.
3. **Os fins**, os do lugar lembrado, mais um:
   - `meta`: chegou ao ponto (o mesmo `ocorrido["chegou"]` do `explorar/ponto`);
   - `trocou` e `desistiu`: como hoje (o `desistiu` pelo `n_sp >= N_desiste`, sem número novo);
   - **`interrompido`** (novo, a guarda da 3.2): uma necessidade apertou.
4. **O crédito** é o da opção (PE-3): a elegibilidade da decisão que começou o passeio, o `r` somado, entregue ao P2 quando acaba; com a
   exceção da 3.3.
5. **Desligada,** nada disso existe, e a vida sai byte a byte: o vagar continua opção de uma decisão.

### 3.2 A guarda: o passeio nunca ganha das necessidades

O risco é o da pesquisa (5.2.2): se o vaguear ganha das necessidades, o pet some do comedouro. Duas camadas, uma no cérebro e uma no plano.

**No cérebro (a regra):**
- **A persistência do passeio só vale sem necessidade urgente.** O termo `persistencia` da unidade do passeio é 0 quando a maior urgência
  das necessidades passa de um limiar `lambda` (fome, higiene, energia e saúde; quais, e o limiar, são a AN-4). Sem a persistência, o
  passeio concorre no sorteio só pelo inato, como o vagar de hoje, e o `u_energia` −2S e o `g_exp` (que cai com a urgência) já o empurram
  para baixo.
- **E o passeio acaba `interrompido`** na decisão em que a urgência passa do limiar. O `interrompido` **não sobe a frustração F** (como o
  `achou` da DX-4): o F tem peso S/2 no próprio explorar, e um passeio interrompido que frustra empurraria o pet a explorar de novo, contra a
  necessidade (AN-5).
- **O reflexo do sono** (`arb.reflexo`) continua acima de tudo, como hoje: ele acaba o passeio com `trocou`.

**No plano (a medida):** a guarda G-COMEDOURO-AN, no molde da G-COMEDOURO da C3 (`docs/PLANO_ANALISE_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md`,
A8.4 e AD8-5): o contraste com e sem o passeio na taxa de fechamento por episódio de fome, nas células do comedouro, **falha só com a classe
"< 0"** de A6.6. A seção 4 diz o resto.

### 3.3 O dono não treina o passeio pelo clique

O modular já não dá o gesto do dono como sinal a nenhum módulo (2.1). **Mas o corpo sente o gesto:** o carinho baixa a solidão e o estresse
(`motor/corpo.ts:568` no jogo; `digilab/corpo.py`), e os dois são canais do `r` (só o susto fica fora, `fora_do_r`). Um carinho no meio de
um passeio entraria no `r` do passeio e subiria o hábito de passear: um treino por clique pela porta do corpo [HIPÓTESE: a AN0 confere no
código e nas vidas do gabarito se isso acontece de fato].

**A proposta (AN-6):** a opção do passeio que tem um gesto do dono (carinho ou tapa) no intervalo dela **não é entregue ao P2**; o motivo
registra `credito: "gesto"`. O precedente é o G-SEM-CREDITO do J5 (a comida na mão não credita a política). Só para o passeio: estender a
regra ao modular inteiro é outra decisão (seção 6).

### 3.4 Como o passeio aparece no log e no motivo

- **No log do motor: nada novo.** O log continua só as ações do dono e os avanços de tempo (event sourcing); o passeio é refeito pelo
  replay, como toda decisão do pet. **Nenhum tipo de evento novo**, e o replay de hoje não muda.
- **No motivo da decisão** (`adapt.motivos`, o que o painel do laboratório lê):
  - a ação `explorar` e o alvo `{"tipo": "ponto", "x", "y", "do_mem": false, "do_passeio": true}` (o campo `do_passeio` é novo; o
    `do_mem` continua dizendo se o ponto veio do M-MEM);
  - a intenção em curso `estado.I` com o tipo `passeio`, o C e o `n_sp`, como as outras intenções;
  - o fim (`meta`, `trocou`, `desistiu`, `interrompido`) em `fins`, com a contagem em `estado.fins`;
  - o crédito descartado pelo gesto (3.3), quando houver.
- **No painel do laboratório** (LM5b): a intenção em curso já aparece; mostrar "passeio" como nome é vista (o passo 2), fora desta tarefa.

### 3.5 O que não muda

- `digilab/engine.py`, o `AcaoPet`, o bandit e as runs da v1;
- o motor (`digilab/mundo.py` e o espelho TS): o ponto do vagar e o `Alvo.ponto` já existem;
- o cérebro A (`digilab/policies/lobos.py` e `web/app/motor/lobos.ts`), os pets v11 a v15 e o pet v17 com o A (`cb` A);
- o W0, o `g_exp` e todo valor de `ConfigDigibrainInatos` (AN-3);
- os gabaritos de hoje: nenhum é regravado.

### 3.6 As etapas (cada uma um PR, na ordem)

| etapa | o quê | onde | gate | modelo |
|---|---|---|---|---|
| **AN0** | o descritivo de hoje, **sem vida nova**: das vidas que já estão gravadas (os gabaritos da LM0 e os `fins` da LM4, sementes dos testes), a fração de decisões `explorar/vagar` por dono e por lugar, as corridas de vagar seguidas, o deslocamento por decisão, a urgência máxima nas decisões de vagar; e a conferência da 3.3 (o gesto entra no `r`?) | `experiments/medir_v3_acoes_novas_hoje.py`, `artifacts_v3_acoes_novas/hoje.json` | o artefato sai igual em duas execuções; nenhum número vira resultado (é descritivo) | Sonnet |
| **AN1** | o gabarito das vidas de hoje, num commit próprio, antes do código: confere se o `tests/gabaritos/genoma_g0_vidas_de_hoje.json` (as 10 vidas do modular REL) e os gabaritos da LM0 bastam; senão, um gabarito do modular com o vagar escolhido | `tests/` | o gabarito se regera igual duas vezes | Sonnet |
| **AN2** | o passeio no Python, atrás da `passeio` desligada (3.1 a 3.4), com testes | `digilab/digibrain/estado.py`, `adapt.py`, `impulso.py`; `digilab/config.py` | **G2-py:** desligada, os gabaritos da AN1 e todos os de hoje passam sem regravar; ligada, os testes dos fins, da guarda e do crédito descartado; o replay bit a bit | Sonnet; Opus se a guarda e a persistência se cruzarem de um jeito que a espec não previu |
| **AN3** | o plano de análise, **antes de qualquer vida**: `docs/PLANO_ANALISE_V3_ACOES_NOVAS.md` (seção 4), com a faixa pedida ao coordenador | `docs/` | o Matheus aprova o plano | Opus |
| **AN4** | a run única do plano, uma vez, nos lugares do MVP | `experiments/run_v3_acoes_novas.py` | os gates do plano; o negativo é registrado como está | Sonnet |
| **AN5** | o porte ao jogo, **só com a AN-7**: o passeio no espelho TS, a versão nova do pet (AN-7) e a paridade | `web/app/motor/digibrain/`, `web/app/motor/constantes.ts`, `web/app/test/` | **G-PAR** do M-ESTADO e do M-ADAPT com o passeio; **G-PAR-VIDA** nas vidas do exportador com a `passeio` ligada; **G1** o replay; **G2-web** desligada, os gabaritos de hoje e os pets v13 a v17 abrem iguais | Sonnet |

A ordem faz o Python primeiro (AN0 a AN4) e a web depois (AN5). A cena do passeio (o pet que anda até o ponto, a chegada) é o passo 2,
só vista, e não entra aqui.

## 4. Experimento e gate

O plano vem num documento próprio, **`docs/PLANO_ANALISE_V3_ACOES_NOVAS.md`** (a AN3), commitado antes da primeira vida. Aqui fica só o
que ele precisa medir, para o Matheus decidir a AN-1 com o custo à vista.

- **Plano de análise:** `docs/PLANO_ANALISE_V3_ACOES_NOVAS.md`, commitado antes da run (AN3).
- **Sementes reservadas:** nenhuma ainda. Uma faixa nova é pedida ao coordenador e entra em `experiments/bancada/faixas.py` antes da run;
  sem calibração (ela fica para a rodada de equilíbrio, no fim, como no `docs/TAREFA_V3_LAB_MODULAR.md`, seção 6).
- **Os braços:** **LAB** (a configuração do pet de teste, o braço REL da C4) contra **LAB+P** (a mesma, com a `passeio` ligada).
- **Os lugares:** os do MVP: o comedouro e o `longe_fixo`.
- **O que medir, PROPOSTO:**

| medida | o que é | papel |
|---|---|---|
| **G-COMEDOURO-AN** | LAB+P − LAB na taxa de fechamento por episódio de fome, nas células do comedouro (a unidade e o teste da G-COMEDOURO da C3) | **a guarda:** falha só com a classe "< 0" de A6.6 |
| a mesma no `longe_fixo` | idem, longe da ração | secundária: o passeio pode ajudar a achar a comida longe, ou atrapalhar a ida |
| a privação e a saúde | a fração do tempo em privação (`Config.limiar_privacao`) e a saúde ao fim | secundárias, só "pior ou não" |
| **o movimento** | a fração das decisões acordadas em que o pet sai do lugar, e a distância andada por dia | **o primário do produto:** o "pet parado" virando medida; leitura descritiva, com IC |
| os passeios | quantos por dia, a duração, os fins (`meta`, `trocou`, `desistiu`, `interrompido`) | descritivo |
| a urgência no passeio | a urgência máxima das necessidades nas decisões de passeio | descritivo: confere a guarda do cérebro |
| o crédito descartado | quantas opções do passeio caíram pela 3.3 | descritivo: confere a regra do clique |

- **Métrica e gate:** o primário do produto (o movimento) não tem limiar: um limiar seria número novo, e qual movimento basta é do
  Matheus jogando, não do Python (AN-1). A run passa se a guarda não falha; ela diz "o passeio move o pet" só se o IC do movimento ficar
  todo acima de 0.
- **GPU:** não. A máquina: até 4 processos, uma run por vez (V3-D8).
- **A alternativa (AN-1):** sem run, só o descritivo nas sementes dos testes e a decisão pelo jogo. Custo na seção 8.

## 5. Entrega

- Testes: `python -m pytest tests/ -q`; em `web/app`: `npm test`, `npm run tipos`, `npm run e2e` (se a frente toca a web).
- Registro: seção própria no fim do arquivo do mês, `docs/registro/AAAA-MM.md`, e uma linha no fim do índice `docs/REGISTRO_DESVIOS.md`
  (rodada de saúde, etapa 2). O resumo da etapa vai no corpo do PR e numa seção no fim do documento da
  frente (o `RESULTADO_V3_*.md` da run ou o `TAREFA_V3_*.md` da etapa), nunca no `CLAUDE.md` (rodada de saúde, etapa 1).
- PR contra a `main` com resumo e números (cada um com o artefato). Aviso ao coordenador. Merge só pelo Matheus.
- O corpo do PR segue `.github/pull_request_template.md`; o CI (`tools/verificar_relato.py`) confere os campos e a evidência da categoria.

## 6. Fora desta tarefa

- **O seguir o dono:** o dono não tem posição no mundo e o motor não registra a presença dele. Fica até existir um evento de presença do
  dono (a pesquisa de referências, 5.2.3 e 5.3), que é decisão de desenho própria porque mexe no replay.
- **O cérebro A e os pets v11 a v14:** nenhuma ação nova no A (a pesquisa, 5.2.1; o `AcaoPet` e o bandit congelado).
- **Qualquer treino por clique:** nenhum gesto do dono como recompensa ou punição, nem direto nem pelo crédito do passeio (3.3).
- **Estender a regra da 3.3 ao modular inteiro** (o carinho que entra no `r` de qualquer ação): fica como questão aberta para o Gerente; esta
  tarefa só fecha a porta do passeio.
- **O toque com lugar no corpo** (a pesquisa, 5.2.4), **o investigar um objeto novo** e **o brincar sozinho** como mudanças de cérebro: o
  investigar (`explorar/cheiro`, `explorar/ponto`) e o brincar com a bola já são intenções com alvo no modular (a pesquisa, seção 1); a
  cena deles é o passo 2.
- **A cena** do passeio, o nome "passeio" no painel e qualquer animação: o passo 2, só vista.
- **A D-C1-3** (de onde vem o ganho do M3\*) e o que o #562 deixou de fora (o selo do painel, a fala e o caráter lidos do A).
- **A calibração** do W0, do `g_exp` e dos limiares: a rodada de equilíbrio, no fim.

## 7. Critérios de aceitação

- **O papel (este PR):** este arquivo na `main`, com as AN-1 a AN-7 na seção 8, cada uma com a recomendação e o custo de errar; nenhum
  arquivo de código mudado (`git diff --stat origin/main` só com `docs/`).
- **AN0:** `artifacts_v3_acoes_novas/hoje.json` existe, sai igual em duas execuções, e a seção do resumo responde à conferência da 3.3.
- **AN1 e AN2:** com a `passeio` desligada, todos os gabaritos de hoje passam sem regravar (o teste da AN1); ligada, um teste por fim
  (`meta`, `trocou`, `desistiu`, `interrompido`), um da persistência zerada acima do limiar e um do crédito descartado pelo gesto.
- **AN3:** o plano commitado antes da primeira vida da faixa (o `git log` mostra a ordem).
- **AN4:** o `RESULTADO_V3_ACOES_NOVAS.md` com a guarda e o movimento, cada número com o artefato.
- **AN5:** o G-PAR-VIDA do passeio passa no `npm test`; o e2e do laboratório e o do cérebro primário passam; os pets v13 a v17 e os saves de hoje abrem iguais.

## 8. Precisa do Matheus

As sete decisões que o worker não toma. A recomendação vem primeiro; todas PROPOSTAS. Nenhuma traz número novo de jogo: onde uma decisão
pede um valor, a recomendação é reusar um que já existe.

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| **AN-1** | o passeio é pesquisa (plano e run única, AN3 e AN4) ou só produto (o descritivo nas sementes dos testes e o jogo) | **pesquisa, com a guarda G-COMEDOURO-AN como único gate.** O passeio mexe na disputa com a fome, e é a guarda que diz se o pet some do comedouro | só produto: um passeio que atrapalha a comida só aparece jogando, depois de portado, e o porte (AN5) teria de ser desfeito. Pesquisa: uma run a mais na fila da máquina (V3-D8), horas de vidas |
| **AN-2** | a forma: o vagar que segura o destino (3.1) ou uma unidade nova `explorar/passeio` ao lado do vagar | **o vagar que segura o destino, com a subchave `passeio`.** Nenhuma unidade nova no M-IMPULSO; o caminho do `Alvo.ponto` já existe e tem paridade | unidade nova: duas unidades de explorar sem alvo concorrem no sorteio, o explorar ganha peso sem ninguém decidir, e o G-PAR do impulso muda de forma. O vagar que segura: o pet perde o zigue-zague de hoje, que alguém pode preferir (a AN0 mostra quanto ele aparece) |
| **AN-3** | o que dispara o passeio | **o que já dispara o vagar: o W0 do `explorar` (o tédio e a curiosidade) e o `g_exp`, sem peso novo.** Se o pet ainda passear pouco, é a calibração do fim | um peso novo agora: um número sem fonte entra antes da rodada de equilíbrio (a regra "Calibração no fim") e mistura o efeito da duração com o da frequência na run |
| **AN-4** | a guarda no cérebro: quais necessidades e qual limiar zeram a persistência e acabam o passeio | **fome, higiene, energia e saúde, com o limiar `urgencia_lambda` que já existe na `ConfigDigibrainInatos` (S/2, PROPOSTO).** O tédio, a curiosidade, a solidão e o estresse ficam fora: são o que dispara o passeio ou o que o dono resolve | limiar alto: o passeio segura o pet com fome, e a guarda do plano falha. Baixo: o passeio quase nunca dura, e o pet volta ao zigue-zague. Um limiar novo: número sem fonte |
| **AN-5** | o `interrompido` sobe a frustração F? | **não** (como o `achou` da DX-4) | sobe: o F tem peso S/2 no explorar, e cada passeio interrompido pela fome empurra o pet a explorar de novo, contra a necessidade que o interrompeu |
| **AN-6** | o crédito do passeio com um gesto do dono no intervalo | **não é entregue ao P2, e o motivo registra `credito: "gesto"`** (3.3; o precedente do G-SEM-CREDITO) | entregue: o carinho no meio do passeio sobe o hábito de passear pelo corpo, e o dono treina o pet por clique, contra a regra do Matheus. Descartado: o passeio perde parte do crédito do corpo (quanto, a AN4 conta) |
| **AN-7** | o porte ao jogo (AN5) e a versão | **só depois da run (AN4), e só se a guarda não falhar; com uma versão nova (a próxima livre na `main` quando a AN5 começar), que herda a v17 com a `passeio` ligada no modular; o pet com o A (`cb` A) não muda.** A v17 continua abrindo igual, e o pet de teste v16 fica como está | portar antes: desde o #562 o modular é o cérebro padrão, e o jogador de todo ovo novo veria um passeio que pode estar tirando o pet do comedouro. Ligar na v17: os saves v17 de hoje mudam de vida no replay (a DM-5: cada mudança que altere a vida usa uma versão nova). Os pets v17 vivos passarem à versão nova (como a promoção v15 → v17 do #562) é decisão à parte, na AN5 |

## 9. Literatura

Só as linhas verificadas de `docs/referencias/referencias_verificadas.csv`, no que a coluna `o_que_sustenta` autoriza (a skill
`literatura-digilab`; verificação por metadados e resumo, não por texto completo).

| referência | DOI | o que autoriza dizer aqui |
|---|---|---|
| Oudeyer e Kaplan (2007) | `10.3389/neuro.12.006.2007` | separa a motivação intrínseca (a novidade, o progresso) da recompensa externa: o passeio pelo tédio e pela curiosidade é do primeiro tipo, e o clique do dono seria do segundo (3.3) |
| Kaplan (2000), sem DOI | — | a resistência e a "inutilidade" do pet artificial são parte do valor do vínculo: um pet que sai andando sem o jogador pedir não é defeito de desenho |
| Brooks (1986); Bryson (2003) | `10.1109/jra.1986.1087032`; `10.1007/3-540-36559-1_7` | arquiteturas por comportamentos, cada um operando por si (verificação por título e metadados) |

**SEM FONTE:** que o passeio aumenta o apego do jogador; que o zigue-zague de hoje parece "parado" ao jogador; o desenho da guarda, da
persistência e do crédito descartado; toda leitura marcada [HIPÓTESE]. **Nenhuma linha deste documento diz que o passeio é inédito:** pets
que andam sozinhos estão em quase todo jogo da pesquisa de referências (P2, "rotina e surpresa").
