# PLANO DE ANÁLISE V3 — PET_VIVO, R1: o rastro da cadeia e o que fica fora do r (2026-11-19, Claude Code, Fable 5.2)

**Status: APROVADO pelo Matheus em 2026-11-19.** À pergunta "Aprova o plano do R1 e as RA-1 a RA-6 pela recomendação?", nesta sessão,
a resposta foi "Aprovo todas" (D-RA-7). As decisões RA-1 a RA-6 da seção 10 estão DECIDIDAS pela recomendação. Os cortes seguem SEM
FONTE. **Nenhum replay e nenhuma conta deste plano rodam antes de três coisas:**
1. a marca "APROVADO pelo Matheus" neste cabeçalho (feita acima);
2. o código da seção 7 na `main`, com os testes dele;
3. as conferências da seção 3.3, que falham alto antes de qualquer medida.

**Este plano não calcula nenhum número de resultado.** Os números que ele cita já estão em artefatos do git, ou são fatos do código, com
o arquivo. Os cortes da seção 5 são PROPOSTOS e SEM FONTE.

**De onde vem:**
- a análise da integração da cadeia ([futuro/integracao_cadeia_digibrain.md](futuro/integracao_cadeia_digibrain.md)): o diagnóstico
  da seção 1.3, o rastro da seção 3.6 e a linha do R1 nas seções 6 e 7;
- a INT-1 (a ordem R0, R1, R2…) e a INT-6 (medir a troca de intenção no R1), DECIDIDAS em 2026-11-17 (D-INT-9);
- o R0 feito e registrado "não levar" ([RESULTADO_V3_PET_VIVO_PV2.md](RESULTADO_V3_PET_VIVO_PV2.md), D-PV2R-13);
- **o pedido do Matheus (2026-11-19): "escreve o plano do R1".** Ele pede o papel. Não aprova este plano e não libera replay nem
  código.

**O que o R1 é:** uma etapa de leitura. O cérebro passa a registrar, por decisão, o que aconteceu com o corpo entre uma decisão e a
seguinte, sem creditar nada. Depois, um replay das vidas já gravadas mede quanto do corpo fica fora do r de hoje. Os números servem ao
plano do R2 (o crédito do intervalo).

**O que este plano não afirma:**
- que creditar o intervalo melhora a vida do pet: isso é do R2, com run própria;
- que o rastro é legível para pessoas: isso é da frente LEGIBILIDADE;
- nada sobre o jogo web: as vidas são do REL na bancada do Python.

**Nenhuma alegação de novidade.**

## 0. O que existe hoje (os fatos do código que o desenho usa)

Conferidos na `origin/main` em `62f5f6c0`.

- **O r de hoje** (`digilab/digibrain/adapt.py`, `_fechar`, linhas 796 a 911): compara o corpo da decisão (`pc0 = p["sens"]["pc"]`)
  com o corpo logo depois dos estímulos da ação, no mesmo tick (`pc1 = p["corpo"][1].corpo`). A conta é a `Afeto.consequencia`
  (`afeto.py:136-151`), sobre o `sinal_corpo` (`base.py:100`) e o `canais_do_sinal` (`afeto.py:35`), que dá o r por canal.
- **O intervalo:** entre o `pc1` da decisão k e o `pc0` da decisão k+1 passam os 15 ticks do passo. Nada lê essa diferença, salvo a
  `fala_unidades` no chamar (`adapt.py:812-815`), desligada no REL.
- **O registro de cada decisão** (o `motivo`): `motivo["consequencia"]` traz `r`, `r_n`, `canais`, `comeu`, `chegou`, `p1`, `creditos`
  e `episodio`; `motivo["fins"]` traz os fins das intenções ("meta", "sumiu", "desistiu", "trocou", "achou"; `estado.py:10-26`).
