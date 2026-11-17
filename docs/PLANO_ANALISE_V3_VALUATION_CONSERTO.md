# PLANO DE ANÁLISE V3 — VALUATION, a V3: o conserto do reflexo do sono

**Status: PROPOSTO.** Nenhuma linha de código do conserto e nenhuma vida existem antes da aprovação.

Escrito em 2026-11-17 (Claude Code, Opus 5.5, branch `v3-valuation-v3`), na Fase V3 do pedido
([TAREFA_V3_VALUATION.md](TAREFA_V3_VALUATION.md)). O Matheus abriu a V3 nesta sessão ("Sim, abra a V3"), com a R como candidata. O plano
para no **CHECKPOINT V3a**, antes do código.

## 1. De onde vem

A V2 ([RESULTADO_V3_VALUATION.md](RESULTADO_V3_VALUATION.md)) confirmou uma hipótese só, a R. Desligar o reflexo do sono (`lambda_sono = 0`)
fecha mais episódios de fome: +0,129 [+0,117; +0,141], 1,55 vez o gap da A1. A ablação, porém, piora o bem-estar:
- a privação sobe +0,084;
- a exaustão sobe +0,276, de 0,22 para 0,50.

O mecanismo, pelos descritivos:
- **O reflexo** (`Arbitragem.reflexo`, `digilab/digibrain/arb.py:109`) força o `dormir`, sem sorteio, sempre que a leitura da energia fica abaixo de `lambda_sono` (S/4). Ele faz isso **com fome ou sem**.
- **No REL,** isso troca 13 intenções de comer por vida, e 42 % das decisões do episódio de fome são `dormir`.

O conserto da V3 tem de fechar mais episódios **sem** a piora (a seção 5.2 do plano da V2, vinculante aqui).

## 2. O conserto (D-VAL-16)

### 2.1 A recomendação: a guarda da fome urgente no reflexo

Com a chave ligada, o reflexo do sono **não dispara quando a fome está urgente**: a urgência da fome do M-AFETO precisa passar de
`urgencia_lambda`. A decisão segue então pelo sorteio de hoje, em que o `dormir` continua concorrendo. Sem a fome urgente, o reflexo é o
de hoje.

**Por que esta, e não as outras:**
- **Não tem número novo:** o limiar é o `urgencia_lambda` dos inatos (S/2), a mesma "fome urgente" de quatro regras que já existem: o sono que segura (`ConfigSonoSegura`), a guarda do passeio (AN-4), a guarda do brincar (EQ-7) e o convite da bola (BB-4).
- **Não é mecanismo novo:** é a regra que o sono que segura já aplica ao pet dormindo, estendida ao reflexo de baixo de `lambda_sono`. O pedido proíbe mecanismo novo.
- **Mexe pouco no sono:** o reflexo só sai da frente na janela da fome urgente. Depois de comer, com a energia ainda baixa, ele volta. A R desligava o reflexo em todas as decisões, o que explica a exaustão de 0,50.

**O risco:** a exaustão pode subir mesmo assim, porque o pet sai para comer com a energia abaixo de S/4, e no `longe_fixo` a comida fica
longe. A guarda da seção 5 mede isso, e uma piora para a fase.

### 2.2 As alternativas, não recomendadas

| alternativa | o que muda | por que não |
|---|---|---|
| (b) `lambda_sono` mais baixo (por exemplo S/8) | o reflexo dispara mais tarde, com fome ou sem | número novo, SEM FONTE, que pede uma calibração com faixa própria antes da validação (duas runs); não separa a fome |
| (c) liberar a `intencao_suspensa` com a `memoria_autobio` | a intenção de comer volta depois do sono | tira uma recusa da config de outra frente (D-VAL-7); o pet ainda dorme durante a janela, então a janela vence do mesmo jeito |
| (d) ajustar o viés do comer | o comer pesa mais | a V2 refutou a E: comer mais não fecha a janela |

### 2.3 A implementação (depois do CHECKPOINT V3a)

- **A config:** `ConfigConsertoValuation(guarda_fome_reflexo: bool = False)` em `digilab/config.py`, PROPOSTA, com a `PARAMETROS_CONSERTO_VALUATION`.
  - Fica fora do `ConfigDigibrain` e dos inatos, para o dump de paridade do modular não mudar, como a `ConfigSonoSegura`.
  - Não tem número próprio, só a chave.
- **O `Arbitragem.reflexo`:** com a chave ligada e `energia < lambda_sono`, devolve `False` se `urgencias["fome"] > urgencia_lambda`. Sem as urgências, falha alto. Com o sono que segura também ligado, a parte dele não muda.
- **O M-ADAPT:** passa as urgências ao reflexo também com o conserto ligado, como já faz com o sono que segura.
- **Desligada (o padrão), a vida de hoje sai byte a byte.** O gabarito é gravado num commit próprio, antes do código.
- **O web:** o conserto fica só no Python nesta fase (D-VAL-17). Levar a chave ao jogo é decisão do Matheus, depois da V4.

## 3. Os testes do código (antes de qualquer vida)

- **"desliga não muda":** o gabarito `tests/gabaritos/valuation_conserto_de_hoje.json` (REL e M3, os 4 donos, o `longe_fixo` e o comedouro, a semente 101, 3 dias), gravado antes do código. Com a chave desligada, as vidas saem byte a byte.
- **A unidade:** com a energia abaixo de `lambda_sono`, o reflexo dispara com a fome não urgente e não dispara com a fome urgente (chave ligada). Com a chave desligada, dispara nos dois casos. Acima de `lambda_sono`, nada muda.
- **A conferência da run:** em toda decisão do braço CON com o reflexo, a fome não está urgente. Em toda decisão com a energia abaixo de `lambda_sono` e sem o reflexo, a fome está urgente. Uma divergência é falha alta.
- **O REL daqui é a vida do REL da C4,** byte a byte, como na V2.

