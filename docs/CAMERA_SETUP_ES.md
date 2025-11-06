# Guía de Configuración de Cámara

> **English version available:** [CAMERA_SETUP.md](CAMERA_SETUP.md)

Esta guía proporciona las mejores prácticas para grabar videos de saltos de cajón (drop jumps) y asegurar un análisis preciso con kinemotion.

## Descripción General

El posicionamiento adecuado de la cámara es crítico para un análisis preciso del salto de cajón. La implementación actual utiliza **análisis 2D del plano sagital**, lo que requiere una configuración de cámara lateral para capturar el movimiento vertical con precisión.

## Configuración de Cámara para Drop Jump

### Posición Requerida de la Cámara

La cámara debe posicionarse en ángulo de vista lateral, perpendicular al plano sagital (90°).

#### Diagrama de Posicionamiento de Cámara

```text
                    Vista Superior (mirando desde arriba)
                    ======================================

                       [Cajón de salto]
     [Cámara]              |
Posicionada al LADO  →     | (atleta cae directamente)
      3-5m                 |
(perpendicular al atleta)  ↓
                           ⬤  ← Punto de aterrizaje (junto al cajón)
```

**Puntos Clave:**

- **Alineación horizontal:** Cámara posicionada al **lado** del área de drop-jump, centrada entre cajón y punto de aterrizaje
- **Ángulo perpendicular:** 90° al plano de movimiento (atleta se mueve verticalmente, no hacia/desde la cámara)
- **Distancia:** 3-5 metros de distancia
- **Altura:** Lente de cámara a altura de cadera del atleta

### Requisitos de Configuración

| Parámetro              | Especificación                                   | Razón                                                      |
| ---------------------- | ------------------------------------------------ | ---------------------------------------------------------- |
| **Posición de cámara** | Vista lateral, perpendicular al plano sagital    | Captura el movimiento vertical (eje-y) directamente        |
| **Distancia**          | 3-5 metros del atleta                            | Visibilidad de cuerpo completo sin distorsión              |
| **Altura**             | Lente de cámara a la altura de cadera del atleta | Minimiza la distorsión de perspectiva                      |
| **Encuadre**           | Cabeza a pies visible durante todo el salto      | Asegura que todos los puntos de referencia sean rastreados |
| **Orientación**        | Horizontal (apaisado)                            | Campo de visión más amplio para el movimiento              |

### Instrucciones Detalladas

#### 1. Posicionamiento de la Cámara

**Posición Horizontal:**

- Coloque la cámara **perpendicular** al plano de salto del atleta (ángulo de 90°)
- **Alinee la cámara horizontalmente en un punto entre el cajón y el punto de aterrizaje**
  - El punto de aterrizaje está inmediatamente adyacente al cajón (el atleta cae directamente)
  - La cámara debe estar centrada en esta área de drop-jump
  - Esto asegura que el atleta se mueva principalmente verticalmente en el encuadre, no hacia/desde la cámara
- Posicione la cámara para capturar toda la secuencia del drop jump:
  - De pie sobre el cajón
  - Bajando (justo al lado del cajón)
  - Aterrizando en el suelo (inmediatamente adyacente al cajón)
  - Saltando hacia arriba
  - Aterrizando nuevamente

**Posición Vertical:**

- Coloque el lente de la cámara aproximadamente a la **altura de la cadera** del atleta
- Esto minimiza la distorsión de perspectiva en los extremos (cabeza y pies)
- Para trípodes ajustables: típicamente altura de 0.8-1.2m

**Distancia:**

- **Mínimo 3 metros**: Más cerca aumenta la distorsión de perspectiva
- **Máximo 5 metros**: Más lejos reduce la precisión del rastreo
- **Óptimo ~4 metros**: Balance entre precisión y campo de visión

#### 2. Encuadre

**Cobertura de Cuerpo Completo:**

```text
Límites del encuadre:
┌──────────────────────┐
│       [cabeza]       │ ← Superior: 10-20cm por encima de la cabeza al estar de pie
│                      │
│         /|\          │
│        / | \         │
│         / \          │ ← Cuerpo: Torso y extremidades completamente visibles
│        /   \         │
│       /     \        │
│      [pies]          │ ← Inferior: Incluir suelo/superficie de aterrizaje
└──────────────────────┘
```