- **Uma conta de r sem efeito já existe:** a `Afeto.sigma_luta` (`afeto.py:153-158`) calcula o r e o r_n sem mexer em V nem em E.
- **O elogio está na `main`, atrás da `ConfigElogio`** (`adapt.py:54-58`, `:308-316`, `:464-465`): com ela ligada, o cérebro guarda as
  últimas `janela` decisões em `_recentes`. Desligada, nada muda. A validação dele está em
  [RESULTADO_V3_ELOGIO.md](RESULTADO_V3_ELOGIO.md).
- **O leitor da 0b** (`experiments/auditoria_pet_vivo.py:101`, a classe `Leitor`): lê o cérebro durante a vida sem mudá-la, e o G1 do
  replay confere isso. A run do PV-2 já o reusou (`experiments/run_v3_pet_vivo_pv2.py`).
- **As vidas da run do PV-2** (`artifacts_v3_pet_vivo/pv2/run/meta.json`): 15 360 vidas, código `34894b50`, `git_limpo` verdadeiro,
  faixa 26101–26505. Os logs estão no `vidas.tar.gz`, que fica só na máquina, com o sha256 no `meta.json` (`3dcb15b7…474df`). O
  `medidas.json.gz` está no git (`0bea4881…193c`).

## 1. As perguntas e as hipóteses, escritas antes

- **Q-FORA:** quanto do que muda no corpo do pet acontece no intervalo entre as decisões, fora do r do mesmo tick? Por receptor.
- **Q-ACAO:** o que acontece no intervalo depende do que o pet fez? Ou é um decaimento igual para qualquer ação?
- **Q-DONO:** quanto do intervalo coincide com um gesto do dono? (O carinho e a ração posta caem dentro dele: a INT-5.)
- **Q-TROCA:** com que frequência a intenção troca, e por qual fim? (A INT-6: o C é um degrau.)
- **Q-TEXTO:** o rastro mostra a cadeia de uma decisão em texto, e um teste consegue lê-lo?

As hipóteses são da leitura do código (a análise, seção 1.3). São HIPÓTESES, SEM FONTE:

| | a hipótese | em uma frase |
|---|---|---|
| **H-FORA** | **a maior parte fica fora** | a energia, o tédio, a solidão e a higiene mudam quase só no intervalo; a fome cai no mesmo tick (a digestão é instantânea) e sobe no intervalo |
| **H-SONO** | **o sono só aparece no intervalo** | o r do mesmo tick do dormir é 0, e o canal da energia do intervalo depois de dormir é positivo |
| **H-CTX** | **a linha de base por contexto apaga o sono** | tirando do intervalo a média do contexto (acordado ou dormindo), o resto do dormir fica perto de 0: a linha de base desenhada para o R2 absorveria justo o que ele quer ensinar |

A H-CTX é o risco de desenho que mais interessa ao R2. Se ela se confirmar, o plano do R2 precisa de outra linha de base.

## 2. O mecanismo do rastro (o que o PR do código implementa, atrás de chave)

- **A subchave:** `ConfigDigibrain.rastro`, desligada por padrão. Desligada, o `motivo` e a vida saem byte a byte como hoje.
- **A conta do intervalo:** uma função pura no `afeto.py` (nome PROPOSTO: `r_intervalo`), no molde da `sigma_luta`. No `_fechar` da
  decisão k+1, com o `pc1` da decisão k guardado:
  - `canais_int = canais_do_sinal(pc1_k, pc0_{k+1}, drives, ganho_r, S)`, com os mesmos drives e o mesmo ganho do r;
  - `r_int` é a soma dos canais; `r_int_n = clamp(div_arred(r_int, r_norm), −S, S)`.
- **O que a conta não toca:** V, E, F, C, o P1, o P2, a memória e a rng. Nenhuma atualização nova. É só registro.
- **O caso da fala:** com a `fala_unidades` ligada, a opção de fala já lê o corpo da decisão seguinte. Nessas decisões o rastro
  registra o intervalo como "já contado", com os canais em 0, para nenhum trecho do tempo entrar duas vezes.
- **O registro:** `motivo["cadeia"]`, só com a subchave ligada:

