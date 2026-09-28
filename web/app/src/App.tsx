/* Esqueleto do app (TAREFA_FRONT_TS, Etapa 3): cabecalho do pet, painel do destino com sub-abas, barra dos
   4 destinos e rodape. A rota vem do endereco (#/destino/aba) ou da aba lembrada, como no HTML. */
import { useEffect, useState } from "preact/hooks";
import { useAtlas } from "./atlas.ts";
import { Cabecalho } from "./componentes/Cabecalho.tsx";
import { Nav } from "./componentes/Nav.tsx";
import { useJogo } from "./jogo.ts";
import {
  DESTINOS, NOME_ABA, NOME_DESTINO, ROTA_INICIAL, enderecoDaRota, gravarAbaLembrada, lerAbaLembrada, rotaDoEndereco,
  type Aba, type Destino, type Rota,
} from "./rotas.ts";
import { TelaProvisoria } from "./telas/Provisoria.tsx";

const armaz = (): Storage => localStorage;

function rotaInicial(): Rota {
  return rotaDoEndereco(location.hash) ?? lerAbaLembrada(armaz()) ?? ROTA_INICIAL;
}

export function App() {
  const jogo = useJogo(), atlas = useAtlas();
  const [rota, setRota] = useState<Rota>(rotaInicial);
  const [ultima, setUltima] = useState<Partial<Record<Destino, Aba>>>(() => ({ [rota.destino]: rota.aba }));

  /* endereco e aba lembrada acompanham a rota; voltar/avancar do navegador muda a rota */
  useEffect(() => {
    const alvo = enderecoDaRota(rota);
    if (location.hash !== alvo) history.replaceState(null, "", alvo);
    gravarAbaLembrada(armaz(), rota);
    document.body.dataset.destino = rota.destino;
    document.title = `${NOME_DESTINO[rota.destino]} · Digilab Pet`;
  }, [rota]);
  useEffect(() => {
    const aoMudar = () => { const r = rotaDoEndereco(location.hash); if (r) setRota(r); };
    addEventListener("hashchange", aoMudar);
    return () => removeEventListener("hashchange", aoMudar);
  }, []);

  const ir = (r: Rota) => { setRota(r); setUltima(u => ({ ...u, [r.destino]: r.aba })); };
  const irDestino = (d: Destino) => { ir({ destino: d, aba: ultima[d] ?? DESTINOS[d][0] }); scrollTo(0, 0); };
  const abas = DESTINOS[rota.destino];

  return (
    <div class="app">
      {jogo.erroSave && (
        <div class="aviso" role="alert">
          O save deste navegador não abriu, e o app não vai gravar por cima dele.
          <p>{jogo.erroSave.erro}. Mostrando o pet de exemplo.</p>
        </div>
      )}
      {atlas.tipo === "erro" && (
        <div class="aviso" role="alert">
          Atlas de sprites não carregou.
          <p>{atlas.erro}. Rode <code>python gerar_atlas_up.py</code> em D:\Trab\digilab\Assets.</p>
        </div>
      )}
      <Cabecalho />
      <section class="painel" aria-labelledby="tela-titulo">
        <div class="tela-cab dl-faixa"><h1 class="dl-num" id="tela-titulo">{NOME_DESTINO[rota.destino]}</h1></div>
        {abas.length > 1 && (
          <div class="tabs" role="tablist" aria-label={`Abas de ${NOME_DESTINO[rota.destino]}`}>
            {abas.map(a => (
              <button type="button" role="tab" key={a} class="tab" aria-selected={a === rota.aba} onClick={() => ir({ destino: rota.destino, aba: a })}>{NOME_ABA[a]}</button>
            ))}
          </div>
        )}
        <div role={abas.length > 1 ? "tabpanel" : undefined}>
          <TelaProvisoria aba={rota.aba} />
        </div>
      </section>
      <footer>
        <span>{jogo.origem === "save" ? "Pet aberto do save deste navegador (replay do registro)." : "Nenhum save aberto: pet de exemplo."}</span>
        <span><b>Versão local com sprites do Digimon UP (Bandai), só para uso pessoal. Não publicar nem distribuir.</b></span>
      </footer>
      <Nav atual={rota.destino} ir={irDestino} />
    </div>
  );
}
