/* Campanha (desenho CampMapa; porte do HTML): uma ilha do UP por lugar, nuvem nos trancados, marcador com o NPC
   em 1x, caminho entre os lugares, o pet no proximo desafio; cartao do lugar com os rivais, a licao, os stats e
   o historico de tentativas (contado do registro). A luta acontece no palco desta aba. */
import { useEffect } from "preact/hooks";
import { NOME_V2, NPC, STATS, chaveSprite, nomeEstagio, nomeEstiloNPC, type Lugar, type Motor } from "../../../motor/index.ts";
import { imagemAtlas, useAtlas } from "../../atlas.ts";
import { fundoDeco } from "../../componentes/Deco.tsx";
import { Peca, RetratoRival } from "../../componentes/Imagens.tsx";
import { FAIXA_LUGAR, FUNDO_NPC, molduraArena, urlDeco, useDecoracao } from "../../decoracao.ts";
import { useJogo } from "../../jogo.ts";
import { LUTA, campAtual, escolherDesafio, escolherLugar, lutarAnimado, lutasDoRegistro, previa, tentativas, useLuta } from "../../luta.ts";
import { ENDERECO_LUTA } from "../../rotas.ts";
import { useDesktop } from "../../desktop.ts";

/* coordenadas da prancha CampMapa (mapa de 390 x 420), em % para acompanhar a largura: ilha 150 px, centro do lugar
   (trilho, plaquinha, marcador do pet) e o pad embaixo */
const W0 = 390, H0 = 420;
export const ILHA = [{ peca: "ilha_campina", x: 6, y: 231, cx: 81, cy: 316, placa: 389 }, { peca: "ilha_torre", x: 120, y: 118, cx: 195, cy: 197, placa: 265 },
  { peca: "ilha_cidadela", x: 230, y: 6, cx: 305, cy: 91, placa: 163 }];
/* pets v5 (evolucao canonica): quatro lugares em zigue-zague, com a Montanha Espiral no alto */
export const ILHA_V5 = [{ peca: "ilha_campina", x: 6, y: 240, cx: 81, cy: 325, placa: 390 }, { peca: "ilha_torre", x: 234, y: 160, cx: 309, cy: 245, placa: 308 },
  { peca: "ilha_cidadela", x: 6, y: 80, cx: 81, cy: 165, placa: 228 }, { peca: "ilha_espiral", x: 234, y: 0, cx: 309, cy: 85, placa: 150 }];
const ilhasDe = (m: Motor) => m.lugares.length === ILHA_V5.length ? ILHA_V5 : ILHA;
/** nivel pedido pelo lugar (Mega na Montanha Espiral) e se o pet ainda esta abaixo dele */
const nivelDoLugar = (L: Lugar): string => NIVEL[L.est] ?? L.sugerido;
const cedoPara = (m: Motor, L: Lugar): boolean => ORDEM_EST.indexOf(m.forma.est) < ORDEM_EST.indexOf(L.est);
const px = (x: number) => `${x / W0 * 100}%`, py = (y: number) => `${y / H0 * 100}%`;
const ORDEM_EST = ["ovo", "bebe", "crianca", "adolescente", "adulto", "mega"];
const NIVEL: Record<string, string> = { crianca: "Rookie", adolescente: "Champion", adulto: "Ultimate", mega: "Mega" };

