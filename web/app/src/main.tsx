/* Entrada do app. Tema: o do sistema; ?tema=claro|escuro sobrepoe (conferencia e screenshots; nao grava nada). */
import { createRoot } from "react-dom/client";
import { App } from "./App.tsx";
import { carregarAtlas } from "./atlas.ts";
import { carregarDecoracao } from "./decoracao.ts";
import { iniciarFalaLLM } from "./fala.ts";
import { iniciarFalaLivre } from "./falaLivre.ts";
import { gravarPendente, iniciarJogo, jogoAtual, ouvirOutrasAbas } from "./jogo.ts";
import { textoSave } from "./save.ts";
import { iniciarEscala } from "./escala.ts";
import { iniciarTema } from "./tema.ts";
import { iniciarTempo } from "./tempo.ts";
import { CHAVE_GUARDADOS, semearGuardados } from "./pets.ts";
import { descartarPetsAntigos } from "./tamer.ts";
import { ligarEscala } from "../motor/index.ts";
import "./estilo/tokens.css";
import "./estilo/base.css";
import "./estilo/pet.css";
import "./estilo/crescer.css";
import "./estilo/lutar.css";
import "./estilo/diario.css";
import "./estilo/decoracao.css";
import "./estilo/desktop.css";
import "./estilo/digibrain.css";
import "./estilo/tailwind.css";

iniciarTema();
iniciarEscala();
/* escala de stats (ConfigEscala, TAREFA_PLANILHA_PROGRESSAO Parte C) ligada no jogo; ?escala=0 desliga so para a
   conferencia de paridade com o HTML antigo (e2e), que nao tem a escala */
ligarEscala(new URLSearchParams(location.search).get("escala") !== "0");

/* descarte unico dos pets antigos (decisoes do Matheus): os v1-v5 na chegada das medalhas do Tamer
   (docs/DESIGN_MEDALHAS_ARENAS.md) e os v6 de antes do combate V21D (docs/VALIDACAO_V21D.md); o aviso fica pendente para o
   App; roda uma vez por versao do descarte (tamer.CHAVE_DESCARTE). Antes de abrir o save */
try { descartarPetsAntigos(localStorage, CHAVE_GUARDADOS); } catch (err) { console.error("descarte dos pets antigos falhou", err); }
iniciarJogo(localStorage);
carregarAtlas();
carregarDecoracao();
ouvirOutrasAbas();
iniciarTempo();
iniciarFalaLLM();
iniciarFalaLivre();
/* o tempo grava no maximo a cada 2 s: o que ficou pendente sai ao esconder ou fechar a aba */
addEventListener("visibilitychange", () => { if (document.visibilityState === "hidden") gravarPendente(); });
addEventListener("pagehide", gravarPendente);
/* conferencia (teste ponta a ponta, Etapa 5): so leitura do pet vivo; nada aqui muda o motor */
Object.assign(window, { __digilab: { assinatura: () => jogoAtual().motor.assinatura(), registro: () => textoSave(jogoAtual().motor), tick: () => jogoAtual().motor.e.tick, digibrain: () => jogoAtual().motor.digibrain() } });
/* varios pets: no primeiro acesso a esta versao, a escada de pets guardados de exemplo (fraco -> forte), depois da
   primeira pintura para nao atrasar a abertura */
setTimeout(() => { try { semearGuardados(); } catch (err) { console.error("pets guardados de exemplo:", err); } }, 400);
const raiz = document.getElementById("app");
if (!raiz) throw new Error("sem #app na página");
createRoot(raiz).render(<App />);
