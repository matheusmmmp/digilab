#!/usr/bin/env bash
# Monta a pasta do Cloudflare Pages (CN5, RC-6): o build do jogo em /jogo/ e, na raiz, só um aviso que leva ao jogo, até a página de
# entrada (a tela 6, RC-5) existir em código, de outra sessão. Nada da pasta Assets: os assets ficam no R2 (assets.<domínio>).
# Os arquivos que só valem na raiz da origem saem do /jogo/ para a raiz (PI-6, D-CONTA-233): o robots.txt, o .well-known/tdmrep.json
# (o aviso de mineração reservada) e o _headers do Pages (o cabeçalho tdm-reservation em tudo). Faltou um deles no build: falha.
#   bash servidor_web/deploy/montar_site.sh web/dist /tmp/site
set -euo pipefail
build="${1:?a pasta do build do jogo}"
site="${2:?a pasta de saída}"
[ -f "$build/index.html" ] || { echo "sem $build/index.html: rode o npm run build"; exit 1; }
rm -rf "$site"
mkdir -p "$site/jogo"
cp -R "$build"/. "$site/jogo/"
for raiz in robots.txt .well-known/tdmrep.json _headers; do
  [ -f "$site/jogo/$raiz" ] || { echo "sem $raiz no build: rode node servidor_web/scripts/gerar_robots.ts e o npm run build"; exit 1; }
  mkdir -p "$(dirname "$site/$raiz")"
  mv "$site/jogo/$raiz" "$site/$raiz"
done
rmdir "$site/jogo/.well-known"
cat > "$site/index.html" <<'HTML'
<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="tdm-reservation" content="1">
<meta http-equiv="refresh" content="0; url=jogo/">
<title>Digilab</title>
</head>
<body><p><a href="jogo/">Abrir o Digilab</a></p></body>
</html>
HTML
n="$(find "$site" -type f | wc -l)"
[ "$n" -le 20000 ] || { echo "o Pages aceita até 20 000 arquivos: $n"; exit 1; }
echo "site: $site ($n arquivos)"
