# Reequilíbrio dos arquétipos do combate V21C — rodada 1 (candidatos A e C)

Status: **rodada de calibração** (2026-09-29). Parte de `docs/DIAGNOSTICO_ARQUETIPOS.md` (candidatos A e C e o gate
proposto da seção 7). Nada foi adotado: as duas mudanças estão atrás de chaves **desligadas por padrão**, e a web não
mudou. A validação (sementes 4101…4505) não foi tocada; ela fica para quando o Matheus escolher a versão.

- **Script:** `python experiments/calibrar_equilibrio.py --etapa todas` (matriz, painel, gate; ~3 min com 8 processos)
  e `--etapa colaterais --variante a_c` (e `--variante a`; ~40 s cada).
- **Artefatos:** `artifacts_combate_v21c/equilibrio_rodada1/` (`matriz.json`, `painel.json`, `gate.json`,
  `colaterais_a_c.json`, `colaterais_a.json`). Todo número abaixo vem deles.
- **Regras:** as da validação V21C (`experiments/configs/v21c/validacao.json`) mais as chaves da variante.
- **Sementes:** só as de calibração (3101…3505), 100 partidas por par por semente e espécie (2.000 por par), os mesmos
  nomes e sementes do diagnóstico.

## Resultado em quatro frases

1. **Nenhuma variante passa o gate proposto.** A melhor, A + C, põe 4 das 8 formas na faixa [0,40; 0,60] e reduz
   os pares extremos de 17 para 11. Mas o furioso (0,726) e os caçadores (0,649 e 0,623) continuam fora, e o suporte
   cai de 5 para 3.
2. **A funciona no confronto que mira** (colosso × guardião) e resgata o titã (0,173 → 0,466). Só que inverte o
   confronto: o titã passa a fazer 0,87 contra o espelho e 0,91 contra a muralha. E o vigia passa a perder do titã
   (0,96 → 0,13).
3. **C sozinho piora tudo** (amplitude 0,582 → 0,677; titã 0,087, sem nenhuma vitória). Junto com A, devolve a muralha
   a 0,402 e fecha parte dos extremos.
4. **Os efeitos colaterais protegidos não quebram** com A + C nem com A: o S1 passa, o E4 na escala passa (menor 0,836)
   e a campanha fica como estava (4 de 5 NPCs nas metas; a Sentinela continua a exceção, e até melhora).

## 1. O que mudou (atrás da chave)

`ConfigCombateV21D` (`digilab/config.py`) é uma subclasse da `ConfigCombateV21C` com duas chaves, as duas `False` por
padrão. Ela é uma classe própria, e não ganhou campos novos na V21C, para que o `asdict` e o `config_sha256` das
configs V21C gravadas não mudem. `run_bateria_v21.regras_de` só monta a V21D quando o config pede uma chave dela.

- **A — `preparo_sob_pele_oculto`.** `oponente_preparando` fica falso quando o preparo do pesado foi feito com a
  pele dura ativa: a pele passa a esconder o pesado, além de protegê-lo. O estado do lutador ganhou
  `preparo_sob_pele`, calculado em `regras.resolver` com a pele ativa no turno do preparo. Com a duração da pele de
  hoje (2 turnos), isso equivale à condição da prévia do diagnóstico (a ação anterior ao preparo foi `pele_dura`).
  A regra também vale para o colosso partido, que tem outra duração de pele. `Condicao.vale` recebe as `Regras`
  (parâmetro com padrão; as chamadas sem ele continuam iguais). Seguindo o diagnóstico, só `oponente_preparando`
  muda. O diagnóstico não mostrou outra leitura do preparo nas decisões. A condição do vigia
  (`oponente_vai_preparar`) lê a intenção antes do preparo e **não** mudou.
- **C — `muralha_lista_espelho`.** A muralha luta com `bots.GAMBITS_MURALHA_V21D`, que é a lista do espelho, como a
  alavanca (d) do diagnóstico. As regras de contra-golpe fora de perto ficam na lista, mas nunca disparam na
  muralha: sem a passiva do espelho, o contra-golpe só é legal de perto, e a lista cai na regra seguinte. A escolha
  fica em `bots.gambits_adulto(forma, cfg)`, usada por `lutador_adulto` e pelo E3 da bateria. `ADULTOS` (as listas
  canônicas) e `SOMBRIOS` não mudam.

**Reprodução com a chave desligada** (testes em `tests/test_equilibrio_v21d.py`; conferências que falham alto no
script):
- config V21C: mesmo `config_sha256` da validação gravada;
- V21D com as duas chaves em `False`: joga as mesmas partidas (log igual) que a V21C;
- matriz da brasa: igual aos pontos por espécie de `diagnostico_arquetipos/mecanismo.json`;
- matriz v21c: idêntica a `reproducao.json` (ε 0,05) e a `epsilon.json` (ε 0,15);
- A e A + C: idênticas a `candidatos.json` (`cand_a`, `cand_a_c`);
- C: a linha da muralha é idêntica à alavanca (d) de `atribuicao.json`;
- painel da v21c: idêntico a `painel.json`;
- campanha da v21c: igual a `experiments/configs/escala/calibracao.json`.

