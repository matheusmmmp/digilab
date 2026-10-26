# Proposta — o diagnóstico depois da avaliação única do DigiBrain modular (2026-10-26)

Autor: Gerente (Claude Code, Opus 5.5), a pedido do Matheus em 2026-10-26. **Status: APROVADA pelo Matheus em 2026-10-26 ("Aprovo a proposta, com replay no piloto"); nada executado.** As vidas do piloto não
estão mais em disco (seção 8); onde rodar o replay espera uma decisão nova.

O pedido: "uma proposta de diagnóstico focada nos resultados, sem executar novas vidas", com o hábito ao contrário, a persistência sem
influência, o papel do sono e do cheiro e a correção futura da medida `visitas_vazias`; os resultados atuais preservados; a faixa
64xxx não volta; antes de qualquer execução ou reavaliação, as mudanças propostas, os testes, os critérios de parada e a nova faixa.

## 0. O que não muda

- **O resultado do #420 fica como está:** `docs/RESULTADO_V2_DIGIBRAIN_MODULAR_PROTOTIPO.md` e `artifacts_v2_digibrain_prototipo/avaliacao/`.
  Nenhum veredito é refeito. O G-MVP falhou, a memória e o incentivo passaram, o hábito saiu ao contrário, a persistência ficou
  inconclusiva por premissa.
- **A faixa 64101…64505 não volta.** Ela já está em `FAIXAS_RESERVADAS` como a avaliação única; a proposta acrescenta "usada; não volta"
  na linha dela.
- **Nenhuma vida nova nesta fase.** Toda evidência abaixo sai de `artifacts_v2_digibrain_prototipo/avaliacao/medidas.json` (5 400 vidas,
  no git) e da leitura do código. O Gerente fez a conta com um script só de leitura, fora do repositório; se a proposta for aprovada,
  ela é refeita pelo script da seção 3.1, com artefato em disco, antes de qualquer número entrar num documento de resultado.
- O A, o `engine.py`, a v12, a `web/` e os gabaritos não mudam.

## 1. O que os artefatos já mostram

Médias por vida, braço M3, 50 vidas por célula, salvo onde dito.

### 1.1 Parte da falha do G-MVP é da medida, não do pet

| célula (M3) | refeições por dia | privação | rações elegíveis | fechadas | taxa | vidas com cadeia |
|---|---|---|---|---|---|---|
| comedouro, atencioso | 6,47 | 0,087 | 109,6 | 21,0 | 0,196 | 0 % |
| perto, atencioso | 4,02 | 0,000 | 57,7 | 34,9 | 0,607 | 96 % |
| comedouro, aleatório | 2,55 | 0,465 | 20,7 | 14,1 | 0,686 | 96 % |
| longe, aleatório | 1,87 | 0,591 | 28,5 | 3,6 | 0,132 | 0 % |

- No comedouro do atencioso, o pet é o mais bem alimentado das 12 células, e mesmo assim nunca "fecha a cadeia". O dono põe ração tantas
  vezes que a maioria das rações elegíveis não pode ser comida na janela: o pet já comeu outra.
- A medida conta cada ração posta com o pet com fome. Com oferta abundante, o denominador cresce mais que o que um pet saciado come. É
  uma falha de validade da medida nessas células, não de aprendizagem.
- O comedouro do incoerente é a mesma vida (as células iguais). As duas células juntas são 2 das 6 que não fecham.

### 1.2 O longe é uma falha real

- No longe, a privação fica entre 0,42 e 0,62, e a taxa entre 0,04 e 0,13, com qualquer dono. Ali o pet de fato não acha a comida.
- A ração longe fica fora da visão (6 células) e só chega pelo cheiro. A espec não dá peso inato ao alvo do cheiro (a tabela 4.5 não tem
  a linha), e a intenção não existe para o cheiro (interpretação do D na 1a, aceita no plano). Então nem o inato nem a persistência
  ajudam onde mais fariam falta.

### 1.3 O sono não explica a diferença entre células