function Mapa() {
  const { motor: m } = useJogo(), a = useAtlas(), luta = useLuta(), sel = campAtual(m);
  if (a.tipo !== "ok") return <div class="mapa-ilhas"><p class="dl-apoio">Carregando o mapa…</p></div>;
  const LUGARES = m.lugares, ILHAS = ilhasDe(m), vencidos = LUGARES.filter((_, i) => m.lugarVencido(i)).length, url = (n: string) => imagemAtlas(a, n).url;
  const aqui = ILHAS[Math.min(vencidos, LUGARES.length - 1)], pet = imagemAtlas(a, chaveSprite(m.forma));
  return (
    <div class="mapa-ilhas" role="group" aria-label="Mapa da campanha">
      <svg class="mapa-caminho" viewBox={`0 0 ${W0} ${H0}`} preserveAspectRatio="none" aria-hidden="true">
        {LUGARES.slice(1).map((_, i) => {
          const A = ILHAS[i], Bq = ILHAS[i + 1], feito = i < vencidos;
          return <g key={i}><line x1={A.cx} y1={A.cy} x2={Bq.cx} y2={Bq.cy} class="trilho-sombra" />
            <line x1={A.cx} y1={A.cy} x2={Bq.cx} y2={Bq.cy} class={feito ? "trilho feito" : "trilho"} /></g>;
        })}
      </svg>
      {LUGARES.map((L, i) => {
        const vit = L.rivais.reduce((n, k) => n + m.campanha[k], 0), aberto = m.desafioAberto(L.rivais[0]), eSel = NPC[sel]!.lug === i, I = ILHAS[i];
        const st = vit ? `vencido ${vit}×` : aberto ? "aberto" : "trancado";
        return [
          <img key={"p" + i} class="mapa-pad" src={url(i === LUGARES.length - 1 ? "marcador_chefe" : vit ? "marcador_3" : "marcador_1")} alt="" style={{ left: px(I.cx - 34), top: py(I.placa - 29) }} />,
          <img key={"i" + i} class={`ilha${aberto ? "" : " fechada"}`} src={url(I.peca)} alt="" style={{ left: px(I.x), top: py(I.y) }} />,
          !aberto && <img key={"n" + i} class="nuvem" src={url("nuvem")} alt="" style={{ left: px(I.x - 12), top: py(I.y - 6) }} />,
          <button key={"b" + i} type="button" class={`lugar${eSel ? " sel" : ""}${aberto ? "" : " bloq"}`} disabled={luta.lutando}
            style={{ left: px(I.cx - 70), top: py(I.placa) }} aria-label={`${i + 1}. ${L.nome}: ${st}`} aria-current={eSel ? "true" : undefined} onClick={() => escolherLugar(i)}>
            <span class="lugar-placa">{L.nome}</span>
            {vit ? <span class="lugar-tag lugar-tag--ok">VENCIDO</span> : aberto ? <span class="lugar-tag">{nivelDoLugar(L).toUpperCase()}</span>
              : <span class="lugar-tag lugar-tag--tranca"><Peca nome="icone_cadeado" />trancado</span>}
          </button>,
        ];
      })}
      {/* seu pet: no proximo desafio (ou no primeiro lugar, se nada foi vencido) */}
      <span class="pet-mapa-ilha" style={{ left: px(aqui.cx - 26), top: py(aqui.cy - 39) }} aria-hidden="true">
        <span class="pet-mapa-circ"><img class="dl-pix" src={pet.url} width={pet.w} height={pet.h} alt="" /></span><span class="pet-mapa-seta" /></span>
    </div>
  );
}
function Detalhe() {
  const { motor: m } = useJogo(), a = useAtlas(), luta = useLuta(), sel = campAtual(m), Li = NPC[sel]!.lug, LUGARES = m.lugares, L = LUGARES[Li], aberto = m.desafioAberto(L.rivais[0]);
  const est = m.forma.est, cedo = cedoPara(m, L), podeLutar = est !== "bebe";
  const prox = LUGARES[Li + 1], c = NPC[sel]!, vit = m.campanha[sel], tent = tentativas(m, sel);
  useDecoracao();
  const faixa = fundoDeco(FAIXA_LUGAR[Li] ?? FUNDO_NPC[sel]);
  const cab = !aberto ? `Trancado: vença alguém em ${LUGARES[Li - 1].nome} antes.` : prox ? `Vencer ${L.rivais.length > 1 ? "qualquer um" : c.nome} abre ${prox.nome}.` : "Último lugar da campanha.";
  const st = vit ? `vencido ${vit}× em ${tent} luta${tent === 1 ? "" : "s"}` : tent ? `${tent} tentativa${tent === 1 ? "" : "s"}, nenhuma vitória` : "ainda não enfrentado";
  return (
    <>
      <section class="camp-det" aria-live="polite" aria-label="Lugar selecionado">
        {faixa && <div class="camp-faixa" style={{ backgroundImage: faixa }}><span aria-hidden="true">{L.nome} · luta contra {c.nome}</span></div>}
        <span class="camp-det-cab"><b>{L.nome}</b><span>sugerido: {L.sugerido}</span></span>
        <div class="camp-rivais" role="radiogroup" aria-label="Rivais do lugar">
          {L.rivais.map(k => {
            const n = NPC[k]!, img = a.tipo === "ok" ? imagemAtlas(a, n.sprite ?? n.k) : null, moldura = molduraArena(m.campanha[k]);
            return (
              <button type="button" key={k} class="camp-rival" role="radio" aria-checked={k === sel} disabled={luta.lutando} onClick={() => { if (k !== sel) escolherDesafio(k); }}>
                {urlDeco(moldura) ? <RetratoRival sprite={n.sprite ?? n.k} moldura={moldura} lado={52} />
                  : <span class="camp-rival-spr">{img && <img class="dl-pix" src={img.url} width={img.w} height={img.h} alt="" />}</span>}
                <b>{n.nome}</b><span>{m.campanha[k]} vitória{m.campanha[k] === 1 ? "" : "s"}</span>
              </button>
            );
          })}
        </div>
        <span class="camp-det-txt">{cab}</span>
        {cedo && aberto && <p class="camp-aviso">Seu pet ainda é {nomeEstagio(m.forma)}: este lugar é pensado para {L.sugerido} em diante.</p>}
        {!podeLutar && <p class="dl-apoio">O In-Training ainda não luta na campanha.</p>}
        <p class="dl-apoio"><b>{c.nome}</b> · {nomeEstiloNPC(c.estilo)} · stats {(c.total / STATS.length).toFixed(1).replace(".0", "").replace(".", ",")} em cada (total {c.total}) · {st}</p>
        <p class="licao">{c.licao}</p>
      </section>
      <button type="button" class={`dl-btn camp-lutar${vit ? " dl-btn--sec" : ""}`} disabled={!aberto || luta.lutando || !podeLutar}
        onClick={() => { LUTA.campSel = sel; lutarAnimado(sel, NOME_V2); if (LUTA.lutando) location.hash = ENDERECO_LUTA; }}>
        {vit ? `Lutar de novo com ${c.nome}` : `Desafiar ${c.nome}`}</button>
    </>
  );
}
/** desktop (CampDesktop): faixa do lugar, os rivais em cards (sprite, nome, estilo, licao), "Nesta ilha" com o que o
    registro conta e os botoes Treinar antes e Desafiar */
