# TAREFA — Revisão de literatura para o experimento maior da V2 (Claude Science)

Para colar numa sessão do Claude Science. A sessão não tem acesso ao repositório (ele é privado), então o contexto necessário vem
abaixo. **Só literatura:** sem código, sem simulação e sem números do projeto.

---

## Quem pede e para quê

Projeto pessoal de pesquisa em vida artificial (não é trabalho acadêmico de pós-graduação; não associe a programa nenhum). O projeto
simula um pet virtual que aprende durante a vida. As runs são determinísticas e as predições são registradas **antes** de rodar.

Daqui a algumas semanas roda **uma única validação**. Quero saber, **antes** dela, o que a literatura prevê, para:
- registrar adendos se a teoria discordar das predições;
- ter onde ancorar a discussão depois.

## A pergunta do projeto

> Em que condições a plasticidade durante a vida produz vantagem adaptativa sobre as predisposições herdadas?

O desenho tem um agente com um **prior herdado**: um instinto fixo que escolhe, entre três frutas, pela preferência de nascença. Por cima
dele há um aprendiz. **Braços** (o que o aprendiz recebe):
- **P0:** só o herdado, sem aprendizado.
- **P1:** aprende pela consequência da própria ação (comer a fruta ruim piora o humor).
- **P2:** um professor **informa** qual fruta faz bem ou mal (informação certa), e o aprendizado continua pela consequência.
- **P2e:** o professor informa errado.
- **P2a:** a mesma quantidade de informação certa, mas em momentos desacoplados da oferta.
- **P3:** o professor dá **reforço explícito** (elogio ou bronca depois da escolha), sabendo o mesmo efeito real que o professor do P2.

**Ambientes:**
- **casado:** a fruta preferida de nascença é a boa;
- **descasado:** a preferida de nascença é a ruim;
- **mutável:** começa casado e inverte no meio da vida.

**Predições registradas** (resumo):
1. No casado, P0 vence: aprender só custa (exploração, deriva).
2. No descasado e no mutável, P1 vence P0, se a vida for longa o bastante.
3. P2 chega lá com menos consequências experimentadas que P1.
4. P2e piora no começo e se recupera quando a consequência refuta a informação.
5. P3 fica perto de P0 (equivalência): reforço explícito sobre a escolha ensina pouco além do que a consequência já ensina.

**Ablações** dentro do mesmo agente:
- memória de episódios;
- arbitragem entre a necessidade do agente e um pedido do professor;
- sinal de reforço escalar × separado por canal (fome, energia, humor).

## O que quero (em ordem de prioridade)

### 1. Teoria do valor do aprendizado × comportamento fixo

O que a ecologia comportamental e a biologia evolutiva preveem sobre **quando aprender compensa**, em função da regularidade do
ambiente, dentro da vida e entre gerações, do custo do aprendizado e da duração da vida. Para cada uma das predições 1, 2 e 4, diga se a
teoria **concorda, discorda ou não fala**, com a passagem que sustenta.

Pistas, **todas por verificar**:
- Stephens (1991), Behavioral Ecology, sobre mudança, regularidade e o valor do aprendizado;
- Dunlap e Stephens (2009), PNAS, evolução experimental do aprendizado e da preferência não aprendida em *Drosophila*;
- Mery e Kawecki, sobre o custo do aprendizado;
- DeWitt, Sih e Wilson (1998), TREE, sobre os custos e limites da plasticidade;
- Snell-Rood (2013), Animal Behaviour, uma revisão da plasticidade comportamental.

Procure também os modelos formais mais recentes que citam esses trabalhos.

### 2. Informação social × aprendizado individual × reforço do professor

O que se sabe sobre:
- quando um agente deveria confiar em informação de outro e quando deveria testar ele mesmo (por exemplo, a literatura de estratégias de
  aprendizado social e de "copiar quando incerto");
- o custo de informação errada e a recuperação dela (a predição 4);
- a diferença entre **informar antes** da escolha e **reforçar depois** dela, em animais, humanos e agentes artificiais (as predições 3
  e 5).

Na parte artificial, o projeto já usa TAMER, COACH (MacGlashan et al., arXiv:1701.06049) e Thomaz e Breazeal (2008, Artificial
Intelligence): procure o que **contradiz ou estende** esses três, e não repita.

### 3. Precedentes do desenho

Algum trabalho cruza, num **mesmo agente**, as três coisas: plasticidade × regularidade do ambiente (casado/descasado/mutável) × canal do
professor (informação × reforço × só consequência)?

Os precedentes que o projeto já conhece, e com os quais **não** pode alegar novidade, são três:
- separar instinto de aprendido, em Hallawa et al., GECCO 2021 Companion, `10.1145/3449726.3459475`;
- herdar o prior, pelo efeito Baldwin: Hinton e Nowlan (1987) e Fernando et al. (2018), `10.1145/3205651.3205763`;
- comportamento "ensinado, não roteirizado", que já está em Black & White (2001).

Diga explicitamente se não achou, e com que buscas. Ausência de resultado é evidência fraca, e quero o registro.

### 4. Medidas e tamanhos de efeito de referência

Quando houver dados experimentais (animais ou agentes) com os mesmos contrastes, extraia o **tamanho de efeito** e a duração em que ele
apareceu. Isso me ajuda a julgar se a margem de equivalência e a duração de vida do projeto são razoáveis.

## Regras

- **Só referência verificada.** Para cada item: DOI (ou arXiv) conferido, autores, ano e veículo. Marque se você leu o **texto completo**
  ou só o resumo. Não cite o que não conseguiu localizar; liste à parte como "não localizado".
- **Preprint × revisado por pares:** marque qual é.
- **Não reproduza** trechos longos; uma frase curta entre aspas por fonte, no máximo.
- **Não alegue novidade** para o projeto. Se algo parecer inédito, escreva "não localizado nas buscas X, Y, Z".
- Fonte de fã, wiki ou blog é pista, nunca evidência.
- Separe sempre "a fonte diz" de "minha leitura".

## Entrega

1. **Uma tabela**, uma linha por referência, com as colunas: referência, tipo (par ou cinza), DOI ou id, texto lido (completo ou resumo),
   o que sustenta (uma frase), a que predição ou ablação se liga, e se concorda, discorda ou não fala.
2. **Uma síntese de uma página**, por predição, com o que a teoria prevê para casado, descasado e mutável.
3. **Divergências.** Liste onde a literatura discorda das predições 1–5 ou sugere outra medida, com a força da evidência. Elas viram
   candidatas a adendo.
4. **Lacunas.** O que não foi achado e as buscas feitas.
5. **Um BibTeX** só com as referências verificadas.
