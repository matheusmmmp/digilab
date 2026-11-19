/* O cais (MMO5 no jogo; a prancha docs/pranchas/ux-cais/, UX-CA-1 a 7 APROVADAS em 2026-11-17): a semana, as tabelas por estagio, os
   estados, a semana fechada e "Conferir a semana". Uma tela so, sem abas (UX-CA-1), no painel dos lugares sem a viagem da camera
   (#/cais, fora dos destinos, como os Ajustes). O cais nao tem botao de luta: ele leva a Arena (UX-LR-1).

   A chave: so aparece com VITE_DIGILAB_API no build (o endereco do servidor_web). Sem ela, o cais continua sem menu.

   Tudo aqui e tela: o cais so le o servidor. As regras e as chamadas ficam em src/cais/cais.ts. */
import { useEffect, useState, useSyncExternalStore } from "react";
import { ChevronLeft, ChevronRight, Copy, Info, KeyRound, RefreshCw, Swords, Trophy, UserRound } from "lucide-react";
import { NIVEL_DO_ESTAGIO } from "../../../motor/index.ts";
import { apiDoBuild } from "../../conta/apiDoBuild.ts";
import {
  CA, ESTAGIOS, LINHAS_FOLHA, LINHAS_LADO, abrirCais, abrirSegredo, andarSemana, atualizarCais, caisLigado, escolherEstagio, estadoDaSemana, faltaAte,
  fecharSegredo, horaDeBrasilia, ligarCais, linhasDaTela, marcoDoCais, ouvirCais, revisaoCais, temSemana, textoDaSemana, verTodas,
  type EstadoDaSemana, type Linha, type Semanas, type Tabelas,
} from "../../cais/cais.ts";
import { abrirMural, diaCurto, estadoMural, fecharMural, INSTALACOES_MURAL, ouvirMural, revisaoMural, type Mural, type Premios } from "../../cais/premios.ts";
import { useJogo } from "../../jogo.ts";
import "../../estilo/conta.css";
import "../../estilo/cais.css";

let tentouLigar = false;
/** liga o cais se o build tem o endereco do servidor; devolve se ele esta ligado */
export function caisNoBuild(): boolean {
  if (!tentouLigar) {
    tentouLigar = true;
    const api = apiDoBuild();
    if (api) ligarCais({ api, buscar: (u, i) => fetch(u, i), agora: () => Date.now() });
  }
  return caisLigado();
}
/** o marco do Tamer que abre o cais neste build (o 10; no beta, o do VITE_DIGILAB_MARCO_RANQUEADA) */
export function marcoDoCaisNoBuild(): number {
  const v: unknown = import.meta.env.VITE_DIGILAB_MARCO_RANQUEADA;
  return marcoDoCais(typeof v === "string" ? v.trim() : "");
}

/** uma busca a partir de um clique: o erro alto vai para o console (o estado "a tabela nao veio" e do cais.ts) */
const agir = (f: () => Promise<void>): void => { f().catch((err: unknown) => console.error(err)); };
const pontosTxt = (p: number): string => Number.isInteger(p) ? String(p) : p.toLocaleString("pt-BR", { maximumFractionDigits: 2 });
const ETIQUETA: Record<EstadoDaSemana, string> = { aberta: "", fechando: " alerta", fechada: " ok" };

/* ------------------------------------------------------------ as pecas */
function Semana({ s, semana, agora, ocupado }: { s: Semanas; semana: string; agora: number; ocupado: boolean }) {
  const estado = estadoDaSemana(s, semana, agora), txt = textoDaSemana(semana), f = s.fechadas.find(x => x.semana === semana);
  const falta = faltaAte(s.fechaEm, agora);
  const sub = estado === "fechada" ? `Fechou em ${horaDeBrasilia(f!.publicadoEm)}`
    : estado === "fechando" ? "A tabela congela 1 h depois do fim da semana"
    : `Fecha domingo, 23:59${falta ? ` · faltam ${falta}` : ""}`;
  return (
    <div className="ca-sem" role="group" aria-label={`Semana de ${txt}, ${estado}`} data-testid="ca-semana" data-estado={estado}>
      <button type="button" className="hx-btn ca-seta" aria-label="Semana anterior" disabled={ocupado || !temSemana(-1)} onClick={() => agir(() => andarSemana(-1))} data-testid="ca-anterior"><ChevronLeft aria-hidden="true" /></button>
      <span className="ca-sem-txt"><b>{txt}</b><span className={"ct-etq" + ETIQUETA[estado]}>{estado}</span><small>{sub}</small></span>
      <button type="button" className="hx-btn ca-seta" aria-label="Semana seguinte" disabled={ocupado || !temSemana(1)} onClick={() => agir(() => andarSemana(1))} data-testid="ca-seguinte"><ChevronRight aria-hidden="true" /></button>
    </div>
  );
}

