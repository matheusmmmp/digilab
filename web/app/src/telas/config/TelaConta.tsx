/* A conta nos Ajustes (CN2 no jogo; as pranchas docs/pranchas/ux-conta/, UX-CN-1 a 6 APROVADAS em 2026-11-12): Entrar, os estados da ida
   ao provedor, o primeiro acesso, a troca do apelido, o perfil e apagar. E uma parte dos Ajustes (#/config/conta), na mesma caixa; a
   linha "Conta" no topo da lista e a porta (UX-CN-2).

   A chave: so aparece com VITE_DIGILAB_API no build (o endereco do servidor_web). Sem ela, os Ajustes sao os de sempre.

   O perfil abre pelas duas pontuacoes (MMO8; a prancha docs/pranchas/ux-reset/, tela 5; UX-RS-5 APROVADA em 2026-11-19): o Respeito do
   Tamer, o conferido grande e o do jogo menor ao lado, com o nivel e a barra ate "Tamer Lendario"; os pontos do melhor Digimon da conta,
   com a posicao; e "De onde vem o Respeito". Os aparelhos, os dados e apagar descem para uma linha que abre.

   Tudo aqui e tela: a conta nao toca o motor, o registro nem o save. As regras e as chamadas ficam em src/conta/conta.ts e, as das
   pontuacoes, em src/cais/pontuacoes.ts. */
import { CopiasDoSave, OfertaLevar } from "../../nuvem/NuvemRaiz.tsx";
import { useEffect, useState, useSyncExternalStore } from "react";
import { Anchor, Check, ChevronRight, Crown, Download, Info, LogOut, Monitor, Shuffle, Smartphone, Trash2, Trophy, TriangleAlert, UserRound } from "lucide-react";
import { DIGIMON_DA_FORMA } from "../../../motor/index.ts";
import { apiDoBuild, enderecoDaPrivacidade, enderecoDosTermos } from "../../conta/apiDoBuild.ts";
import {
  CT, abrirConta, apagarConta, apelidoDaConta, avisarErroDaConta, cancelarPrimeiro, conferirConta, contaLigada, criarConta, desconectar, enderecoDosDados,
  entrarCom, ligarConta, ouvirConta, revisaoConta, sair, trocarApelido, voltaDaBusca, voltarAEntrar, type Conta, type Primeiro,
} from "../../conta/conta.ts";
import { Retrato } from "../lutar/palcoPoc/TelaLugaresPoc.tsx";
import { caisNoBuild } from "../cais/TelaCais.tsx";
import { pedirAbaDoCais } from "../cais/Rankings.tsx";
import { linhaDoPet, melhorDigimon, milhares, ouvirPontuacoes, perfil, revisaoPontuacoes, type DadosPerfil } from "../../cais/pontuacoes.ts";
import { jogoAtual, tamerAtual } from "../../jogo.ts";
import { NIVEL_DO_PRIMEIRO_MEGA, RESPEITO_FEITO, RESPEITO_POR_NIVEL, TAMER_LENDARIO, respeitoLocal } from "../../ranking/pontos.ts";
import { nomeForma } from "../../../motor/index.ts";
import "../../estilo/reset.css";
import "../../estilo/conta.css";

let tentouLigar = false;
function ligarSeHouver(): void {
  if (tentouLigar) return;
  tentouLigar = true;
  const api = apiDoBuild();
  if (api) ligarConta({ api, buscar: (u, i) => fetch(u, i), ir: u => location.assign(u) });
}
/** a conta para os Ajustes; null com a chave desligada */
export function useConta(): typeof CT | null {
  ligarSeHouver();
  useSyncExternalStore(ouvirConta, revisaoConta);
  return contaLigada() ? CT : null;
}
/** a linha "Conta" dos Ajustes: o apelido, ou null sem conta; pergunta ao servidor uma vez, calada */
export function useApelidoNosAjustes(): { ligada: boolean; apelido: string | null } {
  const ct = useConta();
  useEffect(() => { if (ct) void conferirConta().catch((err: unknown) => console.error(err)); }, [ct]);
  return { ligada: ct !== null, apelido: ct ? apelidoDaConta() : null };
}
export { UserRound as IconeConta };