Os 116 testes do combate, da campanha, do treino/sombrias e da escala passam; a suíte inteira passa (seção 6).

**Não lê a chave nesta rodada:** os pets de pesquisa (`evolucao`, `run_educacao`, `run_treino`, `run_campanha`) montam a
lista por `ADULTOS[...]` e lutam com `campanha.REGRAS_CAMPANHA` (V21C). Como a chave está desligada, as runs V3, E1
e a confirmatória não mudam. Ligar a versão adotada nelas é trabalho da decisão, junto com a web.

## 2. Força por forma (`matriz.json`, `painel.json`)

Força = média dos pontos contra as outras 7 (mesma espécie dos dois lados, média das 4 espécies). Painel = pet
canônico (ε 0,05) contra os 32 bots do painel B, com as regras e as listas da variante dos dois lados.

| forma | V21C | A | C | A + C | painel V21C | painel A | painel C | painel A + C |
|---|---|---|---|---|---|---|---|---|
| furioso | 0,755 | 0,718 | 0,763 | 0,726 | 0,702 | 0,659 | 0,713 | 0,670 |
| sentinela | 0,648 | 0,647 | 0,650 | 0,649 | 0,615 | 0,614 | 0,618 | 0,618 |
| espelho | 0,640 | 0,445 | 0,602 | 0,406 | 0,608 | 0,447 | 0,573 | 0,412 |
| emboscador | 0,615 | 0,614 | 0,624 | 0,623 | 0,612 | 0,611 | 0,622 | 0,622 |
| duelista | 0,521 | 0,471 | 0,517 | 0,467 | 0,532 | 0,484 | 0,528 | 0,481 |
| muralha | 0,400 | 0,313 | 0,597 | 0,402 | 0,406 | 0,325 | 0,571 | 0,413 |
| vigia | 0,248 | 0,327 | 0,161 | 0,265 | 0,287 | 0,353 | 0,212 | 0,288 |
| titã | 0,173 | 0,466 | 0,087 | 0,463 | 0,235 | 0,502 | 0,157 | 0,492 |

| resumo (ε 0,05 / ε 0,15) | V21C | A | C | A + C |
|---|---|---|---|---|
| formas em [0,40; 0,60] (contra as 7) | 1* | 3 | 2 | 4 |
| formas em [0,40; 0,60] (painel) | 2 | 3 | 3 | 4 |
| suporte do equilíbrio | 5 | 4 | 3 | 3 |
| pares fora de [0,1; 0,9] (de 28) | 17 / 12 | 14 / 11 | 18 / 14 | 11 / 9 |
| amplitude (mais forte − mais fraca) | 0,582 / 0,587 | 0,405 / 0,507 | 0,677 / 0,671 | 0,461 / 0,434 |
| menor nº de vitórias entre as outras 7 | titã 1 | 2 (muralha, vigia) | titã 0 | vigia 1 |
| distância até a faixa, soma (forças / painel) | 0,637 / 0,415 | 0,339 / 0,206 | 0,791 / 0,586 | 0,333 / 0,222 |

\* A muralha fica em 0,39989: arredondada é 0,400, mas está fora da faixa por 0,0001. O diagnóstico contou 2.

Distância até a faixa = soma, entre as 8 formas, do que falta para cada uma entrar em [0,40; 0,60].

Suporte: V21C {furioso, emboscador, espelho, muralha, sentinela}; A {furioso, emboscador, espelho, muralha} (a
sentinela fica com 0,046); C e A + C {furioso, muralha, sentinela}.

Confrontos que mudam (ε 0,05, pontos da linha contra a coluna):

| confronto | V21C | A | C | A + C |
|---|---|---|---|---|
| titã × espelho | 0,04 | 0,87 | 0,04 | 0,87 |
| titã × muralha | 0,61 | 0,91 | 0,01 | 0,89 |
| vigia × espelho | 0,01 | 0,54 | 0,01 | 0,54 |
| vigia × muralha | 0,61 | 0,92 | 0,00 | 0,49 |
| vigia × titã | 0,96 | 0,13 | 0,96 | 0,13 |
| vigia × duelista | 0,09 | 0,40 | 0,09 | 0,40 |
| vigia × furioso | 0,01 | 0,22 | 0,01 | 0,22 |
| titã × furioso | 0,01 | 0,06 | 0,01 | 0,06 |
| titã × sentinela / × emboscador | 0,02 / 0,01 | 0,02 / 0,01 | 0,02 / 0,01 | 0,02 / 0,01 |
| muralha × espelho | 0,28 | 0,28 | 0,55 | 0,55 |
| furioso × muralha | 0,06 | 0,06 | 0,12 | 0,12 |

