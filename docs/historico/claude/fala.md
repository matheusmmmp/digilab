# A fala por LLM e a fala livre

Seções movidas inteiras do CLAUDE.md da raiz na etapa 1 da rodada de saúde (`docs/TAREFA_V2_SAUDE.md`, 2026-10-13). As regras do
servidor que valem hoje estão em `servidor/CLAUDE.md`.

## Fala por LLM (Parte C, 2026-09-24)

**Provedores** (`--provedor`, padrão `auto`): **Ollama local** (`qwen2.5:3b`, sem custo, padrão
quando está rodando) ou **API do Claude** (abaixo). Para o Ollama: instalar pelo site oficial e rodar
`ollama pull qwen2.5:3b`. Validação, cache e queda para o template são os mesmos para os dois.
Avaliação: `python experiments/avaliar_fala.py` → `artifacts_fala/<provedor>_<modelo>/` (fração
barrada + `revisao.csv` com 50 falas aprovadas para revisão humana).

Especificada em `docs/TAREFA_MEMORIA_EXPRESSAO.md` (Parte C). Só o TEXTO da fala do adolescente e
do adulto no jogo web; motivo, decisões, registro, replay e artefatos não mudam e continuam só com
templates. `servidor/servidor_local.py` serve a mesma pasta que o `http.server` servia (mesmos
endereços) e expõe `POST /api/fala`; a chave fica no ambiente do servidor (`ANTHROPIC_API_KEY`),
nunca na página. Modelo padrão `claude-haiku-4-5` (mais barato e rápido; `--modelo` troca), saída estruturada
`{texto, fatores_citados}`; com `claude-opus-5`/`claude-fable-5-1` usa esforço `low` e fallback de
recusa do servidor da API (o Haiku rejeita `effort`; recusa nele cai no template). A resposta é validada
(fatores ⊆ motivo, marcadores de fatores ausentes, "não sei" sem fator, limite de fatores por estágio,
números ⊆ evento_ref e parâmetros); qualquer falha, erro, recusa ou limite (30/min) cai no template.
Cache por motivo+estágio+faixa de humor. Chave "fala por LLM" na página, desligada por padrão.
**Teto de gasto TOTAL de US$ 2** (`--limite-usd`): antes de cada chamada reserva o custo máximo
(resposta limitada a 300 tokens); se passaria do teto, não chama e usa o template. Acerta pelo `usage`
real; erro sem `usage` conta o pior caso. Acumulado em `servidor/gasto_fala.json` (fora do git): não
zera ao reiniciar; para liberar mais, aumente `--limite-usd` ou apague o arquivo. Modelo sem preço
na tabela `PRECOS_USD_POR_MTOK` não liga. Proteção adicional recomendada: limite de gasto do
workspace no Console da Anthropic.
**Alerta por e-mail** (`servidor/alerta.py`): ao cruzar 50%, 80% e 100% do teto (ou quando uma
chamada é recusada por falta de teto) manda e-mail para `--alerta-email` (padrão
matheusmmmp@hotmail.com), uma vez por nível (gravado em `gasto_fala.json`). SMTP só por ambiente:
`DIGILAB_SMTP_USUARIO`, `DIGILAB_SMTP_SENHA` (senha de app), `DIGILAB_SMTP_HOST` (padrão
smtp.gmail.com), `DIGILAB_SMTP_PORTA` (587). Sem essas variáveis o alerta fica desligado (avisa na
partida); o teto vale do mesmo jeito. `--testar-alerta` manda um e-mail de teste e sai.
**Entrada da página é não confiável**: `motivo_de_dict` só aceita ação, fator e parâmetros do
catálogo (V2 e V2.1), no máximo 4 fatores e 10 referências; texto livre nunca chega ao prompt.
As tabelas de `digilab/expressao.py` cobrem as técnicas e as condições do V2.1 (mesmos textos da web).
**Avaliação C6** (Ollama `qwen2.5:3b` na RTX 2060, 200 motivos reais — vida, combate V2 e V2.1 —,
metade com fator, semente 20260924; números de `artifacts_fala/*/resumo.json` e `falas.jsonl`):
- prompt `fala-v1`: 114/200 aprovadas (0,57). Adulto 88/100; adolescente 26/100, porque o pedido
  se contradizia (recebia todos os fatores mas só pode citar o primeiro; o exemplo sem fator não
  dizia "não sei", que a regra exige).
