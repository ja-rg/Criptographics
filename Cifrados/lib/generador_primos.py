# archivo: primos_ndigitos.py
from random import Random
from typing import Optional, Tuple

def _es_probablemente_primo(n: int, rondas: int, rng: Random) -> bool:
    if n < 2:
        return False
    pequeños = [2,3,5,7,11,13,17,19,23,29]
    if n in pequeños:
        return True
    if any(n % p == 0 for p in pequeños):
        return False
    d = n - 1; s = 0
    while d % 2 == 0:
        d //= 2; s += 1
    for _ in range(rondas):
        a = rng.randrange(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for __ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def primo_ndigitos(n_digitos: int, semilla: Optional[int] = None, rondas_mr: int = 16) -> int:
    if n_digitos < 1:
        raise ValueError("n_digitos debe ser ≥ 1")
    rng = Random(semilla)
    bajo = 10 ** (n_digitos - 1)
    alto = 10 ** n_digitos - 1
    while True:
        candidato = rng.randrange(bajo | 1, alto + 1, 2)  # impar
        while candidato <= alto:
            if _es_probablemente_primo(candidato, rondas_mr, rng):
                return candidato
            candidato += 2

def primos_distintos_ndigitos(n_digitos: int, semilla: Optional[int] = None,
                              rondas_mr: int = 16) -> Tuple[int, int]:
    """
    Devuelve (p, q) primos distintos con exactamente n_digitos.
    Usa una semilla base para reproducibilidad determinista.
    """
    base_rng = Random(semilla)
    seed_p = base_rng.getrandbits(64)
    seed_q = base_rng.getrandbits(64)

    p = primo_ndigitos(n_digitos, semilla=seed_p, rondas_mr=rondas_mr)
    q = primo_ndigitos(n_digitos, semilla=seed_q, rondas_mr=rondas_mr)

    # reintenta hasta que q != p (cambia la semilla del segundo)
    while q == p:
        seed_q = base_rng.getrandbits(64)
        q = primo_ndigitos(n_digitos, semilla=seed_q, rondas_mr=rondas_mr)
    return p, q
