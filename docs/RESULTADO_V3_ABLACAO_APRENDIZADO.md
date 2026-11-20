# Resultado V3: a ablação do aprendizado no jogo (EVIDENCIA A2)

Plano: `docs/PLANO_ANALISE_V3_ABLACAO_APRENDIZADO.md` (APROVADO pelo Matheus em 2026-11-16, "Aprovo, pode rodar"; a AB-2b, "Mapear para
acariciar/tapa"). Tarefa: `docs/TAREFA_V3_EVIDENCIA.md`, fase A2. Worker: Claude Code, Opus 5.5, branch `v3-evidencia-a2`.

**A leitura, pela regra da seção 5.3 do plano: muda.** 9 das 15 medidas são rejeitadas pelo Holm (α = 0,05). O P1 e o P2 mudam o
comportamento do pet no jogo, e **H fica confirmada**. As diferenças são pequenas: a maior está no motivo `cheiro`, −0,0092 da fração das
decisões, e a distância de variação total entre as distribuições médias de ação de A e de B é 0,0084 (n = 200 unidades).

## 1. Os commits e a run

| o quê | onde |
|---|---|
| o plano PROPOSTO, sozinho | `2481e33e` |
| o plano APROVADO, com o harness, o orquestrador, as configs, os testes e a faixa | `ecbe0320` (o `git_head` da run, `git_limpo: true`) |
| os artefatos da run | `81fe6e07` |
| este resultado e o registro | o commit seguinte |

| a run | valor |
|---|---|
| comando | `python experiments/run_v3_ablacao_aprendizado.py --config experiments/configs/v3_ablacao_aprendizado/run.json` |
| o harness | `node web/app/scripts/ablacao_aprendizado.ts --primeira 98101 --k 200 --dias 3` |
| sementes | 98101…98300 (200 unidades), da faixa 98101…98505 reservada para a A2 |
| vidas | 1.200 (200 sementes × 3 donos × 2 braços), 3 dias cada, sem luta; 172.800 decisões em cada braço |
| ambiente | Python 3.13.0, Node v24.19.0; parede 413 s, um processo Node |
| quando | 2026-11-16, das 20:10 às 20:17 |

| artefato em `artifacts_v3_ablacao_aprendizado/run/` | sha256 |
|---|---|
| `medidas.json` | `f2adac9806f3a7215252288336e9dc02ff45cabaf045a291c704db77b867a4af` |
| `resultado.json` | `ced7c7932f0b423ebe9c4203ff15003a6bd347096fc885779ff7cd72161b3299` |
| `meta.json` | `2a9f8081eb909a303689a1c7d17a56407d23d7e054f8149b82ebd71e267a74a2` |

O `meta.json` traz ainda o sha256 do plano (`f10a319c…`), da config, do orquestrador, do harness, do `plast.ts` (`92bf0f03…`), do
`adapt.ts` (`ebeb2aac…`) e do `impulso.ts` (`84d4a64b…`), e o sha256 do log e da sequência das decisões de cada uma das 1.200 vidas.

**Antes da run** (no `ecbe0320`): a suíte Python deu 5.833 passados, 9 pulados e 3 falhas, todas anteriores a este branch. As três são o
`test_fala_livre::test_log_do_pet_nao_conhece_a_fala`, o `test_gabarito_mvp_produto_web::test_o_layout_do_mvp_nao_vaza_para_a_pesquisa` e o
`test_redecidir_evento::test_g2_separado_...` (o `auditoria_pet_vivo.py` e o `figuras_artigo_a1.py`); nenhuma toca arquivo desta fase. O
Vitest do jogo deu 1.931 passados e 3 pulados.

## 2. A manipulação conferida

- **No braço B, nenhuma unidade leu termo aprendido:** 0 unidades com `incentivo` ou `habito` diferente de 0 em 172.800 decisões. No A,
  748.757 leituras de unidade (somadas sobre as decisões) tinham algum termo aprendido.
- **Na unidade escolhida pelo A**, a média por decisão foi 11,18 de `incentivo` e 3,44 de `habito` (descritivo, n = 172.800 decisões, sem
  IC no artefato).
- **O resto:** 0 escolhas fora da lista das unidades, 0 mortes e 0 ações do dono recusadas pelo motor, nos dois braços.
- **Cada vida rodou duas vezes** com o mesmo sha256 do log e das decisões. As do A também foram refeitas pelo `Motor.reproduzir`, com as
  mesmas ações.

## 3. As 15 medidas

A − B por unidade (a média dos 3 donos em cada semente), n = 200, IC95 pelo t com gl 199, p bilateral e Holm sobre a família de 15. Os
níveis de A e de B são descritivos (as médias das 200 unidades). A margem efetiva, o menor efeito com poder 0,8 pelo dp observado, fica
ao lado, como o plano pede, e não muda a decisão.

| medida | A | B | A − B | IC95 | p | p (Holm) | rejeita | margem efetiva |
|---|---|---|---|---|---|---|---|---|
| `acao:ocioso` | 0,0626 | 0,0615 | +0,00109 | [+0,00016; +0,00202] | 2,2e−2 | 0,13 | não | 0,00133 |
| `acao:dormir` | 0,4315 | 0,4357 | −0,00422 | [−0,00552; −0,00293] | 8,9e−10 | 1,1e−8 | **sim** | 0,00185 |
| `acao:comer` | 0,0500 | 0,0475 | +0,00257 | [+0,00201; +0,00313] | 9,5e−17 | 1,3e−15 | **sim** | 0,00079 |
| `acao:brincar` | 0,0595 | 0,0572 | +0,00229 | [+0,00128; +0,00329] | 1,3e−5 | 1,2e−4 | **sim** | 0,00144 |
| `acao:chamar_atencao` | 0,0741 | 0,0716 | +0,00251 | [+0,00036; +0,00465] | 2,2e−2 | 0,13 | não | 0,00306 |
| `acao:explorar` | 0,3210 | 0,3252 | −0,00422 | [−0,00620; −0,00224] | 3,9e−5 | 3,1e−4 | **sim** | 0,00283 |
| `acao:emburrar` | 0,0013 | 0,0013 | −0,00000 | [−0,00026; +0,00026] | 1,0 | 1,0 | não | 0,00037 |
| `tipo:comida` | 0,0401 | 0,0372 | +0,00293 | [+0,00254; +0,00332] | 5,2e−34 | 7,7e−33 | **sim** | 0,00056 |
| `tipo:cheiro` | 0,0952 | 0,1043 | −0,00915 | [−0,01122; −0,00707] | 1,3e−15 | 1,7e−14 | **sim** | 0,00296 |
| `tipo:bola` | 0,0193 | 0,0187 | +0,00052 | [−0,00044; +0,00148] | 0,28 | 0,70 | não | 0,00137 |
| `tipo:vagar` | 0,2100 | 0,2061 | +0,00386 | [+0,00176; +0,00596] | 3,6e−4 | 2,5e−3 | **sim** | 0,00299 |
| `tipo:ponto` | 0,0257 | 0,0250 | +0,00071 | [−0,00038; +0,00179] | 0,20 | 0,70 | não | 0,00154 |
| `tipo:sem_objeto` | 0,6097 | 0,6086 | +0,00113 | [−0,00051; +0,00278] | 0,18 | 0,70 | não | 0,00235 |
| `reflexo` | 0,3604 | 0,3649 | −0,00454 | [−0,00618; −0,00291] | 1,3e−7 | 1,4e−6 | **sim** | 0,00233 |
| `nada_a_fazer` | 0,0025 | 0,0029 | −0,00039 | [−0,00055; −0,00022] | 7,3e−6 | 7,3e−5 | **sim** | 0,00024 |

**Lido em palavras:** com o aprendizado ligado, o pet come e brinca um pouco mais, e dorme e explora um pouco menos. No motivo, vai mais à
comida e ao vagar e menos ao cheiro, age menos por reflexo e fica menos vezes sem nada a fazer. `ocioso` e `chamar_atencao` têm o IC sem
ajuste fora do 0, mas não passam no Holm. Todas as diferenças estão abaixo de 0,01 da fração das decisões.

**Descritivo, ao lado:** a distância de variação total entre as distribuições médias de ação de A e de B é 0,0084 (n = 200 unidades; o
artefato dá o valor sem IC).

## 4. O que esta run não demonstra

- que o aprendizado é bom ou ruim para o pet: nenhuma medida de bem-estar, de vínculo ou de dono entra aqui;
- o resultado fora do ovo v38, fora dos 3 donos sintéticos, fora dos 3 dias de vida e com luta;
- nada sobre o Python, onde a C4 mediu;
- qual das duas regras, a P1 ou a P2, produz a diferença: o braço B zera as duas juntas;
- que a diferença seja grande o bastante para um jogador notar. O plano não tem margem de relevância (seção 5.2), e esta run não cria uma
  depois de ver o dado.

## 5. CHECKPOINT A3

A classe vai ao Matheus como saiu: **muda**. O caso do pedido ("se a ablação der nula, o 'aprendizado em vida' é política fixa + estado +
memória para efeito de produto") **não se aplica**. O efeito existe no jogo e é estatisticamente firme, mas é pequeno: 0,84 % da massa das
ações muda de lugar, em média.

A decisão é do Matheus: seguir para a A3 (o `PREREGISTRO.md`, o `tools/replicar_run.py` e a replicação da C4) como está, ou registrar
antes alguma leitura de produto sobre o tamanho do efeito. A recomendação é seguir para a A3 sem mudar nada. A A3 não depende do tamanho do
efeito, e uma leitura de produto escrita agora teria de criar um limiar de relevância depois de ver o dado. Errar aqui custa pouco: a
leitura de produto pode entrar na síntese da A4, rotulada como interpretação, sem mexer nesta run.