## 4. A run

| item | valor |
|---|---|
| braços | REL (o da C4 e da V2) e CON (o REL com `guarda_fome_reflexo` ligada); uma mudança só |
| células | as 12 da C4 e da A1: os 4 donos × comedouro, longe e `longe_fixo` (D-VAL-19) |
| unidades | 200, a derivação `digibrain_prototipo`, K = 40 |
| faixa | **73101…73505**, PROPOSTA (D-VAL-18), bases 73101, 73202, 73303, 73404 e 73505 |
| dias | 14, orçamento 16 |
| vidas | 2 × 12 × 200 = 4 800 |
| custo | a V2 levou 1 h 35 para 5 600 vidas com 4 processos; cerca de 1 h 20 |

- A run roda **uma vez**, com no máximo 4 processos e sem outra run de pesquisa do DigiLab ao mesmo tempo.
- O orquestrador é o da V2 (`experiments/run_v3_valuation.py`), com o modo `conserto` e uma config própria.

## 5. As medidas e a regra de leitura, escritas antes

A unidade é (base, semente), e o contraste é CON − REL, pareado por unidade, pelo t (o `orq.contraste_t` da C4). As classes são as da A6.6
(`run_v2_longe_regular.classe`), com δ = 0,032, SEM FONTE, a da V2.

| critério | medida | passa se |
|---|---|---|
| **P, "liga melhora"** | a taxa de fechamento por episódio de fome, média das 4 células do `longe_fixo` | classe **"> 0"** e p unilateral < 0,025 |
| **G1, a privação** | a privação, média do `longe_fixo` e média das 12 células | nenhuma das duas em "> 0" |
| **G2, a exaustão** | a exaustão, média do `longe_fixo` e média das 12 células | nenhuma das duas em "> 0" |
| **G3, os outros lugares** | a taxa por episódio, média das 4 células do comedouro e das 4 do longe | nenhuma das duas em "< 0" |
| **D, "desliga não muda"** | o gabarito da seção 3 | o teste passa antes da run |

- **A leitura:**
  - **passa:** P, G1, G2, G3 e D passam;
  - **efeito trivial:** a P sai "≈ 0" com o sinal +, e o conserto não explica a perda. Conta como falha;
  - **falha:** qualquer critério que não passa. A fase para com o relato (a regra do pedido), e o resultado fica registrado como está.
- **Por que sem Holm:** há um primário só. Os critérios G são guardas, todas vinculantes, e qualquer uma que falha reprova. Corrigir para a família só deixaria a guarda mais frouxa.
- **Ao lado, sem classe, os descritivos da 5.3 da V2:**
  - as refeições por dia, a `janela_vencida`, a fração de `dormir` e de `comer` no episódio, os reflexos por vida e a latência;
  - a fração do gap da A1 que o conserto cobre;
  - **no REL, a fração das decisões de reflexo com a fome urgente.** É a conta que a V2 não fez e que mede quanto a guarda pode mudar.
- **O bootstrap e o g1** vão rotulados, como na V2.

**O que a run não demonstra:**
- nada contra a TRIV, que fica para a V4, com faixa própria;
- nada sobre o jogo web;
- nada sobre outro limiar além do `urgencia_lambda` de hoje;
- nada com o sono que segura ligado (o REL da C4 o tem desligado);
- nada fora dos 14 dias e do mundo do MVP.

## 6. Os artefatos

Em `artifacts_v3_valuation/conserto/`, como na V2:
- `resultado.json`, `medidas.json` e `vidas.tar.gz`, determinístico;
- `meta.json`, com o comando, o commit, a árvore limpa, o `plano_sha256`, a faixa, os braços e o sha256 de cada artefato.

## 7. As decisões abertas para o CHECKPOINT V3a

- **D-VAL-16, o conserto.**
  - **A recomendação:** (a), a guarda da fome urgente no reflexo, com o `urgencia_lambda` de hoje.
  - **O custo de errar:** se a guarda abrir pouco o reflexo, porque a fome urgente coincide pouco com a energia baixa, a P sai "≈ 0" e a frente para sem conserto. A conta descritiva da seção 5 diz por quê. Se abrir demais, a G2 reprova.
- **D-VAL-17, só no Python.**
  - **A recomendação:** sim. O conserto entra no jogo só depois da V4 e com a sua decisão.
  - **O custo de errar:** o jogo segue com o reflexo de hoje até lá.
- **D-VAL-18, a faixa 73101…73505.**
  - **A recomendação:** aprovar. Ela foi conferida livre em 2026-11-17 no `faixas.py`, nas configs, nos planos e nas tarefas dos 954 branches remotos.
  - **Por que não a 98xxx:** a `main` a reservou para a A2.
- **D-VAL-19, as 12 células em vez das 4 do `longe_fixo`.**
  - **A recomendação:** as 12. O conserto não pode piorar o comedouro e o longe (a G3), e a V4 vai medir as 12.
  - **O custo:** mais 3 200 vidas, cerca de 55 min.
- **D-VAL-20, a guarda pela classe com δ.**
  - **A recomendação:** a mesma regra da V2. Uma piora menor que δ sai "≈ 0" e não reprova.
  - **A alternativa:** reprovar qualquer IC acima de 0. É mais rígida, e um efeito de 0,005 na exaustão pararia a frente.
