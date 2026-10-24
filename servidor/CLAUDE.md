# CLAUDE.md — o servidor local e a fala por LLM (`servidor/`)

Vale junto com o `CLAUDE.md` da raiz. O histórico da fala (as versões do prompt, as avaliações e os gates) está em
`docs/historico/claude/fala.md`.

## Regras

- **`digilab/` não importa nada daqui** (teste AST). O SDK `anthropic` só existe aqui. A fala livre fica em `digilab_fala_livre/`, também
  fora do pacote do pet.
- **A fala nunca entra no registro do pet.** Motivo, decisões, replay e artefatos ficam só com os templates. O comando pelo chat é a única
  ponte, por um catálogo fechado de ações, e o app valida de novo antes de gravar o evento de sempre.
- **Entrada da página não é confiável:** o servidor só aceita ação, fator e parâmetros do catálogo, e texto livre nunca chega ao prompt
  sem passar pela validação.
- **A chave da API** fica só no ambiente do servidor (`ANTHROPIC_API_KEY`), nunca na página.
- **Teto de gasto TOTAL** (`--limite-usd`, padrão US$ 2), acumulado em `servidor/gasto_fala.json`, fora do git: não zera ao reiniciar. Uma
  chamada que passaria do teto não é feita e cai no template. Modelo sem preço na tabela não liga.
- **Acesso remoto** (túnel): só com `--remoto`, que libera só as rotas do jogo e deixa a API paga desligada, salvo `--claude-remoto`. Sem
  `--remoto`, um pedido vindo por túnel leva 403. O túnel aponta sempre para `http://127.0.0.1:<porta>`. Os sprites do Digimon UP são autorizados pelo Matheus
  (`docs/UI_GUIDELINES.md`, seção 5.1); quem publica é ele.
- **A fala livre** só foi aprovada com o `gemma2:9b`, no Ollama local, e fica desligada por padrão.

## Comandos

```bash
python servidor/servidor_local.py                       # o jogo e a fala em http://localhost:8765/v1/web/dist/
python servidor/servidor_local.py --testar-alerta       # manda o e-mail de teste do alerta de gasto e sai
python experiments/avaliar_fala.py --livre --rodada 2   # avaliação da fala livre
```
