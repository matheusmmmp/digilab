/* Catalogo (desenho DiarioCatalogo; porte do HTML): as formas de cada brasao numa grade com o recorte 1x de cada
   uma (evolucao canonica: os 8 arquetipos adultos sao 4 Ultimates, 2 por linha, e cada linha tem o seu Mega); o toque abre o detalhe com as barras dos 6 stats, vida, guts, tecnica e passiva. Stats pela
   formula do catalogo, sem carater e sem temperamento. */
import { useState } from "react";
import {
  CAT, DESC_PASSIVA, DESC_TECNICA, ESPECIES, FORMAS_AD, LINHAS, LINHA_DA_FORMA, NOME_ARQ, NOME_ESP, NOME_STAT, NOME_V2, STATS,
  chaveSprite, nomeArquetipo, nomeEstagio, nomeForma, perfilDe, vidaExibida, type Especie, type Forma,
} from "../../../motor/index.ts";
import { imagemAtlas, silhuetaAtlas, useAtlas } from "../../atlas.ts";
import { dec } from "../../componentes/Barras.tsx";
import { Deco } from "../../componentes/Deco.tsx";
import { BRASAO } from "../../decoracao.ts";
import { useJogo } from "../../jogo.ts";
import { useDesktop } from "../../desktop.ts";
import { Folha } from "../../componentes/Folha.tsx";
import { idNo, requisito } from "../crescer/TelaEvolucao.tsx";

const n1 = (x: number): string => dec(x, 1).replace(/,0$/, "");
export function formasDoBrasao(esp: Especie): Forma[] {
  return [{ esp, est: "bebe" }, ...(["sereno", "arisco"] as const).map(r => ({ esp, est: "crianca" as const, ramo: r })),
    ...LINHAS.map(l => ({ esp, est: "adolescente" as const, ramo: "sereno" as const, linha: l })),
    ...FORMAS_AD.map(a => ({ esp, est: "adulto" as const, ramo: "sereno" as const, linha: LINHA_DA_FORMA[a], adulta: a })),
    /* o Mega de cada linha (pets v5): o mesmo para os dois arquetipos */
    ...LINHAS.map(l => ({ esp, est: "mega" as const, ramo: "sereno" as const, linha: l, adulta: FORMAS_AD.find(a => LINHA_DA_FORMA[a] === l)! }))];
}
const rotulo = (f: Forma): string => nomeForma(f) + (f.est !== "mega" && nomeArquetipo(f) ? ` · ${nomeArquetipo(f)}` : "");

