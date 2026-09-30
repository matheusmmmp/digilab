# Reequilíbrio dos arquétipos do combate V21C — rodada 2 (D2, E1, E2, vigia e D1, sobre A + C)

Status: **rodada de calibração** (2026-09-30). Continua `docs/EQUILIBRIO_RODADA1.md` a partir da variante A + C.
Decisão do Matheus: primeiro as propostas que não mexem na base do combate (D2, E2, a resposta do vigia; E1 medido
junto), e o parry maior (D1) só no fim. Nada foi adotado: tudo está atrás de chaves **desligadas por padrão**, a web
não mudou e a validação (sementes 4101…4505) não foi tocada.

- **Script:** `python experiments/calibrar_equilibrio.py --rodada 2 --etapa todas` (matriz, painel, gate e
  mecanismo; ~12 min com 8 processos) e `--rodada 2 --etapa colaterais --variante a_c_e2v_v` (e `--variante a_c`;
  ~80 s cada). Sem `--rodada` o script é o da rodada 1 e reproduz `equilibrio_rodada1/matriz.json`.
- **Artefatos:** `artifacts_combate_v21c/equilibrio_rodada2/` (`matriz.json`, `painel.json`, `gate.json`,
  `mecanismo.json`, `colaterais_a_c_e2v_v.json`, `colaterais_a_c.json`). Todo número abaixo vem deles.
- **Regras:** as da validação V21C (`experiments/configs/v21c/validacao.json`) mais as chaves da variante.
- **Sementes:** só as de calibração (3101…3505), 100 partidas por par por semente e espécie, os mesmos nomes e
  sementes do diagnóstico e da rodada 1.

## Resultado em cinco frases

1. **A melhor variante é A + C + E2 só no vigia + V** (`a_c_e2v_v`): 7 das 8 formas na faixa [0,40; 0,60], contra as
   outras 7 e contra o painel, e todas vencem pelo menos 3 das outras 7 (A6 passa). A distância até a faixa cai de
   0,333 (A + C) para 0,125.
2. **O gate ainda não passa.** Falham A1/A2 (só o furioso, 0,725 e 0,672), A3 (suporte 3), A4 (9 e 7 pares
   extremos) e A5 (amplitude 0,319 e 0,425).
3. **D2 e D1 não mexem no furioso** (0,726 → 0,723 e 0,725 → 0,723). A investida contra quem recua passa a errar
   4,65 vezes por partida contra a sentinela, mas o furioso troca a investida pelo avanço e pelo golpe rápido e
   continua em 0,99–1,00 contra os caçadores. O D1 só pega quem defende contra o golpe rápido, e quase ninguém que o
   furioso esmaga faz isso.
4. **E2 funciona, mas no titã passa do ponto:** o titã vai de 0,02 a 0,81 contra a sentinela e sobe para 0,727
   (vence 6 das 7), porque o A já lhe deu os guardiões. No vigia, E2 põe os caçadores em 0,63 e 0,59 e o leva para
   dentro da faixa. E1 (regra) faz o mesmo que E2 no titã, com mais efeito colateral.
5. **Os efeitos colaterais protegidos não quebram** na melhor variante (S1, E4 na escala e campanha iguais aos da
   A + C). O E3 da pele dura passa. O **E3 do contra-golpe falha**, mas já falhava com A + C: é efeito do A, não
   desta rodada.

## 1. O que mudou (atrás da chave)

Cinco chaves novas na `ConfigCombateV21D` (`digilab/config.py`), todas `False` por padrão. A V21C não ganhou campo:
o `asdict` e o `config_sha256` das configs V21C gravadas não mudam. `ADULTOS`, `SOMBRIOS` e as respostas do E3
continuam as canônicas. As listas novas são variantes escolhidas em `bots.gambits_adulto`.

- **D2 — `investida_erra_contra_recuo`** (`v21/regras.resolver`): a investida não causa dano se o alvo recua no mesmo
  turno, e o recuo vale contra ela. A fuga condicionada (C3) deixa de anular o recuo só quando o rival faz uma
  investida; o avanço comum continua prendendo quem recua. A sentinela com a passiva pronta vai para longe, como
  antes.
- **E1 — `preparo_prende`** (`v21/regras.resolver`): recuar não afasta de quem prepara o pesado no mesmo turno. Vale
  para toda forma que prepara (duelista, furioso, guardiões e colossos), sem exceção para a sentinela.