| braço | dormir (fração das decisões) |
|---|---|
| A11 | 0,459 |
| M0 | 0,474 |
| M3 | 0,469 |

- Dormir é quase metade das decisões em todo braço, inclusive no A11. É a necessidade do corpo, não uma escolha do modular.
- Nas células que fecham e nas que não fecham, a fração de dormir é a mesma (de 0,45 a 0,49). O sono encurta a janela de 8 decisões em
  todas, mas não separa as células.
- O reflexo do sono decide cerca de 19 % das decisões do M3 (255 por vida). Mexer no limiar do reflexo não está justificado por estes
  dados.

### 1.4 O hábito "ao contrário" está concentrado no longe, e a medida tem linha de base negativa

| lugar | índice "ganhou, fica" no M1 | no M2 | M2 − M1 |
|---|---|---|---|
| comedouro | −0,075 | −0,067 | +0,008 |
| perto | −0,100 | −0,096 | +0,004 |
| longe | −0,074 | −0,120 | −0,046 |

- O índice é negativo em todo braço, até no M0, que não tem hábito (−0,080). Depois de um alívio (comer, dormir), o pet repete menos a
  ação, porque a necessidade caiu. A medida mistura a saciedade com o hábito.
- O efeito contrário do P2 vem do longe; no comedouro e no perto ele é pequeno e no sentido previsto.
- No M2, caem as duas probabilidades da medida: repetir depois de alívio (de 0,255 para 0,220) e repetir sem alívio (de 0,338 para
  0,315).
- **Hipóteses,** a separar no diagnóstico:
  - **H-P2a, a medida:** um hábito é repetição pouco sensível ao resultado. Um índice de sensibilidade ao resultado pode cair justamente
    quando o hábito funciona.
  - **H-P2b, o crédito por opção no longe:** a opção longa soma o custo da caminhada e a refeição num r_n só, e o P2 credita a linha do
    comportamento com o z do começo da opção. No longe, esse z pode estar longe do contexto em que o alívio veio.
  - **H-P2c, os contextos:** os contextos da medida (o drive mais urgente, comida à vista, noite) não são as características z em que o
    H aprende.

### 1.5 A persistência não tem onde agir

- As intenções já acabam com a meta 93 % das vezes sem a persistência: 0,927 no M3-sp, 0,934 no M3. É um teto.
- Nenhuma intenção acabou por "sumiu" ou "desistiu", em nenhum braço. No M3, por vida: 81 acabam com a meta e 29 por troca.
- Só 2,28 % das decisões têm uma intenção em curso (diagnóstico da calibração). Os alvos de identidade fixa, a comida vista e a bola,
  costumam ser alcançados na primeira decisão.
- A persistência foi desenhada para alvos que pedem várias decisões. O caso típico é a ração longe pelo cheiro, que não tem intenção.

### 1.6 `visitas_vazias` conta toda visita como vazia

- No M3, há 32,2 visitas ao lugar lembrado por vida, e as 32,2 contam como vazias, em todo braço com memória.
- A visita é a decisão de explorar até o ponto; o comer vem numa decisão seguinte. A medida olha só a consequência da própria visita.
- Ela entra só nos descritivos, não em gate.

## 2. As mudanças propostas

Cada uma atrás de chave ou subchave desligada, com o G2 antes, como toda mecânica nova. Nenhuma é executada sem a sua aprovação.

