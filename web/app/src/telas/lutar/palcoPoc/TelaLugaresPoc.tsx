/* A Arena e a Campanha da luta da POC (LUTA_POC, LP3), para os pets v21: antes da luta, a escolha (o rival e o mapa na Arena, LP-4; o
   desafio na Campanha, no mapa fixo do lugar); Lutar grava a luta no registro (Motor.lutarPoc, a mesma de sempre) e abre o palco, que so a
   mostra. A Liga, a Torre, o Salao e a Fabrica continuam na Fronteira com o aviso de antes (a tela deles na luta nova fica para depois). */
import { useState } from "react";
import { Swords } from "lucide-react";
import { CENAS, IDS_CENA, NPC, hashSemente, mapaDoLugar, type IdCena } from "../../../../motor/index.ts";
import { imagemAtlas, useAtlas } from "../../../atlas.ts";
import { mudarMotor, useJogo } from "../../../jogo.ts";
import { assistirPoc, fimDoPet, ladoDesenho, lutasDoResultado, nomeDaChave, useLutaPoc } from "../../../lutaPocTela.ts";
import type { ResultadoLutaPoc } from "../../../../motor/index.ts";

/** grava a luta (o motor decide e entra no registro) e abre o palco; o erro do motor aparece na tela */
function lutar(rival: string, mapa: IdCena | null, contexto: string, setErro: (e: string | null) => void): void {
  let r: ResultadoLutaPoc | null = null;
  try { mudarMotor(m => { r = m.lutarPoc(rival, hashSemente("luta", m.semente, m.log.length), mapa); }); }
  catch (err) { setErro(err instanceof Error ? err.message : String(err)); return; }
  setErro(null);
  const res = r as unknown as ResultadoLutaPoc, lutas = lutasDoResultado(res);
  assistirPoc(lutas, contexto, L => {
    const ult = lutas[lutas.length - 1], serie = lutas.length > 1;
    return fimDoPet(L, ult.A, ult.B, serie ? (res.venceu ? `Venceu as ${lutas.length} lutas seguidas.` : `A série parou na luta ${lutas.length}.`) : "");
  });
}

function Retrato({ k }: { k: string }) {
  const a = useAtlas(), img = a.tipo === "ok" ? imagemAtlas(a, k) : null;
  return <span className="poc-ret" aria-hidden="true">{img && <img className="dl-pix" src={img.url} width={img.w} height={img.h} alt="" />}</span>;
}

export function TelaArenaPoc() {
  const { motor: m, nascendo } = useJogo(), luta = useLutaPoc(), rivais = m.rivaisArenaPoc();
  const [rival, setRival] = useState<string>(() => rivais[0] ?? ""), [mapa, setMapa] = useState<IdCena>("campo"), [erro, setErro] = useState<string | null>(null);
  if (nascendo > 0 || !rivais.length) return <section className="hx-painel poc-lugar"><p>O seu pet ainda não pode lutar na Arena.</p></section>;
  const sel = rivais.includes(rival) ? rival : rivais[0];
  return (
    <section className="hx-painel poc-lugar" aria-labelledby="poc-arena-tit" data-testid="poc-arena">
      <h2 id="poc-arena-tit">Arena</h2>
      <p className="poc-nota">Seu pet luta sozinho, em tempo real. Escolha o rival e o mapa e assista.</p>
      <div className="poc-pet"><Retrato k={m.formaLutaPoc} /><b>{ladoDesenho(m.formaLutaPoc).nomeTela}</b></div>
      <fieldset className="poc-grupo"><legend>Rival</legend>
        <div className="poc-rivais" role="radiogroup" aria-label="Rival">
          {rivais.map(k => (
            <button key={k} type="button" role="radio" aria-checked={k === sel} className="poc-rival" disabled={luta.lutando} onClick={() => setRival(k)} data-testid={`poc-rival-${k}`}>
              <Retrato k={k} /><span>{nomeDaChave(k)}</span>
            </button>
          ))}
        </div>
      </fieldset>
      <fieldset className="poc-grupo"><legend>Mapa</legend>
        <div className="poc-mapas" role="radiogroup" aria-label="Mapa">
          {IDS_CENA.map(id => (
            <button key={id} type="button" role="radio" aria-checked={id === mapa} className="poc-mapa" disabled={luta.lutando} onClick={() => setMapa(id)} data-testid={`poc-mapa-${id}`}>
              <b>{CENAS[id].nome}</b><small>{CENAS[id].desc}</small>
            </button>
          ))}
        </div>
      </fieldset>
      {erro && <p className="aviso" role="alert">A luta não começou: {erro}</p>}
      <button type="button" className="hx-continuar poc-lutar" disabled={luta.lutando} onClick={() => lutar(sel, mapa, `Arena · ${CENAS[mapa].nome}`, setErro)} data-testid="poc-lutar">
        <Swords aria-hidden="true" /> Lutar</button>
    </section>
  );
}

export function TelaCampanhaPoc() {
  const { motor: m } = useJogo(), luta = useLutaPoc(), [erro, setErro] = useState<string | null>(null);
  const desafios = Object.keys(m.campanha).filter(k => NPC[k]);
  return (
    <section className="hx-painel poc-lugar" aria-labelledby="poc-camp-tit" data-testid="poc-campanha">
      <h2 id="poc-camp-tit">Campanha</h2>
      <p className="poc-nota">Cada lugar luta no mapa dele. Na Cidadela são 3 lutas seguidas, sem cura.</p>
      <ul className="poc-desafios">
        {desafios.map(k => {
          const L = m.lugares[m.lugarDe(k)], mapa = mapaDoLugar(L), aberto = m.desafioAberto(k);
          return (
            <li key={k} className="poc-desafio">
              <Retrato k={k} />
              <span><b>{nomeDaChave(k)}</b><small>{L.nome} · {CENAS[mapa].nome}{m.campanha[k] ? ` · vencido ${m.campanha[k]}×` : ""}</small></span>
              <button type="button" className="hx-btn" disabled={luta.lutando || !aberto} onClick={() => lutar(k, mapa, `Campanha · ${L.nome}`, setErro)}
                data-testid={`poc-desafio-${k}`}>{aberto ? "Lutar" : "Trancado"}</button>
            </li>
          );
        })}
      </ul>
      {erro && <p className="aviso" role="alert">A luta não começou: {erro}</p>}
    </section>
  );
}