- **E2 — `tita_bate_em_quem_recua` e `vigia_bate_em_quem_recua`** (listas `bots.GAMBITS_TITA_V21D` e
  `bots.GAMBITS_VIGIA_V21D`): a regra `se(perto, oponente_frequente(recuar)) → golpe_rapido` entra logo antes do
  preparar. Para caber no limite de 8, sai `oponente_preparando → esquivar`: com o A, o preparo sob pele já não
  aparece, e o titã responde ao preparo com a pele antes. Uma chave por forma, para medir cada uma sozinha.
- **V — `vigia_recua_do_preparo_sob_pele`** (lista do vigia): a regra
  `se(oponente_vai_preparar, oponente_frequente(pele_dura)) → recuar` entra no topo. O preparo sob pele não se
  interrompe, então o vigia sai de perto no turno do preparo e o pesado erra por distância. A linguagem não tem
  "o rival está com pele", e a frequência de `pele_dura` nas últimas 5 ações é o que existe de mais próximo. Sai
  `guts abaixo de 20 → carregar`; a regra final `defender` também recupera guts.
- **D1 — `dano_parry` 5 → 8:** não é chave nova. `dano_parry` já é campo da `ConfigCombateV2C`, e a variante só o
  sobrescreve em `regras_base` (a validação usa 5). **Mexe na base V2C inteira: antes de ser adotado, exige rerodar
  G1–G9 da base V2C** (e, por tabela, toda a bateria V21C).

As sombrias não mudam. O colosso partido continua com a lista canônica do titã, e o bastião rachado com a do espelho
sem leitura.

**Reprodução com as chaves desligadas** (`tests/test_equilibrio_v21d.py`; conferências que falham alto no script):
- V21D com as sete chaves em `False` joga as mesmas partidas (log igual) que a V21C, com as mesmas listas;
- matriz da v21c = `diagnostico_arquetipos/reproducao.json` (ε 0,05) e `epsilon.json` (ε 0,15);
- matriz da v21c e da a_c = `equilibrio_rodada1/matriz.json`; painel da v21c = `diagnostico_arquetipos/painel.json`
  e painel da a_c = `equilibrio_rodada1/painel.json`;
- campanha da v21c = `experiments/configs/escala/calibracao.json`; E3 da v21c = `calibracao/v4/uso_tecnicas.json`;
- `mecanismo.json` refaz as partidas da matriz turno a turno e confere os pontos com `matriz.json`;
- a rodada 1 rodada de novo com o script novo (`--rodada 1 --etapa matriz`) sai com o mesmo `por_variante`.

Suíte inteira (`python -m pytest tests/ -q`, chaves desligadas): 426 passaram e 1 foi pulado (os 421 da rodada 1 mais
5 testes novos).

**Não lê as chaves** (como na rodada 1): os pets de pesquisa e as runs V3, E1 e confirmatória (lutam com
`ADULTOS[...]` e `campanha.REGRAS_CAMPANHA`). Ligar a versão adotada nelas é trabalho da decisão, junto com a web.

## 2. Força por forma (`matriz.json`, `painel.json`)

Força = média dos pontos contra as outras 7 (mesma espécie dos dois lados, média das 4 espécies), ε 0,05. Toda
variante abaixo inclui A + C.

| forma | V21C | A + C | + D2 | + E1 | + E2 titã | + E2 vigia | + E2 (os dois) | + V | **+ E2 vigia + V** | + E2 + V | + E2 vigia + V + D1 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| furioso | 0,755 | 0,726 | 0,723 | 0,719 | 0,709 | 0,725 | 0,709 | 0,726 | **0,725** | 0,709 | 0,723 |
| sentinela | 0,648 | 0,649 | 0,702 | 0,400 | 0,536 | 0,564 | 0,451 | 0,649 | **0,564** | 0,451 | 0,564 |
| espelho | 0,640 | 0,406 | 0,407 | 0,405 | 0,406 | 0,405 | 0,404 | 0,418 | **0,416** | 0,416 | 0,403 |
| emboscador | 0,615 | 0,623 | 0,629 | 0,403 | 0,512 | 0,544 | 0,434 | 0,623 | **0,544** | 0,434 | 0,544 |
| duelista | 0,521 | 0,467 | 0,409 | 0,513 | 0,450 | 0,473 | 0,456 | 0,473 | **0,477** | 0,460 | 0,473 |
| muralha | 0,400 | 0,402 | 0,402 | 0,400 | 0,402 | 0,401 | 0,401 | 0,423 | **0,422** | 0,422 | 0,399 |
| vigia | 0,248 | 0,265 | 0,264 | 0,456 | 0,258 | 0,423 | 0,417 | 0,283 | **0,446** | 0,435 | 0,488 |
| titã | 0,173 | 0,463 | 0,463 | 0,704 | 0,727 | 0,465 | 0,729 | 0,406 | **0,406** | 0,674 | 0,407 |

