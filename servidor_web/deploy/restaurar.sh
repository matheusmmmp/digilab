#!/usr/bin/env bash
# Restaura o banco a partir da cópia do Litestream no R2 (CN5, docs/infra/DEPLOY_CN5.md, seção 5).
#   sudo bash restaurar.sh ensaio      # restaura numa cópia ao lado (/var/lib/digilab/ensaio.sqlite) e confere; não para nada
#   sudo bash restaurar.sh valer       # para o servidor e o Litestream, guarda o banco de agora ao lado, restaura no lugar e religa
set -euo pipefail
modo="${1:?ensaio ou valer}"
set -a; . /etc/digilab/litestream.env; set +a
banco=/var/lib/digilab/conta.sqlite

case "$modo" in
  ensaio)
    alvo=/var/lib/digilab/ensaio.sqlite
    rm -f "$alvo"
    litestream restore -config /etc/litestream.yml -o "$alvo" "$banco"
    sqlite3 "$alvo" "PRAGMA integrity_check; PRAGMA user_version; SELECT count(*) FROM contas;"
    echo "ensaio: $alvo restaurado (compare o user_version e as contas com o banco de agora)"
    ;;
  valer)
    systemctl stop digilab-api.service litestream.service
    [ -f "$banco" ] && mv "$banco" "$banco.antes-$(date -u +%Y%m%dT%H%M%SZ)"
    rm -f "$banco-wal" "$banco-shm"
    litestream restore -config /etc/litestream.yml -o "$banco" "$banco"
    chown digilab:digilab "$banco"
    sqlite3 "$banco" "PRAGMA integrity_check;"
    systemctl start litestream.service digilab-api.service
    echo "restaurado e religado"
    ;;
  *) echo "modo desconhecido: $modo (ensaio ou valer)"; exit 1 ;;
esac
