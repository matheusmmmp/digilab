# RESULTADO V3 — PET_VIVO, etapa 0: a auditoria da escolha (0b) e a medida de "age pelo estado" (0c) (2026-11-08, Claude Code, Opus 5.5)

**O plano:** [PLANO_ANALISE_V3_PET_VIVO.md](PLANO_ANALISE_V3_PET_VIVO.md), APROVADO em 2026-11-08 (repassado pelo Gerente da V3,
D-PV0-7), com o registro da run na seção 11 (`545a4a86`), empurrado antes da primeira vida.

**A run:** só leitura, sem vida nova, sem semente e sem faixa. A leitura é pós hoc, descritiva e geradora de hipótese (seção 6 do plano).
- **O código:** a C4 na worktree destacada `D:\Trab\digilab\v3-pet-vivo-a287ba2` (`a287ba20`); a AN0 e o script no branch
  `v3-pet-vivo-run` (`58c28277`, a `main` `e6548917` com o registro e os desvios por cima).
- **O comando:** o da seção 11, sem mudança, com 4 processos.
- **A tentativa que valeu:** a terceira, das 19:51:31 às 21:31:00 (horário local), 1 h 39 min de parede. A parede gravada é de 5 944 s na
  C4 e de 9,5 s na AN0, abaixo das 2,3 a 2,9 h previstas. As duas primeiras caíram antes de gravar qualquer saída (D-PV0R-2 e
  D-PV0R-4), e nenhuma medida foi lida nelas. Como a terceira foi lançada fica no D-PV0R-5.
- **As vidas:** 4 800 da C4 (o REL e o SEM, 3 lugares, 800 por grupo), 10 da AN0 (4 no `comedouro`, 2 no `longe` e 4 no `longe_fixo`). O
  contrafactual rodou em 970 delas: as 960 da subamostra (k < 8) e toda a AN0.
- **As conferências da seção 2.3 passaram:** o script falha alto em cada uma, e saiu com o código 0. Elas cobrem os sha256 do código da
  C4, os sha256 da fonte e dos gabaritos (gravados no `auditoria.json`), o G1 de cada vida e o G1 com o contrafactual ligado.
- **Os artefatos** ficam em `artifacts_v3_pet_vivo/auditoria/`:
  - `auditoria.json`, sha256 `9eb17b31…7ccd`;
  - `auditoria_vidas.json.gz`, sha256 `14a4b75f…b63b`.

  Todo número deste documento sai do `auditoria.json`, nos campos `grupos.<fonte|braço|lugar>`.

## 1. A linha da regra (seção 5)

| grupo | a linha | HA: TV(P, P¹) mediana; ρ do de mais unidades | HC: receptores com o ΔP do alívio baixo; corpo no inato | HP: sensíveis; incoerentes; ramo 2 |
|---|---|---|---|---|
| C4 REL `comedouro` | **indeterminado** | 0,078; `explorar` 1,17 | humor; 0,65 | 4; nenhum; nenhum |
| C4 REL `longe_fixo` | **indeterminado** | 0,083; `explorar` 1,26 | humor; 0,63 | 4; humor; nenhum |
| C4 REL `longe` | **indeterminado** | 0,095; `explorar` 1,34 | humor; 0,63 | 4; humor; nenhum |
| C4 SEM `comedouro` | **indeterminado** | 0,075; `explorar` 1,17 | humor; 0,67 | 4; humor; nenhum |
| C4 SEM `longe_fixo` | **indeterminado** | 0,060; `explorar` 1,22 | humor; 0,66 | 4; humor; nenhum |
| C4 SEM `longe` | **indeterminado** | 0,066; `explorar` 1,26 | humor; 0,64 | 4; humor; nenhum |
| AN0 REL `comedouro` | **aponta para HP** | 0,049; `explorar` 1,12 | humor; 0,61 | 4; fome, humor; fome |
| AN0 REL `longe_fixo` | **aponta para HP** | 0,055; `explorar` 1,18 | nenhum; 0,61 | 2; fome; fome |
| AN0 REL `longe` | **indeterminado** | 0,066; `explorar` 1,31 | humor; 0,55 | 3; humor; nenhum |

- **O reflexo (A-3)** fica abaixo de 1/3 das decisões em todos os grupos: de 0,15 (C4, `comedouro`) a 0,24 (C4 REL, `longe`), e de 0,03
  a 0,22 na AN0. O aviso da seção 5 não se aplica.
