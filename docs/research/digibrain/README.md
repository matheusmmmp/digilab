# DigiBrain: estrutura de estudo

> **Nota (2026-10-24), a direção nova:** o Matheus decidiu, no PROMPT MESTRE, que o produto jogável vem primeiro, que o DigiBrain
> caminha para um cérebro **modular**, e que o cérebro A fica como linha de base, controle e fallback condicionado, e não como o cérebro
> final da web. As decisões "a web roda um DigiBrain, o A" (2026-10-01) e o M6 (rodada 15) estão **SUPERADAS** desde 2026-10-24; o
> texto abaixo fica como estava, como registro. Ver `docs/ARQUITETURA_DIGIBRAIN_MODULAR.md` e `docs/AUDITORIA_V2_PRODUTO_MODULAR.md`.
>
> Correções de citação achadas na auditoria de 2026-10-24 (`docs/ARQUITETURA_DIGIBRAIN_MODULAR.md`, seção 10): o aprendizado
> hebbiano é do resumo de Cliff e Grand (1999), não do de 1997; Adams (2021) e Castro e Gudwin (2013) são usados aqui além do que a
> tabela verificada sustenta. Os arquivos de mecanismo não foram reescritos.

Status: **estudo, não desenho** (2026-10-01). Esta pasta organiza a pesquisa que alimenta o cérebro do pet da V2 (o
"DigiBrain"). Ela **não escolhe arquitetura**, não autoriza mecânica e não muda nada do motor. O desenho é do Matheus; a
ordem de implementação está em `docs/ARQUITETURA_V2_VALIDACAO.md` e `docs/ROADMAP_V2.md`.

Origem: o corpus DigiBrain (`D:\Trab\digilab\docs\digibrain\`, fora do git, consolidado em 2026-10-01), a auditoria dele
contra o repositório (`docs\digibrain\integration\01..08`, também fora do git), as buscas verificadas da V2
(`docs/referencias/V2_SINTESE_Q1_Q7.md`) e das frutas (`V3_SINTESE_FRUTAS_VICIO_V1_V6.md`, ainda só na pasta `v1`) e as
propostas do Matheus de 2026-10-01. Trazer para cá fecha a lacuna B13 da auditoria (o corpus não era versionado).

## A pergunta que organiza tudo

> **Em que condições a plasticidade durante a vida produz vantagem adaptativa sobre as predisposições herdadas?**

Fontes de plasticidade: só consequências · ensino contextual · feedback explícito. Desenho experimental em
`docs/ARQUITETURA_V2_VALIDACAO.md`, seção 6. É a pergunta clássica do efeito Baldwin (Hinton e Nowlan 1987; Fernando et
al. 2018), **não é nova**; o que pode ser contribuição é separar a plasticidade por fonte, com o cuidado controlado.

## Três níveis, três fontes principais

| nível | fontes | o que cada uma pode dar |
|---|---|---|
| biologia e organismo | *Drosophila* (FlyWire e corpo de cogumelo) + Creatures | fisiologia, drives, genoma como substrato, circuitos especializados |
| aprendizagem | *Drosophila* + Creatures × NORNBRAIN | plasticidade local com reforço modulado × gradiente com ator-crítico |
| memória autobiográfica de alto nível | Dwarf Fortress (+ Castro e Gudwin, Sakabe et al.) | história acumulada legível ao jogador; episódio que muda decisão |

## Mapa da pasta

| pasta | conteúdo |
|---|---|
| `sources/` | uma nota por família de fonte: o que ela mostra, o que **não** mostra, como citar |
| `mechanisms/` | um arquivo por mecanismo: o que existe no repositório hoje, o que a literatura sustenta, as hipóteses DigiLab, os confundidores |
| `synthesis/` | cruzamento fonte × mecanismo, registro de hipóteses, perguntas abertas, e o desenho da comparação entre DigiBrains (`brain_comparison.md`) |
| `references/` | índice de fontes com status e BibTeX |

## Rótulos (obrigatórios em todo arquivo)

**Evidência** (vocabulário da `literatura-digilab`, `docs/referencias/REGRAS_CITACAO_DIGILAB.md`):
- **VERIFICADA**: está na tabela verificada do projeto (DOI conferido, resumo sustenta a afirmação).
- **CORPUS**: URL/DOI conferido pelo corpus DigiBrain em 2026-10-01, mas **fora** da tabela verificada do projeto. É pista:
  não entra em texto de resultado até ser verificada (`references/source_index.md`).
- **NÃO VERIFICADA EM FONTE PRIMÁRIA**: só wiki ou fonte de fã. Nunca evidência.
- **NÃO LOCALIZADA**: não citar.

**Afirmação:** `FONTE` (o que a fonte diz), `INTERPRETAÇÃO` (leitura nossa), `HIPÓTESE DIGILAB` (pergunta a testar,
nunca achado), `REPOSITÓRIO` (o que o código e os artefatos mostram hoje, com caminho).

**Estado do projeto:** EXECUTADO / ESPECIFICADO / IDEIA; DECIDIDO / PROPOSTO.

## Regras desta pasta

1. **Literatura não autoriza mecânica.** Nenhuma linha daqui vira código sem tarefa, plano de análise commitado antes e
   decisão do Matheus.
2. **Nada de arquitetura Frankenstein.** Para cada mecanismo: que pergunta responde, se já existe equivalente, se dá para
   isolar, que confundidor traz, quanto custa, de que experimento depende. Uma peça nova por versão de pet.
3. **Canal artificial não é neurotransmissor.** Os nomes de canais de reforço são abstrações do DigiLab; não
   correspondem a dopamina, serotonina ou qualquer molécula.
4. **Vocabulário operacional.** Nada no motor, no log ou na fala afirma que o pet sente prazer, medo ou dor: são
   variáveis com nome.
5. **Não reabrir a v1.** A hipótese central foi refutada e a pergunta do efeito do dono está encerrada
   (`docs/LEITURA_CONSOLIDADA_DONO.md`). Analogia com ALGA, Berridge ou dopamina não reabre nada.
6. **Não alegar novidade bloqueada:** instinto × aprendido (Hallawa et al.), herdar o prior (Baldwin) e "ensinado pelo
   dono" (Black & White).
7. **Pesquisa em Python, produto na web** (decisão do Matheus, 2026-10-01). As comparações entre cérebros e todos os
   experimentos rodam no Python, com replay bit a bit no mesmo runtime. A web roda **um** DigiBrain só, o escolhido para o
   produto, e só ele precisa de porte e paridade Python/web. Um cérebro de pesquisa não precisa caber na web.
