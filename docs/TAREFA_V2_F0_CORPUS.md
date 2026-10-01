# TAREFA V2 — F0-CORPUS (2026-10-01)

Coordenador: chat "Principais jogos Digimon com diálogo" (coordenação da V2). Worker: a abrir. Worktree e branch: `v2-f0-corpus`.
Status: ABERTA.

## 1. Pergunta

Os itens do corpus de espécies que o filtro do alfabeto deixa fora do estilo podem voltar, reescritos em português, sem perder a fonte?
Fase 0, item 3 do `docs/PLANO_V2_PESQUISA.md` ("tradução dos itens em japonês do corpus").

## 2. Depende de

Nada além da `main`. Leitura: `CLAUDE.md` (fala livre e voz própria), `digilab_fala_livre/corpus.py` (filtro do alfabeto, `latino`, `carregar(..., so_latino=…)`).
Fontes do corpus (fora do repositório, só leitura): `D:\Trab\digilab\docs\corpus_digimon\*.md` e `auditoria\*.md`.

## 3. Mudança mínima

- `digilab_fala_livre/corpus_especies.json`: cada item de traço, jeito de falar ou interação cujo texto tem letra fora do alfabeto latino é **reescrito em
  português** (até 120 caracteres), descrevendo o jeito (por exemplo, "termina as frases com uma partícula infantil"), **sem** a palavra japonesa.
  Contagem de partida conferida pelo coordenador: 46 textos com kana/kanji (43 de fala, 2 de traços, 1 de interação); o worker confere pelo `latino()` do
  carregador e reporta o número exato.
- Cada item reescrito mantém `marca`, `fonte` e `jogo`, e ganha `"reescrito": true`. Nada novo é inventado: o texto só diz o que a fonte do item diz.
  Item que não tiver como ser dito sem o original sai do corpus, com a lista no PR.
- Testes: os de `tests/test_voz_fala_livre.py` e `tests/test_corpus*` passando; um teste novo de que `carregar(..., so_latino=False)` e `so_latino=True`
  dão o mesmo número de itens (nenhum fica de fora).
- **Não muda:** o filtro, o prompt, o verificador, o almanaque.

## 4. Experimento e gate

Sem run. **Sem GPU** nesta tarefa: a conferência com o gemma2:9b (a fala com o estilo, sem japonês e sem saída rejeitada) vira uma frente própria na fila
da GPU, depois deste PR.

## 5. Entrega

- Testes: `python -m pytest tests/ -q`.
- Registro: seção no fim do `CLAUDE.md` (fala livre) e do `docs/REGISTRO_DESVIOS.md` (critério da reescrita; itens removidos).
- PR contra a `main` com resumo e números. Aviso ao coordenador. Merge só pelo Matheus.

## 6. Fora desta tarefa

Rodar o modelo; mudar o estilo de outras espécies; ampliar o corpus.