/** bloco da forma (DiarioCatalogo): 66 px, a forma vista (o caminho deste pet) em cor; a nao vista em silhueta cinza */
function Tile({ f, sel, meu, visto, escolher }: { f: Forma; sel: boolean; meu: boolean; visto: boolean; escolher: () => void }) {
  const a = useAtlas(), img = a.tipo === "ok" ? (visto ? imagemAtlas(a, chaveSprite(f)) : silhuetaAtlas(a, chaveSprite(f))) : null;
  return (
    <button type="button" className={`cat-tile${meu ? " meu" : ""}${visto ? "" : " nao-visto"}`} role="option" aria-selected={sel} aria-label={`${rotulo(f)}, ${nomeEstagio(f)}${visto ? "" : ", ainda não vista"}`} onClick={escolher}>
      <span className="cat-cx">{img && <img className="dl-pix" src={img.url} width={img.w} height={img.h} alt="" />}</span>
      <span className="cat-nome">{nomeForma(f)}{f.est !== "mega" && nomeArquetipo(f) && <small className="cat-arq">{nomeArquetipo(f)}</small>}</span>
    </button>
  );
}
function Detalhe({ f, meu }: { f: Forma; meu: boolean }) {
  const { motor: m } = useJogo(), a = useAtlas(), pf = perfilDe(f, null), st = pf.stats, img = a.tipo === "ok" ? imagemAtlas(a, chaveSprite(f)) : null;
  const extra = f.est === "mega" ? `técnica ${NOME_V2[pf.tecnica!]} · passiva: a do arquétipo do Ultimate · vida e guts ×1,15 (só pets novos)`
    : f.adulta ? `técnica ${NOME_V2[pf.tecnica!]} · passiva: ${DESC_PASSIVA[f.adulta]}`
    : f.linha ? `técnica ${NOME_V2[pf.tecnica!]}: ${DESC_TECNICA[pf.tecnica!]}` : f.est === "bebe" ? "luta ao acaso" : "só ações base, 3 regras de combate";
  return (
    <section className="dl-card cat-detalhe">
      <div className="cat-det-cab"><span className="cat-det-spr">{img && <img className="dl-pix" src={img.url} width={img.w} height={img.h} alt="" />}</span>
        <b>{rotulo(f)}</b><span className="cat-det-tags"><span className="dl-tag dl-tag--estagio">{nomeEstagio(f)}</span>{meu && <span className="dl-tag dl-tag--ativo">seu pet</span>}</span></div>
      <p className="dl-apoio" style={{ margin: 0 }}>{CAT.conceito[f.esp]} · {f.est === "bebe" ? "sai do ovo" : requisito(f)}</p>
      <div className="cat-stats">{STATS.map(k => {
        const v = st[k], w = Math.max(0, Math.min(100, (v - CAT.min) / (CAT.max - CAT.min) * 100));
        return <div className="cat-stat" key={k}><span>{NOME_STAT[k]}</span><span className="dl-vida-trilho" role="img" aria-label={`${NOME_STAT[k]} ${n1(v)}`}><i style={{ width: `${w}%`, background: "var(--dl-action)" }} /></span><span className="dl-lcd">{n1(v)}</span></div>;
      })}</div>
      <p style={{ margin: 0 }}>vida {Math.round(vidaExibida(pf, pf.est, 0, m.versao)).toLocaleString("pt-BR")} · guts {pf.guts0.toFixed(0)} de {pf.gutsMax.toFixed(0)} · recupera {n1(pf.regen)} por turno</p>
      <p className="dl-apoio" style={{ margin: 0 }}>{extra}</p>
    </section>
  );
}
export function TelaCatalogo() {
  const { motor: m } = useJogo(), [esp, setEsp] = useState<Especie>(m.especie), [sel, setSel] = useState(-1), [folha, setFolha] = useState(false), desk = useDesktop();
  const formas = formasDoBrasao(esp), meu = idNo(m.forma);
  const vistos = new Set([idNo({ esp: m.especie, est: "bebe" }), ...m.evolucoes.map(x => idNo(x.forma)), meu]);
  const i = sel >= 0 && sel < formas.length ? sel : Math.max(0, formas.findIndex(f => idNo(f) === meu));
  return (
    <div className="tela dl desk cat-tela">
      <div className="cat-brasoes" role="group" aria-label="Brasão">
        {ESPECIES.map(e => <button type="button" key={e} className="chip" aria-pressed={e === esp} onClick={() => { setEsp(e); setSel(-1); }}><Deco nome={BRASAO[e].peca} className="cat-chip-brasao" />{NOME_ESP[e]}</button>)}
        <span className="cat-vistas">{formas.filter(f => vistos.has(idNo(f))).length} de {formas.length} vistas</span>
      </div>
      <div className="cat-grade" role="listbox" aria-label="Formas do brasão">
        {formas.map((f, j) => <Tile key={idNo(f)} f={f} sel={j === i} meu={idNo(f) === meu} visto={vistos.has(idNo(f))} escolher={() => { setSel(j); setFolha(true); }} />)}
      </div>
      {/* ficha: coluna da direita no desktop; folha no celular (secao 7) */}
      {desk ? <Detalhe f={formas[i]} meu={idNo(formas[i]) === meu} />
        : folha && <Folha titulo={`Ficha: ${rotulo(formas[i])}`} fechar={() => setFolha(false)}><Detalhe f={formas[i]} meu={idNo(formas[i]) === meu} /></Folha>}
      <details className="dl-apoio"><summary>Como funciona</summary>
        <p>Vista = forma por onde este pet passou. Cada brasão percorre a mesma árvore, a do cânone (1 In-Training, 2 Rookies, 4 Champions, 4 Ultimates e 4 Megas): cada Champion vira o Ultimate da linha em um de dois arquétipos (a passiva muda), e o Ultimate vira o Mega da linha (só pets novos; o arquétipo continua). Stats pela fórmula do catálogo (brasão + ramo + linha + forma; todo modificador soma zero, com renormalização nos extremos), aqui sem caráter e sem temperamento; vida e guts já com o multiplicador do nível. Os números ainda estão em teste.</p></details>
      <section className="bloco"><h2>Técnicas (Champion)</h2><div className="decisoes">
        {LINHAS.map(l => { const tc = CAT.adolescente[l].tecnica; return <div key={l}><span className="t">{NOME_ARQ[l]}</span> <b>{NOME_V2[tc]}</b>: {DESC_TECNICA[tc]}</div>; })}
      </div></section>
      <section className="bloco"><h2>Passivas (Ultimate e Mega)</h2><div className="decisoes">
        {FORMAS_AD.map(a => <div key={a}><span className="t">{NOME_ARQ[a]}</span> {DESC_PASSIVA[a]}</div>)}
      </div></section>
    </div>
  );
}
