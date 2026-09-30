# Prompt — diagramação da arquitetura do Digilab: como o pet pensa e se comunica

Uso: colar num chat com acesso ao repositório `D:\Trab\digilab\v1` (ou ao GitHub privado `matheusmmmp/digilab`, branch `main`). O resultado esperado é um conjunto de diagramas com o texto que os acompanha. Escrito em 2026-09-29.

---

Você vai diagramar a arquitetura completa de um pet virtual chamado Digilab: como ele percebe, decide, aprende, sente, evolui, luta, herda e **se comunica**. O objetivo é que uma pessoa que nunca viu o código entenda, olhando os diagramas, o caminho de um evento do dono até uma fala do pet, e onde cada sistema se encaixa.

## Regras

1. **Leia o código antes de desenhar.** A verdade está nos arquivos abaixo, não em resumos. Se um diagrama e o código discordarem, o código vence. Leia inteiro: `CLAUDE.md`, `docs/MAPA_SISTEMA_2026-09-29.md`, `docs/DIRECIONAMENTO_2026-09-29.md`, `docs/DESIGN_VOZ_PROPRIA.md`, `docs/DESIGN_MVP_M1_CONFIANCA.md`, `docs/DESIGN_EDUCACAO_HERANCA_LESOES.md`, `docs/ESPEC_COMBATE_V21.md`.
2. **Todo bloco de diagrama aponta para um arquivo.** Cada caixa recebe o nome do módulo que a implementa (ex.: `digilab/obediencia.py`, `web/app/motor/gambits_pet.ts`). Um bloco sem arquivo é uma ideia, e tem que estar marcado como tal.
3. **Marque o estado de cada bloco** com uma cor fixa: **existe e medido** (há artefato em `artifacts*/`), **existe, sinal fraco**, **só na web** (não existe no Python), **em desenho** (branch aberto, sem merge), **não existe**. Use a mesma legenda em todos os diagramas.
4. **Português do Brasil**, sem jargão desnecessário. Na tela do jogo os nomes são de Digimon (Rookie, Champion, WarGreymon…); nos diagramas de arquitetura use os ids internos do motor (`bebe`, `crianca`, `adolescente`, `adulto`, `mega`, `brasa`…) e diga isso na legenda.
5. **Nenhuma imagem da Bandai.** Só caixas, setas e texto. Formato: Mermaid ou SVG, um arquivo por diagrama, mais um `README.md` que os encadeia. Nada de screenshot do jogo.
6. Não invente mecânica. Se não achar no código, escreva "não encontrado".

## O que existe (mapa dos módulos, para você começar)

**Motor de pesquisa, Python, `digilab/` (só biblioteca padrão; `engine.py` congelado):**
- `events.py`, `state.py`, `engine.py`: o log de eventos (ações do dono e avanços de tempo), o estado (necessidades, saúde, humor) e o motor. O estado nunca é salvo; a vida é rejogada do log.
- `policy.py`, `policies/bandit.py`: o `Protocol Politica` (`agir`, `observar`, `estado_interno`), a `PoliticaInstinto` e o bandit contextual (Thompson sampling) cujo prior é a distribuição exata do instinto.
- `tracos.py`: EMA lenta das ações (camada 3).
- `memoria.py`, `memoria_espacos.py`, `emocao.py`: memória curta, memória por espaços (curto e longo), habituação e emoção (tabela categoria × temperamento).
- `temperamento.py`, `vinculo.py`, `obediencia.py`, `desejo.py`: os 4 eixos inatos (`rng_ovo`), o vínculo, a obediência com recusa e motivo, o desejo.
- `motivo.py`, `expressao.py`: o `Motivo` de cada decisão (ação, fatores, referências) e a tabela de frases honestas por estágio e humor.
- `treino.py`, `treino_stats.py`, `treino_vida.py`: o `CanalDeInteracao` (orçamento exato de interações), o `MotorComFeedback`, o treino com fadiga, forçar e sobrecarga.
- `educacao.py`, `donos_educacao.py`, `heranca.py`, `personas.py`: o `MotorEducacao` (janelas de chamado e aviso, disciplina, lutas, lesões, morte, qualificação), os donos sintéticos, a herança (evento `origem`) e as personas de dono geradas por LLM.
- `evolucao.py`: ovo → cuidado → ramo; caráter pela política → linha e forma adulta; sombria.
- `combate_v2/` e `combate_v2/v21/`: o combate por turnos com 3 distâncias, regras puras, gambits ("se isto, faça aquilo"), lutadores, bots, técnicas e passivas por forma.
- `arena.py`, `campanha.py`, `metrics.py`, `protocol.py`, `config.py`, `donos.py`: a arena, a campanha, as métricas únicas, os protocolos com hash e todos os parâmetros.
- A cadeia de motores é por herança de classe: `Motor` → `MotorComFeedback` → `MotorPersonalidade` → `MotorTreino` → `MotorEducacao`. Desenhe isso.

**Fala, `digilab_fala_livre/` e `servidor/`:**
- `fatos.py` (o bloco de fatos com ids: I, T, C, E, M, D, R, V, G e, em desenho, H, O, P, L, F, W), `prompt.py`, `ollama.py`, `saida.py`, `verificador.py` (o juiz que confere se cada afirmação tem fato), `apresentacao.py` (log de apresentação separado do log do pet).
- `servidor/fala_llm.py` (a moldura: a LLM só escreve abertura e fecho, o miolo é a frase honesta), `servidor/fala_livre.py`, `servidor/servidor_local.py`.

