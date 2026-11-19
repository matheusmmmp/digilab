/* A luta ranqueada na aba Arena (MMO4; docs/PLANO_UX_LUTA_RANQUEADA.md e a prancha docs/pranchas/ux-luta-ranqueada/, UX-LR-1 a 6
   APROVADAS em 2026-11-17): a escolha "Treino / Ranqueada", o placar, os rivais com o valor da vitoria, o aviso e o botao; os estados do
   pedido; e o resultado (a previa do jogo e a palavra do servidor). As regras e a conversa com o servidor estao em
   src/ranking/ranqueada.ts; aqui e so a tela.

   A chave: so aparece com VITE_DIGILAB_API no build (o endereco do servidor_web), com um pet so na tela (sem o pet gemeo e fora do
   laboratorio). Sem ela, a Arena e a de sempre.

   A luta e a de sempre (lutarNoPalco, o Motor.lutarPoc), com a semente que o servidor entregou. Do pedido ate a luta entrar no registro o
   tempo do jogo fica parado (segurarTempoDoPedido): a luta tem de entrar na posicao que o pedido prometeu. */
import { useEffect, useState, useSyncExternalStore } from "react";
import { Check, Info, Lock, RefreshCw, Server, Swords, Trophy, Upload, UserRound } from "lucide-react";
import { CENAS, DIGIMON_DA_FORMA, IDS_CENA, type IdCena } from "../../../../motor/index.ts";
import { jogoAtual, tamerAtual, useJogo } from "../../../jogo.ts";
import { nomeDaChave, segurarTempoDoPedido, temReplayPoc, useLutaPoc, verReplayPoc } from "../../../lutaPocTela.ts";
import { LUTAS_POR_DIA } from "../../../ranking/pontos.ts";
import {
  RQ, atualizarHoje, divergiu, enviarRegistro, fecharEstado, fecharResultado, ligarRanqueada, lutaPerdida, ouvirRanqueada, pedirSemente,
  placarDoPet, ranqueadaLigada, registrarPrevia, revisaoRanqueada, temPendente, valorDoRival, type LutaGuardada,
} from "../../../ranking/ranqueada.ts";
import { versaoTamerDe } from "../../../tamer.ts";
import { Retrato, lutarNoPalco } from "./TelaLugaresPoc.tsx";
import { apiDoBuild } from "../../../conta/apiDoBuild.ts";
import "../../../estilo/ranqueada.css";

let tentouLigar = false;
function ligarSeHouver(): void {
  if (tentouLigar) return;
  tentouLigar = true;
  const api = apiDoBuild();
  if (api) ligarRanqueada({ api, buscar: (u, i) => fetch(u, i), armaz: localStorage, agora: () => Date.now() });
}

/** o estado da luta ranqueada para a Arena; null com a chave desligada, com os dois pets ou no laboratorio */
export function useRanqueadaNaArena(): typeof RQ | null {
  ligarSeHouver();
  useSyncExternalStore(ouvirRanqueada, revisaoRanqueada);
  const j = useJogo();
  return ranqueadaLigada() && !j.grupo && !j.emLab ? RQ : null;
}

/** o pet e o Tamer como o envio os leva */
function enviarAgora(): void {
  const m = jogoAtual().motor;
  void enviarRegistro({ semente: m.semente, versao: m.versao, log: m.log }, { versao: versaoTamerDe(tamerAtual().log), log: tamerAtual().log });
}

const plural = (n: number, um: string, varios: string): string => `${n} ${n === 1 ? um : varios}`;
const pontosTxt = (p: number): string => String(p).replace(".", ",");

export function EscolhaDoModo({ modo, trocar }: { modo: "treino" | "ranqueada"; trocar: (m: "treino" | "ranqueada") => void }) {
  const tr = RQ.trancada;
  return (
    <div className="lr-modo" role="radiogroup" aria-label="Tipo de luta">
      <button type="button" role="radio" aria-checked={modo === "treino"} className="lr-filtro" onClick={() => trocar("treino")} data-testid="lr-modo-treino">
        <Swords aria-hidden="true" />Treino</button>
      <button type="button" role="radio" aria-checked={modo === "ranqueada"} className="lr-filtro" onClick={() => trocar("ranqueada")} data-testid="lr-modo-ranqueada"
        aria-label={tr !== null ? `Ranqueada, trancada: abre no nível ${tr}` : undefined}>
        <Trophy aria-hidden="true" />Ranqueada{tr !== null && <Lock aria-hidden="true" />}</button>
    </div>
  );
}