| campo | o que traz | de onde vem |
|---|---|---|
| `id` | o `cadeia_id`, o índice k da decisão | `p["k"]` |
| `tick` | o tick da decisão | `p["tick"]` |
| `mesmo_tick` | o `r`, o `r_n` e os canais de hoje | a `consequencia` |
| `intervalo` | o `r_int`, o `r_int_n`, os canais, o par (`tick_de`, `tick_ate`) e a variação da leitura de cada receptor | a conta acima |
| `gestos` | os gestos do dono dentro do intervalo, com o tick | `p["gestos"]` e o `receber_acao_dono` |
| `atualizacoes` | o P1 (classe, receptor, antes, depois), o P2 (a linha e o Δ) e os episódios codificados, com os ids | `p1`, `creditos`, `episodio` e `autobio` |
| `pesou` | os termos não nulos da unidade escolhida (hábito, incentivo, memória, lembrança) e as sondas que mudariam a escolha | os `termos` e as sondas do `motivo` |

- **O texto:** uma função pura (lugar PROPOSTO: `digilab/digibrain/rastro.py`) monta uma linha por decisão a partir do
  `motivo["cadeia"]`. Por exemplo: "decisão 412: dormir (reflexo); no mesmo tick, nada; nos 15 min seguintes, energia +38; nenhum
  aprendizado". O teste lê esse texto.
- **Os ids dos episódios que pesaram:** se o M-MEM não os devolver sem uma mudança além de leitura, o PR do código registra a lacuna
  como desvio e o campo `pesou` fica só com os termos.
- **O TypeScript não entra nesta etapa** (RA-3): o espelho com paridade vem depois da LZ3, num PR próprio.

## 3. A fonte dos dados

### 3.1 As vidas (RA-2)

| fonte | o que é | as vidas | papel |
|---|---|---|---|
| **o HOJE da run do PV-2** | o REL da C4 com o oráculo do cheiro, nas 12 células (4 donos × `comedouro`, `longe` e `longe_fixo`), 200 unidades, 14 dias | 2 400 | a leitura principal |
| **o OLF-0 da mesma run** | o mesmo cérebro com o órgão no lugar do oráculo | 2 400 | ao lado, sem regra de leitura |
| **o HOJE da checagem do v38** | as chaves do pet do jogo que o Python tem, nos k de 0 a 7, no `longe` e no `longe_fixo` | 320 | a INT-8, descritiva |

- **Por que não as vidas da 0b** (as da C4, que a análise citava): elas são do código `a287ba2`, de antes do jogo v17. O HOJE da run
  do PV-2 é o mesmo braço REL, nas mesmas células e com o mesmo desenho, no código de 2026-11-18.
- **Por que o OLF-0 ao lado:** o R1 dependia do R0 "para incluir o cheiro". O PV-2 ficou como "não levar", então o cheiro pelo órgão
  não é o cérebro do jogo. O OLF-0 sai só como descritivo, para o caso de o oráculo ser trocado um dia.
- **Os outros braços** (OLF-DC, OLF-DCV, OLF-PLA, OLF-G) ficam fora: não vão ao cérebro padrão.
- **Nenhuma vida nova, nenhuma semente nova, nenhuma faixa nova.**

### 3.2 Onde estão

- **Os logs:** `D:\Trab\digilab\v3-pet-vivo-pv2-run\artifacts_v3_pet_vivo\pv2\run\vidas.tar.gz`, fora do git. O script só lê.
- **As medidas da run:** `artifacts_v3_pet_vivo/pv2/run/medidas.json.gz`, no git.
- **Se o `vidas.tar.gz` sumir:** as vidas dos três conjuntos acima são refeitas numa worktree destacada em `34894b50`, com as mesmas
  sementes, e só valem se as medidas saírem iguais às do `medidas.json.gz`. Isso não é vida nova: é a mesma vida, conferida.

### 3.3 As conferências que falham alto, antes de qualquer medida

