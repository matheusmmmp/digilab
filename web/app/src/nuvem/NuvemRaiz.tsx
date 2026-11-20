/* As telas do save na nuvem (CN3; a prancha docs/pranchas/ux-conta-nuvem/, UX-NV-1 a 6 APROVADAS em 2026-11-20): levar o pet para a conta
   (tela 3), a conta que já tem pets (UX-NV-1: "Guardar os dois" marcada; UX-NV-2: o não escolhido vai para as cópias), o pet aberto em outro
   aparelho, as duas histórias com "Decidir depois" (UX-NV-4), "atualize o jogo", o servidor fora do ar (UX-NV-6: uma vez) e "entre de novo";
   o estado da nuvem no lugar do "salvo" do relógio (UX-NV-3, ChipNuvem) e a trava do "só ver" (UX-NV-5: a classe nv-so-ver no <html> apaga
   as ações; a trava do registro é a do src/jogo.ts).

   A chave: sem `nuvemNoBuild()` (VITE_DIGILAB_API e VITE_DIGILAB_NUVEM=1 no build), a raiz não liga nada, o chip não aparece e o jogo é o de
   sempre. As cópias do save ficam em Ajustes › Conta (CopiasDoSave), e as histórias não escolhidas em Diário › Gerações. */
import { useEffect, useRef, useState, useSyncExternalStore } from "react";
import { Cloud, CloudCheck, CloudOff, CloudUpload, Eye, Info, Monitor, RotateCcw, TriangleAlert } from "lucide-react";
import { VERSOES_PET } from "../../motor/index.ts";
import { nuvemNoBuild, apiDoBuild } from "../conta/apiDoBuild.ts";
import { CT, ouvirConta } from "../conta/conta.ts";
import { abrirModal } from "../componentes/modal.ts";
import { BotaoHx } from "../componentes/hx/index.ts";
import { gravarPendente, recarregarDoArmazenamento, travarAcoes } from "../jogo.ts";
import {
  INTERVALO_SYNC_MS, NV, abrirNuvem, agoraNao, conhecerVersoes, escolherHistoria, jogarAqui, levarParaConta, lerPacoteLocal, ligarNuvem,
  listarCopias, nuvemLigada, ouvirNuvem, restaurarCopia, revisaoNuvem, sincronizar, soVer, verAvisoFora, type Copia, type EscolhaLevar,
} from "./cliente.ts";
import "../estilo/menus_config.css";
import "../estilo/conta.css";
import "../estilo/nuvem.css";

const hhmm = (t: number): string => new Date(t).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
const diaDoJogo = (tick: number): number => Math.floor(tick / 1440) + 1;
/** uma ação de um clique: o erro alto vai para o console e a tela diz "não deu" */
function agir(f: () => Promise<void>, erro: (t: string) => void): void { f().catch((err: unknown) => { console.error(err); erro("Não deu. Nada mudou."); }); }

/* o que a tela já dispensou nesta abertura ("Agora não", "Só ver", "Decidir depois", "Depois") */
const dispensado = new Set<string>();
let revDisp = 0;
const ouvDisp = new Set<() => void>();
const dispensar = (k: string): void => { dispensado.add(k); revDisp++; for (const f of ouvDisp) f(); };
/** reabre o aviso da vez ou das duas histórias (o toque no chip "Só ver") */
export function abrirAvisoNuvem(): void { dispensado.delete("outro"); dispensado.delete("divergiu"); revDisp++; for (const f of ouvDisp) f(); }
function useDispensado(): number { return useSyncExternalStore(f => { ouvDisp.add(f); return () => { ouvDisp.delete(f); }; }, () => revDisp); }
export function useNuvem(): typeof NV | null {
  useSyncExternalStore(ouvirNuvem, revisaoNuvem);
  return nuvemLigada() ? NV : null;
}

let ligou = false;
function ligar(): void {
  if (ligou || !nuvemNoBuild()) return;
  ligou = true;
  conhecerVersoes(VERSOES_PET);
  ligarNuvem({
    api: apiDoBuild(), buscar: (u, i) => fetch(u, i),
    armaz: localStorage, chaves: () => Object.keys(localStorage), agora: () => Date.now(),
    aoMudarLocal: recarregarDoArmazenamento, travar: travarAcoes,
  });
}

