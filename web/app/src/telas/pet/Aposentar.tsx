/* Aposentar: o reset do pet (MMO8; a prancha docs/pranchas/ux-reset/, telas 1 a 4; UX-RS-1 a 7 APROVADAS pelo Matheus em 2026-11-19, pela
   recomendacao). Aberto de Meus pets, no pet ativo (UX-RS-1). Tres passos na mesma caixa: o resumo (o nivel do reset em escada, o bonus com
   as travas em texto, o que vai e o que fica), a confirmacao em dois passos no molde de "Apagar a conta" (UX-RS-2) e o feito, com um
   caminho so: "Escolher o brasao". No desktop entra no painel do App (pagina); no celular, numa caixa centralizada.

   As regras e as chamadas ficam em src/reset.ts; os pontos do Digimon vem do GET /digimons (src/cais/pontuacoes.ts). Os textos e os
   tamanhos sao PROPOSTOS, SEM FONTE (os da prancha). */
import { useEffect, useRef, useState } from "react";
import { Check, Coins, Crown, Egg, Info, Layers, Trophy, UserRound } from "lucide-react";
import { chaveSprite, nomeEstagio, nomeForma, type Motor } from "../../../motor/index.ts";
import { dimSprite, imagemAtlas, useAtlas } from "../../atlas.ts";
import { abrirModal } from "../../componentes/modal.ts";
import { PainelHx } from "../../componentes/hx/index.ts";
import { BRASAO } from "../../decoracao.ts";
import { geracao } from "../../heranca.ts";
import { jogoAtual, tamerAtual, useJogo } from "../../jogo.ts";
import { abrirEscolhaBrasao } from "../../jornada.ts";
import { buscarDigimons, linhaDoPet, milhares } from "../../cais/pontuacoes.ts";
import { SemResposta } from "../../cais/cais.ts";
import { BONUS_RESET, PONTOS_MINIMOS_RESET, respeitoLocal, type NivelReset } from "../../ranking/pontos.ts";
import { aposentarPorReset, fecharAposentar, previaDoReset, semReset } from "../../reset.ts";
import type { BitsGanhos, ResetPet } from "../../tamer.ts";
import { caisNoBuild } from "../cais/TelaCais.tsx";
import { diaDe } from "./TelaPet.tsx";
import "../../estilo/conta.css";
import "../../estilo/cais.css";
import "../../estilo/reset.css";

/** o que o pet chegou a, por nivel do reset (MMO-18) */
const CHEGOU: Record<Exclude<NivelReset, 0>, string> = { 1: "Ultimate", 2: "Mega", 3: "Mega e o título da Liga" };
const NIVEIS = [1, 2, 3] as const;

/** os pontos conferidos do pet no servidor: sem o servidor no build, sem conta, buscando, sem resposta, ou os pontos (0 sem linha) */
type Pontos = { tipo: "sem_servidor" } | { tipo: "sem_conta" } | { tipo: "buscando" } | { tipo: "sem_resposta" } | { tipo: "pronto"; pontos: number };
function usePontosDoPet(semente: number): Pontos {
  const [p, setP] = useState<Pontos>(() => (caisNoBuild() ? { tipo: "buscando" } : { tipo: "sem_servidor" }));
  useEffect(() => {
    if (p.tipo === "sem_servidor") return;
    let vivo = true;
    buscarDigimons().then(r => { if (vivo) setP(r === null ? { tipo: "sem_conta" } : { tipo: "pronto", pontos: linhaDoPet(r, semente)?.pontos ?? 0 }); },
      (err: unknown) => { if (!(err instanceof SemResposta)) console.error(err); if (vivo) setP({ tipo: "sem_resposta" }); });
    return () => { vivo = false; };
  }, [semente]);   // eslint-disable-line react-hooks/exhaustive-deps
  return p;
}

