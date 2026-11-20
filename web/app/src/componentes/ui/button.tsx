/* Botão no estilo shadcn (docs/TAREFA_V2_FRONT_REACT.md, etapa 2), para as telas que passarem a Tailwind (a tela Pet do protótipo,
   etapa 3). É o button.tsx do shadcn com duas diferenças: um <button> de verdade no lugar do primitivo do base-ui (sem dependência
   nova), e o alvo de toque de 44 px do guia (UI_GUIDELINES §7) em todos os tamanhos. As cores são as do tema (src/estilo/tailwind.css),
   que apontam para os tokens --ui-*. */
import type { ComponentProps } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "../../lib/utils.ts";

export const buttonVariants = cva(
  "inline-flex min-h-11 shrink-0 items-center justify-center gap-2 rounded-lg border border-transparent text-sm font-semibold whitespace-nowrap transition-all outline-none select-none focus-visible:ring-3 focus-visible:ring-ring/50 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        outline: "border-border bg-background hover:bg-muted hover:text-foreground",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-muted hover:text-foreground",
        destructive: "bg-destructive/10 text-destructive hover:bg-destructive/20",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "px-4",
        sm: "px-3 text-xs",
        lg: "px-6 text-base",
        icon: "min-w-11",
      },
    },
    defaultVariants: { variant: "default", size: "default" },
  },
);

export function Button({ className, variant, size, type = "button", ...props }: ComponentProps<"button"> & VariantProps<typeof buttonVariants>) {
  return <button data-slot="button" type={type} className={cn(buttonVariants({ variant, size, className }))} {...props} />;
}