/** a raiz: liga a nuvem (com a chave), sincroniza de tempos em tempos e mostra o aviso do momento */
export function NuvemRaiz() {
  const nv = useNuvem();
  useDispensado();
  useEffect(() => {
    ligar();
    if (!nuvemLigada()) return;
    void abrirNuvem().catch((err: unknown) => console.error(err));
    /* a conta que acabou de entrar (Ajustes › Conta) abre a nuvem de novo */
    let passo = CT.passo?.tipo;
    const desligarConta = ouvirConta(() => {
      const p = CT.passo?.tipo;
      if (p === "conta" && passo !== "conta" && ["sem_conta", "sessao"].includes(NV.estado)) void abrirNuvem().catch((err: unknown) => console.error(err));
      passo = p;
    });
    const t = setInterval(() => { void sincronizar().catch((err: unknown) => console.error(err)); }, INTERVALO_SYNC_MS);
    /* ao esconder a aba: grava o que está pendente e manda */
    const esconder = () => { if (document.visibilityState === "hidden") { gravarPendente(); void sincronizar().catch((err: unknown) => console.error(err)); } };
    document.addEventListener("visibilitychange", esconder);
    /* "sincronize agora", sem esperar o intervalo (o e2e da nuvem, e2e_conta/nuvem.spec.ts): o mesmo sincronizar de sempre */
    const agora = () => { void sincronizar().catch((err: unknown) => console.error(err)); };
    addEventListener("digilab-nuvem-sincronizar", agora);
    return () => { clearInterval(t); document.removeEventListener("visibilitychange", esconder); removeEventListener("digilab-nuvem-sincronizar", agora); desligarConta(); };
  }, []);
  const travado = nv !== null && soVer();
  useEffect(() => { document.documentElement.classList.toggle("nv-so-ver", travado); }, [travado]);
  if (!nv) return null;
  const e = nv.estado, livre = (k: string) => !dispensado.has(k);
  if (e === "sem_pet" && livre("levar")) return <Levar />;
  if (e === "ja_tem" && livre("levar")) return <Escolher />;
  if (e === "outro" && livre("outro")) return <OutroAparelho />;
  if (e === "divergiu" && livre("divergiu")) return <DuasHistorias />;
  if (e === "atualize" && livre("atualize")) return <Atualize />;
  if (e === "offline" && !nv.avisoForaVisto) return <ForaDoAr />;
  if (e === "sessao" && livre("sessao")) return <EntreDeNovo />;
  return null;
}

/* ------------------------------------------------------------ o diálogo */
function Aviso({ id, rot, icone, children, fechar }: { id: string; rot: string; icone: React.ReactNode; children: React.ReactNode; fechar: () => void }) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => { abrirModal(ref.current); }, []);
  return (
    <dialog className="mc-dialogo nv-aviso" ref={ref} aria-labelledby={`${id}-tit`} data-testid={id} onClose={fechar}>
      <section className="hx-painel nv-painel">
        <header className="nv-cab"><span className="ct-rot">{icone}{rot}</span></header>
        <div className="ct">{children}</div>
      </section>
    </dialog>
  );
}
const fecharDialogo = (el: HTMLElement | null): void => { el?.closest("dialog")?.close(); };
function ErroLinha({ erro }: { erro: string | null }) { return erro ? <p className="mc-erro" role="alert">{erro}</p> : null; }

/** o que este aparelho tem: o pet ativo, os guardados, Gerações e o Tamer (só o que existe) */
function Daqui() {
  const p = lerPacoteLocal(), x = p?.extras ?? {};
  const n = (k: string) => { try { const v = JSON.parse(x[Object.keys(x).find(c => c.endsWith(k)) ?? ""] ?? "[]") as unknown; return Array.isArray(v) ? v.length : 0; } catch { return 0; } };
  const g = n("-guardados"), ger = n("-geracoes");
  return (
    <ul className="nv-lista">
      <li><b>O pet ativo</b><small>{p ? `${p.save.log.length} eventos` : "ainda sem save"}</small></li>
      {g > 0 && <li><b>{g} {g === 1 ? "guardado" : "guardados"}</b></li>}
      {ger > 0 && <li><b>Gerações</b><small>{ger} {ger === 1 ? "vida" : "vidas"}</small></li>}
      <li><b>O Tamer</b><small>medalhas, Bits e itens</small></li>
    </ul>
  );
}