Contra o painel B (pet canônico, ε 0,05, 32 bots sob as regras e listas da variante):

| forma | V21C | A + C | **+ E2 vigia + V** | + E2 + V | + E2 vigia + V + D1 |
|---|---|---|---|---|---|
| furioso | 0,702 | 0,670 | **0,672** | 0,664 | 0,667 |
| sentinela | 0,615 | 0,618 | **0,545** | 0,445 | 0,545 |
| espelho | 0,608 | 0,412 | **0,430** | 0,429 | 0,417 |
| emboscador | 0,612 | 0,622 | **0,552** | 0,456 | 0,552 |
| duelista | 0,532 | 0,481 | **0,494** | 0,487 | 0,484 |
| muralha | 0,406 | 0,413 | **0,427** | 0,426 | 0,410 |
| vigia | 0,287 | 0,288 | **0,449** | 0,438 | 0,489 |
| titã | 0,235 | 0,492 | **0,437** | 0,663 | 0,439 |

(O painel das outras variantes está em `painel.json`; a ordem é a mesma das forças.)

Outras combinações medidas: + E2 vigia + V + D2 (furioso 0,722, sentinela 0,617, duelista 0,418), + E1 + V (furioso
0,720, titã 0,703) e + E2 vigia + V + D1 + D2 (furioso 0,720, sentinela 0,617, muralha 0,399).

Confrontos que mudam (ε 0,05, pontos da linha contra a coluna):

| confronto | V21C | A + C | + D2 | + E1 | + E2 titã | + E2 vigia | + V | **+ E2 vigia + V** | + E2 + V |
|---|---|---|---|---|---|---|---|---|---|
| furioso × sentinela / × emboscador | 1,00 / 1,00 | 1,00 / 1,00 | 0,99 / 1,00 | 0,99 / 0,98 | 1,00 / 1,00 | 1,00 / 1,00 | 1,00 / 1,00 | **1,00 / 1,00** | 1,00 / 1,00 |
| furioso × duelista | 0,92 | 0,92 | 0,92 | 0,92 | 0,92 | 0,92 | 0,92 | **0,92** | 0,92 |
| furioso × titã / × vigia | 0,99 / 0,99 | 0,94 / 0,78 | 0,94 / 0,78 | 0,94 / 0,78 | 0,83 / 0,78 | 0,94 / 0,78 | 0,94 / 0,78 | **0,94 / 0,78** | 0,83 / 0,78 |
| titã × sentinela / × emboscador | 0,02 / 0,01 | 0,02 / 0,01 | 0,02 / 0,01 | 0,87 / 0,83 | 0,81 / 0,79 | 0,02 / 0,01 | 0,02 / 0,01 | **0,02 / 0,01** | 0,81 / 0,79 |
| vigia × sentinela / × emboscador | 0,03 / 0,03 | 0,04 / 0,04 | 0,04 / 0,04 | 0,72 / 0,67 | 0,04 / 0,04 | 0,63 / 0,59 | 0,04 / 0,04 | **0,63 / 0,59** | 0,63 / 0,59 |
| vigia × titã | 0,96 | 0,13 | 0,13 | 0,13 | 0,08 | 0,11 | 0,53 | **0,52** | 0,45 |
| vigia × muralha / × espelho | 0,61 / 0,01 | 0,49 / 0,54 | 0,49 / 0,54 | 0,49 / 0,55 | 0,49 / 0,54 | 0,49 / 0,55 | 0,34 / 0,46 | **0,35 / 0,47** | 0,35 / 0,47 |
| duelista × sentinela / × emboscador | 0,78 / 0,88 | 0,78 / 0,88 | 0,42 / 0,84 | 1,00 / 1,00 | 0,78 / 0,88 | 0,78 / 0,88 | 0,78 / 0,88 | **0,78 / 0,88** | 0,78 / 0,88 |
| titã × espelho / × muralha | 0,04 / 0,61 | 0,87 / 0,89 | 0,87 / 0,89 | 0,88 / 0,90 | 0,88 / 0,89 | 0,87 / 0,89 | 0,87 / 0,89 | **0,87 / 0,89** | 0,88 / 0,89 |