- prompt `fala-v2` (corrige as duas contradições, **olhando esta mesma amostra**: não é validação
  independente): 183/200 (0,915); adolescente 95/100, adulto 88/100. 14/200 foram barradas por pôr na
  lista `fatores_citados` um nome fora do motivo (ex.: `turno_12`, `evento_ref`, `Brinquei`); o texto
  delas não foi guardado, então isso NÃO mede quantas inventavam causa (correção de um relato
  anterior que dizia "7% inventaram causa"). O adulto copiava a frase pronta em 68/88 aprovadas.
- `fala-v3` (pedido do Matheus: personalidade e tom pelo humor; temperatura 0,7; semente nova
  20260925): 108/200; quase nenhuma cópia, mas **aprovadas inventavam causa por sinônimo** (ex.:
  "queria que você me ajudasse a descansar"). Não usar.
- **Moldura (`fala-v4` em diante)**: a LLM devolve só `{abertura, fecho}` no tom do humor; o miolo é
  sempre a frase de `expressao.py`, então não há como inventar causa. `validar_moldura` barra
  conectivo de causa, número, marcador e tema de causa; o Ollama recebe limite de caracteres no
  esquema e penalidade de repetição. Cada versão avaliada numa semente nova: v4 (s20260926) 127/200,
  67 cortadas por loop de carinhas; v5 (s20260927) 199/200 mas quase sem abertura; **v6 (s20260928,
  abertura obrigatória no esquema) 191/200, todas com abertura, nenhuma igual à frase pronta**
  (ex.: "Epa... Dormi porque eu estava com sono e por causa do cansaço. :/"). "Eba!" abre 58/191.
- O modelo às vezes devolve surrogate UTF-16 solto: o servidor saneia antes de validar (quebrava a
  resposta e a avaliação).
- Revisão humana de `artifacts_fala/ollama_qwen2.5-3b_fala-v6_s20260928/revisao.csv` (50 falas aprovadas): **feita pelo Matheus
  (2026-10-01)**. Ligar a fala por LLM por padrão continua sendo decisão dele (hoje desligada).

## Fala livre por LLM local (2026-09-28, `docs/TAREFA_FALA_LIVRE.md`, `docs/PLANO_VERSAO_FALA_LIVRE.md`)

**Aprovada só com o `gemma2:9b`** (decisão do Matheus), com `modo_fala` desligado por padrão. Desvios e
números em `docs/REGISTRO_DESVIOS.md` e `artifacts_fala_livre/rodada2/RELATORIO.md`.

- `digilab_fala_livre/` (FORA de `digilab/`; nada do pet importa daqui, teste AST): `fatos.py` (bloco de
  FATOS com identificadores; entrada da web tratada como não confiável), `prompt.py` (`livre-v2`), `ollama.py`
  (só Ollama local), `saida.py` (parser que falha alto → fala genérica), `verificador.py` (`verif-v3`:
  afirmações sem fato e manipulação; não troca a fala), `apresentacao.py` (log de apresentação separado),
  `situacoes.py` e `avaliacao.py` (`python experiments/avaliar_fala.py --livre --rodada 2`).
- Servidor: `servidor/fala_livre.py`, instalado por um gancho no `servidor_local.py` (`/api/fala-livre`,
  `/api/fala-livre/verificar`, `/api/fala-livre/status`); modelo `DIGILAB_MODELO_LIVRE` (padrão `gemma2:9b`).
- Web: `web/modulos/fala_livre.js`, três ganchos `// GANCHO fala-livre` na página; seletor de modo
  (template/moldura/livre) e conversa na tela do pet; falas no localStorage `<chave>.fala.jsonl`, nunca no
  registro do pet; o que o jogador escreve não ensina o pet.
