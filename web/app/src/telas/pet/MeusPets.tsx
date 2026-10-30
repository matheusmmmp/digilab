/* Meus pets no celular (layout habitat, M5): caixa centralizada na pele XCOM (PainelHx num <dialog>); no desktop e o
   MeusPetsDesktop dentro do PainelTela. O pet ativo, exportar o registro e voltar ao pet anterior (guardado pelos Cenarios).
   Um pet por vez: o jogo guarda o registro de um pet so; ovo novo e no Registro, com confirmacao. */
import { useEffect, useMemo, useRef, useState } from "react";
import "../../estilo/menus_config.css";
import { DO_ESP, Motor, NOME_EST, OVO, chaveSprite, lutadorPet, nomeEstagio, nomeForma, vidaExibida } from "../../../motor/index.ts";
import { dimSprite, imagemAtlas, useAtlas } from "../../atlas.ts";
import { abrirModal } from "../../componentes/modal.ts";
import { BotaoHx, ChipHx, PainelHx } from "../../componentes/hx/index.ts";
import { trocarMotor, useJogo } from "../../jogo.ts";
import { LUTA, previa } from "../../luta.ts";
import { CHAVE } from "../../save.ts";
import { abrirGuardado, ativarGuardado, lerGuardados } from "../../pets.ts";
import { abrirHeranca, podeSerPai } from "../../heranca.ts";
import { abrirImportar, exportarArquivo, nomeArquivo } from "../../importar.ts";
import { dec } from "../../componentes/Barras.tsx";
import { diaDe } from "./TelaPet.tsx";

export const CHAVE_ANTERIOR = CHAVE + "-anterior";
const lerAnterior = (): string | null => { try { return localStorage.getItem(CHAVE_ANTERIOR); } catch { return null; } };

/** volta ao pet guardado antes de um cenario (replay do registro guardado); falha alto se nao abrir */
export function voltarAoAnterior(): string {
  const bruto = lerAnterior();
  if (!bruto) return "Não há pet anterior guardado.";
  const d = JSON.parse(bruto);
  if (!Number.isInteger(d?.semente) || !Array.isArray(d?.log)) throw new Error("pet anterior guardado não tem semente e registro");
  trocarMotor(Motor.reproduzir(d.semente, d.log, d.versao ?? 1), "save");
  try { localStorage.removeItem(CHAVE_ANTERIOR); } catch { /* ja trocou */ }
  LUTA.rivalFixo = null; previa("arena");
  return "Pet anterior restaurado pelo replay do registro guardado.";
}

/** os pets guardados (varios pets, um ativo): parados no tempo; Ativar troca com o ativo */
function Guardados({ ativar, cruzar }: { ativar: (i: number) => void; cruzar: ((i: number) => void) | null }) {
  const a = useAtlas();
  const lista = useMemo(() => {
    try { return lerGuardados().map(g => abrirGuardado(g)); } catch { return null; }
  }, []);
  if (lista === null) return <p className="mc-erro">Os pets guardados não abriram.</p>;
  if (!lista.length) return null;
  return (
    <section aria-labelledby="mp-guard-tit" className="mc-guardados">
      <h3 className="mc-sec" id="mp-guard-tit">Guardados · o tempo deles está parado</h3>
      {cruzar && <p className="mc-apoio">Seu pet é adulto: ele pode cruzar com outro adulto. O filho herda o temperamento dos dois e o brasão de um deles; nada aprendido passa adiante.</p>}
      <ul className="mc-lista">
        {lista.map((g, i) => {
          const img = a.tipo === "ok" ? imagemAtlas(a, chaveSprite(g.forma)) : null, p = lutadorPet(g, "", true).cond;
          return (
            <li key={i} className="mc-guardado">
              <span className="mc-palco mc-palco--congelado">{img && <img className="dl-pix" src={img.url} width={img.w} height={img.h} alt="" />}</span>
              <span className="mc-guardado__txt"><b>{nomeForma(g.forma)}</b>
                <span><ChipHx tom="rotulo">{nomeEstagio(g.forma)}</ChipHx> dia {diaDe(g.e.tick)}</span>
                <span className="mc-apoio">vida {Math.round(vidaExibida(p, g.forma.est, g.treino.total, g.versao)).toLocaleString("pt-BR")} · treino +{dec(g.treino.total, 0)}</span></span>
              <span className="mc-guardado__bts">
                <BotaoHx onClick={() => ativar(i)}>Ativar</BotaoHx>
                {cruzar && podeSerPai(g) &&
                  <BotaoHx onClick={() => cruzar(i)} title="o filho herda o temperamento dos dois e a espécie de um deles">Nova geração</BotaoHx>}
              </span>
            </li>
          );
        })}
      </ul>
    </section>
  );
}

