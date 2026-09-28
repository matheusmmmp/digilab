/* Catalogo (desenho DiarioCatalogo; porte do HTML): as 15 formas de cada brasao numa grade 5 x 3 com o recorte
   1x de cada uma; o toque abre o detalhe com as barras dos 6 stats, vida, guts, tecnica e passiva. Stats pela
   formula do catalogo, sem carater e sem temperamento. */
import { useState } from "preact/hooks";
import {
  CAT, DESC_PASSIVA, DESC_TECNICA, ESPECIES, FORMAS_AD, LINHAS, LINHA_DA_FORMA, NOME_ARQ, NOME_ESP, NOME_STAT, NOME_V2, STATS,
  chaveSprite, nomeEstagio, nomeForma, perfilDe, type Especie, type Forma,
} from "../../../motor/index.ts";
import { dimSprite, imagemAtlas, useAtlas } from "../../atlas.ts";
import { dec } from "../../componentes/Barras.tsx";
import { useJogo } from "../../jogo.ts";
import { requisito } from "../crescer/TelaEvolucao.tsx";

const n1 = (x: number): string => dec(x, 1).replace(/,0$/, "");
export function formasDoBrasao(esp: Especie): Forma[] {
  return [{ esp, est: "bebe" }, ...(["sereno", "arisco"] as const).map(r => ({ esp, est: "crianca" as const, ramo: r })),
    ...LINHAS.map(l => ({ esp, est: "adolescente" as const, ramo: "sereno" as const, linha: l })),
    ...FORMAS_AD.map(a => ({ esp, est: "adulto" as const, ramo: "sereno" as const, linha: LINHA_DA_FORMA[a], adulta: a }))];
}

function Tile({ f, sel, meu, escolher }: { f: Forma; sel: boolean; meu: boolean; escolher: () => void }) {
  const a = useAtlas(), img = a.tipo === "ok" ? imagemAtlas(a, chaveSprite(f)) : null;
  const h = a.tipo === "ok" ? dimSprite(a.dados, chaveSprite(f))[1] : 0, top = h > 52 ? -Math.round(h * .08) : Math.round((52 - h) / 2);
  return (
    <button type="button" class={`cat-tile${meu ? " meu" : ""}`} role="option" aria-selected={sel} aria-label={`${nomeForma(f)}, ${nomeEstagio(f)}`} onClick={escolher}>
      <span class="cat-cx">{img && <img class="dl-pix" src={img.url} width={img.w} height={img.h} alt="" style={{ marginTop: `${top}px` }} />}</span>
      <span class="cat-nome">{nomeForma(f)}</span>
    </button>
  );
}
function Detalhe({ f, meu }: { f: Forma; meu: boolean }) {
  const a = useAtlas(), pf = perfilDe(f, null), st = pf.stats, img = a.tipo === "ok" ? imagemAtlas(a, chaveSprite(f)) : null;
  const extra = f.adulta ? `técnica ${NOME_V2[pf.tecnica!]} · passiva: ${DESC_PASSIVA[f.adulta]}`
    : f.linha ? `técnica ${NOME_V2[pf.tecnica!]}: ${DESC_TECNICA[pf.tecnica!]}` : f.est === "bebe" ? "luta ao acaso" : "só ações base, 3 regras de combate";
  return (
    <section class="dl-card cat-detalhe">
      <span class="cat-det-spr">{img && <img class="dl-pix" src={img.url} width={img.w} height={img.h} alt="" />}</span>
      <div class="cat-det-txt"><span class="dl-placa">{nomeForma(f)}</span> <span class="dl-tag dl-tag--estagio">{nomeEstagio(f)}</span>{meu && <> <span class="dl-tag dl-tag--ativo">seu pet</span></>}
        <p class="dl-apoio" style={{ margin: "6px 0" }}>{f.est === "bebe" ? "sai do ovo" : requisito(f)}</p></div>
      <div class="cat-stats">{STATS.map(k => {
        const v = st[k], w = Math.max(0, Math.min(100, (v - CAT.min) / (CAT.max - CAT.min) * 100));
        return <div class="cat-stat" key={k}><span>{NOME_STAT[k]}</span><span class="dl-vida-trilho" role="img" aria-label={`${NOME_STAT[k]} ${n1(v)}`}><i style={{ width: `${w}%`, background: "var(--dl-action)" }} /></span><span class="dl-lcd">{n1(v)}</span></div>;
      })}</div>
      <p style={{ margin: 0 }}>vida {pf.hpMax.toFixed(0)} · guts {pf.guts0.toFixed(0)} de {pf.gutsMax.toFixed(0)} · recupera {n1(pf.regen)} por turno</p>
      <p class="dl-apoio" style={{ margin: 0 }}>{extra}</p>
    </section>
  );
}
export function TelaCatalogo() {
  const { motor: m } = useJogo(), [esp, setEsp] = useState<Especie>(m.especie), [sel, setSel] = useState(-1);
  const formas = formasDoBrasao(esp), meu = chaveSprite(m.forma);
  const i = sel >= 0 && sel < formas.length ? sel : Math.max(0, formas.findIndex(f => chaveSprite(f) === meu));
  return (
    <div class="tela dl">
      <p>As 15 formas de cada brasão, com os stats de cada uma.</p>
      <details class="dl-apoio"><summary>Como funciona</summary>
        <p>Cada brasão percorre a mesma árvore (1 In-Training, 2 Rookies, 4 Champions, 4 Ultimates e 4 Megas). Stats pela fórmula do catálogo (brasão + ramo + linha + forma; todo modificador soma zero, com renormalização nos extremos), aqui sem caráter e sem temperamento; vida e guts já com o multiplicador do nível. Os números ainda estão em teste.</p></details>
      <div class="dl-linha" role="group" aria-label="Brasão">
        {ESPECIES.map(e => <button type="button" key={e} class="chip" aria-pressed={e === esp} onClick={() => { setEsp(e); setSel(-1); }}>{NOME_ESP[e]}{e === m.especie ? " (seu)" : ""}</button>)}
        <span class="dl-apoio">{CAT.conceito[esp].split("; ").pop()}</span>
      </div>
      <div class="cat-grade" role="listbox" aria-label="Formas do brasão">
        {formas.map((f, j) => <Tile key={chaveSprite(f)} f={f} sel={j === i} meu={chaveSprite(f) === meu} escolher={() => setSel(j)} />)}
      </div>
      <Detalhe f={formas[i]} meu={chaveSprite(formas[i]) === meu} />
      <section class="bloco"><h2>Técnicas (Champion)</h2><div class="decisoes">
        {LINHAS.map(l => { const tc = CAT.adolescente[l].tecnica; return <div key={l}><span class="t">{NOME_ARQ[l]}</span> <b>{NOME_V2[tc]}</b>: {DESC_TECNICA[tc]}</div>; })}
      </div></section>
      <section class="bloco"><h2>Passivas (Ultimate e Mega)</h2><div class="decisoes">
        {FORMAS_AD.map(a => <div key={a}><span class="t">{NOME_ARQ[a]}</span> {DESC_PASSIVA[a]}</div>)}
      </div></section>
    </div>
  );
}
