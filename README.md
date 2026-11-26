# Análisis Experimental de Rendimiento: Algoritmo de Ordenación por Shell (Shell Sort)

Este repositorio contiene una solución integral y modular en Python (`analisis_shell.py`) diseñada para simular, medir empíricamente, exportar y analizar el comportamiento asintótico del algoritmo de **Ordenación por Shell (Shell Sort)** utilizando la secuencia original de saltos propuesta por Donald Shell. Además, incorpora un módulo de validación del **Principio de Invarianza** mediante la comparación cruzada entre dos entornos de hardware/sistema operativo (por ejemplo, macOS vs. Windows).

---

## 1. Fundamentos Teóricos del Algoritmo

El algoritmo **Shell Sort** (propuesto por Donald Shell en 1959) es una generalización de la ordenación por inserción directa (*Insertion Sort*). Mientras que la inserción convencional compara únicamente elementos adyacentes (avanzando de 1 en 1, lo que provoca que mover un elemento pequeño desde el final hacia el inicio requiera $O(n)$ desplazamientos), Shell Sort introduce el concepto de **ordenación por brechas o saltos ($h$-sorting)**.

### Secuencia Original de Saltos
El programa implementa estrictamente la secuencia clásica:
- Salto inicial: $\text{brecha} = \lfloor n / 2 \rfloor$
- En cada pasada subsiguiente: $\text{brecha} = \lfloor \text{brecha} / 2 \rfloor$
- Condición de parada: $\text{brecha} = 0$ (la última pasada se realiza con $\text{brecha} = 1$, equivalente a una inserción directa sobre un arreglo que ya se encuentra "casi ordenado").

### Pseudocódigo e Implementación In-Place
```python
def ordenacion_shell(A: list) -> list:
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
```

- **In-place:** El algoritmo opera directamente en memoria sobre el arreglo recibido sin requerir arreglos auxiliares ($O(1)$ memoria espacial adicional).
- **Complejidad Temporal:**
  - **Mejor Caso:** $O(n \log n)$ cuando el arreglo ya se encuentra ordenado.
  - **Caso Promedio:** Aproximadamente $O(n^{1.25})$ a $O(n^{1.5})$ con la secuencia original de saltos.
  - **Peor Caso:** $\Theta(n^2)$ con la secuencia original de mitades consecutivas en ciertos patrones patológicos.

---

## 2. Estructura del Proyecto

```text
python_shell_sort/
│
├── analisis_shell.py              # Script principal modular y documentado
├── README.md                      # Documentación metodológica y guía de uso
├── resultados_shell_Mac.csv       # Tiempos de ejecución obtenidos en Mac
├── resultados_shell_Windows.csv   # Tiempos de ejecución obtenidos en Windows
│
├── graficas_Mac/                  # Gráficas generadas para el entorno Mac (300 DPI)
│   ├── grafica_mejor_caso_Mac.png
│   ├── grafica_caso_promedio_Mac.png
│   ├── grafica_peor_caso_Mac.png
│   └── grafica_combinada_Mac.png
│
├── graficas_Windows/              # Gráficas generadas para el entorno Windows (300 DPI)
│   └── ...
│
└── graficas_comparativa/          # Gráficas comparativas superpuestas (300 DPI)
    ├── comparativa_mejor_caso.png
    ├── comparativa_caso_promedio.png
    └── comparativa_peor_caso.png
```

---

## 3. Módulos y Funcionamiento de `analisis_shell.py`

El programa está organizado en 10 secciones modulares:

### 3.1. Configuración Centralizada (Cabecera)
Al inicio del archivo se exponen las variables globales para facilitar cualquier ajuste de laboratorio:
```python
NOMBRE_ENTORNO = ""  # Vacío = auto-detección ("Mac" o "Windows")
TAMANIOS = [10000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000]
REPETICIONES = 3     # Promedia 3 ejecuciones por muestra
SEMILLA = 42         # Semilla pseudoaleatoria constante
SOLO_COMPARAR = False # Si es True, salta mediciones y genera comparativas cruzadas
```

### 3.2. Registro Metodológico del Entorno
Utiliza el módulo nativo `platform` para identificar e imprimir en la consola:
- Nombre y distribución del Sistema Operativo.
- Versión del Kernel.
- Arquitectura del procesador (`arm64`, `x86_64`, etc.).
- Versión exacta e implementación del intérprete de Python (ej. CPython 3.13).

### 3.3. Simulación Didáctica por Pasadas (Sección 4.2)
La función `simular_pasadas()` ejecuta Shell Sort sobre la muestra de referencia `[45, 23, 53, 12, 18, 9, 31, 4]` (longitud $n = 8$):
1. **Estado Inicial:** `[45, 23, 53, 12, 18, 9, 31, 4]`
2. **Pasada 1 ($\text{brecha} = 4$):** Sublistas entrelazadas a distancia 4. Estado resultante: `[18, 9, 31, 4, 45, 23, 53, 12]`.
3. **Pasada 2 ($\text{brecha} = 2$):** Sublistas a distancia 2. Estado resultante: `[18, 4, 31, 9, 45, 12, 53, 23]`.
4. **Pasada 3 ($\text{brecha} = 1$):** Inserción final. Estado resultante: `[4, 9, 12, 18, 23, 31, 45, 53]`.

Esta salida se imprime con formato limpio en consola, lista para captura de pantalla e inclusión en el reporte académico.

