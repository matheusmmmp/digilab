# TAREFA V2 — UP-ARENA: a arena em tempo real no jogo web (2026-10-29)

Coordenador: sessão de coordenação da integração UP (Claude Code). Worker: a definir. Worktree e branch: `v2-up-arena`. Status: ABERTA (liberada pelo Matheus em 2026-10-29)
(D1, D2, D3 e D5 decididas; a UP-ATLAS na `main`, #441).

Categoria: implementacao. Origem: Matheus, 2026-10-29: `D:\Trab\digilab\remaster\LEVANTAMENTO_INTEGRACAO.md`, seção 4,
`D:\Trab\digilab\remaster\arena_equilibrio.md` e o protótipo `remaster/fonte/site/arena.html` (publicado em
https://claude.ai/artifact/HHBLAp9HSa8uNFCqNjezmh, `arena.html`, versão 14).

## 1. Pergunta

A arena em tempo real do protótipo pode virar um modo separado do jogo web, com os dados fora do código, em TypeScript com testes, e com a
medição de equilíbrio reproduzível por semente, sem tocar o combate atual? Nó do produto: batalha local (`docs/PRODUTO_VISAO.md`,
seção 3); não vem de hipótese do `PLANO_V2_PESQUISA.md`.

## 2. Depende de

- **D1** (modo próprio no jogo ou protótipo fora dele): se for "fora", esta tarefa se reduz à etapa 0 abaixo.
- **D2** (Python e paridade, ou só web) e **D5** (os números do EQ até o Matheus jogar).
- UP-ATLAS na `main` (os clipes `Run`, `Attack_1`, `Stun`, `Die`). UP-SOM opcional (sem ela, a arena vai muda).

## 3. Mudança mínima

**A pilha do jogo não muda (Matheus, 2026-10-29):** tudo o que o DigiLab já usa de tecnologia fica como está (Vite 8.3.1, TypeScript
7.0.2, React 19.3.0, Tailwind 4.3.3, three 0.186.1, o Node do `engines` e as demais dependências de `web/app/package.json`, nas mesmas
versões; o Python e a biblioteca padrão no pacote `digilab/`). Nenhuma versão sobe ou desce e nenhuma ferramenta é trocada; as mudanças
desta tarefa são implementadas dentro dessa pilha. O `package.json` e o `package-lock.json` saem iguais, a não ser por dependência nova
aprovada pelo Matheus antes (seção 8).

**Fonte conferida em 2026-10-29:** `arena.html` (1 209 linhas, 77 kB), `const EQ` na linha 226 (raio 18, alcanceCorpo 44, investida 58,
recuo 1, peito 24, danoCorpo 1, danoDist 1, kGolpe 0,06, kProj 0,05, pesoEstagio 0,2, variacao 0,1; a "vida ÷ 6" é uma opção da tela,
fora do EQ), `site/ataques/` (`ataques.json` com 379 efeitos de 210 Digimon, `golpes.json` 270, `status.json` 241, `atributos.json`),
`site/arenas/` (16 arquivos). **Achado:** o `arena.html` usa `Math.random` em 18 lugares e não tem semente; o `arena_equilibrio.md` cita
"semente fixa" (7, 42, 1–3, 7–8). O harness com semente não está no arquivo (talvez em `lote*.json` ou fora da pasta durável): vai para o
registro de desvios, e a etapa 0 o procura.

0. **Etapa 0, separar e reproduzir (antes de portar):** localizar o harness das medições do `arena_equilibrio.md`; se não existir, a
   medição "depois" não é reproduzível e fica registrada assim. Separar os dados em JSON (arenas, golpes, efeitos, status, atributos,
   EQ) e listar o que é código. **Parar e mostrar.**
1. **Simulação sem DOM** em `web/app/arena/` (pasta nova, fora de `motor/`; a mesma regra de "sem DOM" do motor, com o seu teste): passo
   de tempo fixo (não o `dt` do quadro), RNG própria com semente (`derivar_semente` como no motor, um fluxo por uso: IA, dano, partículas
   de efeito só visual fora da RNG da simulação), entrada do jogador como evento.
2. **Tela própria** atrás da chave desligada `ARENA_TEMPO_REAL`, numa rota do destino Lutar (sem mexer em `TelaArena.tsx` nem no
   combate V2.1). Desligada, o jogo de hoje igual.
3. **Dados (fora do git):** os JSON de status, golpes e efeitos e a arte dos mapas são do jogo: vão para `D:\Trab\digilab\Assets\arena_up\`,
   servidos pela lista do `vite.config.ts` e do `servidor_local.py`. **Os números do EQ e das regras de arena entram como PROPOSTOS, com
   fonte** (`arena_equilibrio.md`, rodada de 2026-10-29), numa constante versionada do app (são números do DigiLab, não do jogo).
4. **Medição de equilíbrio reproduzível:** um script (`web/app/scripts/medir_arena.ts` ou equivalente em Node) que roda as lutas CPU × CPU
   do método do `arena_equilibrio.md` por semente e grava o resultado em disco; um teste curto confere que a mesma semente dá o mesmo
   resultado. A rodada inteira não roda no CI.
5. **Se D2 = Python com paridade:** a simulação vai também para o Python (fora de `combate_v2`), com gabaritos `experiments/exportar_*.py`
   e o teste de paridade. Se D2 = só web: a arena fica fora do protocolo de resultado e não entra em nenhuma run de pesquisa.

**Não muda:** `combate_v2` (rodadas encerradas), `TelaArena.tsx`, `TelaLuta.tsx`, `PalcoLuta.tsx`, o motor, o `engine.py`, o log e o save
do pet. O pet do jogador não ganha nem perde nada na arena nesta tarefa (sem efeito no motor).

## 4. Experimento e gate

Não há run de pesquisa. A medição de equilíbrio (item 4) é engenharia: a meta é reproduzir as tabelas "depois" do `arena_equilibrio.md`
na mesma semente, ou registrar a diferença. Sem calibração nova nesta tarefa (D5).

## 5. Entrega

`npm test`, `npm run tipos`, `npm run e2e` (a chave desligada e a tela da arena com dados sintéticos versionados); o teste de
determinismo da simulação; a saída do script de medição em disco, citada no relato. Se D2 = Python: os testes de paridade. Registro e
relato como o modelo manda.

## 6. Fora desta tarefa

Ligar a arena ao pet (ganho, treino, evolução); multiplayer; nova rodada de equilíbrio; a simulação de partículas do Unity; a skin
`Invision`; mexer no combate V2.1.

## 7. Critérios de aceitação

1. A etapa 0 diz onde está o harness com semente ou registra que não existe.
2. A simulação roda em Node sem DOM, e a mesma semente dá o mesmo resultado (teste).
3. Os dados do jogo não estão no git; os números do EQ estão numa constante com PROPOSTO e a fonte.
4. Com a chave desligada, nada muda no jogo (e2e e capturas).
5. O script de medição grava as tabelas por arena e por estágio e o relato as compara com o `arena_equilibrio.md`.

## 8. Precisa do Matheus

D1, D2 e D5 antes de começar (com a recomendação do coordenador). Depois da etapa 0: seguir sem o harness original, se ele não aparecer.

## 9. Decisões tomadas

- **D3 DECIDIDA (Matheus, 2026-10-29):** os assets novos seguem a regra dos sprites (`docs/UI_GUIDELINES.md`, seção 5.1).
- **D1 DECIDIDA (Matheus, 2026-10-29, "siga as recomendações"):** a arena em tempo real entra no jogo como modo próprio, atrás da chave
  desligada `ARENA_TEMPO_REAL`, numa rota do destino Lutar, sem tocar o combate V2.1 nem o pet.
- **D2 DECIDIDA (idem):** a arena fica só na web, fora do protocolo de resultado, sem versão Python nem paridade; a simulação em TS é
  determinística, com semente. O item 5 da seção 3 vale só no ramo "só web".
- **D5 DECIDIDA (idem):** os números do EQ e das arenas ficam PROPOSTOS como estão até o Matheus jogar; sem rodada de calibração.
- **A pilha não muda** (Matheus, 2026-10-29): seção 3.