/* ------------------------------------------------------------ as pecas */
const NOME_PROVEDOR: Record<string, string> = { google: "Google", github: "GitHub", falso: "a conta de teste" };
const nomeProvedor = (p: string): string => NOME_PROVEDOR[p] ?? p;
/** a marca do provedor em uma cor so, a do texto (UX-CN-3): as letras num quadro; a marca oficial ainda nao foi conferida */
function Marca({ p }: { p: string }) { return <span className="ct-marca" aria-hidden="true">{p === "google" ? "G" : p === "github" ? "GH" : "T"}</span>; }

/** a chave do sprite de um Rookie pelo nome do Digimon ("Agumon" -> "brasa_crianca_sereno") */
const SPRITE_DO_NOME: Record<string, string> = Object.fromEntries(Object.entries(DIGIMON_DA_FORMA).map(([k, [nome]]) => [nome, k]));
function Apelido({ apelido, sub, children }: { apelido: string; sub: string; children?: React.ReactNode }) {
  const [digimon, numero] = apelido.split("#"), k = SPRITE_DO_NOME[digimon ?? ""];
  return (
    <div className="ct-apelido" data-testid="ct-apelido">
      {k ? <Retrato k={k} /> : <span className="poc-ret" aria-hidden="true" />}
      <span><b>{digimon}<i>#{numero}</i></b><small>{sub}</small></span>
      {children}
    </div>
  );
}
function Destaque({ rot, titulo, perigo, alerta, children }: { rot: string; titulo: string; perigo?: boolean; alerta?: boolean; children: React.ReactNode }) {
  return (
    <div className={"ct-destaque" + (perigo ? " perigo" : "")} role={alerta ? "alert" : "status"}>
      <span className="ct-rot">{perigo && <TriangleAlert aria-hidden="true" />}{rot}</span><b>{titulo}</b>{children}
    </div>
  );
}
function Passos({ agora, provedor }: { agora: 1 | 2; provedor: string }) {
  const nomes = ["Jogo", provedor, "Conta"];
  return <ol className="ct-passos" aria-hidden="true">{nomes.map((n, i) => <li key={n} className={i < agora ? "feito" : i === agora ? "agora" : ""}>{n}</li>)}</ol>;
}
function Marcar({ marcado, mudar, testid, children }: { marcado: boolean; mudar: (v: boolean) => void; testid: string; children: React.ReactNode }) {
  return (
    <label className="ct-aceite" data-testid={testid}>
      <input type="checkbox" checked={marcado} onChange={e => mudar((e.target as HTMLInputElement).checked)} />
      <span className="ct-caixa" aria-hidden="true"><Check /></span><span>{children}</span>
    </label>
  );
}
function Erro() { return CT.erro ? <p className="mc-erro" role="alert" data-testid="ct-erro">{CT.erro}</p> : null; }
/** uma acao da conta a partir de um clique: o erro alto vai para o console e vira uma frase na tela */
function agir(f: () => Promise<void>): void {
  f().catch((err: unknown) => { console.error(err); avisarErroDaConta("Não deu. Nada mudou."); });
}
const dia = (t: number): string => new Date(t).toLocaleDateString("pt-BR");
const hhmm = (t: number): string => new Date(t).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
/** a ultima vez de um aparelho: "agora", "hoje, 21:10", "ontem, 21:10" ou a data */
function ultimaVez(t: number, agora: number): string {
  if (agora - t < 2 * 60_000) return "agora";
  const meiaNoite = new Date(agora); meiaNoite.setHours(0, 0, 0, 0);
  const m = meiaNoite.getTime();
  return t >= m ? `hoje, ${hhmm(t)}` : t >= m - 86_400_000 ? `ontem, ${hhmm(t)}` : dia(t);
}