function Placar({ pet }: { pet: number }) {
  const p = placarDoPet(pet, Date.now());
  return (
    <div className="lr-placar" role="group" aria-label={`Luta ranqueada: ${p.hoje} de ${LUTAS_POR_DIA} lutas de hoje usadas; ${pontosTxt(p.pontos)} pontos na semana`} data-testid="lr-placar">
      <div className="lr-dia"><span className="lr-rot">Hoje</span><b className="lr-num">{p.hoje}<small>/{LUTAS_POR_DIA}</small></b>
        <span className="lr-pinos" aria-hidden="true">{Array.from({ length: LUTAS_POR_DIA }, (_, i) => <i key={i} className={i < p.hoje ? "usada" : ""} />)}</span></div>
      <div className="lr-sem"><span className="lr-rot">Semana</span><b className="lr-num">{pontosTxt(p.pontos)}<small> pontos</small></b>
        <span className="lr-sec">{plural(p.rivais, "rival vencido", "rivais vencidos")} · fecha domingo</span></div>
    </div>
  );
}

function Botoes({ children }: { children: React.ReactNode }) { return <div className="lr-bts">{children}</div>; }

/** quanto falta para a hora, em "3 h 12 min" */
function falta(ate: number): string {
  const min = Math.max(0, Math.ceil((ate - Date.now()) / 60_000));
  return min >= 60 ? `${Math.floor(min / 60)} h ${min % 60} min` : `${min} min`;
}