/** Meus pets (celular): o pet ativo, o aviso de um pet por vez, os guardados, o pet anterior (se houver) e os botoes.
    Exportar baixa o registro (mesmo conteudo do save). */
export function MeusPets({ fechar, irRegistro }: { fechar: () => void; irRegistro: () => void }) {
  const { motor: m, nascendo } = useJogo(), a = useAtlas(), ref = useRef<HTMLDialogElement>(null), [msg, setMsg] = useState("");
  useEffect(() => { abrirModal(ref.current); }, []);
  const ovo = nascendo > 0, nome = ovo ? OVO[m.especie] : chaveSprite(m.forma);
  let img = null;
  if (a.tipo === "ok") { const h = dimSprite(a.dados, nome)[1]; img = imagemAtlas(a, nome, Math.max(1, Math.min(3, Math.floor(150 / h)))); }
  const anterior = lerAnterior();
  let antImg = null;
  if (anterior && a.tipo === "ok") {
    try { const d = JSON.parse(anterior); antImg = Number.isInteger(d?.semente) ? imagemAtlas(a, OVO[Motor.reproduzir(d.semente, [], d.versao ?? 1).especie]) : null; } catch { antImg = null; }
  }
  const ativar = (i: number) => {
    try { ativarGuardado(i); setMsg(""); ref.current?.close(); } catch (err) { setMsg(err instanceof Error ? err.message : String(err)); }
  };
  /* heranca: so com o ativo adulto e vivo; o filho vira o ativo */
  const podeCruzar = !ovo && podeSerPai(m);
  const cruzar = (i: number) => {
    ref.current?.close(); abrirHeranca(i);
  };
  /* o arquivo .digilab e o proprio save do pet (semente, registro e versao) */
  const exportar = () => { exportarArquivo(m); setMsg("Registro baixado: " + nomeArquivo(m)); };
  return (
    <dialog className="meus-pets mc-dialogo" ref={ref} aria-label="Meus pets" onClose={fechar}>
      <PainelHx titulo="Meus pets" onFechar={() => ref.current?.close()} rotuloFechar="Fechar Meus pets">
        <div className="mc">
          <section className="mc-detalhe" aria-label="Pet ativo">
            <div className="mc-detalhe__cab"><h3 className="mc-bloco__tit">{ovo ? "Digi-Egg " + DO_ESP[m.especie] : nomeForma(m.forma)}</h3>
              <ChipHx tom="ok">ATIVO</ChipHx><ChipHx tom="rotulo">{ovo ? NOME_EST.ovo : nomeEstagio(m.forma)}</ChipHx></div>
            <div className="mc-palco mc-palco--ativo">{img && <img className="dl-pix" src={img.url} width={img.w} height={img.h} alt="" />}</div>
          </section>
          <p className="mc-apoio">Só o pet ativo tem o tempo correndo; os guardados ficam parados onde estavam.</p>
          <Guardados ativar={ativar} cruzar={podeCruzar ? cruzar : null} />
          {anterior && <div className="mc-anterior">{antImg && <img className="dl-pix" src={antImg.url} width={antImg.w / 2} height={antImg.h / 2} alt="" />}
            <span><b>Pet anterior guardado</b><span>ficou salvo quando você usou o Laboratório</span></span></div>}
          {anterior && <BotaoHx className="mc-largo" onClick={() => { setMsg(voltarAoAnterior()); ref.current?.close(); }}>Voltar ao pet anterior</BotaoHx>}
          <BotaoHx className="mc-largo" onClick={() => { ref.current?.close(); irRegistro(); }}>Registro e novo ovo</BotaoHx>
          <BotaoHx className="mc-largo" onClick={exportar}>Exportar registro</BotaoHx>
          <BotaoHx className="mc-largo" onClick={() => { ref.current?.close(); abrirImportar(); }}>Importar pet</BotaoHx>
          <p className="mc-apoio" aria-live="polite">{msg}</p>
        </div>
      </PainelHx>
    </dialog>
  );
}
