/* Resultado da luta (pranchas ResVitoria, ResDerrota, ResCampanha e ResDesktop; regras em ResNota e na secao 7 das
   DIRETRIZES_REPLICAR): modal sem x que abre sozinho no fim da luta, sobre a tela cheia congelada no ultimo turno.
   Continuar (ou Esc) volta para a aba de origem; Ver replay abre a luta no Diario. Blocos em ordem fixa, cada um so
   com dado do motor (bloco sem dado fica de fora): faixa (resultado, quem venceu, segundos) -> o que mudou (lugar
   aberto, numeros) -> por que (as regras que dispararam na luta em tempo real e o saldo delas) -> regra nova ou "nenhuma regra nova" ->
   progresso. Elogiar/Repreender
   uma acao da luta nao existe no motor e fica de fora (docs/PENDENCIAS_PRANCHAS.md). */
import { useEffect, useRef, useState } from "react";
import { CAT, MEDALHAS, NPC, PASSO_TR_MS, cartaDe, chaveRegra, fatorExibicao, itemDe, regraDe, rotuloRegra, type ResultadoLuta, duracaoLuta, tamanhoLuta } from "../../../motor/index.ts";
import { dimSprite, imagemAtlas, useAtlas } from "../../atlas.ts";
import { abrirModal } from "../../componentes/modal.ts";
import { Peca } from "../../componentes/Imagens.tsx";
import { jogoAtual, mudarMotor, tamerAtual, useJogo } from "../../jogo.ts";
import { tentativas, type LutadorTela, type Palco } from "../../luta.ts";
import { mapaDe } from "./TelaCampanha.tsx";
import { textoRegra } from "./palcoTR/PalcoTR.tsx";
import { SeloMedalha } from "../../componentes/Medalha.tsx";
import { pedirDica } from "../../dicas.ts";

const inteiro = (x: number): string => Math.round(x).toLocaleString("pt-BR");

/** uma linha do "por que": o que levou o pet a agir (a regra, a exploracao, o pesado preparado), quantas vezes e o saldo de dano dessas
    acoes (o causado menos o recebido enquanto cada uma durou, em fracao da vida maxima do comeco; motor/combate_tr, AcaoRegistro) */