function Estagios({ t, seu }: { t: Tabelas; seu: string | null }) {
  return (
    <>
      <div className="ca-est" role="radiogroup" aria-label="Estágio da tabela">
        {ESTAGIOS.map(e => (
          <button type="button" key={e} className="ct-filtro" role="radio" aria-checked={CA.estagio === e} onClick={() => escolherEstagio(e)} data-testid={`ca-estagio-${e}`}
            aria-label={`${e}, ${t.total[e]} ${t.total[e] === 1 ? "Tamer" : "Tamers"}${e === seu ? ", o estágio do seu pet" : ""}`}>
            {e === seu && <i className="ca-meu" aria-hidden="true" />}{e}<small aria-hidden="true">{t.total[e]}</small>
          </button>
        ))}
      </div>
      {seu !== null && <span className="ca-leg"><i className="ca-meu" aria-hidden="true" />o estágio do seu pet</span>}
    </>
  );
}

function LinhaDaTabela({ l, curto }: { l: Linha; curto: boolean }) {
  return (
    <tr className={l.voce ? "ca-eu" : undefined} aria-current={l.voce ? "true" : undefined} data-testid={l.voce ? "ca-voce" : undefined}>
      <td className="ca-pos">{l.posicao}º</td>
      <th scope="row"><span>{l.apelido}</span>{l.voce && <span className="ct-etq ok">você</span>}</th>
      <td className="ca-pts">{pontosTxt(l.pontos)}</td><td>{l.rivaisVencidos}</td>{!curto && <td>{l.lutasUsadas}</td>}
    </tr>
  );
}

function Tabela({ t, curto, fechada }: { t: Tabelas; curto: boolean; fechada: boolean }) {
  const e = CA.estagio, linhas = t.estagios[e], total = t.total[e], n = curto ? LINHAS_FOLHA : LINHAS_LADO;
  if (total === 0) return (
    <div className="ca-vazia" role="status" data-testid="ca-vazia"><b>Ninguém pontuou em {e} nesta semana</b>
      {!fechada && <span>A tabela nasce com a primeira vitória conferida.</span>}</div>
  );
  /* "Ver todas" tambem mostra a coluna das lutas no celular */
  const { topo, voce } = linhasDaTela(linhas, n, CA.todas), semLutas = curto && !CA.todas;
  return (
    <>
      <table className="ca-tab" data-testid="ca-tabela">
        <caption className="sr-only">Tabela {e}, {fechada ? "final" : "parcial"}: {total} {total === 1 ? "Tamer" : "Tamers"}</caption>
        <thead><tr><th scope="col">#</th><th scope="col">Tamer</th><th scope="col">Pontos</th><th scope="col" title="Rivais diferentes vencidos">Rivais</th>
          {!semLutas && <th scope="col" title="Lutas usadas">Lutas</th>}</tr></thead>
        <tbody>
          {topo.map(l => <LinhaDaTabela key={l.posicao + l.apelido} l={l} curto={semLutas} />)}
          {voce && <><tr className="ca-salto" aria-hidden="true"><td colSpan={semLutas ? 4 : 5}>· · ·</td></tr><LinhaDaTabela l={voce} curto={semLutas} /></>}
        </tbody>
      </table>
      {!CA.todas && linhas.length > n && <button type="button" className="hx-btn ca-mais" onClick={verTodas} data-testid="ca-ver-todas">Ver todas as {linhas.length}</button>}
      {CA.todas && total > linhas.length && <p className="ct-sec">O servidor entrega as {linhas.length} primeiras de {total}.</p>}
    </>
  );
}

function Destaque({ rot, titulo, alerta, children }: { rot: string; titulo: React.ReactNode; alerta?: boolean; children?: React.ReactNode }) {
  return <div className="ct-destaque" role={alerta ? "alert" : "status"}><span className="ct-rot">{rot}</span><b>{titulo}</b>{children}</div>;
}