- **C-FONTE:** o sha256 do `vidas.tar.gz` e do `medidas.json.gz` iguais aos do `meta.json`.
- **C-G1:** cada vida, rejogada pelo log **com o rastro ligado** no código do dia, sai com o log igual ao do disco e com as medidas
  iguais às do `medidas.json.gz` (menos o custo). Esta conferência prova duas coisas de uma vez: que o rastro não muda a vida, e que
  a `main` do dia ainda refaz as vidas do `34894b50`.
  - **Se ela falhar porque a `main` mudou o REL,** o replay para. Nada se ajusta por conta própria. Um adendo propõe rodar o rastro
    sobre uma worktree destacada em `34894b50`, com o patch do rastro aplicado.
  - O PR do código faz uma fumaça desta conferência em 2 vidas da run, sem ler nenhuma medida do rastro.
- **C-FECHO:** para cada receptor e cada decisão, a leitura do `pc0` da decisão k+1 menos a do `pc0` da decisão k é igual, exata, à
  variação do mesmo tick mais a variação do intervalo.
- **C-UMA-VEZ:** os pares (`tick_de`, `tick_ate`) não se repetem, e o `tick_ate` de uma decisão é o tick da decisão seguinte.
- **C-IGUAL:** duas execuções do script saem iguais, byte a byte.

## 4. As medidas (todas no `digilab/metrics.py`, uma vez só)

A unidade da análise é a vida. As contas por decisão viram somas ou médias por vida. Os IC95 são por (braço, lugar), sobre as 200
unidades (base, semente), com a média dos 4 donos, pelo t, como na C4 e na run do PV-2. Os donos saem também separados, sem IC. As
somas são inteiras, e as razões são exatas (`fractions`). A última decisão da vida não tem intervalo e fica fora.

- **M-FORA, a fração fora do r** (Q-FORA):
  - **por receptor** (os 11): `F_r = Σ|Δint_r| / (Σ|Δtick_r| + Σ|Δint_r|)`, sobre a leitura do receptor na escala S;
  - **no sinal** (os canais do r): `F_sinal = Σ|canal_int| / (Σ|canal_tick| + Σ|canal_int|)`, somando os canais dos drives;
  - ao lado, as somas com sinal por dia: `Σ r` e `Σ r_int`.
- **M-ACAO, o intervalo por ação** (Q-ACAO, H-SONO e H-CTX):
  - o contexto de cada decisão: "dormindo" se a ação foi dormir (com o reflexo), "acordado" nas outras;
  - a média do `r_int_n` por comportamento (os 7), por vida;
  - **o resto global:** `r_int_n` menos a média da vida;
  - **o resto por contexto:** `r_int_n` menos a média do contexto na vida;
  - **η²_g** e **η²_c:** a fração da variância do resto (global e por contexto) que fica entre os comportamentos. No η²_c, o
    contexto "dormindo" tem um comportamento só, então ele mede a diferença entre os comportamentos acordados;
  - a média do resto do dormir, pelas duas linhas de base;
  - a fração das decisões de dormir com o r do mesmo tick diferente de 0 (o esperado pela leitura do código é 0).
  - **A média da vida fica no lugar da média móvel do R2.** O `k_b` da média móvel é número do plano do R2, e não deste.
- **M-DONO** (Q-DONO): a fração dos intervalos com pelo menos um gesto do dono, e a média do `r_int_n` com e sem gesto, por tipo de
  gesto e por dono. Sem IC.
- **M-TROCA** (Q-TROCA): por vida, o número de intenções por dia, a duração em decisões (1, 2, 3, 4 ou mais), a fração das decisões
  que trocam de intenção, por fim, e a fração das trocas que vêm do reflexo do sono.
- **M-MUDA** (a pergunta do D-PV0R-6): por receptor, a fração das decisões com a variação do mesmo tick diferente de 0, e a mesma
  fração para o intervalo. Sem os cortes da 0b: é só a contagem.
- **M-CUSTO:** o tempo por vida com o rastro ligado e desligado, nas sementes dos testes, medido no PR do código.

## 5. A regra de leitura, escrita antes

Nenhuma medida deste plano é gate: nada muda no cérebro, e nada vai para a web por ela. A regra diz **o que o plano do R2 recebe**. Ela
se lê no HOJE, nos 3 lugares, pelo limite do IC95. Os cortes são os da RA-5, SEM FONTE.

