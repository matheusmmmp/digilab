/* cn() dos componentes no estilo shadcn (docs/TAREFA_V2_FRONT_REACT.md, etapa 2): junta as classes e resolve os conflitos do
   Tailwind (a última ganha: cn("px-4", "px-8") dá "px-8"). */
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...entradas: ClassValue[]): string {
  return twMerge(clsx(entradas));
}
