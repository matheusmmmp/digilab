# Contexto do Digilab — pesquisa e projeto (até 2026-09-29)

Documento para passar a outra LLM. Leia inteiro antes de qualquer tarefa. Os números vêm do `CLAUDE.md` do
repositório e dos artefatos citados; **se for usar um número, confira no artefato, não neste texto**.

> **Nota (2026-10-24):** este contexto é de 2026-09-29. Duas coisas mudaram: o repositório é público, e a regra dos sprites da
> Bandai ("privado", "só uso pessoal", "nunca os sprites da Bandai" em material publicado) foi retirada pelo Matheus em
> 2026-10-22 e 2026-10-24 (relatado pelo Gerente; `docs/UI_GUIDELINES.md`, seção 5.1). A direção do cérebro também mudou
> (`docs/ARQUITETURA_DIGIBRAIN_MODULAR.md`).

## 1. O que é

- **Projeto de pesquisa pessoal do Matheus.** NÃO é a pesquisa de mestrado dele (o mestrado é outro tema, no
  PPGCC/UFSC). Nunca associar os dois.
- Um **pet virtual evolutivo e competitivo com IA**, inspirado em Tamagotchi/Digimon. O dono cuida e treina o pet
  por feedback; o pet tem memória, personalidade e traços persistentes; pets de donos diferentes lutam numa arena.
- Diferencial pretendido: o comportamento do pet é **ensinado pelo dono, não roteirizado**, e isso é testado de
  forma falsificável, com braços de controle e o mesmo volume de interação.
- Repositório: `D:\Trab\digilab\v1`, GitHub `matheusmmmp/digilab`. Tem que continuar **privado**: a versão web usa
  sprites da Bandai (Digimon UP), sem licença, só para uso pessoal.

## 2. Hipóteses e vocabulário

- **H-central:** treino por um dono coerente produz um pet melhor que feedback aleatório com o mesmo volume de
  interação (em simulação, sem humanos). **Estado: refutada na confirmatória** (seção 4).
- **H-legibilidade** (especificada, não testada com humanos): o jogador só valoriza o aprendizado se o perceber.
- **H-explicação:** uma LLM traduz o motivo estruturado da decisão em linguagem natural sem inventar causa, se for
  presa aos fatos. Testada em simulação (seção 6).

Rótulos obrigatórios: **EXECUTADO** (código + run + artefato), **ESPECIFICADO** (só especificação), **IDEIA**.
Parâmetros: DECIDIDO ou PROPOSTO. Em 2026-09-29 o Matheus referendou todos os campos PROPOSTOS
(`protocol.REFERENDO`); valores novos voltam a contar como não referendados.

## 3. Regras do projeto (não negociáveis)

- **Não aumentar escopo.** Só o que a tarefa pede. Exceções autorizadas ficam registradas no `CLAUDE.md`.
- **Determinismo:** mesma semente + mesmo log = mesmo resultado, até o último float. Replay quebrado para tudo.
  - Exceção (2026-09-28): **modo livre gravado**. LLM e acaso real decidem ao vivo, toda saída não determinística vira
    evento no log e o replay lê o evento. O modo determinístico continua padrão e o único válido para confirmatória,
    protocolos com hash e paridade Python/web.
- **Event sourcing:** o estado do pet nunca é salvo, só o log (ações do dono + avanço do tempo).
- `digilab/engine.py` congelado (sha256 conferido em `protocol.py`). Parâmetros só em `digilab/config.py`.
- Só biblioteca padrão dentro de `digilab/` (verificado por AST). Falhar alto: nada de `dropna`, default silencioso
  ou `except: pass`.
- RNG do ambiente e RNG da política separadas. Métricas existem uma vez só (`digilab/metrics.py`).
- **Nenhum número em resultado sem artefato em disco** que o produza.
- Plano de análise congelado **antes** da run. Desvios em `docs/REGISTRO_DESVIOS.md`. Sementes de calibração
  separadas das de validação.
- LLM liberada desde 2026-09-24, quando a tarefa pedir. Fala livre: só modelos locais (Ollama). API paga do Claude:
  teto total de US$ 2, chave só no ambiente do servidor.
