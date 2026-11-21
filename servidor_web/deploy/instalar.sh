#!/usr/bin/env bash
# Prepara a VPS uma vez (CN5, docs/infra/DEPLOY_CN5.md, seção 4): Ubuntu 24.04 LTS no Lightsail, como root.
#   sudo LITESTREAM_SHA256=<o sha256 do .deb, conferido na página do release> bash instalar.sh
# Instala o Node (versão fixa, conferida pelo SHASUMS256 do nodejs.org), o Litestream (versão fixa, conferida pelo sha256 dado) e o
# cloudflared (pelo repositório apt assinado da Cloudflare); cria o usuário digilab, as pastas e as unidades do systemd; fecha o firewall
# em tudo menos o SSH. Não põe segredo nenhum: os /etc/digilab/*.env são preenchidos à mão, pelos modelos *.env.exemplo.
set -euo pipefail

NODE_VERSAO="24.19.0"          # a mesma do desenvolvimento (PROPOSTO)
LITESTREAM_VERSAO="0.3.13"     # PROPOSTO: a última da linha 0.3, que a litestream.yml usa
AQUI="$(cd "$(dirname "$0")" && pwd)"

[ "$(id -u)" -eq 0 ] || { echo "rode como root (sudo)"; exit 1; }
[ -n "${LITESTREAM_SHA256:-}" ] || { echo "falta LITESTREAM_SHA256 (o sha256 do litestream-v${LITESTREAM_VERSAO}-linux-amd64.deb)"; exit 1; }
[ "$(dpkg --print-architecture)" = "amd64" ] || { echo "esta receita é para amd64"; exit 1; }

apt-get update
apt-get install -y --no-install-recommends ca-certificates curl gnupg ufw sqlite3 xz-utils

# o Node, conferido pelo SHASUMS256.txt do próprio nodejs.org
tmp="$(mktemp -d)"
arq="node-v${NODE_VERSAO}-linux-x64.tar.xz"
curl -fsSLo "$tmp/$arq" "https://nodejs.org/dist/v${NODE_VERSAO}/$arq"
curl -fsSLo "$tmp/SHASUMS256.txt" "https://nodejs.org/dist/v${NODE_VERSAO}/SHASUMS256.txt"
(cd "$tmp" && grep " $arq\$" SHASUMS256.txt | sha256sum -c -)
tar -xJf "$tmp/$arq" -C /usr/local --strip-components=1 --exclude CHANGELOG.md --exclude LICENSE --exclude README.md
node --version | grep -qx "v${NODE_VERSAO}"

# o Litestream, conferido pelo sha256 dado
deb="litestream-v${LITESTREAM_VERSAO}-linux-amd64.deb"
curl -fsSLo "$tmp/$deb" "https://github.com/benbjohnson/litestream/releases/download/v${LITESTREAM_VERSAO}/$deb"
echo "${LITESTREAM_SHA256}  $tmp/$deb" | sha256sum -c -
dpkg -i "$tmp/$deb"
[ -x /usr/local/bin/litestream ] || ln -sf "$(command -v litestream)" /usr/local/bin/litestream

# o cloudflared, pelo repositório apt da Cloudflare (a chave dela)
mkdir -p --mode=0755 /usr/share/keyrings
curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg -o /usr/share/keyrings/cloudflare-main.gpg
echo "deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared any main" > /etc/apt/sources.list.d/cloudflared.list
apt-get update
apt-get install -y cloudflared
rm -rf "$tmp"

# o usuário e as pastas: o código em /opt/digilab (só leitura para o serviço), os dados em /var/lib/digilab
id digilab >/dev/null 2>&1 || useradd --system --home /var/lib/digilab --shell /usr/sbin/nologin digilab
install -d -o digilab -g digilab -m 0750 /var/lib/digilab
install -d -o root -g root -m 0755 /opt/digilab /opt/digilab/versoes
install -d -o root -g digilab -m 0750 /etc/digilab
for e in api litestream; do
  [ -f "/etc/digilab/$e.env" ] || install -o root -g digilab -m 0640 "$AQUI/$e.env.exemplo" "/etc/digilab/$e.env"
done
install -o root -g root -m 0644 "$AQUI/litestream.yml" /etc/litestream.yml
install -o root -g root -m 0644 "$AQUI/digilab-api.service" "$AQUI/litestream.service" /etc/systemd/system/
install -o root -g root -m 0755 "$AQUI/publicar.sh" /usr/local/sbin/digilab-publicar
systemctl daemon-reload
systemctl enable litestream.service digilab-api.service

# o firewall: só o SSH entra; a API sai pelo túnel, de dentro para fora (feche também o 80 e o 443 no firewall do Lightsail)
ufw default deny incoming
ufw default allow outgoing
ufw allow OpenSSH
ufw --force enable

echo "pronto. Falta: preencher /etc/digilab/api.env e litestream.env; ligar o túnel (cloudflared service install <token>); o primeiro deploy."
