/* Teto de gasto TOTAL em dolares, persistido em arquivo fora do git (reiniciar nao zera): porte do ControleGasto de servidor/fala_llm.py,
   no mesmo formato de arquivo. Antes de cada chamada reserva o custo maximo possivel; se a reserva passaria do teto, nao chama. Depois acerta
   pelo `usage` real; se a chamada falha sem `usage`, conta o maximo reservado (errar para o lado do credito). Node e de uma thread so: a
   reserva e o acerto nao precisam de trava. */
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { CATALOGO } from "./catalogo.ts";

export interface GastoDict { gasto_usd: number; limite_usd: number; chamadas: number; restante_usd: number }
export type Alerta = (nivel: number, gasto: GastoDict) => void;

const arred6 = (x: number): number => Math.round(x * 1e6) / 1e6;

export class ControleGasto {
  readonly limite: number;
  readonly arquivo: string | null;
  reservado = 0;
  gasto = 0;
  chamadas = 0;
  avisados: number[] = [];
  private readonly alerta: Alerta | null;
  private readonly niveis: number[];

  constructor(limiteUsd: number, arquivo: string | null, alerta: Alerta | null = null, niveis: number[] = [0.5, 0.8, 1.0]) {
    if (!(limiteUsd >= 0)) throw new Error("limite de gasto negativo");
    this.limite = limiteUsd;
    this.arquivo = arquivo;
    this.alerta = alerta;
    this.niveis = [...niveis].sort((a, b) => a - b);
    if (arquivo !== null && existsSync(arquivo)) {
      /* arquivo corrompido ou sem os campos: falha alto (nao recomeca do zero em silencio) */
      const d = JSON.parse(readFileSync(arquivo, "utf8"));
      const gasto = Number(d.gasto_usd), chamadas = Number(d.chamadas);
      if (!Number.isFinite(gasto) || !Number.isInteger(chamadas)) throw new Error(`arquivo de gasto invalido: ${arquivo}`);
      this.gasto = gasto;
      this.chamadas = chamadas;
      this.avisados = (d.alertas_enviados ?? []).map(Number);
    }
  }

  private salvar(): void {
    if (this.arquivo === null) return;
    const d = { gasto_usd: this.gasto, chamadas: this.chamadas, limite_usd: this.limite, alertas_enviados: this.avisados };
    writeFileSync(this.arquivo, JSON.stringify(d, null, 1), "utf8");
  }

  /** niveis cruzados e ainda nao avisados; marca e salva (os avisados nao se repetem ao reiniciar) */
  private novosNiveis(esgotado: boolean): number[] {
    const frac = this.limite > 0 ? this.gasto / this.limite : 1;
    const novos = this.niveis.filter(n => !this.avisados.includes(n) && (frac >= n || (esgotado && n >= 1)));
    if (novos.length) {
      this.avisados.push(...novos);
      this.salvar();
    }
    return novos;
  }

  private avisar(novos: number[]): void {
    if (this.alerta) for (const n of novos) this.alerta(n, this.paraDict());
  }

  reservar(custoMax: number): boolean {
    if (this.gasto + this.reservado + custoMax > this.limite) {
      this.avisar(this.novosNiveis(true));
      return false;
    }
    this.reservado += custoMax;
    return true;
  }

  acertar(custoMax: number, custoReal: number): void {
    this.reservado -= custoMax;
    this.gasto += custoReal;
    this.chamadas += 1;
    this.salvar();
    this.avisar(this.novosNiveis(false));
  }

  paraDict(): GastoDict {
    return { gasto_usd: arred6(this.gasto), limite_usd: this.limite, chamadas: this.chamadas, restante_usd: arred6(Math.max(0, this.limite - this.gasto)) };
  }
}

/** custo em US$ (tabela de precos do catalogo; modelo fora dela levanta erro) */
export function custoUsd(modelo: string, tokensEntrada: number, tokensSaida: number): number {
  const p = CATALOGO.precos_usd_por_mtok[modelo];
  if (!p) throw new Error(`modelo sem preco: ${modelo}`);
  return (tokensEntrada * p[0] + tokensSaida * p[1]) / 1_000_000;
}
