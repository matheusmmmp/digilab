/* Entrada do app. Tema: o do sistema; ?tema=claro|escuro sobrepoe (conferencia e screenshots; nao grava nada). */
import { render } from "preact";
import { App } from "./App.tsx";
import { carregarAtlas } from "./atlas.ts";
import { carregarDecoracao } from "./decoracao.tsx";
import { iniciarFalaLLM } from "./fala.ts";
import { iniciarFalaLivre } from "./falaLivre.ts";
import { gravarPendente, iniciarJogo, jogoAtual, ouvirOutrasAbas } from "./jogo.ts";
import { textoSave } from "./save.ts";
import { iniciarTema } from "./tema.ts";
import { iniciarTempo } from "./tempo.ts";
import "./estilo/tokens.css";
import "./estilo/base.css";
import "./estilo/pet.css";
import "./estilo/crescer.css";
import "./estilo/lutar.css";
import "./estilo/diario.css";

iniciarTema();

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
Object.assign(window, { __digilab: { assinatura: () => jogoAtual().motor.assinatura(), registro: () => textoSave(jogoAtual().motor) } });
const raiz = document.getElementById("app");
if (!raiz) throw new Error("sem #app na página");
render(<App />, raiz);
