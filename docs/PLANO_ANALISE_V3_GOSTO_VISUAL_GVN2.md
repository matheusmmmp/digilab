# PLANO DE ANÁLISE V3 — GOSTO_VISUAL, GVN-2: a leitura das vidas gravadas das duas GV3 (2026-11-12, Claude Code, Opus 5.5)

**Status: APROVADO pelo Matheus em 2026-11-12**, pela decisão da GVN-2 de `docs/futuro/gosto_visual_porque_negativo.md` (seção 4), que já
inclui este plano curto. A citação, repassada pela sessão coordenadora: "Eu concordo com todas as recomendações e daí pode efetuar o
merge das pendências finalizadas e daí seguir em frente com as recomendações." O registro é a seção "2026-11-12 — GOSTO_VISUAL: as GVN-1
a 6 DECIDIDAS e a GVN-2" de `docs/registro/2026-11.md` (D-GV-GVN-1 e 2).

**Este plano foi commitado e empurrado antes de qualquer `vidas.tar.gz` ser aberto.** O que ele sabe dos arquivos vem só do código que os
gravou (`experiments/run_v3_gosto_visual.py`, `_vida`; `experiments/sonda_duas_tvs.py`, `ler_replica` e `sonda`).

## 1. O que é e o que não é

- **Descritivo, não confirmatório.** Nenhuma vida nova, nenhuma faixa, nenhum código do repositório importado, nenhum parâmetro novo. As
  contas foram escolhidas depois de ver os dois resultados e não têm correção para comparações múltiplas. Um IC95 que não contém 0 não é
  "o efeito apareceu".
- **Os dois negativos ficam como estão.** As frases da GV3 (`docs/RESULTADO_V3_GOSTO_VISUAL.md`) e da GV3b
  (`docs/RESULTADO_V3_GOSTO_VISUAL_ENJOO.md`) não mudam, nem a regra da 7.2 do plano das duas. Nada daqui junta as 72 unidades numa conta
  só: cada número sai por run.
- **O que se lê:** só os dois `vidas.tar.gz`, `artifacts_v3_gosto_visual/gosto_visual/vidas.tar.gz` (GV3) e
  `artifacts_v3_gosto_visual/gosto_visual_enjoo2/vidas.tar.gz` (GV3b), e deles só os `*_sonda.json`. O `medidas.json` de cada run entra só
  para ligar a vida à unidade (base, k) e para conferir que as sondas lidas são as que a run mediu. A pasta `vidas/` já extraída (ignorada
  pelo git) não é lida.
- **O script:** `artifacts_v3_gosto_visual/gvn2/leitura.py <raiz>`, no padrão do `porque/descritivo.py`: grava `leitura.json` ao lado, com
  LF, e sai igual byte a byte a cada execução (o teste `tests/test_gosto_visual_gvn2.py` confere). Um processo só.

## 2. O que a sonda gravou (do código, antes de abrir)

Cada réplica que coube tem: `olhadas` (os trechos de ticks da janela de 240, cada um `[rótulo, n]`, com o rótulo `A`, `B` ou nulo),
`ticks`, `primeira`, `agrado` (o inato e o de agora de A e de B, no início da janela), `decisoes` (cada decisão da janela só com `acao` e
`olha`, o id da TV olhada, 2 = A e 3 = B, ou nulo), `posicao` e `dormiu`. Uma réplica sem lugar (só na GV3b) tem só `sem_lugar`.

**Os termos e os pesos das unidades não estão gravados.** O `motivos` do cérebro tem `unidades` com `termos`, `a` e `w`, mas a sonda copia
dele só `acao` e `olha`. A medida da H5 que a proposta escreve (a parte do peso da unidade de olhar no total e quanto o `gosto` a muda)
**não se lê nestes arquivos**. O script confere isso em cada decisão (as chaves têm de ser exatamente `acao` e `olha`) e falha alto se
não for.

## 3. As medidas, exatamente

Todas por run (GV3, GV3b) e por genoma (próprio, vazio); os três donos juntos, como na seção 3 da proposta (escolha desta leitura, não do
plano das runs). Uma réplica é **válida** quando olhou alguma TV (o `tempo_relativo` não é nulo). Os IC95 são percentis de 2000
reamostras de unidades (base, k) inteiras, com a semente 20261112 (a do `descritivo.py`); as reamostras indefinidas são contadas.

**C0, a conferência (falha alto se não bater):** o número de vidas e de réplicas de cada run é o do `medidas.json`; para cada réplica que
coube, `escolha`, `tempo_relativo`, `tempo_total` (recalculados de `ticks` e `primeira`, como `metrics.medidas_duas_tvs`),
`agrado_inato` (A − B) e `agrado_agora` (A − B) são iguais aos do `medidas.json`; os trechos de `olhadas` somam 240 e batem com `ticks`;
todo `olha` é nulo, 2 ou 3; toda decisão tem só `acao` e `olha`.

**M1, as saídas e as voltas por réplica (dos trechos de `olhadas`, por tick), nas réplicas válidas:**
- `episodios`: os trechos com rótulo A ou B;
- `saidas`: os trechos A ou B seguidos de um trecho nulo (o pet deixa de olhar as duas; o fim da janela não conta);
- `trocas_diretas`: um trecho A seguido de um B, ou B de A;
- `voltas`: os trechos A ou B precedidos de um trecho nulo que tem algum trecho A ou B antes, separados em `voltas_mesma` (à TV do último
  trecho olhado) e `voltas_outra`;
