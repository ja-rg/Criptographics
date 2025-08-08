# Método de Hill (2×2 y 3×3) — paso a paso con "mini sustitución"
# Alfabeto con Ñ: A=0, B=1, ..., N=13, Ñ=14, O=15, ..., Z=26  → MOD = 27
# Mensajes se empaquetan como matriz n×c (n=2 o 3). Padding con 0 (letra 'A').

from typing import List, Tuple
from math import gcd

ALFABETO = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"  # 27 símbolos
MOD = len(ALFABETO)  # 27
MAP = {ch: i for i, ch in enumerate(ALFABETO)}

# === Utilidades de texto ===
def normalizar_texto(t: str) -> str:
    t = t.upper().replace("Ñ", "Ñ")  # asegurar mayúscula; se preserva la Ñ
    # filtrar solo letras del alfabeto definido
    return "".join(c for c in t if c in ALFABETO)

def letras_a_numeros(t: str) -> List[int]:
    return [MAP[c] for c in t]

def numeros_a_letras(nums: List[int]) -> str:
    return "".join(ALFABETO[n % MOD] for n in nums)

# === Utilidades de matrices modulares ===
def mod_inv(a: int, m: int) -> int:
    a %= m
    # inverso modular por búsqueda (m es pequeño: 27)
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    raise ValueError("No existe inverso modular (no coprimo)")

def det2(K: List[List[int]]) -> int:
    return (K[0][0]*K[1][1] - K[0][1]*K[1][0]) % MOD

def adj2(K: List[List[int]]) -> List[List[int]]:
    return [[ K[1][1] % MOD, (-K[0][1]) % MOD],
            [(-K[1][0]) % MOD,  K[0][0] % MOD]]

def det3(K: List[List[int]]) -> int:
    a,b,c = K[0]
    d,e,f = K[1]
    g,h,i = K[2]
    return (a*(e*i - f*h) - b*(d*i - f*g) + c*(d*h - e*g)) % MOD

def adj3(K: List[List[int]]) -> List[List[int]]:
    a,b,c = K[0]
    d,e,f = K[1]
    g,h,i = K[2]
    C00 =  (e*i - f*h)
    C01 = -(d*i - f*g)
    C02 =  (d*h - e*g)
    C10 = -(b*i - c*h)
    C11 =  (a*i - c*g)
    C12 = -(a*h - b*g)
    C20 =  (b*f - c*e)
    C21 = -(a*f - c*d)
    C22 =  (a*e - b*d)
    # adj = cofactores transpuestos
    return [[C00 % MOD, C10 % MOD, C20 % MOD],
            [C01 % MOD, C11 % MOD, C21 % MOD],
            [C02 % MOD, C12 % MOD, C22 % MOD]]

def inv_matriz(K: List[List[int]]) -> List[List[int]]:
    n = len(K)
    if any(len(row) != n for row in K):
        raise ValueError("K debe ser cuadrada")
    if n == 2:
        d = det2(K)
        if gcd(d, MOD) != 1:
            raise ValueError("K no invertible mod 27 (det no coprimo)")
        d_inv = mod_inv(d, MOD)
        A = adj2(K)
        return [[(d_inv*A[i][j]) % MOD for j in range(2)] for i in range(2)]
    elif n == 3:
        d = det3(K)
        if gcd(d, MOD) != 1:
            raise ValueError("K no invertible mod 27 (det no coprimo)")
        d_inv = mod_inv(d, MOD)
        A = adj3(K)
        return [[(d_inv*A[i][j]) % MOD for j in range(3)] for i in range(3)]
    else:
        raise ValueError("Solo se admite 2×2 o 3×3 en esta demo")

def mat_mul(A: List[List[int]], B: List[List[int]]) -> List[List[int]]:
    # A: (n×n), B: (n×c)
    n = len(A)
    c = len(B[0])
    out = [[0]*c for _ in range(n)]
    for i in range(n):
        for j in range(c):
            s = 0
            for k in range(n):
                s += A[i][k] * B[k][j]
            out[i][j] = s % MOD
    return out

