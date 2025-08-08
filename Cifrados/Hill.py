# Hill_paso_a_paso.py
from sympy import Matrix, print_latex
from Matrices import (
    M, texto_a_nums, nums_a_text, partir_bloques,
    matriz_clave_valida, inv_matriz_mod, mult_mod,
    latex_matriz_letras_y_num, latex_vec_operacion
)

def cifrar_hill(texto: str, K: Matrix) -> str:
    assert matriz_clave_valida(K, M), f"Clave no válida: det(K) mod {M} no es coprimo."
    nums = texto_a_nums(texto)
    bloques = partir_bloques(nums, K.rows)
    print(f"1) Texto {texto} convertido a números: {nums}")
    
    print(f"2) Partir en bloques de {K.rows} (columna). Total:", len(bloques))
    print("3) Cifrado por bloques: y ≡ K·x (mod 27)\n")

    latex_pasos = []
    cifrados = []
    for idx, x in enumerate(bloques, 1):
        y = mult_mod(K, x, M)
        cifrados.extend(int(v) for v in y)
        print(f"  Bloque {idx}: x = {list(map(int, x))} -> y = {list(map(int, y))}")
        latex_pasos.append(latex_vec_operacion(K, x, y, mod=M))

    print("\n4) Resultado numérico:", cifrados)
    texto_c = nums_a_text(cifrados)
    print("5) Resultado en letras:", texto_c)

    # Bonus: imprime LaTeX listo para render
    print("\n—— LaTeX (copia y pega) ——")
    print(r"\[")
    for paso in latex_pasos:
        print(paso + r"\quad")
    print(r"\]")

    return texto_c

def descifrar_hill(texto_c: str, K: Matrix) -> str:
    K_inv = inv_matriz_mod(K, M)
    nums = texto_a_nums(texto_c)
    bloques = partir_bloques(nums, K.rows)
    print("\n=== Descifrado ===")
    print("1) Inversa modular K^{-1} (mod 27) calculada.")
    print("2) Aplicar x ≡ K^{-1}·y (mod 27)\n")

    latex_pasos = []
    planos = []
    for idx, y in enumerate(bloques, 1):
        x = mult_mod(K_inv, y, M)
        planos.extend(int(v) for v in x)
        print(f"  Bloque {idx}: y = {list(map(int, y))} -> x = {list(map(int, x))}")
        latex_pasos.append(latex_vec_operacion(K_inv, y, x, mod=M))

    print("\n3) Plano numérico:", planos)
    texto_p = nums_a_text(planos)
    print("4) Plano letras:", texto_p)

    print("\n—— LaTeX (copia y pega) ——")
    print(r"\[")
    for paso in latex_pasos:
        print(paso + r"\quad")
    print(r"\]")

    return texto_p

if __name__ == "__main__":
    # Ejemplo 2x2 válido (det coprimo con 27)
    K = Matrix([[3, 5],
                [7, 2]])
    assert matriz_clave_valida(K), "La clave no es invertible mod 27 (prueba otra)."

    texto = "HOLAÑ"
    print("=== Hill paso a paso (mod 27, alfabeto con Ñ) ===")
    print("Clave K =")
    print_latex(K)

    cifrado = cifrar_hill(texto, K)
    plano  = descifrar_hill(cifrado, K)

    print("\n¿Coinciden? ->", "SÍ ✅" if texto == plano[:len(texto)] else "NO ❌")
