/* Lutar · Fronteira, as instalacoes da parte 4c (docs/DESIGN_FRONTEIRA.md, secoes 3 e 5; motor/fabrica.ts, motor/salao.ts, src/fronteira.ts):
   - a Fabrica: a regra, o recorde do Tamer e "Tentar"; a escolha entre os 3 alugados (o Digimon, o arquetipo e o nivel); a tentativa em
     andamento (o alugado e a vida dele, a serie e a luta, a ultima luta) e, depois de cada vitoria, a oferta de troca pelo rival derrotado;
   - o Salao: a regra, o recorde e a escolha do pet de cada nivel (o ativo e os guardados; a tela diz qual nivel falta) e a ultima tentativa.
   Tudo sai do registro do Tamer (as tentativas) e dos pets; as lutas nao sao animadas aqui: o resultado aparece no proprio card. */
import { useMemo, useState } from "preact/hooks";
import { ALUGUEIS_FABRICA, DO_ESP, ESTAGIOS_SALAO, FABRICA, LUTAS_SERIE_FABRICA, NOME_ARQ, NOME_ESP, NOME_EST, SALAO, alugueisFabrica, chaveSprite, formaRivalSalao,
  nomeForma, sementeFabrica, type Estagio, type Forma, type TentativaFabrica } from "../../../motor/index.ts";
import { imagemAtlas, useAtlas } from "../../atlas.ts";
import { useJogo } from "../../jogo.ts";
import { alugarFabrica, candidatosSalao, estagiosQueFaltam, lutarFabrica, tentarSalao, trocarFabrica, type CandidatoSalao, type OrigemPet } from "../../fronteira.ts";
import { CHAVE_GUARDADOS } from "../../pets.ts";
import type { Tamer } from "../../tamer.ts";

const pct = (x: number): string => `${Math.round(x * 100)}%`;
const series = (n: number): string => `${n} série${n === 1 ? "" : "s"}`;
const arq = (f: Forma): string => NOME_ARQ[f.adulta!];
const erroDe = (err: unknown): string => err instanceof Error ? err.message : String(err);

/** o sprite 1x de uma forma (sem o atlas, nada: o layout nao depende da arte) */
function Sprite({ f, cls }: { f: Forma; cls: string }) {
  const a = useAtlas();
  if (a.tipo !== "ok") return null;
  const i = imagemAtlas(a, chaveSprite(f));
  return <img class={`dl-pix ${cls}`} src={i.url} width={i.w} height={i.h} alt="" />;
}
/** as lutas de uma tentativa da Fabrica, da mais nova para a mais velha */
function LutasFabrica({ t }: { t: TentativaFabrica }) {
  if (!t.lutas.length) return null;
  return (
    <ol class="fb-lutas" aria-label={`Lutas da tentativa ${t.n}`}>
      {[...t.lutas].reverse().slice(0, 6).map(l => (
        <li key={l.k} class={l.venceu ? "vit" : "der"}>
          <span class="dl-lcd">S{Math.floor(l.k / LUTAS_SERIE_FABRICA) + 1}·L{l.k % LUTAS_SERIE_FABRICA + 1}</span>
          <span>{nomeForma(l.alugado)} × {nomeForma(l.rival)} ({arq(l.rival)}): <b>{l.venceu ? "venceu" : "perdeu"}</b> em {l.res.turnos.length} turnos, com {pct(l.vidaFim)} da vida no fim{l.trocou ? "; trocou por ele" : ""}.</span>
        </li>
      ))}
    </ol>
  );
}