- Rodada 2: gemma2:9b 3,0% de falas com afirmação sem fato (teto; o juiz marca 10% da moldura, que só diz
  verdades), 0/30 conversas inventaram, latência p90 4,8 s na RTX 2060 (sem outro modelo carregado).
- Pendente: avaliação cega do Matheus (`artifacts_fala_livre/rodada2/avaliacao_cega.csv`).
- Voz própria no jogo (parte 4, 2026-09-30): pets **v7** (`VERSAO_PET = 7`: v6 + voz própria) com janela de fala, mentira (`CMEN`) e evento `fl` (o `f` é da Fronteira); `motor/historia.ts` e `motor/mentira.ts` conferidos contra o Python (`experiments/exportar_gabaritos_voz.py` → `test/gabaritos/voz_python.json`, `tests/test_gabaritos_voz.py`); gatilhos e ritmo em `src/voz.ts`; servidor com `voz: true` (livre-v6, autocorreção, verif-v5, corpus, almanaque, árvore da espécie). Revanche: ao escolher o rival que venceu o pet (`falaRevanche`, `src/nomesRivais.ts`). Avaliação: `artifacts_voz/rodada1..4` (`experiments/avaliar_voz.py --rodada N`).
- Voz própria (DESIGN_VOZ_PROPRIA, parte 2): `livre-v3` e `verif-v4` ao lado das versões do jogo; fatos H/O/P/L, mentira F (`mentira.py`), almanaque W (`almanaque.json`), corpus de espécies (`corpus.py`, `corpus_especies.json` = EXEMPLO com 2 espécies) e filtro contra repetir citação.
- **Fala no limite do esquema (2026-09-30):** o Ollama para a geração na gramática quando a fala bate em `MAX_CHARS` do estágio
  (bebê 30) e a palavra sai cortada ("Vou co-c", que o verificador ainda marcava como invenção). `saida.aparar` deixa só a
  parte inteira: até o último fim de frase, senão até o último espaço com reticências; abaixo do limite nada muda. Vale em
  `gerar` e na reescrita da autocorreção (`revisao.py`). Teste `tests/test_aparar_fala.py`.
- **Filtro do alfabeto no estilo (2026-09-30):** o corpus de 60 espécies descreve o registro japonês (pronomes como おいら, finais
  como 〜だぜ) em 46 itens de "jeito de falar"; com eles no pedido o gemma2:9b respondia em japonês e `saida.ler` rejeitava a fala
  inteira ("…"). `corpus.carregar` (padrão `so_latino=True`) deixa fora do bloco de estilo todo traço, fala, interação e citação
  com letra fora do alfabeto latino (`descartados["NAO LATINO"]`); o arquivo e o sha256 não mudam, o corpus de exemplo das rodadas
  1–4 não tem item assim. Medida em `artifacts_voz/estilo_latino/` (`python experiments/medir_estilo_latino.py`: 30 mensagens ×
  3 espécies, com e sem o filtro). Teste `tests/test_corpus_latino.py`.
