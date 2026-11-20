/* Etapa 2 da TAREFA_V2_FRONT_REACT: o Tailwind, o shadcn e o lucide configurados (nenhuma tela usa ainda). O Button no estilo shadcn
   sai como <button> com as classes do tema, o cn() resolve conflito de classe e um ícone do lucide sai como SVG. */
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { Heart } from "lucide-react";
import { describe, expect, it } from "vitest";
import { Button } from "../src/componentes/ui/button.tsx";
import { cn } from "../src/lib/utils.ts";

describe("shadcn e lucide", () => {
  it("cn junta as classes e a última ganha no conflito do Tailwind", () => {
    expect(cn("px-4 text-sm", false && "hidden", "px-8")).toBe("text-sm px-8");
  });
  it("o Button é um <button type=button> com o alvo de 44 px e as cores do tema", () => {
    const html = renderToStaticMarkup(createElement(Button, null, "Alimentar"));
    expect(html).toMatch(/^<button data-slot="button" type="button" class="[^"]*">Alimentar<\/button>$/);
    expect(html).toContain("min-h-11");
    expect(html).toContain("bg-primary text-primary-foreground");
  });
  it("as variantes trocam as classes e o className de fora ganha", () => {
    const html = renderToStaticMarkup(createElement(Button, { variant: "outline", size: "lg", className: "px-2" }, "Ver"));
    expect(html).toContain("border-border bg-background");
    expect(html).toContain("px-2");
    expect(html).not.toContain("px-6");
  });
  it("um ícone do lucide sai como SVG de traço", () => {
    const svg = renderToStaticMarkup(createElement(Heart, { size: 20 }));
    expect(svg).toMatch(/^<svg [^>]*class="lucide lucide-heart[^"]*"/);
    expect(svg).toContain('stroke-width="2"');
  });
});