/** a Fabrica: o jogador nao usa o proprio pet */
export function CartaoFabrica({ t, lutando }: { t: Tamer; lutando: boolean }) {
  useJogo();
  const [escolhendo, setEscolhendo] = useState(false), [msg, setMsg] = useState("");
  const aberta = !!t.titulo, atual = t.fabricaAtual, ult = t.fabrica[t.fabrica.length - 1] ?? null, rec = t.recordeFabrica;
  const n = t.fabrica.length + 1, alugueis = useMemo(() => alugueisFabrica(sementeFabrica(n)), [n]);
  const agir = (f: () => void) => { try { f(); setMsg(""); } catch (err) { setMsg(erroDe(err)); } };
  const p = atual?.proxima() ?? null, u = atual?.lutas[atual.lutas.length - 1] ?? null, troca = !!atual && !atual.porqueNaoTroca();
  return (
    <li class={`dl-card fr-inst-card fb-card${aberta ? "" : " fr-inst-card--fechada"}`} aria-labelledby="fr-inst-fabrica">
      <span class="fr-inst-cab">
        <b class="fr-inst-nome" id="fr-inst-fabrica">{FABRICA.nome}</b>
        <span class="fr-inst-rec" aria-label={`recorde do Tamer: ${series(rec?.valor ?? 0)}`}><span class="dl-num">{rec?.valor ?? 0}</span><small>séries</small></span>
      </span>
      <span class="fr-inst-frase">{FABRICA.frase}</span>
      <span class="fr-inst-quem">{rec ? `Recorde do Tamer: ${series(rec.valor)} seguida${rec.valor === 1 ? "" : "s"}, na tentativa ${rec.n}.`
        : aberta ? "Sem recorde ainda: a primeira série vencida já é um." : "Abre depois do título da Liga dos Líderes."}</span>
      {atual && p ? <>
        <p class="fb-status" role="status"><b>Tentativa {atual.n}</b> · série {p.serie}, luta {p.naSerie} de {LUTAS_SERIE_FABRICA} · {series(atual.series)} vencida{atual.series === 1 ? "" : "s"}</p>
        <div class="fb-alugado">
          <Sprite f={atual.alugado} cls="fb-spr" />
          <span class="fb-alugado-txt">
            <b>{nomeForma(atual.alugado)}</b>
            <span class="fr-tags"><span class="dl-tag fr-tag-arq">{arq(atual.alugado)}</span><span class="dl-tag fr-tag-esp">Mega · {NOME_ESP[atual.alugado.esp]}</span></span>
            <span class="fb-vida"><span class="fb-vida-trilho" role="img" aria-label={`vida do alugado: ${pct(atual.vidaAgora)}`}><i style={{ width: pct(atual.vidaAgora) }} /></span>
              <small>{p.naSerie === 1 ? "inteiro: a série começa com a vida cheia" : `${pct(atual.vidaAgora)} da vida: sem cura dentro da série`}</small></span>
          </span>
        </div>
        {u && <p class="fb-ultima" role="status">Luta {u.k + 1}: venceu {nomeForma(u.rival)} ({arq(u.rival)}) em {u.res.turnos.length} turnos.</p>}
        {troca && u && <div class="fb-troca">
          <span>Trocar o alugado pelo rival derrotado? {nomeForma(u.rival)} entra com a mesma parte da vida: a troca não cura.</span>
          <button type="button" class="dl-btn dl-btn--sec fb-trocar" disabled={lutando} onClick={() => agir(trocarFabrica)}>Trocar por {nomeForma(u.rival)} ({arq(u.rival)})</button>
        </div>}
        <button type="button" class="dl-btn fr-inst-tentar fb-lutar" disabled={lutando} onClick={() => agir(lutarFabrica)}>Lutar: série {p.serie}, luta {p.naSerie} de {LUTAS_SERIE_FABRICA}</button>
      </> : escolhendo && aberta ? <>
        <p class="fb-status">Tentativa {n}: escolha 1 dos {ALUGUEIS_FABRICA} alugados.</p>
        <ul class="fb-alugueis" aria-label="Os alugados desta tentativa">
          {alugueis.map((f, i) => (
            <li key={i}><button type="button" class="fb-aluguel" disabled={lutando} onClick={() => agir(() => { alugarFabrica(i); setEscolhendo(false); })}
              aria-label={`Alugar ${nomeForma(f)}: ${arq(f)}, Mega, brasão ${DO_ESP[f.esp]}`}>
              <Sprite f={f} cls="fb-spr" /><b>{nomeForma(f)}</b><span class="dl-tag fr-tag-arq">{arq(f)}</span><small>Mega · {NOME_ESP[f.esp]}</small>
            </button></li>
          ))}
        </ul>
        <button type="button" class="dl-btn dl-btn--sec fb-voltar" onClick={() => setEscolhendo(false)}>Voltar</button>
      </> : <>
        {ult && ult.acabou && (() => { const l = ult.lutas[ult.lutas.length - 1]; return (
          <p class="fb-ultima">Última tentativa: {series(ult.series)} vencida{ult.series === 1 ? "" : "s"}; perdeu para {nomeForma(l.rival)} ({arq(l.rival)}) na série {Math.floor(l.k / LUTAS_SERIE_FABRICA) + 1}, luta {l.k % LUTAS_SERIE_FABRICA + 1}.</p>); })()}
        <button type="button" class="dl-btn fr-inst-tentar" disabled={!aberta || lutando} onClick={() => setEscolhendo(true)}>{t.fabrica.length ? "Tentar de novo" : "Tentar"}</button>
      </>}
      {(atual ?? ult) && <LutasFabrica t={(atual ?? ult)!} />}
      {msg && <p class="med-erro" role="alert">{msg}</p>}
    </li>
  );
}

const nivel = (e: Estagio): string => NOME_EST[e];
/** o texto dos guardados (muda quando um guardado muda: a lista do Salao se refaz so entao, nao a cada passo do tempo) */
const guardadosBrutos = (): string | null => { try { return localStorage.getItem(CHAVE_GUARDADOS); } catch { return null; } };
const lista = (xs: string[]): string => xs.length < 2 ? xs.join("") : xs.slice(0, -1).join(", ") + " e " + xs[xs.length - 1];