- **A C4: indeterminado nos seis grupos.** É a leitura do tamanho, com 800 vidas por grupo. Pela tabela da seção 5, a auditoria não
  escolhe a frente, e a recomendação da rodada (PV-2 primeiro) fica como está.
- **A AN0: HP em dois dos três lugares, pelo ramo 2 só, no receptor da fome.** O ramo 2 é este: nas decisões com a fome urgente e o
  `comer` perdendo, mais da metade da vantagem da vencedora vem do viés e do contexto. O script conta o ramo 2 como verdadeiro com um
  receptor só.
  - **O tamanho:** a AN0 tem 4 vidas no `comedouro`, 4 no `longe_fixo` e 2 no `longe`.
  - **A comparação:** as duas fontes não dão a mesma leitura. Pela seção 5, a comparação sai lado a lado, sem teste.
- **Por que a HA não aponta:** a TV mediana fica abaixo de 0,10 em todos os grupos. O ρ do `explorar` passa de 1,25 em quatro grupos da
  C4 (o `longe` dos dois braços e o `longe_fixo` do REL) e no `longe` da AN0. No `comedouro` da C4, o comportamento de mais unidades é o
  `explorar` (ρ 1,17), mas o `comer` tem ρ 1,38 e 1,35 (REL e SEM) (D-PV0R-6).
- **Por que a HC e o ramo 1 da HP não apontam, por construção:** só 2 a 4 receptores têm a A_r não vazia: curiosidade, fome, humor e tédio
  na C4. Os dois cortes pedem 6 receptores, e não podem ser atingidos nestas vidas (D-PV0R-6).

## 2. A medida de "age pelo estado" (0c): a SE-C e a RV

A média por unidade, o IC95 sobre as unidades e o dp entre elas, nas 40 unidades da subamostra da C4. A AN0 vem ao lado, sobre as vidas.

| grupo | SE-C | dp por unidade | RV (o `comer` com a fome mudada) | H(P), em bits |
|---|---|---|---|---|
| C4 REL `comedouro` | 0,113 [0,111; 0,115] | 0,0065 | 0,377 [0,370; 0,384] | 1,41 |
| C4 REL `longe_fixo` | 0,114 [0,108; 0,121] | 0,0191 | 0,359 [0,350; 0,369] | 1,48 |
| C4 REL `longe` | 0,103 [0,100; 0,106] | 0,0094 | 0,316 [0,308; 0,323] | 1,56 |
| C4 SEM `comedouro` | 0,121 [0,118; 0,124] | 0,0094 | 0,405 [0,401; 0,409] | 1,45 |
| C4 SEM `longe_fixo` | 0,120 [0,112; 0,127] | 0,0230 | 0,390 [0,383; 0,397] | 1,53 |
| C4 SEM `longe` | 0,114 [0,111; 0,117] | 0,0092 | 0,340 [0,333; 0,346] | 1,59 |
| AN0 REL `comedouro` (n = 4) | 0,130 [0,046; 0,214] | 0,0530 | 0,448 [0,338; 0,558] | 1,31 |
| AN0 REL `longe_fixo` (n = 4) | 0,112 [0,002; 0,223] | 0,0693 | 0,458 [0,249; 0,667] | 1,47 |
| AN0 REL `longe` (n = 2) | 0,197 [0,007; 0,387] | 0,0211 | 0,330 [0,060; 0,600] | 1,40 |

- **O σ da SE-C por unidade, para o δ_E da etapa 2 (7.4):** de 0,0065 a 0,023 na C4, conforme o lugar e o braço. O δ_E não se decide
  aqui.
- **Por receptor, na C4:**
  - a coerência C_r fica perto de 1 na curiosidade e no tédio, perto de 0,6 na fome e perto de 0,5 no humor;
  - o ΔP do alívio do humor fica perto de 0,01, abaixo de 0,05 em todos os grupos da C4.

## 3. O que esta leitura não diz

Valem as ressalvas da seção 6 do plano:
- **Nenhuma causa fica provada.** A leitura é descritiva e gera hipótese.
- **O contrafactual não é uma vida.** Ele mede a escolha de uma decisão com o corpo mudado.
- **Os cortes continuam PROPOSTOS.** Isso vale para os cortes da seção 5 e para o Δ = S/4.
- **Nada muda no jogo nem no cérebro padrão.**

A escolha da frente da etapa 1 é do Matheus. Pela tabela da seção 5, o indeterminado da C4 deixa a recomendação da rodada (PV-2 primeiro)
como está. O HP da AN0 sugeriria a revisão dos pesos inatos, que esbarra na regra "calibração no fim".
