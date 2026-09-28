/* Entrada do app. Tema: o do sistema; ?tema=claro|escuro sobrepoe (conferencia e screenshots; nao grava nada). */
import { render } from "preact";
import { App } from "./App.tsx";
import { carregarAtlas } from "./atlas.ts";
import { iniciarFalaLLM } from "./fala.ts";
import { iniciarFalaLivre } from "./falaLivre.ts";
import { gravarPendente, iniciarJogo, ouvirOutrasAbas } from "./jogo.ts";
import { iniciarTempo } from "./tempo.ts";
import "./estilo/tokens.css";
import "./estilo/base.css";
import "./estilo/pet.css";

const tema = new URLSearchParams(location.search).get("tema");
if (tema === "claro" || tema === "escuro") document.documentElement.dataset.tema = tema;

iniciarJogo(localStorage);
carregarAtlas();
ouvirOutrasAbas();
iniciarTempo();
iniciarFalaLLM();
iniciarFalaLivre();
/* o tempo grava no maximo a cada 2 s: o que ficou pendente sai ao esconder ou fechar a aba */
addEventListener("visibilitychange", () => { if (document.visibilityState === "hidden") gravarPendente(); });
addEventListener("pagehide", gravarPendente);
const raiz = document.getElementById("app");
if (!raiz) throw new Error("sem #app na página");
render(<App />, raiz);