- Toda mudança de jogo vai também para o jogo web, na mesma entrega.
- Na tela do jogo os nomes são os do Digimon (formas, NPCs, níveis Rookie/Champion…, brasões Coragem/Amizade/
  Conhecimento/Sinceridade). Ids internos (bebe, crianca, brasa…) ficam só no motor, log e save.
- Comentários e docstrings em português, sem acento em identificadores.

## 4. Linha do tempo da pesquisa e resultados

Todas as runs abaixo estão EXECUTADAS, com artefatos em `artifacts*/`.

| etapa | artefato | resultado |
|---|---|---|
| Arena V1 canônica (5 sementes) | `artifacts/` | atencioso × aleatório 0,72 [0,64; 0,82]; só trocar o sorteio das partidas derrubou para 0,61 |
| Ablação treino × cuidado | `artifacts_ablacao/` | efeito do treino 0,14 [0,00; 0,28], não distinguível de 0. **Superada** (2026-09-29) |
| Memória curta / por espaços / emoção e habituação | `artifacts_v1_memoria*/`, `artifacts_v1_habituacao/` | memória muda pouco (≈7% dos motivos citam memória); bootstrap sobre sementes sem evidência de efeito na divergência |
| Personalidade (temperamento, vínculo, obediência, desejo) | `artifacts_v1_personalidade/` | central 0,615 [0,45; 0,77], inconclusivo; obediência separa donos (+0,147), **vínculo não** (aleatório fica com o vínculo mais alto: desenho a revisar) |
| Combate V2 e V2.1 originais | `artifacts_combate_v2/`, `_v21/` | REPROVADOS (V2: G4, G5; V2.1: E1–E5) |
| Combate corrigido V2C / V21C | `artifacts_combate_v2c/`, `_v21c/` | APROVADOS com ressalvas; exceções aceitas pelo Matheus: E2 (Ferrugem domina, falta ciclo entre espécies), E4, G6b, G8 |
| Treino, "forçar" e formas sombrias | `artifacts_treino/` | forçar não compensa (vínculo 0,22 × 0,56; 4/10 exigentes viram sombrios); gates S1 e S2 passam |
| Campanha contra NPCs | `artifacts_campanha/` | todo pet treinado vence cada NPC (0,81–0,97); não separa mais os donos |
| Escala de stats | `artifacts_progressao/`, `_v21c/validacao_escala` | 4 de 5 NPCs nas metas; Sentinela é exceção aceita |
| Análise de poder | `artifacts_poder/` | ovos dominam a variância (ICC 0,74 no desenho A); Δ = 0,10 pede ~135 ovos no A, ~40–44 no B |
| **Confirmatória** (desenho B, condição neutra, 160 ovos) | `artifacts_confirmatoria/resultado.json` | atencioso − aleatório **−0,034 [−0,072; +0,006] → H-central REFUTADA**. Secundárias (Holm): relapso, incoerente e exigente abaixo do aleatório. Descritivo: no desenho A com condição real o atencioso fica em 0,58 [0,52; 0,64] — a vantagem vem da condição física (cuidado), não do ensino |
| Exploratória V3: educação, lesões, morte, qualificação | `artifacts_educacao/` | atencioso − aleatório +0,121 [+0,066; +0,175]; cerca de metade vem das mortes do aleatório (sem mortes, pós hoc: +0,058) |
| V3b: "luta treina" | `artifacts_educacao_v3b/` | 577/640 pets viram forma sombria → desligado; equilíbrio dos estilos virou tarefa de game design |
| V3c: 24 personas geradas por LLM (gemma2:9b) × 40 ovos | `artifacts_educacao_v3c/` | braços fixos repetem a V3 (+0,139); entre as personas só o **limiar de cuidado** tem efeito (+0,065 [+0,008; +0,115]); coerência do feedback e perfil de treino sem efeito detectável |

**Leitura atual:** o ensino por feedback, como está modelado, não produz pet melhor; o que diferencia os donos é o
cuidado (saúde, condição, mortes). O bandit mexe pouco na política (JSD entre braços ≈ 0,02 bit, no limiar), e os
ovos dominam a variância.

