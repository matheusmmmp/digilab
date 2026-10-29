/* Lutar · Arena em tempo real (docs/TAREFA_V2_UP_ARENA.md), atras da chave ARENA_TEMPO_REAL: equipes de 3 com troca, 8 arenas, atributo,
   habilidade com recarga, modo jogador (WASD ou setas, mouse para mirar, clique ou Espaco ataca, Q/E ou botao direito habilidade, Shift
   investida, 1/2/3 troca) e CPU x CPU. A simulacao e a de arena/ (passo fixo, sorteios com semente); esta tela so le a luta, desenha e
   manda a entrada do jogador como evento. Nada aqui toca no pet, no log ou no save. */
import { useEffect, useMemo, useRef, useState } from "react";
import {
  CENAS, DIFIC, FORCAS, IDS_CENA, MUNDO, OPCOES_PADRAO, PASSO_MS, RITMOS, STATS_PADRAO, criarLuta, passo, sorteiosPorFluxo,
  type ConfigLuta, type Dificuldade, type Entrada, type FonteStats, type IdCena, type Lado, type Luta,
} from "../../../../arena/index.ts";
import { carregarArenaTr, falhasImagem, imagemArena, type EstadoArenaTr, type PacoteArena } from "../../../arenaTempoReal.ts";
import { aplicarEventosVisuais, arquivosCena, desenhar, indexarEfeitos, visualNovo, type Imagens, type Visual } from "./desenho.ts";
import { NOME_ATR, textoEvento } from "./log.ts";