| id | o quê | tipo | por quê | recomendação |
|---|---|---|---|---|
| **DX-1** | `visitas_vazias`: a visita conta como "achou" se a opção que começou com o `ponto` acaba comendo, na mesma opção ou na decisão seguinte | medida | 1.6 | **sim**: conserto de medida, sem efeito no pet |
| **DX-2** | o G-MVP por episódio de fome: um episódio começa quando a fome cruza 0,5 com ração posta e fecha se o pet come qualquer ração dentro da janela | medida | 1.1 | **sim, como secundária pré-registrada**; a primária fica a de hoje, para comparar com o #420 |
| **DX-3** | o peso inato do alvo do cheiro: uma linha `cheiro` na tabela 4.5 (comer e explorar), atrás da subchave `cheiro_inato` | mecanismo (espec) | 1.2 | **sim** |
| **DX-4** | a intenção no cheiro: a unidade de cheiro abre intenção com meta "comer qualquer comida", acaba por `N_desiste` sem a distância do cheiro cair; atrás da subchave `intencao_cheiro` | mecanismo (muda uma interpretação da 1a) | 1.2 e 1.5 | **sim**, porque é onde a persistência faria efeito |
| **DX-5** | o índice do hábito por ação, sem as ações de consumo (comer e dormir), ao lado do índice de hoje | medida | 1.4, H-P2a | **sim, como secundária**; o G-ABLA-P2 da reavaliação continua com o índice de hoje |
| **DX-6** | o crédito do P2 só com o z e o r da última consequência da opção (H-P2b) | mecanismo | 1.4 | **não agora**: só depois do diagnóstico de 3.2 apontar para o crédito |
| **DX-7** | o limiar do reflexo do sono (`lambda_sono`) | parâmetro | 1.3 | **não**: os dados não sustentam |

## 3. O diagnóstico, antes de qualquer mudança

### 3.1 Só com os artefatos que já existem (nenhuma execução)

- Refazer as tabelas da seção 1 por um script só de leitura (`experiments/diagnostico_avaliacao_digibrain.py`), com saída em
  `artifacts_v2_digibrain_prototipo/diagnostico/`, para cada número ter artefato.
- A leitura de código das hipóteses H-P2a a H-P2c e do caminho do cheiro até a unidade (`impulso.py`, `estado.py`, `plast.py`).

### 3.2 Com o replay das vidas já gravadas (precisa da sua decisão)

O registro de cada decisão (qual módulo decidiu, o z, o r da opção) não vai ao log; ele só sai rejogando a vida. **Rejogar as vidas
gravadas da 64xxx não é vida nova:** mesmo log, mesmo commit `5fc8943`, nenhuma semente nova, e o G1 confere que o replay refaz as
medidas gravadas bit a bit. Mesmo assim, é tocar a faixa da avaliação, e por isso fica para você decidir.
- **O que sairia:** o índice do hábito por ação e por contexto z (H-P2a, H-P2c); o r_n e o z das opções creditadas no longe (H-P2b); a
  fração de dormir dentro da janela de cada ração elegível; a distância do cheiro nas rações longe que não fecharam.
- **A alternativa sem tocar a 64xxx:** rejogar as vidas do piloto (63xxx, já gravadas). O piloto tem 576 vidas e os mesmos padrões nos
  números; serve para o diagnóstico, com menos poder.
- **Recomendação:** o piloto. Ele responde às mesmas perguntas, e a 64xxx fica intocada.

## 4. Os testes, antes de qualquer vida

- **Os de sempre, com toda chave nova desligada:** o G2 (as 196 vidas e o gabarito do MVP, byte a byte), o G1, o G-MECANISMO, os T-PONTO-1
  a 3, o G-INT, a G-RECEPTOR e o G-SEM-DIRECAO. O gabarito das vidas de hoje é gravado num commit próprio antes da mudança.
- **Novos, por mudança:**
  - DX-1: `T-VISITA-1`, uma sequência sintética em que a visita ao ponto é seguida de comer conta como achou, e a sem comer como vazia;
  - DX-2: `T-EPISODIO-1` e `-2`, oferta abundante com o pet saciado não abre episódio; um episódio fecha com qualquer ração comida;
  - DX-3: `T-CHEIRO-1`, com a subchave ligada, a unidade de cheiro tem peso inato positivo com fome e 0 sem cheiro; desligada, o termo é 0
    em toda decisão, com `raise` se não for;
  - DX-4: `T-PERS-CHEIRO-1` e `-2`, a intenção no cheiro dura enquanto a distância cai e acaba por `desistiu` depois de `N_desiste`
    decisões sem cair; desligada, nenhuma intenção no cheiro;
  - DX-5: `T-HABITO-1`, o índice sem consumo numa sequência sintética conhecida;
  - o oráculo T-CADEIA-1 tem de continuar passando com as mudanças ligadas.