**Importante:**

- ✅ Mantenga al atleta centrado en el encuadre durante todo el salto
- ✅ Incluya la superficie de aterrizaje (suelo) en el encuadre
- ✅ Deje margen sobre la cabeza (~10-20cm) para la altura completa del salto
- ❌ No corte ninguna parte del cuerpo durante el movimiento
- ❌ No realice paneo o zoom durante la grabación

#### 3. Iluminación

**Recomendado:**

- Iluminación uniforme sobre el cuerpo del atleta
- Evite contraluz (atleta como silueta)
- Interior: luces de gimnasio generalmente son suficientes
- Exterior: evite sombras marcadas (condiciones nubladas son ideales)

**Por qué importa:**

- MediaPipe depende del contraste visual para la detección de puntos de referencia
- La iluminación deficiente reduce las puntuaciones de visibilidad de puntos de referencia
- El auto-ajuste puede compensar pero la precisión disminuye

#### 4. Fondo

**Mejores prácticas:**

- Fondo simple, con contraste (ej. pared detrás del atleta)
- Evite fondos ocupados (múltiples personas, equipamiento)
- Minimice el movimiento en el fondo

**Por qué importa:**

- MediaPipe funciona mejor con separación clara figura-fondo
- Los fondos ocupados pueden interferir con la detección de pose

### Configuración de Grabación

| Configuración            | Recomendación         | Notas                                                        |
| ------------------------ | --------------------- | ------------------------------------------------------------ |
| **Velocidad de Cuadros** | 30-60 fps             | Más alto es mejor; el auto-ajuste ajusta los parámetros      |
| **Resolución**           | 1080p mínimo          | Mayor resolución mejora la detección de puntos de referencia |
| **Orientación**          | Horizontal (apaisado) | Mejor campo de visión para encuadre lateral                  |
| **Formato**              | MP4, MOV, AVI         | Formatos de video más comunes soportados                     |
| **Estabilización**       | Usar trípode          | Videos con cámara en mano pueden reducir precisión           |

### Errores Comunes a Evitar

#### ❌ Vista Frontal/Trasera en Lugar de Lateral

```text
❌ INCORRECTO: Vista frontal

    [Cámara]
       ↓
      ---
     | O |  ← Atleta mirando a la cámara
      ---
     / | \
      / \
```

**Problema:** El movimiento vertical se convierte en profundidad (eje-z), lo cual es:

- Menos preciso en visión computacional 2D
- No validado en literatura de investigación
- No puede medir la altura del salto de manera confiable

**Solución:** Siempre use vista lateral como se especifica arriba.

#### ❌ Cámara Demasiado Cerca (\< 3m)

**Problema:**

- La distorsión de perspectiva aumenta el error de medición
- Riesgo de que el atleta se salga del encuadre
- Distorsión de lente gran angular en los bordes

#### ❌ Cámara Demasiado Alta/Baja

**Problema:**

- Mirar hacia abajo/arriba al atleta crea error de paralaje
- El posicionamiento a altura de cadera minimiza este efecto

#### ❌ Ángulo de Cámara No Perpendicular

```text
❌ INCORRECTO: Cámara a ángulo de 45°

         [Cámara]
           ↙
         /
        /
      ⬤ ← Atleta
```

**Problema:**

- Trayectoria de movimiento acortada por ángulo de proyección
- Altura del salto subestimada
- Cálculo del tiempo de contacto con el suelo afectado

**Solución:** Posicione la cámara a verdadero ángulo de 90° (perpendicular al plano sagital).

### Lista de Verificación de Configuración de Cámara

Antes de grabar, verifique:

- [ ] Cámara en trípode estable (sin movimiento durante la grabación)
- [ ] Vista lateral: Cámara perpendicular al plano de salto del atleta
- [ ] Distancia: 3-5 metros del cajón/área de aterrizaje
- [ ] Altura: Lente de cámara a altura de cadera del atleta
- [ ] Encuadre: Cuerpo completo visible (cabeza a pies + margen)
- [ ] Iluminación: Uniforme, sin sombras marcadas ni contraluz
- [ ] Fondo: Simple, mínimas distracciones
- [ ] Configuración: 30+ fps, 1080p+ resolución, orientación horizontal
- [ ] Grabación de prueba: Verificar que el atleta permanezca en el encuadre durante todo el salto

