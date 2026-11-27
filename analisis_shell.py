#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
ESTUDIO EXPERIMENTAL DEL ALGORITMO DE ORDENACIÓN POR SHELL (SHELL SORT)
Simulación, medición empírica, exportación y análisis comparativo de rendimiento
==============================================================================
"""

import os
import glob
import time
import csv
import random
import platform

# Configuración del directorio de caché de Matplotlib para evitar advertencias de permisos
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")
try:
    import matplotlib.pyplot as plt
except ImportError:
    import sys
    print("\n" + "=" * 78)
    print(" [ERROR DE DEPENDENCIAS] La librería 'matplotlib' no está instalada.")
    print("=" * 78)
    print(" Para instalarla, ejecuta en tu terminal:")
    print("    pip install matplotlib")
    print(" o bien:")
    print("    pip3 install matplotlib")
    print("=" * 78 + "\n")
    sys.exit(1)

# ==============================================================================
# 1. PARÁMETROS GLOBALES DE CONFIGURACIÓN
# ==============================================================================
# Si se deja vacío (""), detecta automáticamente el sistema operativo ("Mac" o "Windows").
# Si se especifica un texto (ej. "Windows_Estresada", "Mac_M1", etc.), se usará ese nombre.
NOMBRE_ENTORNO = ""

# Lista de 10 tamaños de muestra N para el análisis asintótico empírico
TAMANIOS = [10000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000]

# Número de repeticiones para promediar las mediciones y minimizar perturbaciones externas
REPETICIONES = 3

# Semilla pseudoaleatoria fija para garantizar muestras idénticas entre plataformas
SEMILLA = 42

# Modo comparativo: Si es True, omite las pruebas empíricas y genera inmediatamente
# las tablas y gráficas comparativas cruzando los archivos CSV existentes.
SOLO_COMPARAR = False


# ==============================================================================
# 2. IDENTIFICACIÓN Y REGISTRO DEL ENTORNO DE PRUEBAS
# ==============================================================================
def resolver_nombre_entorno() -> str:
    """
    Determina el identificador del entorno.
    Si NOMBRE_ENTORNO no está definido, mapea Darwin -> Mac y Windows -> Windows.
    """
    if NOMBRE_ENTORNO.strip():
        return NOMBRE_ENTORNO.strip()
    
    sistema = platform.system()
    if sistema == "Darwin":
        return "Mac"
    elif sistema == "Windows":
        return "Windows"
    return sistema


def registrar_entorno(entorno: str) -> None:
    """
    Imprime en consola las especificaciones del entorno de ejecución
    (SO, procesador/arquitectura y versión de Python) para documentación metodológica.
    """
    print("\n" + "=" * 78)
    print("         REGISTRO METODOLÓGICO DEL ENTORNO DE EJECUCIÓN")
    print("=" * 78)
    print(f"  * Entorno Identificado : {entorno}")
    print(f"  * Sistema Operativo    : {platform.system()} {platform.release()} ({platform.version()})")
    print(f"  * Arquitectura         : {platform.machine()}")
    print(f"  * Procesador           : {platform.processor() or 'No reportado por el SO'}")
    print(f"  * Versión de Python    : {platform.python_version()} ({platform.python_implementation()})")
    print("=" * 78 + "\n")


# ==============================================================================
# 3. IMPLEMENTACIÓN EXACTA DE SHELL SORT (IN-PLACE)
# ==============================================================================
def ordenacion_shell(A: list) -> list:
    """
    Ordenación por Shell (Shell Sort) in-place con la secuencia original de saltos
    propuesta por Donald Shell (brecha = n // 2, brecha //= 2).
    
    Pseudocódigo exacto:
      - Inicializar brecha = n // 2
      - Mientras brecha > 0:
        - Para i desde brecha hasta n - 1:
          - temporal = A[i]
          - j = i
          - Mientras j >= brecha y A[j - brecha] > temporal:
            - A[j] = A[j - brecha]
            - j -= brecha
          - A[j] = temporal
        - brecha //= 2
    """
    n = len(A)
    brecha = n // 2
    while brecha > 0:
        for i in range(brecha, n):
            temporal = A[i]
            j = i
            while j >= brecha and A[j - brecha] > temporal:
                A[j] = A[j - brecha]
                j -= brecha
            A[j] = temporal
        brecha //= 2
    return A


# ==============================================================================
# 4. SIMULACIÓN PASO A PASO (SECCIÓN 4.2)
# ==============================================================================
def simular_pasadas() -> None:
    """
    Ejecuta una simulación didáctica de Shell Sort sobre el arreglo:
    [45, 23, 53, 12, 18, 9, 31, 4]
    Imprime el estado inicial y el estado del arreglo al concluir cada pasada
    con su respectiva brecha, facilitando su captura de pantalla para el reporte.
    """
    A = [45, 23, 53, 12, 18, 9, 31, 4]
    n = len(A)
    
    print("=" * 78)
    print("  SECCIÓN 4.2: SIMULACIÓN DE PASADAS DE SHELL SORT (TRAZA DIDÁCTICA)")
    print("=" * 78)
    print(f" Arreglo Inicial : {A}")
    print("-" * 78)
    
    pasada = 1
    brecha = n // 2
    while brecha > 0:
        for i in range(brecha, n):
            temporal = A[i]
            j = i
            while j >= brecha and A[j - brecha] > temporal:
                A[j] = A[j - brecha]
                j -= brecha
            A[j] = temporal
        
        print(f" Pasada {pasada} (brecha = {brecha:2d}) -> Estado: {A}")
        pasada += 1
        brecha //= 2
        
    print("-" * 78)
    print(f" Arreglo Ordenado: {A}")
    print("=" * 78 + "\n")


# ==============================================================================
# 5. GENERACIÓN DETERMINÍSTICA DE MUESTRAS (SECCIÓN VI)
# ==============================================================================
def generar_muestra(n: int, caso: str, semilla: int = SEMILLA) -> list:
    """
    Genera la muestra de tamaño n según el caso de estudio:
      - 'mejor': Lista ya ordenada ascendentemente: list(range(n))
      - 'promedio': Lista aleatoria generada determinísticamente con una instancia
                   local de random.Random(semilla) reiniciada por cada n.
      - 'peor': Lista ordenada inversamente: list(range(n, 0, -1))
    """
    if caso == "mejor":
        return list(range(n))
    elif caso == "promedio":
        # Instancia local reiniciada para garantizar secuencias idénticas en cualquier SO
        rng = random.Random(semilla)
        return [rng.randint(0, n * 10) for _ in range(n)]
    elif caso == "peor":
        return list(range(n, 0, -1))
    else:
        raise ValueError(f"Caso de prueba no reconocido: {caso}")


# ==============================================================================
# 6. MEDICIÓN TEMPORAL PRECISA Y PROTOCOLO DE CALIBRACIÓN
# ==============================================================================
def medir_tiempo_promedio(n: int, caso: str, repeticiones: int = REPETICIONES, semilla: int = SEMILLA) -> float:
    """
    Mide exclusivamente el tiempo de ordenacion_shell(copia) usando time.perf_counter().
    No incluye el tiempo de generación ni de clonación de la lista.
    Promedia las repeticiones indicadas.
    """
    muestra_base = generar_muestra(n, caso, semilla)
    tiempos = []
    
    for _ in range(repeticiones):
        copia = muestra_base.copy()
        inicio = time.perf_counter()
        ordenacion_shell(copia)
        fin = time.perf_counter()
        tiempos.append(fin - inicio)
        
    return sum(tiempos) / len(tiempos)


def ejecutar_banco_pruebas(tamanios: list, repeticiones: int, semilla: int) -> dict:
    """
    Ejecuta las pruebas para los 10 tamaños y los 3 casos, registrando los tiempos.
    Valida la condición de calibración al inicio.
    """
    resultados = {
        "N": tamanios,
        "Mejor_Caso_s": [],
        "Caso_Promedio_s": [],
        "Peor_Caso_s": []
    }
    
    print("Iniciando mediciones temporales empíricas...")
    print(f"Tamaños: {tamanios}")
    print(f"Repeticiones por muestra: {repeticiones} | Semilla: {semilla}\n")
    
    for idx, n in enumerate(tamanios, 1):
        print(f"[{idx:2d}/{len(tamanios)}] Midiendo N = {n:,} ...", end="", flush=True)
        
        t_mejor = medir_tiempo_promedio(n, "mejor", repeticiones, semilla)
        t_promedio = medir_tiempo_promedio(n, "promedio", repeticiones, semilla)
        t_peor = medir_tiempo_promedio(n, "peor", repeticiones, semilla)
        
        resultados["Mejor_Caso_s"].append(t_mejor)
        resultados["Caso_Promedio_s"].append(t_promedio)
        resultados["Peor_Caso_s"].append(t_peor)
        
        print(f" -> Mejor: {t_mejor:.5f}s | Promedio: {t_promedio:.5f}s | Peor: {t_peor:.5f}s")
        
        # Alerta de calibración: se evalúa en el primer tamaño (N mínimo) para el mejor caso
        if idx == 1 and t_mejor < 0.05:
            print("\n" + "!" * 78)
            print(" [ADVERTENCIA DE CALIBRACIÓN - UMBRAL TEMPORAL]")
            print(f" El tiempo del primer Mejor Caso (N={n}) fue de {t_mejor:.6f} s (< 0.05 s).")
            print(" Para obtener una resolución temporal de alta precisión con mínimo ruido,")
            print(" se sugiere incrementar los valores de TAMANIOS en la computadora más rápida")
            print(" antes de realizar la comparativa final entre ambas plataformas.")
            print("!" * 78 + "\n")
            
    print("\nMediciones completadas con éxito.\n")
    return resultados


# ==============================================================================
# 7. VISUALIZACIÓN EN TABLA Y EXPORTACIÓN A CSV
# ==============================================================================
def mostrar_tabla_consola(resultados: dict, entorno: str) -> None:
    """
    Imprime una tabla formateada y perfectamente alineada con los resultados.
    """
    titulo = f"RESULTADOS TEMPORALES SHELL SORT ({entorno})"
    print("=" * 78)
    print(titulo.center(78))
    print("=" * 78)
    print(f"{'N':>10} | {'Mejor Caso (s)':>18} | {'Caso Promedio (s)':>18} | {'Peor Caso (s)':>18}")
    print("-" * 78)
    
    for i in range(len(resultados["N"])):
        n_val = f"{resultados['N'][i]:,}"
        t_mej = f"{resultados['Mejor_Caso_s'][i]:.6f}"
        t_pro = f"{resultados['Caso_Promedio_s'][i]:.6f}"
        t_peo = f"{resultados['Peor_Caso_s'][i]:.6f}"
        print(f"{n_val:>10} | {t_mej:>18} | {t_pro:>18} | {t_peo:>18}")
        
    print("=" * 78 + "\n")


def exportar_csv(resultados: dict, entorno: str) -> str:
    """
    Exporta los resultados a un archivo CSV con las columnas exactas:
    N,Mejor_Caso_s,Caso_Promedio_s,Peor_Caso_s
    """
    nombre_archivo = f"resultados_shell_{entorno}.csv"
    with open(nombre_archivo, mode="w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["N", "Mejor_Caso_s", "Caso_Promedio_s", "Peor_Caso_s"])
        for i in range(len(resultados["N"])):
            escritor.writerow([
                resultados["N"][i],
                f"{resultados['Mejor_Caso_s'][i]:.6f}",
                f"{resultados['Caso_Promedio_s'][i]:.6f}",
                f"{resultados['Peor_Caso_s'][i]:.6f}"
            ])
            
    ruta_absoluta = os.path.abspath(nombre_archivo)
    print(f"Archivo CSV guardado correctamente: {ruta_absoluta}")
    return nombre_archivo


# ==============================================================================
# 8. GENERACIÓN AUTOMÁTICA DE GRÁFICAS CON MATPLOTLIB (300 DPI)
# ==============================================================================
def generar_graficas_entorno(resultados: dict, entorno: str) -> None:
    """
    Genera y guarda en 'graficas_{NOMBRE_ENTORNO}/':
      - 3 gráficas individuales (Mejor, Promedio, Peor) con etiquetas numéricas.
      - 1 gráfica combinada con las 3 curvas.
    Todas a 300 DPI, sin bloquear la ejecución.
    """
    carpeta_salida = f"graficas_{entorno}"
    os.makedirs(carpeta_salida, exist_ok=True)
    
    tamanios = resultados["N"]
    casos_info = [
        ("Mejor_Caso_s", "Mejor Caso (Lista Ordenada)", "#1f77b4", "mejor_caso"),
        ("Caso_Promedio_s", "Caso Promedio (Lista Aleatoria)", "#ff7f0e", "caso_promedio"),
        ("Peor_Caso_s", "Peor Caso (Lista Inversa)", "#d62728", "peor_caso")
    ]
    
    # -------------------------------------------------------------------------
    # 8.1. Gráficas individuales
    # -------------------------------------------------------------------------
    for columna, etiqueta, color, slug in casos_info:
        tiempos = resultados[columna]
        fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
        
        ax.plot(tamanios, tiempos, marker="o", color=color, linewidth=2, markersize=6, label=etiqueta)
        
        # Etiquetas numéricas sobre cada punto
        for x, y in zip(tamanios, tiempos):
            ax.annotate(
                f"{y:.4f}s",
                xy=(x, y),
                xytext=(0, 7),
                textcoords="offset points",
                ha="center",
                fontsize=8,
                fontweight="bold"
            )
            
        ax.set_title(f"Shell Sort: {etiqueta} - Entorno {entorno}", fontsize=13, fontweight="bold", pad=12)
        ax.set_xlabel("Tamaño de muestra (N)", fontsize=11, labelpad=8)
        ax.set_ylabel("Tiempo de ejecución (segundos)", fontsize=11, labelpad=8)
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.legend(loc="upper left", frameon=True)
        ax.margins(y=0.12)
        fig.tight_layout()
        
        ruta_guardado = os.path.join(carpeta_salida, f"grafica_{slug}_{entorno}.png")
        fig.savefig(ruta_guardado, dpi=300)
        plt.close(fig)
        print(f"Gráfica individual generada: {os.path.abspath(ruta_guardado)}")
        
    # -------------------------------------------------------------------------
    # 8.2. Gráfica combinada (las 3 curvas juntas)
    # -------------------------------------------------------------------------
    fig_comb, ax_comb = plt.subplots(figsize=(11, 7), dpi=300)
    for columna, etiqueta, color, _ in casos_info:
        tiempos = resultados[columna]
        ax_comb.plot(tamanios, tiempos, marker="o", color=color, linewidth=2, markersize=5, label=etiqueta)
        
    ax_comb.set_title(f"Shell Sort: Comparación de Casos - Entorno {entorno}", fontsize=14, fontweight="bold", pad=14)
    ax_comb.set_xlabel("Tamaño de muestra (N)", fontsize=11, labelpad=8)
    ax_comb.set_ylabel("Tiempo de ejecución (segundos)", fontsize=11, labelpad=8)
    ax_comb.grid(True, linestyle="--", alpha=0.6)
    ax_comb.legend(loc="upper left", frameon=True, fontsize=10)
    fig_comb.tight_layout()
    
    ruta_comb = os.path.join(carpeta_salida, f"grafica_combinada_{entorno}.png")
    fig_comb.savefig(ruta_comb, dpi=300)
    plt.close(fig_comb)
    print(f"Gráfica combinada generada:  {os.path.abspath(ruta_comb)}\n")


# ==============================================================================
# 9. COMPARATIVA MULTIPLATAFORMA (PRINCIPIO DE INVARIANZA)
# ==============================================================================
def cargar_csv(ruta: str) -> dict:
    """Lee un archivo CSV y devuelve los datos en un diccionario estructurado."""
    datos = {
        "N": [],
        "Mejor_Caso_s": [],
        "Caso_Promedio_s": [],
        "Peor_Caso_s": []
    }
    with open(ruta, mode="r", encoding="utf-8") as f:
        lector = csv.DictReader(f)
        for fila in lector:
            datos["N"].append(int(fila["N"]))
            datos["Mejor_Caso_s"].append(float(fila["Mejor_Caso_s"]))
            datos["Caso_Promedio_s"].append(float(fila["Caso_Promedio_s"]))
            datos["Peor_Caso_s"].append(float(fila["Peor_Caso_s"]))
    return datos


def extraer_nombre_entorno_de_archivo(ruta: str) -> str:
    """Extrae el nombre del entorno a partir del patrón 'resultados_shell_{NOMBRE}.csv'."""
    base = os.path.basename(ruta)
    nombre = base.replace("resultados_shell_", "").replace(".csv", "")
    return nombre if nombre else "Desconocido"


def ejecutar_comparativa_entornos(entorno_actual: str = "") -> None:
    """
    Revisa si existen datos de Windows y Mac (o de dos entornos distintos).
    Si ambos existen:
      - Imprime las tablas comparativas con la razón c = t_mas_lento / t_mas_rapido.
      - Genera automáticamente las 3 gráficas comparativas en 'graficas_comparativa/'.
    Si solo existe el entorno local:
      - Notifica amigablemente que se completó el registro local y explica cómo
        desbloquear la gráfica comparativa al obtener los datos reales de Windows.
    """
    archivos_csv = sorted(glob.glob("resultados_shell_*.csv"))
    
    print("\n" + "=" * 78)
    print("      MÓDULO DE COMPARACIÓN DE RENDIMIENTO (PRINCIPIO DE INVARIANZA)")
    print("=" * 78)
    
    csv_mac = "resultados_shell_Mac.csv"
    csv_win = "resultados_shell_Windows.csv"
    
    tiene_mac = os.path.exists(csv_mac)
    tiene_win = os.path.exists(csv_win)
    
    if tiene_mac and tiene_win:
        archivo_1, archivo_2 = csv_mac, csv_win
    elif len(archivos_csv) >= 2:
        archivo_1, archivo_2 = archivos_csv[0], archivos_csv[1]
    else:
        print(f" Estado: Datos del entorno actual '{entorno_actual or 'local'}' almacenados.")
        if not tiene_win:
            print(f" [AVISO] Aún no existen datos reales de Windows ('{csv_win}').")
            print(" -> Para generar la comparativa Mac vs. Windows:")
            print("    1. Ejecuta 'analisis_shell.py' en tu máquina con Windows.")
            print(f"    2. Copia el archivo '{csv_win}' generado en Windows a este directorio.")
            print("    3. Vuelve a ejecutar este script (o actívalo con SOLO_COMPARAR = True);")
            print("       la aplicación detectará los datos de Windows y generará automáticamente")
            print("       las tablas y las 3 gráficas comparativas en 'graficas_comparativa/'.")
        elif not tiene_mac:
            print(f" [AVISO] Falta el archivo de Mac ('{csv_mac}').")
        print("=" * 78 + "\n")
        return

    entorno_1 = extraer_nombre_entorno_de_archivo(archivo_1)
    entorno_2 = extraer_nombre_entorno_de_archivo(archivo_2)
    
    print(f"Comparando Entorno 1: [{entorno_1}] ({archivo_1})")
    print(f"           Entorno 2: [{entorno_2}] ({archivo_2})")
    print("=" * 78 + "\n")
    
    datos_1 = cargar_csv(archivo_1)
    datos_2 = cargar_csv(archivo_2)
    
    # Validar que los tamaños coincidan
    if datos_1["N"] != datos_2["N"]:
        print("[ERROR] Los tamaños N de ambos archivos CSV no coinciden. No se puede realizar la comparativa.")
        return

    carpeta_comp = "graficas_comparativa"
    os.makedirs(carpeta_comp, exist_ok=True)
    
    casos = [
        ("Mejor_Caso_s", "Mejor Caso", "comparativa_mejor_caso.png"),
        ("Caso_Promedio_s", "Caso Promedio", "comparativa_caso_promedio.png"),
        ("Peor_Caso_s", "Peor Caso", "comparativa_peor_caso.png")
    ]
    
    tamanios = datos_1["N"]
    
    for columna, nombre_caso, archivo_grafica in casos:
        tiempos_1 = datos_1[columna]
        tiempos_2 = datos_2[columna]
        
        print("=" * 78)
        print(f"TABLA COMPARATIVA: {nombre_caso.upper()}".center(78))
        print("=" * 78)
        col1_tit = f"Tiempo_{entorno_1}_s"
        col2_tit = f"Tiempo_{entorno_2}_s"
        print(f"{'N':>10} | {col1_tit:>20} | {col2_tit:>20} | {'c = Lento / Rapido':>22}")
        print("-" * 80)
        
        razones_c = []
        for n, t1, t2 in zip(tamanios, tiempos_1, tiempos_2):
            t_min = min(t1, t2)
            t_max = max(t1, t2)
            c = (t_max / t_min) if t_min > 0 else 1.0
            razones_c.append(c)
            print(f"{n:>10,d} | {t1:>20.6f} | {t2:>20.6f} | {c:>22.4f}")
            
        c_promedio = sum(razones_c) / len(razones_c) if razones_c else 1.0
        print("-" * 80)
        print(f"  Razón promedio c (Principio de Invarianza): {c_promedio:.4f}")
        print("=" * 80 + "\n")
        
        # Generar gráfica superpuesta
        fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
        ax.plot(tamanios, tiempos_1, marker="o", linewidth=2, label=f"{entorno_1} ({nombre_caso})", color="#1f77b4")
        ax.plot(tamanios, tiempos_2, marker="s", linewidth=2, linestyle="--", label=f"{entorno_2} ({nombre_caso})", color="#d62728")
        
        # Cuadro de texto con la razón promedio c
        ax.text(
            0.03, 0.82,
            f"Razón promedio c: {c_promedio:.4f}\n(Principio de Invarianza)",
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment="top",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="#cccccc", alpha=0.9)
        )
        
        ax.set_title(f"Principio de Invarianza: {nombre_caso} ({entorno_1} vs {entorno_2})", fontsize=13, fontweight="bold", pad=12)
        ax.set_xlabel("Tamaño de muestra (N)", fontsize=11, labelpad=8)
        ax.set_ylabel("Tiempo de ejecución (segundos)", fontsize=11, labelpad=8)
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.legend(loc="upper left", frameon=True)
        fig.tight_layout()
        
        ruta_salida = os.path.join(carpeta_comp, archivo_grafica)
        fig.savefig(ruta_salida, dpi=300)
        plt.close(fig)
        print(f"Gráfica comparativa guardada: {os.path.abspath(ruta_salida)}")
        
    print(f"\nComparativa finalizada. Las gráficas se encuentran en '{carpeta_comp}/'.\n")


# ==============================================================================
# 10. FUNCIÓN PRINCIPAL (ORQUESTADOR)
# ==============================================================================
def main() -> None:
    # 1. Determinar el entorno de ejecución
    entorno = resolver_nombre_entorno()
    registrar_entorno(entorno)
    
    # 2. Si SOLO_COMPARAR está activo, salta directamente a la comparativa de CSVs
    if SOLO_COMPARAR:
        print("[MODO SOLO COMPARAR ACTIVO]: Omitiendo mediciones de laboratorio...")
        ejecutar_comparativa_entornos(entorno)
        return

    # 3. Simulación didáctica de pasadas (Sección 4.2)
    simular_pasadas()
    
    # 4. Banco de pruebas empíricas (Sección VI)
    resultados = ejecutar_banco_pruebas(TAMANIOS, REPETICIONES, SEMILLA)
    
    # 5. Visualización de tabla en consola
    mostrar_tabla_consola(resultados, entorno)
    
    # 6. Exportación a archivo CSV
    exportar_csv(resultados, entorno)
    
    # 7. Generación de gráficas individuales y combinada (300 DPI)
    generar_graficas_entorno(resultados, entorno)
    
    # 8. Módulo comparativo (revisa si existen datos del otro entorno para comparar)
    ejecutar_comparativa_entornos(entorno)


if __name__ == "__main__":
    main()