export interface LinhaPorque { rotulo: string; vezes: number; saldo: number; travada: boolean }
/** o "por que" da luta em tempo real: as acoes do pet agrupadas pelo motivo, as de maior saldo (a favor ou contra) primeiro; ate `max` */
export function porqueTR(res: ResultadoLuta, A: LutadorTela, travadas: Record<string, number> | null, max = 5): LinhaPorque[] {
  if (!res.tr) throw new Error("luta sem o tempo real: o porquê só existe nas lutas dos pets v13");
  const g = A.estilo.gambits, por = new Map<string, LinhaPorque>();
  for (const x of res.tr.acoes) {
    if (x.lado !== 0) continue;
    const rotulo = textoRegra({ motivo: x.motivo, nome: x.nome }, A), l = por.get(rotulo);
    if (l) { l.vezes++; l.saldo += x.saldo; continue; }
    const travada = !!travadas && typeof x.motivo === "number" && !!g && x.motivo < g.regras.length && chaveRegra(g.regras[x.motivo]) in travadas;
    por.set(rotulo, { rotulo, vezes: 1, saldo: x.saldo, travada });
  }
  return [...por.values()].sort((a, b) => Math.abs(b.saldo) - Math.abs(a.saldo) || b.vezes - a.vezes).slice(0, max);
}
/** o saldo em pontos da vida maxima, com o sinal ("+12%", "−3%") */
export const saldoTexto = (x: number): string => { const v = Math.round(x * 100); return v === 0 ? "0%" : (v > 0 ? "+" : "−") + Math.abs(v) + "%"; };
/** como a luta acabou, numa linha */
export function comoAcabou(res: ResultadoLuta, A: LutadorTela, B: LutadorTela, desafiado = false): string {
  const hpA = res.E.L[0].hp, hpB = res.E.L[1].hp, s = res.tr ? Math.round(res.tr.passos * PASSO_TR_MS / 1000) : 0;
  if (res.fim === "ko") return `${[hpA <= 0 && A.nomeTela, hpB <= 0 && B.nomeTela].filter(Boolean).join(" e ")} caiu aos ${s} s.`;
  if (desafiado) return `Limite de tempo sem nocaute: a luta fica com quem foi desafiado (${B.nomeTela}).`;
  return `Limite de tempo: vence quem tem mais vida (${inteiro(Math.max(0, hpA) * fatorExibicao(A.cond, jogoAtual().motor.versao))} × ${inteiro(Math.max(0, hpB) * fatorExibicao(B.cond, jogoAtual().motor.versao))}).`;
}
/** o bloco do "por que" (o Resultado e o replay do Diario) */
export function PorqueLuta({ res, A, B, travadas, desafiado }: { res: ResultadoLuta; A: LutadorTela; B: LutadorTela; travadas: Record<string, number> | null; desafiado: boolean }) {
  const linhas = porqueTR(res, A, travadas);
  return (
    <section className="res-decidiu" aria-labelledby="res-dec-tit">
      <h3 id="res-dec-tit">Por quê</h3>
      <ol>
        {linhas.map(l => <li key={l.rotulo}><span className={`res-t${l.saldo > .005 ? " res-t--bom" : l.saldo < -.005 ? " res-t--ruim" : ""}`}>{saldoTexto(l.saldo)}</span>
          <span>{l.rotulo} · {l.vezes}×{l.travada ? " · regra travada por você" : ""}</span></li>)}
        <li><span className={`res-t${res.pontosA === 1 ? " res-t--bom" : res.pontosA === 0 ? " res-t--ruim" : ""}`}>fim</span><span>{comoAcabou(res, A, B, desafiado)}</span></li>
      </ol>
      <p className="dl-apoio res-porque-nota">O saldo de cada regra: o dano que o pet causou menos o que levou enquanto agia por ela, em % da vida.</p>
    </section>
  );
}

function Numeros({ itens }: { itens: [string, string][] }) {
  return <div className="res-nums">{itens.map(([v, r]) => <div className="res-num" key={r}><span className="dl-num">{v}</span><span>{r}</span></div>)}</div>;
}

