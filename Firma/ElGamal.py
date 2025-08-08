# ElGamal firma paso x paso con "mini sustitución" y nombres descriptivos
from random import Random, randrange
from math import gcd

from lib.generador_primos import primo_ndigitos

# --- utilidades ---
def inverso_modular(valor, modulo_n):
    """Devuelve x tal que valor*x ≡ 1 (mod modulo_n). Requiere gcd(valor, modulo_n) = 1."""
    try:
        return pow(valor, -1, modulo_n)  # Python 3.8+
    except TypeError:
        # Euclides extendido
        def egcd(a, b):
            return (a, 1, 0) if b == 0 else (lambda g, x, y: (g, y, x - (a // b) * y))(*egcd(b, a % b))
        g, x, _ = egcd(valor, modulo_n)
        assert g == 1, "No hay inverso (no coprimos)"
        return x % modulo_n

# --- generación de claves (igual que para cifrado ElGamal) ---
def generar_claves(primo_modulo_p, generador_g):
    print("1) Parámetros del grupo: primo p y generador g.")
    print(f"   p = {primo_modulo_p}, g = {generador_g}")
    exponente_privado_x = randrange(1, primo_modulo_p - 1)
    print("2) Elegir exponente privado x ∈ [1, p-2].")
    print(f"   x = {exponente_privado_x}  (SECRETO)")
    componente_publica_y = pow(generador_g, exponente_privado_x, primo_modulo_p)
    print("3) Calcular y = g^x mod p (parte pública).")
    print(f"   y = {generador_g}^{exponente_privado_x} mod {primo_modulo_p} = {componente_publica_y}")
    print(f"   Clave pública: (p,g,y) = ({primo_modulo_p},{generador_g},{componente_publica_y}). Clave privada: x = {exponente_privado_x}.")
    return (primo_modulo_p, generador_g, componente_publica_y), exponente_privado_x

# --- firma ---
def firmar_mensaje(clave_publica, exponente_privado_x, hash_mensaje_h):
    """
    Firma ElGamal sobre Z_p* (texto: h). Asume 0 < h < p.
    Fórmulas:
      r = g^k mod p, con k ∈ [1, p-2], gcd(k, p-1)=1 y r ≠ 0
      s = k^{-1} * (h - x*r) mod (p-1)
    Firma: (r, s)
    """
    primo_modulo_p, generador_g, componente_publica_y = clave_publica

    print("4) FIRMA del hash del mensaje h (0 < h < p).")
    print(f"   h = {hash_mensaje_h}")

    # Elegir k válido: 1 ≤ k ≤ p-2, gcd(k, p-1) = 1, r != 0
    while True:
        k_efimero = randrange(1, primo_modulo_p - 1)
        if gcd(k_efimero, primo_modulo_p - 1) != 1:
            continue
        r = pow(generador_g, k_efimero, primo_modulo_p)
        if r == 0:
            continue
        break

    print("   Elegir k efímero tal que gcd(k, p-1)=1 y r≠0.")
    print(f"   k = {k_efimero}")
    print(f"   r = g^k mod p = {generador_g}^{k_efimero} mod {primo_modulo_p} = {r}")

    inverso_k = inverso_modular(k_efimero, primo_modulo_p - 1)
    print(f"   k^(-1) mod (p-1) = inv({k_efimero}, {primo_modulo_p - 1}) = {inverso_k}")

    # --- MINI SUSTITUCIÓN para s ---
    print("   (Mini sustitución) s = k^(-1) * (h - x*r) mod (p-1)")
    print(f"                      s = {inverso_k} * ({hash_mensaje_h} - {exponente_privado_x}*{r}) mod {primo_modulo_p - 1}")

    s = (inverso_k * (hash_mensaje_h - exponente_privado_x * r)) % (primo_modulo_p - 1)
    print(f"   Resultado: s = {s}")

    print(f"   Firma: (r, s) = ({r}, {s})\n")
    return (r, s)

# --- verificación ---
def verificar_firma(clave_publica, hash_mensaje_h, firma):
    primo_modulo_p, generador_g, componente_publica_y = clave_publica
    r, s = firma

    print("5) VERIFICACIÓN de la firma (r,s).")
    print(f"   Recibido (h, r, s) = ({hash_mensaje_h}, {r}, {s})")
    assert 0 < r < primo_modulo_p, "r fuera de rango"

    # LHS: g^h mod p
    izquierda = pow(generador_g, hash_mensaje_h, primo_modulo_p)

    # RHS: y^r * r^s mod p
    derecha = (pow(componente_publica_y, r, primo_modulo_p) * pow(r, s, primo_modulo_p)) % primo_modulo_p

    # --- MINI SUSTITUCIÓN de la igualdad ---
    print("   Comprobación: g^h ≟ y^r · r^s (mod p)")
    print(f"                 {generador_g}^{hash_mensaje_h} mod {primo_modulo_p} ≟ {componente_publica_y}^{r} · {r}^{s} mod {primo_modulo_p}")
    print(f"   Lado izquierdo = {izquierda}")
    print(f"   Lado derecho   = {derecha}")

    es_valida = izquierda == derecha
    print("   ¿Firma válida? ->", "SÍ ✅" if es_valida else "NO ❌", "\n")
    return es_valida

# --- propuesta g (idéntica a la versión de cifrado) ---
def proponer_generador_aleatorio(primo_p, semilla=None):
    """Proponer un generador aleatorio g para el grupo multiplicativo Z/pZ."""
    rng = Random(semilla)
    while True:
        g = rng.randrange(2, primo_p)
        # Comprobación rápida para p primo seguro no garantizada; para demo basta probar que no sea de orden 2
        if pow(g, (primo_p - 1) // 2, primo_p) != 1:
            return g
        continue

# --- hash simplificado para demo ---
def hash_simplificado_a_entero(mensaje: str, primo_modulo_p: int) -> int:
    """Hash muy simple para demo: suma de códigos + longitud, reducido mod p-1 y luego desplazado a (0, p-1)."""
    h = sum(ord(c) for c in mensaje) + len(mensaje)
    # En muchas definiciones, h se toma mod (p-1) para trabajar en el exponente
    return (h % (primo_modulo_p - 1)) or 1  # Evitar 0

# --- demo breve ---
if __name__ == "__main__":
    print("=== ElGamal firma paso x paso (con mini sustitución) ===")
    # Primo pequeño y generador para demo de examen
    primo_p = primo_ndigitos(4, semilla=2026)
    generador_g = proponer_generador_aleatorio(primo_p, semilla=2026)

    clave_publica, exponente_privado_x = generar_claves(primo_p, generador_g)

    mensaje = "Hola, examen de cripto"
    h = hash_simplificado_a_entero(mensaje, primo_p)

    firma = firmar_mensaje(clave_publica, exponente_privado_x, h)

    print("6) Verificación final:")
    ok = verificar_firma(clave_publica, h, firma)

    print(f"   Mensaje (para hash) = '{mensaje}'")
    print(f"   h = {h}")
    print(f"   Firma (r,s) = {firma}")
    print("   ¿Coincide la verificación? ->", "SÍ ✅" if ok else "NO ❌")