## 5. Em andamento agora: programa da linhagem (lente de Vida Artificial)

- `docs/PLANO_LINHAGEM_ALIFE.md`: plano (só planejamento) de linhagem por procriação, com os experimentos E1 a E5.
  O Matheus autorizou como exceção de escopo **só o E1**.
- **E1 — natureza × criação**, plano congelado em `docs/PLANO_ANALISE_LINHAGEM.md` (2026-09-29), branch
  `plano-linhagem-alife`, script `experiments/run_natureza_criacao.py`:
  - separa **genoma** (semente g: espécie e temperamentos do ovo) de **ambiente** (semente r: motor, dono,
    travessuras, lesões, sparring), sem mexer no motor; com g = r reproduz a V3 byte a byte;
  - desenho: 40 genomas × 4 donos (atencioso, aleatório, permissivo, relapso) × 4 ambientes = 640 vidas; rodada 1
    com espécie fixa (brasa, principal), rodada 2 com espécies balanceadas (descritiva); painel B, condição neutra;
  - análise: ANOVA de 3 fatores cruzados (método dos momentos), bootstrap "pigeonhole" (McCullagh 2000), 10 000
    reamostras;
  - **gate:** limite inferior do IC95 de σ²_genoma > 0. Se falhar, E2 (herdabilidade pai-filho) e E3 (linhagem 2×2)
    não seguem com este genoma;
  - **estado:** piloto feito (32 vidas, só confere o pipeline); rodada 1 **rodando** (245 de 640 vidas em
    2026-09-29 19:17). Sem resultado ainda.
- Decisões em aberto do Matheus para depois do E1: 1 ou 2 genitores; o que acontece se falhar na condição de
  procriar; σ da mutação, gerações até o estágio 5 e teto de ganho; critério de procriar; destino do estágio 5.
- Banco de ideias: `docs/IDEIAS_PROGRESSAO_PERSONALIDADE.md` (prompt de pesquisa sobre progressão, personalidade,
  herança, medalhas e endgame; não rodado).

## 6. Fala do pet por LLM

- **Moldura** (EXECUTADA, desligada por padrão): a LLM só escreve abertura e fecho no tom do humor; o miolo é
  sempre a frase verdadeira de `digilab/expressao.py`, então não dá para inventar causa. qwen2.5:3b, `fala-v6`:
  191/200 na semente 20260928; 92% na semente 20260929. Caractere quebrado do modelo agora barrado.
  **Pendente:** leitura do Matheus em `artifacts_fala/ollama_qwen2.5-3b_fala-v6_s20260929/revisao.csv` (coluna s/n).
