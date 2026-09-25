# Redesenho dos bots adultos da V2.1 (G6b e G8) e E4 — tentativa NÃO adotada

Sementes de calibração (3101…3505), regras V21C (base V2C, vida por vigor 2,5, marca frágil).
Scripts e saídas brutas nesta pasta (os `.py` são os que geraram os `.log`).

- `g6b_*.log`, `g6b2_*.log`, `g6b3_*.log`: regras de virada genéricas ("abaixo de X% de vida e o oponente
  repete a jogada Y → Z") no topo de cada bot. Os 8 arquétipos passam no espelho do G6b (≤ 0,65).
- `full21.py` (saída no relatório da sessão): com essas regras nos 8 bots, o E1 cai (suporte 5 → 3:
  duelista, emboscador, espelho), a Brasa passa a dominar (E2) e o E4 quebra ao contrário (sentinela e
  emboscador adultos 0,0 contra o adolescente): a regra dispara contra qualquer oponente, não só no espelho.
- `tecnica_b*.log` (`busca21.py`): regras de virada disparadas pela técnica da própria linha (só um
  oponente da mesma linha a usa). Não quebram o resto, mas só sentinela, emboscador e titã passam no G6b;
  duelista, furioso, muralha e vigia não têm candidato que passe (16 por arquétipo).
- `e4.py`: adolescente com 7 ou 8 regras (as regras do adulto que ele pode usar) não muda o E4: quase
  todas as regras do adulto usam condições que o adolescente não tem.

Nada disto foi adotado; a V21C segue com os bots da V2.1.