**L-FORA, se há o que creditar** (pela `F_sinal`):

| o que sai | a leitura |
|---|---|
| o limite de baixo ≥ 1/2 nos 3 lugares | "a maior parte do sinal está fora do r" |
| o limite de cima < 1/4 nos 3 lugares | "o intervalo é pequeno": o R2 perde a razão principal, e o plano dele precisa de outra |
| qualquer outro caso | "parte do sinal está fora", com o número de cada lugar |

**L-ACAO, se o intervalo distingue a ação** (pelo η², com o corte em 0,05):

| o que sai | a leitura | o que o plano do R2 recebe |
|---|---|---|
| o limite de baixo do η²_c > 0,05 em pelo menos 2 lugares | "o intervalo distingue a ação mesmo acordado" | o desenho da análise (seção 3.3) segue |
| só o do η²_g > 0,05, e o limite de cima do η²_c < 0,05 | "o sinal do intervalo é o sono, e a linha de base por contexto o apaga" (a H-CTX) | o R2 propõe outra linha de base, ou outro contexto, antes do código |
| nenhum dos dois | "o intervalo é decaimento igual para toda ação" | nas vidas de hoje o R2 não tem o que creditar: ele precisa primeiro de um efeito atrasado (a T4 da análise) |
| qualquer outro caso | "indeterminado", com os números | o plano do R2 mede de novo nas sementes dele |

**Sem regra:** a M-DONO vai ao plano do R2 (a INT-5), a M-TROCA ao do R3 (a INT-6) e a M-MUDA fica como resposta descritiva ao
D-PV0R-6. O OLF-0 e a checagem do v38 saem ao lado, sem leitura.

**O que a regra não decide:** se creditar o intervalo melhora a vida, se piora o forrageio, nem que números o traço usa.

## 6. O tamanho e o custo

- **5 120 replays** (2 400 + 2 400 + 320), sem contrafactual.
- **O custo é estimado e SEM MEDIDA.** O replay da 0b fez as 4 800 vidas da C4 em 1 a 2 h de parede com 4 processos (a estimativa
  do plano dela). O PR do código mede o tempo em 2 vidas das sementes dos testes e declara a projeção no relato.
- **A regra do custo** (RA-6): se a projeção passar de 4 h com 4 processos (corte PROPOSTO), um adendo propõe um conjunto menor
  **antes** do replay, nunca depois.
- **A máquina (V3-D8):** no máximo 4 processos. O replay conta como a run de pesquisa do momento e passa pelo `tools/pre_run.py`.

## 7. O que falta antes do replay (o PR do código, depois do APROVADO)

- **O byte a byte:** com a subchave desligada, os gabaritos de hoje do modular (`web/app/test/gabaritos/digibrain_modular_*.json.gz`)
  saem iguais. Se nenhum gabarito cobrir o `motivo` inteiro do REL, o gabarito entra num commit próprio, antes da mudança.
- **O código:** a subchave `rastro` (`config.py`), a `r_intervalo` (`afeto.py`), o `motivo["cadeia"]` (`adapt.py`), o texto, e as
  medidas da seção 4 no `metrics.py`.
- **Os testes** (`tests/test_rastro_cadeia.py`, nome PROPOSTO), nas sementes dos testes:
  - desligada, a vida e o `motivo` saem byte a byte;
  - ligada, a escolha é idêntica decisão a decisão, e o estado do cérebro no fim é o mesmo;
  - a C-FECHO e a C-UMA-VEZ;
  - o r do mesmo tick do rastro é o da `consequencia`;
  - cada medida do `metrics.py` contra um caso feito à mão (uma vida de 3 decisões com os corpos escritos no teste);
  - o texto de três decisões conhecidas: um consumo, um sono e uma troca de intenção;
  - o script falha alto com a fonte errada.
- **O script** `experiments/rastro_cadeia.py` (nome PROPOSTO): lê a fonte, faz as conferências da seção 3.3, refaz as vidas e grava
  `artifacts_v3_pet_vivo/r1/` (`meta.json`, `resultado.json` e as medidas por vida).