## ¿Por Qué Vista Lateral?

### Fundamento Biomecánico

Los drop jumps son **principalmente movimientos verticales** en el plano sagital:

1. **Fase de caída**: Descenso vertical (gravedad)
1. **Aterrizaje**: Desaceleración vertical (fuerza de reacción del suelo)
1. **Contacto con el suelo**: Desplazamiento vertical mínimo
1. **Despegue**: Aceleración vertical (salto)
1. **Vuelo**: Movimiento vertical (trayectoria parabólica)

### Requisitos de Medición

**Lo que medimos:**

- ✅ **Desplazamiento vertical** (eje-y): Altura del salto
- ✅ **Velocidad vertical** (dy/dt): Detección de contacto
- ✅ **Ángulos articulares en plano sagital**: Extensión de tobillo, rodilla, cadera

**Lo que no necesitamos (para drop jumps):**

- ❌ Desplazamiento horizontal (x, z): Debe ser mínimo en técnica correcta
- ❌ Movimiento en plano frontal: No es métrica principal para drop jumps
- ❌ Rotación/giro: No aplicable a drop jumps

### Validación de Investigación

Los protocolos estándar para investigación biomecánica de drop jumps emplean universalmente **posicionamiento de cámara lateral**:

- Visualización directa de la cinemática del plano sagital
- Medición precisa del desplazamiento vertical
- Observación clara de triple extensión (tobillo-rodilla-cadera)
- Validado contra plataformas de fuerza y captura de movimiento 3D

**Referencia:** El análisis 2D del plano sagital muestra fuerte correlación (r = 0.51-0.93) con captura de movimiento 3D para ángulos articulares del cuerpo inferior durante tareas de salto.

## Impacto de la Calidad de Video en el Análisis

### Video de Alta Calidad (Recomendado)

**Características:**

- 60 fps de velocidad de cuadros
- Resolución 1080p o 4K
- Buena iluminación (visibilidad de puntos de referencia > 0.7)
- Cámara estable (trípode)
- Fondo limpio

**Ajustes de auto-ajuste:**

- Suavizado mínimo (preserva detalle)
- Filtro bilateral deshabilitado (no necesario)
- Umbrales de confianza estándar

**Precisión esperada:** Mediciones de grado de investigación

### Video de Calidad Media (Aceptable)

**Características:**

- 30 fps de velocidad de cuadros
- Resolución 720p
- Iluminación moderada (visibilidad de puntos de referencia 0.4-0.7)
- Cámara estable
- Algo de desorden en el fondo

**Ajustes de auto-ajuste:**

- Suavizado moderado
- Filtro bilateral habilitado
- Umbrales de confianza estándar

**Precisión esperada:** Buena para entrenamiento y evaluación

### Video de Baja Calidad (Puede Funcionar)

**Características:**

- \< 30 fps de velocidad de cuadros
- \< 720p de resolución
- Iluminación deficiente (visibilidad de puntos de referencia \< 0.4)
- Cámara en mano (ligero movimiento)
- Fondo ocupado

**Ajustes de auto-ajuste:**

- Suavizado agresivo
- Filtro bilateral habilitado
- Umbrales de confianza reducidos

**Precisión esperada:** Precisión reducida, usar solo para evaluación preliminar

**Recomendación:** Si es posible, vuelva a grabar con mejores condiciones.

## Configuración Multi-Cámara (Característica Futura)

**Nota:** La implementación actual usa cámara lateral única. Las versiones futuras pueden soportar análisis multi-cámara.

### Configuración Multi-Cámara Potencial

```text
                Vista Superior
                ==============

    [Cámara 2]
    (Vista frontal)
         ↓

         ⬤  <-- Atleta
         |

[Cámara 1] ◄──┤
(Vista lateral)
```

**Cámara 1 (Vista lateral):** Análisis del plano sagital

- Altura del salto
- Tiempo de contacto con el suelo
- Ángulos de triple extensión

