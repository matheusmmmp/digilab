# Dreyfus e o corpo situado: as referências conferidas (2026-11-16)

Rodada pedida pelo Matheus em 2026-11-16, depois da conversa sobre *What Computers Can't Do*. São 18 referências: a crítica de
Dreyfus, o contraponto publicado e as linhas teóricas que ela toca no Digilab (corpo, aterramento do símbolo, modelo de mundo,
conhecimento social). A tabela é a [`v3_dreyfus_referencias_verificadas.csv`](v3_dreyfus_referencias_verificadas.csv), o registro bruto
é o [`v3_dreyfus_verificacao_crossref.json`](v3_dreyfus_verificacao_crossref.json) e o `.bib` é o
[`v3_dreyfus_referencias.bib`](v3_dreyfus_referencias.bib).

## Método

- **Existência:** o DOI resolveu no `api.crossref.org/works` (status 200). Título, autores, ano, veículo, volume e páginas foram
  conferidos, e nenhum registro tem `update-to`. Os dois livros sem DOI (Dreyfus 1972 e Dreyfus e Dreyfus 1986) foram confirmados
  por uma resenha com DOI.
- **Conteúdo:** o resumo veio do OpenAlex (`abstract_inverted_index`), do Semantic Scholar ou do Crossref. Nenhum texto completo
  foi lido.
- **O status segue o vocabulário da skill `literatura-digilab`:** VERIFICADA só quando o título ou o resumo sustentam o que a coluna
  `o_que_sustenta` diz.
  - Quando só havia o TLDR gerado pelo Semantic Scholar, ele não contou como resumo: a linha ficou EXISTÊNCIA CONFIRMADA; CONTEÚDO
    NÃO LIDO, exceto onde o próprio título já sustenta a tese (Brooks 1991, Friston 2010).
  - Nesses dois casos, a coluna se limita ao título e diz que o resumo do autor não foi obtido.

## O que fica

| status | n | referências |
|---|---|---|
| VERIFICADA | 11 | McCarthy 1996, Brooks 1991, Varela et al. 1991, Pfeifer e Bongard 2006, Harnad 1990, Searle 1980, Damasio 1996, Friston 2010, Clark 2013, Lake et al. 2017, Collins 1990 |
| VERIFICADA (sem DOI) | 2 | Dreyfus 1972/1992 (pela resenha `10.2307/1575958`), Dreyfus e Dreyfus 1986 (pela resenha `10.1109/mex.1987.4307079`) |
| EXISTÊNCIA CONFIRMADA; CONTEÚDO NÃO LIDO | 5 | Dreyfus 2002, Dreyfus 2007, Haugeland 1996, Collins 1996, Koschmann 1996 |

A lacuna mais relevante é o **Dreyfus 2007**, o texto mais próximo do Digilab, que só tem o primeiro parágrafo lido. A leitura
corrente de que ele critica a IA "heideggeriana" de Brooks e Agre e propõe a neurodinâmica de Freeman **não foi conferida** e não pode
ser citada como conteúdo até alguém ler o artigo.

## O que as verificadas autorizam dizer (e o que não)

- **A crítica existe e tem tese própria.** Dreyfus (1972; 2ª ed. 1992) sustenta que as máquinas sem corpo não imitam as funções mentais
  superiores, e a 2ª edição estende a avaliação ao conexionismo. As quatro suposições e o argumento da relevância são do texto, que não
  foi lido nesta rodada.
- **Há contraponto publicado.** McCarthy (1996) responde no mesmo número da *Artificial Intelligence*.
- **O corpo molda o comportamento.** Pfeifer e Bongard (2006) e Varela et al. (1991) sustentam o enquadramento, e Damasio (1996) o
  peso do estado do corpo na decisão. Nada disso valida o corpo químico do Digilab: são enquadramento, não evidência sobre o pet.
- **A fala precisa de chão.** Harnad (1990) sustenta o enquadramento da fala pelo decodificador de conceitos, e Searle (1980) o limite
  do que se diz da fala por LLM. Nunca escrever que o pet entende, nem que o decodificador resolve o aterramento.
- **O pet que planeja.** Clark (2013), Friston (2010) e Lake et al. (2017) dão o vocabulário do modelo de mundo, e Brooks (1991) o
  da posição contrária, sem representação central.
- **O conhecimento é social.** Collins (1990) enquadra o que o pet aprende com o dono. A pergunta do efeito do dono continua
  encerrada (`docs/LEITURA_CONSOLIDADA_DONO.md`).

**Nenhuma dessas fontes sustenta afirmação de novidade.** Valem as regras da skill: a regra 3 ("ensinado, não roteirizado" não é
diferencial) e a regra 9 (corpo com homeostase, aprendizado em vida e memória num agente já foi publicado).

## Limites

- Os resumos foram lidos, os textos completos não.
- O regex de DOI do `tools/verificar_relato.py` para no `(`. Os DOIs da Elsevier dos anos 1990, como `10.1016/0004-3702(91)90053-M`,
  entram cortados no `10.1016/0004-3702(91`. E já colide: as três resenhas de 1996 (McCarthy, Haugeland, Koschmann) viram
  `10.1016/0004-3702(95`, e o verificador trata o McCarthy, VERIFICADA aqui, como não citável. Até o regex mudar, cite o McCarthy num
  relato de PR sem o DOI (D-LIT-DR-4).