function CartaoPet({ m }: { m: Motor }) {
  const a = useAtlas(), k = chaveSprite(m.forma);
  const img = a.tipo === "ok" ? imagemAtlas(a, k, Math.max(1, Math.min(2, Math.floor(56 / dimSprite(a.dados, k)[1])))) : null;
  return (
    <div className="rs-pet" data-testid="rs-pet">
      <span className="rs-palco">{img && <img className="dl-pix" src={img.url} width={img.w} height={img.h} alt="" />}</span>
      <span><b>{nomeForma(m.forma)}</b><small>{nomeEstagio(m.forma)} · {BRASAO[m.especie].nome} · Dia {diaDe(m.e.tick)} · {geracao(m)}ª geração</small>
        {m.liga.titulos > 0 && <span className="ct-etq ok">título da Liga</span>}</span>
    </div>
  );
}

function Escada({ nivel }: { nivel: NivelReset }) {
  return (
    <ol className="rs-escada" aria-label="Os níveis do reset" data-testid="rs-escada">
      {NIVEIS.map(n => {
        const eu = n === nivel, b = BONUS_RESET[n];
        return (
          <li key={n} className={"rs-nv" + (eu ? " rs-eu" : n < nivel ? " rs-feito" : "")} aria-current={eu ? "true" : undefined}>
            <span className="rs-nv-n">{n}</span>
            <span><b>{CHEGOU[n]}</b>{eu && <span className="ct-etq ok">este pet</span>}</span>
            <span className="rs-nv-v"><b>+{milhares(b.respeito)}</b><small>Respeito</small></span>
            <span className="rs-nv-v"><b>+{b.bits}</b><small>Bits</small></span>
          </li>
        );
      })}
    </ol>
  );
}

/** a linha do Respeito, com a trava dos 200 pontos conferidos em texto; ok: entra no ranking */
function linhaRespeito(p: Pontos): { ok: boolean; sub: string } {
  switch (p.tipo) {
    case "sem_servidor": return { ok: true, sub: "no seu perfil" };
    case "sem_conta": return { ok: false, sub: "no seu perfil; o ranking pede a conta" };
    case "buscando": return { ok: true, sub: "conferindo os pontos dele no servidor" };
    case "sem_resposta": return { ok: false, sub: `os pontos dele não vieram do servidor; o ranking pede ${PONTOS_MINIMOS_RESET} conferidos` };
    case "pronto": return p.pontos >= PONTOS_MINIMOS_RESET
      ? { ok: true, sub: `entra no ranking: ele tem ${milhares(p.pontos)} pontos conferidos (o mínimo é ${PONTOS_MINIMOS_RESET})` }
      : { ok: false, sub: `fica só no seu perfil: ele tem ${milhares(p.pontos)} pontos conferidos, e o ranking pede ${PONTOS_MINIMOS_RESET}` };
  }
}

function Bonus({ nivel, p, bitsPagos }: { nivel: Exclude<NivelReset, 0>; p: Pontos; bitsPagos: boolean }) {
  const b = BONUS_RESET[nivel], r = linhaRespeito(p);
  return (
    <ul className="rs-bonus" aria-label="O bônus deste reset" data-testid="rs-bonus">
      <li className={r.ok ? undefined : "rs-parcial"} data-testid="rs-bonus-respeito"><Crown aria-hidden="true" />
        <span><b>+{milhares(b.respeito)} Respeito</b><small>{r.sub}</small></span></li>
      <li className={bitsPagos ? "rs-parcial" : undefined} data-testid="rs-bonus-bits"><Coins aria-hidden="true" />
        <span><b>{bitsPagos ? "0" : "+" + b.bits} Bits</b><small>{bitsPagos ? "o reset desta semana já foi pago: o próximo, na segunda" : "o reset pago desta semana"}</small></span></li>
    </ul>
  );
}

function FicaSai({ m }: { m: Motor }) {
  return (
    <div className="rs-duas">
      <div><span className="ct-rot">Vai para Gerações</span>
        <ul className="rs-lista">
          <li><Layers aria-hidden="true" />{nomeForma(m.forma)}, com a vida inteira, só para ver</li>
          <li><Trophy aria-hidden="true" />os pontos dele ficam no ranking dos Digimon</li>
        </ul></div>
      <div><span className="ct-rot">Fica com você</span>
        <ul className="rs-lista fica">
          <li><Check aria-hidden="true" />as medalhas, os itens e o título</li>
          <li><Check aria-hidden="true" />os Bits, o portão e as melhorias</li>
          <li><Check aria-hidden="true" />o nível, o Respeito, os selos</li>
          <li><Check aria-hidden="true" />os pets guardados</li>
        </ul></div>
    </div>
  );
}