export function ModalResultado({ p, continuar, verReplay }: { p: Palco; continuar: () => void; verReplay: (idx: number) => void }) {
  const ref = useRef<HTMLDialogElement>(null), replay = useRef(false);
  useEffect(() => { abrirModal(ref.current); }, []);
  const { motor: m } = useJogo(), a = useAtlas(), r = p.resultado!, res = r.res;
  const venceu = res.pontosA === 1, perdeu = res.pontosA === 0, empate = !venceu && !perdeu;
  const npc = r.npc ? NPC[r.npc]! : null, Li = npc ? m.lugarDe(r.npc!) : -1, LUGARES = m.lugares;
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
  /* tutorial (Bit): a primeira derrota na campanha e a primeira regra nova */
  useEffect(() => { if (npc && perdeu) pedirDica("derrota_campanha"); if (nova) pedirDica("regra_nova"); }, []);

  /* a Liga dos Lideres (Fronteira, pets v6): a tentativa inteira; vencer as 6 e o titulo */
  const liga = r.lideres, venceuLiga = !!liga && r.serie.length === r.nLutas && venceu;
  /* uma instalacao da Fronteira (pets v6): a sequencia de vitorias ate a primeira que nao foi; o recorde do Tamer, se bateu */
  const inst = r.instalacao, vitInst = inst ? r.serie.filter(x => x.pontosA === 1).length : 0, rivaisLista = liga ?? r.rivais;
  const tag = liga ? "Fronteira · Liga dos Líderes" : inst ? `Fronteira · ${inst.nome}` : npc ? `Campanha · ${LUGARES[Li].nome}` : "Arena · fim da luta";
  const titulo = liga ? (venceuLiga ? "Campeão!" : perdeu ? "Derrota" : "Empate") : inst ? (r.recorde ? "Recorde!" : "Fim da sequência")
    : lugarNovo ? "Ilha vencida!" : venceu ? "Vitória!" : perdeu ? "Derrota" : "Empate";
  const dur = duracaoLuta(res);
  if (!res.tr) throw new Error("luta sem o tempo real: o Resultado só mostra as lutas dos pets v13");
  const durNum: [string, string] = [String(tamanhoLuta(res)), "segundos"];
  /* lutas seguidas (Cidadela e Liga): o resultado e o da serie; "n turnos" e o da ultima luta */
  const serie = r.nLutas > 1 ? r.serie : null;
  const sub = inst
    ? `${vitInst} vitória${vitInst === 1 ? "" : "s"} seguida${vitInst === 1 ? "" : "s"}; ${venceu ? `venceu as ${r.serie.length} lutas` : `parou na luta ${r.serie.length}, contra ${r.rivais![r.serie.length - 1].nomeTela}`}`
    : liga
    ? (venceuLiga ? `${p.A.nomeTela} venceu os ${r.nLutas} líderes seguidos` : `A Liga parou na luta ${r.serie.length} de ${r.nLutas}, contra ${liga[r.serie.length - 1].nomeTela}`)
    : serie
    ? (venceu ? `${p.A.nomeTela} venceu as ${r.nLutas} lutas seguidas` : `A série parou na luta ${serie.length} de ${r.nLutas}`)
    : venceu ? `${p.A.nomeTela} venceu ${p.B.nomeTela} · ${dur}` : perdeu ? `${p.B.nomeTela} venceu · ${dur}` : `Empate no limite · ${dur}`;
  /* dano na escala de quem recebeu (com a escala de stats, a campanha mostra os números grandes) */
  /* o dano e a vida que cada um perdeu (a cura da carta volta a somar no do pet) */
  const curaA = res.tr.curou[0] ? Math.max(0, res.E.L[0].hp - res.E0.L[0].hp) : 0;
  const danoDado = (res.E0.L[1].hp - res.E.L[1].hp) * fatorExibicao(p.B.cond, m.versao),
    danoLevado = (res.E0.L[0].hp - res.E.L[0].hp + curaA) * fatorExibicao(p.A.cond, m.versao);
  const vencidos = LUGARES.filter((_, i) => m.lugarVencido(i)).length;
  const recordeTamer = inst ? tamerAtual().recorde(inst.id) : null;
  const nums: [string, string][] = inst
    ? [[String(vitInst), "vitórias seguidas"], [String(m.instalacoes[inst.id].tentativas), "tentativas"], [String(recordeTamer?.valor ?? 0), "recorde"]]
    : liga
    ? [durNum, [String(m.liga.tentativas), "tentativas"], [`${r.serie.filter(x => x.pontosA === 1).length} de ${r.nLutas}`, "lutas vencidas"]]
    : npc
    ? [durNum, [String(tentativas(m, r.npc!)), "tentativas"], [`${vencidos} de ${LUGARES.length}`, "ilhas"]]
    : [durNum, [inteiro(danoDado), "dano dado"], [inteiro(danoLevado), "dano levado"]];

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
    <img className={`dl-pix ${cls}`} src={s.img.url} alt={cls === "res-caido" ? `${L.nomeTela} caído` : L.nomeTela}
      style={{ "--w": s.img.w, "--h": s.img.h, "--km": s.km, "--kd": s.kd }} />
  );

  const progresso = r.sparringContou ? Math.min(r.sparringAntes + 1, CAT.sparring) : null;
  const proximo = lugarNovo && Li < LUGARES.length - 1 ? Li + 1 : null;
  /* as ilhas do mapa da versao do pet (os v5 tem a Montanha Espiral; os v6, as seis arenas) */
  const ilhas = mapaDe(m).ilhas;
  const ilha = proximo !== null && a.tipo === "ok" ? imagemAtlas(a, ilhas[proximo].peca).url : null;
  const md = r.medalha, mdNum = md ? MEDALHAS.findIndex(x => x.id === md.id) + 1 : 0, mdInfo = md ? MEDALHAS[mdNum - 1] : null;

  return (
    <dialog className={`modal-res res dl ${venceu ? "res--vit" : empate ? "res--emp" : "res--der"}`} ref={ref} aria-labelledby="res-tit"
      onClose={() => (replay.current && r.idxLog !== null ? verReplay(r.idxLog) : continuar())}>
      <div className={`res-faixa ${venceu ? "res-faixa--vit" : "res-faixa--der"}`}>
        <span className="res-tag">{tag}</span>
        <h2 className={`res-tit dl-num${titulo.length > 9 ? " res-tit--longo" : ""}`} id="res-tit">{titulo}</h2>
        <span className="res-sub">{sub}</span>
        <div className={`res-palco${empate ? " res-palco--empate" : ""}`} aria-hidden="true">
          <span className="res-anel" />
          {sc && <Img s={sc} cls={empate ? "res-lado2" : "res-caido"} L={caido} />}
          {sv && <Img s={sv} cls="res-venc" L={ganhou} />}
        </div>
        <div className="res-nums-faixa"><Numeros itens={nums} /></div>
      </div>
      <div className="res-lado">
        <div className="res-corpo">
          {lugarNovo && (proximo !== null
            ? <div className="res-ilha">
                <span className="res-ilha-img">{ilha && <img src={ilha} alt="" />}</span>
                <span className="res-ilha-txt"><span className="res-selo">aberta</span><b>{LUGARES[proximo].nome}</b>
                  <span>sugerido: {LUGARES[proximo].sugerido} · {LUGARES[proximo].rivais.length} {LUGARES[proximo].rivais.length === 1 ? "rival" : "rivais"}</span></span>
              </div>
            : <div className="res-ilha"><span className="res-ilha-txt"><span className="res-selo">concluída</span><b>Campanha concluída</b>
                <span>{p.A.nomeTela} venceu {LUGARES[Li].nome}, o último lugar do mapa.</span></span></div>)}
          {md && mdInfo && <div className="res-medalha" role="status">
            <SeloMedalha n={mdNum} ganha tam={40} />
            <span className="res-ilha-txt"><span className="res-selo">medalha nova</span><b>{mdInfo.nome}</b>
              <span>O Tamer tem {md.n} de {MEDALHAS.length}. Ela é sua: vale para todos os seus pets.</span></span>
          </div>}
          {r.itens.map(x => { const it = itemDe(x.id); return (
            <div className="res-item" role="status" key={x.n}>
              <span className="res-ilha-txt"><span className="res-selo">{x.origem === "medalha" ? "item novo" : "carta da revanche"}</span><b>{it.nome}</b>
                <span>{it.efeito} {it.tipo === "carta" ? "Escolha antes de uma luta." : "Equipe em Crescer · Itens."}</span></span>
            </div>); })}
          {r.carta && <p className="res-carta" role="note">Carta usada: <b>{cartaDe(r.carta).nome}</b>. {cartaDe(r.carta).efeito}{res.tr.curou[0] ? " Ela curou o pet nesta luta." : ""}</p>}
          {r.titulo && <div className="res-titulo" role="status">
            <SeloMedalha n={0} ouro ganha tam={40} />
            <span className="res-ilha-txt"><span className="res-selo">medalha de ouro</span><b>Campeão da Liga dos Líderes</b>
              <span>{r.titulo.n === 1 ? "O título é seu, Tamer: a jornada chegou ao fim." : `${r.titulo.forma} também venceu a Liga (título ${r.titulo.n}).`}</span></span>
          </div>}
          {r.recorde && inst && <div className="res-titulo res-recorde" role="status">
            <span className="res-recorde-num dl-num" aria-hidden="true">{r.recorde.valor}</span>
            <span className="res-ilha-txt"><span className="res-selo">recorde novo</span><b>{inst.nome}</b>
              <span>{r.recorde.valor} vitória{r.recorde.valor === 1 ? "" : "s"} seguida{r.recorde.valor === 1 ? "" : "s"}: o recorde agora é seu, Tamer, com {r.recorde.forma}.</span></span>
          </div>}
          {serie && <section className="res-serie" aria-labelledby="res-serie-tit">
            <h3 id="res-serie-tit">{liga ? `Liga dos Líderes · ${r.nLutas} lutas seguidas, sem cura` : inst ? `${inst.nome} · ${r.nLutas} lutas seguidas, sem cura` : `Resistência · ${r.nLutas} lutas seguidas, sem cura`}</h3>
            <ol>{Array.from({ length: r.nLutas }, (_, i) => {
              const x = serie[i], fimVida = x ? Math.max(0, x.E.L[0].hp) / x.E.L[0].hpMax : 0;
              return <li key={i} className={!x ? "res-serie-nao" : x.pontosA === 1 ? "res-serie-vit" : "res-serie-der"}>
                <span className="res-t">Luta {i + 1}</span>
                <span>{rivaisLista ? <><b>{rivaisLista[i].nomeTela}</b> ({rivaisLista[i].estiloTela}): </> : null}{!x ? "não chegou a lutar" : `${x.pontosA === 1 ? "venceu" : x.pontosA === 0 ? "perdeu" : "empatou"} em ${duracaoLuta(x)} · terminou com ${Math.round(fimVida * 100)}% da vida`}</span>
              </li>;
            })}</ol>
          </section>}
          {inst?.regra === "sozinho" && <p className="res-arena-nota" role="note">Palácio: {p.A.nomeTela} lutou sem as suas travas, vetos e chips de regra, com as regras que ele mesmo escolheu.</p>}
          {r.arena?.regra === "vinculo" && <p className="res-arena-nota" role="note">Arena do Lago: {p.A.nomeTela} lutou sem as suas travas e vetos, com as regras que ele mesmo escolheu.</p>}
          <div className="res-nums-corpo"><Numeros itens={nums} /></div>
          <PorqueLuta res={res} A={p.A} B={p.B} travadas={gp ? gp.travas : null} desafiado={!r.cenario && m.desafiado === 1} />
          {r.cenario
            ? <div className="res-semregra"><span className="dl-num" aria-hidden="true">?</span><span>Contra pet de cenário o seu não aprende.</span></div>
            : nova
              ? <section className="res-regra dl-malha" aria-label="Regra nova">
                  <span className="res-regra-topo"><span>REGRA NOVA · aprendida lutando</span><span className="res-regra-pos">{nova.pos} de {nova.de}</span></span>
                  <span className="res-regra-txt">{rotuloRegra(regraDe(nova.k)).replace(/^se/, "Se")}</span>
                  {estadoNova === "livre" && !msgRegra && <span className="res-regra-bts">
                    <button type="button" className="regra-travar" onClick={() => intervir("travar")}><Peca nome="icone_cadeado" />Travar</button>
                    <button type="button" className="regra-vetar" onClick={() => intervir("vetar")}>Vetar</button></span>}
                  {msgRegra && <span className="res-regra-msg" role="status">{msgRegra}</span>}
                </section>
              : r.ativasAntes && <div className="res-semregra"><span className="dl-num" aria-hidden="true">?</span><span>Nenhuma regra nova desta vez.</span></div>}
          {progresso !== null && <div className="res-prog">
            <span className="res-prog-rot"><span>lutas de treino</span><span><b>+1</b> · {progresso} de {CAT.sparring}</span></span>
            <span className="res-prog-barra" role="img" aria-label={`lutas de treino: ${progresso} de ${CAT.sparring}`}>
              {Array.from({ length: CAT.sparring }, (_, i) => <i key={i} className={i < progresso ? "on" : ""} />)}</span>
          </div>}
        </div>
        <div className="res-rodape">
          {r.idxLog !== null && <button type="button" className="dl-btn dl-btn--sec res-replay" onClick={() => { replay.current = true; ref.current?.close(); }}>Ver replay</button>}
          <button type="button" className="dl-btn res-continuar" data-autofocus onClick={() => ref.current?.close()}>{proximo !== null ? "Ver o mapa" : "Continuar"}</button>
        </div>
      </div>
    </dialog>
  );
}