/** tela 3: levar o pet para a conta (a conta sem pet) */
function Levar() {
  const [erro, setErro] = useState<string | null>(null), ref = useRef<HTMLDivElement>(null);
  const tem = lerPacoteLocal() !== null;
  return (
    <Aviso id="nv-levar" rot="Conta" icone={<CloudUpload aria-hidden="true" />} fechar={() => dispensar("levar")}>
      <p className="ct-chamada" id="nv-levar-tit">Levar os pets para a conta</p>
      <div><span className="ct-rot">Neste aparelho</span><Daqui /></div>
      <p className="ct-sec nv-linha"><Info aria-hidden="true" />A conversa e o laboratório não sobem.</p>
      <ErroLinha erro={erro} />
      <div className="ct-bts" ref={ref}>
        <BotaoHx data-autofocus disabled={!tem || NV.ocupado} data-testid="nv-levar-sim" onClick={() => agir(async () => { await levarParaConta("levar"); fecharDialogo(ref.current); }, setErro)}>
          <CloudUpload aria-hidden="true" />Levar para a conta</BotaoHx>
        <BotaoHx onClick={() => { agoraNao(); fecharDialogo(ref.current); }}>Agora não</BotaoHx>
      </div>
      <p className="ct-sec">Eles continuam também neste aparelho.</p>
    </Aviso>
  );
}

/** tela 3, a conta já tem pets: as três respostas; "Guardar os dois" vem marcada (UX-NV-1) */
function Escolher() {
  const [qual, setQual] = useState<EscolhaLevar>(() => (lerPacoteLocal() ? "os_dois" : "nuvem")), [erro, setErro] = useState<string | null>(null), ref = useRef<HTMLDivElement>(null);
  const r = NV.resumo;
  const op = (v: EscolhaLevar, tit: string, sub: string) => (
    <button type="button" role="radio" aria-checked={qual === v} className="nv-op" onClick={() => setQual(v)} data-testid={`nv-op-${v}`}>
      <span className="nv-radio" aria-hidden="true" /><span><b>{tit}</b><small>{sub}</small></span></button>);
  return (
    <Aviso id="nv-escolher" rot="Conta" icone={<Cloud aria-hidden="true" />} fechar={() => dispensar("levar")}>
      <p className="ct-chamada" id="nv-escolher-tit">A conta já tem pets</p>
      <div className="nv-lados">
        <div className="nv-lado"><span className="ct-rot"><Monitor aria-hidden="true" />Neste aparelho</span><Daqui /></div>
        <div className="nv-lado"><span className="ct-rot"><Cloud aria-hidden="true" />Na nuvem</span>
          {r && <><b>{r.forma}</b><small>dia {diaDoJogo(r.tick)}{r.guardados ? ` · ${r.guardados} ${r.guardados === 1 ? "guardado" : "guardados"}` : ""}{r.aparelho ? ` · do ${r.aparelho}` : ""}</small></>}</div>
      </div>
      <div><span className="ct-rot" id="nv-qual">O que fica</span>
        <div className="nv-opcoes" role="radiogroup" aria-labelledby="nv-qual">
          {op("os_dois", "Guardar os dois", "O pet deste aparelho segue ativo. O da nuvem entra nos guardados.")}
          {op("aparelho", "Ficar com os deste aparelho", "Os da nuvem vão para as cópias, por 30 dias.")}
          {op("nuvem", "Ficar com os da nuvem", "Os deste aparelho vão para as cópias, por 30 dias.")}
        </div></div>
      <ErroLinha erro={erro} />
      <div className="ct-bts" ref={ref}>
        <BotaoHx data-autofocus disabled={NV.ocupado || (qual !== "nuvem" && lerPacoteLocal() === null)} data-testid="nv-continuar"
          onClick={() => agir(async () => { await levarParaConta(qual); fecharDialogo(ref.current); }, setErro)}>Continuar</BotaoHx>
        <BotaoHx onClick={() => { agoraNao(); fecharDialogo(ref.current); }}>Agora não</BotaoHx>
      </div>
    </Aviso>
  );
}