const COMO = "O reset é do pet, não do Tamer: o Digimon se aposenta e um ovo novo choca. O bônus vem do ponto a que ele chegou. "
  + "O ovo novo começa do zero, sem os stats do anterior. O cruzamento também conta como reset do pai que se aposenta.";
const Como = () => <details className="rs-como"><summary><Info aria-hidden="true" />Como o reset funciona</summary><p>{COMO}</p></details>;

function Destaque({ rot, titulo, tom, children }: { rot: string; titulo: string; tom?: "perigo" | "ok"; children?: React.ReactNode }) {
  return <div className={"ct-destaque" + (tom ? " " + tom : "")} role="status"><span className="ct-rot">{rot}</span><b>{titulo}</b>{children}</div>;
}

/** por que nao da para aposentar agora, em texto do jogo */
const TEXTO_SEM_RESET: [RegExp, string][] = [
  [/dois pets/, "Os dois pets ainda não se aposentam: o reset do par vem numa etapa própria."],
  [/laboratório/, "O pet de teste do laboratório não se aposenta."],
  [/exemplo/, "O pet de exemplo não é seu: choque um ovo primeiro."],
  [/ovo ainda/, "O ovo ainda não chocou."],
];

type Feito = { reset: ResetPet; bits: BitsGanhos | null; respeito: number; saldo: number };

