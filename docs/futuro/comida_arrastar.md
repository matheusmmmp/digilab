# Comida de arrastar — o dono escolhe onde a comida cai (ideia)

Status (2026-10-22): **IDEIA, PROPOSTA.** Pedido do Matheus depois de testar o jogo no celular ("a comida está como drag n drop para
eu escolher onde jogar para o pet?"). Não autoriza implementação: entra quando o mundo físico estiver no jogo (seção 3).

**Regras deste documento:** nenhum número novo; nenhuma alegação de novidade; só o que o código da `main` tem é dado como existente.

## 1. A ideia

No jogo, o dono arrasta a comida (ração ou fruta) e a solta num ponto do mundo. O pet vê, decide ir e anda até ela. Onde o dono põe a
comida passa a ter consequência: perto da casa, longe, ao lado de um tronco que tapa a visão.

## 2. O que já existe (a `main`, 2026-10-22)

| peça | onde | estado |
|---|---|---|
| o gesto com lugar, `deixar_comida(tipo, x, y)` | `digilab/mundo.py` (seção 4 da docstring), `events.deixar_comida` | existe no Python, atrás da chave do mundo (`ConfigMundo.ligada`) |
| o mesmo evento no TS, com o replay | `web/app/motor/mundo.ts` (`EventoMundo`, `deixar_comida`) | existe no motor TS do mundo, com paridade |
| o dono sintético com lugar (`DonoComLugar`: comedouro, perto, longe) | `digilab/mundo.py` | a pesquisa já varia onde a comida cai |
| a fruta ao lado da ração (`deixar_fruta`) | `digilab/mundo.py`, `docs/futuro/paladar.md` (RP-2) | existe atrás da chave própria |
| o pet que anda até o alvo, a percepção pelo cone (P4) | `mundo.py`, `motor/mundo.ts` (#384, #390, #394) | existe atrás das chaves do contrato |

**O que o jogo de hoje faz:**
- O pet v11 do jogo roda sem o mundo físico. Alimentar é o botão das ações da tela Pet (`AcaoDono` `alimentar`), sem posição.
- O único arrastar e soltar do jogo é o dos módulos do quadro no desktop (`src/componentes/Quadro.tsx`).
- O cenário 3D da tela Pet (#375) é só vista: o pet fica na plataforma.

## 3. O que falta, e em que ordem

1. **O mundo físico no jogo:** um pet do jogo com o `MotorMundo` ligado (versão nova de pet, `VERSAO_PET`) e a vista 3D do POC
   desenhando o mundo do motor. Depende da P4 (`docs/TAREFA_V2_P4_CEREBRO_MUNDO.md`; a P4-7 diz que o jogo não muda até lá).
2. **O gesto na tela:** arrastar a comida da barra de ações e soltar no chão do mundo. A tela converte o ponto da vista para a célula do
   motor e grava `deixar_comida(tipo, x, y)`; o motor valida (dentro do mapa, sem parede) e falha alto se não valer.
3. **Acessibilidade e celular:** o arrastar não pode ser o único caminho. Tocar em "Alimentar" continua pondo a comida no comedouro
   (o lugar padrão do `DonoComLugar`), e tocar num ponto do chão depois de escolher a comida também vale.

Sem o passo 1, o arrastar só mudaria o desenho: o pet do jogo de hoje não anda até a comida. Por isso a ideia espera.

## 4. Perguntas para quando abrir

- **CA-1:** quais comidas se arrastam (só a ração, ou também as frutas do paladar)?
- **CA-2:** o lugar da comida entra numa pergunta de pesquisa (o que o pet aprende sobre o mundo pelo lugar que o dono escolhe) ou fica
  só no jogo? A pergunta do dono está encerrada (`docs/LEITURA_CONSOLIDADA_DONO.md`): só se reabre com pergunta nova sobre o aprendiz.
- **CA-3:** limites do gesto: quantas comidas no chão ao mesmo tempo, e se a comida some com o tempo (hoje o motor do mundo decide; não
  mudar sem tarefa).

## Referências

SEM FONTE: nenhuma referência sustenta esta ideia; é pedido de jogo do Matheus.