### 3.4. Generación Determinística de Muestras (Sección VI)
Para asegurar que los experimentos sean estrictamente reproducibles entre diferentes computadoras:
- **Mejor Caso:** Lista estrictamente ordenada de menor a mayor: `list(range(n))`.
- **Caso Promedio:** Lista de enteros pseudoaleatorios generada con `random.Random(SEMILLA)`. Al instanciar un generador local reiniciado con la misma semilla antes de cada $n$, la secuencia de números generada en Windows y en macOS es **idéntica byte a byte**.
- **Peor Caso (empírico):** Lista estrictamente invertida (orden descendente): `list(range(n, 0, -1))`.

### 3.5. Medición Temporal Rigurosa y Alerta de Calibración
- **Aislamiento del cronómetro:** Se utiliza `time.perf_counter()` únicamente alrededor de `ordenacion_shell(copia)`. Los tiempos de generación de la muestra y el clonado (`lista.copy()`) quedan explícitamente excluidos.
- **Promedio estadístico:** Se promedian `REPETICIONES = 3` mediciones por muestra.
- **Umbral de Calibración:** Si el primer tiempo del Mejor Caso ($N = 10,000$) resulta inferior a `0.05` segundos, se emite una advertencia visual prominente recomendando aumentar `TAMANIOS` si se busca mayor resolución frente al ruido del planificador del SO.

### 3.6. Exportación y Visualización de Datos
- **Consola:** Tabla perfectamente alineada con los tiempos en segundos para los 10 tamaños en los 3 casos.
- **CSV:** Archivo `resultados_shell_{NOMBRE_ENTORNO}.csv` con columnas exactas:
  ```csv
  N,Mejor_Caso_s,Caso_Promedio_s,Peor_Caso_s
  ```

### 3.7. Generación de Gráficas en Alta Resolución (300 DPI)
El programa crea la carpeta `graficas_{NOMBRE_ENTORNO}/` y genera mediante `matplotlib`:
1. `grafica_mejor_caso_{NOMBRE_ENTORNO}.png`: Curva con marcadores circulares, cuadrícula y etiquetas de tiempo numéricas sobre cada punto.
2. `grafica_caso_promedio_{NOMBRE_ENTORNO}.png`: Curva del caso promedio con anotaciones numéricas.
3. `grafica_peor_caso_{NOMBRE_ENTORNO}.png`: Curva del peor caso con anotaciones numéricas.
4. `grafica_combinada_{NOMBRE_ENTORNO}.png`: Las 3 curvas superpuestas con colores diferenciados y leyenda.
Todas las figuras se exportan a 300 DPI y se cierran de inmediato con `plt.close(fig)` para no bloquear la ejecución del flujo.

---

## 4. Principio de Invarianza y Comparación Multiplataforma

### Fundamento Teórico
El **Principio de Invarianza** de la teoría de algoritmos establece que dos implementaciones correctas del mismo algoritmo ejecutadas en dos máquinas distintas $M_1$ y $M_2$ difieren en su tiempo de ejecución únicamente por un factor constante multiplicativo $c$:

$$T_{M_2}(n) \approx c \cdot T_{M_1}(n)$$

Donde $c$ refleja la diferencia de potencia de cómputo (frecuencia de reloj, arquitectura de memoria, compilador/intérprete, microarquitectura), mientras que la forma asintótica de la curva se mantiene idéntica.

### Cálculo Empírico en el Programa
Cuando existen al menos dos archivos CSV en el directorio (por ejemplo, `resultados_shell_Mac.csv` y `resultados_shell_Windows.csv`):
1. El programa calcula la razón para cada tamaño $N$:
   $$c = \frac{T_{\text{más\_lento}}}{T_{\text{más\_rápido}}}$$
2. Imprime tablas comparativas por caso con las columnas:
   - `N`
   - `Tiempo_Mac_s`
   - `Tiempo_Windows_s`
   - `c = Lento / Rapido`
   - Razón promedio $\bar{c}$.
3. Genera en `graficas_comparativa/` 3 gráficas comparativas superponiendo ambas curvas con marcadores diferenciados (`o` para Mac, `s` con línea punteada para Windows) y un cuadro informativo indicando la razón promedio $c$.

---

## 5. Instrucciones de Uso y Flujo de Trabajo

### Requisitos Previos
Tener instalado Python 3.8+ y `matplotlib`:
```bash
pip install matplotlib
```

### Paso 1: Ejecutar en el primer entorno (ejemplo: macOS)
Simplemente corre el script:
```bash
python3 analisis_shell.py
```
- Se generarán:
  - `resultados_shell_Mac.csv`
  - Carpeta `graficas_Mac/` con las 4 imágenes `.png` en 300 DPI.

### Paso 2: Ejecutar en el segundo entorno (ejemplo: Windows)
Copia `analisis_shell.py` a la máquina Windows y ejecútalo en PowerShell o CMD:
```powershell
python analisis_shell.py
```
- Se generarán:
  - `resultados_shell_Windows.csv`
  - Carpeta `graficas_Windows/` con sus 4 imágenes `.png`.

### Paso 3: Generar la Comparativa Cruzada (Principio de Invarianza)
1. Coloca `resultados_shell_Mac.csv` y `resultados_shell_Windows.csv` en la misma carpeta.
2. Abre `analisis_shell.py` y cambia la opción en la línea 32:
   ```python
   SOLO_COMPARAR = True
   ```
3. Ejecuta de nuevo:
   ```bash
   python3 analisis_shell.py
   ```
4. El programa omitirá las pruebas y generará de inmediato las tablas de razones $c$ en consola y las 3 gráficas comparativas en `graficas_comparativa/`.
