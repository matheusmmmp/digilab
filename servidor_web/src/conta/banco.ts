/* O banco da conta (CN2, docs/PLANO_V3_CONTA.md seção 4): SQLite pelo node:sqlite do Node 24, sem dependência nova.
   O arquivo fica fora do git (DIGILAB_BANCO; por padrão servidor_web/dados/conta.sqlite, no .gitignore). O Litestream (a cópia para o R2)
   é a CN5 e só lê o mesmo arquivo: por isso o modo WAL.

   As migrações são versionadas pelo PRAGMA user_version: a lista MIGRACOES só cresce (nunca se edita uma que já saiu), e cada uma roda
   numa transação. Um banco de versão maior que a do código não abre (o código antigo não sabe ler o banco novo).

   O que NÃO entra no banco (seção 9): o nome, o e-mail e o lugar. A lista de convidados por e-mail guarda só o SHA-256 do e-mail. */
import { mkdirSync } from "node:fs";
import { dirname } from "node:path";
import { DatabaseSync } from "node:sqlite";

export type Banco = DatabaseSync;

export const MIGRACOES: readonly string[] = [
  /* 1: a conta (CN2) */
  `
  CREATE TABLE contas (
    id         TEXT PRIMARY KEY,
    apelido    TEXT NOT NULL UNIQUE,
    criada_em  INTEGER NOT NULL,
    idade      TEXT NOT NULL CHECK (idade IN ('18_ou_mais'))
  ) STRICT;
  CREATE TABLE identidades (
    provedor     TEXT NOT NULL,
    id_provedor  TEXT NOT NULL,
    conta_id     TEXT NOT NULL REFERENCES contas(id) ON DELETE CASCADE,
    criada_em    INTEGER NOT NULL,
    PRIMARY KEY (provedor, id_provedor)
  ) STRICT;
  CREATE INDEX identidades_conta ON identidades(conta_id);
  CREATE TABLE consentimentos (
    conta_id            TEXT NOT NULL REFERENCES contas(id) ON DELETE CASCADE,
    versao_termos       TEXT NOT NULL,
    versao_privacidade  TEXT NOT NULL,
    aceito_em           INTEGER NOT NULL,
    PRIMARY KEY (conta_id, versao_termos, versao_privacidade)
  ) STRICT;
  CREATE TABLE aparelhos (
    id         TEXT PRIMARY KEY,
    conta_id   TEXT NOT NULL REFERENCES contas(id) ON DELETE CASCADE,
    nome       TEXT NOT NULL,
    criado_em  INTEGER NOT NULL,
    visto_em   INTEGER NOT NULL
  ) STRICT;
  CREATE INDEX aparelhos_conta ON aparelhos(conta_id);
  CREATE TABLE sessoes (
    token_hash   TEXT PRIMARY KEY,
    conta_id     TEXT NOT NULL REFERENCES contas(id) ON DELETE CASCADE,
    aparelho_id  TEXT NOT NULL REFERENCES aparelhos(id) ON DELETE CASCADE,
    csrf         TEXT NOT NULL,
    criada_em    INTEGER NOT NULL,
    expira_em    INTEGER NOT NULL
  ) STRICT;
  CREATE INDEX sessoes_conta ON sessoes(conta_id);
  CREATE TABLE estados_oauth (
    state        TEXT PRIMARY KEY,
    provedor     TEXT NOT NULL,
    verificador  TEXT NOT NULL,
    destino      TEXT NOT NULL,
    expira_em    INTEGER NOT NULL
  ) STRICT;
  CREATE TABLE acessos_pendentes (
    token_hash   TEXT PRIMARY KEY,
    provedor     TEXT NOT NULL,
    id_provedor  TEXT NOT NULL,
    apelido      TEXT NOT NULL,
    csrf         TEXT NOT NULL,
    destino      TEXT NOT NULL,
    expira_em    INTEGER NOT NULL
  ) STRICT;
  CREATE TABLE convidados (
    chave          TEXT PRIMARY KEY,
    adicionado_em  INTEGER NOT NULL
  ) STRICT;
  `,
  /* 2: os envios dos logs (MMO3, servidor_web/src/envio/): a linha de cada envio conferido fica; os registros, só do envio aceito e até
     apagar_em (MMO-4, seção 11 do plano MMO). Os dois pendem da conta: apagar a conta leva os envios */
  `
  CREATE TABLE envios (
    id                TEXT PRIMARY KEY,
    conta_id          TEXT NOT NULL REFERENCES contas(id) ON DELETE CASCADE,
    recebido_em       INTEGER NOT NULL,
    pet               INTEGER NOT NULL,
    versao_pet        INTEGER NOT NULL,
    eventos           INTEGER NOT NULL,
    hash_log          TEXT NOT NULL,
    versao_tamer      INTEGER NOT NULL,
    hash_tamer        TEXT NOT NULL,
    resultado         TEXT NOT NULL CHECK (resultado IN ('aceito', 'recusado')),
    motivo            TEXT,
    detalhe           TEXT,
    marco10           TEXT CHECK (marco10 IN ('confere', 'de_outro_pet', 'sem_marco')),
    pontos            REAL NOT NULL,
    lutas_ranqueadas  INTEGER NOT NULL,
    ms_conferencia    REAL NOT NULL,
    CHECK ((resultado = 'aceito') = (motivo IS NULL AND marco10 IS NOT NULL))
  ) STRICT;
  CREATE INDEX envios_conta ON envios(conta_id, pet);
  CREATE TABLE envios_registros (
    envio_id        TEXT PRIMARY KEY REFERENCES envios(id) ON DELETE CASCADE,
    registro_pet    TEXT NOT NULL,
    registro_tamer  TEXT NOT NULL,
    apagar_em       INTEGER NOT NULL
  ) STRICT;
  CREATE INDEX envios_registros_apagar ON envios_registros(apagar_em);
  `,
];