const PADRAO: Record<Lado, string[]> = { a: ["Agumon", "Gabumon", "Patamon"], b: ["Devimon", "Gomamon", "Palmon"] };  // Vacina, Dados e Virus dos dois lados
const VELOCIDADES = [0.25, 0.5, 1, 2, 4] as const;
const NOME_DIFIC: Record<Dificuldade, string> = { facil: "CPU fácil", normal: "CPU normal", dificil: "CPU difícil" };
const virgula = (x: number) => String(x).replace(".", ",");

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
  const nomes = useMemo(() => Object.keys(dados.atlas.d), [dados]);
  const prefabs = useMemo(() => indexarEfeitos(efeitos), [efeitos]);
  const inicial = (l: Lado) => (PADRAO[l].every(n => dados.atlas.d[n]) ? PADRAO[l] : [0, 1, 2].map(i => nomes[(i + (l === "a" ? 0 : 3)) % nomes.length]));
  const [equipes, setEquipes] = useState<Record<Lado, string[]>>({ a: inicial("a"), b: inicial("b") });
  const [cena, setCena] = useState<IdCena | "aleatoria">("coliseu");
  const [jogador, setJogador] = useState(true);
  const [dific, setDific] = useState<Dificuldade>(OPCOES_PADRAO.dific);
  const [ritmo, setRitmo] = useState<number>(OPCOES_PADRAO.ritmo);
  const [forca, setForca] = useState<number>(OPCOES_PADRAO.forca);
  const [vel, setVel] = useState(1);
  const [fonte, setFonte] = useState<Record<Lado, FonteStats>>({ a: "jogo", b: "jogo" });
  const [nivel, setNivel] = useState<Record<Lado, number>>({ a: 1, b: 1 });
  const [pausado, setPausado] = useState(false);
  const [log, setLog] = useState<{ k: number; t: string; txt: string; lado: Lado | null }[]>([]);
  const [placar, setPlacar] = useState({ a: 0, b: 0, e: 0 });
  const [semente, setSemente] = useState<number | null>(null);
  const [cenaAtual, setCenaAtual] = useState<IdCena | null>(null);
  const [falhas, setFalhas] = useState<string[]>([]);
  const [erro, setErro] = useState<string | null>(null);
  const canvas = useRef<HTMLCanvasElement>(null);
  /* o estado vivo da luta fica em ref: o laco de quadros le e escreve sem re-render */
  const vivo = useRef<{ L: Luta; v: Visual; im: Imagens; entradas: Entrada[]; acc: number } | null>(null);
  const opcoes = useRef({ vel, pausado }); opcoes.current = { vel, pausado };
  const nLog = useRef(0);

  const invalidos = (["a", "b"] as const).flatMap(l => equipes[l].filter(n => !dados.atlas.d[n]));

  async function lutar(sementeNova?: number) {
    if (invalidos.length) return;
    const id: IdCena = cena === "aleatoria" ? IDS_CENA.filter(k => k !== "campo")[Math.floor(Math.random() * (IDS_CENA.length - 1))] : cena;
    const sd = sementeNova ?? Math.floor(Math.random() * 2 ** 31);
    const lado = (l: Lado) => ({ equipe: equipes[l] as [string, string, string], fonte: fonte[l], nivel: nivel[l], generico: { ...STATS_PADRAO } });
    const cfg: ConfigLuta = { cena: id, dific, forca, ritmo, pvel: OPCOES_PADRAO.pvel, jogador, a: lado("a"), b: lado("b") };
    /* as imagens antes da luta: sprites, as folhas dos efeitos dos golpes e os mapas da arena */
    const todos = [...equipes.a, ...equipes.b], donos = new Set(["_comum"]);
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
    vivo.current = { L, v: visualNovo(), im, entradas: [], acc: 0 };
    nLog.current = 0;
    setLog([]); registrar(inicio, L);
    setSemente(sd); setCenaAtual(id); setPausado(false);
  }

  function registrar(ev: Parameters<typeof textoEvento>[0][], L: Luta) {
    const novas = ev.map(textoEvento).filter(x => x !== null).map(x => ({ k: nLog.current++, t: (L.relogio / 1000).toFixed(1).replace(".", ","), ...x }));
    if (novas.length) setLog(l => [...novas.reverse(), ...l].slice(0, 80));
    for (const e of ev) if (e.tipo === "fim") setPlacar(p => e.vencedor ? { ...p, [e.vencedor]: p[e.vencedor] + 1 } : { ...p, e: p.e + 1 });
  }

  /* comeca uma luta quando os dados chegam */
  useEffect(() => { void lutar(); /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, []);

  /* o laco: acumula o tempo real x velocidade e da passos fixos de PASSO_MS */
  useEffect(() => {
    let raf = 0, ultimo = 0;
    const quadro = (t: number) => {
      const dtReal = Math.min(50, t - (ultimo || t)); ultimo = t;
      const s = vivo.current, ctx = canvas.current?.getContext("2d");
      if (s && !opcoes.current.pausado && !s.L.fim) {
        s.acc += dtReal * opcoes.current.vel;
        const juntos = [];
        while (s.acc >= PASSO_MS && !s.L.fim) {
          const ev = passoComEntradas(s);
          aplicarEventosVisuais(s.v, s.L, ev, prefabs); juntos.push(...ev); s.acc -= PASSO_MS;
        }
        if (juntos.length) registrar(juntos, s.L);
      } else if (s && s.L.fim) aplicarEventosVisuais(s.v, s.L, [], prefabs);
      if (s && ctx) desenhar(ctx, s.L, s.v, s.im, prefabs);
      if (s) (window as unknown as { __arenaTr?: object }).__arenaTr = { semente: semRef.current, relogio: s.L.relogio, fim: s.L.fim, vencedor: s.L.vencedor, cena: s.L.cena.id };
      raf = requestAnimationFrame(quadro);
    };
    raf = requestAnimationFrame(quadro);
    return () => cancelAnimationFrame(raf);
  }, [prefabs]);
  const semRef = useRef<number | null>(null); semRef.current = semente;

  /* teclado (o jogador e a equipe azul): so com a luta do jogador, e so enquanto esta tela existe */
  useEffect(() => {
    const teclas = new Set<string>();
    const CONTROLE = new Set(["w", "a", "s", "d", "arrowup", "arrowdown", "arrowleft", "arrowright", " ", "shift", "1", "2", "3", "q", "e"]);
    const enviar = (e: Entrada) => { const s = vivo.current; if (s && s.L.cfg.jogador) s.entradas.push(e); };
    const mover = () => {
      const mx = (teclas.has("d") || teclas.has("arrowright") ? 1 : 0) - (teclas.has("a") || teclas.has("arrowleft") ? 1 : 0);
      const my = (teclas.has("s") || teclas.has("arrowdown") ? 1 : 0) - (teclas.has("w") || teclas.has("arrowup") ? 1 : 0);
      enviar({ tipo: "mover", mx: mx as -1 | 0 | 1, my: my as -1 | 0 | 1 });
    };
    const baixo = (ev: KeyboardEvent) => {
      const k = ev.key.toLowerCase(), s = vivo.current;
      if (!CONTROLE.has(k) || !s || !s.L.cfg.jogador || (ev.target as HTMLElement)?.closest?.("input, select")) return;
      ev.preventDefault();
      if (k === " ") enviar({ tipo: "atacar" });
      else if (k === "q" || k === "e") enviar({ tipo: "habilidade" });
      else if (k === "1" || k === "2" || k === "3") enviar({ tipo: "trocar", slot: +k - 1 });
      else if (k === "shift") enviar({ tipo: "investida", ligada: true });
      else { teclas.add(k); mover(); }
    };
    const cima = (ev: KeyboardEvent) => {
      const k = ev.key.toLowerCase();
      if (k === "shift") enviar({ tipo: "investida", ligada: false });
      else if (teclas.delete(k)) mover();
    };
    const limpar = () => { teclas.clear(); mover(); };
    addEventListener("keydown", baixo); addEventListener("keyup", cima); addEventListener("blur", limpar);
    return () => { removeEventListener("keydown", baixo); removeEventListener("keyup", cima); removeEventListener("blur", limpar); };
  }, []);

  const noMundo = (ev: React.PointerEvent<HTMLCanvasElement>): [number, number] => {
    const r = ev.currentTarget.getBoundingClientRect();
    return [(ev.clientX - r.left) * MUNDO.w / r.width, (ev.clientY - r.top) * MUNDO.h / r.height];
  };
  const enviar = (e: Entrada) => { const s = vivo.current; if (s && s.L.cfg.jogador) s.entradas.push(e); };
  const s = vivo.current;

  return (
    <div className="arena-tr-corpo">
      {erro && <div className="aviso" role="alert">A luta não começou.<p>{erro}</p></div>}
      {falhas.length > 0 && (
        <div className="aviso" role="alert" data-testid="aviso-arena-tr-arte">
          Parte da arte da arena não carregou; esses Digimon e objetos aparecem como marcadores.
          <p>{falhas.slice(0, 6).join(", ")}{falhas.length > 6 ? ` e mais ${falhas.length - 6}` : ""}. Rode <code>python gerar_arena_up.py</code> em D:\Trab\digilab\Assets.</p>
        </div>
      )}
      {(recuos.tag.length > 0 || recuos.semGolpe.length > 0) && (
        <details className="arena-tr-recuos dl-card" data-testid="recuos-arena-tr">
          <summary>Regras de recuo dos dados do jogo ({recuos.tag.length + recuos.semGolpe.length})</summary>
          {recuos.tag.length > 0 && <p>Sem a animação da habilidade no atlas, estes usam a do golpe: {recuos.tag.map(r => `${r.n} (${r.anim} → ${r.usa})`).join(", ")}.</p>}
          {recuos.semGolpe.length > 0 && <p>Sem script de ataque no jogo, estes usam o golpe genérico (corpo a corpo, 0,4 s): {recuos.semGolpe.join(", ")}.</p>}
          {recuos.semStatus.length > 0 && <p>Sem registro de status no jogo ({recuos.semStatus.length}), estes usam os status genéricos.</p>}
        </details>
      )}
      <div className="arena-tr-palco dl-card">
        <canvas ref={canvas} className="arena-tr-canvas" width={MUNDO.w * MUNDO.esc} height={MUNDO.h * MUNDO.esc} aria-label="Arena da luta"
          onPointerMove={ev => enviar({ tipo: "mira", ...ponto(noMundo(ev)) })}
          onPointerLeave={() => enviar({ tipo: "sem_mira" })}
          onPointerDown={ev => { enviar({ tipo: "mira", ...ponto(noMundo(ev)) }); enviar(ev.button === 2 ? { tipo: "habilidade" } : { tipo: "atacar" }); }}
          onContextMenu={ev => ev.preventDefault()} />
        <div className="arena-tr-linha">
          <span className="arena-tr-placar" aria-label="Placar">Azul <b>{placar.a}</b> · Vermelha <b>{placar.b}</b> · Empates <b>{placar.e}</b></span>
          {cenaAtual && <span className="arena-tr-nota"><b>{CENAS[cenaAtual].nome}.</b> {CENAS[cenaAtual].desc}</span>}
          {semente !== null && <span className="arena-tr-nota" data-testid="arena-tr-semente">semente {semente}</span>}
        </div>
        <div className="arena-tr-acoes">
          <button type="button" className="dl-btn" onClick={() => void lutar()} disabled={invalidos.length > 0}>{s ? "Recomeçar" : "Lutar"}</button>
          <button type="button" className="dl-btn dl-btn--sec" onClick={() => semente !== null && void lutar(semente)} disabled={semente === null || invalidos.length > 0}>Revanche (mesma semente)</button>
          <button type="button" className="dl-btn dl-btn--sec" onClick={() => setPausado(p => !p)}>{pausado ? "Continuar" : "Pausar"}</button>
          <button type="button" className="dl-btn dl-btn--sec" onClick={() => {
            const ns = nomes.filter(n => dados.golpes[n]);
            setEquipes({ a: [0, 1, 2].map(() => ns[Math.floor(Math.random() * ns.length)]), b: [0, 1, 2].map(() => ns[Math.floor(Math.random() * ns.length)]) });
          }}>Sortear equipes</button>
        </div>
        {jogador && <p className="arena-tr-nota">Você é a equipe azul: WASD ou setas andam, o mouse mira, clique ou Espaço ataca, Q/E ou botão direito usa a habilidade, Shift faz a investida, 1/2/3 trocam.</p>}
      </div>
      <div className="arena-tr-opcoes dl-card">
        <label>Arena <select aria-label="Arena" value={cena} onChange={e => setCena(e.target.value as IdCena | "aleatoria")}>
          <option value="aleatoria">Arena aleatória</option>{IDS_CENA.map(id => <option key={id} value={id}>{CENAS[id].nome}</option>)}</select></label>
        <label>Modo <select aria-label="Modo" value={jogador ? "jogador" : "cpu"} onChange={e => setJogador(e.target.value === "jogador")}>
          <option value="jogador">Você (azul) × CPU</option><option value="cpu">CPU × CPU</option></select></label>
        <label>Dificuldade <select aria-label="Dificuldade" value={dific} onChange={e => setDific(e.target.value as Dificuldade)}>
          {(Object.keys(DIFIC) as Dificuldade[]).map(d => <option key={d} value={d}>{NOME_DIFIC[d]}</option>)}</select></label>
        <label>Ritmo <select aria-label="Ritmo" value={ritmo} onChange={e => setRitmo(+e.target.value)}>
          {RITMOS.map(r => <option key={r} value={r}>Vida do jogo ÷ {r}</option>)}</select></label>
        <label>Atributo <select aria-label="Atributo" value={forca} onChange={e => setForca(+e.target.value)}>
          {FORCAS.map(f => <option key={f} value={f}>{f === 1 ? "Atributo desligado" : `Vantagem ${virgula(f)}×`}</option>)}</select></label>
        <label>Velocidade <select aria-label="Velocidade" value={vel} onChange={e => setVel(+e.target.value)}>
          {VELOCIDADES.map(v => <option key={v} value={v}>{virgula(v)}×</option>)}</select></label>
        <datalist id="arena-tr-nomes">{nomes.map(n => <option key={n} value={n} />)}</datalist>
        {(["a", "b"] as const).map(l => (
          <fieldset key={l} className={`arena-tr-equipe arena-tr-equipe--${l}`}>
            <legend>Equipe {l === "a" ? "azul" : "vermelha"}</legend>
            {equipes[l].map((n, i) => (
              <label key={i}>Digimon {i + 1}
                <input list="arena-tr-nomes" value={n} aria-invalid={!dados.atlas.d[n]} onChange={e => setEquipes(q => ({ ...q, [l]: q[l].map((x, j) => j === i ? e.target.value : x) }))} />
                <small>{dados.atlas.d[n] ? NOME_ATR[dados.atributos[n]] ?? dados.atributos[n] : "Nome não encontrado: escolha um da lista."}</small>
              </label>
            ))}
            <label>Status <select value={fonte[l]} onChange={e => setFonte(f => ({ ...f, [l]: e.target.value as FonteStats }))}>
              <option value="jogo">Do jogo</option><option value="generico">Genéricos</option></select></label>
            <label>Nível <input type="number" min={1} max={60} value={nivel[l]} onChange={e => setNivel(v => ({ ...v, [l]: Math.max(1, Math.min(60, Math.round(+e.target.value) || 1)) }))} /></label>
          </fieldset>
        ))}
        <p className="arena-tr-nota">As opções valem a partir da próxima luta (Lutar ou Recomeçar). Números da arena PROPOSTOS (docs/TAREFA_V2_UP_ARENA.md).</p>
      </div>
      <ol className="arena-tr-log dl-card" aria-label="Registro da luta" data-testid="arena-tr-log">
        {log.map(x => <li key={x.k} className={x.lado ?? ""}>{x.t}s {x.txt}</li>)}
      </ol>
      <p className="arena-tr-credito">Digimon, golpes, efeitos e mapas: DIGIMON UP (Bandai), com o crédito (docs/UI_GUIDELINES.md, seção 5.1).</p>
    </div>
  );
}

const ponto = ([x, y]: [number, number]) => ({ x, y });
/** um passo da simulacao com as entradas do jogador juntadas desde o passo anterior */
function passoComEntradas(s: { L: Luta; entradas: Entrada[] }) {
  const e = s.entradas; s.entradas = [];
  return passo(s.L, e);
}
