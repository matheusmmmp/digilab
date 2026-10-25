# TAREFA V2 — DIGIBRAIN-MODULAR-LITERATURA: as fontes do substrato neural (a PE-1) (2026-10-25)

Coordenador: o Gerente. Worker: o C (Claude Code, Opus 5.5). Worktree e branch: `v2-modular-literatura`, de `origin/main` (`79ce52e`,
depois do merge do #406 e do #407). Categoria: `literatura`. **Só papel: nenhum código, nenhuma run, nenhuma semente, nenhum plano de
análise.** Roda em paralelo à etapa 0 do protótipo (com o D); as duas não dependem uma da outra.

Este arquivo registra o despacho, que chegou por mensagem entre sessões (relato do Gerente), e a entrega.

**Status:** CONCLUÍDA. A busca entrou na `main` pelo #408 (`34a5263`). As decisões D-0, D-1 e D-2 foram DECIDIDAS pelo Matheus em
2026-10-25 (seção 5). As trocas foram aplicadas na espec pela tarefa documental da D-0 (branch `v2-modular-espec-fontes`).

## 1. A pergunta

A PE-1 de `docs/ESPEC_DIGIBRAIN_MODULAR.md` (seção 15) foi decidida pelo Matheus em 2026-10-25: os SEM FONTE da seção 2 trocam por
fontes ou por "não localizada" antes da primeira vida do protótipo.

As escolhas SEM FONTE das seções 2 e 14 da espec têm fonte verificada? Em especial:
- **(a)** os integradores com vazamento em ponto fixo e as unidades de taxa como substrato de criaturas artificiais;
- **(b)** as redes recorrentes de tempo contínuo (CTRNN, CfC e NCP), só como estudo. A DM-9 pede conferir e registrar as licenças antes
  de qualquer reúso;
- **(c)** as regras hebbianas de três fatores com modulação neuroquímica;
- **(d)** o crédito por opção contra o crédito por janela;
- **(e)** a memória episódica por lugar informando a escolha.

## 2. As regras

- **Só referência verificada** (a skill `literatura-digilab`; os metadados e o resumo, nunca o texto completo).
- **Cada item** vira FONTE VERIFICADA (com o DOI, o que ela sustenta de fato e o que NÃO sustenta) ou "NÃO LOCALIZADA".
- **Nenhuma alegação de novidade.**
- **A espec não muda nesta tarefa:** só uma lista de "troca proposta" por item, que o Gerente leva ao Matheus.

## 3. A entrega pedida

- **A síntese,** em `docs/LITERATURA_V2_DIGIBRAIN_MODULAR.md` ou na tabela em `docs/referencias/`, no padrão que já existe lá. A escolha
  é do worker, com a justificativa.
- **As entradas novas** nas tabelas de referências.
- **O registro** do mês e a linha no índice.
- **Um PR** com o relato no modelo, com o `conferir_saude` e o `verificar_relato` passando. Entregue e pare.

## 4. Entrega (2026-10-25)

**Onde ficou:** em `docs/referencias/`, no padrão das revisões anteriores. Cada rodada tem a sua síntese e o seu trio (a tabela
`*_verificadas.csv`, o `.bib` e o `*_verificacao_crossref.json`), como a v2 (`V2_SINTESE_Q1_Q7.md`) e a v3
(`V3_SINTESE_FRUTAS_VICIO_V1_V6.md`). Duas razões:
- **o CI** (`tools/verificar_relato.py`) lê todo `docs/referencias/*_verificadas.csv`;
- **a auditoria por rodada** se perderia se as linhas entrassem numa tabela anterior.

**Os arquivos:**
- **a síntese:** `docs/referencias/DM_REVISAO_SUBSTRATO_NEURAL.md`;
- **a tabela:** `docs/referencias/dm_referencias_verificadas.csv`, com 36 linhas (31 VERIFICADA, 1 VERIFICADA sem DOI e 4 NÃO
  LOCALIZADA);
- **o BibTeX das 32:** `docs/referencias/dm_referencias.bib`;
- **o registro bruto por DOI:** `docs/referencias/dm_verificacao_crossref.json`, com 29 DOIs, nenhum com `update-to`.

**A resposta, item a item** (a síntese, seções 2 a 7):

| item | veredito |
|---|---|
| (a) | o modelo tem fonte (unidades de taxa, populações, CTRNN em agente, integrador com vazamento em decisão); **o ponto fixo é NÃO LOCALIZADA** |
| (b) | a CTRNN, a LTC e o CfC são VERIFICADA (o NCP e o Funahashi, só pelo título). **As licenças do CfC e do NCP são Apache-2.0;** o NORNBRAIN continua não comercial; as patentes não foram buscadas |
| (c) | o termo "três fatores" e a elegibilidade têm fonte, e há precedentes em agentes que forrageiam. **O r homeostático como terceiro fator é NÃO LOCALIZADA.** O Doya (2002) diverge da PE-4 no mapeamento do modulador |
| (d) | as opções e os traços têm fonte; **a comparação entre os dois é NÃO LOCALIZADA.** A escolha por opção se apoia na evidência interna |
| (e) | tem fonte em animais (Clayton e Dickinson 1998) e em agentes. **"O mais recente do lugar manda" é NÃO LOCALIZADA** |

**As trocas propostas** são 10, de T-a1 a T-e2. Com elas vão as decisões D-0 a D-2 para o Matheus (a síntese, seção 8). A espec não
mudou.

## 5. As decisões do Matheus (2026-10-25)

Por relato do Gerente, depois do merge do #408:
- **D-0, aplicar todas as trocas:** T-a1 a T-e2 e as duas linhas sem número (Luce e o acumulador com inibição mútua), em
  `docs/ESPEC_DIGIBRAIN_MODULAR.md`.
  - **A condição do Matheus:** em cada troca, o texto separa "a fonte afirma" da "leitura do Digilab".
  - **As três NÃO LOCALIZADA continuam SEM FONTE,** escritas como escolha nossa: o ponto fixo, o sinal homeostático como terceiro
    fator e "o mais recente do lugar manda".
  - **Aplicadas** no branch `v2-modular-espec-fontes`, numa tarefa documental, antes de qualquer vida do modular.
- **D-1, a PE-4:**
  - **a decisão fica:** a excitação modula o `g_apr`, atrás da subchave, desligada no primeiro braço, com a ablação;
  - **o registro, nas palavras do Matheus:** Doya (2002) associa a velocidade de aprendizagem à acetilcolina, e a excitação no Digilab é
    HIPÓTESE EXPERIMENTAL, não conclusão da literatura.
- **D-2, a predição de Lengyel e Dayan (2007), "memória cedo, hábito depois":**
  - entra como leitura descritiva, **SEM gate**, marcada [HIPÓTESE] com fonte, na seção 2.5 da espec;
  - é item para o plano de análise do protótipo.
- **A PE-15** fica feita quanto à licença do código: CfC e `ncps` em Apache-2.0. As patentes não foram buscadas.
