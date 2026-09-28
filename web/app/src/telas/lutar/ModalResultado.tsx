/* Resultado da luta (pranchas ResVitoria, ResDerrota, ResCampanha e ResDesktop; regras em ResNota e na secao 7 das
   DIRETRIZES_REPLICAR): modal sem x que abre sozinho no fim da luta, sobre a tela cheia congelada no ultimo turno.
   Continuar (ou Esc) volta para a aba de origem; Ver replay abre a luta no Diario. Blocos em ordem fixa, cada um so
   com dado do motor (bloco sem dado fica de fora): faixa (resultado, quem venceu, turnos) -> o que mudou (lugar
   aberto, numeros) -> o que decidiu a luta -> regra nova ou "nenhuma regra nova" -> progresso. Elogiar/Repreender
   uma acao da luta nao existe no motor e fica de fora (docs/PENDENCIAS_PRANCHAS.md). */
import { useEffect, useRef, useState } from "preact/hooks";
import { CAT, LUGARES, NOME_V2, NPC, chaveRegra, regraDe, rotuloRegra, type ResultadoLuta, type Turno } from "../../../motor/index.ts";
import { dimSprite, imagemAtlas, useAtlas } from "../../atlas.ts";
import { abrirModal } from "../../componentes/modal.ts";
import { Peca } from "../../componentes/Imagens.tsx";
import { mudarMotor, useJogo } from "../../jogo.ts";
import { tentativas, type LutadorTela, type Palco } from "../../luta.ts";
import { ILHA } from "./TelaCampanha.tsx";

const inteiro = (x: number): string => String(Math.round(x));

/** uma linha de "o que decidiu": o que cada lado fez no turno, o dano que causou e o que falhou */
export function fraseTurno(tr: Turno, A: LutadorTela, B: LutadorTela, travadas: Record<string, number> | null): string {
  const lados = ([0, 1] as const).map(i => {
    const L = i ? B : A, acao = i ? tr.b : tr.a, dano = tr.dano[1 - i];
    let s = `${L.nomeTela}: ${NOME_V2[acao] ?? acao}`;
    if (dano > 0) s += ` −${inteiro(dano)}`;
    if (tr.errou[i]) s += " (o pesado errou)";
    if (tr.interr[i]) s += " (pesado interrompido)";
    /* regra travada pelo dono que decidiu a acao do pet */
    const mot = i ? tr.mb : tr.ma, g = L.estilo.gambits;
    if (!i && travadas && typeof mot === "number" && g && mot < g.regras.length && chaveRegra(g.regras[mot]) in travadas) s += " · regra travada por você";
    return s;
  });
  return lados.join("; ") + ".";
}
/** os momentos que decidiram: ate dois turnos marcantes antes do ultimo, o ultimo e como acabou */
export function momentosDecisivos(res: ResultadoLuta, A: LutadorTela, B: LutadorTela, travadas: Record<string, number> | null): { t: string; txt: string; tom: "" | "bom" | "ruim" }[] {
  const n = res.turnos.length; if (!n) return [];
  const marcante = (tr: Turno) => tr.dano[0] > 0 || tr.dano[1] > 0 || tr.errou[0] || tr.errou[1] || tr.interr[0] || tr.interr[1]
    || [tr.a, tr.b].some(x => x === "preparar_pesado" || x === "fintar");
  /* turnos seguidos com a mesma frase viram um intervalo (T19–21) */
  const ult = res.turnos[n - 1], linhas: { t: string; txt: string; tom: "" | "bom" | "ruim" }[] = [];
  let ini = -1, fim = -1, txt = "";
  const fecha = () => { if (txt) linhas.push({ t: ini === fim ? `T${ini}` : `T${ini}–${fim}`, txt, tom: "" }); };
  for (const tr of [...res.turnos.slice(0, -1).filter(marcante).slice(-4), ult]) {
    const f = fraseTurno(tr, A, B, travadas);
    if (f === txt && tr.t === fim + 1) { fim = tr.t; continue; }
    fecha(); ini = fim = tr.t; txt = f;
  }
  fecha();
  linhas.splice(0, Math.max(0, linhas.length - 3));
  const hpA = res.E.L[0].hp, hpB = res.E.L[1].hp;
  if (res.fim === "ko") {
    const caiu = [hpA <= 0 && A.nomeTela, hpB <= 0 && B.nomeTela].filter(Boolean).join(" e ");
    return [...linhas, { t: `T${ult.t}`, txt: `${caiu} caiu.`, tom: res.pontosA === 1 ? "bom" : res.pontosA === 0 ? "ruim" : "" }];
  }
  return [...linhas, { t: `T${ult.t}`, txt: `Limite de turnos: vence quem tem mais vida (${inteiro(Math.max(0, hpA))} × ${inteiro(Math.max(0, hpB))}).`, tom: res.pontosA === 1 ? "bom" : res.pontosA === 0 ? "ruim" : "" }];
}

