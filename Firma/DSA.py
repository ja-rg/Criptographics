# DSA paso a paso con "mini sustitución" y nombres descriptivos
from random import Random
from math import gcd
import hashlib

# ---------- utilidades ----------
def inverso_modular(a, m):
    """x tal que a*x ≡ 1 (mod m)."""
    try:
        return pow(a, -1, m)
    except TypeError:
        def egcd(x, y):
            return (x, 1, 0) if y == 0 else (lambda g, u, v: (g, v, u - (x // y) * v))(*egcd(y, x % y))
        g, u, _ = egcd(a, m)
        assert g == 1, "No hay inverso"
        return u % m

def _miller_rabin(n, k, rng):
    if n < 2:
            return False
    # Divisores pequeños
    pequeños = [2,3,5,7,11,13,17,19,23,29]
    if n in pequeños:
        return True
    if any(n % p == 0 for p in pequeños):
        return False
    # n-1 = d*2^s
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for _ in range(k):
        a = rng.randrange(2, n - 2)
        x = pow(a, d, n)
        if x in (1, n - 1): 
            continue
        for __ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def _primo_de_ndigitos(n_digitos, rng, rondas=16):
    bajo = 10**(n_digitos - 1)
    alto = 10**n_digitos - 1
    if bajo <= 2 <= alto: 
        if n_digitos == 1:
            return 2
    while True:
        n = rng.randrange(bajo | 1, alto + 1, 2)
        if _miller_rabin(n, rondas, rng):
            return n

# ---------- parámetros DSA (q | p-1) ----------
def generar_parametros_dsa(n_digitos_q=3, semilla=2025, rondas=16):
    """
    Genera (p, q, g) con q primo pequeño (n_digitos_q) y p primo tal que q | p-1.
    Para examen: tamaños pequeños y rápidos de escribir.
    """
    rng = Random(semilla)
    print("1) Elegir q primo pequeño.")
    q = _primo_de_ndigitos(n_digitos_q, rng, rondas)
    print(f"   q = {q}")

    print("2) Buscar p primo tal que p ≡ 1 (mod q).")
    # Intenta p = t*q + 1 hasta que sea primo.
    while True:
        t = rng.randrange(2, 10_000)  # rango modesto para examen
        p = t * q + 1
        if _miller_rabin(p, rondas, rng):
            print(f"   p = {t}*{q} + 1 = {p}  (primo)")
            break

    print("3) Calcular generador g = h^{(p-1)/q} mod p con g>1.")
    # Elegir h aleatorio, construir g = h^((p-1)/q) mod p
    exp = (p - 1) // q
    while True:
        h = rng.randrange(2, p - 1)
        g = pow(h, exp, p)
        if g > 1:
            print(f"   h = {h}")
            print(f"   g = h^{exp} mod {p} = {g}")
            break

    print(f"   Parámetros: p={p}, q={q}, g={g}\n")
    return p, q, g

# ---------- claves ----------
def generar_claves_dsa(p, q, g, semilla=2025):
    rng = Random(semilla ^ 0xA5A5)
    print("4) Elegir clave privada x ∈ [1, q-1] y pública y = g^x mod p.")
    x_priv = rng.randrange(1, q)  # 1..q-1
    y_pub = pow(g, x_priv, p)
    print(f"   x = {x_priv} (SECRETO)")
    print(f"   y = g^x mod p = {g}^{x_priv} mod {p} = {y_pub}\n")
    return (p, q, g, y_pub), x_priv

# ---------- hash ----------
def hash_entero(m_bytes: bytes) -> int:
    """Hash SHA-1 → entero (DSA clásico)."""
    return int.from_bytes(hashlib.sha1(m_bytes).digest(), 'big')

# ---------- firma ----------
def firmar_dsa(params_pub, x_priv, mensaje_bytes: bytes, semilla=777):
    p, q, g, y = params_pub
    rng = Random(semilla)
    h = hash_entero(mensaje_bytes) % q
    print("5) FIRMA DSA de H(m) (m se firma vía hash).")
    print(f"   H(m) mod q = {h}")

    while True:
        k_efimero = rng.randrange(1, q)  # 1..q-1
        if gcd(k_efimero, q) != 1:
            continue
        r = pow(g, k_efimero, p) % q
        if r == 0:
            continue
        k_inv = inverso_modular(k_efimero, q)
        s = (k_inv * (h + x_priv * r)) % q
        if s == 0:
            continue

        # Mini sustitución
        print(f"   k = {k_efimero}  →  r = (g^k mod p) mod q = ({g}^{k_efimero} mod {p}) mod {q} = {r}")
        print(f"   k^(-1) mod q = inv({k_efimero}, {q}) = {k_inv}")
        print("   (Mini sustitución) s = k^{-1} * (H(m) + x*r) mod q")
        print(f"                     s = {k_inv} * ({h} + {x_priv}*{r}) mod {q} = {s}\n")
        return (r, s)

# ---------- verificación ----------
def verificar_dsa(params_pub, mensaje_bytes: bytes, firma):
    p, q, g, y = params_pub
    r, s = firma
    if not (0 < r < q and 0 < s < q):
        print("Firma fuera de rango ❌")
        return False

    h = hash_entero(mensaje_bytes) % q
    print("6) VERIFICACIÓN DSA.")
    print(f"   H(m) mod q = {h}")
    w = inverso_modular(s, q)
    u1 = (h * w) % q
    u2 = (r * w) % q
    v = (pow(g, u1, p) * pow(y, u2, p) % p) % q

    # Mini sustitución
    print(f"   w = s^{-1} mod q = inv({s}, {q}) = {w}")
    print(f"   u1 = H(m)*w mod q = {h}*{w} mod {q} = {u1}")
    print(f"   u2 = r*w   mod q = {r}*{w} mod {q} = {u2}")
    print("   (Mini sustitución) v = (g^{u1} * y^{u2} mod p) mod q")
    print(f"                     v = ({g}^{u1} * {y}^{u2} mod {p}) mod {q} = {v}")
    print(f"   ¿v == r?  →  {v} == {r}  →  {'SÍ ✅' if v == r else 'NO ❌'}\n")
    return v == r

# ---------- demo breve ----------
if __name__ == "__main__":
    print("=== DSA paso a paso (con mini sustitución) ===")
    # Parámetros pequeños para examen (rápidos de escribir/entender)
    p, q, g = generar_parametros_dsa(n_digitos_q=3, semilla=2025)
    params_pub, x_priv = generar_claves_dsa(p, q, g, semilla=2025)

    mensaje = b"Prueba DSA"
    firma = firmar_dsa(params_pub, x_priv, mensaje, semilla=4242)
    es_valida = verificar_dsa(params_pub, mensaje, firma)

    print("7) Resumen:")
    print(f"   p = {p}\n   q = {q}\n   g = {g}\n   y = {params_pub[3]}\n   x = {x_priv} (secreto)")
    print(f"   Firma (r, s) = {firma}")
    print(f"   Verificación = {'VÁLIDA ✅' if es_valida else 'INVÁLIDA ❌'}")