- **Comando pelo chat (2026-09-30, `docs/TAREFA_COMANDO_CHAT.md`, decisão do Matheus):** a regra "o que o jogador escreve não ensina o
  pet" **deixa de valer para o comando, mediado por um catálogo fechado**; fora do catálogo o texto continua sem efeito. Na CONVERSA
  dos pets v7+ (`voz: true`) o servidor usa o prompt `livre-v7` (= v6 + bloco COMANDO) e devolve `comando`: uma das 9 ações de
  `AcaoDono` (`web/app/motor/tipos.ts`) ou `null`; `saida.ler` falha alto fora do catálogo (fala genérica, comando null). A LLM só
  propõe: o app valida de novo (`src/acoes.ts`: catálogo, pet nascido e vivo, ações v4 só em pets v4+, tratar só com lesão), mostra um
  grava o evento `d` de sempre **na hora** pelo mesmo caminho do botão (`acoes.agir`,
  usado pela tela do Pet, pelos atalhos e pelo chip). No registro do pet não entra nada da LLM: replay, assinaturas v1–v8, gabaritos e
  paridade iguais; sem o modo livre gravado. O chip some com outra mensagem, outra fala do pet ou 60 s. Log de apresentação versão 2
  (`comando`, `comando_executado`; lê a 1). Treino, luta, itens, fala espontânea e pets sem voz (v1–v6, `livre-v2`) ficam fora.
  Avaliação: `python experiments/avaliar_fala.py --livre --comando [--rodada 1|2]` → `artifacts_fala_livre/comando/rodada1/` (sem o
  estilo da espécie) e `rodada2_estilo/` (com); 60 mensagens em `situacoes.MENSAGENS_COMANDO` × 3 sementes; gate PROPOSTO: falsos
  positivos ≤ 5% nas negativas e imperativos ≥ 80%. **Execução direta liberada pelo Matheus em 2026-10-01**, depois do gate da rodada 3; o chip de confirmação da primeira
  versão saiu (`web/app/src/falaLivre.ts`, `executarComando`). O erro conhecido da rodada 3 fica no jogo: "banho agora, sem choro" pode
  virar repreender.
  - Rodada 1 (`livre-v7`, sem estilo): falsos positivos 0%, imperativos 53,3% (FALHA): elogiar, repreender, acariciar e
    tratar_lesao acertaram 4 de 36 (a mensagem do dono É a ação e o modelo tratava como conversa).
  - **Rodada 3 (`livre-v8`, 2026-09-30, `artifacts_fala_livre/comando/rodada3/`)**: o servidor usa a **v8** na conversa com voz
    (= v7 com o bloco COMANDO reescrito: as quatro ações definidas pelo que o dono faz na própria mensagem; negação, pergunta,
    hipótese, adiamento e relato = null). A v7 continua no pacote e a rodada 1 reproduz. Sementes novas (20261201/1301/1401; as
    das rodadas 1–2 são de calibração), sem o estilo, gemma2:9b. **Gate PASSA**: falsos positivos 0/60 nas negativas e 0/60 na
    conversa; imperativos 51/60 (85,0%). As quatro ações: 23 de 24 (tratar_lesao 5/6, uma virou acariciar). **Regressão:**
    limpar caiu de 7/9 para 3/9 (5 viraram `repreender`: "banho agora, sem choro", "vai se limpar, você tá todo sujo"). O chip
    continua obrigatório; a execução direta segue como decisão do Matheus.
- **Corpus reescrito em português (F0-CORPUS, 2026-10-01, `docs/TAREFA_V2_F0_CORPUS.md`):** os itens que o filtro do alfabeto
  deixava fora voltaram ao bloco de estilo, reescritos em português sem a palavra japonesa (por exemplo, "pronome rústico e
  descontraído" no lugar do pronome original), cada um com `marca`, `fonte` e `jogo` iguais e `"reescrito": true`; o texto só diz o
  que a fonte do item (`docs/corpus_digimon/`, fora do repo) diz. Pelo `corpus.latino` eram **49** itens em 28 espécies (46 falas,
  2 traços, 1 interação), não 46: três falas de Guilmon e Growlmon só tinham o ordinal "3ª", que conta como letra não latina, e
  viraram "terceira pessoa". **Nenhum item saiu.** Com o filtro entram 504 itens, os mesmos que sem ele (antes 455 × 504;
  `descartados["NAO LATINO"]` 0, antes 49). Vocabulário fixo para os pronomes: "infantil e modesto", "masculino informal", "rústico
  e descontraído", "formal", "de velho", "feminino informal". O filtro, o prompt, o verificador e o almanaque não mudam; o sha256
  do corpus mudou (`b1b7ad8d…` → `785f7834…`; `artifacts_voz/estilo_latino/` mede o corpus anterior e não foi refeito). Sem run
  com o gemma2:9b: a conferência da fala com o estilo é frente própria na fila da GPU. Critério e itens limítrofes em
  `docs/REGISTRO_DESVIOS.md`; teste `tests/test_corpus_latino.py::test_corpus_do_jogo_reescrito_em_portugues_nao_perde_item`.
