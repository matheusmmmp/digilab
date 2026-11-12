/* Evolucao (docs/TAREFA_V2_EVOLUCAO.md; L2 de "Lugares da ilha", prancha crescer_evolucao_*, regra do texto): a forma atual (o pet, o nome, o
   estagio e o brasao), o tempo ate a proxima evolucao, o que o nivel pede (os selos das medalhas do Tamer e as lutas de treino, em numero) e a arvore
   so da linha do pet; o historico e o porque ficam fechados e o "Como funciona" tambem. Nenhuma frase a vista: o lugar de cada medalha, os 80%, o que
   leva a cada no vao para o balao (foco e hover) e para o aria-label. A arvore: In-Training, 2 Rookie, 4 Champion (so a do pet com sprite; as outras
   linhas, nos pequenos e pontilhados), os 2 arquetipos do Ultimate da linha e a sombria, e o Mega (pets v5), com estados percorrido/agora/possivel/
   fechado/sombria. A forma futura ainda nao decidida pelo motor aparece como "?", sem nome (guia, secao 5). */
import { useId, type ReactNode } from "react";
import { Check, ChevronRight, Heart, History, Hourglass, Info, Swords } from "lucide-react";
import {
  CAT, CDJ, CLE, CMD, CMG, CSO, DESC_PASSIVA, DESC_TECNICA, FORMAS_AD, LINHAS, LINHA_DA_FORMA, MEDALHAS, NOME_ARQ, NOME_V2, SOMBRIA, TICK_INICIAL, TPD,
  caraterPrevisto, chaveSprite, corDominante, formaAdultaDe, linhaDoCarater, nomeArquetipo, nomeEstagio, nomeForma, type Carater, type Forma, type FormaAdultaNormal, type Motor,
} from "../../../motor/index.ts";
import { imagemAtlas, silhuetaAtlas, useAtlas } from "../../atlas.ts";
import { rotuloRel } from "../../componentes/Barras.tsx";
import { Deco } from "../../componentes/Deco.tsx";
import { ComDica, ComoFunciona } from "../../componentes/Dica.tsx";
import { PetGrande, Porque, reverEvolucao } from "../../componentes/Revelacao.tsx";
import { BRASAO } from "../../decoracao.ts";
import { tamerAtual, useJogo } from "../../jogo.ts";
import { comoGanhar, medalhasQueFaltam, textoFalta } from "../../tamer.ts";
import { diaDe, hhmm } from "../pet/TelaPet.tsx";

export function duracao(min: number): string {
  const d = Math.floor(min / TPD), h = Math.floor((min % TPD) / 60), m = min % 60;
  return [d ? `${d}d` : "", h ? `${h}h` : "", !d && m ? `${m}min` : ""].filter(Boolean).join(" ") || "agora";
}
/** caráter em palavras: so os eixos fora da faixa comum */
export const fmtCar = (car: Partial<Carater>): string => {
  const f = Object.entries(car).filter(([, v]) => Math.abs(v as number) >= CDJ.limiarTom).map(([k, v]) => `${k} ${rotuloRel(v as number)}`);
  return f.length ? f.join(", ") : "todos os eixos na faixa comum";
};
/** para onde o pet iria se a transicao acontecesse agora, e por que */
export function previsaoEvo(m: Motor): { falta: number; prox: Forma; porque: string } | null {
  const t = m.e.tick - TICK_INICIAL, D = m.dur, f = m.forma;
  if (f.est === "bebe") {
    const c = m.fracaoCuidado();
    return { falta: D.bebe - t, prox: { ...f, est: "crianca", ramo: c >= CAT.limiarCuidado ? "sereno" : "arisco" },
      porque: `cuidado ${(c * 100).toFixed(0)}% (${m.chamados.atendidos} de ${m.chamados.total} chamados atendidos em até ${CAT.janelaChamado} min)` };
  }
  if (f.est === "crianca") {
    const car = caraterPrevisto(m, "adolescente"), linha = linhaDoCarater(car);
    return { falta: m.tickLimiteEstagio()! - m.e.tick, prox: { ...f, est: "adolescente", linha }, porque: `caráter ${fmtCar(car)}` };
  }
  if (f.est === "adolescente") {
    const car = caraterPrevisto(m, "adulto"), adulta = formaAdultaDe(f.linha!, car), comp = CAT.adulto[f.linha!].comp;
    return { falta: m.tickLimiteEstagio()! - m.e.tick, prox: { ...f, est: "adulto", adulta },
      porque: `${comp} ${rotuloRel(car[comp])}; lutas de treino ${m.sparring} de ${CAT.sparring}` };
  }
  /* pets v5: Ultimate -> Mega (a sombria nunca) */
  const r = m.requisitosMega();
  if (r && !m.sombria) {
    const L = m.lutas;
    return { falta: r.falta, prox: { ...f, est: "mega" },
      porque: `vínculo ${virgula(m.vinc.valor)} de ${virgula(CMG.vinculo)}; lutas no Ultimate ${L.lutas} de ${CAT.sparring}, `
        + `vitórias ${L.lutas ? Math.round(L.vitorias / L.lutas * 100) : 0}% de ${Math.round(CLE.limiarTaxa * 100)}%` };
  }
  return null;
}
const virgula = (x: number): string => (Math.round(x * 100) / 100).toString().replace(".", ",");
/** id do no da arvore: as duas formas adultas da linha tem o mesmo sprite (o Ultimate), entao o no e pela forma; o Mega
    tem um no por linha */