def vector_a_matriz(vec: List[int], n: int) -> List[List[int]]:
    # Rellena con 0 (padding) hasta múltiplo de n y forma matriz n×c por columnas
    v = vec[:]
    resto = len(v) % n
    if resto:
        v.extend([0]*(n - resto))  # padding con 0 ('A')
    c = len(v)//n
    M = [[0]*c for _ in range(n)]
    idx = 0
    for j in range(c):
        for i in range(n):
            M[i][j] = v[idx]
            idx += 1
    return M

def matriz_a_vector(M: List[List[int]]) -> List[int]:
    # aplana por columnas
    n, c = len(M), len(M[0])
    out = []
    for j in range(c):
        for i in range(n):
            out.append(M[i][j] % MOD)
    return out

# === Cifrado / Descifrado con "mini sustitución" ===
def cifrar_hill(K: List[List[int]], mensaje: str) -> str:
    n = len(K)
    print(f"1) CIFRADO — usar bloques de tamaño n={n} con padding 0 (A). MOD={MOD}")
    limpio = normalizar_texto(mensaje)
    v = letras_a_numeros(limpio)
    P = vector_a_matriz(v, n)
    print(f"   Texto limpio: '{limpio}' → {v}")
    print(f"   Matriz del mensaje P (n×c): {n}×{len(P[0])}")
    # Mini sustitución sobre la primera columna
    if len(P[0]) > 0:
        col0 = [P[i][0] for i in range(n)]
        print("   (Mini sustitución) c₀ = K * p₀ mod", MOD)
        print(f"                     p₀ = {tuple(col0)}")
    C = mat_mul(K, P)
    if len(P[0]) > 0:
        colC0 = [C[i][0] for i in range(n)]
        print(f"                     c₀ = {tuple(colC0)}")
    cif_nums = matriz_a_vector(C)
    cif = numeros_a_letras(cif_nums)
    print(f"   Resultado cifrado → {cif_nums} → '{cif}'")
    return cif

def descifrar_hill(K: List[List[int]], cifrado: str) -> str:
    n = len(K)
    print(f"2) DESCIFRADO — calcular K^(-1) mod {MOD} y aplicar a columnas")
    Kinv = inv_matriz(K)
    nums = letras_a_numeros(normalizar_texto(cifrado))
    C = vector_a_matriz(nums, n)
    # Mini sustitución sobre la primera columna
    if len(C[0]) > 0:
        col0 = [C[i][0] for i in range(n)]
        print("   (Mini sustitución) p₀ = K^{-1} * c₀ mod", MOD)
        print(f"                     c₀ = {tuple(col0)}")
    P = mat_mul(Kinv, C)
    if len(C[0]) > 0:
        colP0 = [P[i][0] for i in range(n)]
        print(f"                     p₀ = {tuple(colP0)}")
    dec_nums = matriz_a_vector(P)
    dec = numeros_a_letras(dec_nums)
    print(f"   Resultado descifrado → {dec_nums} → '{dec}'")
    return dec

# === Demo breve ===
if __name__ == "__main__":
    print("=== Hill n×n (n=2 o 3) con Ñ, padding 0 y mini sustitución ===")
    # Ejemplo 3×3 con det=1 (invertible mod 27)
    K3 = [
        [1, 2, 3],
        [0, 1, 4],
        [0, 0, 1],
    ]
    mensaje = "CRIPTOCON Ñ Y HILL"
    C = cifrar_hill(K3, mensaje)
    P = descifrar_hill(K3, C)
    print("3) Verificación final:")
    print(f"   Mensaje original = '{normalizar_texto(mensaje)}'")
    print(f"   Cifrado          = '{C}'")
    print(f"   Descifrado       = '{P}'")
    print("   ¿Coinciden? ->", "SÍ ✅" if normalizar_texto(mensaje) == P[:len(normalizar_texto(mensaje))] else "NO ❌")
