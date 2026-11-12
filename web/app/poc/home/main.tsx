/* A entrada da POC da página inicial (docs/pranchas/ux-pagina-inicial/POC.md). Fica fora do build do jogo: só o poc/vite.config.ts a lê. */
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./home.css";
import { Home } from "./Home.tsx";

const raiz = document.getElementById("raiz");
if (!raiz) throw new Error("sem #raiz na página");
createRoot(raiz).render(<StrictMode><Home /></StrictMode>);
