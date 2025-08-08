# archivo: primos_ndigitos.py
from random import Random
from typing import Optional

def _es_probablemente_primo(n: int, rondas: int, rng: Random) -> bool:
    """Test de primalidad Miller–Rabin (probabilístico)."""
    if n < 2:
        return False
    # casos pequeños
    pequeños = [2,3,5,7,11,13,17,19,23,29]
    if n in pequeños:
        return True
    if any(n % p == 0 for p in pequeños):
        return False

    # escribir n-1 = d * 2^s con d impar
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    for _ in range(rondas):
        a = rng.randrange(2, n - 2)  # 2 ≤ a ≤ n-2
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
    """
    Genera un número primo con exactamente n_digitos usando una semilla reproducible.
    - n_digitos: cantidad de dígitos decimales (≥1).
    - semilla: entero para Random(); None => no determinista.
    - rondas_mr: rondas de Miller–Rabin (16 es seguro para uso académico).
    """
    if n_digitos < 1:
        raise ValueError("n_digitos debe ser ≥ 1")

    rng = Random(semilla)
    bajo = 10 ** (n_digitos - 1)
    alto = 10 ** n_digitos - 1

    if bajo <= 2 <= alto:
        return 2 if n_digitos == 1 else 3  # atajo trivial para 1 dígito

    # generar candidatos impares dentro del rango
    while True:
        candidato = rng.randrange(bajo, alto + 1)
        # forzar impar y n_digitos exactos
        if candidato % 2 == 0:
            candidato += 1
        if candidato > alto:
            candidato = bajo | 1  # menor impar en el rango
        # probar hasta hallar primo
        while candidato <= alto:
            if _es_probablemente_primo(candidato, rondas_mr, rng):
                return candidato
            candidato += 2
        # si llegamos al final, reempezar desde el primer impar
        # (el bucle externo asegura que no quedemos atrapados)


if __name__ == "__main__":
    # Ejemplo de uso
    primo = primo_ndigitos(5, semilla=42)
    print("Número primo de 5 dígitos:", primo)
    