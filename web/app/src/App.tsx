/* Esqueleto do app (TAREFA_FRONT_TS, Etapa 3): cabecalho do pet, painel do destino com sub-abas, barra dos
   4 destinos e rodape. A rota vem do endereco (#/destino/aba) ou da aba lembrada, como no HTML. */
import { useEffect, useState } from "preact/hooks";
import { useAtlas } from "./atlas.ts";
import { Nav } from "./componentes/Nav.tsx";
import { RevelacaoEvolucao } from "./componentes/Revelacao.tsx";
import { useJogo } from "./jogo.ts";
import {
  DESTINOS, NOME_ABA, NOME_DESTINO, ROTA_INICIAL, enderecoDaRota, gravarAbaLembrada, lerAbaLembrada, rotaDoEndereco,
  type Aba, type Destino, type Rota,
} from "./rotas.ts";
import { TelaCatalogo } from "./telas/diario/TelaCatalogo.tsx";
import { TelaCenarios } from "./telas/diario/TelaCenarios.tsx";
import { TelaRegistro } from "./telas/diario/TelaRegistro.tsx";
import { TelaAprend } from "./telas/crescer/TelaAprend.tsx";
import { TelaEvolucao } from "./telas/crescer/TelaEvolucao.tsx";
import { TelaTreinar } from "./telas/crescer/TelaTreinar.tsx";
import { TelaArena } from "./telas/lutar/TelaArena.tsx";
import { TelaCampanha } from "./telas/lutar/TelaCampanha.tsx";
import { TelaConversar } from "./telas/conversar/TelaConversar.tsx";
import { TelaPet } from "./telas/pet/TelaPet.tsx";
import { CHAVE } from "./save.ts";

const armaz = (): Storage => localStorage;

/* slogan so na primeira visita (preferencia de tela, chave propria; a chave do save nao muda) */
function primeiraVisita(): boolean {
  try { if (localStorage.getItem(CHAVE + "-boas-vindas") !== "1") { localStorage.setItem(CHAVE + "-boas-vindas", "1"); return true; } } catch { /* sem armazenamento */ }
  return false;
}

function rotaInicial(): Rota {
  return rotaDoEndereco(location.hash) ?? lerAbaLembrada(armaz()) ?? ROTA_INICIAL;
}

export function App() {
  const jogo = useJogo(), atlas = useAtlas();
  const [rota, setRota] = useState<Rota>(rotaInicial);
  const [boasVindas] = useState(primeiraVisita);
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
      {boasVindas && (
        <header class="boas-vindas">
          <h1 class="dl-num">DIGILAB</h1>
          <p>Crie, cuide e treine um pet que aprende com você. Depois, leve-o para a arena.</p>
        </header>
      )}
      {rota.destino === "pet" ? <TelaPet irRegistro={() => ir({ destino: "diario", aba: "registro" })} />
        : rota.destino === "conversar" ? <TelaConversar voltar={() => { ir({ destino: "pet", aba: "estado" }); scrollTo(0, 0); }} /> : (
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
          {rota.aba === "treinar" ? <TelaTreinar /> : rota.aba === "aprend" ? <TelaAprend /> : rota.aba === "evolucao" ? <TelaEvolucao />
            : rota.aba === "arena" ? <TelaArena voltarPet={() => { ir({ destino: "pet", aba: "estado" }); scrollTo(0, 0); }} />
            : rota.aba === "campanha" ? <TelaCampanha voltarPet={() => { ir({ destino: "pet", aba: "estado" }); scrollTo(0, 0); }} />
            : rota.aba === "registro" ? <TelaRegistro irPet={() => { ir({ destino: "pet", aba: "estado" }); scrollTo(0, 0); }} />
            : rota.aba === "catalogo" ? <TelaCatalogo /> : <TelaCenarios />}
        </div>
      </section>)}
      <footer>
        <span>Motor do Digilab em TypeScript: mesmas regras e parâmetros de <code>config.py</code>. O gerador aleatório é outro, então os resultados não batem bit a bit com os artefatos de pesquisa em Python.</span>
        <span><b>Versão local com sprites do Digimon UP (Bandai), só para uso pessoal. Não publicar nem distribuir.</b></span>
        <span><a href="../digilab_sprites.html?antigo=1">Versão antiga (HTML)</a>: mesmo save; não abra as duas ao mesmo tempo no mesmo pet.</span>
      </footer>
      <Nav atual={rota.destino} ir={irDestino} />
      <RevelacaoEvolucao />
    </div>
  );
}
