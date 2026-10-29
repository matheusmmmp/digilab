/* Lutar · Arena em tempo real (docs/TAREFA_V2_UP_ARENA.md, secao 12), atras da chave ARENA_TEMPO_REAL. E o pet do jogador que luta,
   sozinho, pela IA da arena, contra um rival do mesmo estagio; o jogador assiste (correcao do Matheus, 2026-10-29: "a batalha em tempo
   real, mas e ele que joga, nao sou eu"). A simulacao e a de arena/ (passo fixo, sorteios com semente); esta tela so le a luta e desenha.
   Nada aqui toca no pet, no log ou no save: a luta nao da nem tira nada do pet. */
import { useEffect, useMemo, useRef, useState } from "react";
import {
  CENAS, IDS_CENA, MUNDO, OPCOES_PADRAO, PASSO_MS, STATS_PADRAO, criarLuta, passo, rivaisDoEstagio, sortearRival, sorteiosPorFluxo,
  type ConfigLuta, type Evento, type IdCena, type Lado, type Luta,
} from "../../../../arena/index.ts";
import { carregarArenaTr, falhasImagem, imagemArena, petNaArena, type EstadoArenaTr, type PacoteArena } from "../../../arenaTempoReal.ts";
import { useJogo } from "../../../jogo.ts";
import { aplicarEventosVisuais, arquivosCena, desenhar, indexarEfeitos, visualNovo, type Imagens, type Visual } from "./desenho.ts";
import { NOME_ATR, textoEvento } from "./log.ts";

/** o nivel do jogo dos dois lados na arena: 1 (PROPOSTO, SEM FONTE). O estagio do pet ja entra pelo status do Digimon dele
    (status.json, com EQ.pesoEstagio) e o rival e do mesmo estagio; somar um nivel pelo estagio contaria o estagio duas vezes */
const NIVEL_ARENA = 1;
const NOME_ESTAGIO: Record<string, string> = { InTraining1: "Bebê I", InTraining2: "In-Training", Rookie: "Rookie", Champion: "Champion", Ultimate: "Ultimate", Mega: "Mega", Armor: "Armor" };

let pedido: Promise<PacoteArena> | null = null;
function useDadosArena(): EstadoArenaTr {
  const [e, setE] = useState<EstadoArenaTr>({ tipo: "carregando" });
  useEffect(() => {
    let vivo = true;
    (pedido ??= carregarArenaTr()).then(p => { if (vivo) setE({ tipo: "ok", pacote: p }); }, (err: unknown) => {
      pedido = null; if (vivo) setE({ tipo: "erro", erro: err instanceof Error ? err.message : String(err) });
    });
    return () => { vivo = false; };
  }, []);
  return e;
}

export function TelaArenaTempoReal({ sair }: { sair: () => void }) {
  const estado = useDadosArena();
  return (
    <section className="painel arena-tr" aria-labelledby="arena-tr-titulo" data-testid="arena-tr">
      <div className="tela-cab dl-faixa">
        <h1 className="dl-num" id="arena-tr-titulo">Arena em tempo real</h1>
        <button type="button" className="dl-btn dl-btn--sec arena-tr-voltar" onClick={sair}>Voltar</button>
      </div>
      {estado.tipo === "carregando" && <p className="arena-tr-nota">Carregando os dados da arena…</p>}
      {estado.tipo === "erro" && (
        <div className="aviso" role="alert" data-testid="aviso-arena-tr">
          Os dados da arena em tempo real não carregaram.
          <p>{estado.erro}. Rode <code>python gerar_arena_up.py</code> em D:\Trab\digilab\Assets.</p>
        </div>
      )}
      {estado.tipo === "ok" && <Arena pacote={estado.pacote} />}
    </section>
  );
}

