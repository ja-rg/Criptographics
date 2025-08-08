# ElGamal paso x paso con "mini sustitución" y nombres descriptivos
from random import Random, randrange

from lib.generador_primos import primo_ndigitos

# --- utilidades ---
def inverso_modular(valor, primo_modulo):
    """Devuelve x tal que valor*x ≡ 1 (mod primo_modulo)."""
    try:
        return pow(valor, -1, primo_modulo)  # Python 3.8+
    except TypeError:
        # Euclides extendido
        def egcd(x,b): 
            return (x,1,0) if b==0 else (lambda g,x,y:(g,y,x-(x//b)*y))(*egcd(b,x%b))
        g,x,_ = egcd(valor, primo_modulo)
        assert g == 1, "No hay inverso (valor y primo no coprimos)"
        return x % primo_modulo

# --- generación de claves ---
def generar_claves(primo_modulo, generador_g):
    print("1) Parámetros del grupo: primo p y generador g.")
    print(f"   p = {primo_modulo}, g = {generador_g}")
    exponente_privado_x = randrange(1, primo_modulo-1)
    print("2) Elegir exponente privado x ∈ [1, p-2].")
    print(f"   x = {exponente_privado_x}  (SECRETO)")
    componente_publica_y = pow(generador_g, exponente_privado_x, primo_modulo)
    print("3) Calcular y = g^x mod p (parte pública).")
    print(f"   y = {generador_g}^{exponente_privado_x} mod {primo_modulo} = {componente_publica_y}")
    print(f"   Clave pública: (p,g,y) = ({primo_modulo},{generador_g},{componente_publica_y}). Clave privada: x = {exponente_privado_x}.")
    clave_publica = (primo_modulo, generador_g, componente_publica_y)
    return clave_publica, exponente_privado_x

# --- cifrado ---
def cifrar_mensaje(clave_publica, mensaje_m):
    primo_modulo, generador_g, componente_publica_y = clave_publica
    print("4) CIFRADO del mensaje m (0 < m < p).")
    print(f"   m = {mensaje_m}")
    exponente_efimero_k = randrange(1, primo_modulo-1)
    print("   Elegir k aleatorio efímero ≠ 0.")
    print(f"   k = {exponente_efimero_k}")
    cifrado_parte_c1 = pow(generador_g, exponente_efimero_k, primo_modulo)
    print(f"   c1 = g^k mod p = {generador_g}^{exponente_efimero_k} mod {primo_modulo} = {cifrado_parte_c1}")
    h_elevado_k = pow(componente_publica_y, exponente_efimero_k, primo_modulo)
    print(f"   y^k = ({componente_publica_y})^{exponente_efimero_k} mod {primo_modulo} = {h_elevado_k}")
    cifrado_parte_c2 = (mensaje_m * h_elevado_k) % primo_modulo
    print(f"   c2 = m * y^k mod p = {mensaje_m} * {h_elevado_k} mod {primo_modulo} = {cifrado_parte_c2}")
    print("   Texto cifrado: C = (c1, c2).\n")
    return (cifrado_parte_c1, cifrado_parte_c2)

# --- descifrado ---
def descifrar_mensaje(clave_publica, exponente_privado_x, texto_cifrado_C):
    primo_modulo, generador_g, componente_publica_y = clave_publica
    cifrado_parte_c1, cifrado_parte_c2 = texto_cifrado_C
    print("5) DESCIFRADO con la privada x.")
    print(f"   Recibido C = (c1,c2) = ({cifrado_parte_c1}, {cifrado_parte_c2})")
    secreto_compartido_s = pow(cifrado_parte_c1, exponente_privado_x, primo_modulo)
    print(f"   s = c1^x mod p = {cifrado_parte_c1}^{exponente_privado_x} mod {primo_modulo} = {secreto_compartido_s}")
    inverso_de_s = inverso_modular(secreto_compartido_s, primo_modulo)
    print(f"   s^(-1) mod p = inv({secreto_compartido_s}, {primo_modulo}) = {inverso_de_s}")

    # --- MINI SUSTITUCIÓN ANTES DE LA RESPUESTA FINAL ---
    # Mostramos explícitamente la operación de recuperación:
    print("   (Mini sustitución) m = c2 * s^(-1) mod p")
    print(f"                     m = {cifrado_parte_c2} * {inverso_de_s} mod {primo_modulo}")

    mensaje_recuperado = (cifrado_parte_c2 * inverso_de_s) % primo_modulo
    print(f"   Resultado: m = {mensaje_recuperado}\n")
    return mensaje_recuperado

# --- propuesta g ---
def proponer_generador_aleatorio(primo_p, semilla=None):
    """Proponer un generador aleatorio g para el grupo multiplicativo Z/pZ."""
    rng = Random(semilla)
    while True:
        g = rng.randrange(2, primo_p)
        if pow(g, (primo_p - 1) // 2, primo_p) != 1:
            return g
        # Si no es generador, probamos con otro
        continue
    

# --- demo breve ---
if __name__ == "__main__":
    print("=== ElGamal paso x paso (con mini sustitución) ===")
    # Primo pequeño y generador para demo de examen
    primo_p = primo_ndigitos(4, semilla=2026)
    generador_g = proponer_generador_aleatorio(primo_p, semilla=2026)

    clave_publica, exponente_privado_x = generar_claves(primo_p, generador_g)
    mensaje_original_m = 123

    texto_cifrado = cifrar_mensaje(clave_publica, mensaje_original_m)
    mensaje_descifrado = descifrar_mensaje(clave_publica, exponente_privado_x, texto_cifrado)

    print("6) Verificación final:")
    print(f"   Mensaje original = {mensaje_original_m}")
    print(f"   Mensaje recuperado = {mensaje_descifrado}")
    print("   ¿Coinciden? ->", "SÍ ✅" if mensaje_original_m == mensaje_descifrado else "NO ❌")
