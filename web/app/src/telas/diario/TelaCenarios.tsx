/* Cenarios (Lab; porte do HTML): monta dois pets com donos simulados (mesmo codigo do rival da arena). O pet A
   vira o pet do jogador (o anterior fica guardado para voltar) e o B vira o rival fixo da arena. Mostra lado a
   lado estado, sinal de aprendizado e JSD da politica media ao prior; 100 lutas A x B. Ferramenta de inspecao
   do porte, nao resultado de pesquisa: uma semente, outro RNG, sem IC. */
import { useState } from "react";
import {
  ACOES_PET, ACOES_V2_OBS, CA, NOME_BOT, NOME_COMB, NOME_DONO, NOME_V2, afinidades, corDominante, hashSemente, jogarLuta, lutadorPet, tamanhoLuta,
  nomeForma, observacao, treinarPet, type Motor, type Observacao, type TipoDono,
} from "../../../motor/index.ts";
import { comSinal, dec } from "../../componentes/Barras.tsx";
import { jogoAtual, trocarMotor, useJogo } from "../../jogo.ts";
import { LUTA, previa, useLuta } from "../../luta.ts";
import { CHAVE_ANTERIOR, voltarAoAnterior } from "../pet/MeusPets.tsx";
import { textoSave } from "../../save.ts";

interface Lado { dono: TipoDono; dias: number; porDia: number }
interface Cenario { id: string; titulo: string; desc?: string; a: Lado; b: Lado }
const CENARIOS: Cenario[] = [
  { id: "adulto-bebe", titulo: "Ultimate bem cuidado × In-Training aleatório", desc: "A: atencioso, 6 dias, 40 interações/dia. B: aleatório, 2 horas (ainda In-Training), 8/dia.",
    a: { dono: "atencioso", dias: 6, porDia: 40 }, b: { dono: "aleatorio", dias: .1, porDia: 8 } },
  { id: "controle", titulo: "Controle da pesquisa", desc: "Atencioso × aleatório, 5 dias, 16/dia nos dois. É a comparação do portão.",
    a: { dono: "atencioso", dias: 5, porDia: 16 }, b: { dono: "aleatorio", dias: 5, porDia: 16 } },
  { id: "orcamento", titulo: "Mesmo dono, orçamento diferente", desc: "Atencioso nos dois, 5 dias. A com 40/dia, B com 6/dia.",
    a: { dono: "atencioso", dias: 5, porDia: 40 }, b: { dono: "atencioso", dias: 5, porDia: 6 } },
  { id: "negligenciado", titulo: "Ultimate negligenciado × Rookie cuidado", desc: "A: relapso, 6 dias, 4/dia. B: atencioso, meio dia (ainda Rookie), 24/dia.",
    a: { dono: "relapso", dias: 6, porDia: 4 }, b: { dono: "atencioso", dias: .5, porDia: 24 } },
  { id: "incoerente", titulo: "Incoerente × atencioso", desc: "Mesmo volume (16/dia, 5 dias). Só a coerência do feedback muda.",
    a: { dono: "incoerente", dias: 5, porDia: 16 }, b: { dono: "atencioso", dias: 5, porDia: 16 } },
];
/* observacao da arena V1 (HP cheio dos dois): onde o HTML compara a politica ao prior */
const OBS_ARENA: Observacao = { v: [CA.fome, CA.hig, 1, .5, CA.saude, 0, 0, CA.hora], tdc: 0 };
function jsdBits(p: Record<string, number>, q: Record<string, number>): number {
  let s = 0;
  for (const a of ACOES_PET) {
    const m = (p[a] + q[a]) / 2;
    if (p[a] > 0) s += .5 * p[a] * Math.log2(p[a] / m);
    if (q[a] > 0) s += .5 * q[a] * Math.log2(q[a] / m);
  }
  return s;
}
function resumoPet(m: Motor, spec: Lado): Record<string, string | number> {
  const e = m.e, r = m.pol.rec, af = afinidades(m.tracos), dom = corDominante(m.tracos), pm = m.pol.media(OBS_ARENA);
  return {
    dono: NOME_DONO[spec.dono], idade: `${spec.dias} d · ${nomeForma(m.forma)}`, porDia: spec.porDia, total: m.log.filter(x => x[1] === "d").length,
    saude: e.saude, fome: e.fome, higiene: e.higiene, humor: e.humor,
    elogio: r.elogio, repreensao: r.repreensao, atendido: r.atendido, ignorado: r.ignorado,
    atualizacoes: ACOES_PET.reduce((t, a) => t + m.pol.bracos[a].n, 0),
    jsdAgora: jsdBits(m.pol.media(observacao(e)), m.pol.prior(observacao(e))), jsdArena: jsdBits(pm, m.pol.prior(OBS_ARENA)),
    topo: m.gp ? m.gp.linha! : "ao acaso (In-Training)", dom: `${NOME_COMB[dom]} ${comSinal(af[dom], 3)}`,
  };
}
/* o cenario montado fica entre as trocas de aba (como no HTML) */
let atual: { cen: Cenario; semente: number; ra: Record<string, string | number>; rb: Record<string, string | number> } | null = null;
let lutasTxt: { resumo: string; nota: string; linhas: [string, string, string][] } | null = null;