function DetalheDesk({ irTreinar }: { irTreinar: () => void }) {
  const { motor: m } = useJogo(), luta = useLuta(), sel = campAtual(m), Li = NPC[sel]!.lug, LUGARES = m.lugares, L = LUGARES[Li], aberto = m.desafioAberto(L.rivais[0]);
  const prox = LUGARES[Li + 1], c = NPC[sel]!, vit = m.campanha[sel], podeLutar = m.forma.est !== "bebe";
  useDecoracao();
  const faixa = fundoDeco(FAIXA_LUGAR[Li] ?? FUNDO_NPC[sel]);
  const regra = !aberto ? `trancado: vença alguém em ${LUGARES[Li - 1].nome} antes` : prox ? `vencer ${L.rivais.length > 1 ? "qualquer um" : c.nome} abre ${prox.nome}` : "último lugar da campanha";
  const a = useAtlas(), img = (k: string) => { if (a.tipo !== "ok") return null; const i = imagemAtlas(a, k); return <img class="dl-pix" src={i.url} width={i.w} height={i.h} alt="" />; };
  const tent = L.rivais.reduce((n, k) => n + tentativas(m, k), 0), vencidos = L.rivais.filter(k => m.campanha[k] > 0).length;
  /* melhor turno (vitoria mais curta) e regras novas: as lutas deste lugar refeitas do registro */
  const doLugar = lutasDoRegistro(m).filter(x => L.rivais.includes(x.rival)), vitDoLugar = doLugar.filter(x => x.pontosA === 1);
  const melhor = vitDoLugar.length ? Math.min(...vitDoLugar.map(x => x.turnos)) : null, novas = doLugar.reduce((n, x) => n + x.regrasNovas, 0);
  return (
    <>
      <div class="campd-faixa" style={faixa ? { backgroundImage: faixa } : undefined}>
        <b class="dl-num">{L.nome}</b><span>sugerido: {L.sugerido} · {regra}</span>
      </div>
      <div class="campd-rivais" role="radiogroup" aria-label="Rivais do lugar">
        {L.rivais.map(k => {
          const n = NPC[k]!, moldura = molduraArena(m.campanha[k]);
          return (
            <button type="button" key={k} class="campd-rival" role="radio" aria-checked={k === sel} disabled={luta.lutando} onClick={() => { if (k !== sel) escolherDesafio(k); }}>
              {urlDeco(moldura) ? <RetratoRival sprite={n.sprite ?? n.k} moldura={moldura} lado={52} />
                : <span class="camp-rival-spr">{img(n.sprite ?? n.k)}</span>}
              <span class="campd-rival-txt"><span><b>{n.nome}</b><span class="campd-estilo">{nomeEstiloNPC(n.estilo)}</span></span><span>{n.licao}</span></span>
            </button>
          );
        })}
      </div>
      <section class="campd-ilha" aria-labelledby="campd-ilha-tit">
        <span class="campd-ilha-cab"><h2 id="campd-ilha-tit">Nesta ilha</h2><span>{vencidos} de {L.rivais.length} vencidos</span></span>
        <div class="res-nums">
          <div class="res-num"><span class="dl-num">{tent}</span><span>tentativas</span></div>
          <div class="res-num"><span class="dl-num">{melhor === null ? "—" : `T${melhor}`}</span><span>melhor turno</span></div>
          <div class="res-num"><span class="dl-num">{novas}</span><span>regras novas</span></div>
        </div>
        {!podeLutar && <p class="dl-apoio">O In-Training ainda não luta na campanha.</p>}
        <p class="dl-apoio">Perder também ensina: a regra que ele tirar da luta aparece em Arena · Regras.</p>
      </section>
      <div class="campd-bts">
        <button type="button" class="dl-btn dl-btn--sec" onClick={irTreinar}>Treinar antes</button>
        <button type="button" class="dl-btn camp-lutar" disabled={!aberto || luta.lutando || !podeLutar}
          onClick={() => { LUTA.campSel = sel; lutarAnimado(sel, NOME_V2); if (LUTA.lutando) location.hash = ENDERECO_LUTA; }}>
          {vit ? `Lutar de novo com ${c.nome}` : `Desafiar ${c.nome}`}</button>
      </div>
    </>
  );
}