/** tela 5: o pet aberto em outro aparelho, com "Jogar aqui" e "Só ver" */
function OutroAparelho() {
  const [erro, setErro] = useState<string | null>(null), ref = useRef<HTMLDivElement>(null), v = NV.vez;
  const nome = v?.aparelho ?? "outro aparelho";
  return (
    <Aviso id="nv-outro" rot="Outro aparelho" icone={<Eye aria-hidden="true" />} fechar={() => dispensar("outro")}>
      <p className="ct-chamada" id="nv-outro-tit">Este pet está aberto no {nome}</p>
      <p className="ct-sec">{v?.desde ? `Desde as ${hhmm(v.desde)}. ` : ""}Aqui ele fica só para ver.</p>
      <ErroLinha erro={erro} />
      <div className="ct-bts" ref={ref}>
        <BotaoHx data-autofocus disabled={NV.ocupado} data-testid="nv-jogar-aqui" onClick={() => agir(async () => { await jogarAqui(); fecharDialogo(ref.current); }, setErro)}>
          <Monitor aria-hidden="true" />Jogar aqui</BotaoHx>
        <BotaoHx data-testid="nv-so-ver" onClick={() => fecharDialogo(ref.current)}>Só ver</BotaoHx>
      </div>
      <p className="ct-sec nv-linha"><Info aria-hidden="true" />Jogar aqui fecha a vez do {nome}. O que ele já enviou fica.</p>
    </Aviso>
  );
}

/** tela 5: as duas histórias; nenhuma marcada; "Decidir depois" deixa o pet só para ver nos dois aparelhos (UX-NV-4) */
function DuasHistorias() {
  const [qual, setQual] = useState<"nuvem" | "outra" | null>(null), [erro, setErro] = useState<string | null>(null), ref = useRef<HTMLDivElement>(null);
  const d = NV.divergencia;
  if (!d) return null;
  const lado = (k: "nuvem" | "outra") => {
    const l = d[k];
    return (
      <button type="button" role="radio" aria-checked={qual === k} className="nv-lado nv-op" onClick={() => setQual(k)} data-testid={`nv-historia-${k}`}>
        <span className="ct-rot"><span className="nv-radio" aria-hidden="true" />{l.aparelho}</span><b>{l.forma} · dia {diaDoJogo(l.tick)}</b>
        <small>{l.eventos_novos} {l.eventos_novos === 1 ? "evento novo" : "eventos novos"}</small>{l.ultimo && <small>o último: {l.ultimo}</small>}</button>);
  };
  return (
    <Aviso id="nv-divergiu" rot="Duas histórias" icone={<RotateCcw aria-hidden="true" />} fechar={() => dispensar("divergiu")}>
      <div className="ct-destaque" role="status"><span className="ct-rot">Duas histórias</span><b id="nv-divergiu-tit">O pet seguiu por dois caminhos</b>
        <p>Os dois aparelhos jogaram sem se falar. Escolha qual história fica.</p></div>
      <div className="nv-lados" role="radiogroup" aria-label="Qual história fica">{lado("outra")}{lado("nuvem")}</div>
      <p className="ct-sec nv-linha"><Info aria-hidden="true" />A outra vai para Gerações, só para ver. Nada é apagado.</p>
      <ErroLinha erro={erro} />
      <div className="ct-bts" ref={ref}>
        <BotaoHx disabled={qual === null || NV.ocupado} data-testid="nv-ficar" onClick={() => agir(async () => { await escolherHistoria(qual!); fecharDialogo(ref.current); }, setErro)}>Ficar com esta</BotaoHx>
        <BotaoHx data-autofocus data-testid="nv-depois" onClick={() => fecharDialogo(ref.current)}>Decidir depois</BotaoHx>
      </div>
    </Aviso>
  );
}