const linhaDe = (g: Forma): string => g.linha ?? SOMBRIA[g.adulta!]?.linha ?? LINHA_DA_FORMA[g.adulta as FormaAdultaNormal];
export const idNo = (g: Forma): string => g.est === "mega" ? `${g.esp}_mega_${linhaDe(g)}` : g.est === "adulto" ? `${g.esp}_adulto_${g.adulta}` : chaveSprite(g);
/** pets v6: as medalhas do Tamer que a evolucao para a forma pede (texto do no) */
const medReq = (g: Forma): string => {
  const n = (CMD as Record<string, number>)[g.est] ?? 0;
  return n ? ` · ${n} medalha${n === 1 ? "" : "s"} do Tamer` : "";
};
export function requisito(g: Forma): string {
  if (g.est === "bebe") return "sai do ovo";
  if (g.est === "crianca") return g.ramo === "sereno" ? `cuidado ≥ ${CAT.limiarCuidado * 100}% dos chamados no In-Training` : `cuidado < ${CAT.limiarCuidado * 100}% dos chamados no In-Training`;
  if (g.est === "adolescente") { const a = CAT.adolescente[g.linha!]; return `caráter dominante ${a.eixo} ao fim do Rookie${medReq(g)} · técnica ${NOME_V2[a.tecnica]}: ${DESC_TECNICA[a.tecnica]}`; }
  if (g.est === "mega") return `Mega: o mesmo arquétipo do Ultimate, mais forte · ${duracao(CMG.durRapida)} como Ultimate (o dobro no ritmo clássico), ${CAT.sparring} lutas com ${CLE.limiarTaxa * 100}% ou mais de vitórias e vínculo ${virgula(CMG.vinculo)} ou mais${medReq(g)} (a sombria não chega)`;
  const a = CAT.adulto[g.linha!], s = a.formas[g.adulta as FormaAdultaNormal]!.sinal;
  return `${NOME_ARQ[g.adulta!]}: ${a.comp} ${s > 0 ? "acima" : "abaixo"} do pet comum e ${CAT.sparring} lutas de treino${medReq(g)} · passiva: ${DESC_PASSIVA[g.adulta!]}`;
}

type EstadoNo = "agora" | "percorrido" | "possivel" | "fechado";

/** um no da arvore da linha do pet: so o estado e (revelado) o sprite; o que leva ate ele vai no balao e no aria-label. `g` nulo: a forma da
    linha ainda nao existe (o pet ainda nao tem linha) */
function No({ g, estado, sombriaNo, sombriaAgora, rotuloEst, nomeGenerico }: { g: Forma | null; estado: EstadoNo; sombriaNo: boolean; sombriaAgora: boolean; rotuloEst: string; nomeGenerico: string }) {
  const a = useAtlas(), revelado = !!g && (estado === "agora" || estado === "percorrido");
  const img = g && a.tipo === "ok" && revelado ? imagemAtlas(a, chaveSprite(g), 1, { sombria: sombriaNo && sombriaAgora, recortar: true }) : null;
  const det = !g ? `${nomeGenerico}: forma ainda não decidida`
    : (revelado ? nomeForma(g) : "Forma ainda não decidida") + ": " + (sombriaNo ? "forma sombria da linha (sobrecarga alta na virada para Ultimate)" : requisito(g));
  const nome = revelado ? nomeForma(g!) : !g ? nomeGenerico : sombriaNo ? "forma sombria da linha" : g.est === "adulto" ? `${nomeGenerico}, arquétipo ${NOME_ARQ[g.adulta!]}` : "forma não decidida";
  const cls = `evl-no evl-no--${estado}${sombriaNo ? " evl-no--sombria" : ""}`;
  return (
    <ComDica papel="img" className={cls} rotulo={`${nome}, ${sombriaNo && !revelado ? "sombria, " : ""}${rotuloEst}`} dica={det}>
      {revelado ? (img ? <img className="dl-pix" src={img.url} width={img.w} height={img.h} alt="" /> : <span aria-hidden="true">{nomeForma(g!).slice(0, 2)}</span>)
        : <span aria-hidden="true">{estado === "fechado" && !sombriaNo ? "" : "?"}</span>}
    </ComDica>
  );
}