- **Fala livre** (EXECUTADA, aprovada só com **gemma2:9b**, PR #49, `modo_fala` desligado por padrão):
  - pacote `digilab_fala_livre/` fora de `digilab/`: bloco de FATOS com ids, prompt `livre-v2`, verificador
    `verif-v3` (LLM extrai afirmações e um juiz confere se cada uma tem fato) e log de apresentação separado; nada do
    que o jogador escreve ensina o pet;
  - rodada 2 (`artifacts_fala_livre/rodada2/RELATORIO.md`): gemma2:9b 3,0% das falas com afirmação sem fato (teto:
    o juiz marca 10% da moldura, que só diz verdades), 0/30 conversas inventaram, latência p90 4,8 s (RTX 2060);
    qwen2.5:7b 25,5% e qwen2.5:3b 46% reprovados;
  - **pendentes:** avaliação cega do Matheus (`artifacts_fala_livre/rodada2/avaliacao_cega.csv`, 60 pares) e
    confirmar se os dois "Não me deixe…" do qwen2.5:7b contam como manipulação.
- O motivo do bandit sem fator e sem exploração agora diz "Foi instinto: é o meu jeito." (antes "Não sei, só quis.").

## 7. O jogo web

- Desde 2026-09-28 o jogo é o app **Vite + TypeScript + Preact** em `web/app/`: motor puro em `web/app/motor/` (sem
  DOM), telas em `web/app/src/`, testes de paridade (Vitest) contra gabaritos do HTML antigo e ponta a ponta
  (Playwright). `web/digilab_sprites.html` virou versão antiga (`?antigo=1`) e referência dos gabaritos.
- Servido por `python servidor/servidor_local.py` em `http://localhost:8765/v1/web/dist/` (após `npm run build`);
  o servidor também expõe a fala por LLM. Acesso remoto só por túnel com `--remoto`.
- Funcionalidades: cuidado e necessidades, treino, evolução em 4 espécies × 15 formas (60 Digimon), combate V21C,
  gambits híbridos (só na web), campanha com mapa (Campina → Torre → Cidadela, boss final Piedmon), pets v4 com
  educação, lesões, morte, qualificação e herança (cruzar dois adultos), vários pets, tutorial com o Professor
  Agumon, jornada completa (brasão → ovo → boss → conclusão), ritmo de crescimento escolhido no ovo, importar e
  exportar pet, nova geração e Diário · Gerações, conversa com a fala livre.
- Layout: celular abaixo de 900 px, barra lateral de 900 a 1099 px, desktop (pranchas `*Desktop`) de 1100 px em
  diante. Conversar fica no cabeçalho do Pet no celular e no pé da barra lateral no desktop.

## 8. Pendências e decisões do Matheus

1. Resultado do gate do E1 (em andamento) → decidir se E2/E3 seguem e as decisões abertas da linhagem.
2. Avaliação cega da fala livre; leitura s/n da moldura; os dois "Não me deixe…" do 7b.
3. Combate: E2 pede espécies com identidade que gere ciclo (redesenho, não calibração); E4 pede redesenho do
   adolescente ou da passiva do adulto; equilíbrio dos estilos sob "luta treina" (V3b).
4. Vínculo precisa de redesenho antes de ser usado como medida de coerência.
5. Recusa do pet (B2) exigiria mexer no motor: decisão do pesquisador.
6. Gambits híbridos no Python: adiados (nenhuma pergunta atual depende deles).
7. Estudo com humanos: IDEIA; exige comitê de ética antes de qualquer coleta.

## 9. Literatura (existência confirmada, conteúdo ainda a extrair)

- Trabalhos: *Purr-ogrammed love* (revisão sobre pets virtuais); iPET (ACL 2025); *Designing Virtual Animal
  Companions*; MineRL BASALT; *From Pixels to Partners* (2024, treino por reforço × repetição em pet digital:
  provavelmente o mais próximo da hipótese).
- Produtos: AI Arena (treinar lutadores de IA que lutam sozinhos: o parente mais próximo da arena); Moflin;
  Sweekar; Peridot (LLM no pet); AI Tamago; Animal-AI Environment.
- Trilhas: criaturas que aprendem em jogos (Creatures, Black & White); aprendizado por feedback humano
  (TAMER/COACH); companion AI; explicabilidade de RL para leigos; fidelidade de LLM como explicador; efeito IKEA
  em agentes; avaliação de jogos competitivos (não transitividade, equilíbrio); Vida Artificial (linhagem, Baldwin).
- O que ainda parece sem equivalente: teste falsificável com controles e mesmo volume de interação; ensino por
  feedback esparso; separação ensino × cuidado; explicação verificada contra a causa real. A revisão precisa
  confirmar ou derrubar isso.

**Padrão de citação:** a referência tem que existir **e** sustentar a afirmação. Nunca inventar autor, ano, DOI ou
citação; se não achar, dizer que não achou. Fonte de fã/wiki só como pista.

## 10. Como trabalhar com o Matheus

- Responder em português brasileiro, direto, com a recomendação em vez de uma lista de opções.
- Não sugerir aumentar escopo; decisões de escopo são dele.
- Separar sempre o que o artefato diz da interpretação.
- Material publicado (artigo, apresentação, demo) usa só arte original ou licenciada, nunca os sprites da Bandai.
- Mudança de jogo: Python e web juntos. Uma branch e um commit por etapa; nada vai para `main` sem ele decidir.