Leitura:
- **A** tira dos guardiões a leitura do pesado, e com isso o colosso passa a vencê-los com folga. O confronto troca de
  lado em vez de se equilibrar. O vigia perde a vitória contra o titã: a passiva dele ainda vê a
  intenção, mas o golpe não interrompe preparo sob pele.
- **Nem A nem C tocam** o colosso × caçador (0,01–0,02) nem o furioso × caçador. O furioso cai só 0,03–0,04.
- **C sozinho** transforma a muralha num segundo espelho (vence 5 das outras 7) e esmaga os colossos (titã × muralha
  0,61 → 0,01). Com A, a muralha volta a 0,402 e o vigia × muralha fica em 0,49.

## 3. Gate proposto, item a item (`gate.json`; calibração, não validação)

| gate | critério | V21C | A | C | A + C |
|---|---|---|---|---|---|
| A1 força entre formas | 8 em [0,40; 0,60] | 1 de 8 | 3 de 8 | 2 de 8 | 4 de 8 |
| A2 força contra o painel | 8 em [0,40; 0,60] | 2 de 8 | 3 de 8 | 3 de 8 | 4 de 8 |
| A3 suporte | ≥ 6 | 5 | 4 | 3 | 3 |
| A4 decisividade | ≤ 7 extremos com ε 0,05 e ≤ 4 com ε 0,15 | 17 e 12 | 14 e 11 | 18 e 14 | 11 e 9 |
| A5 amplitude | ≤ 0,20 com ε 0,05 e 0,15 | 0,582 e 0,587 | 0,405 e 0,507 | 0,677 e 0,671 | 0,461 e 0,434 |
| A6 lugar no ciclo | toda forma vence ≥ 2 das 7 | titã 1 | **passa** | titã 0, vigia 1 | vigia 1 |

**Melhor variante: A + C.** Ela tem mais formas na faixa (4 e 4), menos pares extremos (11 e 9), a menor amplitude
com ε 0,15 e a menor distância até a faixa nas forças (0,333, contra 0,339 de A). **A** vem logo atrás e é a única que
passa um item (A6). Ela tem a menor amplitude com ε 0,05 (0,405), o suporte maior (4) e a menor distância no painel
(0,206). A escolha entre as duas é praticamente um empate: os efeitos colaterais foram medidos para as duas.

O que falta em A + C, forma por forma:
- **acima da faixa:** furioso (0,726), sentinela (0,649) e emboscador (0,623);
- **abaixo da faixa:** vigia (0,265);
- **equilíbrio:** o suporte encolhe para {furioso, muralha, sentinela}.

Os três fortes são justamente os confrontos que A e C não tocam: furioso × caçadores e colossos, caçadores ×
colossos.

Distância percorrida desde a V21C (A + C):
- soma do que falta para a faixa: 0,637 → 0,333 nas forças e 0,415 → 0,222 no painel;
- amplitude: 0,582 → 0,461 (ε 0,05) e 0,587 → 0,434 (ε 0,15);
- pares extremos: 17 → 11 (ε 0,05) e 12 → 9 (ε 0,15);
- A6: continua falhando, mas agora pelo vigia (1 vitória) em vez do titã.

## 4. Efeitos colaterais (`colaterais_a_c.json`, `colaterais_a.json`)

Nas mesmas sementes de calibração, cada variante comparada com a V21C medida no mesmo script.

| verificação | V21C | A + C | A |
|---|---|---|---|
| **S1** (nenhuma sombria vence as 8 normais) | passa | **passa** | **passa** |
| devastador contra as normais (média; vitórias) | 0,389; 3 | 0,368; 3 | 0,389; 3 |
| colosso partido | 0,154; 1 (muralha) | 0,265; 2 (espelho, muralha) | 0,306; 2 (espelho, muralha) |
| predador | 0,329; 2 | 0,336; 2 | 0,329; 2 |
| bastião rachado | 0,118; 0 | 0,146; 0 | 0,118; 0 |
| **E4 na escala** (adulto sem treino ≥ 0,60 contra o Champion sem treino e com +22) | passa, menor 0,836 | **passa**, menor 0,836 | **passa**, menor 0,836 |
| muralha × adolescente (sem treino / +22) | 1,000 / 1,000 | 0,857 / 0,854 | 1,000 / 1,000 |
| **campanha na escala** (≤ 0,30 sem treino e ≥ 0,80 com o típico) | 4 de 5 (Sentinela fora) | **4 de 5** (Sentinela fora) | **4 de 5** (Sentinela fora) |
| Brutamontes (sem / com) | 0,220 / 0,980 | 0,220 / 0,980 | 0,220 / 0,980 |
| Carcereiro | 0,254 / 0,848 | 0,254 / 0,848 | 0,254 / 0,848 |
| Porteiro | 0,180 / 0,884 | 0,180 / 0,884 | 0,180 / 0,884 |
| Sentinela (exceção aceita) | 0,386 / 0,705, travado: colosso | 0,389 / 0,758, travado: colosso | 0,389 / 0,758, travado: colosso |
| Soberano | 0,153 / 0,911 | 0,187 / 0,911 | 0,153 / 0,911 |

