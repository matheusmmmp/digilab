# Plano de UX das janelas do pet: arrastar, esconder e arrumar (2026-11-12)

**Status: PROPOSTO.** Sem código. A prancha está em `docs/pranchas/ux-janelas/` e espera a aprovação do Matheus. Os tamanhos, as
distâncias e os nomes são **PROPOSTO, SEM FONTE**. Autor: Gerente da UX_TELA_PET (Claude Code, Fable 5.2), branch `v3-ux-janelas`.

**O pedido do Matheus (2026-11-12):** "eu pedi para os menus [...] serem todos modulares, eles serem drag and drop, e a gente conseguir
arrastar e conseguir montar o layout da página da melhor maneira possível para o usuário. [...] se o usuário quiser deixar a aba de
DigiBrain no meio da tela e ele quiser arrastar a aba de últimas [ações] para baixo, ou tirar ela, ele poder fazer isso. [...] E daí em
ajustes vai ter em exibir, daí vai ter o exibir dedicado a cada janela dessa [...]. Quero saber como aplicar isso tecnicamente com o
que a gente já tem hoje em dia. Se é muito custoso [...]. O usuário realmente é um laboratório onde ele consegue controlar essas
questões." E, à pergunta "Faço o plano e a prancha dos menus modulares com arrastar?": "Sim, plano e prancha".

Vale só para a tela do pet no desktop (a partir de 900 px). No celular entram só as chaves de exibir (seção 6).

## 1. O que existe hoje (lido em `web/app/src`, 2026-11-12)

| a peça | onde | o que faz | o que falta para o pedido |
|---|---|---|---|
| os painéis Estado atual, Evolução e Últimas ações | `telas/pet/TelaPet.tsx` (`PainelHud`) | abrem e fecham, cada um; a escolha fica no navegador (a chave `-hud`) | cada um se mover sozinho |
| a linha DigiBrain | `TelaPet.tsx` (`LinhaDigiBrain`) | abre o scan num diálogo modal (`componentes/ScanDigiBrain.tsx`) | ficar na tela enquanto se joga |
| o arraste | `hudPet.ts` (`useArrastavelPorAlca`) | a pilha inteira se arrasta pelos cabeçalhos, **como um bloco só**; a posição fica no navegador (`-hud-arraste`) | um arraste por janela, com encaixe |
| exibir | `hudPet.ts` (`useDetalhesPet`) e Ajustes | **uma chave só,** "Exibir detalhes do pet", liga ou desliga os quatro juntos | uma chave por janela |
| voltar ao lugar | `hudPet.ts` (`voltarPaineis`) e Ajustes › Visual | apaga as posições gravadas | vem junto |