export function TelaCampanha({ voltarPet, irTreinar }: { voltarPet: () => void; irTreinar: () => void }) {
  const desk = useDesktop(), { motor: m } = useJogo(), v5 = m.lugares.length === ILHA_V5.length;
  const luta = useLuta();
  /* a aba abre com o palco do proprio modo (a mensagem da arena nao aparece aqui) */
  useEffect(() => { if (!LUTA.palco || LUTA.palco.modo !== "campanha") previa("campanha"); }, []);
  return (
    <div class="tela dl desk camp-tela">
      <div class="camp-principal"><Mapa /></div>
      <div class="camp-lado">{desk ? <DetalheDesk irTreinar={irTreinar} /> : <Detalhe />}
      {!desk && <details class="dl-apoio"><summary>Como funciona</summary><p>{v5 ? "Quatro" : "Três"} lugares pelo mapa, em sequência: o próximo só abre depois de vencer um rival do anterior. Na Torre há três rivais com estilos diferentes.{v5 ? " No alto fica a Montanha Espiral, com os Mestres das Trevas: ela é pensada para o Mega." : ""} Todo pet bem treinado vence qualquer um deles; sem treino, a luta vira sorte. Os NPCs têm stats iguais em todos os atributos (somando de 72 a 110; um pet sem treino tem 60), lutam com um estilo fixo e são imprevisíveis; o primeiro tem o tamanho de um Rookie. <b>Treine o pet no estágio sugerido</b> para vencer com segurança (na campanha o treino vale inteiro, stats absolutos). As lutas entram no registro e ensinam as regras de combate do seu pet.</p></details>}
      </div>
    </div>
  );
}
