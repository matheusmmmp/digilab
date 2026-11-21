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
  /* 3: a luta ranqueada (MMO4, servidor_web/src/envio/sementes.ts): as sementes entregues (pendem da conta), o segredo de cada semana
     (do servidor, não da conta: publicado quando a semana fecha, MMO5) e, em cada envio, quantas sementes a conferência usou e os marcos do
     Tamer (a trava do nível do pedido) */
  `
  ALTER TABLE envios ADD COLUMN sementes INTEGER NOT NULL DEFAULT 0;
  ALTER TABLE envios ADD COLUMN marcos_tamer TEXT NOT NULL DEFAULT '[]';
  CREATE TABLE segredos_semana (
    semana     TEXT PRIMARY KEY,
    segredo    TEXT NOT NULL,
    criado_em  INTEGER NOT NULL
  ) STRICT;
  CREATE TABLE sementes (
    conta_id    TEXT NOT NULL REFERENCES contas(id) ON DELETE CASCADE,
    numero      INTEGER NOT NULL,
    pet         INTEGER NOT NULL,
    versao_pet  INTEGER NOT NULL,
    indice      INTEGER NOT NULL,
    hash_ate    TEXT NOT NULL,
    semente     INTEGER NOT NULL,
    hora        INTEGER NOT NULL,
    dia         TEXT NOT NULL,
    semana      TEXT NOT NULL,
    PRIMARY KEY (conta_id, numero)
  ) STRICT;
  CREATE INDEX sementes_dia ON sementes(conta_id, dia);
  CREATE INDEX sementes_pet ON sementes(conta_id, pet, versao_pet, numero);
  `,
  /* 4: o ranking da semana (MMO5, servidor_web/src/envio/semanas.ts): em cada semente, o que a conferência do envio achou dela (NULL
     até o primeiro envio que a confere); no segredo, quando a semana congelou e ele foi publicado (NULL com a semana aberta); e as
     tabelas congeladas, que pendem da conta (apagar a conta tira a linha dela) */
  `
  ALTER TABLE sementes ADD COLUMN situacao TEXT CHECK (situacao IN ('vitoria', 'derrota', 'nao_enviada', 'pendente', 'fora_da_arena', 'acima_do_limite'));
  ALTER TABLE sementes ADD COLUMN estagio TEXT;
  ALTER TABLE sementes ADD COLUMN rival TEXT;
  ALTER TABLE sementes ADD COLUMN faixa TEXT;
  ALTER TABLE sementes ADD COLUMN envio_id TEXT;
  CREATE INDEX sementes_semana ON sementes(semana);
  ALTER TABLE segredos_semana ADD COLUMN publicado_em INTEGER;
  CREATE TABLE tabelas_semana (
    semana           TEXT NOT NULL,
    estagio          TEXT NOT NULL,
    posicao          INTEGER NOT NULL,
    conta_id         TEXT NOT NULL REFERENCES contas(id) ON DELETE CASCADE,
    pontos           REAL NOT NULL,
    rivais_vencidos  INTEGER NOT NULL,
    lutas_usadas     INTEGER NOT NULL,
    hora_dos_pontos  INTEGER,
    PRIMARY KEY (semana, estagio, posicao)
  ) STRICT;
  CREATE INDEX tabelas_semana_conta ON tabelas_semana(conta_id);
  `,
  /* 5: o rival e o mapa que o pedido da semente prometeu (D-CONTA-116): a luta com outro rival ou outro mapa não é a luta pedida. NULL
     no rival: a semente é de antes da regra, e nada se confere */
  `
  ALTER TABLE sementes ADD COLUMN rival_pedido TEXT;
  ALTER TABLE sementes ADD COLUMN mapa_pedido TEXT;
  `,
  /* 6: o desafio do dia (MMO6, servidor_web/src/desafio/): o segredo de cada dia (do servidor, não da conta: publicado quando o dia
     congela); a tentativa de cada conta em cada dia (uma só), com o que ela prometeu antes de cada semente (a escolha e as trocas) e o
     resultado conferido; as sementes das lutas entregues; a linha de cada envio conferido; e as tabelas congeladas com o selo do Top do
     dia (MMO-11). Tudo o que é da conta pende dela: apagar a conta leva tudo */
  `
  CREATE TABLE segredos_dia (
    dia           TEXT PRIMARY KEY,
    segredo       TEXT NOT NULL,
    criado_em     INTEGER NOT NULL,
    publicado_em  INTEGER
  ) STRICT;
  CREATE TABLE desafios (
    conta_id     TEXT NOT NULL REFERENCES contas(id) ON DELETE CASCADE,
    dia          TEXT NOT NULL,
    comecou_em   INTEGER NOT NULL,
    versao       INTEGER NOT NULL,
    escolha      INTEGER,
    trocas       TEXT NOT NULL DEFAULT '[]',
    vitorias     INTEGER,
    series       INTEGER,
    lutas        INTEGER,
    acabou       INTEGER,
    vida_ultima  INTEGER,
    terminou_em  INTEGER,
    envio_id     TEXT,
    PRIMARY KEY (conta_id, dia),
    CHECK ((vitorias IS NULL) = (envio_id IS NULL))
  ) STRICT;
  CREATE INDEX desafios_dia ON desafios(dia);
  CREATE TABLE desafio_lutas (
    conta_id  TEXT NOT NULL,
    dia       TEXT NOT NULL,
    k         INTEGER NOT NULL,
    semente   INTEGER NOT NULL,
    hora      INTEGER NOT NULL,
    escolha   INTEGER NOT NULL,
    trocas    TEXT NOT NULL,
    PRIMARY KEY (conta_id, dia, k),
    FOREIGN KEY (conta_id, dia) REFERENCES desafios(conta_id, dia) ON DELETE CASCADE
  ) STRICT;
  CREATE TABLE desafio_envios (
    id             TEXT PRIMARY KEY,
    conta_id       TEXT NOT NULL REFERENCES contas(id) ON DELETE CASCADE,
    dia            TEXT NOT NULL,
    recebido_em    INTEGER NOT NULL,
    hash_registro  TEXT NOT NULL,
    resultado      TEXT NOT NULL CHECK (resultado IN ('aceito', 'recusado')),
    motivo         TEXT,
    detalhe        TEXT,
    vitorias       INTEGER,
    lutas          INTEGER NOT NULL,
    ms_conferencia REAL NOT NULL,
    CHECK ((resultado = 'aceito') = (motivo IS NULL AND vitorias IS NOT NULL))
  ) STRICT;
  CREATE INDEX desafio_envios_conta ON desafio_envios(conta_id, dia);
  CREATE TABLE tabelas_dia (
    dia          TEXT NOT NULL,
    posicao      INTEGER NOT NULL,
    conta_id     TEXT NOT NULL REFERENCES contas(id) ON DELETE CASCADE,
    vitorias     INTEGER NOT NULL,
    vida_ultima  INTEGER NOT NULL,
    terminou_em  INTEGER NOT NULL,
    selo         INTEGER NOT NULL CHECK (selo IN (0, 1)),
    PRIMARY KEY (dia, posicao)
  ) STRICT;
  CREATE INDEX tabelas_dia_conta ON tabelas_dia(conta_id);
  `,
  /* 7: o mural (MMO7, servidor_web/src/premios/): o recorde de todos os tempos de cada conta na Torre, na Fábrica e no Salão, só do que a
     conferência de um envio aceito refez (visto_em: a hora do servidor em que o valor foi visto pela primeira vez, o desempate do mural);
     e as lutas do Salão que o replay de cada pet refez, para juntar a tentativa do Tamer, que tem um pet por estágio. Os títulos, os
     selos e os enfeites não têm tabela: saem das tabelas congeladas da semana e do dia. Tudo pende da conta */
  `
  CREATE TABLE recordes (
    conta_id  TEXT NOT NULL REFERENCES contas(id) ON DELETE CASCADE,
    inst      TEXT NOT NULL CHECK (inst IN ('torre', 'fabrica', 'salao')),
    valor     INTEGER NOT NULL CHECK (valor >= 1),
    visto_em  INTEGER NOT NULL,
    envio_id  TEXT NOT NULL,
    PRIMARY KEY (conta_id, inst)
  ) STRICT;
  CREATE INDEX recordes_inst ON recordes(inst, valor DESC, visto_em);
  CREATE TABLE salao_vistas (
    conta_id  TEXT NOT NULL REFERENCES contas(id) ON DELETE CASCADE,
    pet       INTEGER NOT NULL,
    semente   INTEGER NOT NULL,
    venceu    INTEGER NOT NULL CHECK (venceu IN (0, 1)),
    PRIMARY KEY (conta_id, pet, semente)
  ) STRICT;
  `,
  /* 8: as duas pontuações e o reset (MMO8, servidor_web/src/premios/rankings.ts): o máximo histórico dos Digimon (uma linha por pet, pelo
     total da vida que a conferência refez; pontos_em: a hora do servidor em que o total chegou ao valor de hoje, o desempate; aposentado_em:
     o envio que conferiu o reset dele); os resets conferidos (o nível refeito do registro final do pet); e os feitos do Tamer que o servidor
     viu no replay do pet que os fez (a 1ª medalha de cada líder, "medalha:<id>", e o título da Liga, "liga"). Tudo pende da conta */
  `
  CREATE TABLE digimons (
    conta_id       TEXT NOT NULL REFERENCES contas(id) ON DELETE CASCADE,
    pet            INTEGER NOT NULL,
    versao_pet     INTEGER NOT NULL,
    pontos         REAL NOT NULL CHECK (pontos >= 0),
    estagio        TEXT NOT NULL,
    forma          TEXT NOT NULL,
    pontos_em      INTEGER NOT NULL,
    aposentado_em  INTEGER,
    envio_id       TEXT NOT NULL,
    PRIMARY KEY (conta_id, pet, versao_pet)
  ) STRICT;
  CREATE INDEX digimons_pontos ON digimons(pontos DESC, pontos_em);
  CREATE TABLE resets (
    conta_id  TEXT NOT NULL REFERENCES contas(id) ON DELETE CASCADE,
    pet       INTEGER NOT NULL,
    nivel     INTEGER NOT NULL CHECK (nivel BETWEEN 0 AND 3),
    hash      TEXT NOT NULL,
    por       TEXT NOT NULL CHECK (por IN ('reset', 'cruzamento')),
    visto_em  INTEGER NOT NULL,
    envio_id  TEXT NOT NULL,
    PRIMARY KEY (conta_id, pet)
  ) STRICT;
  CREATE TABLE feitos_tamer (
    conta_id  TEXT NOT NULL REFERENCES contas(id) ON DELETE CASCADE,
    feito     TEXT NOT NULL,
    pet       INTEGER NOT NULL,
    visto_em  INTEGER NOT NULL,
    envio_id  TEXT NOT NULL,
    PRIMARY KEY (conta_id, feito)
  ) STRICT;
  `,
  /* 9: o save na nuvem (CN3, servidor_web/src/nuvem/): o pacote da conta (o save do pet do jogador, um por conta como no aparelho, e as
     outras chaves da CN0), com a posição confirmada (eventos e hash), o resumo (a forma e o tick, do replay) e a vez (o aparelho, desde,
     até); as divergências (a outra história inteira, até a escolha); as cópias de 30 dias (a diária e as que guardam o que saiu do lugar);
     e as histórias não escolhidas, que ficam em Gerações só para ver. O registro fica aqui, em texto, até o armazenamento de objetos da
     CN5 (D-CONTA-180). Tudo pende da conta; a vez solta quando o aparelho é desconectado */
  `
  CREATE TABLE nuvem_pets (
    conta_id       TEXT PRIMARY KEY REFERENCES contas(id) ON DELETE CASCADE,
    semente        INTEGER NOT NULL,
    versao         INTEGER NOT NULL,
    grupo          INTEGER NOT NULL CHECK (grupo IN (0, 1)),
    foco           TEXT,
    log            TEXT NOT NULL,
    eventos        INTEGER NOT NULL,
    hash           TEXT NOT NULL,
    firme          INTEGER NOT NULL,
    hash_firme     TEXT NOT NULL,
    extras         TEXT NOT NULL,
    extras_hash    TEXT NOT NULL,
    forma          TEXT NOT NULL,
    tick           INTEGER NOT NULL,
    atualizado_em  INTEGER NOT NULL,
    atualizado_por TEXT,
    vez_aparelho   TEXT REFERENCES aparelhos(id) ON DELETE SET NULL,
    vez_desde      INTEGER,
    vez_ate        INTEGER
  ) STRICT;
  CREATE TABLE nuvem_divergencias (
    id             TEXT PRIMARY KEY,
    conta_id       TEXT NOT NULL REFERENCES contas(id) ON DELETE CASCADE,
    criada_em      INTEGER NOT NULL,
    aparelho_nome  TEXT NOT NULL,
    save           TEXT NOT NULL,
    extras         TEXT NOT NULL,
    comum          INTEGER NOT NULL,
    lados          TEXT NOT NULL,
    resolvida_em   INTEGER,
    fica           TEXT CHECK (fica IN ('nuvem', 'outra')),
    CHECK ((resolvida_em IS NULL) = (fica IS NULL))
  ) STRICT;
  CREATE INDEX nuvem_divergencias_conta ON nuvem_divergencias(conta_id, resolvida_em);
  CREATE TABLE nuvem_copias (
    id         TEXT PRIMARY KEY,
    conta_id   TEXT NOT NULL REFERENCES contas(id) ON DELETE CASCADE,
    feita_em   INTEGER NOT NULL,
    dia        TEXT NOT NULL,
    motivo     TEXT NOT NULL CHECK (motivo IN ('diaria', 'nao_escolhido', 'troca', 'antes_de_restaurar', 'historia', 'durante_divergencia')),
    save       TEXT NOT NULL,
    extras     TEXT NOT NULL,
    eventos    INTEGER NOT NULL,
    forma      TEXT NOT NULL,
    tick       INTEGER NOT NULL,
    apagar_em  INTEGER NOT NULL
  ) STRICT;
  CREATE INDEX nuvem_copias_conta ON nuvem_copias(conta_id, feita_em);
  CREATE INDEX nuvem_copias_apagar ON nuvem_copias(apagar_em);
  CREATE TABLE nuvem_historias (
    id              TEXT PRIMARY KEY,
    conta_id        TEXT NOT NULL REFERENCES contas(id) ON DELETE CASCADE,
    criada_em       INTEGER NOT NULL,
    aparelho_nome   TEXT NOT NULL,
    divergencia_id  TEXT NOT NULL,
    save            TEXT NOT NULL,
    extras          TEXT NOT NULL,
    eventos         INTEGER NOT NULL,
    forma           TEXT NOT NULL,
    tick            INTEGER NOT NULL
  ) STRICT;
  CREATE INDEX nuvem_historias_conta ON nuvem_historias(conta_id, criada_em);
  `,
  /* 10: a cota da fala (CN4, servidor_web/src/protecao/cota.ts): quantas falas pela LLM a conta usou em cada dia de Brasília. Só o número,
     nunca o texto (a fala não se guarda, seção 9 do plano). Pende da conta */
  `
  CREATE TABLE cota_fala (
    conta_id  TEXT NOT NULL REFERENCES contas(id) ON DELETE CASCADE,
    dia       TEXT NOT NULL,
    usadas    INTEGER NOT NULL CHECK (usadas >= 0),
    PRIMARY KEY (conta_id, dia)
  ) STRICT;
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
