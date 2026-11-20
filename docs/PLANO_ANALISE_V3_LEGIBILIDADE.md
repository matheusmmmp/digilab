# Plano de análise V3 — LEGIBILIDADE: o aprendizado da A2 aparece para quem olha? (2026-11-17)

**Status: PROPOSTO, esperando o Matheus (decisões LG-1 a LG-6, seção 9).** Sem a linha de trava, nada é gerado nem coletado. Depois da
aprovação, a linha de trava entra num commit próprio, antes do primeiro estímulo.

Tarefa: `docs/TAREFA_V3_LEGIBILIDADE.md`. Origem: a rodada de literatura `docs/referencias/V3_SINTESE_DREYFUS.md`, que entra com o PR #954.
A linha de base é a ablação da A2 (`docs/PLANO_ANALISE_V3_ABLACAO_APRENDIZADO.md` e o resultado, no PR #952, ainda aberto).

## 0. O que já foi visto

- **A A2 deu "muda":**
  - 9 das 15 medidas rejeitadas pelo Holm, com efeitos pequenos (o maior foi o "cheiro", −0,009);
  - a distância de variação total entre as distribuições médias de ação de A e B ficou em 0,0084.

  O efeito é real no motor e pequeno. Nenhuma vida da A2 foi olhada como vídeo, e nenhum estímulo deste plano foi gerado.
- **A literatura que motiva o plano** (VERIFICADA, `docs/referencias/v3_dreyfus_referencias_verificadas.csv`):
  - Collins (1996, pp. 106-108): quem usa a máquina conserta as deficiências dela sem notar;
  - Anderson et al. (2019), na lista verificada da skill: a legibilidade tem de ser medida, não presumida.

## 1. A pergunta, a hipótese e a previsão, escritas antes

- **A pergunta:** uma pessoa que não sabe qual é qual consegue dizer, olhando o pet, qual das duas vidas teve o aprendizado em vida (o
  braço A da A2) e qual o teve zerado (o braço B)?
- **A hipótese (H):** sim, acima do acaso, com margem.
- **A previsão:** SEM FONTE. A distância de variação total de 0,0084 sugere que o efeito pode ser pequeno demais para o olho, e a
  regra de leitura (seção 5) aceita qualquer resultado.

## 2. Os estímulos

### 2.1 As vidas

- **De onde vêm:** as vidas da run da A2, refeitas de forma determinística pelo SHA dela (`git_head` ecbe0320 no meta da run), com o
  mesmo harness (`web/app/scripts/ablacao_aprendizado.ts`).
- **Os braços:** a mesma semente, o mesmo dono e o mesmo pet. Em A, o aprendizado está ligado; em B, ele é zerado antes de cada leitura
  (a seção 2.2 do plano da A2).
- **Nenhuma faixa nova:** as sementes são da A2 (98101…98300) e nada se mede no motor. A conferência é o sha256 das ações de cada vida,
  que tem de bater com o `vidas_sha256` do meta da A2 (falha alto).

### 2.2 A seleção dos pares, escrita antes de qualquer estímulo

- **As sementes:** 20 sementes sorteadas de 98101…98300 por `random.Random(20261117).sample(range(98101, 98301), 20)`.
- **Os pares:** os 3 donos de cada semente (`atencioso`, `relapso`, `incoerente`), 60 pares (A, B) ao todo.
- **Sem filtro por conteúdo.** Nenhum par sai por ser parecido demais; filtrar olhando o estímulo enviesaria a taxa de acerto.

### 2.3 O recorte (LG-1, LG-2)

- **A forma:** um vídeo do pet no jogo, com a câmera e a interface do jogo de hoje (LG-1).
  - **Em A:** a vida é refeita pelo replay do jogo (`Motor.reproduzir`).
  - **Em B:** o replay do jogo não instala o invólucro da A2. Por isso, um roteiro de laboratório em `web/app/scripts/` monta o motor com
    o invólucro e alimenta a vista. Isso é implementação e fica para depois da aprovação, sem mudar o jogo.
- **A janela (LG-2):** as **últimas 10 horas de jogo** de cada vida, a mesma regra em A e B, mostradas em **60 s** (10 min de jogo por
  segundo, a velocidade do beta).
  - As últimas horas foram escolhidas porque o aprendizado teve mais tempo de agir.
  - Se a vida morreu antes do fim, valem as 10 horas antes da morte. Ver a morte não é um sinal escondido: o número de mortes por braço
    vai no descritivo.
- **O cego:**
  - os vídeos não têm rótulo, e o nome de cada arquivo é um hash;
  - o lado (esquerda ou direita) de A em cada par é sorteado por avaliador, com a rng `random.Random(f"legibilidade|{id}")`;
  - a tabela que liga o hash ao braço fica fora do formulário e só é lida na análise.

## 3. A tarefa e os avaliadores

- **A pergunta mostrada (LG-5):** "Os dois pets nasceram iguais e tiveram o mesmo tipo de dono. Um deles aprende com o que acontece com
  ele (o que come, o que faz) e o outro não. Qual aprendeu?" A resposta é forçada, esquerda ou direita, seguida da confiança (1 a 5) e de
  um campo livre opcional ("o que você viu?").
  - **Por que não "aprendeu com o dono":** a auditoria `docs/AUDITORIA_V3_SUCESSO_CORPO.md` (seção 6) mostra que o modular não aprende
    com o gesto do dono (`adapt.py:622-625`). Ele aprende com a variação do próprio corpo. A frase "com o dono" mentiria ao avaliador.
  - **O que a A2 tira:** o braço B zera só o P1 e o P2 (o desfecho, o custo de andar e o hábito, M4 a M6 na auditoria). A memória do lugar
    e a autobiográfica (M7 e M8) continuam nos dois braços. O teste mede a legibilidade do P1 e do P2, não de todo o aprendizado.
- **Os pares por avaliador:** 12 pares de teste, sorteados dos 60 (4 de cada dono) pela rng do avaliador, mais 2 pares de atenção (seção
  6). A ordem também é sorteada.
- **Os avaliadores (LG-3, LG-6):**
  - os convidados do beta fechado (`docs/PLANO_V3_BETA.md`, o #944: 30 convidados, 20 ativos);
  - **N = 20 avaliadores válidos**, no mínimo;
  - se o beta tiver mais, até 30, decidido antes da coleta e não durante.
- **Privacidade:** cada avaliador recebe um id anônimo, e só as respostas são guardadas. Nada vai para serviço externo (LG-6).

## 4. As medidas

- **A primária:** a taxa de acerto de cada avaliador nos 12 pares de teste.
- **Ao lado (descritivo, não muda a leitura):**
  - a taxa de acerto por dono e por par;
  - a confiança média nos acertos e nos erros;
  - a relação entre o acerto de um par e a distância de variação total entre as ações de A e B na janela daquele par;
  - as respostas livres, agrupadas à mão, com a regra de agrupamento escrita antes de ler.

## 5. A análise (uma vez) e a regra de leitura

- **O teste:** a média das taxas por avaliador, com o IC95 pelo t (gl N − 1), usando `ic_t` de `digilab/metrics.py`. A unidade é o
  avaliador.
- **A margem:** δ = 0,10, PROPOSTA e SEM FONTE (LG-4). Ela é o menor acerto acima do acaso que importa para o produto: um em cada cinco
  jogadores a mais acertaria.
- **A regra, escrita antes:**

| o que sai | condição sobre o IC95 [l; u] da taxa média | a leitura |
|---|---|---|
| **visível** | l > 0,60 | o aprendizado aparece para quem olha. **H confirmada** |
| **invisível** | 0,40 ≤ l e u ≤ 0,60 | ninguém distingue os braços. **H refutada:** o efeito da A2 existe no motor e não aparece |
| **invertido** | u < 0,40 | as pessoas apontam o braço B como o que aprendeu |
| **indeterminado** | o resto | **H não confirmada nem refutada.** O N não basta para a margem |

- **O poder, SEM FONTE:** com um desvio-padrão de 0,15 entre avaliadores, o N = 20 dá meia-largura ≈ 0,07. "Visível" exige uma média
  perto de 0,67 ou mais. "Invisível" exige uma média entre ≈ 0,47 e 0,53, então "indeterminado" é um resultado provável e não é um
  fracasso do plano.
- **O que a leitura faz:**
  - **visível:** o efeito "muda" da A2 vale como diferencial de produto, nos limites do que foi medido;
  - **invisível:** o aprendizado precisa de um canal que o mostre (por exemplo, o painel DigiBrain) para ter valor de produto. Este plano
    não decide qual canal.

## 6. A atenção, a exclusão e a parada

- **Os pares de atenção:** 2 pares com uma instrução escrita no próprio par ("neste par, escolha o da direita").
- **A exclusão:** o avaliador que erra os 2 pares de atenção sai da análise, e o número de excluídos vai no resultado. Nenhuma outra
  exclusão é permitida.
- **A parada:** uma coleta só. Ela fecha ao atingir o N decidido ou no fim da semana do beta, o que vier primeiro. Ninguém olha as
  respostas antes do fecho. Se o N válido ficar abaixo de 20, a análise roda assim mesmo e o resultado diz o N.

## 7. O que refutaria e o que não refutaria

- **Refuta H:** "invisível".
- **Não refuta:** "indeterminado". Isso é falta de N, não evidência de que o efeito seja invisível.
- **Não é o objetivo:** um "visível" não diz que o pet entende nem que foi socializado (Searle 1980; Collins 1996, pp. 113-115). Diz só
  que pessoas distinguem as duas vidas.

## 8. O custo esperado

- **Os estímulos:** 120 vídeos de 60 s (60 pares). Gerá-los exige um roteiro de laboratório para B e a captura pelo Playwright
  (`web/app/playwright.capturas.config.ts` já captura telas). É implementação de ferramenta, sem mudança no jogo, estimada em uma sessão.
- **O formulário:** uma página servida localmente ou pelo servidor do beta, que guarda as respostas em
  `artifacts_v3_legibilidade/respostas.jsonl`.
- **O tempo de cada avaliador:** cerca de 20 min (14 pares, 2 vídeos de 60 s cada).
- **A máquina:** não é uma run de pesquisa. A geração dos vídeos é uma vez só, com até 4 processos.

## 9. As decisões para o Matheus

| id | o que decidir | recomendação | custo de errar |
|---|---|---|---|
| LG-1 | a forma do estímulo | **vídeo do jogo**, com o roteiro de laboratório para B. A alternativa é uma tira de ações por hora, mais barata | a tira mede leitura de gráfico, não o que o jogador vê; um "invisível" nela não diria nada sobre o jogo |
| LG-2 | a janela | **as últimas 10 h de jogo, em 60 s** | uma janela cedo demais mostra o pet antes de o aprendizado agir; a janela inteira de 3 dias deixa o vídeo longo demais para 14 pares |
| LG-3 | o N | **20 avaliadores válidos**, até 30 se o beta tiver | com menos de 20, "indeterminado" fica quase certo |
| LG-4 | a margem | **δ = 0,10**, SEM FONTE | uma margem menor pede um N que o beta não tem; uma maior chamaria de "invisível" um efeito que um em cada sete jogadores veria |
| LG-5 | a pergunta mostrada | **"Qual aprendeu?"**, com a frase da seção 3 ("aprende com o que acontece com ele", não "com o dono") | uma pergunta vaga ("qual é mais esperto?") mede outra coisa |
| LG-6 | onde coletar | **dentro do beta, numa página local ou do servidor do beta**, sem serviço externo | um formulário externo manda as respostas a terceiros e pede outro consentimento |

## 10. Referências

Todas VERIFICADAS (a skill `literatura-digilab`):
- Collins, H. M. (1996). Embedded or embodied? *Artificial Intelligence* 80, 99-117. `10.1016/0004-3702(96)00083-6`. Texto completo:
  pp. 106-108 (o erro sociológico) e pp. 113-115 (estímulo-resposta não é socialização).
- Searle, J. R. (1980). Minds, brains, and programs. *Behavioral and Brain Sciences* 3, 417-424. `10.1017/S0140525X00005756`.
- Anderson et al. (2019), `10.24963/ijcai.2019/184`: mede a compreensão de leigos (a skill, "Restrições de desenho").
- O número 0,0084 e as 9 de 15 medidas vêm do `artifacts_v3_ablacao_aprendizado/run/resultado.json` (PR #952).
