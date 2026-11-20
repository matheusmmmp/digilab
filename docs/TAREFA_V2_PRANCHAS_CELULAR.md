# TAREFA V2 — PRANCHAS_CELULAR (2026-10-19)

> **V2, congelado em 2026-10-30** (tag `v2-final`). O estado em que este documento fica na V3 está em `docs/FECHAMENTO_V2.md`; o
> plano da V3, em `docs/PLANO_V3.md`.

Coordenador: Gerente (coordenação da V2). Worker: Claude Code, sessão "Digilab interface design". Worktree e branch: `v2-pranchas-celular`. Status: ABERTA.

Categoria: documentacao. Origem: Matheus, 2026-10-19, pela coordenação (Gerente): um worker de design desenha as pranchas do celular no modelo novo da imagem referencia_mobile_2026-10-19.

## 1. Pergunta

Frente de produto, sem hipótese de pesquisa: como ficam no celular as telas que o jogo tem hoje, desenhadas no modelo novo da referência
`D:\Trab\digilab\_ref\referencia_mobile_2026-10-19.png` (fora do repositório) e conversando com o desktop novo do worker A (`v2-tela-pet`).

## 2. Depende de

- Nenhuma frente de código. Lê o app da `main` (`web/app/src`, React desde o #368) para saber o que cada tela mostra.
- Usa os tokens, os ícones e o pet de reserva da `TelasLayoutDesktop.html` do branch `v2-tela-pet` (ainda fora da `main`).

## 3. Mudança mínima

- **Muda:** só documentos e pranchas.
  - `docs/estilo_up/pranchas/TelasCelular390.html` (novo): as 22 telas do celular; com `?tela=N`, uma tela só, na largura do aparelho;
  - `docs/estilo_up/pranchas/capturas/TelasCelular390_NN.png` e `TelasCelular360_NN.png` (novos), mais o `TelasCelular_mapa.png`;
  - `docs/estilo_up/pranchas/README.md`: as linhas da prancha nova;
  - este documento, a seção do registro e a linha do índice.
- **Não muda:** o código do app e do motor, o save, as rotas e os assets.

## 4. Experimento e gate (se houver run)

Não há run.

## 5. Entrega

- Testes: `python -m pytest tests/ -q`; em `web/app`: `npm test`, `npm run tipos`, `npm run e2e` (se a frente toca a web).
- Registro: seção própria no fim do arquivo do mês, `docs/registro/AAAA-MM.md`, e uma linha no fim do índice `docs/REGISTRO_DESVIOS.md`
  (rodada de saúde, etapa 2). O resumo da etapa vai no corpo do PR e numa seção no fim do documento da
  frente (o `RESULTADO_V2_*.md` da run ou o `TAREFA_V2_*.md` da etapa), nunca no `CLAUDE.md` (rodada de saúde, etapa 1).
- PR contra a `main` com resumo e números (cada um com o artefato). Aviso ao coordenador. Merge só pelo Matheus.
- O corpo do PR segue `.github/pull_request_template.md`; o CI (`tools/verificar_relato.py`) confere os campos e a evidência da categoria.

## 6. Fora desta tarefa

- O código: a troca das telas do app fica para uma tarefa de implementação, depois do ok do Matheus.
- O que a referência mostra e o motor não tem: Lv e XP, a barra de tempo do Treino, a Exploração com níveis e áreas trancadas, o sino. Onde a
  referência mostra, a prancha marca "sem dado no motor".
- Os sprites do Digimon UP: as pranchas versionadas usam o pet de reserva vetorial.

## 7. Critérios de aceitação

- `TelasCelular390.html` abre direto do disco e mostra as 22 telas; `?tela=0` a `?tela=21` mostram uma de cada vez.
- Há 22 capturas em 390 × 844 e 22 em 360 × 800 (página inteira) em `capturas/`.
- Nenhuma tela tem rolagem horizontal em 390 nem em 360: o `scrollWidth` do documento não passa do `clientWidth`, conferido na captura.
- Nenhuma imagem de terceiros nos arquivos versionados.

## 8. Precisa do Matheus

Estão no corpo do PR e na seção 9.

## 9. Resumo da etapa (2026-10-19)

**O que foi desenhado:** 22 telas, cada uma com o conteúdo que a tela do app mostra hoje no celular (levantado em `web/app/src`):
1. **Pet:** a marca, o número grande "01 PET //", o habitat com o balão, as chips e o cartão do parceiro (abre Meus pets), o chamado, os seis
   blocos de ação dos pets v11, a necessidade e a vontade, o Estado atual;
2. **Meus pets;**
3. a 6. **Crescer:** Treinar, Aprendizado (pets v11), Evolução e Itens;
7. a 12. **Lutar:** Arena, Campanha, Fronteira, Medalhas, a luta em andamento e o resultado;
13. a 16. **Diário:** Registro, Catálogo, Gerações e Cenários;
17. a 22. **Conversar, Ajustes, a escolha do brasão, o ovo chocando, a evolução** (a tela azul cheia da referência) **e a morte (v4+).**

**A casca:**
- fundo claro com a grade de 48 px e os estilhaços azuis;
- nas telas internas, o título só em português (sem nenhum caractere japonês, correção do Matheus de 2026-10-19: os títulos em japonês
  da referência eram só ilustração) e o número da seção como marca d'água;
- as sub-abas em pílulas que rolam dentro da faixa;
- a barra de baixo branca (Pet, Crescer, Lutar, Diário), com o item ativo em azul de canto cortado;
- Conversar e Ajustes no cabeçalho do Pet, como hoje.

**Conferências:**
- 44 capturas em 390 e 360 px, página inteira (`capturas/TelasCelular390_NN.png` e `TelasCelular360_NN.png`);
- nenhuma tela com rolagem horizontal nas duas larguras.

**Diferenças com a referência, por não terem dado no motor:**
- o Lv e a barra de XP: a Evolução mostra o tempo até a próxima forma;
- a barra "toque no momento certo" do Treino: o treino é um toque por vez, com intervalo;
- a Exploração com níveis e áreas trancadas: não há essa tela; os lugares trancados do jogo são as ilhas da Campanha;
- o sino.

Onde a referência mostra uma dessas coisas, a prancha marca **"sem dado no motor"**.

**Decisões para o Matheus:**
1. **A barra de baixo.**
   - Recomendação: branca, como na referência.
   - Custo de errar: o `PetPrototipo390` do worker A usa a barra azul-marinho; as duas pranchas precisam ficar iguais antes do código.
2. **Os nomes dos exercícios.**
   - Recomendação: os do motor (`motor/nomes.ts`: Levantar pedra, Corrida, Alvo, Esquiva, Meditar, Resistência).
   - Custo de errar: a `TelasLayoutDesktop` mostra Força, Defesa, Velocidade, Vigor, Técnica e Foco, que não existem no motor.
3. **O "00 OVO //".**
   - Recomendação: manter só como rótulo da tela do ovo chocando.
   - Custo de errar: o motor não tem estágio de ovo, e o número pode sugerir um.
