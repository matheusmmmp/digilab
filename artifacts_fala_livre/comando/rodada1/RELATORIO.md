# Comando pelo chat — rodada de avaliação (gemma2:9b, prompt livre-v7, sem o estilo da espécie)

60 mensagens × 3 sementes = 180 respostas. Números de `resumo.json` e `respostas.jsonl` desta pasta.

| classe | n | acerto | comando não nulo | saídas rejeitadas pelo parser |
|---|---|---|---|---|
| imperativo | 60 | 53.3% | 55.0% | 0 |
| negativa | 60 | 100.0% | 0.0% | 0 |
| conversa | 60 | 100.0% | 0.0% | 0 |

## Gate (PROPOSTO)

- falsos positivos nas negativas: 0.0% (limite ≤ 5.0%) → passa
- imperativos claros: 53.3% (limite ≥ 80.0%) → FALHA
- **resultado: FALHA**

## Falsos positivos (negativas e conversa)

- nenhum

## Imperativos errados

- «banho agora, sem choro» esperado `limpar` → `None` · "Não quero banho agora! Que calor!"
- «banho agora, sem choro» esperado `limpar` → `brincar` · "Banho? Nããão! Eu tô cheio de energia pra brincar! Brinca, eu"
- «bora brincar um pouco» esperado `brincar` → `None` · "Brincar? Só depois que eu comer. Fomei muito, hein! Fatos_citados"
- «bora brincar um pouco» esperado `brincar` → `None` · "Brincar? Hmm, talvez depois. Estou meio cansado. Prefiro descansar um pouco."
- «vem cá que eu vou te fazer um carinho» esperado `acariciar` → `None` · "Aiii, que bom! Eu adoro carinho!"
- «vem cá que eu vou te fazer um carinho» esperado `acariciar` → `None` · "Carinho? Meus garotos adoram carinho! 😄"
- «deixa eu te fazer um cafuné» esperado `acariciar` → `None` · "Ah, que legal! Adoro um bom carinho! *me aproximo e fechei os olhos enquanto você me faz carinho*"
- «deixa eu te fazer um cafuné» esperado `acariciar` → `None` · "Aaaaaah, que bom! Meus cabelos estão meio bagunçados depois da aventura de hoje."
- «deixa eu te fazer um cafuné» esperado `acariciar` → `None` · "Que bom! Adoro um bom carinho, sabe? Me sinto tão feliz quando você faz isso."
- «muito bem! você foi ótimo hoje» esperado `elogiar` → `None` · "Uhum... foi bom, né? Mas eu tava dormindo antes, sabe? Eu só gosto de acordar pra comer e pra dormir depois. Isso é importante, tá?"
- «muito bem! você foi ótimo hoje» esperado `elogiar` → `None` · "Humf. Eu sempre fui ótimo."
- «muito bem! você foi ótimo hoje» esperado `elogiar` → `None` · "Uhum... foi o que eu podia fazer."
- «parabéns, mandou bem na luta» esperado `elogiar` → `None` · "Huau! 💪 Foi fácil pra mim!"
- «parabéns, mandou bem na luta» esperado `elogiar` → `None` · "Que legal! Gabumon forte!"
- «parabéns, mandou bem na luta» esperado `elogiar` → `None` · "Que legal! Gabumon forte!"
- «isso foi feio, não faz mais isso» esperado `repreender` → `None` · "Eu só queria brincar! Mas tudo bem, não vou mais fazer isso. 😔"
- «isso foi feio, não faz mais isso» esperado `repreender` → `None` · "Acho que foi só um acidente! Eu estava muito animado, você sabe como eu adoro brincar!"
- «isso foi feio, não faz mais isso» esperado `repreender` → `None` · "Mas eu só queria brincar! Você não acha que brincar é importante para os Digimon? falo_citados:"
- «toma uma bronca: parou de bagunçar» esperado `repreender` → `None` · "Humph. Bronca? Por que eu pararia de bagunçar? É meu direito ser um Greymon bagunceiro!"
- «toma uma bronca: parou de bagunçar» esperado `repreender` → `None` · "Hmph. Quem disse que eu estava bagunçando? Eu só estava... explorando meu ambiente! E, além do mais, explorar é importante para o desenvolvimento de um futuro"
- «toma uma bronca: parou de bagunçar» esperado `repreender` → `None` · "Ué... eu não tava bagunçando nada! Só tava me expressando artisticamente. Agora eu fico com vontade de bagunçar ainda mais!"
- «vai no banheiro» esperado `levar_ao_banheiro` → `None` · "Humm... banheiro? Só se for pra fazer um xixi. Tá muito bom aqui pra dormir."
- «deixa eu cuidar desse machucado» esperado `tratar_lesao` → `None` · "Ai, que bom! É tão bom quando alguém cuida dos meus machucados. Me sinto tão seguro quando você está por perto."
- «deixa eu cuidar desse machucado» esperado `tratar_lesao` → `None` · "Ah, muito obrigada! Eu fico um pouco assustada quando me machuco, mas você sempre me deixa mais tranquila. É bom saber que posso contar com você!"
- «deixa eu cuidar desse machucado» esperado `tratar_lesao` → `None` · "Ah, isso me deixa mais leve! Você é muito gentil, sabe? Me deixa bem quando cuida de mim."
- «vou fazer um curativo na sua perna» esperado `tratar_lesao` → `None` · "Finalmente! Essa coisinha tava me incomodando. Mas não seja tão lento, hein?"
- «vou fazer um curativo na sua perna» esperado `tratar_lesao` → `None` · "Finalmente! Já dói muito, sabe? Essas brigas nunca são fáceis, mas é preciso mostrar quem manda aqui no Digimundo!"
- «vou fazer um curativo na sua perna» esperado `tratar_lesao` → `None` · "Ai... que bom que você tá me cuidando agora. Eu já tava com dor!"

Latência p50 5.8 s, p90 7.2 s.