/** os estados do pedido (a prancha `estados`): cada um diz o que houve, se a luta foi gasta e o caminho */
function EstadoDoPedido({ pet, irTreino, tentar }: { pet: number; irTreino: () => void; tentar: () => void }) {
  const e = RQ.pedido, hoje = placarDoPet(pet, Date.now()).hoje;
  const treino = (principal: boolean) => <button type="button" className={principal ? "hx-continuar" : "hx-btn"} onClick={() => { fecharEstado(); irTreino(); }} data-testid="lr-ir-treino">Lutar de treino</button>;
  if (e.tipo === "pedindo") return (
    <div className="lr-estado" data-testid="lr-estado-pedindo">
      <ol className="lr-passos" aria-label="Passos do pedido"><li className="feito">Escolha</li><li className="agora" aria-current="step">Servidor</li><li>Luta</li></ol>
      <p className="lr-chamada" role="status">Pedindo a luta ao servidor</p>
      <p className="lr-sec">A luta começa assim que a resposta chegar.</p>
    </div>
  );
  if (e.tipo === "sem_resposta") return (
    <div className="lr-estado" data-testid="lr-estado-sem-resposta">
      <div className="lr-destaque" role="alert"><span className="lr-rot">Sem resposta</span><b>A luta não foi pedida</b>
        <p>Nada foi gasto: continuam {hoje} de {LUTAS_POR_DIA} hoje.</p></div>
      <Botoes><button type="button" className="hx-continuar" onClick={tentar} data-testid="lr-tentar">Tentar de novo</button>{treino(false)}</Botoes>
    </div>
  );
  if (e.tipo === "limite") return (
    <div className="lr-estado" data-testid="lr-estado-limite">
      <div className="lr-destaque" role="status"><span className="lr-rot">Limite de hoje</span><b>{LUTAS_POR_DIA} de {LUTAS_POR_DIA} lutas feitas</b>
        <p>Volta à meia-noite, no horário de Brasília. Faltam {falta(e.reabreEm)}.</p></div>
      <Botoes>{treino(true)}<a className="hx-btn" href="#/cais" onClick={fecharEstado} data-testid="lr-ver-semana">Ver a semana</a></Botoes>
    </div>
  );
  if (e.tipo === "trancada") return (
    <div className="lr-estado" data-testid="lr-estado-trancada">
      <div className="lr-destaque" role="status"><span className="lr-rot">Trancada{e.marco !== null ? ` · Nv ${e.marco}` : ""}</span>
        <b>{e.marco === null || e.marco === 10 ? "Abre com o primeiro Mega" : `Abre no nível ${e.marco} do Tamer`}</b>
        <p>{e.marco === null || e.marco === 10 ? "Leve um pet ao Mega e envie o registro." : "Chegue ao nível e envie o registro."} A luta de treino continua aberta.</p></div>
      <Botoes>{treino(true)}<button type="button" className="hx-btn" disabled={RQ.enviando} onClick={enviarAgora} data-testid="lr-enviar-registro"><Upload aria-hidden="true" />Enviar o registro</button></Botoes>
    </div>
  );
  if (e.tipo === "sem_conta") {
    /* o Entrar leva a parte Conta dos Ajustes (telas/config/TelaConta.tsx) */
    return (
      <div className="lr-estado" data-testid="lr-estado-sem-conta">
        <div className="lr-destaque" role="status"><span className="lr-rot">Só com a conta</span><b>A luta ranqueada pede a conta</b>
          <p>O servidor confere cada luta. Sem conta, nada muda no jogo.</p></div>
        <Botoes><a className="hx-continuar" href="#/config/conta" onClick={fecharEstado} data-testid="lr-entrar"><UserRound aria-hidden="true" />Entrar</a>
          <button type="button" className="hx-btn" onClick={() => { fecharEstado(); irTreino(); }} data-testid="lr-agora-nao">Agora não</button></Botoes>
      </div>
    );
  }
  if (e.tipo === "versao") return (
    <div className="lr-estado" data-testid="lr-estado-versao">
      <div className="lr-destaque" role="alert"><span className="lr-rot">Versão antiga</span><b>Atualize o jogo</b>
        <p>O servidor confere com a versão nova. Nada foi gasto.</p></div>
      <Botoes><button type="button" className="hx-continuar" onClick={() => location.reload()} data-testid="lr-recarregar"><RefreshCw aria-hidden="true" />Recarregar</button>{treino(false)}</Botoes>
    </div>
  );
  if (e.tipo === "recusado") return (
    <div className="lr-estado" data-testid="lr-estado-recusado">
      <div className="lr-destaque" role="alert"><span className="lr-rot">A luta não começou</span>
        <b>{e.gasta ? "A luta pedida foi gasta" : "O servidor não aceitou o pedido"}</b>
        <p>{e.gasta ? `Ela já conta nas ${LUTAS_POR_DIA} de hoje e vale como derrota.` : "Nada foi gasto."} Motivo: {e.motivo}.</p></div>
      <Botoes><button type="button" className="hx-continuar" onClick={fecharEstado} data-testid="lr-voltar">Voltar</button>{treino(false)}</Botoes>
    </div>
  );
  return null;
}

