# TO-DO FUTURO — Interação do jogador e corpo do pet

**Status: IDEIA / PROPOSTO — etapa futura.** Registrado em 2026-09-30, a pedido do Matheus. Este documento não autoriza
implementação, mudança de arquitetura nem alteração dos experimentos atuais.

## Origem da ideia

Durante uma discussão de game design, o Matheus levantou uma possível limitação: o jogador talvez tenha poucas oportunidades
de criar situações nas quais o pet toma decisões e experimenta consequências.

Essa percepção ainda precisa ser confrontada com a implementação real. A questão é investigar se existem interações
suficientes para o jogador influenciar a experiência do pet e perceber mudanças no comportamento ao longo da convivência.

O Matheus sugeriu um ambiente visual inspirado em Digimon World Championship (Nintendo DS): pixel art, manipulação por
arrastar, áreas de cuidado e treinamento e alimentos colocados no cenário. A proposta é explorar um corpo situado nesse
ambiente, capaz de perceber objetos, movimentar-se e interagir com eles. A referência ao Championship é de apresentação e
interação; não pressupõe que o jogo original implemente aprendizagem durante a vida.

## Problema que a proposta busca enfrentar

Poucas interações podem limitar:

- as oportunidades de decisão do pet;
- a variedade de experiências produzidas pelo jogador;
- a percepção de autonomia e individualidade;
- a observação de aprendizagem, preferências e consequências;
- o interesse da convivência cotidiana.

Hipótese de design: um ambiente manipulável pode aumentar as oportunidades de interação e influência do jogador sobre o
comportamento do pet. Isso não garante aprendizagem nem personalidade emergente. A expansão também pode apenas acrescentar
tarefas repetitivas; esse risco deve ser avaliado.

Ligação com o que já foi medido (2026-09-30): a confirmatória refutou a hipótese central e o aprendido muda a política em
cerca de 0,02 bit, com fator explicável em 13–18% das decisões. A leitura registrada é que o ambiente tem poucas decisões em
que o dono importa. Esta proposta é uma das formas de criar essas decisões; a outra discutida foi uma política com lobos
(ver conversa de 2026-09-30, sem tarefa aberta). As duas só valem com o gate de divergência entre donos definido antes.

## Ideia central

O jogador modifica situações e oportunidades. O pet percebe o que consegue detectar, escolhe uma ação e enfrenta suas
consequências.

Exemplo: jogador coloca comida → pet percebe → aproxima-se ou ignora → consome ou abandona → ocorre uma consequência →
decisões posteriores podem mudar.

"Corpo físico" significa presença e capacidades no mundo simulado. Não exige modelo 3D, anatomia detalhada ou física
complexa; pode ser representado por sprites em um ambiente 2D.

## Abordagens candidatas

1. **Manipulação direta.** O jogador pega e transporta o pet ou os objetos. Questão futura: transportar o pet apenas muda
   sua posição ou também provoca alguma reação? Não definir antecipadamente efeitos sobre confiança, obediência ou
   personalidade.
2. **Convites e sinais.** O jogador aponta, chama, oferece ou demonstra. O pet pode aceitar, ignorar ou escolher outra ação.
   Distinguir uma mudança física imposta pelo jogador de uma ação voluntária do pet.
3. **Objetos e consequências.** Candidatos, não lista obrigatória:
   - comida: perceber, aproximar-se, investigar, consumir ou recusar;
   - bola: perseguir, tocar, empurrar, carregar e soltar;
   - obstáculo: contornar, tentar mover ou abandonar a tentativa;
   - equipamento: explorar, usar, treinar ou interromper;
   - área de descanso: procurar, entrar, descansar ou sair.
4. **Capacidades corporais.** Avaliar somente as necessárias às interações escolhidas: posição, orientação, alcance,
   movimento, colisão, manipulação de objetos, energia, fadiga, dano e recuperação. O que o jogador vê não precisa ser
   automaticamente conhecido pelo pet.

## Como investigar essa etapa futuramente

1. Auditar as interações e capacidades já existentes no repositório.
2. Identificar uma situação concreta em que falta uma decisão significativa.
3. Escolher uma interação pequena para experimentar.
4. Definir o que o jogador controla, o que o pet percebe e o que ele decide.
5. Introduzir apenas as capacidades corporais necessárias.
6. Comparar com a experiência atual.

Avaliar oportunidades de decisão, autonomia percebida, variedade de comportamento, clareza das consequências, repetição de
tarefas e custo computacional.

Separar explicitamente: evento registrado → experiência representada → aprendizagem → memória recuperada → mudança de
decisão. Um nível não demonstra automaticamente o seguinte.

## Possibilidades posteriores

A convivência com outros pets foi colocada como possibilidade mais distante.

O Matheus também propôs PvP assíncrono com um ghost do adversário. Alternativas a investigar:

- reprodução de ações gravadas;
- controlador aproximado por perfil;
- cópia congelada do controlador e do estado relevante, capaz de reagir durante uma nova luta.

Esse PvP é uma discussão futura própria; não é requisito para experimentar o ambiente corporal.

## Preservação da pesquisa

Esta proposta não reabre a hipótese confirmatória refutada sobre feedback coerente versus aleatório do dono.

Qualquer investigação futura deve respeitar os experimentos, gates, determinismo, event sourcing e paridade Python/web
vigentes, verificando seu estado no repositório. Relacionado: o stand-by do combate 1×1 em tempo real (CLAUDE.md,
Pendências conhecidas), que também parte do Championship e compartilha a mesma razão de espera.

**Próximo passo quando esta etapa for retomada:** discutir qual interação mínima acrescenta decisões significativas e
permite observar sua influência sobre o pet, antes de ampliar o ambiente.
