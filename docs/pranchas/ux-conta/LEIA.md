# Prancha: a conta (entrar e primeiro acesso)

**Status: PROPOSTA** (2026-11-12). O plano é o `docs/PLANO_UX_CONTA.md`; as regras vêm do `docs/PLANO_V3_CONTA.md` (CN-1 a CN-18
DECIDIDAS). O código é da etapa CN2 e só vem depois desta prancha aprovada.

É só desenho: HTML estático, sem código do jogo. Os tokens e os moldes são os da prancha dos lugares
(`../ux-lugares-menus/lugares.css` e `movel.css`, cópias de `web/app/src/estilo/tokens.css`). O que é novo está em `conta.css`. Não há
cor nova.

## As telas

| a tela | o que mostra | as capturas (`capturas/`) |
|---|---|---|
| `ajustes_conta` | a linha "Conta" no topo dos Ajustes, sem conta | `_1920_` e `_390_`, `vidro` e `militar` |
| `entrar` | Entrar: o que vai para o servidor, Google, GitHub, "Agora não" | `_1920_`, `_390_`; `entrar_1920_vidro_limpa` (sem as notas) |
| `estados` | os cinco estados: saiu para o Google, conferindo, não deu, fora da lista, menos de 18 | `_1920_` |
| `falhou` | o estado "não deu" na folha baixa do celular | `_390_` |
| `primeiro` | Primeiro acesso: o apelido, a idade, o aceite | `_1920_`, `_390_`, `_360_`; `primeiro_1920_vidro_limpa` |
| `apelido` | a troca do apelido: a lista fechada e o número | `_1920_`, `_390_` |
| `perfil` | Conta: o apelido, os aparelhos, os dados, sair e apagar | `_1920_`, `_390_`; `perfil_1920_vidro_limpa` |
| `apagar` | Apagar a conta: o que some e a confirmação | `_1920_` (antes de marcar) e `_390_` (marcado) |

## O que é real e o que é desenho

- **O fundo** é a captura do jogo de 2026-11-06 da prancha dos lugares; a HUD em volta é a de lá, simplificada.
- **A caixa** é a dos Ajustes de hoje. A lista dos Ajustes está encurtada.
- **Os textos** são desta prancha; as regras por trás de cada um estão no cabeçalho do `gerar.py`.
- **Exemplo de layout, nunca dado:** "Agumon#4821", as datas e as horas, os aparelhos, os oito nomes da lista, "versão 2026-11".
- **A marca do Google** é um desenho simples em uma cor; a do GitHub é o ícone do lucide.

## O que a prancha pede ao Matheus

As UX-CN-1 a UX-CN-6, na seção 7 do `docs/PLANO_UX_CONTA.md`.

## Como gerar e capturar

```bash
python docs/pranchas/ux-conta/gerar.py    # os HTML
sh docs/pranchas/ux-conta/capturar.sh     # as capturas, em D:\Trab\digilab\capturas_ux_conta\ (fora do git)
```

As capturas precisam dos sprites em `D:\Trab\digilab\Assets` (fora do git) e da rede, para as fontes. A pele vem de
`?pele=vidro|xcom`; no desktop `?sem` tira as notas amarelas, e no celular elas só aparecem com `?notas`.

## O que não foi feito

- Nenhum revisor viu a prancha, e o contraste não foi medido.
- As telas da CN3 (levar o pet para a conta, o ícone de sincronização, as cópias) e as páginas públicas da CN6 não estão aqui.