O quadro modular antigo (a alça, o menu, o arranjo salvo; #375, 2026-10-20) saiu em 2026-10-30, quando o habitat passou a tela cheia.
O pedido de arrastar voltou em 2026-11-08 e foi atendido só em parte: a pilha se move, mas inteira.

## 2. O desenho

- **Cada painel vira uma janela solta,** com o cabeçalho de hoje e mais duas coisas: a alça (seis pontos, só para mostrar que arrasta)
  e o menu (três pontos).
- **O arranjo padrão é a pilha de hoje, no mesmo lugar.** Quem não mexer em nada vê o jogo de hoje.
- **Arrastar** é pelo cabeçalho. Perto de uma borda ou de outra janela, aparecem as guias e a sombra do encaixe; longe de tudo, a
  janela fica onde for solta. Ela nunca sai da tela nem entra debaixo do topo, do trilho e das ações de baixo. Esc cancela.
- **Esconder** tira a janela da tela. Ela volta por Ajustes › Exibir, ou pela faixa das escondidas no modo arrumar.
- **Ajustes › Exibir** tem uma chave por janela, três arranjos ("Padrão", "Meu", "Limpo"), "Arrumar as janelas" e "Voltar ao lugar".
- **O DigiBrain** passa a ser uma janela como as outras: fica aberta ao lado do pet, sem travar o jogo.
- **O modo arrumar** (opcional) mostra a grade, o contorno de cada janela, o canto de redimensionar e a faixa das escondidas, com o
  jogo por baixo sem receber toques.
- **Sem arrastar também dá:** o menu de cada janela tem "Mover" (as setas do teclado, Enter fixa, Esc cancela), "Esconder" e "Voltar
  ao lugar". Nada importante fica só no gesto (guia, seção 13).

As janelas da prancha são seis: Estado atual, Evolução, Últimas ações, DigiBrain, Agora (a linha do alto) e o Minimapa. O balão da
fala e o aviso da necessidade já se arrastam hoje e ficam como estão.

## 3. Como fazer com o que já temos

Nenhuma biblioteca nova. O arraste por ponteiro do `hudPet.ts` já existe e já grava no navegador.

1. **Um cadastro das janelas** (um arquivo): o id, o título, o ícone, o conteúdo e o lugar padrão de cada uma. A tela do pet e os
   Ajustes leem o mesmo cadastro; uma janela nova entra num lugar só.
2. **Um estado por janela,** numa chave só do navegador: visível, aberta, e o lugar como o canto mais próximo da tela mais a distância
   até ele (hoje o `hudPet.ts` guarda um deslocamento em pixels a partir do lugar padrão, o que quebra quando a janela do navegador
   muda de tamanho). Com a migração das três chaves de hoje (`-hud`, `-hud-arraste`, `-detalhes-pet`).
3. **Um componente `Janela`** em volta de cada painel, usando o arraste que já existe, com o encaixe e os limites.
4. **A lista de Ajustes › Exibir** gerada do cadastro.
5. **O DigiBrain não modal:** o conteúdo do scan dentro de uma janela comum, no lugar do `<dialog>`.

**Fora do save, do registro e do replay:** é só apresentação. E fica no aparelho: a medida da CN0 fechou que os ajustes de tela não
sobem para a nuvem.

## 4. As etapas e o custo

Um PR por etapa. O custo é a leitura do código, não uma medida.

| etapa | o que entrega | custo | o que pesa |
|---|---|---|---|
| **JN1** | o cadastro das janelas e uma chave "exibir" por janela em Ajustes; nada se move ainda | baixo | a migração da chave única; os e2e que ligam e desligam os detalhes |
| **JN2** | cada janela se arrasta sozinha, com o encaixe, os limites, o lugar guardado por canto, o menu e o mover pelo teclado | médio | os e2e que procuram a pilha no lugar de hoje; o foco do teclado; as duas peles |
| **JN3** | o DigiBrain como janela que fica na tela | médio a alto | hoje ele é um diálogo modal: muda o foco, o Esc, o minimapa (que some com ele aberto) e o que acontece quando ele cobre o pet |
| **JN4** (opcional) | o modo arrumar, os arranjos prontos e o redimensionar | alto | redimensionar pede que o conteúdo de cada janela se adapte à largura |

## 5. Os riscos

| o risco | o que se vê | o que segura |
|---|---|---|
| uma janela cobre o pet, o dock ou o minimapa | o toque no pet cai na janela | os limites do encaixe; o toque só vale no corpo da janela; "Voltar ao lugar" |
| a janela do navegador encolhe | uma janela fica para fora | o lugar guardado por canto; ao abrir, toda janela é trazida para dentro |
| o DigiBrain sempre aberto | o desenho da rede gasta processamento com a ilha 3D rodando | medir na JN3; recolhido, ele não desenha |
| o arraste briga com a câmera solta | arrastar o cabeçalho move a câmera | o arraste começa só no cabeçalho, como hoje |
| o arranjo vira bagunça | o jogador não acha uma janela | "Padrão" e "Voltar ao lugar" a um toque; a lista de Ajustes |

## 6. O celular

Não cabe arrastar numa tela de 390 px, e o mobile mínimo aprovado abre os painéis pelo leque do retrato. No celular entram só as
chaves de Ajustes › Exibir: cada uma põe ou tira o botão daquele painel no leque.

## 7. O custo em determinismo e em e2e

- **No determinismo:** nenhum. Nada entra no motor, no registro nem no save.
- **No e2e:** os testes que procuram `.pet-hud`, a linha do DigiBrain e "Exibir detalhes do pet" mudam nas etapas JN1 a JN3. As
  capturas de referência da tela do pet só mudam com o ok do Matheus (nunca rodo `--update-snapshots` sem ele).

## 8. Decisões para o Matheus

- **UX-JN-1. A prancha inteira:** aprovar para o código começar pela JN1. Recomendo aprovar. Custo de errar: baixo; cada etapa é um PR.
- **UX-JN-2. Soltar livre ou só em encaixes:** **livre, com o encaixe perto das bordas e das outras janelas.** A outra opção é uma
  grade fixa de lugares. Custo de errar: baixo. A grade fixa é mais arrumada e não deixa pôr o DigiBrain "no meio da tela", que é o seu
  exemplo.
- **UX-JN-3. O DigiBrain como janela que fica na tela:** **sim,** no lugar do modal de hoje. A outra opção é a janela só guardar o
  lugar e continuar modal. Custo de errar: médio; é a etapa mais cara e a que mais muda o jogo.
- **UX-JN-4. Quais são as janelas:** **as seis da prancha** (Estado atual, Evolução, Últimas ações, DigiBrain, Agora, Minimapa). O
  topo, o trilho e as ações de baixo ficam fixos. Custo de errar: baixo; outra peça entra depois pelo cadastro.
- **UX-JN-5. Os arranjos prontos:** **"Padrão", "Meu" e "Limpo".** Custo de errar: baixo; são só nomes e posições.
- **UX-JN-6. O modo arrumar (JN4):** **deixar para depois da JN3,** e só se o arraste solto não bastar. Custo de errar: baixo.
- **UX-JN-7. A chave "Exibir detalhes do pet":** **sai,** trocada pelas chaves por janela; quem a tinha desligada começa com as quatro
  janelas escondidas. Custo de errar: baixo.

## 9. O que não foi feito

- Nenhum revisor viu a prancha, e o contraste não foi medido.
- O custo do DigiBrain sempre aberto não foi medido.
- O redimensionar aparece só no quadro do modo arrumar; o conteúdo de cada janela em outra largura não foi desenhado.
- A pele Militar foi capturada e não foi olhada.