/** o resultado (a prancha `resultado`): a previa do jogo, a palavra do servidor, a divergencia e a luta ainda nao enviada */
function Resultado({ l, forma, irTreino }: { l: LutaGuardada; forma: string; irTreino: () => void }) {
  const p = placarDoPet(l.pet, Date.now()), conferido = l.envio === "conferido" && l.servidor !== null, dif = divergiu(l);
  const ganhou = conferido ? l.servidor!.situacao === "vitoria" : l.previa?.venceu === true, pts = conferido ? l.servidor!.pontos : l.previa?.pontos ?? 0;
  const mapa = l.mapa && CENAS[l.mapa as IdCena] ? CENAS[l.mapa as IdCena].nome : null;
  const outra = <button type="button" className="hx-continuar" onClick={fecharResultado} data-testid="lr-outra">Outra luta</button>;
  const rever = temReplayPoc() && <button type="button" className="hx-btn" onClick={verReplayPoc} data-testid="lr-rever">Ver a luta de novo</button>;
  return (
    <div className="lr-resultado" data-testid="lr-resultado">
      <div className="lr-luta"><Retrato k={forma} /><span className="lr-x" aria-hidden="true">×</span>
        <span><b>{l.rival ? nomeDaChave(l.rival) : "Rival"}</b><small>{mapa ? `${mapa} · ` : ""}{l.doDia > 0 ? `luta ${l.doDia} de ${LUTAS_POR_DIA} de hoje` : "luta ranqueada"}</small></span></div>
      <div className={`lr-res${conferido ? (dif ? " alerta" : " ok") : ""}`} role={dif ? "alert" : "status"} data-testid="lr-res">
        {conferido ? (dif ? <span className="lr-etq alerta">o servidor</span> : <span className="lr-etq ok"><Check aria-hidden="true" />conferido</span>) : <span className="lr-etq">prévia</span>}
        <b className="lr-grande">{ganhou ? "Vitória" : "Derrota"}</b><b className={`lr-pts${pts ? "" : " zero"}`}>{pts ? `+${pontosTxt(pts)}` : "0"}</b>
      </div>
      {conferido && !dif && <p className="lr-serv"><Server aria-hidden="true" /><span>Semana: <b>{pontosTxt(p.pontos)} pontos</b> · {plural(p.rivais, "rival vencido", "rivais vencidos")} · {p.hoje} de {LUTAS_POR_DIA} hoje</span></p>}
      {conferido && dif && <div className="lr-destaque"><span className="lr-rot">O servidor viu outra luta</span>
        <p>Aqui deu {l.previa!.venceu ? "vitória" : "derrota"}, valendo {pontosTxt(l.previa!.pontos)}; no servidor, {ganhou ? "vitória" : "derrota"}, valendo {pontosTxt(pts)}. Vale a conta do servidor. Isso é raro e fica registrado.</p></div>}
      {l.envio === "pendente" && RQ.enviando && <p className="lr-serv" role="status"><Server aria-hidden="true" /><span>O servidor está conferindo a luta.</span>
        <span className="lr-pontos3" aria-hidden="true"><i /><i /><i /></span></p>}
      {l.envio === "pendente" && !RQ.enviando && <div className="lr-destaque" role="alert"><span className="lr-rot">Ainda não enviada</span>
        <p>Sem conexão. O jogo envia sozinho quando ela voltar. Se não chegar até domingo, vale como derrota.</p></div>}
      {l.envio === "recusado" && <div className="lr-destaque" role="alert"><span className="lr-rot">O servidor recusou o registro</span>
        <p>A luta vale como derrota. Motivo: {l.motivo ?? "recusado"}.</p></div>}
      {l.envio === "pendente" && !RQ.enviando
        ? <Botoes><button type="button" className="hx-continuar" onClick={enviarAgora} data-testid="lr-enviar"><Upload aria-hidden="true" />Enviar agora</button>
          <button type="button" className="hx-btn" onClick={() => { fecharResultado(); irTreino(); }} data-testid="lr-ir-treino">Lutar de treino</button></Botoes>
        : <Botoes>{outra}{rever}</Botoes>}
    </div>
  );
}

