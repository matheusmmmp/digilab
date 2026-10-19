/* Diario · Geracoes (prancha HerGeracoes): os pets por geracao. Aposentados (sairam ao cruzar), o ativo (AGORA) e os
   em espera. Cada filho confere a origem: a impressao do registro de cada pai tem que bater com um log que esteja
   neste aparelho; sem o log, a origem fica sem conferir (importar o arquivo resolve). So leitura. */
import { useMemo } from "react";
import { Motor, chaveSprite, hashSemente, nomeEstagio, nomeForma } from "../../../motor/index.ts";
import { dimSprite, imagemAtlas, useAtlas } from "../../atlas.ts";
import { Deco } from "../../componentes/Deco.tsx";
import { BRASAO } from "../../decoracao.ts";
import { CHAVE_GERACOES, geracao, lerAposentados } from "../../heranca.ts";
import { useJogo } from "../../jogo.ts";
import { CHAVE_GUARDADOS, abrirGuardado, lerGuardados } from "../../pets.ts";
import { diaDe } from "../pet/TelaPet.tsx";

interface Item { m: Motor; papel: "aposentado" | "ativo" | "espera" }

export function TelaGeracoes() {
  const { motor: ativo } = useJogo(), a = useAtlas();
  /* o replay dos guardados e aposentados so muda quando eles mudam (nao a cada passo do relogio) */
  const bruto = (k: string) => { try { return localStorage.getItem(k) ?? ""; } catch { return ""; } };
  const chave = `${ativo.semente}|${bruto(CHAVE_GUARDADOS).length}|${bruto(CHAVE_GERACOES).length}`;
  const fixos = useMemo((): { ap: Item[]; esp: Item[]; hashes: number[] } => {
    const ap = lerAposentados().map(x => ({ m: Motor.reproduzir(x.semente, x.log, x.versao), papel: "aposentado" as const }));
    let esp: Item[] = [];
    try { esp = lerGuardados().map(g => ({ m: abrirGuardado(g), papel: "espera" as const })); } catch { esp = []; }
    return { ap, esp, hashes: [...ap, ...esp].map(x => hashSemente(JSON.stringify(x.m.log))) };
  }, [chave]);
  const itens: Item[] = [...fixos.ap, { m: ativo, papel: "ativo" }, ...fixos.esp];
  const porHash = new Set([...fixos.hashes, hashSemente(JSON.stringify(ativo.log))]);
  const faltando: string[] = [];
  const grupos = new Map<number, Item[]>();
  for (const x of itens) { const g = geracao(x.m); grupos.set(g, [...(grupos.get(g) ?? []), x]); }
  for (const x of itens) if (x.m.origem) for (const p of x.m.origem.pais) if (!porHash.has(p.h))
    faltando.push(`${nomeForma(x.m.forma)} (geração ${geracao(x.m)}): um dos pais não está neste aparelho`);
  const spr = (m: Motor) => {
    if (a.tipo !== "ok") return null;
    const k = chaveSprite(m.forma), s = imagemAtlas(a, k, Math.max(1, Math.min(2, Math.floor(56 / dimSprite(a.dados, k)[1]))));
    return <img className="dl-pix" src={s.url} width={s.w} height={s.h} alt="" />;
  };
  const conferido = (m: Motor) => !m.origem || m.origem.pais.every(p => porHash.has(p.h));
  return (
    <div className="ger-tela">
      {[...grupos.keys()].sort((x, y) => x - y).map(g => (
        <section key={g} className="ger-linha" aria-labelledby={`ger-${g}`}>
          <h3 id={`ger-${g}`}>GERAÇÃO {g}</h3>
          <div className="ger-cards">
            {grupos.get(g)!.map((x, i) => (
              <div key={i} className={`ger-card${x.papel === "ativo" ? " agora" : ""}`}>
                <span className="ger-spr">{spr(x.m)}</span>
                <span className="ger-txt"><span className="ger-nome"><b>{nomeForma(x.m.forma)}</b><Deco nome={BRASAO[x.m.especie].peca} largura={24} altura={16} /></span>
                  <small>{x.papel === "aposentado" ? "aposentado" : x.papel === "ativo" ? "você · agora" : "em espera"} · {nomeEstagio(x.m.forma)} · {diaDe(x.m.e.tick)} d</small>
                  <span className="ger-tags">{x.papel === "ativo" && <span className="dl-tag dl-tag--ativo">AGORA</span>}
                    {x.m.origem && <span className={conferido(x.m) ? "ger-ok" : "ger-falta"}>{conferido(x.m) ? "✓ origem conferida" : "! log de um pai ausente"}</span>}</span></span>
              </div>
            ))}
          </div>
        </section>
      ))}
      {faltando.length > 0 && <p className="ger-aviso">{faltando.join(". ")}. Importe o arquivo do pai para conferir a origem.</p>}
      <p className="dl-apoio">Um pet aposentado saiu do jogo ao cruzar: ele fica aqui, só para ver. Nada se perde.</p>
    </div>
  );
}