function Atualize() {
  const ref = useRef<HTMLDivElement>(null);
  return (
    <Aviso id="nv-atualize" rot="Atualizar" icone={<TriangleAlert aria-hidden="true" />} fechar={() => dispensar("atualize")}>
      <div className="ct-destaque" role="status"><span className="ct-rot">Versão antiga</span><b id="nv-atualize-tit">Atualize o jogo</b>
        <p>A sincronização volta depois de atualizar. O pet continua neste aparelho.</p></div>
      <div className="ct-bts" ref={ref}>
        <BotaoHx data-autofocus onClick={() => location.reload()}>Atualizar agora</BotaoHx>
        <BotaoHx onClick={() => fecharDialogo(ref.current)}>Depois</BotaoHx>
      </div>
    </Aviso>
  );
}

/** o servidor fora do ar: aparece uma vez; depois, só o estado "Offline" (UX-NV-6) */
function ForaDoAr() {
  const ref = useRef<HTMLDivElement>(null);
  return (
    <Aviso id="nv-fora" rot="Nuvem" icone={<CloudOff aria-hidden="true" />} fechar={verAvisoFora}>
      <div className="ct-destaque" role="status"><span className="ct-rot">Nuvem</span><b id="nv-fora-tit">O servidor não respondeu</b>
        <p>O jogo continua neste aparelho e envia quando o servidor voltar.</p></div>
      {NV.ultima && <p className="ct-sec">Última sincronização: {new Date(NV.ultima).toLocaleDateString("pt-BR")}, {hhmm(NV.ultima)}.</p>}
      <div className="ct-bts" ref={ref}><BotaoHx data-autofocus onClick={() => fecharDialogo(ref.current)}>Continuar jogando</BotaoHx></div>
    </Aviso>
  );
}

function EntreDeNovo() {
  const ref = useRef<HTMLDivElement>(null);
  return (
    <Aviso id="nv-sessao" rot="Conta" icone={<Cloud aria-hidden="true" />} fechar={() => dispensar("sessao")}>
      <div className="ct-destaque" role="status"><span className="ct-rot">Conta</span><b id="nv-sessao-tit">Entre de novo</b>
        <p>A sessão acabou. O pet continua neste aparelho; entre para voltar a sincronizar.</p></div>
      <div className="ct-bts" ref={ref}>
        <BotaoHx data-autofocus onClick={() => { fecharDialogo(ref.current); location.hash = "#/config/conta"; }}>Entrar</BotaoHx>
        <BotaoHx onClick={() => fecharDialogo(ref.current)}>Agora não</BotaoHx>
      </div>
    </Aviso>
  );
}

/* ------------------------------------------------------------ o estado no relógio (UX-NV-3) */
/** o estado da nuvem no lugar do "salvo": null com a chave desligada (o "salvo" de sempre). `soIcone`: o celular */
export function ChipNuvem({ soIcone = false }: { soIcone?: boolean }) {
  const nv = useNuvem();
  if (!nv) return null;
  const e = nv.estado;
  const [I, txt, cls] = e === "ok" ? [CloudCheck, "Na nuvem", "ok"] as const
    : e === "enviando" ? [CloudUpload, "Enviando", ""] as const
    : e === "offline" || e === "atualize" || e === "recusado" ? [CloudOff, "Offline", "alerta"] as const
    : e === "outro" || e === "divergiu" || e === "conferindo" ? [Eye, "Só ver", "alerta"] as const
    : [Cloud, "Salvo", ""] as const;
  const hora = e === "offline" && nv.ultima ? hhmm(nv.ultima) : null;
  const rotulo = `${txt}${hora ? `, última sincronização às ${hora}` : ""}`;
  const abre = e === "outro" || e === "divergiu";
  const corpo = <><I aria-hidden="true" />{!soIcone && txt}{!soIcone && hora && <small>{hora}</small>}</>;
  return (
    <span className={`pet-salvo nv-chip ${cls}`} role="status" aria-live="polite" data-testid="nv-chip" data-estado={e}>
      {abre ? <button type="button" className="nv-chip-bt" aria-label={`${rotulo}: abrir`} onClick={abrirAvisoNuvem}>{corpo}</button>
        : <span aria-label={soIcone ? rotulo : undefined}>{corpo}</span>}
    </span>
  );
}