## 3. Cada proposta sozinha, e por quê (`mecanismo.json`, contagens médias por partida)

**D2 — o recuo esquiva a investida.** A condição acontece, mas não decide.
- Furioso × sentinela: sem D2, 2,58 investidas por partida encontram a sentinela recuando e acertam. Com D2, são 4,65,
  e todas erram. O furioso passa a fazer mais investidas (6,91 → 9,77), mais avanços (3,47 → 6,79) e mais golpes
  rápidos (3,95 → 5,14). A sentinela recebe o mesmo dano (101,7 → 100,6), e o furioso ainda faz 0,99.
- Furioso × emboscador: 3,19 investidas erram por partida; o emboscador recebe 92,2 → 91,7 de dano, e o furioso
  segue em 1,00.
- O motivo é o do diagnóstico: com a C3, o avanço comum prende quem recua, e de perto o golpe rápido acerta.
  A sentinela e o emboscador passam boa parte da distância média marcando e atirando, não recuando.
- Colateral: o duelista, que também tem investida, cai contra a sentinela (0,78 → 0,42) e sai da faixa na
  combinação com D2 (0,418). A sentinela sobe para 0,702 com D2 sozinho.

**E2 no titã.** A regra nova dispara 6,48 vezes por partida contra a sentinela, e os pesados caem de 5,17 para 0,54
por partida. O titã vai de 0,02 para 0,81 contra a sentinela e de 0,01 para 0,79 contra o emboscador. Como o A já lhe
deu os guardiões (0,87 e 0,89), ele passa a vencer 6 das 7 e chega a 0,727. Sozinho, o titã fica fora da faixa pelo
lado de cima.

**E2 no vigia.** A regra dispara 3,79 (sentinela) e 3,96 (emboscador) vezes por partida, e os pesados caem de 2,96
para 0,43. O vigia vai de 0,04 para 0,63 e 0,59 contra os caçadores e de 0,265 para 0,423 no geral. O vigia não
tinha os guardiões (0,49 e 0,54), então ganha sem passar do ponto. A sentinela e o emboscador caem para 0,564 e
0,544 e entram na faixa.

**E1 — o preparo prende (regra).** Faz nos dois colossos o que E2 faz, e mais: titã 0,87 e 0,83, vigia 0,72 e 0,67
contra os caçadores. Só que vale para todos que preparam: o duelista passa a fazer 1,00 contra os dois caçadores, e
os caçadores caem para 0,400 e 0,403. O titã vai a 0,704. É mais caro que E2, porque mexe em regra e atinge todas as
formas que preparam o pesado. Não entra na melhor variante.

**V — o vigia recua do preparo sob pele.** A regra dispara 2,18 vezes por partida contra o titã. Os pesados do titã
que erram por distância vão de 0,04 para 2,15 por partida, e o vigia × titã vai de 0,13 para 0,53. Custo: o vigia
cai contra a muralha (0,49 → 0,34) e o espelho (0,54 → 0,46). As guardiãs não têm pele dura, então a regra nova
nunca dispara contra elas; o que muda nesses confrontos é a regra `carregar` que saiu para dar lugar à V. Mesmo
assim, o vigia sobe no geral (0,265 → 0,283) e resolve o que a rodada 1 deixou aberto: com A, o vigia perdia do titã
em todo confronto.

**D1 — parry 5 → 8.** Quase nada. O furioso fica em 0,723. Ele esmaga quem não defende contra o golpe rápido: o
vigia defende 1,72 vezes por partida e o titã 0,08. Contra os caçadores o parry nem entra. O que o D1 move é a
guardiã: espelho 0,416 → 0,403, muralha 0,422 → 0,399 (sai da faixa), vigia 0,446 → 0,488. O suporte vai de 3
para 4.

**O que o furioso ainda faz** (melhor variante): 1,00 contra os dois caçadores (avanço + golpe, ver D2), 0,92 contra
o duelista, 0,94 contra o titã e 0,78 contra o vigia. Contra os colossos, o golpe rápido interrompe o preparo: 2,24
preparos do titã e 4,38 do vigia por partida.

## 4. Gate proposto, item a item (`gate.json`; calibração, não validação)