const pct = (v: string | number): string => ((v as number) * 100).toFixed(0) + "%";
const temAnterior = (): boolean => { try { return !!localStorage.getItem(CHAVE_ANTERIOR); } catch { return false; } };

export function TelaCenarios() {
  useJogo(); useLuta();
  const [msg, setMsg] = useState<{ txt: string; erro?: boolean } | null>(atual ? { txt: `${atual.cen.titulo} · semente ${atual.semente}. O pet A agora é o seu.` } : null);
  const [, setRev] = useState(0);
  const [form, setForm] = useState({ ca: { dono: "atencioso", dias: "5", pd: "16" }, cb: { dono: "aleatorio", dias: "5", pd: "16" }, semente: "1" });
  const comEspera = (fn: () => void) => {
    setMsg({ txt: "Treinando os dois pets…" });
    setTimeout(() => { try { fn(); } catch (err) { setMsg({ txt: err instanceof Error ? err.message : String(err), erro: true }); } }, 30);
  };
  const montar = (cen: Cenario, semente: number) => {
    const sa = hashSemente("cenario", cen.id, semente, "a"), sb = hashSemente("cenario", cen.id, semente, "b");
    const A = treinarPet(cen.a.dono, cen.a.dias, cen.a.porDia, sa), B = treinarPet(cen.b.dono, cen.b.dias, cen.b.porDia, sb);
    /* o pet atual fica guardado para o botao de voltar; so o registro e salvo, como sempre */
    try { if (!localStorage.getItem(CHAVE_ANTERIOR)) localStorage.setItem(CHAVE_ANTERIOR, textoSave(jogoAtual().motor)); } catch { /* sem armazenamento */ }
    trocarMotor(A, "save");
    LUTA.rivalFixo = { rival: B, dias: cen.b.dias, tipo: cen.b.dono };
    previa("arena");
    atual = { cen, semente, ra: resumoPet(A, cen.a), rb: resumoPet(B, cen.b) };
    lutasTxt = null;
    setMsg({ txt: `${cen.titulo} · semente ${semente}. O pet A agora é o seu.` });
  };
  const lerNumero = (v: string, rot: string): number => { const n = Number(v); if (!Number.isFinite(n) || n <= 0) throw new Error(`${rot}: valor inválido`); return n; };
  const montarAMao = () => comEspera(() => {
    const semente = lerNumero(form.semente, "Semente");
    if (!Number.isInteger(semente)) throw new Error("Semente precisa ser inteira");
    const lado = (p: "ca" | "cb"): Lado => ({ dono: form[p].dono as TipoDono, dias: lerNumero(form[p].dias, "Dias de vida"), porDia: lerNumero(form[p].pd, "Interações/dia") });
    const a = lado("ca"), b = lado("cb");
    montar({ id: "manual", titulo: `${NOME_DONO[a.dono]} × ${NOME_DONO[b.dono]}`, a, b }, semente);
  });
  const rodarLutas = (n: number) => {
    const fixo = LUTA.rivalFixo;
    if (!fixo) throw new Error("monte um cenário antes");
    const m = jogoAtual().motor, A = lutadorPet(m, "Pet A"), B = lutadorPet(fixo.rival, "Pet B");
    const contA: Record<string, number> = {}, contB: Record<string, number> = {};
    for (const c of ACOES_V2_OBS) { contA[c] = 0; contB[c] = 0; }
    /* acoes: os turnos (por turnos) ou as acoes de cada lado (pets v13, em tempo real); dur: turnos ou segundos */
    let v = 0, d = 0, e = 0, dur = 0, acoesA = 0, acoesB = 0, lim = 0;
    for (let k = 0; k < n; k++) {
      const r = jogarLuta(A, B, hashSemente("lab", m.semente, m.log.length, k), m.regras);
      if (r.pontosA === 1) v++; else if (r.pontosA === 0) d++; else e++;
      dur += tamanhoLuta(r); lim += r.fim === "limite" ? 1 : 0;
      for (const t of r.turnos) { contA[t.a]++; contB[t.b]++; acoesA++; acoesB++; }
      if (r.tr) for (const x of r.tr.acoes) { if (x.lado === 0) { contA[x.nome]++; acoesA++; } else { contB[x.nome]++; acoesB++; } }
    }
    const tempoReal = !!m.regras?.tempoReal;
    lutasTxt = {
      resumo: `${n} lutas: A ${v} vitórias, B ${d}, ${e} empates. A fez ${((v + e / 2) / n * 100).toFixed(0)}% dos pontos. Média de ${(dur / n).toFixed(1).replace(".", ",")} ${tempoReal ? "s" : "turnos"}; ${lim} no limite.`,
      nota: `A luta com as regras de combate aprendidas dele (semente: ${NOME_BOT[A.estilo.base!] || A.estilo.base}); B com os dele (semente: ${NOME_BOT[B.estilo.base!] || B.estilo.base}). Estas lutas não ensinam nenhum dos dois.`,
      linhas: ACOES_V2_OBS.map(c => [NOME_V2[c], pct(contA[c] / acoesA), pct(contB[c] / acoesB)]),
    };
    setRev(x => x + 1);
  };
  const voltar = () => {
    try { setMsg({ txt: voltarAoAnterior() }); } catch (err) { setMsg({ txt: err instanceof Error ? err.message : String(err), erro: true }); return; }
    LUTA.rivalFixo = null; previa("arena"); atual = null; lutasTxt = null;
  };
  const L = (rot: string, k: string, f: (x: string | number) => string | number = x => x) => <tr key={k}><td>{rot}</td><td>{f(atual!.ra[k])}</td><td>{f(atual!.rb[k])}</td></tr>;
  const sec = (t: string) => <tr className="sec" key={t}><td colSpan={3}>{t}</td></tr>;
  const bits = (x: string | number) => dec(x as number, 4);
  const campo = (p: "ca" | "cb", k: "dias" | "pd", rot: string, min: string, max: string, passo: string) => (
    <label>{rot} <input type="number" min={min} max={max} step={passo} value={form[p][k]} onChange={ev => setForm({ ...form, [p]: { ...form[p], [k]: (ev.target as HTMLInputElement).value } })} /></label>
  );
  const dono = (p: "ca" | "cb") => (
    <label>Dono simulado <select value={form[p].dono} onChange={ev => setForm({ ...form, [p]: { ...form[p], dono: (ev.target as HTMLSelectElement).value } })}>
      {Object.entries(NOME_DONO).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select></label>
  );
  return (
    <div className="tela dl">
      <div className="lab-intro dl-malha"><b>FERRAMENTA DE PESQUISA</b>
        <span>Monte dois pets com donos simulados e compare o que cada um aprendeu. O pet A vira o seu; o B vira o rival fixo da arena. Mesma semente, mesmo resultado.</span></div>
      <fieldset className="lab-pet lab-pet--a"><legend>Pet A · vira o seu</legend>{dono("ca")}{campo("ca", "dias", "Dias de vida", "0.5", "14", "0.5")}{campo("ca", "pd", "Interações por dia", "1", "200", "1")}</fieldset>
      <fieldset className="lab-pet lab-pet--b"><legend>Pet B · rival fixo</legend>{dono("cb")}{campo("cb", "dias", "Dias de vida", "0.5", "14", "0.5")}{campo("cb", "pd", "Interações por dia", "1", "200", "1")}</fieldset>
      <label className="lab-semente">Semente <input id="c-semente" className="campo-num" type="number" min="1" step="1" value={form.semente} onChange={ev => setForm({ ...form, semente: (ev.target as HTMLInputElement).value })} /></label>
      <p className="lab-nota">Simular troca o seu pet atual. Dá para voltar ao anterior em Meus pets. Os pets simulados são da versão sem medalhas: evoluem sem o Tamer e não ganham medalhas.</p>
      <button type="button" className="dl-btn dl-btn--largo" onClick={montarAMao}>Simular e comparar</button>
      <details className="dl-apoio"><summary>Cenários prontos</summary>
        <div className="cenarios">
          {CENARIOS.map(c => <button type="button" key={c.id} className="cen" onClick={() => comEspera(() => montar(c, 1))}><b>{c.titulo}</b><span>{c.desc}</span></button>)}
        </div>
      </details>
      {msg && <p className={msg.erro ? "erro" : "resultado"} aria-live="polite">{msg.txt}</p>}
      {atual && <div className="tabela-rola"><table className="comp"><thead><tr><th /><th>A (seu)</th><th>B (rival)</th></tr></thead><tbody>
        {sec("Perfil")}{L("Dono", "dono")}{L("Idade", "idade")}{L("Interações/dia", "porDia")}{L("Interações no total", "total")}
        {sec("Estado no fim")}{L("Saúde", "saude", pct)}{L("Saciedade", "fome", pct)}{L("Higiene", "higiene", pct)}{L("Humor", "humor", pct)}
        {sec("Sinal de aprendizado")}{L("Elogios", "elogio")}{L("Repreensões", "repreensao")}{L("Pedidos atendidos", "atendido")}{L("Pedidos ignorados", "ignorado")}{L("Atualizações do bandit", "atualizacoes")}
        {sec("Quanto o aprendizado afastou a política do prior (JSD, bits)")}{L("No estado atual", "jsdAgora", bits)}{L("Na arena (HP cheio)", "jsdArena", bits)}
        {sec("Na arena")}{L("Regras de combate semeadas por", "topo")}{L("Traço dominante", "dom")}
      </tbody></table></div>}
      <div className="dl-linha">
        <button type="button" className="dl-btn" disabled={!LUTA.rivalFixo} onClick={() => { try { rodarLutas(100); } catch (err) { setMsg({ txt: String(err instanceof Error ? err.message : err), erro: true }); } }}>Rodar 100 lutas A × B</button>
        {temAnterior() && <button type="button" className="dl-btn dl-btn--sec" onClick={voltar}>Voltar ao pet anterior</button>}
      </div>
      {lutasTxt && <div className="tabela-rola">
        <p className="resultado">{lutasTxt.resumo}</p><p className="dl-apoio">{lutasTxt.nota}</p>
        <table className="comp"><thead><tr><th>Ação usada</th><th>A</th><th>B</th></tr></thead><tbody>{lutasTxt.linhas.map(([a, x, y]) => <tr key={a}><td>{a}</td><td>{x}</td><td>{y}</td></tr>)}</tbody></table>
      </div>}
    </div>
  );
}
