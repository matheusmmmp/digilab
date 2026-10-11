# TAREFA V2 — DOIS PETS: dois pets de verdade no mesmo mundo (2026-10-07)

Coordenador: Gerente. Workers: A (motor e web), B (cérebro e corpo), D (bancada) e C (plano). Worktree e branch de cada etapa:
`v2-dois-pets-<etapa>`. Status: **ABERTA.**

**O que já está decidido** (pelo Matheus, em 2026-10-07):
- dois pets de verdade no mesmo mundo;
- DP-1 a DP-10, sendo a DP-4 (os sentidos) e a DP-7 (os donos) com mudança;
- DP-11 (visão e toque no degrau 1; audição e cheiro no 1b) e DP-12 (o cheiro de estado no degrau 3), as duas pela recomendação.

**O desenho:** `docs/futuro/dois_pets.md`. Esta tarefa põe em ordem, com dono e gate, o que o desenho propõe.

**Nenhuma run de pesquisa** sem o plano de análise (etapa 6), commitado antes.

## 1. Pergunta

Dois pets reais no mesmo mapa, competindo pela comida e percebendo um ao outro: **o B aprende algo que só o A viveu?** É o degrau 1 da escada
de `docs/futuro/cognicao_social.md` (o "aprendido de outros"). É a terceira via de informação ao lado do herdado (P0) e do vivido (P1), no
mesmo agente e com controles.

## 2. Depende de