| gate | critério | V21C | A + C | + E2 vigia | **+ E2 vigia + V** | + E2 + V | + E1 + V | + E2 vigia + V + D1 |
|---|---|---|---|---|---|---|---|---|
| A1 força entre formas | 8 em [0,40; 0,60] | 1 de 8 | 4 de 8 | 7 de 8 | **7 de 8** (furioso 0,725) | 6 de 8 | 6 de 8 | 6 de 8 |
| A2 força contra o painel | 8 em [0,40; 0,60] | 2 de 8 | 4 de 8 | 7 de 8 | **7 de 8** (furioso 0,672) | 6 de 8 | 5 de 8 | 7 de 8 |
| A3 suporte | ≥ 6 | 5 | 3 | 3 | **3** | 3 | 3 | 4 |
| A4 decisividade | ≤ 7 extremos com ε 0,05 e ≤ 4 com ε 0,15 | 17 e 12 | 11 e 9 | 9 e 7 | **9 e 7** | 6 e 5 | 9 e 7 | 9 e 7 |
| A5 amplitude | ≤ 0,20 com ε 0,05 e 0,15 | 0,582 e 0,587 | 0,461 e 0,434 | 0,324 e 0,434 | **0,319 e 0,425** | 0,293 e 0,411 | 0,320 e 0,420 | 0,324 e 0,417 |
| A6 lugar no ciclo | toda forma vence ≥ 2 das 7 | titã 1 | vigia 1 | passa | **passa** (mínimo 3) | passa | passa | passa |
| distância até a faixa (forças / painel) | | 0,637 / 0,415 | 0,333 / 0,222 | 0,125 / 0,071 | **0,125 / 0,072** | 0,183 / 0,128 | 0,223 / 0,172 | 0,124 / 0,067 |

**Melhor variante: A + C + E2 no vigia + V** (`a_c_e2v_v`). Ela empata com + E2 vigia nas forças e na distância, e a V
acrescenta o que faltava ao vigia: o vigia × titã sai de 0,11 para 0,52, e toda forma passa a vencer pelo menos 3.
A + E2 + V (com o titã) tem menos extremos (6 e 5) e amplitude menor, mas o titã fica em 0,674 e vence 6 das 7.
Com o D1, a muralha sai da faixa e o furioso não se move.

O que falta na melhor variante:
- **A1/A2:** só o furioso, 0,125 acima da faixa entre formas e 0,072 contra o painel.
- **A3:** o suporte é {furioso 0,364, muralha 0,361, sentinela 0,274}.
- **A4** (9 extremos com ε 0,05): 4 do furioso (× sentinela 1,00, × emboscador 1,00, × titã 0,94, × duelista 0,92)
  e 5 fora dele (sentinela × muralha 1,00, emboscador × muralha 1,00, espelho × emboscador 0,00, sentinela × titã
  0,98, emboscador × titã 0,99). Mesmo sem o furioso o A4 não passa.
- **A5:** com ε 0,05, 0,319 é o furioso (0,725) menos o titã (0,406). Sem o furioso seria 0,564 − 0,406 = 0,158.
  Com ε 0,15 a amplitude é 0,425 (furioso 0,765, espelho 0,340). Sem o furioso, emboscador 0,620 − espelho 0,340
  = 0,280: o ruído derruba as guardiãs, como no diagnóstico.

## 5. Efeitos colaterais (`colaterais_a_c_e2v_v.json`, `colaterais_a_c.json`)

Nas mesmas sementes de calibração, comparados com a V21C medida no mesmo script.

| verificação | V21C | A + C | **A + C + E2 vigia + V** |
|---|---|---|---|
| **S1** (nenhuma sombria vence as 8 normais) | passa | passa | **passa** |
| devastador (média; vitórias) | 0,389; 3 | 0,368; 3 | 0,371; 3 (duelista, titã, vigia) |
| colosso partido | 0,154; 1 (muralha) | 0,265; 2 | 0,234; 2 (espelho, muralha) |
| predador | 0,329; 2 | 0,336; 2 | 0,332; 2 |
| bastião rachado | 0,118; 0 | 0,146; 0 | 0,147; 0 |
| **E4 na escala** (adulto sem treino ≥ 0,60 contra o Champion sem treino e com +22) | passa, menor 0,836 | passa, menor 0,836 | **passa**, menor 0,836 |
| **campanha na escala** (≤ 0,30 sem treino e ≥ 0,80 com o típico) | 4 de 5 (Sentinela fora) | 4 de 5 | **4 de 5** (Sentinela fora) |
| Sentinela (exceção aceita) | 0,386 / 0,705, travado: colosso | 0,389 / 0,758 | 0,389 / 0,758, travado: colosso |
| Soberano | 0,153 / 0,911 | 0,187 / 0,911 | 0,196 / 0,911 |
| **E3 pele dura** (resposta "ficar longe") | 0,243 → 0,003 | 0,384 → 0,003 | **0,435 → 0,101** (titã 0,412 → 0,005; vigia 0,457 → 0,197) |
| E3 investida | 0,616 → 0,578 | 0,577 → 0,495 | 0,582 → 0,499 |
| E3 marcar | 0,613 → 0,311 | 0,617 → 0,369 | 0,546 → 0,447 |
| **E3 contra-golpe** | 0,522 → 0,461 | **0,417 → 0,483** (falha) | **0,428 → 0,495** (falha) |

