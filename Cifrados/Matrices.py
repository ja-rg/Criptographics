# Matrices.py
from sympy import Matrix, gcd

# ——————————————————————————————
# Alfabeto base 0 con Ñ (A=0,...,Ñ=14,...,Z=26)
# ——————————————————————————————
ALFABETO = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","Ñ","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
M = len(ALFABETO)  # 27
MAP_LETRA_NUM = {ch:i for i,ch in enumerate(ALFABETO)}

# ——————————————————————————————
# Conversiones letra↔número y texto↔números (con Ñ)
# ——————————————————————————————
def letra_a_num(ch: str) -> int:
    ch = ch.upper()
    if ch not in MAP_LETRA_NUM:
        raise ValueError(f"Carácter no soportado en el alfabeto de 27 (incluye Ñ): {ch!r}")
    return MAP_LETRA_NUM[ch]

def num_a_letra(n: int) -> str:
    return ALFABETO[int(n) % M]

def texto_a_nums(texto: str) -> list[int]:
    """Convierte texto (A..Z y Ñ) a lista de enteros base-27."""
    return [letra_a_num(c) for c in texto.upper().replace(" ", "")]

def nums_a_text(nums: list[int]) -> str:
    return "".join(num_a_letra(n) for n in nums)

# ——————————————————————————————
# Utilidades de matrices/vectores mod 27
# ——————————————————————————————
def matriz_clave_valida(K: Matrix, mod: int = M) -> bool:
    """Det coprimo con 27 (no múltiplo de 3)."""
    d = int(K.det()) % mod
    return gcd(d, mod) == 1

def inv_matriz_mod(K: Matrix, mod: int = M) -> Matrix:
    """Inversa modular (falla si det no es invertible mod 27)."""
    return K.inv_mod(mod)

def vector_mod(v: Matrix | list[int], mod: int = M) -> Matrix:
    v = Matrix(v) if not isinstance(v, Matrix) else v
    return v.applyfunc(lambda x: int(x) % mod)

def mult_mod(K: Matrix, v: Matrix | list[int], mod: int = M) -> Matrix:
    v = Matrix(v) if not isinstance(v, Matrix) else v
    return vector_mod(K * v, mod)

# ——————————————————————————————
# Impresiones con “número previo”: letraₙ
# ——————————————————————————————
def matriz_a_letras_list(mat) -> list[list[str]]:
    """Solo para mostrar: mapea números→letras; NO metas strings a Matrix."""
    if isinstance(mat, Matrix):
        return [[num_a_letra(mat[i, j]) for j in range(mat.cols)] for i in range(mat.rows)]
    return [[num_a_letra(v) for v in fila] for fila in mat]

def latex_matriz_letras_y_num(mat: Matrix, parens: bool = False) -> str:
    """
    Devuelve LaTeX con letra y número como subíndice, p.ej. \text{B}_{1}
    Úsalo solo para render (NO convierte nada dentro de SymPy).
    """
    env = "pmatrix" if parens else "bmatrix"
    filas = []
    for i in range(mat.rows):
        cols = [rf"\text{{{num_a_letra(int(mat[i,j]))}}}_{{{int(mat[i,j])}}}" for j in range(mat.cols)]
        filas.append(" & ".join(cols))
    cuerpo = r" \\ ".join(filas)
    return rf"\begin{{{env}}}{cuerpo}\end{{{env}}}"

def latex_vec_operacion(K: Matrix, x: Matrix, y: Matrix | None = None, mod: int = M) -> str:
    """
    Mini-sustitución: muestra K·x (=y) con letraₙ y números:
    [B₁; ...]  →  multiplica →  [C₂; ...]
    """
    from sympy import latex
    y = mult_mod(K, x, mod) if y is None else Matrix(y)
    A = latex(K)
    X_let = latex_matriz_letras_y_num(x, parens=True)
    Y_let = latex_matriz_letras_y_num(y, parens=True)
    # Extra: también la versión numérica:
    X_num = latex(Matrix(x))
    Y_num = latex(Matrix(y))
    return (
        rf"{A}\cdot {X_let} = {Y_let}"
        rf"\quad\text{{ (números: }}{A}\cdot {X_num} \equiv {Y_num}\pmod{{{mod}}}\text{{)}}"
    )

# ——————————————————————————————
# Bloques Hill (padding con 'X' = 24)
# ——————————————————————————————
def partir_bloques(nums: list[int], n: int, padding: int = MAP_LETRA_NUM["X"]) -> list[Matrix]:
    """Parte en bloques columna de tamaño n (rellena con 'X' si falta)."""
    out = []
    for i in range(0, len(nums), n):
        bloque = nums[i:i+n]
        if len(bloque) < n:
            bloque += [padding] * (n - len(bloque))
        out.append(Matrix(bloque))
    return out