export function ArenaRanqueada({ rivais, rival, setRival, mapa, setMapa, irTreino }: {
  rivais: readonly string[]; rival: string; setRival: (k: string) => void; mapa: IdCena; setMapa: (m: IdCena) => void; irTreino: () => void;
}) {
  const { motor: m } = useJogo(), luta = useLutaPoc(), [erro, setErro] = useState<string | null>(null), [maisMapas, setMaisMapas] = useState(false);
  const agora = Date.now(), pet = m.semente, valor = valorDoRival(rival, pet, agora);

  /* ao abrir: as lutas de hoje pelo servidor e o reenvio do que ficou pendente; e de novo quando a conexao volta (UX-LR-4) */
  useEffect(() => {
    void atualizarHoje();
    const reenviar = () => { if (temPendente(jogoAtual().motor.semente)) enviarAgora(); };
    reenviar();
    window.addEventListener("online", reenviar);
    return () => window.removeEventListener("online", reenviar);
  }, []);

  async function lutarValendo(): Promise<void> {
    setErro(null);
    segurarTempoDoPedido(true);
    try {
      const j = jogoAtual().motor;
      /* o rival e o mapa vao no pedido: a escolha e de antes da semente (D-CONTA-116) */
      const s = await pedirSemente({ semente: j.semente, versao: j.versao, log: j.log }, rival, mapa);
      if (!s) return;
      /* o registro tem de estar onde o pedido prometeu; se mudou no meio, a luta pedida ja foi gasta */
      if (jogoAtual().motor !== j || j.log.length !== s.indice) { lutaPerdida(s.numero, "o registro do pet mudou durante o pedido"); return; }
      let falha: string | null = null;
      const r = lutarNoPalco(rival, mapa, `Ranqueada · ${CENAS[mapa].nome}`, e => { falha = e; }, () => s.semente);
      if (!r) { lutaPerdida(s.numero, falha ?? "o motor recusou a luta"); return; }
      registrarPrevia(s.numero, rival, mapa, r.venceu, Date.now());
      enviarAgora();
    } catch (err) { setErro(err instanceof Error ? err.message : String(err)); }
    finally { segurarTempoDoPedido(false); }
  }

  const res = RQ.resultado !== null ? RQ.lutas.find(l => l.numero === RQ.resultado) ?? null : null;
  const corpo = RQ.pedido.tipo !== "parado" ? <EstadoDoPedido pet={pet} irTreino={irTreino} tentar={() => { fecharEstado(); void lutarValendo(); }} />
    : res ? <Resultado l={res} forma={m.formaLutaPoc} irTreino={irTreino} />
    : null;
  const mapasVisiveis = maisMapas ? IDS_CENA : [...IDS_CENA.slice(0, 4), ...(IDS_CENA.indexOf(mapa) >= 4 ? [mapa] : [])];
  return (
    <section className="hx-painel poc-lugar lr-arena" aria-labelledby="poc-arena-tit" data-testid="lr-arena">
      <h2 id="poc-arena-tit">Arena</h2>
      <EscolhaDoModo modo="ranqueada" trocar={x => { if (x === "treino" && RQ.pedido.tipo !== "pedindo") { fecharEstado(); irTreino(); } }} />
      <Placar pet={pet} />
      {corpo ?? <>
        <fieldset className="poc-grupo"><legend>Rival · quanto vale a vitória</legend>
          <div className="poc-rivais" role="radiogroup" aria-label="Rival">
            {rivais.map(k => {
              const v = valorDoRival(k, pet, agora), faixa = DIGIMON_DA_FORMA[k]?.[1] ?? "";
              const obs = v.vencido ? `vencido ${v.vencido}×` : "";
              return (
                <button key={k} type="button" role="radio" aria-checked={k === rival} className="poc-rival lr-rival" disabled={luta.lutando} onClick={() => setRival(k)} data-testid={`lr-rival-${k}`}
                  aria-label={`${nomeDaChave(k)}, vale ${pontosTxt(v.pontos)} pontos${obs ? `, ${obs}, vale a metade` : ""}`}>
                  <Retrato k={k} /><span className="lr-nome"><b>{nomeDaChave(k)}</b><small>{obs ? `${obs} · vale a metade` : faixa}</small></span>
                  <span className={`lr-vale${obs ? " meio" : ""}`}><b>{pontosTxt(v.pontos)}</b></span>
                </button>
              );
            })}
          </div>
        </fieldset>
        <fieldset className="poc-grupo"><legend>Mapa</legend>
          <div className="lr-mapas" role="radiogroup" aria-label="Mapa">
            {mapasVisiveis.map(id => (
              <button key={id} type="button" role="radio" aria-checked={id === mapa} className="lr-filtro" disabled={luta.lutando} onClick={() => setMapa(id)} data-testid={`lr-mapa-${id}`}>{CENAS[id].nome}</button>
            ))}
            {!maisMapas && IDS_CENA.length > mapasVisiveis.length && <button type="button" className="lr-filtro" aria-expanded="false" onClick={() => setMaisMapas(true)}
              aria-label={`Mostrar os outros ${IDS_CENA.length - mapasVisiveis.length} mapas`} data-testid="lr-mais-mapas">+{IDS_CENA.length - mapasVisiveis.length}</button>}
          </div>
        </fieldset>
        <p className="lr-aviso"><Info aria-hidden="true" /><span>Ao pedir, a luta <b>já conta</b> nas {LUTAS_POR_DIA} de hoje. Se ela não chegar ao servidor, vale como derrota.</span></p>
        {erro && <p className="aviso" role="alert">A luta não começou: {erro}</p>}
        <button type="button" className="hx-continuar poc-lutar" disabled={luta.lutando || valor.pontos === 0} onClick={() => void lutarValendo()} data-testid="lr-lutar">
          <Trophy aria-hidden="true" /> {valor.pontos ? `Lutar valendo ${pontosTxt(valor.pontos)}` : "Este rival não vale ponto"}</button>
      </>}
    </section>
  );
}