- **O modelo recomendado:** o Sonnet, para a implementação com escopo claro.
- **O relato:** um `docs/RESULTADO_V3_PET_VIVO_R1.md` novo. A linha da regra da seção 5 vai também no corpo do PR.
- **Roda uma vez.** Nada se ajusta olhando o resultado. Uma regra diferente entra por adendo, antes do replay.

**O código não entra neste PR.** Este PR é só de documentos.

## 8. O que fica de fora

- **Qualquer crédito:** o traço, a linha de base e o `η_int` são do R2.
- **O elogio ligado:** as vidas foram vividas sem a `ConfigElogio`. Ligá-la no replay mudaria a vida.
- **O TypeScript, o painel e o balão:** depois da LZ3 (RA-3). A ponte ao jogador da análise (o texto que cita o `cadeia_id`) é desse PR.
- **Os cenários T1 a T8** da análise: cada um é da etapa do mecanismo dele.
- **O `tau_c`:** só se mede a troca de intenção (a INT-6). Nada muda.
- **As vidas da C4** e os outros braços do PV-2.
- **O `engine.py`** não muda.

## 9. A literatura

Este plano não cita referência nova. O mecanismo que o R1 prepara (o crédito com um traço e uma linha de base) está na análise, com as
referências dela e o estado de cada uma. Aqui só se mede o que o código de hoje já faz.

## 10. As decisões com o Matheus (DECIDIDAS pela recomendação em 2026-11-19, "Aprovo todas"; D-RA-7)

| # | decisão | recomendação | custo de errar |
|---|---|---|---|
| **RA-1** | onde fica o plano | **este arquivo, na frente PET_VIVO,** ao lado dos planos da 0b e do PV-2 | uma frente nova (`TAREFA_V3_INTEGRACAO`) espalharia a cadeia em dois lugares; um adendo ao plano do PV-2 misturaria uma leitura com uma run de mecanismo já encerrada |
| **RA-2** | a fonte das vidas | **o HOJE da run do PV-2** (2 400), com o OLF-0 e o HOJE do v38 ao lado; não as da C4 | com as da C4, os números seriam do cérebro de antes do jogo v17, e o replay pediria o rastro portado para o código antigo. Com as do PV-2, a C-G1 pode falhar se a `main` tiver mudado o REL, e aí vem um adendo |
| **RA-3** | o TypeScript | **só o Python agora;** o rastro no TS, com a paridade do registro e o texto no painel, num PR próprio depois da LZ3 | fazer agora mexe no `leitura.ts` e no `motor.ts`, que a LZ3 vai reescrever (a INT-7), e o trabalho se perde no conflito. Esperar deixa o jogador sem o rastro por mais uma etapa |
| **RA-4** | as linhas de base medidas | **as duas: a global e a por contexto** (acordado, dormindo), pela média da vida | só com a por contexto, a H-CTX não tem como aparecer. A média da vida não é a média móvel do R2: o número exato pode mudar com o `k_b` |
| **RA-5** | os cortes da regra de leitura | **1/2 e 1/4 na L-FORA; 0,05 no η²** | cortes altos demais dão "indeterminado" e o plano do R2 mede tudo de novo; baixos demais deixam ruído decidir o desenho do R2. Como nada vai ao jogo por esta regra, o custo é uma etapa de papel |
| **RA-6** | o corte do custo | **4 h de parede com 4 processos;** acima disso, um adendo antes do replay | um replay longo segura a máquina das outras frentes (V3-D8) |

## 11. O que este plano não demonstra, mesmo depois do replay

- Nada sobre o jogo web nem sobre o v38 além da checagem descritiva.
- Nada fora dos 14 dias, do mundo do MVP e dos lugares da C4.
- Nada sobre o crédito: medir que o sinal existe não mostra que creditá-lo ajuda.
- Nada sobre o efeito do dono: a M-DONO é uma coincidência no tempo, e não uma causa.