Nenhuma das três verificações quebra. O que se move:
- **Colosso partido:** passa a vencer também o espelho, e a média dele sobe (0,154 → 0,265 com A + C e 0,306 com
  A). Continua longe de vencer as 8.
- **Adolescente colosso contra a Sentinela:** com +22 sobe de 0,1225 para 0,3325 (A esconde o preparo dele do NPC).
  Continua travado.
- **Soberano:** a muralha adulta sem treino vence o Soberano em 0,3675 (era 0,1025) com a lista do espelho. A média
  segue abaixo de 0,30.
- **E4:** a muralha deixa de esmagar o adolescente (1,00 → 0,86), sempre acima de 0,60.

A Brutamontes, o Carcereiro e o Porteiro saem iguais nas quatro casas gravadas.

**Não medidos aqui:**
- E3 da pele dura (a resposta "ficar longe" não lê o preparo, então deve continuar funcionando, mas não foi rodado);
- E2, G6b, G8 e G9;
- o painel e as runs de pesquisa com pets reais;
- a paridade web.

Tudo isso entra na validação da versão escolhida.

## 5. O que a rodada 2 precisa atacar

Os três fortes que sobram (furioso, sentinela, emboscador) vivem de dois mecanismos que A e C não tocam.

**Furioso pela base (candidato D).** O mecanismo, pelo diagnóstico:
- ele esmaga os caçadores com a investida na distância média, porque, com a C3, o recuo não afasta de quem avança;
- ele esmaga os colossos com o golpe rápido barato, que interrompe o preparo.

Com A + C ele ainda faz 0,726.
- **D1 — parry maior:** `dano_parry` 5 → 8 na `ConfigCombateV2C` (numa `ConfigCombateV2D` com chave). É o único
  freio medido: 15,9 de parry por partida da muralha contra ele. Vale para toda a base, então pede G1–G9 de novo.
- **D2 — recuo esquiva a investida:** a investida erra quando o alvo recua a partir da distância média, como o pesado
  erra por distância. É uma exceção à C3 só para a investida. Mira o furioso × caçadores (investida de 63,1 e 51,1 de
  dano por partida na sentinela e no emboscador), sem tocar no avanço comum.

**Caçadores que fogem do pesado.** O titã e o vigia fazem 0,01–0,02 contra os caçadores com qualquer variante:
- o titã executa ~5 pesados por partida, e ~96% erram por distância;
- o caçador recua em 41–48% das ações, marca e atira.

(Números de `diagnostico_arquetipos/mecanismo.json`, pares titã × sentinela e titã × emboscador; nesta rodada os
confrontos não mudaram.)
- **E1 — o preparo prende:** enquanto o oponente prepara o pesado, recuar não afasta, uma extensão da fuga
  condicionada (C3) ao preparo. É mudança de regra, atrás de chave. Precisa conferir a sentinela, cuja passiva hoje
  faz o recuo valer contra o avanço, e se ela fica com uma exceção.
- **E2 — o colosso não prepara contra quem foge:** só nas listas, como C. Pôr
  `se(perto, oponente_frequente(recuar)) → golpe_rapido` antes do preparar no titã e no vigia. O golpe rápido acerta
  de perto na hora, sem dar os dois turnos de aviso.

**Também por resolver:** A inverte o vigia × titã (0,96 → 0,13), e o vigia termina com 1 vitória em A + C. A
rodada 2 precisa dar ao vigia uma resposta ao preparo sob pele, por exemplo recuar contra o preparo que ele não
consegue interromper (lista). Senão a A6 segue falhando.

## 6. Reprodução

```bash
python -m pytest tests/test_equilibrio_v21d.py -q            # chave desligada = V21C; ~10 s
python experiments/calibrar_equilibrio.py --etapa todas      # matriz, painel, gate; ~3 min com 8 processos
python experiments/calibrar_equilibrio.py --etapa colaterais --variante a_c
python experiments/calibrar_equilibrio.py --etapa colaterais --variante a
```

Suíte inteira (`python -m pytest tests/ -q`, com as chaves desligadas): 421 passaram e 1 foi pulado, em 4 min 24 s. O erro padrão entre sementes não foi estimado: como no
diagnóstico, diferenças abaixo de ~0,01 não devem ser lidas.
