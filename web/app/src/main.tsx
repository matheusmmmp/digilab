/* Entrada do app. Tema: o do sistema; ?tema=claro|escuro sobrepoe (conferencia e screenshots; nao grava nada). */
import { render } from "preact";
import { App } from "./App.tsx";
import { carregarAtlas } from "./atlas.ts";
import { iniciarJogo } from "./jogo.ts";
import "./estilo/tokens.css";
import "./estilo/base.css";

const tema = new URLSearchParams(location.search).get("tema");
if (tema === "claro" || tema === "escuro") document.documentElement.dataset.tema = tema;

iniciarJogo(localStorage);
carregarAtlas();
const raiz = document.getElementById("app");
if (!raiz) throw new Error("sem #app na página");
render(<App />, raiz);
