# TAREFA V3 — O pet que pensa: o cérebro que planeja com um modelo do próprio corpo

Status: **ABERTA, etapa PQV-0 (o desenho) PROPOSTA** (2026-11-21). Nenhum código e nenhuma vida.

**A origem:** o Matheus decidiu em 2026-11-21: "vamos partir para o 'pet que pensa'". É a opção D3 do parecer da Gerência (vault,
`10 Auditoria/Vale continuar o cérebro 2026-11-21.md`): um cérebro que planeja, com um modelo do próprio corpo, já que é o corpo que
decide. O pedido de fundo é de 2026-10-07: o pet que prevê "se eu fizer X, acontece Y" e planeja.

## O que esta tarefa entrega, por etapa

| etapa | o quê | estado |
|---|---|---|
| **PQV-0** | o levantamento (vault, `10 Auditoria/Levantamento do pet que pensa 2026-11-21.md`) e o desenho [docs/futuro/pet_que_pensa_v3.md](futuro/pet_que_pensa_v3.md) | PROPOSTO; as decisões PQV-1 a PQV-12 esperam o Matheus |
| PQV-1c | o código Python do M-PLANO, desligado, com os testes | espera a PQV-0 |
| PQV-2t | a fumaça e a triagem de 20 unidades | espera o código e o ok do Matheus |
| PQV-3 | o plano de análise, a seção `PR-<id>` e a run de 200 | só se a triagem passar no corte |
| PQV-4w | o porte à web | só se a confirmatória confirmar |

## As regras em vigor

- **A triagem antes de confirmar:** de 10 a 20 unidades, minutos de máquina, sem pré-registro, só depois de o Matheus aprovar o desenho.
  O corte (|efeito| > 2δ) ainda não foi decidido.
- **A máquina:** no máximo 4 processos e uma run de pesquisa por vez; o `tools/pre_run.py` é a porta. As faixas de sementes vêm da
  sessão coordenadora.
- **Os merges** são só do Matheus, com o CI verde.
- **O treino nunca se baseia em clicar carinho ou tapa.**
- **Só vale a aprovação dada pelo Matheus direto**, não a repassada.