**Jogo web, `web/app/motor/` (TypeScript, espelho do Python, sem DOM) e `web/app/src/` (telas):**
- `motor.ts` (o `Motor` com o registro de eventos `t/d/l/g/o/c…`, o replay, as versões de pet 1–5), `bandit.ts`, `estado.ts`, `memoria.ts`, `vinculo.ts`, `carater.ts`, `treino.ts`, `combate.ts`, `gambits_pet.ts` (gambits híbridos: o pet aprende a lista, o dono trava ou veta), `bots.ts` (lugares e NPCs da campanha), `catalogo.ts`, `constantes.ts` (conferidas contra o Python por `test/mapa_constantes.json`), `expressao.ts`, `nomes.ts`.
- Telas: `pet`, `crescer` (treinar, aprendizado, evolução), `lutar` (arena, campanha), `diario` (registro, catálogo, cenários, gerações), `conversar`, `config`.

**Em desenho ou em branch (marque como tal):** voz própria (extrator da história, mentira aprendida, almanaque, corpus de espécies), M1 (confiança de combate e novidade por rival), evolução canônica (Mega como estágio, pets v5).

## Os diagramas que quero (nesta ordem)

1. **Visão geral em camadas por escala de tempo.** Corpo e drives (minutos) → decisão e aprendizado (horas) → traços, relação e história (dias e vida) → linhagem (gerações) → Tamer (entre vidas). Fora da mente: dono, ambiente, outros pets. Mostre os ciclos: expressão → dono, e morte → linhagem.
2. **O caminho de um toque do dono.** Do clique em "alimentar" até a frase do pet: evento no log → `CanalDeInteracao` → `_aplicar_acao_usuario` na cadeia de motores → mudança de estado → `observar` do bandit (recompensa) → memória → vínculo e obediência (aceita ou recusa, com motivo) → `Motivo` → `expressao` → moldura ou fala livre → tela. Um diagrama de sequência.
3. **O caminho de uma decisão do pet.** A cada tick: estado → `Observacao` → instinto (prior) + bandit (aprendido) + memória (fatores) + temperamento (modula) → ação → `Motivo` com fatores → traços (EMA). Mostre onde a rng do ambiente e a rng da política se separam.
4. **A cadeia de motores e o replay.** As cinco classes de motor, o que cada uma acrescenta, e como o replay rejoga o log do zero e confere o estado (Python) e a assinatura (web). Inclua o modo livre gravado: onde a LLM ou o acaso entram e como viram evento.
5. **Como o pet fala.** Os três modos (template, moldura, fala livre) lado a lado, com o que cada um recebe (motivo, fatos com ids), o que a LLM pode escrever, o verificador, o log de apresentação, e o que **nunca** entra no registro do pet (o texto do jogador). Acrescente, marcado como em desenho, a voz própria: extrator da história, gatilhos espontâneos, a mentira decidida pelo motor e registrada, o almanaque e o corpus de espécies.
6. **Personalidade em três escalas.** Estado (humor, emoção, confiança em desenho) → traço (EMA, caráter) → predisposição (temperamento herdado). Quais eixos existem, quais são derivados, e o que cada camada modula.
7. **Evolução e formas.** Ovo (espécie pela semente) → `bebe` → cuidado → ramo → caráter → linha → eixo complementar → forma adulta; sobrecarga → sombria; qualificação por vitórias; Mega (em desenho). Uma espécie como exemplo, com os ids e, ao lado, os nomes de Digimon que a tela mostra.
8. **Combate.** Estado da luta (distância, HP, guts), lista de gambits (condições do catálogo fechado → ação), técnicas por linha e passivas por forma, o ε (disciplina, sombria, confiança em desenho), e o aprendizado dos gambits híbridos na web (nota por regra, trava e veto do dono).
9. **Educação, lesão e morte.** Janelas de chamado e aviso (real ou falso), a resposta do dono (bronca, petisco, nada) e o efeito na disciplina e no vínculo; lutas, lesões, morte; a mentira (em desenho) como janela do mesmo tipo.
10. **Herança e linhagem.** Cruzar dois adultos → `rng_heranca` → temperamento (média + ruído) e espécie → evento `origem` com os hashes dos pais → ovo. O que **não** herda. Ao lado, em cinza, o que a pesquisa mediu: genoma explica 4,9%.
11. **Pesquisa: como uma run vira número.** Config → protocolo com hash → vidas (donos sintéticos, orçamento) → replay do disco → arena ou painel → `metrics.py` → bootstrap → gate → `artifacts*/`. Mostre onde entram sementes de calibração e de validação.
12. **Python × web: paridade.** O que é espelhado (motor, constantes via `mapa_constantes.json`, gabaritos), o que existe só na web (gambits híbridos, jornada, escala ligada) e o que existe só no Python (arena de pesquisa, protocolos).

## Como entregar

- Uma pasta `docs/diagramas/` com `01_visao_geral.md` … `12_paridade.md` (Mermaid dentro do Markdown) ou `.svg`, e um `README.md` com a legenda de cores, a lista dos diagramas e, para cada um, três linhas de texto dizendo o que ele mostra.
- No fim do `README.md`, uma seção **"O que não encontrei"** com tudo o que o prompt pediu e o código não tem, e uma seção **"Onde o código discorda dos documentos"**.
- Não altere nenhum arquivo fora de `docs/diagramas/`. Não abra PR: deixe num branch chamado `diagramas-arquitetura`.
