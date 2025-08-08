# archivo: tabla_base0.py

def generar_simbolos():
    # a hasta n
    simbolos = [chr(c) for c in range(ord('a'), ord('n') + 1)]
    # ñ
    simbolos.append('ñ')
    # o hasta z
    simbolos += [chr(c) for c in range(ord('o'), ord('z') + 1)]
    return simbolos

def imprimir_tabla(simbolos_por_linea=8):
    simbolos = generar_simbolos()
    ancho_num = len(str(len(simbolos) - 1))
    ancho_sim = max(len(s) for s in simbolos)
    ancho_celda = max(ancho_num, ancho_sim) + 2  # ancho base para centrar

    # Encabezado centrado (símbolo primero)
    encabezado = f"{'Símb'.center(ancho_celda)}{'Número'.center(ancho_celda)}"
    encabezado_linea = (encabezado + "  ") * simbolos_por_linea
    print(encabezado_linea.rstrip())
    print((("=" * ancho_celda + " " * ancho_celda + "  ") * simbolos_por_linea).rstrip())

    # Filas centradas (símbolo primero)
    for fila_inicio in range(0, len(simbolos), simbolos_por_linea):
        fila = []
        for i in range(fila_inicio, min(fila_inicio + simbolos_por_linea, len(simbolos))):
            simb_centrado = simbolos[i].center(ancho_celda)
            num_centrado = str(i).center(ancho_celda)
            fila.append(simb_centrado + num_centrado)
        print("  ".join(fila))




if __name__ == "__main__":
    imprimir_tabla()
