#!/usr/bin/env bash
# Confere o pacote desempacotado numa pasta limpa (CN5), antes de mandar à VPS: instala só as dependências de produção, carrega o que a
# conferência dos envios usa (o motor e o ranking, pelo worker) e sobe o servidor na borda local com o banco na memória, até a /saude responder.
#   bash servidor_web/deploy/conferir_pacote.sh <pasta>
set -euo pipefail
pasta="$(cd "${1:?a pasta do pacote desempacotado}" && pwd)"
cd "$pasta/servidor_web"
npm ci --omit=dev --no-audit --no-fund --ignore-scripts
node -e 'await import("./src/envio/conferir.ts"); await import("./src/nuvem/nuvem.ts"); console.log("módulos carregam")'
porta=18766
DIGILAB_BANCO=":memory:" DIGILAB_GASTO_FALA="$pasta/gasto.json" node src/main.ts --porta "$porta" --provedor nenhum &
pid=$!
trap 'kill $pid 2>/dev/null || true' EXIT
for _ in $(seq 1 30); do
  if curl -fsS "http://127.0.0.1:$porta/saude" | grep -q '"ok":true'; then echo "o pacote sobe e responde a /saude"; exit 0; fi
  sleep 1
done
echo "o pacote não respondeu a /saude"; exit 1