- Os testes de medida usam só sequências sintéticas; os de mecanismo, só as sementes dos testes (101…505).

## 5. Os critérios de parada

- **No diagnóstico:** termina com um relato e para. Nenhuma mudança de código é feita na mesma etapa.
- **Na implementação:**
  - qualquer quebra do G2 ou do G1 para tudo, e se conserta antes de seguir;
  - se uma mudança exigir mexer no motor, no corpo, no mundo, no `engine.py` ou no A, para e volta a você;
  - se o oráculo T-CADEIA-1 falhar com uma mudança ligada, ela volta ao desenho.
- **Na calibração da nova faixa:** só os valores novos (o peso do cheiro, o `N_desiste` do cheiro) e os da lista da seção 6.1; no máximo
  três rodadas, o mesmo critério de fechamento; se não fechar, fica a melhor rodada, registrada como não fechada, como agora.
- **Na reavaliação:** roda uma vez, nas regras de hoje. Se o G-MVP primário falhar de novo, o resultado é registrado e o protótipo da
  etapa 1 para aí; o próximo passo vai a você, sem nova rodada de conserto automática.

## 6. A nova faixa

| faixa | uso | bases |
|---|---|---|
| **65101…65505** | a calibração do conserto e o piloto | calibração 65101 e 65202; piloto 65303, 65404 e 65505 |
| **66101…66505** | a reavaliação, uma vez | 66101, 66202, 66303, 66404 e 66505 |

As duas faixas estão livres (conferido em `experiments/bancada/faixas.py` e `experiments/configs/`). Elas entram em `FAIXAS_RESERVADAS`
com a sua aprovação, num commit antes de qualquer vida.

## 7. A ordem e o que depende de você

1. Aprovar esta proposta (ou parte dela) e decidir a seção 3.2: replay do piloto, da avaliação ou nenhum.
2. O diagnóstico (3.1 e 3.2), que termina num relato. **Nenhuma vida nova.**
3. Com o relato, você escolhe as mudanças (DX-1 a DX-6). Elas viram o adendo 3 do plano, com os testes, os critérios e as faixas,
   commitado antes de qualquer vida.
4. A implementação atrás das chaves, com o G2 antes.
5. A calibração e o piloto na 65xxx, a reavaliação na 66xxx; cada passo volta a você antes do seguinte.

**O custo de errar:**
- Aprovar DX-2 como primária mudaria o gate depois de ver os dados; por isso ela entra como secundária.
- Não fazer o diagnóstico antes e ir direto às mudanças pode consertar o hábito no lugar errado (DX-6).
- Usar a 64xxx no replay não é vida nova, mas é tocar a faixa da avaliação; o piloto evita isso.

## 8. As vidas do piloto não estão mais em disco (achado do Gerente, 2026-10-26)

- **O que aconteceu:** as vidas do piloto e da calibração ficavam fora do git, nas worktrees `v2-modular-piloto` e
  `v2-modular-calibracao`. Na limpeza do disco autorizada em 2026-10-26, o Gerente conferiu em cada worktree os arquivos modificados e
  não rastreados, mas não os ignorados pelo git; o `git worktree remove` apaga os ignorados junto. **As vidas das duas foram apagadas.**
  Os artefatos no git (o meta, as medidas, o resultado, o relato) estão intactos.
- **O que sobrou:** as vidas da avaliação única (5 400) e as da queda (336) existem só na worktree `v2-modular-avaliacao`, que não pode
  ser removida sem cópia.
- **Por que o replay do piloto não é imediato:** sem as vidas, não há log para rejogar. Elas podem ser **regeradas** a partir do commit
  do piloto (`c3a4d82`) com a mesma config: as vidas são determinísticas, e a conferência das 336 vidas da queda já mostrou isso. A
  prova de que a regeração é o mesmo piloto: o `medidas.json` refeito igual byte a byte ao que está no git. Não sai informação nova; mas
  é executar de novo as 576 vidas, e por isso vai ao Matheus.