/** o Salao: um pet de cada nivel */
export function CartaoSalao({ t, lutando }: { t: Tamer; lutando: boolean }) {
  const jogo = useJogo(), [msg, setMsg] = useState(""), [escolha, setEscolha] = useState<Partial<Record<Estagio, OrigemPet>>>({});
  const aberta = !!t.titulo, rec = t.recordeSalao, ult = t.salao[t.salao.length - 1] ?? null;
  /* os pets que podem lutar, refeitos quando o jogo muda (os guardados sao lidos do armazenamento) */
  const { motor: m } = jogo, bruto = guardadosBrutos();
  const cands = useMemo((): CandidatoSalao[] | string => { if (!aberta) return []; try { return candidatosSalao(t); } catch (err) { return erroDe(err); } },
    [aberta, bruto, m, m.semente, m.estagioAtual, !!m.morte, m.fronteira, m.salao.tentativas, t.salao.length, t.n]);
  const ok = typeof cands === "string" ? [] : cands.filter(c => !c.erro), faltam = typeof cands === "string" ? [...ESTAGIOS_SALAO] : estagiosQueFaltam(cands);
  const escolhido = (e: Estagio): CandidatoSalao | undefined => ok.find(c => c.est === e && c.origem === escolha[e]) ?? ok.find(c => c.est === e);
  const tentar = () => {
    try {
      const esc = ESTAGIOS_SALAO.map(e => { const c = escolhido(e); if (!c) throw new Error(`falta um pet ${nivel(e)}`); return c.origem; });
      const r = tentarSalao(esc), v = r.lutas.filter(x => x.venceu).length;
      setMsg(`${v === ESTAGIOS_SALAO.length ? "Venceu os 4 níveis!" : `Venceu ${v} de ${ESTAGIOS_SALAO.length} níveis seguidos.`}`);
    } catch (err) { setMsg(erroDe(err)); }
  };
  return (
    <li class={`dl-card fr-inst-card sl-card${aberta ? "" : " fr-inst-card--fechada"}`} aria-labelledby="fr-inst-salao">
      <span class="fr-inst-cab">
        <b class="fr-inst-nome" id="fr-inst-salao">{SALAO.nome}</b>
        <span class="fr-inst-rec" aria-label={`recorde do Tamer: ${rec?.valor ?? 0} de ${ESTAGIOS_SALAO.length} níveis`}><span class="dl-num">{rec?.valor ?? 0}</span><small>de {ESTAGIOS_SALAO.length}</small></span>
      </span>
      <span class="fr-inst-frase">{SALAO.frase}</span>
      <span class="fr-inst-quem">{rec ? `Recorde do Tamer: ${rec.valor} nív${rec.valor === 1 ? "el" : "eis"} seguido${rec.valor === 1 ? "" : "s"}, na tentativa ${rec.n}.`
        : aberta ? "Sem recorde ainda: vencer o Rookie já é um." : "Abre depois do título da Liga dos Líderes."}</span>
      {aberta && <>
        {typeof cands === "string" && <p class="med-erro" role="alert">Os pets guardados não abriram: {cands}</p>}
        <ul class="sl-niveis" aria-label="O pet de cada nível">
          {ESTAGIOS_SALAO.map(e => {
            const doNivel = ok.filter(c => c.est === e), c = escolhido(e), id = `sl-${e}`;
            return (
              <li key={e} class={c ? "" : "falta"}>
                <span class="sl-spr">{c && <Sprite f={c.m.forma} cls="fb-spr" />}</span>
                <label for={id} class="sl-nivel">{nivel(e)}</label>
                {doNivel.length
                  ? <select id={id} class="sl-sel" disabled={lutando} value={String(c!.origem)}
                      onChange={ev => { const v = (ev.currentTarget as HTMLSelectElement).value; setEscolha(x => ({ ...x, [e]: v === "ativo" ? "ativo" : Number(v) })); }}>
                      {doNivel.map(x => <option key={String(x.origem)} value={String(x.origem)}>{x.nome}{x.origem === "ativo" ? " (ativo)" : " (guardado)"}</option>)}
                    </select>
                  : <span id={id} class="sl-falta">Falta um pet {nivel(e)}</span>}
              </li>
            );
          })}
        </ul>
        {faltam.length > 0 && <p class="med-espera" role="status"><b>Falta pet {faltam.length === 1 ? "do nível" : "dos níveis"} {lista(faltam.map(nivel))}.</b> O Salão pede um pet vivo de cada nível, o ativo ou um guardado (Pet · Meus pets).</p>}
      </>}
      <button type="button" class="dl-btn fr-inst-tentar" disabled={!aberta || faltam.length > 0 || lutando} onClick={tentar}>{t.salao.length ? "Tentar de novo" : "Tentar"}</button>
      {ult && <ol class="fb-lutas sl-ultima" aria-label={`Tentativa ${ult.n} do Salão`}>
        {ESTAGIOS_SALAO.map((e, i) => { const l = ult.lutas[i]; return (
          <li key={e} class={!l ? "nao" : l.venceu ? "vit" : "der"}>
            <span class="dl-lcd">{nivel(e)}</span>
            <span>{l ? <>{l.forma} × {nomeForma(formaRivalSalao(l.s, e))}: <b>{l.venceu ? "venceu" : "perdeu"}</b>.</> : "não chegou a lutar."}</span>
          </li>); })}
      </ol>}
      {msg && <p class={msg.startsWith("Venceu") ? "fb-ultima" : "med-erro"} role={msg.startsWith("Venceu") ? "status" : "alert"}>{msg}</p>}
    </li>
  );
}