function Arena({ pacote }: { pacote: PacoteArena }) {
  const { dados, efeitos, recuos } = pacote;
  const jogo = useJogo();
  const pet = useMemo(() => petNaArena(jogo.nascendo > 0 ? null : jogo.motor.forma, dados), [jogo.nascendo, jogo.motor.forma, dados]);
  const candidatos = useMemo(() => (pet.ok ? rivaisDoEstagio(dados, pet.estagio, pet.nome) : []), [pet, dados]);
  const prefabs = useMemo(() => indexarEfeitos(efeitos), [efeitos]);
  const [cena, setCena] = useState<IdCena | "aleatoria">("coliseu");
  const [escolhaRival, setEscolhaRival] = useState<string>("sorteado");
  const [log, setLog] = useState<{ k: number; t: string; txt: string; lado: Lado | null }[]>([]);
  const [placar, setPlacar] = useState({ a: 0, b: 0, e: 0 });
  const [atual, setAtual] = useState<{ semente: number; cena: IdCena; rival: string } | null>(null);
  const [falhas, setFalhas] = useState<string[]>([]);
  const [erro, setErro] = useState<string | null>(null);
  const canvas = useRef<HTMLCanvasElement>(null);
  /* o estado vivo da luta fica em ref: o laco de quadros le e escreve sem re-render */
  const vivo = useRef<{ L: Luta; v: Visual; im: Imagens; acc: number; semente: number } | null>(null);
  const nLog = useRef(0);

  /** uma luta: o pet (azul, sozinho) contra o rival (vermelho), as duas pela IA; com `repetir`, a mesma semente, arena e rival */
  async function lutar(repetir?: { semente: number; cena: IdCena; rival: string }) {
    if (!pet.ok || candidatos.length === 0) return;
    const sd = repetir?.semente ?? Math.floor(Math.random() * 2 ** 31);
    const id: IdCena = repetir?.cena ?? (cena === "aleatoria" ? IDS_CENA.filter(k => k !== "campo")[Math.floor(Math.random() * (IDS_CENA.length - 1))] : cena);
    const rival = repetir?.rival ?? (escolhaRival === "sorteado" ? sortearRival(candidatos, sd) : escolhaRival);
    const lado = (n: string) => ({ equipe: [n], fonte: "jogo" as const, nivel: NIVEL_ARENA, generico: { ...STATS_PADRAO } });
    const cfg: ConfigLuta = { cena: id, dific: OPCOES_PADRAO.dific, forca: OPCOES_PADRAO.forca, ritmo: OPCOES_PADRAO.ritmo, pvel: OPCOES_PADRAO.pvel,
      jogador: false, a: lado(pet.nome), b: lado(rival) };
    /* as imagens antes da luta: sprites, as folhas dos efeitos dos golpes e os mapas da arena */
    const todos = [pet.nome, rival], donos = new Set(["_comum"]);
    for (const n of todos) {
      const g = dados.golpes[n]; if (!g) continue;
      for (const p of [g.proj?.prefab, g.skill?.proj?.prefab, ...g.hits.map(h => h.prefab), ...(g.skill?.hits ?? []).map(h => h.prefab)]) {
        const r = p ? prefabs.get(p.toLowerCase()) : undefined; if (r) donos.add(r.dono);
      }
    }
    const carregar = async (pasta: string, lista: string[]) => new Map(await Promise.all(lista.map(async n => [n, await imagemArena(`${pasta}/${pasta === "mapas" ? n : n + ".png"}`)] as const)));
    const im: Imagens = { sprites: await carregar("sprites", todos), folhas: await carregar("efeitos", [...donos]), mapas: await carregar("mapas", arquivosCena(id)) };
    setFalhas([...falhasImagem]);
    let L: Luta;
    try { L = criarLuta(cfg, dados, sorteiosPorFluxo(sd)); } catch (err) { setErro(err instanceof Error ? err.message : String(err)); return; }
    setErro(null);
    const inicio = L.eventos; L.eventos = [];
    vivo.current = { L, v: visualNovo(), im, acc: 0, semente: sd };
    nLog.current = 0;
    setLog([]); registrar(inicio, L);
    setAtual({ semente: sd, cena: id, rival });
  }

  function registrar(ev: Evento[], L: Luta) {
    const novas = ev.map(textoEvento).filter(x => x !== null).map(x => ({ k: nLog.current++, t: (L.relogio / 1000).toFixed(1).replace(".", ","), ...x }));
    if (novas.length) setLog(l => [...novas.reverse(), ...l].slice(0, 80));
    for (const e of ev) if (e.tipo === "fim") setPlacar(p => e.vencedor ? { ...p, [e.vencedor]: p[e.vencedor] + 1 } : { ...p, e: p.e + 1 });
  }

  /* comeca uma luta quando os dados chegam (so com um pet que pode lutar) */
  useEffect(() => { if (pet.ok) void lutar(); /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, [pet.ok]);

  /* o laco: acumula o tempo real e da passos fixos de PASSO_MS */
  useEffect(() => {
    let raf = 0, ultimo = 0;
    const quadro = (t: number) => {
      const dtReal = Math.min(50, t - (ultimo || t)); ultimo = t;
      const s = vivo.current, ctx = canvas.current?.getContext("2d");
      if (s && !s.L.fim) {
        s.acc += dtReal;
        const juntos: Evento[] = [];
        while (s.acc >= PASSO_MS && !s.L.fim) {
          const ev = passo(s.L);
          aplicarEventosVisuais(s.v, s.L, ev, prefabs); juntos.push(...ev); s.acc -= PASSO_MS;
        }
        if (juntos.length) registrar(juntos, s.L);
      } else if (s) aplicarEventosVisuais(s.v, s.L, [], prefabs);
      if (s && ctx) desenhar(ctx, s.L, s.v, s.im, prefabs);
      /* so leitura, para a conferencia (e2e) */
      if (s) (window as unknown as { __arenaTr?: object }).__arenaTr = { semente: s.semente, relogio: s.L.relogio, fim: s.L.fim, vencedor: s.L.vencedor, cena: s.L.cena.id, azul: s.L.eq.a.map(u => u.n), vermelho: s.L.eq.b.map(u => u.n) };
      raf = requestAnimationFrame(quadro);
    };
    raf = requestAnimationFrame(quadro);
    return () => cancelAnimationFrame(raf);
  }, [prefabs]);

  if (!pet.ok) return (
    <div className="arena-tr-corpo">
      <div className="aviso" role="alert" data-testid="aviso-arena-tr-pet">
        Seu pet não pode lutar na arena em tempo real.
        <p>Motivo: {pet.motivo}. Quem luta aqui é o seu pet, e só ele.</p>
      </div>
    </div>
  );
  if (candidatos.length === 0) return (
    <div className="arena-tr-corpo">
      <div className="aviso" role="alert" data-testid="aviso-arena-tr-pet">Não há rival do estágio do seu pet nos dados da arena.</div>
    </div>
  );

  return (
    <div className="arena-tr-corpo">
      {erro && <div className="aviso" role="alert">A luta não começou.<p>{erro}</p></div>}
      {falhas.length > 0 && (
        <div className="aviso" role="alert" data-testid="aviso-arena-tr-arte">
          Parte da arte da arena não carregou; esses Digimon e objetos aparecem como marcadores.
          <p>{falhas.slice(0, 6).join(", ")}{falhas.length > 6 ? ` e mais ${falhas.length - 6}` : ""}. Rode <code>python gerar_arena_up.py</code> em D:\Trab\digilab\Assets.</p>
        </div>
      )}
      <div className="arena-tr-palco dl-card">
        <p className="arena-tr-confronto" data-testid="arena-tr-confronto">
          <span className="arena-tr-azul" data-testid="arena-tr-pet">Seu pet: <b>{pet.tela}</b> ({NOME_ESTAGIO[pet.estagio] ?? pet.estagio}, {NOME_ATR[dados.atributos[pet.nome]] ?? dados.atributos[pet.nome]})</span>
          {atual && <span className="arena-tr-vermelho">Rival: <b>{atual.rival.replace(/_/g, " ")}</b> ({NOME_ATR[dados.atributos[atual.rival]] ?? dados.atributos[atual.rival]})</span>}
        </p>
        <canvas ref={canvas} className="arena-tr-canvas" width={MUNDO.w * MUNDO.esc} height={MUNDO.h * MUNDO.esc} aria-label="Arena da luta" />
        <div className="arena-tr-linha">
          <span className="arena-tr-placar" aria-label="Placar">Seu pet <b>{placar.a}</b> · Rival <b>{placar.b}</b> · Empates <b>{placar.e}</b></span>
          {atual && <span className="arena-tr-nota"><b>{CENAS[atual.cena].nome}.</b> {CENAS[atual.cena].desc}</span>}
          {atual && <span className="arena-tr-nota" data-testid="arena-tr-semente">semente {atual.semente}</span>}
        </div>
        <div className="arena-tr-acoes">
          <button type="button" className="dl-btn" onClick={() => void lutar()}>Lutar</button>
          <button type="button" className="dl-btn dl-btn--sec" onClick={() => atual && void lutar(atual)} disabled={!atual}>Revanche (mesma semente)</button>
          <label className="arena-tr-escolha">Arena <select aria-label="Arena" value={cena} onChange={e => setCena(e.target.value as IdCena | "aleatoria")}>
            <option value="aleatoria">Arena aleatória</option>{IDS_CENA.map(id => <option key={id} value={id}>{CENAS[id].nome}</option>)}</select></label>
          <label className="arena-tr-escolha">Rival <select aria-label="Rival" value={escolhaRival} onChange={e => setEscolhaRival(e.target.value)}>
            <option value="sorteado">Sorteado (mesmo estágio)</option>{candidatos.map(n => <option key={n} value={n}>{n.replace(/_/g, " ")}</option>)}</select></label>
        </div>
        <p className="arena-tr-nota">Seu pet luta sozinho, pela IA da arena; você assiste. A luta não muda nada no pet. A arena e o rival valem a partir da próxima luta.</p>
      </div>
      {(recuos.tag.length > 0 || recuos.semGolpe.length > 0) && (
        <details className="arena-tr-recuos dl-card" data-testid="recuos-arena-tr">
          <summary>Regras de recuo dos dados do jogo ({recuos.tag.length + recuos.semGolpe.length})</summary>
          {recuos.tag.length > 0 && <p>Sem a animação da habilidade no atlas, estes usam a do golpe: {recuos.tag.map(r => `${r.n} (${r.anim} → ${r.usa})`).join(", ")}.</p>}
          {recuos.semGolpe.length > 0 && <p>Sem script de ataque no jogo, estes usam o golpe genérico (corpo a corpo, 0,4 s): {recuos.semGolpe.join(", ")}.</p>}
        </details>
      )}
      <ol className="arena-tr-log dl-card" aria-label="Registro da luta" data-testid="arena-tr-log">
        {log.map(x => <li key={x.k} className={x.lado ?? ""}>{x.t}s {x.txt}</li>)}
      </ol>
      <p className="arena-tr-credito">Digimon, golpes, efeitos e mapas: DIGIMON UP (Bandai), com o crédito (docs/UI_GUIDELINES.md, seção 5.1). Números da arena PROPOSTOS.</p>
    </div>
  );
}