- **Na `main` já estão:**
  - o `MotorMundo`, o instinto do mundo e o `MotorCorpo` no mundo;
  - a etapa 6 do corpo (drives novos, gestos e o grafo de reações, #245);
  - a bancada do mundo físico;
  - o motor em TypeScript.
- **A DP-11 (decidida):** a audição e o cheiro entram no degrau 1b (a etapa 8 abaixo).
- **A validação do mundo físico** vem antes de qualquer run desta frente: ela dá a referência do pet sozinho.

## 3. Etapas e donos

| etapa | dono | arquivos | entrega | gates |
|---|---|---|---|---|
| **0. gabaritos** | A | `tests/gabaritos/dois_pets_vidas_de_hoje.json` | as vidas do mundo físico de hoje, com e sem o corpo, nos dois layouts, gravadas **antes** da etapa 1 | — |
| **1. o `Mundo` como componente** | A | `digilab/mundo.py` (separar o `Mundo` do `MotorMundo`, como o `mundo.ts`) | com um pet, o `MotorMundo` é dono do próprio `Mundo`; a atualização do mundo fica idempotente por tick | **G2** (os gabaritos da etapa 0, `mundo_vidas_de_hoje.json` e `corpo_mundo_vidas_de_hoje.json`), G-ENGINE, a suíte de sempre |
| **2. o `Grupo`** | A | `digilab/grupo.py` (novo), `ConfigGrupo` no fim de `config.py` | N motores sobre um `Mundo`; a vez sorteada no fluxo `mundo-ordem` (DP-2); as sementes do grupo; o registro do grupo com cabeçalho, destino e o campo de origem para o dono (DP-3); o `reproduzir_grupo`; a entrada de um pet depois do tick 0 | **G2** com um pet no grupo, **G1-GRUPO**, **G-ORDEM**, **G-NUMS-GRUPO** |
| **3. visão, toque e disputa (degrau 1)** | A | `digilab/mundo.py`, `digilab/policy.py` (só o campo `Observacao.social`, com padrão `None`) | a `PercepcaoSocial` com a visão (5.1) e o toque (5.2: o contato na mesma célula ou na vizinha, com os tipos disputa, encostar e esbarrar); os candidatos `seguir` e `onde_comeu` no explorar; a disputa (o primeiro na vez come, o segundo não acha: MF-2); os registros para as medidas (disputas e quem ganhou, contatos, idas a `onde_comeu`, tempo à vista) | **G-RECEPTOR-SOCIAL**, **G-SENTIDOS** (visão e toque), **G-MEC-SOCIAL**, o G2 de novo |
| **4. o cérebro A no grupo** | B | `digilab/policies/lobos.py` (atrás de uma chave) | o alvo aprendido por classe de candidato, com o prior do padrão e o peso pequeno nas outras classes (PROPOSTO); as entradas sociais (visão e toque) nas regras de tempo livre, com prior 0; o modelo dos outros (familiaridade, confiança por atividade, afinidade) só registrado (DP-8); o embrulho repassando o que for novo | com a chave e sem o grupo, a vida de hoje (**G2**); **no prior, o P0 com lobos é o instinto do mundo byte a byte**, também com o outro à vista; **G1**; a conta exata do alvo aprendido; o modelo dos outros não muda a decisão |
| **4c. a rota do canal do humor no mundo físico (PDP-7, DECIDIDA em 2026-10-11)** | B | `digilab/policies/lobos.py` (o crédito do canal do humor no `consequencia_mundo`, hoje uma falha alta) | o canal do humor da fruta comida no mundo físico chega aos pesos que leem a fruta, como nos mundos das frutas; a montagem completa do plano roda com os canais (o nó `canais_fruta_mundo` da bancada, #264, sai) | com a chave dos canais desligada, a vida de hoje (**G2**); a soma dos canais igual ao escalar (o contrato K-6); **G1**; a conta exata de um crédito do humor |
| **5. a bancada do grupo (um dono)** | D | `experiments/bancada_v2.py`, `digilab/metrics.py`, `experiments/configs/v2_dois_pets/` | o grupo como célula, **com um dono e orçamento por pet** (DP-7, a validação inicial); o A experiente que entra K dias antes; os braços B só, B + A informativo, B + A embaralhado e B + A ingênuo (DP-9); o mundo com o efeito por tipo de árvore e o desarranjo do embaralhado; as medidas do plano; as faixas e o prefixo `dois_pets`, quando o plano os der | o G1 de todo grupo; **o B só é a vida de hoje** com a mesma semente; os braços com as mesmas ordens sorteadas quando a composição é a mesma |
| **6. o plano de análise** | C | `docs/PLANO_ANALISE_V2_DOIS_PETS.md` | a pergunta; as medidas; o contraste primário (B + informativo contra B + embaralhado); a calibração (só o que for do mundo e do K, sem o primário); as sementes novas; o gate e a regra de decisão | commitado **antes de qualquer run** |
| **7. o segundo dono** | A (o registro e o laço do dono) e D (a bancada) | `digilab/grupo.py`, `experiments/bancada_v2.py` | um dono por pet (DP-7, o objetivo): cada um com a própria política, o próprio orçamento e as próprias rngs, e a origem `dono:<id>` no registro | **G-DONOS:** dois donos de mesmo comportamento reproduzem byte a byte a vida com um dono só; o G1 do grupo. Só depois os donos podem diferir, por plano próprio |
| **8. audição e cheiro (degrau 1b)** | A (o som e o rastro no mundo) e B (o emissor externo no grafo do corpo, seção 18 da tarefa do corpo) | `digilab/mundo.py`, `digilab/corpo.py`/grafo, `digilab/policies/lobos.py` (as entradas) | a audição (5.4: os sons `comendo`, `bola`, `chamado`, `emburrado`, com direção e distância); o cheiro próprio e o rastro (5.3), como emissores externos de intensidade constante, sem químico; as entradas no cérebro com prior 0 | **G-SENTIDOS** (audição e cheiro); **G2**; as checagens do grafo do corpo passam com o emissor externo; **G-RECEPTOR-SOCIAL** |
| **8b. os órgãos do olfato e do ouvido (DP-13 e DP-14 DECIDIDAS em 2026-10-11: duas narinas e dois ouvidos, atrás de chave desligada)** | B (o receptor com limiar, adaptação e saturação no grafo do corpo), A (a intensidade só no ponto da narina e do ouvido, a direção do último passo, os candidatos `cheiro_seguir` e `cheiro_virar` no lugar do `cheiro`) e D (o braço "órgão × leitura pronta") | `digilab/corpo.py`/grafo, `digilab/mundo.py`, `ConfigOlfato` no fim de `config.py`, `experiments/bancada_v2.py` | o órgão atrás de chave desligada, com as sub-chaves `outro_pet` (o cheiro e o som do outro, junto da etapa 8) e `comida` (o cheiro da comida) separadas; desenho em `docs/futuro/dois_pets.md`, seção 5.6 | **G2**; **G-ORGAO-MEC**; **G-SEM-DIRECAO**; as checagens do grafo do corpo; **G1**; a medida só por adendo de plano |
| **9. o grupo em TypeScript** | A | `web/app/motor/grupo.ts` e a paridade | quando o produto voltar (o v11 está pausado) | **G-PAR** |

**O cheiro de estado** (estresse, medo; DP-12) fica fora desta tarefa: entra no degrau 3, com a solidão e a aglomeração.

**A ordem:**
1. **O motor:** 0 → 1 → 2 → 3, em paralelo com as etapas 7 e 8 do corpo.
2. **O cérebro e a bancada:** a etapa 4 (B), já com a etapa 6 do corpo na `main`, e depois a 5 (D).
3. **O plano (6):** pode ser escrito em paralelo, mas é commitado antes de qualquer run.
4. **A validação do degrau 1,** com um dono.
5. **Depois dela,** a etapa 7 (o segundo dono, DP-7) e a 8 (a audição e o cheiro, pela DP-11), em qualquer ordem. Cada uma tem o seu gate e,
   se medir algo, o seu adendo de plano.
6. **A etapa 9,** quando o produto voltar.

Um PR por etapa, com o relato no corpo. **O merge é do Matheus.**

## 4. Experimento e gate

- **O plano:** `docs/PLANO_ANALISE_V2_DOIS_PETS.md` (etapa 6), commitado antes da run, com o lugar dos adendos das etapas 7 e 8 previsto. A audição e o cheiro (etapa 8) e o segundo dono
  (etapa 7) entram por adendo, também antes da run deles.
- **As sementes:** faixas novas fora de `FAIXAS_RESERVADAS`, propostas pelo plano e registradas pelo D.
- **A medida e o gate:** são do plano. O desenho só aponta o contraste primário (seção 11).
- **GPU:** não.

## 5. Fronteiras (o que não muda)

- **`engine.py`:** o sha256 de sempre.
- **O `AcaoPet`:** nenhum membro novo. Os candidatos sociais são alvos, e a comunicação (degrau 2, fora desta tarefa) seria sub-decisão do
  `chamar_atencao` (DP-6). **O som não é mensagem.**
- **Os pets v1 a v10 e a web de hoje:** iguais. Nenhuma versão de pet nova nesta tarefa.
- **Com a chave do grupo desligada, ou um pet só,** tudo é byte a byte como hoje (G2), inclusive com os sentidos: sem o grupo, o mundo não
  guarda rastro nem som.
- **Nenhum sentido lê o estado interno do outro:** só o que é físico ou emitido por um emissor declarado no grafo do corpo.
- **Nenhum sinal de reforço sai do outro pet,** e nenhum parâmetro passa de um cérebro ao outro.
- **Sem agressão entre pets** (CV-3).

## 6. Entrega de cada etapa

- **Os testes:** `python -m pytest tests/ -q`. Em `web/app`, `npm test` e `npm run tipos`, só na etapa 9.
- **O registro:** uma seção própria no fim do `CLAUDE.md` e do `docs/REGISTRO_DESVIOS.md`.
- **O PR** vai contra a `main`, com o resumo e os números, cada um com o artefato. O relato vai no corpo do PR.

## 7. Fora desta tarefa

- **O degrau 2,** a comunicação (`COMIDA(lugar)`).
- **O degrau 3:** a relação e o modelo dos outros decidindo; a solidão e a aglomeração no corpo; o cheiro de estado (DP-12).
- **Os degraus 4 em diante.**
- **A agressão entre pets.**
- **A visita do pet de outro jogador.**
- **A tela.**
- **O ego social.**
