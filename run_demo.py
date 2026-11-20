"""Demo do v0: dois donos, mesmo motor, 14 dias.

O ponto desta demo NAO e mostrar que os pets ficam diferentes. E mostrar
COMO eles ficam diferentes no v0: so pelo estado acumulado, nunca pela
politica. A politica e identica nos dois, porque no v0 ninguem aprende.

Esse e o numero que o v1 tem que bater.
"""

from __future__ import annotations

import random
from collections import Counter

from digilab import AcaoUsuario, Motor


def dono_atencioso(motor: Motor, rng: random.Random, dias: int) -> None:
    for _ in range(dias * 24):
        motor.avancar(60)
        if rng.random() < 0.55:
            motor.observar(
                rng.choices(
                    [
                        AcaoUsuario.ALIMENTAR,
                        AcaoUsuario.LIMPAR,
                        AcaoUsuario.BRINCAR,
                        AcaoUsuario.ACARICIAR,
                        AcaoUsuario.ELOGIAR,
                    ],
                    weights=[3, 3, 3, 2, 2],
                )[0]
            )


def dono_relapso(motor: Motor, rng: random.Random, dias: int) -> None:
    for _ in range(dias * 24):
        motor.avancar(60)
        if rng.random() < 0.12:
            motor.observar(
                rng.choices(
                    [AcaoUsuario.ALIMENTAR, AcaoUsuario.REPREENDER],
                    weights=[4, 1],
                )[0]
            )


def resumo(nome: str, motor: Motor) -> None:
    e = motor.estado()
    contagem = Counter(a.value for _, a in motor.acoes_recentes(10_000))
    total = sum(contagem.values()) or 1
    principais = ", ".join(
        f"{acao} {100 * n / total:.0f}%" for acao, n in contagem.most_common(3)
    )
    print(f"\n{nome}")
    print(f"  saude {e['saude']:.2f} | humor {e['humor']:.2f} | fome {e['fome']:.2f}")
    print(f"  cuidados recebidos: {e['total_cuidados']} | eventos no log: {len(motor.log)}")
    print(f"  comportamento: {principais}")


def main() -> None:
    dias = 14

    atencioso = Motor(semente=42)
    dono_atencioso(atencioso, random.Random(1), dias)
    resumo("Dono atencioso", atencioso)

    relapso = Motor(semente=42)
    dono_relapso(relapso, random.Random(1), dias)
    resumo("Dono relapso", relapso)

    # Prova de reprodutibilidade, rodando de verdade.
    from digilab import reproduzir

    igual = reproduzir(atencioso.log, semente=42).estado() == atencioso.estado()
    print(f"\nreplay bate com o original: {igual}")


if __name__ == "__main__":
    main()