**Cámara 2 (Vista frontal):** Análisis del plano frontal (requiere implementación 3D)

- Valgo/varo de rodilla
- Asimetrías bilaterales
- Estabilidad lateral

**Estado:** No soportado actualmente. Manténgase atento a futuras actualizaciones.

## Resolución de Problemas

### Advertencia de "Visibilidad de puntos de referencia deficiente"

**Causa:** MediaPipe no puede detectar puntos de referencia corporales de manera confiable

**Soluciones:**

1. Mejorar la iluminación (agregar fuente de luz, evitar sombras)
1. Asegurar fondo con contraste
1. Verificar el enfoque de la cámara (atleta debe estar enfocado nítidamente)
1. Acercar la cámara (pero mantener 3m mínimo)
1. Aumentar la resolución del video

### La altura del salto parece incorrecta

**Posibles causas:**

1. Ángulo de cámara no perpendicular (trayectoria de salto parece más corta)
1. Falta parámetro de calibración `--drop-height`
1. Atleta moviéndose horizontalmente durante el salto (desviación)
1. Calidad de rastreo deficiente (verificar superposición de video de depuración)

**Soluciones:**

1. Verificar que la cámara esté a verdadero ángulo de 90°
1. Proporcionar altura conocida del cajón: `--drop-height 0.40`
1. Asegurar que el atleta salte derecho hacia arriba (entrenamiento)
1. Mejorar la calidad del video como se describe arriba

### Error "No se detectó drop jump"

**Posibles causas:**

1. El video no incluye la secuencia completa (falta fase de estar parado en el cajón)
1. El encuadre de la cámara corta al atleta
1. Calidad de rastreo muy deficiente

**Soluciones:**

1. Comenzar a grabar antes de que el atleta suba al cajón
1. Asegurar que el cuerpo completo sea visible en todo momento
1. Mejorar la calidad del video
1. Usar `--drop-start-frame` manual si la auto-detección falla

## Recomendaciones de Equipo de Cámara

### Opción Económica ($100-300)

- Smartphone en trípode (iPhone, Android con 1080p/60fps)
- Trípode económico con soporte para teléfono
- Aplicaciones de grabación de video gratuitas con controles manuales

**Pros:** Accesible, portátil, calidad suficiente
**Contras:** Zoom limitado, sensor más pequeño

### Opción Gama Media ($300-800)

- Cámara de acción (GoPro, DJI) con FOV amplio
- Trípode robusto
- Buena en condiciones de iluminación variadas

**Pros:** Duradera, altas velocidades de cuadros (120fps+), buena calidad de imagen
**Contras:** Distorsión de gran angular en los bordes

### Opción Profesional ($800+)

- Cámara sin espejo/DSLR (Sony, Canon, Nikon)
- Trípode profesional con cabeza fluida
- Lente principal o zoom (rango 24-70mm)

**Pros:** Mejor calidad de imagen, control manual, lentes intercambiables
**Contras:** Costoso, configuración más compleja

**Recomendación:** La mayoría de los smartphones (2020+) son suficientes para el análisis de drop jump. Priorice el posicionamiento adecuado sobre el equipo costoso.

## Resumen

**Puntos Clave:**

1. ✅ **La vista lateral es obligatoria** para el análisis actual de drop jump
1. ✅ Posicione la cámara **perpendicular** al plano de salto
1. ✅ Mantenga **distancia de 3-5 metros** a **altura de cadera**
1. ✅ Encuadre **cuerpo completo** con margen para altura del salto
1. ✅ Use **trípode** para estabilidad
1. ✅ Grabe a **30+ fps, resolución 1080p+**
1. ✅ Asegure **buena iluminación** y **fondo limpio**

Siga estas pautas para maximizar la precisión y confiabilidad del análisis.

## Documentación Relacionada

- **[English Version](CAMERA_SETUP.md)** - English version of this guide
- [Guía de Parámetros CLI](PARAMETERS.md) - Explicación detallada de todos los parámetros de análisis
- [Guía de Procesamiento por Lotes](BULK_PROCESSING.md) - Procesamiento eficiente de múltiples videos
- [CLAUDE.md](../CLAUDE.md) principal - Documentación completa del proyecto
