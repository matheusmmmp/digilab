# Mutação como abertura de possibilidades (nota de pesquisa)

Status (2026-10-16): **HIPÓTESE CONCEITUAL**, pedido do Matheus. Não é mecânica implementada, não autoriza implementação e não é
afirmação literal do Harari. Liga-se ao desenho do genoma em `docs/futuro/ecossistema_genetico.md` (seção 4.1, mistura e mutação) e ao
paladar em `docs/futuro/paladar.md`.

**Regras desta nota:**
- O Harari é **moldura**, não evidência (ver `docs/research/digibrain/sources/harari.md`). Livro de divulgação, sem revisão por pares.
- As duas referências técnicas da seção 4 foram conferidas no Crossref em 2026-10-16 (metadados; conteúdo não lido).
- **Nenhuma alegação de novidade.** Construção de nicho e evolução aberta são linhas antigas; o Digilab só as usa como pergunta.

## 1. A inspiração

Harari, *Nexus* (2024), capítulo 1, "O que é informação?". O exemplo é uma zebra com uma mutação que inibe a produção de adrenalina:
ela foge pior dos predadores e tende a sobreviver menos. O ponto do autor é que o DNA não se avalia como representação verdadeira ou
falsa da realidade, e que os erros de cópia nem sempre reduzem a aptidão: às vezes a aumentam, e sem eles não haveria evolução.

Citação, **a conferir no livro (página e redação da edição brasileira)**:

> "Todas as formas de vida existem graças a 'erros' genéticos." — Harari, *Nexus* (2024), cap. 1.

A redação veio de um resumo externo, não do texto. Antes de usar entre aspas em qualquer texto público, conferir no livro.

## 2. A ideia para o Digilab

A mutação não precisa ser tratada como defeito a corrigir. O valor adaptativo de uma mutação depende do contexto, e não de ela ser um
desvio do genoma de origem.

- **Exemplo da agressividade:** uma mutação que sobe a agressividade pode favorecer o pet num ambiente competitivo e prejudicá-lo num
  ambiente que depende de cooperação (ligação: `docs/futuro/dois_pets.md`, `docs/futuro/cognicao_social.md`).
- **Exemplo da fruta:** um pet que, por mutação, deixa de comer uma fruta não é necessariamente deficiente. A mudança pode ser uma
  desvantagem imediata, um traço neutro ou o começo de uma trajetória diferente: rejeitar a fruta pode levar o pet a explorar outras
  fontes, formar outras preferências e se relacionar de outro jeito com o mundo e com os outros pets. No genoma proposto, isso cairia
  nas seções `paladar` (`h_q`) e `frutas` (preferência inata), hoje sem herança (PL-2 e F5 em aberto).

## 3. A hipótese

> A variabilidade genética pode não só mudar o quanto o pet se adapta a um ambiente dado, mas também mudar a interação dele com o
> ambiente, criando novas pressões seletivas, nichos e trajetórias.

O interesse experimental não é só se uma mutação é boa ou ruim, mas **o que aparece** da interação entre genoma, fisiologia,
aprendizado, comportamento e ambiente.

**Duas distinções obrigatórias:**
1. A mutação não precisa ser adaptativa quando surge. O efeito pode depender do ambiente e das gerações seguintes.
2. A abertura de um nicho novo não se atribui à mutação isolada, e sim à interação entre o organismo e o ambiente. Um teste precisa
   ter o braço de controle em que o ambiente não responde ao pet.

## 4. Linhas teóricas para investigar

| linha | referência conferida | o que ela autoriza |
|---|---|---|
| construção de nicho | Laland, Odling-Smee e Feldman (2000), *Behavioral and Brain Sciences*, `10.1017/S0140525X00002417` | o vocabulário: organismos mudam o ambiente e, com isso, as pressões de seleção sobre si e sobre os outros |
| evolução aberta | Taylor et al. (2016), *Artificial Life*, `10.1162/artl_a_00210` | o estado da pergunta em ALife: o que conta como novidade contínua e como medi-la |

Para mutação e réplica em evolução digital, as referências já usadas em `ecossistema_genetico.md` valem (Ray 1993; Ofria e Wilke 2004;
Lenski et al. 2003). Para o caso inesperado sair como relato honesto, Lehman et al. (2020), `10.1162/artl_a_00319`.

## 5. O que fica em aberto

- Se e quando isso vira experimento depende do genoma da V2 (EG-1 a EG-8) e da herança do paladar (PL-2). Não há decisão.
- Uma medida candidata, se virar experimento: por linhagem, a dispersão das preferências e do uso do mundo ao longo das gerações,
  com e sem mutação, e com e sem um ambiente que responda ao pet. SEM FONTE; só pista.