/** a arvore so da linha do pet (as outras linhas do Champion viram nos pequenos e pontilhados, sem texto) */
function Arvore({ m }: { m: Motor }) {
  const f = m.forma, esp = m.especie, evs = m.evolucoes, idDe = idNo;
  const bebe: Forma = { esp, est: "bebe" };
  const cri: Forma[] = (["sereno", "arisco"] as const).map(r => ({ esp, est: "crianca", ramo: r }));
  const ado: Forma[] = LINHAS.map(l => ({ esp, est: "adolescente", ramo: "sereno", linha: l }));
  const aduDe = (l: string): Forma[] => FORMAS_AD.filter(ad => LINHA_DA_FORMA[ad] === l).map(ad => ({ esp, est: "adulto", ramo: "sereno", linha: LINHA_DA_FORMA[ad], adulta: ad }));
  const somDe = (l: string): Forma => { const x = CSO.formas[l as keyof typeof CSO.formas]; return { esp, est: "adulto", ramo: "sereno", linha: l as Forma["linha"], adulta: x.nome as Forma["adulta"] }; };
  const megaDe = (l: string): Forma => ({ ...aduDe(l)[0], est: "mega" });
  const caminho = new Set([idDe(bebe), ...evs.map(x => idDe(x.forma))]);
  const atualId = idDe(f);
  const adu = LINHAS.flatMap(aduDe), meg = LINHAS.map(megaDe);
  /* o que ainda da para alcancar a partir da forma atual (o Mega: nunca a sombria) */
  const alcance = new Set(f.est === "bebe" ? [...cri, ...ado, ...adu, ...meg].map(idDe) : f.est === "crianca" ? [...ado, ...adu, ...meg].map(idDe)
    : f.est === "adolescente" ? [...adu, ...meg].filter(x => x.linha === f.linha).map(idDe)
    : f.est === "adulto" && !m.sombria ? [idDe(megaDe(f.linha ?? linhaDe(f)))] : []);
  const estado = (id: string): EstadoNo => id === atualId ? "agora" : caminho.has(id) ? "percorrido" : alcance.has(id) ? "possivel" : "fechado";
  /* a linha do pet: so de depois do Rookie */
  const L = f.est === "bebe" || f.est === "crianca" ? null : linhaDe(f);
  const no = (g: Forma, sombriaNo = false) => (
    <No key={idDe(g) + (sombriaNo ? "_s" : "")} g={g} estado={sombriaNo ? (m.sombria && idDe(g) === atualId ? "agora" : "fechado") : estado(idDe(g))}
      sombriaNo={sombriaNo} sombriaAgora={m.sombria} rotuloEst={sombriaNo ? (m.sombria && idDe(g) === atualId ? "agora" : "fechada") : { agora: "agora", percorrido: "percorrido", possivel: "possível", fechado: "fechada" }[estado(idDe(g))]} nomeGenerico={nomeEstagio(g)} />
  );
  const generico = (rot: string) => <No key={rot} g={null} estado="possivel" sombriaNo={false} sombriaAgora={false} rotuloEst="possível" nomeGenerico={rot} />;
  const fila = (rot: string, nos: ReactNode) => <div className="evl-fila" key={rot}><span className="lg-rot">{rot}</span><div className="evl-nos">{nos}</div></div>;
  return (
    <div className="evl-arv" role="group" aria-label="Árvore de evolução">
      {fila("In-Training", no(bebe))}
      {fila("Rookie", cri.map(c => no(c)))}
      {fila("Champion", ado.map(x => no(x)))}
      {fila("Ultimate", L ? [...aduDe(L).map(y => no(y)), no(somDe(L), true)] : generico("Ultimate"))}
      {fila("Mega", L ? no(megaDe(L)) : generico("Mega"))}
    </div>
  );
}

