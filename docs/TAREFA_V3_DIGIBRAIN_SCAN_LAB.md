# TAREFA V3 — DIGIBRAIN_SCAN_LAB (2026-11-11)

Coordenador e worker: sessão do Gerente da V3 (Claude Code, Opus 5.5). Worktree e branch: `v3-digibrain-scan-lab`. Status: ENTREGUE (PR
aberto).

Categoria: implementacao. Origem: Matheus, 2026-11-11. Ele viu o painel antigo do DigiBrain no jogo e pensou que o visual novo tinha se
perdido no merge. A auditoria mostrou outra causa: o scan (#668 e #681) só foi feito para o pet do cérebro A, e o pet do laboratório do
modular (v16) abria o painel antigo de propósito. Pedido: "Sim, leve".

## 1. Pergunta

O pet do laboratório abre o DigiBrain no mesmo scan do pet do A? Nó do produto: a leitura do cérebro (`docs/PRODUTO_VISAO.md`).

## 2. Depende de

O scan na `main` (D1b, D1c e D1d da UX_TELA_PET, #668, #681 e #689) e a leitura do modular (`Motor.leituraLab()`, LM5b).

## 3. Mudança mínima

- **`web/app/src/componentes/ScanDigiBrainLab.tsx` (novo):**
  - a mesma casca do scan: o modal pequeno, o selo, o "i", o mapa em texto, o fechar, a varredura e o pulso numa decisão nova;
  - o desenho do modular:
    - atrás, os 7 módulos do motivo (`ORDEM_TERMOS`);
    - no meio, a soma;
    - na frente, as opções com a chance de cada uma (no máximo 7, com a escolhida sempre dentro);
  - cada fio é a barra de hoje: a parte de cada módulo no peso da escolhida, tracejada quando puxou contra;
  - o mapa em texto é o painel de antes inteiro (`ConteudoDigiBrainLab`).
- **`web/app/src/componentes/ScanDigiBrain.tsx`:** só exporta as peças da casca e do desenho que o novo usa. O scan do A não muda.
- **`web/app/src/telas/pet/TelaPet.tsx`:** o pet do laboratório abre o `ScanDigiBrainLab`. O caminho do painel antigo (`PainelDigiBrain`) sai.
- **`web/app/src/componentes/DigiBrainLab.tsx`:** exporta `NOME_TERMO`.
- **CSS:**
  - `painel-hx.css`, `pele-vidro.css` e `pele-xcom.css`: o mapa em texto do modular usa os mesmos tokens escuros dos painéis;
  - `scan_digibrain.css`: o mapa em texto fica sem o fundo e a margem da folha.

Não mudam o motor, o log, o save, o replay nem a leitura do modular.

## 4. Experimento e gate

Não há run.

## 5. Entrega

`npm run tipos`, `npx vitest run`, os e2e do laboratório e do DigiBrain, as capturas em `docs/pranchas/digibrain-lab/`.

## 6. Fora desta tarefa

- Fios para as opções não escolhidas: a leitura só traz as barras da escolhida.
- O selo "experimental" dentro do scan: o selo do laboratório continua no topo da tela (`.topo-lab .lab-selo`).

## 7. Critérios de aceitação

1. O pet do laboratório abre o scan (`#pet-painel.scan--lab`), com o mapa (`svg.mp--lab`) e uma opção escolhida (e2e `lab_modular`).
2. O mapa em texto mostra as seções do painel de antes (o mesmo e2e).
3. O desenho tem um fio por barra e um ponto por módulo e por opção, em 390 e 1920 px (`test/scan_digibrain_lab.test.ts`).
4. Os e2e do DigiBrain do pet do A seguem passando.

## 8. Precisa do Matheus

O merge. O número `OPCOES_NO_DESENHO` = 7 é PROPOSTO, SEM FONTE (D-SCANLAB-2).
