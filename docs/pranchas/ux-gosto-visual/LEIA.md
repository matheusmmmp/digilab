# Prancha: o pet assistindo TV

**Status: PROPOSTA, à espera da aprovação do Matheus.** O plano é o `docs/PLANO_UX_GOSTO_VISUAL.md` (UX-GV-1 a 10 aprovadas em 2026-11-11:
"Sim, segue a prancha"). O código só vem depois desta prancha aprovada. Tudo fica atrás de `?gosto_visual=1`, menos o giro da TV
(UX-GV-3).

É só desenho: HTML estático, sem código do jogo. Os tokens são os da prancha dos lugares (`../ux-lugares-menus/lugares.css`, cópias de
`web/app/src/estilo/tokens.css`). Não há cor nova.

## As telas

| a tela | o que mostra | a captura |
|---|---|---|
| `desligada_1440` | o painel ao abrir: Ligar a TV (principal), Mostrar minha tela, a frase da privacidade e o gosto | `capturas/desligada_1440_vidro.jpg` |
| `ligada_1440` | a tela do dono na TV: o selo com o Parar, a reação em palavras, a frase do gosto e o porquê curto | `capturas/ligada_1440_vidro.jpg`, `_militar.jpg`, `_vidro_limpa.jpg` (sem as notas) |
| `porque_1440` | "Ver todos": os sete componentes, em Imagem e Som, com as três origens | `capturas/porque_1440_vidro.jpg`, `_militar.jpg` |
| `passando_1440` | "O que está passando", separado do gosto | `capturas/passando_1440_vidro.jpg` |
| `fechado_1440` | o painel fechado com a TV ligada: o selo, o botão TV na pilha e o Carinho do dock | `capturas/fechado_1440_vidro.jpg` |
| `ligada_900` | o mesmo painel a 900 px | `capturas/ligada_900_vidro.jpg` |
| `recolhida_390` | a folha baixa do celular, recolhida em duas linhas | `capturas/recolhida_390_vidro.jpg`, `_militar.jpg` |
| `aberta_390` | a folha esticada, com o porquê | `capturas/aberta_390_vidro.jpg` |
| `desligada_390` | a TV desligada no celular: só a TV do jogo | `capturas/desligada_390_vidro.jpg` |
| `janela_360` | a janela pequena (360 × 620): o pet, o balão, uma linha e dois botões | `capturas/janela_360_vidro.jpg`, `_militar.jpg` |
| `reacoes_1440` | as seis reações: a pose, o sinal e as palavras | `capturas/reacoes_1440_vidro.jpg` |
| `giro_1440` | o giro da TV: hoje, de frente (descartada) e em três quartos | `capturas/giro_1440_vidro.jpg` |

## O que é real e o que é desenho

- **O fundo** é uma captura do jogo de 2026-11-06 (`../ux-lugares-menus/img/cena_sem_pet.jpg`). O cantinho de verdade fica perto da
  barraca do Tamer; aqui ele está sobre outro trecho de grama, só para o enquadramento.
- **A TV** é o modelo do #814 (`docs/objetos3d/cartoon/tv.py`), desenhado pelo `desenhar_tv.py` na inclinação da câmera. A imagem na
  tela é um desenho de exemplo.
- **O tapete e as almofadas** são amostras do próprio fundo. No jogo, as cores são as do `cantinhoTv.ts` (#820).
- **O pet** é o sprite do Agumon. As poses das reações são o mesmo quadro, deslocado ou virado. No jogo, são as do cantinho.
- **A HUD em volta** (o topo, o trilho, o dock e a pilha) está simplificada, só para situar. O desenho fiel é o das pranchas
  `ux-pet` e `ux-lugares-menus`.
- **Os textos** vêm do módulo do P0 (`gosto.ts`, `estadoTv.ts`, `tvDoJogo.ts`) e do plano. A tabela está no cabeçalho do `gerar.py`.
- **As posições das marcas nos trilhos, o tempo junto e o relógio** são exemplo de layout, nunca dado.

## O que a prancha pede ao Matheus

- **PR-1, a prancha inteira:** aprovar para o código começar. A recomendação é aprovar; o custo de errar é baixo, porque tudo fica atrás
  da chave e a etapa de código é uma por vista.
- **PR-2, o sinal no "olhando" e no "distraído":** os dois ficam sem ícone, só com a pose. A recomendação é manter assim; o custo é o
  "distraído" passar despercebido com o painel fechado.
- **PR-3, a frase da reação com o motivo** ("Está adorando: tem as cores de que ele gosta"): o motivo é o componente que mais pesou na
  leitura do segundo. O módulo do P0 não devolve esse componente hoje; a etapa de código precisa calculá-lo. A recomendação é fazer;
  sem ele, a frase fica só "Está adorando".

## Como gerar e capturar

```bash
python docs/pranchas/ux-gosto-visual/desenhar_tv.py   # as imagens da TV, em img/ (só quando o tv.py muda)
python docs/pranchas/ux-gosto-visual/gerar.py         # os HTML
sh docs/pranchas/ux-gosto-visual/capturar.sh          # as capturas, em D:\Trab\digilab\capturas_ux_gosto_visual\ (fora do git)
```

As capturas precisam dos sprites em `D:\Trab\digilab\Assets` (fora do git) e da rede, para as fontes. A pele vem de `?pele=vidro|xcom`,
e `?sem` tira as notas amarelas.

## O que não foi feito

- Nenhum revisor (`rev-a11y`, `rev-cena`) viu a prancha.
- O contraste não foi medido; os tokens são os de hoje.
- O P0 não foi aberto no navegador para um "antes" capturado: o antes está descrito no plano.
- Os tamanhos e os tempos são PROPOSTO, SEM FONTE.