/* ------------------------------------------------------------ as cópias do save (Ajustes › Conta) */
const motivoDaCopia: Record<string, string> = {
  diaria: "a cópia do dia", nao_escolhido: "o que não foi escolhido", troca: "o pet de antes da troca", antes_de_restaurar: "antes de restaurar",
  historia: "a história não escolhida", durante_divergencia: "durante a escolha",
};
/** a linha "Cópias do save" e a lista, com "Restaurar" e a confirmação. Só com a nuvem ligada */
export function CopiasDoSave() {
  const nv = useNuvem(), [lista, setLista] = useState<Copia[] | null>(null), [conf, setConf] = useState<Copia | null>(null), [erro, setErro] = useState<string | null>(null);
  useEffect(() => { if (nv) agir(async () => setLista(await listarCopias()), setErro); }, [nv !== null]);
  if (!nv || !["ok", "enviando", "outro", "offline"].includes(nv.estado)) return null;
  const quando = (t: number) => `${new Date(t).toLocaleDateString("pt-BR")}, ${hhmm(t)}`;
  return (
    <section className="nv-copias-sec" aria-labelledby="nv-copias-tit" data-testid="nv-copias">
      <span className="ct-rot" id="nv-copias-tit"><RotateCcw aria-hidden="true" />Cópias do save</span>
      <p className="ct-sec">Uma cópia por dia, guardada por 30 dias. As histórias que você não escolheu também ficam aqui.</p>
      <ErroLinha erro={erro} />
      {lista === null ? <p className="ct-sec" role="status">Buscando as cópias</p> : lista.length === 0 ? <p className="ct-sec">Nenhuma cópia ainda.</p> : (
        <ul className="nv-copias">{lista.map(c => (
          <li key={c.id}><span><b>{quando(c.feitaEm)}</b><small>{c.forma} · dia {diaDoJogo(c.tick)} · {motivoDaCopia[c.motivo] ?? c.motivo}</small></span>
            <BotaoHx disabled={nv.ocupado || soVer()} data-testid="nv-restaurar" onClick={() => setConf(c)}><RotateCcw aria-hidden="true" />Restaurar</BotaoHx></li>))}</ul>)}
      {conf && <ConfirmarRestaurar c={conf} fechar={() => setConf(null)} feito={() => agir(async () => setLista(await listarCopias()), setErro)} />}
    </section>
  );
}
function ConfirmarRestaurar({ c, fechar, feito }: { c: Copia; fechar: () => void; feito: () => void }) {
  const [erro, setErro] = useState<string | null>(null), ref = useRef<HTMLDivElement>(null);
  return (
    <Aviso id="nv-restaurar-conf" rot="Restaurar" icone={<RotateCcw aria-hidden="true" />} fechar={fechar}>
      <div className="ct-destaque" role="status"><span className="ct-rot">Restaurar</span><b id="nv-restaurar-conf-tit">Voltar à cópia de {new Date(c.feitaEm).toLocaleDateString("pt-BR")}</b>
        <ul className="nv-lista">
          <li>O {c.forma} volta ao dia {diaDoJogo(c.tick)}.</li>
          <li>O de agora vira uma cópia. Nada se perde.</li>
          <li>Vale para todos os aparelhos da conta.</li>
        </ul></div>
      <ErroLinha erro={erro} />
      <div className="ct-bts" ref={ref}>
        <BotaoHx data-testid="nv-restaurar-sim" onClick={() => agir(async () => { await restaurarCopia(c.id); fecharDialogo(ref.current); feito(); }, setErro)}>Restaurar</BotaoHx>
        <BotaoHx data-autofocus onClick={() => fecharDialogo(ref.current)}>Cancelar</BotaoHx>
      </div>
    </Aviso>
  );
}
/** a oferta de levar o pet, em Ajustes › Conta, depois de um "Agora não" (a tela 3 não insiste) */
export function OfertaLevar() {
  const nv = useNuvem();
  if (!nv || nv.estado !== "sem_conta" || CT.passo?.tipo !== "conta") return null;
  return (
    <div className="ct-bts"><BotaoHx data-testid="nv-oferta" onClick={() => { dispensado.delete("levar"); void abrirNuvem().catch((err: unknown) => console.error(err)); }}>
      <CloudUpload aria-hidden="true" />Levar o pet para a conta</BotaoHx></div>
  );
}