- de cada uma, a média e a mediana por réplica e as frações com 0, 1, 2 e 3 ou mais; a fração das réplicas com pelo menos uma volta;
- nas réplicas em que o pet viu as duas (0 < `tempo_relativo` < 1): quantas chegaram à segunda TV por uma troca direta e quantas por uma
  volta à outra (a primeira passagem para a TV ainda não vista).

**M2, ficar mais uma decisão (das `decisoes`; a previsão da H5 na seção 2 da proposta):** cada par de decisões seguidas (t, t + 1) da
janela com `olha` em t igual a A ou B. O `gosto` da decisão t + 1 é o da TV olhada em t (`adapt._gosto_da_decisao`).
- o desfecho de cada par: `fica` (`olha` em t + 1 é a mesma TV), `troca` (a outra) ou `sai` (nulo); as frações por TV (A, B) e juntas;
- nos pares `sai`, a contagem de cada `acao` da decisão t + 1;
- por pet: `p_fica_A` e `p_fica_B` (sobre os pares de cada TV, todas as réplicas da sonda juntas) e `dif_fica = p_fica_A − p_fica_B`, só
  nos pets com pelo menos um par de cada TV (os outros são contados);
- no próprio: Spearman(Δ_I, `dif_fica`), com o IC95; o mesmo só com os pares das réplicas em que o pet viu as duas;
- no vazio (Δ_I = 0): a média de `dif_fica`, com o IC95;
- para a H4: o número médio de pares por pet e por réplica válida.

**M3, o tamanho do termo `gosto` (calculado do agrado gravado, não lido do motivo):** com w_gosto = S = 1024
(`ConfigOlhar.w_gosto`), o termo da TV X é mul(S, agrado(X) − S/2, S) = agrado(X) − 512. Por réplica válida, `g_A`, `g_B` e
`d_g = g_A − g_B` (= o `agrado_agora` A − B). A média e os percentis 5, 50 e 95 de |`g_A`|, |`g_B`| e |`d_g`|, em S e em fração do teto da
ativação A_max = 4S (`ConfigDigibrainInatos.a_max`). **Ressalvas fixadas antes:** o agrado é o do início da janela; na GV3b o termo usa o
agrado efetivo (o agrado menos o tédio do enjoo, `sens.agrado_efetivo`), que a sonda não gravou, então lá o M3 é o termo sem o tédio (um
teto do termo, não o termo); e o termo só existe na TV olhada na decisão anterior.

**M4, a parte do peso da unidade de olhar (a medida da H5 como a proposta a escreve):** não mensurável nestes arquivos (seção 2). O JSON
leva `"M4": "nao_mensuravel"` com a razão.

## 4. As frases permitidas

Só estas, com os números e as chaves do `leitura.json`, por run:
1. "Por réplica válida, o pet teve em média <x> saídas e <y> voltas (<z> à mesma TV, <w> à outra) (`M1...`)."
2. "Nas réplicas em que viu as duas, a segunda TV veio por uma troca direta em <x> e por uma volta em <y> (`M1...`)."
3. "Depois de uma decisão olhando uma TV, a decisão seguinte ficou na mesma TV em <x> dos pares, trocou em <y> e saiu em <z>; nas saídas,
   as ações mais contadas foram <...> (`M2...`)."
4. "No próprio, Spearman(Δ_I, dif_fica) = <ρ> [<IC95>] (`M2...`); o IC95 contém 0 / não contém 0. Leitura descritiva."
5. "No vazio, a média de dif_fica é <x> [<IC95>] (`M2...`)."
6. "O termo `gosto` calculado do agrado gravado diferiu entre as duas TVs, em média, <x> S, contra o teto da ativação de 4 S (`M3...`)" —
   na GV3b, com "sem o tédio do enjoo, um teto do termo".
7. "A parte do peso da unidade de olhar não se lê nos `vidas.tar.gz`: a sonda não gravou os termos (`M4`)."
8. Sobre as hipóteses, só: "isto é / não é o que a H5 (ou a H4) prevê na seção 2 da proposta", sem dizer que ela vale ou não vale.

**Proibidas:** "o gosto é fraco" ou "forte"; "a H5 (ou a H4) vale", "foi confirmada" ou "foi refutada"; "o pet gosta", "prefere" ou
"enjoa"; "a parte do genoma (ou do dono) aparece"; qualquer frase que mude ou releia as frases da GV3 ou da GV3b; qualquer conta com as
duas runs juntas; comparações com animais; qualquer alegação de novidade.

## 5. A decisão aberta: GVN-2b

| id | a decisão | a recomendação | o custo de errar |
|---|---|---|---|
| **GVN-2b** | Medir a parte do peso da unidade de olhar (a H5 como escrita) refazendo as sondas pelo replay dos logs gravados, com o `motivos` inteiro de cada decisão da janela. Executa o motor sobre os logs das duas runs (sem semente nova nem vida nova), com um plano próprio. | **Só se o M2 deixar a H5 em aberto** e antes de mexer no `w_gosto` (GVN-6). O replay é determinístico (a regra do replay), mas é uma execução, não uma leitura: entra como etapa própria, com o seu plano. | Fazer sem necessidade custa o tempo de refazer as sondas das 432 vidas pelo replay (da ordem do custo das vidas, `custo.json` das duas runs). Não fazer, se o M2 não separa a H5, deixa o `w_gosto` sem medida. |

## 6. O que vai no resultado

Uma seção nova em `docs/futuro/gosto_visual_porque_negativo.md` ("A GVN-2: o que as vidas gravadas mostram"), com cada número citando a
chave do `leitura.json`, só as frases da seção 4 e o que isso diz das H5 e H4, e uma linha na `docs/TAREFA_V3_GOSTO_VISUAL.md`.
