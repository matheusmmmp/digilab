import { defineConfig } from "vitest/config";

/* testTimeout: os testes que refazem uma vida inteira (a conferência, o reset) levam ~4 s numa máquina livre, e o runner do CI, com os
   arquivos em paralelo (o e2e da nuvem da CN3 junto), passava dos 5 s do padrão. 20 s (PROPOSTO, SEM FONTE; D-CONTA-196) */
export default defineConfig({
  test: { include: ["test/**/*.test.ts"], environment: "node", testTimeout: 20_000 },
});