/* ------------------------------------------------------------ Entrar */
function Entrar({ agoraNao }: { agoraNao: () => void }) {
  const ligados = CT.provedores.filter(p => p.ligado), termos = enderecoDosTermos(), privacidade = enderecoDaPrivacidade();
  return (
    <div className="ct" data-testid="ct-entrar">
      <p className="ct-chamada">A conta abre a luta ranqueada</p>
      <div><span className="ct-rot">O que vai para o servidor</span>
        <ul className="ct-vai">
          <li><span>O registro dos pets e do Tamer</span><span className="ct-etq ok">vai</span></li>
          <li><span>Um apelido</span><span className="ct-etq ok">vai</span></li>
          <li className="nao"><span>Nome, e-mail e conversa</span><span className="ct-etq">não vão</span></li>
        </ul></div>
      <Erro />
      {ligados.length > 0
        ? <div className="ct-prov">{ligados.map(p => (
            <button key={p.nome} type="button" className="hx-btn" onClick={() => entrarCom(p.nome)} data-testid={`ct-entrar-${p.nome}`}><Marca p={p.nome} />Entrar com {nomeProvedor(p.nome)}</button>))}</div>
        : <Destaque rot="Fechada" titulo="A entrada está fechada agora"><p>O jogo continua neste aparelho.</p></Destaque>}
      <div className="ct-rodape">
        <button type="button" className="hx-btn" onClick={agoraNao} data-testid="ct-agora-nao">Agora não</button>
        {termos && <a className="ct-link" href={termos} target="_blank" rel="noreferrer">Termos</a>}
        {privacidade && <a className="ct-link" href={privacidade} target="_blank" rel="noreferrer">Privacidade</a>}
      </div>
      <p className="ct-sec">Sem conta, nada muda: o pet fica neste aparelho. Sem senha. Por enquanto, só convidados com 18 anos ou mais.</p>
    </div>
  );
}

