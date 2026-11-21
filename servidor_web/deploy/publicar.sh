#!/usr/bin/env bash
# Publica uma versão do servidor na VPS (CN5): o CI manda o pacote (git archive do commit) e chama este script pelo SSH.
#   sudo digilab-publicar /tmp/digilab-<commit>.tar.gz <commit>
# Desempacota em /opt/digilab/versoes/<commit>, instala as dependências de produção (npm ci, as versões exatas do package-lock), troca o
# link /opt/digilab/atual e reinicia. Se a /saude não responder em 30 s, volta o link para a versão de antes, reinicia e sai com erro.
# Guarda as 5 últimas versões. O banco não é tocado: as migrações rodam sozinhas na abertura (servidor_web/src/conta/banco.ts).
set -euo pipefail

pacote="${1:?o pacote .tar.gz}"
commit="${2:?o commit}"
[[ "$commit" =~ ^[0-9a-f]{7,40}$ ]] || { echo "commit inválido: $commit"; exit 1; }
[ "$(id -u)" -eq 0 ] || { echo "rode como root (sudo)"; exit 1; }

destino="/opt/digilab/versoes/$commit"
anterior="$(readlink -f /opt/digilab/atual 2>/dev/null || true)"

rm -rf "$destino.novo"
mkdir -p "$destino.novo"
tar -xzf "$pacote" -C "$destino.novo"
(cd "$destino.novo/servidor_web" && npm ci --omit=dev --no-audit --no-fund --ignore-scripts)
rm -rf "$destino"
mv "$destino.novo" "$destino"
ln -sfn "$destino" /opt/digilab/atual.novo
mv -T /opt/digilab/atual.novo /opt/digilab/atual
systemctl restart digilab-api.service

saude() {
  # o servidor só aceita o pedido com os cabeçalhos do túnel (--borda cloudflare); daqui de dentro, eles vão à mão
  curl -fsS -H "cf-ray: publicar" -H "cf-connecting-ip: 127.0.0.1" http://127.0.0.1:8766/saude | grep -q '"ok":true'
}
for _ in $(seq 1 30); do
  if saude; then
    echo "publicado: $commit"
    ls -1dt /opt/digilab/versoes/*/ | tail -n +6 | xargs -r rm -rf
    rm -f "$pacote"
    exit 0
  fi
  sleep 1
done

echo "a /saude não respondeu: voltando para $anterior"
if [ -n "$anterior" ] && [ "$anterior" != "$destino" ]; then
  ln -sfn "$anterior" /opt/digilab/atual.novo
  mv -T /opt/digilab/atual.novo /opt/digilab/atual
  systemctl restart digilab-api.service
fi
journalctl -u digilab-api.service -n 50 --no-pager || true
exit 1
