-- SPRITES_ACOES, missao M1 (docs/TAREFA_V3_SPRITES_ACOES.md, secoes 3.3 e 3.4): as receitas do lote 1 de um Digimon: o Comer e,
-- depois dele, Feliz, Sacudir, Chamar e Emburrar (M1 do lote 1, 2026-11-05).
-- Roda no Aseprite em linha de comando, chamada pelo tools/sprites_acoes/gerar_acoes.py, que le o tools/sprites_acoes/ancoras.json e
-- passa os numeros como --script-param. Parte do .aseprite do UP (camadas sombra e personagem; o arquivo do UP nao e alterado) e grava:
--   out_ase:              o .aseprite derivado, com as camadas sombra, personagem e comida e as tags Comer, Feliz, Sacudir, Chamar e Emburrar;
--   out_png / out_json:   o export das acoes (sombra e personagem), as 5 tags, json_array, frameTags, sem corte, na caixa do UP;
--   obj_png / obj_json:   o export so da camada comida (a carne e o farelo), so a tag Comer, nos mesmos ms.
-- Dois modos do Comer:
--   par:    alterna quadros do proprio UP com a boca aberta e fechada (a prova 2); a carne fica parada onde a boca a morde;
--   prova1: o Idle inclinado (cisalhamento: o topo anda, o pe fica) e achatado no pe, sem abrir a boca (a prova 1).
-- A carne e arte propria. Falha alto (error) se um pixel opaco cairia fora da caixa ou se o personagem passa do pe do Idle.
-- Numeros PROPOSTOS, SEM FONTE (os da prova 2 e da prova 1 do Agumon, 2026-11-04).
local p = app.params
local function req(k) local v = p[k]; if v == nil or v == "" then error("falta o parametro " .. k) end; return v end
local function nums(s) local t = {}; for x in s:gmatch("[^,]+") do t[#t + 1] = tonumber(x) end; return t end

local src = app.open(req("src"))
if not src then error("nao abriu " .. p.src) end
local W, H = src.width, src.height
local cw, ch = table.unpack(nums(req("caixa")))
if W ~= cw or H ~= ch then error(("caixa %dx%d, o ancoras diz %dx%d"):format(W, H, cw, ch)) end
local PE = tonumber(req("pe"))
local pers, somb
for _, l in ipairs(src.layers) do if l.name == "personagem" then pers = l elseif l.name == "sombra" then somb = l end end
if not (pers and somb) then error("sem camada personagem ou sombra") end
local A = app.pixelColor.rgbaA
local P = app.pixelColor.rgba

local function plano(layer, fi)
  if fi < 1 or fi > #src.frames then error("quadro fora do sprite: " .. fi) end
  local img = Image(W, H, ColorMode.RGB)
  local c = layer:cel(fi)
  if c then img:drawImage(c.image, c.position) end
  return img
end
local function caixa(img)
  local top, foot = H, -1
  for y = 0, H - 1 do for x = 0, W - 1 do
    if A(img:getPixel(x, y)) > 0 then if y < top then top = y end; if y > foot then foot = y end end
  end end
  if foot < 0 then error("quadro sem pixel opaco") end
  return top, foot
end
local function conferir_pe(img, onde)
  local _, foot = caixa(img)
  if foot > PE then error(("%s: o personagem passa do pe do Idle (linha %d > %d)"):format(onde, foot, PE)) end
end
local function ponto(img, x, y, cor, onde)
  if x < 0 or y < 0 or x >= W or y >= H then error(("%s: pixel opaco fora da caixa em (%d,%d)"):format(onde, x, y)) end
  img:drawPixel(x, y, cor)
end

-- a carne (arte propria): 12x8, o osso para a direita; a mordida corta colunas da esquerda
local cor = { k = P(58, 31, 20, 255), M = P(181, 83, 47, 255), H = P(233, 138, 92, 255), B = P(243, 234, 210, 255) }
local CARNE = { "..kkkk......", ".kMMMMk.....", "kMHMMMMk....", "kMMMMMMkkk.k", "kMMMMMMkBBBk", "kMMMMMMkkk.k", ".kMMMMk.....", "..kkkk......" }
local CORTE = { 0, 2, 4, 5 }
local function carne(img, mordidas, ox, oy, onde)
  local corte = CORTE[math.min(mordidas, 3) + 1]
  for r, linha in ipairs(CARNE) do for c = 1, #linha do
    local chv = linha:sub(c, c)
    if chv ~= "." and not ((c - 1) < corte and r >= 2 and r <= 7) then ponto(img, ox + c - 1, oy + r - 1, cor[chv], onde) end
  end end
  if corte > 0 then for r = 2, 7 do
    if CARNE[r]:sub(corte + 1, corte + 1) ~= "." then ponto(img, ox + corte, oy + r - 1, cor.k, onde) end
  end end
end
-- o farelo cai abaixo da carne no perfil; de frente a boca fica perto do chao, e ele cai ao lado da carne
local FRENTE = req("orientacao") == "frente"
local function farelo(img, ox, oy, onde)
  if FRENTE then
    ponto(img, ox - 2, oy + 3, cor.M, onde); ponto(img, ox - 1, oy + 5, cor.H, onde); ponto(img, ox - 3, oy + 7, cor.M, onde)
  else
    ponto(img, ox - 1, oy + 9, cor.M, onde); ponto(img, ox + 1, oy + 11, cor.H, onde); ponto(img, ox - 2, oy + 13, cor.M, onde)
  end
end

-- o cisalhamento e o achatamento ancorados no pe, vizinho mais proximo; falha se um pixel da linha usada sairia da caixa
local function inclinar(img, k, sy, onde)
  local top, foot = caixa(img)
  local out = Image(W, H, ColorMode.RGB)
  local alt = math.max(1, foot - top)
  for y = 0, H - 1 do
    local ys = math.floor(foot - (foot - y) / sy + 0.5)
    if ys >= 0 and ys < H then
      local dx = math.floor(k * (foot - ys) / alt + 0.5)
      for xs = 0, W - 1 do
        local px = img:getPixel(xs, ys)
        if A(px) > 0 then ponto(out, xs + dx, y, px, onde) end
      end
    end
  end
  return out, top, foot, alt
end

-- os quadros: { quadro do UP, ms, personagem (Image), quadro da sombra, mordidas acumuladas, farelo, carne x, carne y }
local Q = {}
local modo = req("modo")
local i0, n = table.unpack(nums(req("idle")))
local I0 = i0
local cx, cy
if modo == "par" then
  local c = nums(req("carne")); cx, cy = c[1], c[2]
  local mordidas = 0
  for item in req("seq"):gmatch("[^;]+") do
    local q, ms, mo, fa = table.unpack(nums(item))
    if mo == 1 then mordidas = mordidas + 1 end
    -- a sombra e a do 1o quadro do Idle, parada (secao 3.4): a do golpe pode descer abaixo do pe do Idle
    Q[#Q + 1] = { q = q, ms = ms, img = plano(pers, q), sombra = I0, mordidas = mordidas, farelo = fa == 1, x = cx, y = cy }
  end
elseif modo == "prova1" then
  local b = nums(req("boca"))
  -- ajustes por Digimon do ancoras.json, para caber na caixa: a fracao da inclinacao usada e o recuo da carne em x
  local escala = tonumber(req("escala_inclinacao"))
  local recuo = tonumber(req("recuo_carne"))
  local desl = nums(req("carne_desl"))
  if #desl ~= 2 then error("carne_desl precisa de dx,dy") end
  for item in req("tabela"):gmatch("[^;]+") do
    local off, k, sy, mo, fa, ms = table.unpack(nums(item))
    k = k * escala
    local q = i0 + (off % n)
    local img, top, foot, alt = inclinar(plano(pers, q), k, sy, "Idle " .. q)
    -- a boca do 1o quadro do Idle levada pela mesma inclinacao e achatamento
    local by = math.floor(foot - (foot - b[2]) * sy + 0.5)
    local bx = b[1] + math.floor(k * (foot - b[2]) / alt + 0.5)
    local x, y
    -- o canto da carne: o carne_deslocamento da orientacao (ancoras.json) a partir da boca, mais o recuo
    x, y = bx + desl[1] + recuo, by + desl[2]
    Q[#Q + 1] = { q = q, ms = ms, img = img, sombra = q, mordidas = mo, farelo = fa == 1, x = x, y = y }
  end
else
  error("modo desconhecido: " .. modo)
end
if #Q == 0 then error("sequencia vazia") end

-- as acoes do lote 1 (Feliz, Sacudir, Chamar, Emburrar): transformacoes de um quadro do Idle, ancoradas no pe dele (a ultima linha
-- opaca do quadro), vizinho mais proximo, sem desenho. Cada quadro: { deslocamento no Idle, dx, dy, sx, sy, k, ms, abaixar }:
--   dx, dy:  translacao em px (dy < 0 sobe; nunca desce abaixo do pe, o conferir_pe falha);
--   sx, sy:  escala em x (pelo meio da caixa do personagem) e em y (pelo pe); sy < 1 amassa;
--   k:       cisalhamento, o topo anda k px e o pe fica;
--   abaixar: px tirados da altura pelo pe (o Emburrar), somados ao sy.
-- A sombra e a do quadro do Idle de origem, sem mudanca (secao 3.4). Falha alto se um pixel opaco cairia fora da caixa.
local function transformar(img, dx, dy, sx, sy, k, abaixar, onde)
  local top, foot = caixa(img)
  local left, right = W, -1
  for y = top, foot do for x = 0, W - 1 do
    if A(img:getPixel(x, y)) > 0 then if x < left then left = x end; if x > right then right = x end end
  end end
  local alt = math.max(1, foot - top)
  local syf = sy * (alt - abaixar) / alt
  if syf <= 0 or sx <= 0 then error(onde .. ": escala invalida") end
  local cx = (left + right) / 2
  local function cis(ys) return k * (foot - ys) / alt end
  -- ida: todo pixel opaco tem de cair dentro da caixa
  for ys = top, foot do for xs = left, right do
    if A(img:getPixel(xs, ys)) > 0 then
      local x = math.floor(cx + (xs - cx) * sx + cis(ys) + dx + 0.5)
      local y = math.floor(foot - (foot - ys) * syf + dy + 0.5)
      if x < 0 or y < 0 or x >= W or y >= H then error(("%s: pixel opaco fora da caixa em (%d,%d)"):format(onde, x, y)) end
    end
  end end
  -- volta: cada pixel de saida pega o vizinho mais proximo da origem
  local out = Image(W, H, ColorMode.RGB)
  for y = 0, H - 1 do
    local ys = math.floor(foot - (foot - (y - dy)) / syf + 0.5)
    if ys >= top and ys <= foot then
      for x = 0, W - 1 do
        local xs = math.floor(cx + (x - dx - cis(ys) - cx) / sx + 0.5)
        if xs >= left and xs <= right then
          local px = img:getPixel(xs, ys)
          if A(px) > 0 then out:drawPixel(x, y, px) end
        end
      end
    end
  end
  return out
end

local LOTE1 = { "Feliz", "Sacudir", "Chamar", "Emburrar" }
local tags = { { nome = "Comer", de = 1, ate = #Q } }
for _, nome in ipairs(LOTE1) do
  local spec = req("acao_" .. nome)
  local de = #Q + 1
  for item in spec:gmatch("[^;]+") do
    local off, dx, dy, sx, sy, k, ms, abx = table.unpack(nums(item))
    if abx == nil then error(nome .. ": quadro sem os 8 campos: " .. item) end
    local q = i0 + (off % n)
    local onde = ("%s quadro %d (Idle %d)"):format(nome, #Q - de + 2, q)
    Q[#Q + 1] = { q = q, ms = ms, img = transformar(plano(pers, q), dx, dy, sx, sy, k, abx, onde), sombra = q, onde = onde }
  end
  if #Q < de then error(nome .. ": sem quadros") end
  tags[#tags + 1] = { nome = nome, de = de, ate = #Q }
end

local s = Sprite(W, H, ColorMode.RGB)
s.layers[1].name = "sombra"
local lp = s:newLayer(); lp.name = "personagem"
local lc = s:newLayer(); lc.name = "comida"
for _ = 2, #Q do s:newEmptyFrame() end
for i, f in ipairs(Q) do
  if f.ms ~= math.floor(f.ms) or f.ms <= 0 then error("ms invalido no quadro " .. i) end
  local onde = f.onde or ("Comer quadro %d (UP %d)"):format(i, f.q)
  conferir_pe(f.img, onde)
  local fr = s.frames[i]; fr.duration = f.ms / 1000
  s:newCel(s.layers[1], fr, plano(somb, f.sombra), Point(0, 0))
  s:newCel(lp, fr, f.img, Point(0, 0))
  if f.mordidas then   -- so o Comer tem objeto
    local c = Image(W, H, ColorMode.RGB)
    carne(c, f.mordidas, f.x, f.y, onde)
    if f.farelo then farelo(c, f.x, f.y, onde) end
    s:newCel(lc, fr, c, Point(0, 0))
  end
end
for _, t in ipairs(tags) do s:newTag(t.de, t.ate).name = t.nome end
s:saveAs(req("out_ase"))
src:close()

-- a acao: todas as tags; o objeto: so a tag Comer (as acoes do lote 1 nao tem objeto; o coracao, a nota e o tom ficam na vista)
local COLUNAS = 8
local function exportar(png, js, so_comida)
  s.layers[1].isVisible = not so_comida
  lp.isVisible = not so_comida
  lc.isVisible = so_comida
  app.command.ExportSpriteSheet {
    ui = false, askOverwrite = false, type = SpriteSheetType.ROWS, columns = COLUNAS,
    textureFilename = png, dataFilename = js, dataFormat = SpriteSheetDataFormat.JSON_ARRAY,
    filenameFormat = "{tag}_{tagframe00}", borderPadding = 0, shapePadding = 0, innerPadding = 0,
    trim = false, trimSprite = false, extrude = false, listLayers = false, listTags = true, listSlices = false,
    tag = so_comida and "Comer" or "",
  }
end
exportar(req("out_png"), req("out_json"), false)
-- o json do objeto listaria as 5 tags sobre so os quadros do Comer: tiram-se as outras (o .aseprite ja foi gravado com todas)
for i = #s.tags, 1, -1 do if s.tags[i].name ~= "Comer" then s:deleteTag(s.tags[i]) end end
exportar(req("obj_png"), req("obj_json"), true)
s:close()
print(("ok %s quadros=%d tags=%d"):format(modo, #Q, #tags))