function Segredo({ semana }: { semana: string }) {
  const g = CA.segredo!, [copiado, setCopiado] = useState<"" | "sim" | "nao">("");
  const copiar = (texto: string) => {
    navigator.clipboard.writeText(texto).then(() => setCopiado("sim"), (err: unknown) => { console.error(err); setCopiado("nao"); });
  };
  return (
    <div className="ca-segredo" data-testid="ca-segredo">
      {g.tipo === "buscando" && <p className="ct-chamada" role="status">Buscando o segredo</p>}
      {g.tipo === "sem_resposta" && <Destaque rot="Sem resposta" titulo="O segredo não veio" alerta><p>Ele continua publicado no servidor.</p></Destaque>}
      {g.tipo === "sem_segredo" && <Destaque rot="Sem lutas" titulo="Esta semana não teve segredo"><p>Nenhuma luta ranqueada foi pedida em {textoDaSemana(semana)}.</p></Destaque>}
      {g.tipo === "pronto" && (
        <>
          <div><span className="ct-rot">O segredo da semana</span>
            <div className="ca-seg"><code data-testid="ca-segredo-texto">{g.segredo}</code>
              <button type="button" className="hx-btn" aria-label="Copiar o segredo" onClick={() => copiar(g.segredo)} data-testid="ca-copiar"><Copy aria-hidden="true" />Copiar</button></div>
            <span className="ct-sec" role="status">{copiado === "sim" ? "Copiado." : copiado === "nao" ? "Não deu para copiar. Selecione o texto." : ""}</span></div>
          <p className="ct-sec">Com ele, qualquer pessoa refaz a semente de cada luta e confere que o servidor não escolheu a sorte de ninguém.</p>
          <div><span className="ct-rot">Como conferir</span>
            <p className="ca-txt">A semente da luta são os 4 primeiros bytes de HMAC-SHA256 do segredo com "conta|número da luta".</p></div>
          <p className="ct-sec">O segredo só sai depois que a semana congela. O da semana aberta fica no servidor.</p>
        </>
      )}
      <div className="ct-bts">
        {g.tipo === "sem_resposta" && <button type="button" className="hx-continuar" onClick={() => agir(abrirSegredo)}>Tentar de novo</button>}
        <button type="button" className="hx-btn" onClick={fecharSegredo} data-testid="ca-voltar-tabela">Voltar à tabela</button>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------ o mural e os premios (MMO7; a prancha esta pendente com o Matheus: so o
   minimo, com as pecas do cais) */
function SeusPremios({ p }: { p: Premios }) {
  const t = p.tituloAtual[0] ?? null;
  return (
    <div data-testid="ca-premios">
      <span className="ct-rot">Os seus prêmios</span>
      {t && <Destaque rot="Título da semana" titulo={t.texto}><p>No perfil até {horaDeBrasilia(t.noPerfilAte)}.</p></Destaque>}
      <table className="ca-tab"><caption className="sr-only">Os seus prêmios</caption><tbody>
        <tr><th scope="row">Respeito conferido</th><td className="ca-pts" data-testid="ca-respeito">{p.respeito}</td></tr>
        <tr><th scope="row">Títulos da semana</th><td>{p.titulos.length}</td></tr>
        <tr><th scope="row">Selos Top do dia</th><td data-testid="ca-selos">{p.selos.length}{p.selos.length > 0 && <small> · o último em {diaCurto(p.selos[0]!.dia)}</small>}</td></tr>
        <tr><th scope="row">Taças da temporada</th><td data-testid="ca-tacas">{p.enfeites.length ? p.enfeites.map(e => `T${e.temporada}`).join(", ") : "0"}</td></tr>
      </tbody></table>
      <p className="ct-sec">O Respeito conta só o que o servidor deu: 100 por título da semana e 20 por selo. A taça fica na ilha, perto do cais.</p>
    </div>
  );
}

function RecordesDoMural({ m }: { m: Mural }) {
  return (
    <>
      {INSTALACOES_MURAL.map(([id, nome]) => (
        <div key={id} data-testid={`ca-mural-${id}`}>
          <span className="ct-rot">{nome} · recorde de todos os tempos</span>
          {m.recordes[id].length === 0 ? <p className="ct-sec">Ninguém tem recorde conferido ainda.</p> : (
            <table className="ca-tab"><caption className="sr-only">{nome}: {m.total[id]} Tamers</caption>
              <thead><tr><th scope="col">#</th><th scope="col">Tamer</th><th scope="col">Recorde</th></tr></thead>
              <tbody>{m.recordes[id].map(l => (
                <tr key={l.posicao} className={l.voce ? "ca-eu" : undefined} aria-current={l.voce ? "true" : undefined}>
                  <td className="ca-pos">{l.posicao}º</td><th scope="row"><span>{l.apelido}</span>{l.voce && <span className="ct-etq ok">você</span>}</th><td className="ca-pts">{l.valor}</td>
                </tr>))}</tbody></table>
          )}
        </div>
      ))}
      <div data-testid="ca-mural-titulos">
        <span className="ct-rot">Os campeões das semanas</span>
        {m.titulos.length === 0 ? <p className="ct-sec">Nenhuma semana fechou com campeão ainda.</p> : (
          <table className="ca-tab"><caption className="sr-only">Os títulos das semanas</caption><tbody>{m.titulos.map(t => (
            <tr key={t.semana + t.estagio} className={t.voce ? "ca-eu" : undefined}><th scope="row">{t.texto}</th><td><span>{t.apelido}</span>{t.voce && <span className="ct-etq ok">você</span>}</td></tr>
          ))}</tbody></table>
        )}
      </div>
    </>
  );
}

function MuralCais({ fechar }: { fechar: () => void }) {
  const e = estadoMural()!;
  return (
    <div className="ct ca" data-testid="ca-mural">
      {e.passo === "buscando" && <p className="ct-chamada" role="status">Buscando o mural</p>}
      {e.passo === "sem_resposta" && <Destaque rot="Sem resposta" titulo="O mural não veio" alerta><p>Os seus prêmios continuam guardados no servidor.</p></Destaque>}
      {e.passo === "sem_conta" && <Destaque rot="Só com a conta" titulo="O mural pede a conta"><p>Ele mostra só os apelidos.</p></Destaque>}
      {e.passo === "pronto" && <><SeusPremios p={e.premios} /><RecordesDoMural m={e.mural} /></>}
      <div className="ct-bts">
        {e.passo === "sem_resposta" && <button type="button" className="hx-continuar" onClick={() => agir(abrirMural)}>Tentar de novo</button>}
        <button type="button" className="hx-btn" onClick={() => { fecharMural(); }} data-testid="ca-voltar-semana">Voltar à semana</button>
        <button type="button" className="hx-btn" onClick={fechar}>Voltar à ilha</button>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------ a tela */
/** `curto`: a folha do celular (6 linhas, sem a coluna das lutas); `irArena` leva a aba Arena do portao; `fechar` volta a ilha */
export function TelaCais({ curto, irArena, fechar }: { curto: boolean; irArena: () => void; fechar: () => void }) {
  const jogo = useJogo(), ligado = caisNoBuild();
  useSyncExternalStore(ouvirCais, revisaoCais);
  useSyncExternalStore(ouvirMural, revisaoMural);
  /* o mural fecha quando o cais fecha */
  useEffect(() => () => fecharMural(), []);
  const seu = NIVEL_DO_ESTAGIO[jogo.motor.estagioAtual] ?? null, seuComTabela = seu !== null && ESTAGIOS.includes(seu) ? seu : null;
  /* cada abertura do cais busca de novo: a tabela muda no servidor */
  useEffect(() => { if (ligado) agir(() => abrirCais(seuComTabela)); }, [ligado]);   // eslint-disable-line react-hooks/exhaustive-deps
  /* o relogio da tela ("faltam 2 d 4 h" e a passagem para "fechando"), de minuto em minuto */
  const [agora, setAgora] = useState(() => Date.now());
  useEffect(() => { const r = setInterval(() => setAgora(Date.now()), 60_000); return () => clearInterval(r); }, []);
  if (!ligado) throw new Error("o cais abriu sem o endereço do servidor no build");
  if (estadoMural()) return <MuralCais fechar={fechar} />;

  const s = CA.semanas, semana = CA.semana, t = CA.tabelas, ocupado = CA.passo === "buscando";
  const cab = s && semana !== null ? <Semana s={s} semana={semana} agora={agora} ocupado={ocupado} /> : null;
  if (CA.passo === null || CA.passo === "buscando") return (
    <div className="ct ca" data-testid="ca-buscando">{cab}<p className="ct-chamada" role="status">Buscando a tabela</p>
      <p className="ct-sec">A semana e os estágios aparecem assim que a resposta chegar.</p></div>
  );
  if (CA.passo === "sem_resposta") return (
    <div className="ct ca" data-testid="ca-sem-resposta">
      <Destaque rot="Sem resposta" titulo="A tabela não veio" alerta><p>Os seus pontos continuam guardados no servidor.</p></Destaque>
      <div className="ct-bts"><button type="button" className="hx-continuar" onClick={() => agir(atualizarCais)} data-testid="ca-tentar">Tentar de novo</button>
        <button type="button" className="hx-btn" onClick={fechar}>Voltar à ilha</button></div>
    </div>
  );
  if (CA.passo === "sem_conta") return (
    <div className="ct ca" data-testid="ca-sem-conta">
      <Destaque rot="Só com a conta" titulo="As tabelas pedem a conta"><p>Elas mostram só os apelidos. Sem conta, nada muda no jogo.</p></Destaque>
      <div className="ct-bts"><a className="hx-continuar" href="#/config/conta" data-testid="ca-entrar"><UserRound aria-hidden="true" />Entrar</a>
        <button type="button" className="hx-btn" onClick={fechar} data-testid="ca-agora-nao">Agora não</button></div>
    </div>
  );
  if (!s || semana === null || !t) throw new Error("o cais está pronto sem a semana ou sem as tabelas");
  if (CA.segredo) return <div className="ct ca">{cab}<Segredo semana={semana} /></div>;

  const estado = estadoDaSemana(s, semana, agora), fechada = estado === "fechada", eu = t.estagios[CA.estagio].find(l => l.voce) ?? null;
  return (
    <div className="ct ca" data-testid="ca-pronto">
      {cab}
      {estado === "fechando" && <Destaque rot="A semana acabou" titulo="Conferindo as últimas lutas">
        <p>A luta feita até 23:59 e ainda não enviada pode chegar até {horaDeBrasilia(t.congelaEm).split(", ")[1]}. Depois disso, vale como derrota.</p></Destaque>}
      {fechada && eu && <Destaque rot={`O seu resultado · ${CA.estagio}`} titulo={<>{eu.posicao}º lugar <small>de {t.total[CA.estagio]}</small></>}>
        <p>{pontosTxt(eu.pontos)} pontos · {eu.rivaisVencidos} {eu.rivaisVencidos === 1 ? "rival vencido" : "rivais vencidos"} · {eu.lutasUsadas} {eu.lutasUsadas === 1 ? "luta" : "lutas"}</p></Destaque>}
      <Estagios t={t} seu={seuComTabela} />
      <Tabela t={t} curto={curto} fechada={fechada} />
      {!fechada && t.total[CA.estagio] > 0 && !eu && <p className="ca-parcial" data-testid="ca-fora"><Info aria-hidden="true" /><span>Você não lutou com um {CA.estagio} nesta semana.</span></p>}
      {!fechada && <p className="ca-parcial"><Info aria-hidden="true" /><span>Parcial: entram só as lutas que o servidor já conferiu.</span></p>}
      {!curto && !fechada && <details className="ca-como"><summary><Info aria-hidden="true" />Como a tabela conta</summary>
        <p>Só a vitória ranqueada conferida pelo servidor conta. No empate de pontos, fica na frente quem venceu mais rivais diferentes; depois, quem usou
          menos lutas; depois, quem chegou antes aos pontos.</p></details>}
      {fechada
        ? <button type="button" className="ca-conferir" onClick={() => agir(abrirSegredo)} data-testid="ca-conferir"><KeyRound aria-hidden="true" /><span>Conferir a semana</span><small>segredo publicado</small><ChevronRight aria-hidden="true" /></button>
        : <div className="ct-bts"><button type="button" className="hx-continuar" onClick={irArena} data-testid="ca-arena"><Swords aria-hidden="true" />Ir para a Arena</button>
            <button type="button" className="hx-btn" onClick={() => agir(atualizarCais)} data-testid="ca-atualizar"><RefreshCw aria-hidden="true" />Atualizar</button></div>}
      <button type="button" className="ca-conferir" onClick={() => agir(abrirMural)} data-testid="ca-abrir-mural"><Trophy aria-hidden="true" /><span>Mural e prêmios</span><small>recordes e títulos</small><ChevronRight aria-hidden="true" /></button>
    </div>
  );
}