function Numeros({ itens }: { itens: [string, string][] }) {
  return <div class="res-nums">{itens.map(([v, r]) => <div class="res-num" key={r}><span class="dl-num">{v}</span><span>{r}</span></div>)}</div>;
}

export function ModalResultado({ p, continuar, verReplay }: { p: Palco; continuar: () => void; verReplay: (idx: number) => void }) {
  const ref = useRef<HTMLDialogElement>(null), replay = useRef(false);
  useEffect(() => { abrirModal(ref.current); }, []);
  const { motor: m } = useJogo(), a = useAtlas(), r = p.resultado!, res = r.res;
  const venceu = res.pontosA === 1, perdeu = res.pontosA === 0, empate = !venceu && !perdeu;
  const npc = r.npc ? NPC[r.npc]! : null, Li = npc ? npc.lug : -1;
  const lugarNovo = !!npc && venceu && !r.lugarJaVencido;
  /* regra nova: a que ficou ativa com a luta (antes de o dono mexer); fixada na abertura do modal */
  const [nova] = useState(() => {
    if (r.cenario || !r.ativasAntes || !r.ativasDepois) return null;
    const k = r.ativasDepois.find(x => !r.ativasAntes!.includes(x));
    return k ? { k, pos: r.ativasDepois.indexOf(k) + 1, de: r.ativasDepois.length } : null;
  });
  const [msgRegra, setMsgRegra] = useState("");
  const intervir = (op: "travar" | "vetar") => {
    try { mudarMotor(mm => mm.intervirGambit(op, nova!.k)); setMsgRegra(op === "vetar" ? "Vetada: o pet não usa mais esta regra." : "Travada nesta posição."); }
    catch (err) { setMsgRegra(err instanceof Error ? err.message : String(err)); }
  };
  const gp = m.gp, estadoNova = nova && gp ? (gp.vetos.includes(nova.k) ? "vetada" : nova.k in gp.travas ? "travada" : gp.ativas.includes(nova.k) ? "livre" : "fora") : null;
  const momentos = momentosDecisivos(res, p.A, p.B, gp ? gp.travas : null);

  const tag = npc ? `Campanha · ${LUGARES[Li].nome}` : "Arena · fim da luta";
  const titulo = lugarNovo ? "Ilha vencida!" : venceu ? "Vitória!" : perdeu ? "Derrota" : "Empate";
  const n = res.turnos.length;
  const sub = venceu ? `${p.A.nomeTela} venceu ${p.B.nomeTela} · ${n} turnos` : perdeu ? `${p.B.nomeTela} venceu no turno ${n}` : `Empate no limite · ${n} turnos`;
  const danoDado = res.turnos.reduce((s, tr) => s + tr.dano[1], 0), danoLevado = res.turnos.reduce((s, tr) => s + tr.dano[0], 0);
  const vencidos = LUGARES.filter((_, i) => m.lugarVencido(i)).length;
  const nums: [string, string][] = npc
    ? [[String(n), "turnos"], [String(tentativas(m, r.npc!)), "tentativas"], [`${vencidos} de ${LUGARES.length}`, "ilhas"]]
    : [[String(n), "turnos"], [inteiro(danoDado), "dano dado"], [inteiro(danoLevado), "dano levado"]];

  /* sprites: o vencedor grande, o perdedor apagado e menor; no empate os dois de pe */
  const spr = (L: LutadorTela, alvoM: number, alvoD: number) => {
    if (a.tipo !== "ok") return null;
    const img = imagemAtlas(a, L.sprite, 1, { sombria: L.sombra }), h = dimSprite(a.dados, L.sprite)[1];
    return { img, km: Math.max(1, Math.floor(alvoM / h)), kd: Math.max(1, Math.floor(alvoD / h)) };
  };
  const [ganhou, caido] = venceu ? [p.A, p.B] : perdeu ? [p.B, p.A] : [p.A, p.B];
  const sv = spr(ganhou, 112, 168), sc0 = spr(caido, empate ? 112 : 64, empate ? 168 : 96);
  /* o perdedor nunca maior que o vencedor */
  const sc = sc0 && sv && !empate ? { ...sc0, km: Math.min(sc0.km, sv.km), kd: Math.min(sc0.kd, sv.kd) } : sc0;
  const Img = ({ s, cls, L }: { s: NonNullable<typeof sv>; cls: string; L: LutadorTela }) => (
    <img class={`dl-pix ${cls}`} src={s.img.url} alt={cls === "res-caido" ? `${L.nomeTela} caído` : L.nomeTela}
      style={{ "--w": s.img.w, "--h": s.img.h, "--km": s.km, "--kd": s.kd }} />
  );

  const progresso = r.sparringContou ? Math.min(r.sparringAntes + 1, CAT.sparring) : null;
  const proximo = lugarNovo && Li < LUGARES.length - 1 ? Li + 1 : null;
  const ilha = proximo !== null && a.tipo === "ok" ? imagemAtlas(a, ILHA[proximo].peca).url : null;

  return (
    <dialog class={`modal-res res dl ${venceu ? "res--vit" : empate ? "res--emp" : "res--der"}`} ref={ref} aria-labelledby="res-tit"
      onClose={() => (replay.current && r.idxLog !== null ? verReplay(r.idxLog) : continuar())}>
      <div class={`res-faixa ${venceu ? "res-faixa--vit" : "res-faixa--der"}`}>
        <span class="res-tag">{tag}</span>
        <h2 class={`res-tit dl-num${titulo.length > 9 ? " res-tit--longo" : ""}`} id="res-tit">{titulo}</h2>
        <span class="res-sub">{sub}</span>
        <div class={`res-palco${empate ? " res-palco--empate" : ""}`} aria-hidden="true">
          <span class="res-anel" />
          {sc && <Img s={sc} cls={empate ? "res-lado2" : "res-caido"} L={caido} />}
          {sv && <Img s={sv} cls="res-venc" L={ganhou} />}
        </div>
        <div class="res-nums-faixa"><Numeros itens={nums} /></div>
      </div>
      <div class="res-lado">
        <div class="res-corpo">
          {lugarNovo && (proximo !== null
            ? <div class="res-ilha">
                <span class="res-ilha-img">{ilha && <img src={ilha} alt="" />}</span>
                <span class="res-ilha-txt"><span class="res-selo">aberta</span><b>{LUGARES[proximo].nome}</b>
                  <span>sugerido: {LUGARES[proximo].sugerido} · {LUGARES[proximo].rivais.length} {LUGARES[proximo].rivais.length === 1 ? "rival" : "rivais"}</span></span>
              </div>
            : <div class="res-ilha"><span class="res-ilha-txt"><span class="res-selo">concluída</span><b>Campanha concluída</b>
                <span>{p.A.nomeTela} venceu {LUGARES[Li].nome}, o último lugar do mapa.</span></span></div>)}
          <div class="res-nums-corpo"><Numeros itens={nums} /></div>
          {momentos.length > 0 && <section class="res-decidiu" aria-labelledby="res-dec-tit">
            <h3 id="res-dec-tit">O que decidiu a luta</h3>
            <ol>{momentos.map((l, i) => <li key={i}><span class={`res-t${l.tom ? " res-t--" + l.tom : ""}`}>{l.t}</span><span>{l.txt}</span></li>)}</ol>
          </section>}
          {r.cenario
            ? <div class="res-semregra"><span class="dl-num" aria-hidden="true">?</span><span>Contra pet de cenário o seu não aprende.</span></div>
            : nova
              ? <section class="res-regra dl-malha" aria-label="Regra nova">
                  <span class="res-regra-topo"><span>REGRA NOVA · aprendida lutando</span><span class="res-regra-pos">{nova.pos} de {nova.de}</span></span>
                  <span class="res-regra-txt">{rotuloRegra(regraDe(nova.k)).replace(/^se/, "Se")}</span>
                  {estadoNova === "livre" && !msgRegra && <span class="res-regra-bts">
                    <button type="button" class="regra-travar" onClick={() => intervir("travar")}><Peca nome="icone_cadeado" />Travar</button>
                    <button type="button" class="regra-vetar" onClick={() => intervir("vetar")}>Vetar</button></span>}
                  {msgRegra && <span class="res-regra-msg" role="status">{msgRegra}</span>}
                </section>
              : r.ativasAntes && <div class="res-semregra"><span class="dl-num" aria-hidden="true">?</span><span>Nenhuma regra nova desta vez.</span></div>}
          {progresso !== null && <div class="res-prog">
            <span class="res-prog-rot"><span>lutas de treino</span><span><b>+1</b> · {progresso} de {CAT.sparring}</span></span>
            <span class="res-prog-barra" role="img" aria-label={`lutas de treino: ${progresso} de ${CAT.sparring}`}>
              {Array.from({ length: CAT.sparring }, (_, i) => <i key={i} class={i < progresso ? "on" : ""} />)}</span>
          </div>}
        </div>
        <div class="res-rodape">
          {r.idxLog !== null && <button type="button" class="dl-btn dl-btn--sec res-replay" onClick={() => { replay.current = true; ref.current?.close(); }}>Ver replay</button>}
          <button type="button" class="dl-btn res-continuar" autofocus onClick={() => ref.current?.close()}>{proximo !== null ? "Ver o mapa" : "Continuar"}</button>
        </div>
      </div>
    </dialog>
  );
}