- S1, E4 e a campanha saem como na A + C da rodada 1. Brutamontes, Carcereiro e Porteiro ficam iguais nas quatro
  casas; o Soberano sobe um pouco sem treino (0,187 → 0,196) e continua abaixo de 0,30.
- **E3 da pele dura** (pedido na rodada 1): passa. A resposta ainda derruba os dois colossos, mas o vigia com a V
  resiste mais (0,197).
- **E3 do contra-golpe falha já com A + C.** Por usuário: o espelho **sobe** com a resposta declarada ("recuar de
  perto e atirar"), de 0,629 para 0,917 na V21C e de 0,424 para 0,947 na melhor variante, porque ele reflete o
  disparo. A muralha cai (0,416 → 0,005 na V21C; 0,431 → 0,043). Na V21C a média ainda caía (0,522 → 0,461); com
  A o espelho perde força sem a resposta (0,629 → 0,419), e a média passa a subir. O problema é antigo: a resposta
  declarada do contra-golpe nunca funcionou contra o espelho, e a média escondia isso. A causa agora é o A, não esta
  rodada.

**Não medidos:** E2 (espécies), E5, G6b, G8 e G9; as runs de pesquisa com pets reais; a paridade web.

## 6. Recomendação

**Levar à validação ainda não.** A variante a levar é **A + C + E2 no vigia + V** (`a_c_e2v_v`): só listas e uma
condição (A), sem mexer na base. Ela põe 7 das 8 formas na faixa e passa a A6, sem quebrar S1, E4 e campanha. O gate
proposto ainda reprova em quatro itens, e três deles passam pelo furioso. O furioso não responde a nada desta rodada:
D2 e D1 foram medidos e ficam em 0,723. Validar agora (4101…4505) e espelhar na web gastaria a validação numa versão
que já sabemos reprovada.

O que ainda falta, em ordem:
1. **Furioso pela base (rodada 3).** O excesso vem do avanço que prende o recuo (C3) contra os caçadores e do golpe
   rápido que interrompe o preparo contra os colossos. D2 só tira a investida, e o furioso a troca pelo avanço. D1 só
   pega quem defende. As saídas são mexer na base V2C: a C3 contra o avanço (não só contra a investida) ou o custo do
   golpe rápido. As duas exigem rerodar G1–G9 da base V2C antes de qualquer adoção, assim como o D1.
2. **Decisividade e suporte:** os extremos sem o furioso são caçador × guardiã (1,00 e 0,00) e caçador × titã
   (0,98 e 0,99). E2 no titã fecha os dois últimos, mas o torna dominante (0,727), porque o A lhe deu os guardiões.
   Para usar E2 no titã, os guardiões precisariam de uma resposta ao preparo escondido (lista do espelho e da
   muralha), fora do escopo desta rodada.
3. **E3 do contra-golpe:** decidir se a resposta declarada ("recuar e atirar") muda, já que ela nunca funcionou
   contra o espelho; ou aceitar a exceção. A falha vem do A.

Se o Matheus preferir fixar o ganho agora e deixar o furioso como exceção conhecida, a versão a validar e espelhar
na web é `a_c_e2v_v`, com as chaves `preparo_sob_pele_oculto`, `muralha_lista_espelho`, `vigia_bate_em_quem_recua`
e `vigia_recua_do_preparo_sob_pele`.

## 7. Reprodução

```bash
python -m pytest tests/test_equilibrio_v21d.py -q                        # chaves desligadas = V21C; ~10 s
python experiments/calibrar_equilibrio.py --rodada 2 --etapa todas        # ~12 min com 8 processos
python experiments/calibrar_equilibrio.py --rodada 2 --etapa colaterais --variante a_c_e2v_v
python experiments/calibrar_equilibrio.py --rodada 2 --etapa colaterais --variante a_c
```

O erro padrão entre sementes não foi estimado: como no diagnóstico e na rodada 1, diferenças abaixo de ~0,01 não
devem ser lidas.