export function TelaEvolucao() {
  const { motor: m } = useJogo(), f = m.forma, evs = m.evolucoes, p = previsaoEvo(m), t = tamerAtual(), idMed = useId();
  /* pets v6: as medalhas do Tamer que a proxima evolucao pede (null nos v1-v5 e sem proxima evolucao) */
  const rMed = m.requisitosEvolucao()?.medalhas ?? null, faltaMed = !!rMed && !rMed.ok, prontoMed = !!m.esperandoMedalha();
  const espera = !!p && p.falta <= 0 && (f.est === "adolescente" || f.est === "adulto" || (f.est === "crianca" && faltaMed));
  const rMega = f.est === "adulto" ? m.requisitosMega() : null;
  const ult = evs[evs.length - 1];
  const det = (x: typeof evs[number]) => x.estagio === "mega" ? `vínculo ${virgula(x.vinculo!)}; ${x.sparring} lutas no Ultimate`
    : x.estagio === "crianca" ? `cuidado ${(x.cuidado! * 100).toFixed(0)}%`
    : x.estagio === "adolescente" ? `caráter: ${fmtCar(x.carater!)}` : `${NOME_ARQ[x.adulta!]}; caráter: ${fmtCar(x.carater!)}; ${x.sparring} lutas de treino`;
  const alvo = p ? nomeEstagio(p.prox) : "", cor = corDominante(m.tracos), arq = nomeArquetipo(f), br = BRASAO[m.especie];
  /* os selos: so a conta do Tamer (a prancha; pergunta 7 da secao L2/L3): as que ele tem, e as que faltam com o lugar de cada uma no balao */
  const precisa = rMed?.precisa ?? 0, tem = Math.min(t.n, precisa), ganhas = MEDALHAS.filter(x => t.tem(x.id)), faltam = medalhasQueFaltam(t, precisa);
  const comLutas = f.est === "adolescente" || !!rMega, nLutas = rMega ? m.lutas.lutas : m.sparring;
  const pctVit = Math.round(CLE.limiarTaxa * 100);
  return (
    <div className="tela dl evl lg">
      <section className="evl-topo" aria-label="Forma atual">
        <span className="evl-palco" aria-hidden="true"><PetGrande f={f} alvo={[90, 70]} cor={cor} sombria={m.sombria} maxEscala={3} /></span>
        <div className="evl-nome">
          <b>{nomeForma(f)}</b>
          <div className="lg-linha"><span className="lg-etq">{nomeEstagio(f)}{arq ? ` · ${arq}` : ""}</span><span className="lg-linha" style={{ gap: 4 }}><Deco nome={br.peca} largura={30} altura={20} alt="" />{br.nome}</span></div>
        </div>
        <ComDica className="evl-prazo" lado="dir" rotulo={p ? `${espera ? "Falta" : "Faltam"} ${duracao(Math.max(0, p.falta))} para ${alvo}` : "Forma final"} dica={p ? <>Se evoluísse agora: {p.porque}.</> : <>Não há próxima evolução.</>}>
          <span className="lg-linha"><Hourglass aria-hidden="true" /><b className="lg-num">{p ? (espera ? (prontoMed ? "Pronto" : "Espera") : duracao(Math.max(0, p.falta))) : "Final"}</b></span>
          {p && <small>{espera ? "para" : "até"} {alvo}</small>}
        </ComDica>
      </section>
      {(rMed || comLutas) && (
        <div className="lg-destaque evl-reqs" role="group" aria-label={p ? `O que a evolução para ${alvo} pede` : "O que a evolução pede"}>
          {rMed && (
            <span className="evl-req evl-medalhas" aria-describedby={idMed}>
              <span className="evl-selos">
                {Array.from({ length: precisa }, (_, k) => {
                  const ganha = k < tem, md = ganha ? ganhas[k] : faltam[k - tem];
                  return (
                    <ComDica key={k} papel="img" rotulo={`${md?.nome ?? "Medalha"}, ${ganha ? "ganha" : "falta"}`} dica={<><b>{md?.nome ?? "Medalha"}</b>{ganha ? "." : <>: {comoGanhar(md!)}.</>}</>}>
                      <span className={`evl-selo${ganha ? "" : " evl-selo--falta"}`}><i>{ganha ? <Check aria-hidden="true" /> : k + 1}</i></span>
                    </ComDica>
                  );
                })}
              </span>
              <small>medalhas</small><b className="lg-num lg-num--p">{tem}/{precisa}</b>
              <span className="evo-medalha-txt sr-so" id={idMed} role="status">{prontoMed ? <b>Pronto para evoluir. </b> : null}{textoFalta(t, precisa) || "Medalhas do Tamer."}</span>
            </span>
          )}
          {comLutas && (
            <ComDica className="evl-req" rotulo={`Lutas de treino: ${nLutas} de ${CAT.sparring}`}
              dica={<>Lutas de treino na Arena: {CAT.sparring} para virar {alvo}, com {pctVit}% ou mais de vitórias{m.lutas.lutas ? ` (agora ${m.lutas.vitorias} de ${m.lutas.lutas})` : ""}.</>}>
              <Swords aria-hidden="true" /><b className="lg-num lg-num--p">{nLutas}/{CAT.sparring}</b><small>lutas</small>
            </ComDica>
          )}
          {rMega && !rMega.vinculo && (
            <ComDica className="evl-req" rotulo={`Vínculo ${virgula(m.vinc.valor)} de ${virgula(CMG.vinculo)}`} dica={<>Vínculo mínimo para o Mega: {virgula(CMG.vinculo)}.</>}>
              <Heart aria-hidden="true" /><b className="lg-num lg-num--p">{virgula(m.vinc.valor)}/{virgula(CMG.vinculo)}</b>
            </ComDica>
          )}
        </div>
      )}
      <Arvore m={m} />
      <div className="evl-bts">
        <details className="evl-det">
          <summary><History aria-hidden="true" />Histórico<ChevronRight className="lg-seta" aria-hidden="true" /></summary>
          <ol className="evl-hist">
            <li><span className="t">D1 {hhmm(TICK_INICIAL)}</span><span>nasceu: <b>{nomeForma({ esp: m.especie, est: "bebe" })}</b></span></li>
            {evs.map((x, i) => (
              <li key={i}><span className="t">D{diaDe(x.tick)} {hhmm(x.tick)}</span>
                <span>virou <b>{nomeForma(x.forma)}</b> ({det(x)})</span>
                <button type="button" className="evl-rever" aria-label={`Ver a revelação de novo: ${nomeForma(x.forma)}`} onClick={() => reverEvolucao(i)}>Ver a revelação de novo</button></li>
            ))}
          </ol>
        </details>
        {ult && (
          <details className="evl-det evl-porque">
            <summary><Info aria-hidden="true" />Porquê<ChevronRight className="lg-seta" aria-hidden="true" /></summary>
            <div className="revel-porque"><Porque x={ult} /></div>
          </details>
        )}
      </div>
      <ComoFunciona>
        Cada evolução é decidida pelo que o pet viveu: cuidado, caráter e lutas de treino. Uma moeda por transição (os contadores zeram a cada evolução).
        <b> In-Training → Rookie</b> ({m.dur.bebe / 60} h): o <b>cuidado</b> decide o ramo; o In-Training chama em horário fixo (fome a cada 30 min, higiene a cada 60, atenção a cada 45) e atender pelo menos 80% dos chamados em até 15 min dá Sereno, menos dá Arisco.
        <b> Rookie → Champion</b> ({m.dur.crianca / 60} h): o <b>caráter dominante</b> decide a linha e a técnica.
        <b> Champion → Ultimate</b> ({m.dur.adolescente / 60} h e 10 lutas de treino na arena): o <b>eixo complementar</b> da linha decide o arquétipo e a passiva (as duas formas da linha são o mesmo Ultimate).
        <b> Ultimate → Mega</b> ({m.dur.adulto / 60} h, {CAT.sparring} lutas com {pctVit}% ou mais de vitórias e vínculo {virgula(CMG.vinculo)} ou mais): o mesmo arquétipo, mais forte. A forma sombria não chega ao Mega.
        {" "}Cada evolução depois do Rookie pede também <b>medalhas do Tamer</b>: {CMD.adolescente} para virar Champion, {CMD.adulto} para Ultimate e {CMD.mega} para Mega. Se o pet cumpre o resto e falta medalha, ele espera pronto e evolui assim que você ganhar a medalha.
        {" "}Na árvore: o verde é o caminho, o claro é agora, o tracejado é possível, o pontilhado é fechado e o roxo é a sombria (sobrecarga alta na virada para Ultimate).
      </ComoFunciona>
    </div>
  );
}
