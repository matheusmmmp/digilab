# Prancha: o save na nuvem (levar o pet e os estados)

**Status: PROPOSTA** (2026-11-12). São as telas 3 e 5 do `docs/PLANO_V3_CONTA.md` (seção 3), da etapa CN3, e a parte da frente UX
na F0 do `docs/ROADMAP_V3_CONTA.md`. O código só vem depois desta prancha aprovada, e depois da CN2.

**O pedido:** veio pela sessão "Arquitetura, segurança e infraestrutura do projeto", em 2026-11-12, que repassou a frase do Matheus
"Eu aceito as recomendações e pode efetuar o merge e seguir com as próximas etapas" e pediu as pranchas das telas 3 e 5 no molde da
prancha da conta. O Matheus não fez este pedido nesta sessão; as decisões abaixo vão a ele.

É só desenho: HTML estático, sem código do jogo. O molde é o da prancha da conta (`../ux-conta/`: a caixa, a folha, os botões), sobre
os tokens da prancha dos lugares. O que é novo está em `nuvem.css`. Não há cor nova.

## As telas

| a tela | o que mostra | as capturas (`capturas/`) |
|---|---|---|
| `levar` | tela 3: os pets deste aparelho (o ativo, os guardados, Gerações, o Tamer), "Levar para a conta" e o que não sobe | `_1920_` e `_390_`, `vidro` e `militar` |
| `escolher` | tela 3, quando a conta já tem pets: os dois lados e as três respostas, cada uma com a consequência | `_1920_`, `_390_` |
| `hud` | tela 5: o estado da nuvem no HUD, nos cinco estados (na nuvem, enviando, offline com a hora, só ver, sem conta) | `_1920_` |
| `outro` | tela 5: "este pet está aberto em outro aparelho", com "Jogar aqui" e "Só ver" | `_1920_`, `_390_` |
| `divergiu` | tela 5: as duas histórias e a escolha de qual fica | `_1920_` (nada marcado) e `_390_` (uma marcada) |
| `avisos` | tela 5: "atualize o jogo", "o servidor não respondeu" e "entre de novo" | `_1920_` |
| `copias` | as cópias do save, uma por dia, com "Restaurar" | `_1920_` |
| `restaurar` | a confirmação de restaurar: o que volta e o que acontece com o de agora | `_1920_`, `_390_` |

## O que é real e o que é desenho

- **As regras** vêm do plano (seções 5.1 a 5.6) e da medida da CN0 (`docs/RESULTADO_V3_CONTA_CN0.md`): o que sobe, o que nunca sobe e
  que o pet não envelhece com o jogo fechado. A origem de cada uma está no cabeçalho do `gerar.py`.
- **Exemplo de layout, nunca dado:** os nomes dos pets e dos aparelhos, "dia 3, 07:42", as horas, "38 eventos novos", as datas das
  cópias e "03:00".
- **O fundo e a HUD** são os da prancha dos lugares, simplificados.

## O que a prancha pede ao Matheus

- **UX-NV-1, a resposta marcada quando a conta já tem pets:** **"Guardar os dois" vem marcada.** É a única que não tira nada de lugar.
  A outra opção é nenhuma marcada. Custo de errar: baixo.
- **UX-NV-2, o destino do que não foi escolhido na tela 3:** o plano não diz. **Proponho as cópias, por 30 dias,** o mesmo prazo da
  CN-5; as outras opções são apagar com uma confirmação a mais, ou mandar para Gerações como na divergência. Custo de errar: alto, se
  um pet sumir sem o jogador ver.
- **UX-NV-3, onde fica o estado da nuvem:** **no lugar do "salvo" do relógio,** sem peça nova no HUD. A outra opção é um ícone próprio.
  Custo de errar: baixo.
- **UX-NV-4, "Decidir depois" nas duas histórias:** **o pet fica só para ver nos dois aparelhos até a escolha.** A outra opção é não
  deixar adiar. Custo de errar: médio. Sem o adiar, o jogador escolhe com pressa; com ele, o pet fica parado até decidir.
- **UX-NV-5, o que é "só ver":** **a ilha e o pet aparecem, as ações ficam apagadas e o toque no pet não faz nada.** Isso pede uma
  trava nova no jogo, na CN3 (hoje não existe um pet aberto que não aceita ação). Custo de errar: alto, se uma ação entrar no registro
  de um aparelho sem a vez: é a divergência que a vez existe para evitar.
- **UX-NV-6, o aviso do servidor fora do ar:** **aparece uma vez; depois, só o estado "Offline" no HUD.** Custo de errar: baixo.

## Como gerar e capturar

```bash
python docs/pranchas/ux-conta-nuvem/gerar.py    # os HTML
sh docs/pranchas/ux-conta-nuvem/capturar.sh     # as capturas, em D:\Trab\digilab\capturas_ux_conta_nuvem\ (fora do git)
```

As capturas precisam dos sprites em `D:\Trab\digilab\Assets` (fora do git) e da rede, para as fontes. A pele vem de
`?pele=vidro|xcom`; no desktop `?sem` tira as notas amarelas, e no celular elas só aparecem com `?notas`.

## O que não foi feito

- Nenhum revisor viu a prancha, e o contraste não foi medido.
- A pele Militar foi capturada e não foi olhada.
- O estado da nuvem no celular está descrito numa nota e não desenhado.
- A linha "Cópias do save" na tela Conta (a prancha `ux-conta`) não foi acrescentada lá; está descrita na nota do quadro 7.
- O que acontece com a velocidade do tempo ao abrir noutro aparelho (a questão aberta da CN0, D-CONTA-38) não é desta prancha.
