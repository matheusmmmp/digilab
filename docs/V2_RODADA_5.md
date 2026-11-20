# V2 — marco da rodada 5 (2026-10-04)

Coordenador: chat "Principais jogos Digimon com diálogo". Divisão da rodada 5 em `docs/V2_RODADA_4.md`.

## O que a rodada entregou (tudo na `main`; nenhuma run de pesquisa)

| chat | frente | PR | resultado |
|---|---|---|---|
| B | LOBOS-MUNDO | #141 | os lobos veem a bola e as frutas (12 entradas, 9 regras, 759 pesos com o mundo ligado) e escolhem a fruta pelo lobo de decisão; aprendizado desligado = instinto byte a byte nos mundos da bola e das frutas; **E2**: comer fruta ruim dá sinal negativo pelo humor, as outras ações ignoram o humor |
| A | N5-MUNDO | #140 | evento `informar_fruta_<a\|b\|c>_<bem\|mal>`, fora do orçamento, sem mexer no estado nem chegar ao aprendiz; percepção por janela (`Observacao.info_frutas`, 240 min); `DonoInformante` certo/errado nos mesmos ticks; medida N1 da saciedade com a preferência inata |
| C | N5-PLANO | #142 | `docs/PLANO_ANALISE_V2_N5.md`: P2, P2e, P2a (acoplado), gates G-EF, G-PIORA, G-REC (Holm) e G5; riscos registrados antes (exposição, teto) |
| D | BANCADA-FRUTAS | #144 | mundos `casado_frutas`, `descasado`, `mutavel` (troca no dia 7); ofertas por calendário da semente (`CalendarioFrutas`), iguais em todos os braços; `taxa_fruta_ruim` por janela; unidades derivadas sem colisão |

Suíte depois dos três merges de código: 819 passados, 1 pulado.

## Decisões do Matheus na rodada

- N5-1 a N5-8 do plano do N5, como recomendadas: confiança de partida acima de zero e abaixo do teto; a informação só na escolha de
  qual fruta comer; um peso compartilhado; acoplado com o mesmo conteúdo em ticks sorteados; só no descasado; Holm sobre três gates; as
  leituras "inconclusivo por exposição" e "limitado pelo teto"; janela de 240 min.
- Correção do coordenador registrada no plano do N5: o calendário igual entre braços é o `CalendarioFrutas` da bancada.

## Pontos abertos

1. **A bancada ainda cria os lobos sem ver o mundo** (#144 e #141 vieram em paralelo). Ligar isso é a primeira tarefa da rodada 6.
2. O descasado da bancada não é o do N4. Na bancada, a fruta menos preferida faz bem no descasado; no N4, só a preferida fazia mal. A
   regra fica em `efeitos_da_condicao`.
3. O `motivo_lobos` não cita as regras novas (`bola_no_cenario`, `fruta_no_cenario`), e por isso o G4 dos braços com fruta subestima.

## Rodada 6 (divisão)

| chat | frente | tarefa | ordem |
|---|---|---|---|
| D | bancada: lobos vendo o mundo + braços P2/P2e/P2a | `docs/TAREFA_V2_BANCADA_N5.md` | primeiro (destrava B) |
| B | N5 no cérebro (entrada da informação) e depois a revisão do aprendiz | `docs/TAREFA_V2_N5_CEREBRO.md`, `docs/TAREFA_V2_REVISAO_APRENDIZ.md` | em paralelo com D; a revisão depois dos dois |
| A | modo acoplado do informante (P2a) + motivo das regras novas | `docs/TAREFA_V2_N5_ACOPLADO.md` | em paralelo |
| C | plano do N6 (memória) | `docs/TAREFA_V2_N6_PLANO.md` | em paralelo |

Reservas: revisão do aprendiz 18101…18505 (só calibração). N5 12101…12505 / 13101…13505 (a calibração e a validação do N5 ficam
para a rodada 7, depois da revisão). Experimento maior 14101…14505 / 15101…15505.