export const VERSAO_BANCO = MIGRACOES.length;

/** a versão gravada no arquivo (PRAGMA user_version) */
export function versaoDe(banco: Banco): number {
  return Number((banco.prepare("PRAGMA user_version").get() as { user_version: number }).user_version);
}

/** roda as migrações que faltam, cada uma na sua transação; devolve quantas rodaram */
export function migrar(banco: Banco): number {
  const atual = versaoDe(banco);
  if (atual > VERSAO_BANCO) throw new Error(`o banco está na versão ${atual}, e este código só conhece até a ${VERSAO_BANCO}`);
  for (let v = atual; v < VERSAO_BANCO; v++) {
    banco.exec("BEGIN IMMEDIATE");
    try {
      banco.exec(MIGRACOES[v]!);
      banco.exec(`PRAGMA user_version = ${v + 1}`);
      banco.exec("COMMIT");
    } catch (err) {
      banco.exec("ROLLBACK");
      throw err;
    }
  }
  return VERSAO_BANCO - atual;
}

/** abre (e cria, se faltar) o banco no caminho dado, ou na memória com ":memory:"; liga as chaves estrangeiras e migra */
export function abrirBanco(caminho: string): Banco {
  if (caminho !== ":memory:") mkdirSync(dirname(caminho), { recursive: true });
  const banco = new DatabaseSync(caminho);
  banco.exec("PRAGMA foreign_keys = ON");
  if (caminho !== ":memory:") banco.exec("PRAGMA journal_mode = WAL");
  banco.exec("PRAGMA busy_timeout = 5000");
  migrar(banco);
  return banco;
}

/** roda `f` numa transação: tudo ou nada */
export function transacao<T>(banco: Banco, f: () => T): T {
  banco.exec("BEGIN IMMEDIATE");
  try {
    const r = f();
    banco.exec("COMMIT");
    return r;
  } catch (err) {
    banco.exec("ROLLBACK");
    throw err;
  }
}