/* ------------------------------------------------------------ o primeiro acesso */
function PrimeiroAcesso({ p }: { p: Primeiro }) {
  const [idade, setIdade] = useState<"18_ou_mais" | "menos_de_18" | null>(null), [aceite, setAceite] = useState(false), [trocando, setTrocando] = useState(false);
  const termos = enderecoDosTermos(), privacidade = enderecoDaPrivacidade();
  if (trocando) return <TrocarApelido p={p} voltar={() => setTrocando(false)} />;
  const opcao = (v: "18_ou_mais" | "menos_de_18", rotulo: string) => (
    <button type="button" role="radio" aria-checked={idade === v} className="ct-filtro" onClick={() => setIdade(v)} data-testid={`ct-idade-${v}`}>{rotulo}</button>);
  return (
    <div className="ct" data-testid="ct-primeiro">
      <h4 className="ct-tit">Primeiro acesso</h4>
      <div><span className="ct-rot">Apelido</span>
        <Apelido apelido={p.apelido} sub="É como os outros veem você.">
          <button type="button" className="hx-btn" disabled={CT.ocupado} onClick={() => setTrocando(true)} data-testid="ct-trocar">Trocar</button>
        </Apelido></div>
      <div><span className="ct-rot" id="ct-idade">Idade</span>
        <div className="ct-idade" role="radiogroup" aria-labelledby="ct-idade">{opcao("18_ou_mais", "18 anos ou mais")}{opcao("menos_de_18", "Menos de 18")}</div></div>
      <Marcar marcado={aceite} mudar={setAceite} testid="ct-aceite">
        Li e aceito os {termos ? <a href={termos} target="_blank" rel="noreferrer">Termos</a> : "Termos"} e a {privacidade ? <a href={privacidade} target="_blank" rel="noreferrer">Privacidade</a> : "Privacidade"}
        <small>versão {p.versaoTermos}{p.versaoPrivacidade !== p.versaoTermos ? ` e ${p.versaoPrivacidade}` : ""}</small>
      </Marcar>
      <Erro />
      <div className="ct-bts">
        <button type="button" className="hx-continuar" disabled={idade === null || !aceite || CT.ocupado} onClick={() => agir(() => criarConta(idade!))} data-testid="ct-criar">Criar a conta</button>
        <button type="button" className="hx-btn" disabled={CT.ocupado} onClick={() => agir(cancelarPrimeiro)} data-testid="ct-cancelar">Cancelar</button>
      </div>
    </div>
  );
}
function TrocarApelido({ p, voltar }: { p: Primeiro; voltar: () => void }) {
  const atual = p.apelido.split("#")[0] ?? "", [escolhido, setEscolhido] = useState(atual);
  return (
    <div className="ct" data-testid="ct-trocar-apelido">
      <h4 className="ct-tit">Apelido</h4>
      <Apelido apelido={p.apelido} sub="O número é sorteado.">
        <button type="button" className="hx-btn" disabled={CT.ocupado} onClick={() => agir(() => trocarApelido(atual))} data-testid="ct-numero"><Shuffle aria-hidden="true" />Número</button>
      </Apelido>
      <div><span className="ct-rot" id="ct-digimon">O Digimon do apelido</span>
        <div className="ct-nomes" role="radiogroup" aria-labelledby="ct-digimon">{p.digimons.map(d => (
          <button key={d} type="button" role="radio" aria-checked={escolhido === d} className="ct-filtro" onClick={() => setEscolhido(d)} data-testid={`ct-digimon-${d}`}>{d}</button>))}</div></div>
      <Erro />
      <div className="ct-bts">
        <button type="button" className="hx-continuar" disabled={CT.ocupado} data-testid="ct-usar"
          onClick={() => agir(async () => { if (escolhido !== atual) await trocarApelido(escolhido); if (!CT.erro) voltar(); })}>Usar este</button>
        <button type="button" className="hx-btn" onClick={voltar} data-testid="ct-voltar">Voltar</button>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------ as duas pontuacoes (MMO8) */
function Cartoes({ d }: { d: DadosPerfil }) {
  const r = d.respeito, local = respeitoLocal(tamerAtual()).total, melhor = melhorDigimon(d.digimons), j = jogoAtual(), m = j.motor;
  const ativo = j.grupo ? null : linhaDoPet(d.digimons, m.semente), pct = Math.min(100, r.conferido / TAMER_LENDARIO * 100);
  const prox = r.nivel === null ? null : (r.nivel + 1 - NIVEL_DO_PRIMEIRO_MEGA) * RESPEITO_POR_NIVEL;
  return (
    <div className="rs-pont">
      <section className="rs-pc" aria-labelledby="rs-r" data-testid="ct-respeito"><span className="ct-rot" id="rs-r"><Crown aria-hidden="true" />Respeito do Tamer</span>
        <b className="rs-grande" data-testid="ct-respeito-conferido">{milhares(r.conferido)}</b>
        <small>conferido · {milhares(local)} no jogo</small>
        {r.nivel !== null && prox !== null && <span className="rs-linha"><span className="ct-etq" data-testid="ct-nivel">Nv {r.nivel}</span><small>Nv {r.nivel + 1} em {milhares(prox)}</small></span>}
        <span className="rs-barra" role="img" aria-label={`${milhares(r.conferido)} de ${milhares(TAMER_LENDARIO)} até Tamer Lendário`}><i style={{ "--v": `${pct.toFixed(0)}%` } as React.CSSProperties} /></span>
        {r.titulo ? <span className="rs-linha"><span className="ct-etq ok">{r.titulo}</span><small>a conta não para</small></span>
          : <small>Tamer Lendário em {milhares(TAMER_LENDARIO)} · a conta não para</small>}</section>
      <section className="rs-pc" aria-labelledby="rs-d" data-testid="ct-digimon"><span className="ct-rot" id="rs-d"><Trophy aria-hidden="true" />Pontos do Digimon</span>
        {melhor ? <>
          <span><b className="rs-grande" data-testid="ct-digimon-pontos">{milhares(melhor.pontos)}</b><small>{melhor.forma}{melhor.aposentado ? " · aposentado" : ""}</small></span>
          <span className="rs-linha"><span className="ct-etq ok">{melhor.posicao}º</span><small>no ranking dos Digimon</small></span>
          {melhor.pet !== m.semente && !j.grupo && <small>O ativo, {nomeForma(m.forma)}, tem {milhares(ativo?.pontos ?? 0)}. Cada pet começa do zero.</small>}
        </> : <small data-testid="ct-digimon-vazio">Nenhum pet seu pontuou ainda: os pontos vêm das lutas ranqueadas.</small>}</section>
    </div>
  );
}
function DeOndeVem({ d }: { d: DadosPerfil }) {
  const r = d.respeito, c = r.contagem;
  const linhas: [string, string, number][] = [
    ["1ª medalha de cada líder", `${c.lideres} · ${RESPEITO_FEITO.lider} cada`, r.lideres], ["título da Liga", c.liga ? "1" : "0", r.liga],
    ["resets", String(c.resets), r.resets], ["títulos da semana", `${c.titulos} · ${RESPEITO_FEITO.titulo_semana} cada`, r.titulos],
    ["selos Top do dia", `${c.selos} · ${RESPEITO_FEITO.selo_dia} cada`, r.selos],
  ];
  return (
    <details className="rs-de" data-testid="ct-de-onde"><summary><Info aria-hidden="true" />De onde vem o Respeito</summary>
      <ul>{linhas.map(([t, q, v]) => <li key={t}><span><b>{t}</b><small>{q}</small></span><span className="rs-v">+{milhares(v)}</span></li>)}</ul>
      <p>O ranking conta só o que o servidor viu nos registros enviados. Um reset que o servidor ainda não viu fica só no jogo.</p>
    </details>
  );
}
function Pontuacoes() {
  const ligado = caisNoBuild();
  useSyncExternalStore(ouvirPontuacoes, revisaoPontuacoes);
  useEffect(() => { if (ligado) void perfil.abrir(); return () => perfil.fechar(); }, [ligado]);
  if (!ligado) return null;
  const e = perfil.atual();
  if (e === null || e.passo === "buscando") return <p className="ct-sec" role="status" data-testid="ct-pontuacoes-buscando">Buscando as pontuações</p>;
  if (e.passo !== "pronto") return (
    <div className="ct-destaque" role="status" data-testid="ct-pontuacoes-sem-resposta"><span className="ct-rot">Sem resposta</span><b>As pontuações não vieram</b>
      <p>O Respeito do jogo é {milhares(respeitoLocal(tamerAtual()).total)}. O conferido continua guardado no servidor.</p>
      <div className="ct-bts"><button type="button" className="hx-btn" onClick={() => void perfil.abrir()}>Tentar de novo</button></div></div>
  );
  return (
    <>
      <Cartoes d={e.dados} />
      <DeOndeVem d={e.dados} />
      <div className="ct-bts"><a className="hx-continuar" href="#/cais" onClick={() => pedirAbaDoCais("tamers")} data-testid="ct-ver-rankings"><Anchor aria-hidden="true" />Ver os rankings no cais</a></div>
    </>
  );
}

/* ------------------------------------------------------------ o perfil e apagar */
function Perfil({ c }: { c: Conta }) {
  const [apagando, setApagando] = useState(false), agora = Date.now();
  if (apagando) return <Apagar c={c} manter={() => setApagando(false)} />;
  return (
    <div className="ct" data-testid="ct-perfil">
      <Apelido apelido={c.apelido} sub={`${c.provedores.map(nomeProvedor).join(" e ")} · desde ${dia(c.criadaEm)}`} />
      <Pontuacoes />
      <details className="rs-de" data-testid="ct-mais" open={!caisNoBuild()}><summary><Monitor aria-hidden="true" />Aparelhos, dados e a conta<ChevronRight aria-hidden="true" /></summary>
      <div className="ct"><div><span className="ct-rot">Aparelhos</span>
        <ul className="ct-ap">{c.aparelhos.map(a => (
          <li key={a.id}>{/celular|android|iphone|ipad/i.test(a.nome) ? <Smartphone aria-hidden="true" /> : <Monitor aria-hidden="true" />}
            <span><b>{a.nome}</b><small>{ultimaVez(a.vistoEm, agora)}</small></span>
            {a.atual ? <span className="ct-etq ok">aqui</span>
              : <button type="button" className="hx-btn" disabled={CT.ocupado} onClick={() => agir(() => desconectar(a.id))} aria-label={`Desconectar ${a.nome}`}>Desconectar</button>}
          </li>))}</ul></div>
      {/* o save na nuvem (CN3): a oferta de levar o pet e as cópias; sem a chave, nada */}
      <OfertaLevar />
      <CopiasDoSave />
      <div><span className="ct-rot">Seus dados</span>
        <div className="ct-dados">
          <a className="hx-btn" href={enderecoDosDados()} download data-testid="ct-baixar"><Download aria-hidden="true" />Baixar meus dados</a>
          {c.aceitoEm !== null && <span className="ct-sec">Termos e Privacidade · aceitos em {dia(c.aceitoEm)}</span>}
        </div></div>
      <Erro />
      <div className="ct-bts ct-bts--fim">
        <button type="button" className="hx-btn" disabled={CT.ocupado} onClick={() => agir(sair)} data-testid="ct-sair"><LogOut aria-hidden="true" />Sair</button>
        <button type="button" className="hx-btn ct-perigo" disabled={CT.ocupado} onClick={() => setApagando(true)} data-testid="ct-apagar"><Trash2 aria-hidden="true" />Apagar a conta</button>
      </div></div>
      </details>
    </div>
  );
}
function Apagar({ c, manter }: { c: Conta; manter: () => void }) {
  const [entendi, setEntendi] = useState(false);
  return (
    <div className="ct" data-testid="ct-apagar-tela">
      <h4 className="ct-tit">Apagar a conta</h4>
      <Destaque rot="Sem volta" titulo={`Apagar ${c.apelido}`} perigo>
        <ul className="ct-some">
          <li>Somem do servidor o apelido, os registros enviados e os aparelhos.</li>
          <li>Tudo é apagado em até 30 dias.</li>
          <li className="fica">O pet deste aparelho continua aqui.</li>
        </ul>
      </Destaque>
      <a className="hx-btn" href={enderecoDosDados()} download><Download aria-hidden="true" />Baixar meus dados antes</a>
      <Marcar marcado={entendi} mudar={setEntendi} testid="ct-entendi">Entendi que não volta</Marcar>
      <Erro />
      <div className="ct-bts">
        <button type="button" className="hx-continuar" onClick={manter} data-testid="ct-manter">Manter a conta</button>
        <button type="button" className="hx-btn ct-perigo" disabled={!entendi || CT.ocupado} onClick={() => agir(apagarConta)} data-testid="ct-apagar-sempre">Apagar para sempre</button>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------ a parte Conta */
export function TelaConta({ agoraNao, irPet }: { agoraNao: () => void; irPet: () => void }) {
  const ct = useConta();
  useEffect(() => {
    if (!ct) return;
    /* a volta do provedor: o servidor poe ?conta=<estado> no endereco; le uma vez e tira */
    const volta = voltaDaBusca(location.search);
    if (volta) history.replaceState(null, "", location.pathname + location.hash);
    /* ao abrir a parte, um estado de passagem ou de fim (a ida, o erro, a idade, a conta apagada) nao fica: pergunta de novo ao servidor */
    const fica = CT.passo?.tipo === "conta" || CT.passo?.tipo === "primeiro" || CT.passo?.tipo === "sem_conta";
    if (volta || !fica) void abrirConta(volta).catch((err: unknown) => console.error(err));
  }, [ct]);
  if (!ct) return null;
  const p = ct.passo, tentar = () => void abrirConta().catch((err: unknown) => console.error(err));
  if (p === null || p.tipo === "conferindo") return (
    <div className="ct" data-testid="ct-conferindo">
      <Passos agora={2} provedor="Entrada" />
      <Destaque rot="Conta" titulo="Conferindo a conta"><p>Você volta para onde estava.</p></Destaque>
      <div className="ct-bts"><button type="button" className="hx-btn" onClick={voltarAEntrar}>Cancelar</button></div>
    </div>
  );
  if (p.tipo === "saindo") return (
    <div className="ct" data-testid="ct-saindo">
      <Passos agora={1} provedor={p.provedor === "falso" ? "Teste" : nomeProvedor(p.provedor)} />
      <Destaque rot="Conta" titulo="Abrindo a entrada"><p>Escolha a conta na página que abrir. O jogo espera aqui.</p></Destaque>
      <div className="ct-bts"><button type="button" className="hx-btn" onClick={voltarAEntrar}>Cancelar</button></div>
    </div>
  );
  if (p.tipo === "nao_deu") return (
    <div className="ct" data-testid="ct-nao-deu">
      <Destaque rot="Não entrou" titulo="Não deu para entrar" perigo alerta><p>O jogo continua neste aparelho.</p></Destaque>
      <div className="ct-bts">
        <button type="button" className="hx-continuar" onClick={tentar} data-testid="ct-tentar">Tentar de novo</button>
        <button type="button" className="hx-btn" onClick={agoraNao}>Agora não</button>
      </div>
    </div>
  );
  if (p.tipo === "fora_da_lista") return (
    <div className="ct" data-testid="ct-fora-da-lista">
      <Destaque rot="Só convidados" titulo="Esta conta não está na lista" alerta><p>Nada foi guardado. O jogo continua neste aparelho.</p></Destaque>
      <div className="ct-bts">
        <button type="button" className="hx-continuar" onClick={voltarAEntrar} data-testid="ct-outra">Usar outra conta</button>
        <button type="button" className="hx-btn" onClick={agoraNao}>Agora não</button>
      </div>
    </div>
  );
  if (p.tipo === "menos_de_18") return (
    <div className="ct" data-testid="ct-menos-de-18">
      <Destaque rot="Idade" titulo="A conta ainda é só para adultos" alerta><p>Nada foi guardado. O jogo continua neste aparelho, sem conta.</p></Destaque>
      <div className="ct-bts"><button type="button" className="hx-continuar" onClick={() => { voltarAEntrar(); irPet(); }} data-testid="ct-voltar-ao-pet">Voltar ao pet</button></div>
    </div>
  );
  if (p.tipo === "apagada") return (
    <div className="ct" data-testid="ct-apagada">
      <Destaque rot="Conta" titulo="A conta foi apagada"><p>O pet deste aparelho continua aqui.</p></Destaque>
      <div className="ct-bts"><button type="button" className="hx-continuar" onClick={() => { voltarAEntrar(); irPet(); }}>Voltar ao pet</button></div>
    </div>
  );
  if (p.tipo === "primeiro") return <PrimeiroAcesso p={p.dados} />;
  if (p.tipo === "conta") return <Perfil c={p.conta} />;
  return <Entrar agoraNao={agoraNao} />;
}