function Corpo({ fechar }: { fechar: () => void }) {
  const { motor: m } = useJogo(), j = jogoAtual(), [passo, setPasso] = useState<"resumo" | "confirmar">("resumo");
  const [entendi, setEntendi] = useState(false), [ocupado, setOcupado] = useState(false), [erro, setErro] = useState(""), [feito, setFeito] = useState<Feito | null>(null);
  const pontos = usePontosDoPet(m.semente);
  if (feito) {
    const n = feito.reset.nivel;
    return (
      <div className="ct rs" data-testid="rs-feito">
        <Destaque rot="Reset feito" titulo={`${feito.reset.forma} foi para Gerações`} tom="ok">
          <p>{n === 0 ? "Sem bônus: ele não chegou ao Ultimate." : `Nível ${n} do reset: ${CHEGOU[n]}.`}</p></Destaque>
        {n > 0 && <ul className="rs-bonus" aria-label="O que entrou">
          <li><Crown aria-hidden="true" /><span><b>+{milhares(BONUS_RESET[n].respeito)} Respeito</b>
            <small>agora {milhares(feito.respeito)} · conferido quando o servidor vir o registro dele</small></span></li>
          <li className={feito.bits ? undefined : "rs-parcial"}><Coins aria-hidden="true" /><span><b>{feito.bits ? "+" + feito.bits.valor : "0"} Bits</b>
            <small>{feito.bits ? `saldo ${milhares(feito.saldo)}` : "o reset desta semana já foi pago"}</small></span></li>
        </ul>}
        <div className="ct-bts"><button type="button" className="hx-continuar" onClick={() => { fechar(); abrirEscolhaBrasao(); }} data-testid="rs-brasao">
          <Egg aria-hidden="true" />Escolher o brasão</button></div>
      </div>
    );
  }
  const nao = semReset(j);
  if (nao) return (
    <div className="ct rs" data-testid="rs-sem-reset">
      <CartaoPet m={m} />
      <Destaque rot="Agora não" titulo="Este pet não se aposenta agora"><p>{TEXTO_SEM_RESET.find(([r]) => r.test(nao))?.[1] ?? nao}</p></Destaque>
      <div className="ct-bts"><button type="button" className="hx-continuar" onClick={fechar}>Voltar a Meus pets</button></div>
    </div>
  );
  const pv = previaDoReset(m, tamerAtual());
  const fazer = async () => {
    setOcupado(true); setErro("");
    try {
      const r = await aposentarPorReset(), t = tamerAtual();
      setFeito({ ...r, respeito: respeitoLocal(t).total, saldo: t.bits });
    } catch (err) { setErro(err instanceof Error ? err.message : String(err)); }
    finally { setOcupado(false); }
  };
  if (passo === "confirmar") return (
    <div className="ct rs" data-testid="rs-confirmar">
      <Destaque rot="Sem volta" titulo={`Aposentar ${nomeForma(m.forma)}`} tom="perigo">
        <ul className="ct-some">
          <li>Ele vai para Gerações e não volta a ser o ativo.</li>
          <li>Você escolhe o brasão do ovo novo em seguida.</li>
          {pv.nivel > 0 && <li className="fica">+{milhares(pv.respeito)} Respeito{pv.bits > 0 ? ` e +${pv.bits} Bits` : ""}.</li>}
        </ul>
      </Destaque>
      <label className="ct-aceite" data-testid="rs-entendi"><input type="checkbox" checked={entendi} onChange={e => setEntendi(e.target.checked)} />
        <span className="ct-caixa" aria-hidden="true"><Check /></span><span>Entendi que não volta</span></label>
      {erro && <p className="mc-erro" role="alert">{erro}</p>}
      <div className="ct-bts">
        <button type="button" className="hx-continuar" onClick={() => { setPasso("resumo"); setEntendi(false); }} data-testid="rs-manter">Manter {nomeForma(m.forma)}</button>
        <button type="button" className="hx-btn ct-perigo" disabled={!entendi || ocupado} onClick={() => void fazer()} data-testid="rs-aposentar-sempre"><Egg aria-hidden="true" />Aposentar</button>
      </div>
    </div>
  );
  if (pv.nivel === 0) return (
    <div className="ct rs" data-testid="rs-sem-bonus">
      <CartaoPet m={m} />
      <Destaque rot="Sem bônus" titulo="O bônus começa no Ultimate"><p>Aposentar agora é o recomeço de sempre: o pet vai para Gerações e nada entra.</p></Destaque>
      <div className="ct-bts"><button type="button" className="hx-continuar" onClick={fechar}>Continuar com ele</button>
        <button type="button" className="hx-btn" onClick={() => setPasso("confirmar")} data-testid="rs-aposentar">Aposentar assim</button></div>
    </div>
  );
  return (
    <div className="ct rs" data-testid="rs-resumo">
      <CartaoPet m={m} />
      <div><span className="ct-rot">O nível do reset</span><Escada nivel={pv.nivel} /></div>
      <Bonus nivel={pv.nivel} p={pontos} bitsPagos={pv.bitsDaSemanaPagos} />
      {pontos.tipo === "pronto" && pontos.pontos < PONTOS_MINIMOS_RESET &&
        <p className="ca-parcial"><Info aria-hidden="true" /><span>Os pontos vêm das lutas ranqueadas. Depois do reset, ele não luta mais.</span></p>}
      {pv.bitsDaSemanaPagos && <p className="ca-parcial"><Info aria-hidden="true" /><span>O Respeito entra igual. Os Bits pagam um reset por semana.</span></p>}
      <FicaSai m={m} />
      <Como />
      <div className="ct-bts">
        <button type="button" className="hx-btn" onClick={fechar}>Agora não</button>
        {pontos.tipo === "sem_conta" && <a className="hx-btn" href="#/config/conta"><UserRound aria-hidden="true" />Entrar</a>}
        <button type="button" className="hx-btn ct-perigo" onClick={() => setPasso("confirmar")} data-testid="rs-aposentar"><Egg aria-hidden="true" />Aposentar e chocar um ovo</button>
      </div>
    </div>
  );
}

/** `pagina`: no painel do desktop (o App poe o titulo); senao, a caixa centralizada do celular */
export function Aposentar({ pagina = false }: { pagina?: boolean }) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => { if (!pagina) abrirModal(ref.current); }, []);   // eslint-disable-line react-hooks/exhaustive-deps
  const fechar = () => { if (pagina) fecharAposentar(); else ref.current?.close(); };
  if (pagina) return <Corpo fechar={fechar} />;
  return (
    <dialog className="meus-pets mc-dialogo" ref={ref} aria-label="Aposentar" onClose={fecharAposentar}>
      <PainelHx titulo="Aposentar" onFechar={() => ref.current?.close()} rotuloFechar="Fechar Aposentar"><Corpo fechar={fechar} /></PainelHx>
    </dialog>
  );
}
