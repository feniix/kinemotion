# Guía de Configuración de Cámara

> **English version available:** [camera-setup.md](../../guides/camera-setup.md)

Esta guía proporciona las mejores prácticas para grabar videos de drop jumps y CMJ para asegurar un análisis preciso con kinemotion.

## Descripción General

Kinemotion ahora utiliza **posicionamiento de cámara a 45°** como configuración estándar, proporcionando mejor visibilidad de puntos de referencia y precisión de rastreo comparado con vistas laterales puras. Esta guía cubre:

1. **Un iPhone a 45°** (configuración estándar recomendada)
1. **Configuración estéreo con dos iPhones** (avanzado - para mayor precisión)

**¿Por qué 45° en lugar de lateral (90°)?**

La investigación muestra que el ángulo de visión de la cámara afecta significativamente la precisión de la estimación de pose. El ángulo de 45° proporciona:

- **Mejor visibilidad**: 40-60% de visibilidad de tobillo/rodilla vs 18-27% en vista lateral
- **Oclusión reducida**: Ambas piernas más visibles (menos auto-oclusión)
- **Buena captura del plano sagital**: Aún mide altura de salto y movimiento vertical con precisión
- **Compromiso práctico**: Entre frontal (alta visibilidad, pobre profundidad) y lateral (sagital puro, alta oclusión)

______________________________________________________________________

## Configuración 1: Un iPhone a 45° (Estándar)

### Posicionamiento de Cámara

**Recomendado para:** La mayoría de usuarios, entornos de entrenamiento, evaluación de atletas individuales

#### Diagrama Vista Superior (Una Cámara)

```text
                    N (Norte - Atleta mira hacia adelante)
                    ↑

        [Cajón]     |
            |       |
            ↓       |
           ⬤ Atleta (salta arriba/abajo)
            ↘
             ↘ ángulo 45°
              ↘
            [iPhone en Trípode]

Visualización vista lateral:

    Atleta            iPhone
       ⬤  - - - - - - [📱]
                      ↑
                   3-5m distancia
                   Altura de cadera (130-150cm)
```

**Posicionamiento clave:**

- **Ángulo:** 45° del plano sagital del atleta (entre lateral y frontal)
- **Distancia:** 3-5 metros (óptimo: 4 metros)
- **Altura:** Nivel de cadera (130-150 cm del suelo)
- **Orientación:** Modo horizontal (apaisado)

### Instrucciones Detalladas de Configuración

#### 1. Colocación Física

**Paso a paso:**

1. **Posicione al atleta en el cajón** - El atleta debe estar en su posición de salto
1. **Identifique el plano sagital** - Imagine una línea de adelante hacia atrás a través del centro del atleta
1. **Marque la posición de 45°** - Desde el lateral del atleta, muévase 45° hacia el frente
   - Si el atleta mira al Norte, la cámara debe estar al Sureste o Suroeste
   - La cámara ve el frente-lateral del atleta (no perfil puro)
1. **Establezca la distancia** - Mida 3-5m desde la posición de salto del atleta
1. **Establezca la altura** - Lente de cámara a altura de cadera del atleta (típicamente 130-150 cm)
1. **Nivele el trípode** - Asegure que la cámara esté nivelada (no inclinada arriba/abajo)

#### 2. Composición del Encuadre

**A 1080p (1920x1080), encuadre al atleta así:**

```text
|--------------------------|
|  [10-15% margen arriba]  |
|                          |
|         👤 Atleta        | ← Cuerpo completo visible
|          ↕               | ← Altura completa del salto
|         / \              | ← Ambas piernas visibles
|        /   \             |
|    [Área de aterrizaje]  | ← Suelo visible
| [10-15% margen abajo]    |
|--------------------------|
```

**Lista de verificación:**

- ✅ Cuerpo entero visible (cabeza a pies)
- ✅ 10-15% margen sobre la cabeza (para altura de salto)
- ✅ Superficie de aterrizaje visible en el encuadre
- ✅ Atleta permanece centrado durante todo el movimiento
- ✅ Ambas piernas visibles (ventaja clave del ángulo de 45°)
- ❌ No corte partes del cuerpo
- ❌ No haga paneo o zoom durante la grabación

#### 3. Configuración de Cámara

| Configuración               | Especificación               | Razón                                                 |
| --------------------------- | ---------------------------- | ----------------------------------------------------- |
| **Resolución**              | 1080p (1920x1080)            | Mínimo para detección precisa de puntos de referencia |
| **Velocidad de Cuadros**    | 60 fps (30 fps mínimo)       | 60 fps recomendado para tiempos de contacto cortos    |
| **Orientación**             | Horizontal (apaisado)        | Campo de visión más amplio                            |
| **Enfoque**                 | Manual (bloqueado en atleta) | Previene búsqueda de autoenfoque                      |
| **Exposición**              | Bloqueada/manual             | Brillo consistente durante todo el video              |
| **Velocidad de Obturación** | 1/120s o más rápido          | Reduce desenfoque de movimiento                       |
| **Estabilización**          | Trípode (requerido)          | Elimina vibración de cámara                           |

**Configuraciones específicas de iPhone:**

```text
App Cámara → Ajustes:
- Formato: Más Compatible (H.264)
- Grabar Video: 1080p a 60fps
- Bloquear Enfoque: Toque y mantenga en el atleta
- Bloquear Exposición: Deslice arriba/abajo para ajustar, luego bloquee
```

#### 4. Iluminación

**Mejores prácticas:**

- Iluminación uniforme sobre el cuerpo del atleta
- Evite contraluz (atleta como silueta)
- Interior: Luces de gimnasio generalmente suficientes
- Exterior: Condiciones nubladas ideales (luz suave y uniforme)

**Por qué importa:** MediaPipe depende del contraste visual. La iluminación deficiente reduce las puntuaciones de visibilidad de puntos de referencia y la precisión del análisis.

#### 5. Fondo

**Óptimo:**

- Pared simple o fondo de color sólido
- Alto contraste con la ropa del atleta
- Movimiento mínimo en el fondo

**Evite:**

- Fondos ocupados (equipamiento, otras personas)
- Colores similares a la ropa del atleta
- Superficies reflectivas (espejos, ventanas)

### Rendimiento Esperado

**Mejoras sobre vista lateral (90°):**

| Métrica                          | Vista Lateral (90°) | Ángulo 45°   | Mejora          |
| -------------------------------- | ------------------- | ------------ | --------------- |
| **Visibilidad Tobillo/Rodilla**  | 18-27%              | 40-60%       | +100-150%       |
| **Precisión Ángulo Articular**   | ~10-15° error       | ~8-12° error | ~20-30% mejor   |
| **Confiabilidad de Detección**   | Buena               | Excelente    | Más consistente |
| **Detección Contacto con Suelo** | Desafiante          | Más fácil    | Más robusto     |

**Limitaciones:**

- Aún monocular (estimación de profundidad ruidosa)
- Sin restricciones biomecánicas (vs Pose2Sim)
- No de grado de investigación (para eso, use configuración de doble cámara)

### Lista de Verificación de Configuración de Cámara

Antes de grabar, verifique:

- [ ] iPhone en trípode estable (sin movimiento durante grabación)
- [ ] Cámara a 45° del plano sagital del atleta
- [ ] Distancia: 3-5 metros del área de aterrizaje
- [ ] Altura: Lente de cámara a altura de cadera del atleta (130-150cm)
- [ ] Encuadre: Cuerpo completo visible (cabeza a pies + márgenes 10-15%)
- [ ] Configuración: 1080p, 60 fps, orientación horizontal
- [ ] Enfoque: Bloqueado en atleta (toque y mantenga)
- [ ] Exposición: Bloqueada (iluminación consistente)
- [ ] Iluminación: Uniforme, sin sombras marcadas ni contraluz
- [ ] Fondo: Simple, mínimas distracciones
- [ ] Grabación de prueba: Atleta permanece en encuadre durante todo el salto

______________________________________________________________________

## Configuración 2: Estéreo con Dos iPhones (Avanzado)

### Cuándo Usar Configuración de Doble Cámara

**Recomendado para:**

- Aplicaciones de investigación que requieren mayor precisión
- Evaluación de atletas de élite
- Cuando la precisión de profundidad es crítica
- Análisis biomecánico que requiere ángulos articulares

**Beneficios sobre cámara única:**

- **~50% reducción de error** (30.1mm RMSE vs 56.3mm monocular)
- **Reconstrucción 3D precisa** (elimina ambigüedad de profundidad)
- **Mejor visibilidad de puntos de referencia** (cada cámara ve ángulos diferentes)
- **Precisión de grado de investigación** (con calibración y procesamiento adecuados)

**Requisitos:**

- 2 iPhones (se recomienda mismo modelo para configuraciones coincidentes)
- 2 trípodes
- Patrón de calibración (tablero ChArUco o tablero de ajedrez)
- Flujo de trabajo de procesamiento más complejo

### Posicionamiento de Cámaras

#### Configuración óptima: ±45° del plano sagital, separación de 90°

#### Diagrama Vista Superior (Doble Cámara)

```text
                    N (Atleta mira hacia adelante)
                    ↑

    [iPhone 2]      |      [iPhone 1]
    (Lado izq.)     |      (Lado der.)
         ↘          |          ↙
          ↘ 45°     |      45° ↙
           ↘        |        ↙
             ↘   [Cajón]   ↙
               ↘    |   ↙
                 ↘  ↓ ↙
                   ⬤ Atleta

    Separación total: 90° (óptimo para triangulación)
```

**¿Por qué separación de 90°?**

La investigación de Pagnon et al. (2022) y Dill et al. (2024) encontró que un ángulo de 90° entre cámaras es óptimo para reconstrucción 3D estéreo. Esto balancea:

- Precisión de triangulación (ángulos más amplios mejor)
- Campo de visión superpuesto (cámaras deben ver los mismos puntos de referencia)
- Restricciones prácticas de configuración

### Configuración Detallada de Doble Cámara

#### Paso 1: Posicionar Ambas Cámaras

**iPhone 1 (Cámara derecha):**

- Posicionar a 45° del lado derecho del atleta
- Si el atleta mira al Norte, la cámara está al Sureste
- Distancia: 3-5m del atleta
- Altura: Nivel de cadera (130-150cm)

**iPhone 2 (Cámara izquierda):**

- Posicionar a 45° del lado izquierdo del atleta
- Si el atleta mira al Norte, la cámara está al Suroeste
- Distancia: 3-5m del atleta (igual que iPhone 1)
- Altura: Nivel de cadera (igualar iPhone 1 exactamente)

**Alineación crítica:**

- Ambas cámaras a la **misma altura** (tolerancia ±2cm)
- Ambas cámaras a la **misma distancia** del atleta (tolerancia ±10cm)
- Ambas cámaras **niveladas** (no inclinadas)
- **Separación de 90°** entre cámaras (tolerancia ±5°)

#### Paso 2: Composición del Encuadre (Ambas Cámaras)

Ambos iPhones deben encuadrar al atleta idénticamente:

```text
Vista de cada cámara:
|------------------------|
|   [margen]             |
|      👤 Cuerpo comp.   | ← Mismo encuadre
|       ↕ Altura salto   | ← Ambas cámaras
|      / \               |
|  [Área aterrizaje]     |
|   [margen]             |
|------------------------|
```

**Sincronizar encuadre:**

- Atleta centrado en ambos encuadres
- Mismos márgenes (10-15% arriba/abajo)
- Ambas ven secuencia completa de salto
- Área de aterrizaje visible en ambas

#### Paso 3: Configuración de Cámara (Ambos iPhones)

##### CRÍTICO: Ambas cámaras deben tener configuraciones idénticas

| Configuración            | Ambas Cámaras                         |
| ------------------------ | ------------------------------------- |
| **Resolución**           | 1080p (1920x1080) - exactamente igual |
| **Velocidad de Cuadros** | 60 fps - exactamente igual            |
| **Orientación**          | Horizontal - exactamente igual        |
| **Enfoque**              | Manual, bloqueado                     |
| **Exposición**           | Manual, bloqueada (mismo brillo)      |
| **Formato**              | H.264, Más Compatible                 |

**Por qué importan configuraciones idénticas:**

- La sincronización requiere velocidades de cuadros coincidentes
- La triangulación asume la misma resolución
- Diferentes exposiciones afectan la detección de puntos de referencia

#### Paso 4: Sincronización

##### Opción A: Inicio manual (simple)

1. Iniciar grabación en iPhone 1
1. Iniciar grabación en iPhone 2 dentro de 1-2 segundos
1. **Señal de sincronización:** Que el atleta aplauda o salte una vez antes de la prueba real
1. Usar este evento para sincronizar videos en post-procesamiento

##### Opción B: Sincronización de audio (mejor)

1. Usar señal de audio externa (aplauso, pitido, comando de voz)
1. Ambos iPhones graban audio
1. Alinear videos usando forma de onda de audio en post-procesamiento
1. Software como Pose2Sim tiene herramientas de sincronización incorporadas

##### Opción C: Sincronización por hardware (mejor, requiere equipo)

1. Usar dispositivo de disparo externo
1. Inicia ambas cámaras simultáneamente
1. Sincronización más precisa
1. Requiere hardware adicional

**Recomendación:** Comience con Opción A (manual + aplauso), actualice a Opción B si es necesario.

#### Paso 5: Calibración

**Requerido:** Calibración única antes del primer uso o si cambian las posiciones de cámara

**Opciones de patrón de calibración:**

1. **Tablero ChArUco** (recomendado - más robusto)

   - Imprimir patrón ChArUco grande (A3 o mayor)
   - Montar en tablero rígido
   - Tamaño de cuadrícula: 7x5 o similar

1. **Tablero de ajedrez** (alternativa)

   - Imprimir tablero de ajedrez grande (A3 o mayor)
   - Cuadrícula 8x6 o 9x7
   - Asegurar perfectamente plano

**Procedimiento de calibración:**

```bash
# Si usa Pose2Sim
1. Grabar patrón de calibración desde ambas cámaras
2. Mover patrón a través del volumen de captura (10-15 posiciones diferentes)
3. Asegurar que el patrón sea visible en ambas cámaras simultáneamente
4. Ejecutar calibración:
   Pose2Sim.calibration()
```

**Salidas de calibración:**

- Intrínsecos de cámara (distancia focal, distorsión)
- Extrínsecos de cámara (posiciones relativas, rotación)
- Se guarda en archivo de calibración para reutilización

**Re-calibrar cuando:**

- Las posiciones de cámara cambien
- Se usen diferentes lentes
- Después de varias semanas (verificación de deriva)

### Procesamiento de Videos de Doble Cámara

**Soporte actual de kinemotion:** Solo cámara única

**Para procesar videos estéreo, necesitará:**

#### Opción A: Usar Pose2Sim (recomendado)

```bash
# Instalar Pose2Sim
pip install pose2sim

# Procesar videos estéreo
Pose2Sim.calibration()      # Una vez
Pose2Sim.poseEstimation()   # Ejecutar MediaPipe en ambos videos
Pose2Sim.synchronization()  # Sincronizar videos
Pose2Sim.triangulation()    # Reconstrucción 3D
Pose2Sim.filtering()        # Suavizar trayectorias
Pose2Sim.kinematics()       # Ángulos articulares OpenSim
```

#### Opción B: Futuro soporte estéreo de kinemotion

El soporte de doble cámara puede ser agregado a kinemotion en versiones futuras. Hoja de ruta actual:

- Módulo de triangulación estéreo
- Sincronización automática
- Flujo de trabajo de calibración integrado

#### Opción C: Triangulación manual

Si tiene experiencia en programación, implemente triangulación estéreo usando OpenCV y la salida de MediaPipe de ambas cámaras.

### Rendimiento Esperado (Doble Cámara)

**Mejoras de precisión sobre cámara única:**

| Métrica                       | Cámara Única (45°) | Doble Cámara (Estéreo) | Mejora                 |
| ----------------------------- | ------------------ | ---------------------- | ---------------------- |
| **RMSE de Posición**          | ~56mm              | ~30mm                  | 47% mejor              |
| **Error de Ángulo Articular** | ~8-12°             | ~5-7°                  | ~30-40% mejor          |
| **Precisión de Profundidad**  | Pobre (ruidosa)    | Buena                  | Elimina ambigüedad     |
| **Visibilidad de Puntos**     | 40-60%             | 70-90%                 | Cobertura multi-ángulo |

**Investigación validada:**

- Dill et al. (2024): MediaPipe estéreo logró 30.1mm RMSE vs estándar de oro Qualisys
- Pagnon et al. (2022): Separación de cámara de 90° óptima para triangulación

### Lista de Verificación de Doble Cámara

Antes de grabar, verifique:

- [ ] **Ambos iPhones** en trípodes estables
- [ ] **Cámara 1** a +45° del lado derecho del atleta
- [ ] **Cámara 2** a -45° del lado izquierdo del atleta
- [ ] **Separación total de 90°** entre cámaras
- [ ] **Misma distancia** (3-5m) del atleta para ambas cámaras
- [ ] **Misma altura** (nivel de cadera, 130-150cm) para ambas cámaras
- [ ] **Ambas niveladas** (no inclinadas arriba/abajo)
- [ ] **Configuraciones idénticas** (1080p, 60fps, horizontal)
- [ ] **Enfoque y exposición** idénticos bloqueados
- [ ] **Método de sincronización** planeado (aplauso, señal de audio, etc.)
- [ ] **Calibración** completada (una vez)
- [ ] **Grabación de prueba** desde ambas cámaras simultáneamente

______________________________________________________________________

## Configuración de Grabación (Ambas Configuraciones)

### Especificaciones de Video

| Configuración            | Requisito       | Recomendación     | Razón                                               |
| ------------------------ | --------------- | ----------------- | --------------------------------------------------- |
| **Resolución**           | 1080p mínimo    | 1080p (1920x1080) | Mayor resolución mejora precisión de MediaPipe      |
| **Velocidad de Cuadros** | 30 fps mínimo   | **60 fps**        | Mejor para tiempos de contacto cortos (150-250ms)   |
| **Orientación**          | Solo horizontal | Horizontal        | Campo de visión más amplio para movimiento de salto |
| **Formato**              | MP4, MOV, AVI   | MP4 (H.264)       | Compatibilidad universal                            |
| **Bitrate**              | Más alto mejor  | Auto o 50+ Mbps   | Preserva detalle durante movimiento                 |

### ¿Por qué 60 fps vs 30 fps?

**Para drop jumps y CMJ:**

| Métrica                         | 30 fps            | 60 fps            |
| ------------------------------- | ----------------- | ----------------- |
| **Resolución temporal**         | 33.3ms por cuadro | 16.7ms por cuadro |
| **Muestreo contacto con suelo** | 5-8 cuadros       | 10-15 cuadros     |
| **Error de medición de tiempo** | ±33ms             | ±16ms             |
| **Precisión de velocidad**      | Buena             | Mejor             |

**Tiempos de contacto con suelo en drop jumps:** 150-250ms

- A 30 fps: Solo 5-8 muestras durante contacto
- A 60 fps: 10-15 muestras durante contacto (2x mejor)

**Recomendación:** Use 60 fps si su iPhone lo soporta. La mejora en precisión justifica el tamaño de archivo mayor.

### Configuraciones de Cámara de iPhone

**Cómo configurar iPhone para grabación óptima:**

1. **Abrir app Cámara**
1. **Ajustes → Cámara → Grabar Video**
   - Seleccionar: **1080p a 60 fps** (o 30 fps si 60 no disponible)
1. **Ajustes → Cámara → Formatos**
   - Seleccionar: **Más Compatible** (H.264, no HEVC)
1. **Antes de grabar:**
   - **Bloquear enfoque:** Toque y mantenga en atleta hasta que aparezca "Bloqueo AE/AF"
   - **Bloquear exposición:** Deslice arriba/abajo para ajustar brillo, luego mantenga bloqueado
1. **Composición de encuadre:**
   - Posicionar atleta en el centro
   - Asegurar cuerpo completo visible con márgenes
1. **Iniciar grabación** antes de que el atleta comience la secuencia de salto

**Consejo Profesional:** Grabe un video de prueba primero y verifique:

- Atleta permanece en encuadre
- Enfoque permanece nítido
- Iluminación es adecuada
- Sin desenfoque de movimiento

______________________________________________________________________

## Guías de Iluminación

### Grabación Interior

**Recomendado:**

- Luces de gimnasio superiores (típicamente 400-800 lux suficiente)
- Iluminación uniforme a través del área de salto
- Evite crear sombra del atleta en el fondo

**Verificar:**

- Cara y articulaciones del atleta claramente visibles
- Sin sombras marcadas en el cuerpo
- Sin puntos brillantes (ventanas, superficies reflectivas)

### Grabación Exterior

**Mejores condiciones:**

- Día nublado (iluminación suave y uniforme)
- Evite sol del mediodía (sombras marcadas)
- Evite tarde (ángulo bajo, sombras largas)

**Posicionamiento:**

- Sol detrás o al lado de las cámaras
- Atleta no a contraluz (silueta)
- Considere hora del día para iluminación consistente

______________________________________________________________________

## Guías de Fondo

**Fondo óptimo:**

- Pared simple (color neutro)
- Contraste con ropa del atleta
- Sin patrones o elementos ocupados
- Estático (sin movimiento)

**Ejemplos de contraste de color:**

- Atleta con ropa oscura → fondo claro (pared blanca/gris)
- Atleta con ropa clara → fondo oscuro (pared azul/gris)
- Evite: Atleta en blanco → fondo blanco (bajo contraste)

**Por qué importa:** MediaPipe separa figura del fondo. Alto contraste mejora precisión de detección de puntos de referencia y reduce falsos positivos.

______________________________________________________________________

## Errores Comunes a Evitar

### ❌ Cámara No a Ángulo de 45°

```text
❌ INCORRECTO: Lateral puro (90°)
         [Atleta]
             |
             |
    [Cámara]←┘

❌ INCORRECTO: Frontal puro (0°)
    [Cámara]
       ↓
    [Atleta]

✅ CORRECTO: Ángulo de 45°
         [Atleta]
             ↘
              ↘ 45°
            [Cámara]
```

**Problema con lateral:** Alta oclusión, baja visibilidad de tobillo/rodilla
**Problema con frontal:** Ambigüedad de profundidad, medición de altura de salto pobre
**Solución:** Use ángulo de 45° como se especifica

### ❌ Cámara Demasiado Cerca (\<3m)

**Problemas:**

- Distorsión de perspectiva (efecto gran angular)
- Riesgo de que atleta salga del encuadre
- Distorsión de lente en bordes (líneas curvas)

**Solución:** Mantener distancia de 3-5m

### ❌ Cámara Demasiado Alta o Baja

```text
❌ Muy alta (mirando hacia abajo):
    [Cámara]
       ↓ ↘
         [Atleta]

❌ Muy baja (mirando hacia arriba):
         [Atleta]
       ↗ ↑
    [Cámara]

✅ Correcta (nivel de cadera):
    [Cámara] → [Atleta]
```

**Problema:** Error de paralaje, proporciones distorsionadas
**Solución:** Lente de cámara a altura de cadera (130-150cm)

### ❌ Encuadre Pobre

**Errores comunes:**

- Atleta muy pequeño en encuadre (cámara muy lejos)
- Atleta cortado durante salto (cámara muy cerca o baja)
- No centrado (atleta se sale del encuadre)

**Solución:**

- Grabar prueba primero
- Ajustar encuadre para incluir salto completo con márgenes
- Marcar posición de salto para asegurar consistencia

### ❌ Configuraciones Inconsistentes Entre Cámaras Duales

**Solo para configuración estéreo:**

**Problemas:**

- Diferentes velocidades de cuadros → sincronización imposible
- Diferentes resoluciones → triangulación falla
- Diferentes exposiciones → detección de puntos de referencia inconsistente

**Solución:** Configurar ambos iPhones idénticamente (ver Lista de Verificación de Doble Cámara)

______________________________________________________________________

## Resolución de Problemas

### Advertencia de "Visibilidad de Puntos de Referencia Pobre"

**Síntomas:** Kinemotion reporta puntuaciones bajas de visibilidad

**Causas:**

- Iluminación insuficiente
- Bajo contraste con el fondo
- Cámara desenfocada
- Desenfoque de movimiento (velocidad de obturación muy lenta)

**Soluciones:**

1. Agregar fuentes de iluminación
1. Cambiar fondo o ropa del atleta para contraste
1. Bloquear enfoque en atleta (toque y mantenga)
1. Aumentar velocidad de obturación (reducir exposición si es necesario)
1. Asegurar resolución 1080p

### La Altura del Salto Parece Incorrecta

**Posibles causas:**

1. Ángulo de cámara no exactamente 45° (error de medición)
1. Falta parámetro de calibración `--drop-height`
1. Atleta moviéndose horizontalmente (deriva durante salto)
1. Cámara no nivelada (inclinada)

**Soluciones:**

1. Verificar ángulo de 45° con app de medición o transportador
1. Proporcionar altura del cajón: `--drop-height 0.40`
1. Entrenar al atleta para saltar derecho hacia arriba (deriva mínima)
1. Usar indicador de nivel de trípode o app de nivel de teléfono

### Error "No se Detectó Drop Jump"

**Posibles causas:**

1. Video no incluye secuencia completa
1. Atleta cortado en encuadre
1. Calidad de rastreo muy pobre

**Soluciones:**

1. Iniciar grabación antes de que atleta suba al cajón
1. Ajustar encuadre - probar con salto de práctica
1. Mejorar calidad de video (iluminación, enfoque, resolución)
1. Usar bandera manual `--drop-start-frame` si auto-detección falla

### Doble Cámara: Videos No Sincronizados

**Síntomas:** Triangulación falla o produce poses 3D irreales

**Soluciones:**

1. Verificar que ambos videos tengan velocidades de cuadros idénticas
1. Usar señal audio/visual para sincronizar (aplauso, pitido)
1. Usar módulo de sincronización de Pose2Sim
1. Considerar gatillo de hardware para futuras grabaciones

______________________________________________________________________

## Recomendaciones de Equipo

### Configuración de Cámara Única

**Opción Económica ($100-300):**

- iPhone SE (2020 o posterior) o Android insignia
- Trípode básico con soporte para smartphone ($20-50)
- Total: ~$150-350

**Gama Media ($500-800):**

- iPhone reciente (11 o posterior) con 4K/60fps
- Trípode de calidad con cabeza fluida ($100-200)
- Total: ~$600-1000

**Lo que necesita:**

- iPhone capaz de 1080p @ 60fps mínimo
- Trípode estable (peso ligero OK para uso interior)
- Indicador de nivel (la mayoría de trípodes tienen nivel de burbuja)

### Configuración de Doble Cámara

**Estéreo Económico ($300-600):**

- 2x iPhone SE o similar
- 2x trípodes básicos
- Tablero de calibración (imprimir y montar, \<$20)
- Total: ~$350-650

**Estéreo Gama Media ($1000-1600):**

- 2x iPhone reciente (mismo modelo)
- 2x trípodes de calidad
- Tablero de calibración profesional
- Opcional: Gatillo de sincronización por hardware
- Total: ~$1200-1800

**Lo que necesita:**

- 2 iPhones (mismo modelo muy recomendado)
- 2 trípodes estables (ajuste de altura idéntico)
- Patrón de calibración (ChArUco o tablero de ajedrez)
- Capacidad de procesamiento (laptop/desktop para Pose2Sim)

**Comparación de costo con sistemas de grado de investigación:**

- MoCap basado en marcadores (Vicon, Qualisys): $50,000-$500,000
- Markerless comercial (Theia3D): $5,000-$20,000
- Doble iPhone + Pose2Sim: $300-$1,800 (¡100x más barato!)

______________________________________________________________________

## Validación y Verificaciones de Calidad

### Después de Grabar

**Para cada video, verifique:**

1. **Verificación de reproducción:**

   - Secuencia de salto completa capturada
   - Atleta permanece en encuadre
   - Enfoque nítido durante todo
   - Sin desenfoque de movimiento

1. **Métricas de calidad:**

   - Tamaño de archivo apropiado (60fps 1080p ≈ 200MB/min)
   - Sin cuadros perdidos (reproducción suave)
   - Audio claro (si se usa para sincronización)

1. **Prueba de análisis:**

   - Ejecutar kinemotion en video
   - Verificar salida de superposición de depuración
   - Verificar calidad de detección de puntos de referencia

### Indicadores de Calidad

**Video de buena calidad (listo para análisis):**

- ✅ Puntuaciones de visibilidad de MediaPipe >0.5 promedio
- ✅ Rastreo suave de puntos de referencia (jitter mínimo)
- ✅ Todas las fases de salto detectadas automáticamente
- ✅ Superposición de depuración muestra rastreo consistente

**Video de calidad pobre (se recomienda re-grabar):**

- ❌ Puntuaciones de visibilidad \<0.3 promedio
- ❌ Posiciones de puntos de referencia errática (pérdida de rastreo)
- ❌ Detección de fase fallida
- ❌ Superposición de depuración muestra huecos o poses irreales

______________________________________________________________________

## Consejos Avanzados

### Para Grabación Consistente Multi-Sesión

**Crear una configuración estandarizada:**

1. **Marcar posiciones de cámara** en el suelo con cinta

   - Medir ángulo de 45° con precisión
   - Marcar círculo de distancia de 4m
   - Etiquetar posiciones "Cámara 1" y "Cámara 2"

1. **Documentar su configuración:**

   - Tomar fotos de posiciones de cámara
   - Anotar configuraciones de altura de trípode
   - Guardar captura de pantalla de configuraciones de cámara

1. **Usar mismo equipo** a través de sesiones

   - Mismo(s) iPhone(s)
   - Misma altura de trípode
   - Misma habitación/ubicación si es posible

**Beneficios:**

- Mediciones consistentes a través del tiempo
- Más fácil comparar progreso del atleta
- Configuración simplificada para cada sesión

### Optimización para Diferentes Tipos de Salto

**Específico para Drop Jump:**

- Asegurar que cajón de salto sea visible en encuadre (importante para contexto)
- Capturar fase de estar parado antes de caer
- Necesita ver contacto con suelo claramente

**Específico para CMJ:**

- Iniciar con atleta ya en encuadre (sin cajón)
- Capturar fase de contramovimiento (movimiento hacia abajo)
- Necesita rango completo de movimiento (punto más bajo al pico)

**Ambos:**

- 60 fps beneficioso para movimientos rápidos
- Altura de cámara a nivel de cadera óptima
- Ángulo de 45° funciona para ambos tipos de salto

______________________________________________________________________

## Antecedentes de Investigación

### ¿Por Qué Estas Recomendaciones?

**Ángulo de cámara (45°):**

- Baldinger et al. (2025) mostró que el ángulo de visión de cámara afecta significativamente la validez del ángulo articular
- 45° reduce oclusión mientras mantiene visibilidad del plano sagital
- Compromiso entre frontal (alta visibilidad) y lateral (sagital puro)

**Separación de doble cámara de 90°:**

- Pagnon et al. (2022): Probó múltiples ángulos, encontró 90° óptimo para triangulación 3D
- Dill et al. (2024): Validó MediaPipe estéreo a 30.1mm RMSE con configuración de 90°
- Balance entre línea base amplia (precisión) y vistas superpuestas (coincidencia)

**1080p @ 60fps:**

- Mayor resolución mejora detección de puntos de referencia de MediaPipe
- 60 fps necesario para eventos temporales precisos (contacto con suelo)
- Validado en múltiples estudios como suficiente para biomecánica

### Limitaciones de Cámara Única

**Lo que cámara única (45°) NO PUEDE proporcionar:**

- Precisión de grado de investigación (limitado a ~8-12° errores de ángulo articular)
- Coordenadas 3D/profundidad precisas (eje-z ruidoso)
- Restricciones biomecánicas (sin modelo esquelético)
- Validación contra estándar de oro (necesita multi-cámara)

**Lo que cámara única (45°) PUEDE proporcionar:**

- Mediciones de calidad para entrenamiento y evaluación
- Comparaciones relativas (mismo atleta a través del tiempo)
- Métricas clave de drop jump (tiempo de contacto, tiempo de vuelo, RSI)
- Métricas de CMJ (altura de salto, profundidad de contramovimiento)

**Para precisión de grado de investigación:** Use configuración estéreo de doble cámara con Pose2Sim o OpenCap.

______________________________________________________________________

## Resumen

### Un iPhone a 45° (Configuración Estándar)

**Configuración rápida:**

1. Posicionar cámara a 45° del plano sagital del atleta
1. 4 metros de distancia, altura de cadera (130-150cm)
1. 1080p @ 60 fps, horizontal, enfoque/exposición bloqueados
1. Encuadrar cuerpo completo con márgenes de 10-15%
1. Iluminación uniforme, fondo simple
1. Grabar secuencia completa de salto

**Precisión esperada:** Buena para entrenamiento/evaluación (~8-12° ángulos articulares)

### Estéreo con Dos iPhones (Configuración Avanzada)

**Configuración rápida:**

1. Posicionar Cámara 1 a +45° (derecha), Cámara 2 a -45° (izquierda)
1. Ambas a 4m distancia, ambas a altura de cadera, separación de 90°
1. Configuraciones idénticas: 1080p @ 60fps
1. Calibrar con patrón ChArUco/tablero de ajedrez
1. Sincronizar con aplauso o señal de audio
1. Procesar con Pose2Sim para reconstrucción 3D

**Precisión esperada:** Grado de investigación (~5-7° ángulos articulares, 30mm RMSE)

### Guía de Decisión

**Use cámara única si:**

- Aplicaciones de entrenamiento/coaching
- Evaluar mejoras relativas
- Restricciones de presupuesto/equipo
- Se prioriza simplicidad

**Use doble cámara si:**

- Aplicaciones de investigación
- Evaluación de atletas de élite
- Se necesita cinemática 3D precisa
- Publicación o validación requerida

______________________________________________________________________

## Documentación Relacionada

- **[English Version](../../guides/camera-setup.md)** - Versión en inglés de esta guía
- **[Estimación de Pose para Biomecánica Deportiva](../../research/sports-biomechanics-pose-estimation.md)** - Investigación completa sobre sistemas de pose
- **[Referencia Rápida de Sistemas de Pose](../../reference/pose-systems.md)** - Guía de comparación de sistemas
- [Guía de Parámetros CLI](../../reference/parameters.md) - Parámetros de análisis
- [Guía CMJ](../../guides/cmj-guide.md) - Especificaciones de salto con contramovimiento
- [CLAUDE.md](https://github.com/feniix/kinemotion/blob/main/CLAUDE.md) principal - Documentación completa del proyecto (GitHub)

______________________________________________________________________

## Referencias

**Investigación de ángulo de cámara:**

- Baldinger, M., Reimer, L. M., & Senner, V. (2025). Influence of the Camera Viewing Angle on OpenPose Validity in Motion Analysis. *Sensors*, 25(3), 799. <https://doi.org/10.3390/s25030799>

**Validación de cámara estéreo:**

- Dill, S., et al. (2024). Accuracy Evaluation of 3D Pose Reconstruction Algorithms Through Stereo Camera Information Fusion for Physical Exercises with MediaPipe Pose. *Sensors*, 24(23), 7772. <https://doi.org/10.3390/s24237772>

**Separación óptima de cámara:**

- Pagnon, D., Domalain, M., & Reveret, L. (2022). Pose2Sim: An End-to-End Workflow for 3D Markerless Sports Kinematics—Part 2: Accuracy. *Sensors*, 22(7), 2712. <https://doi.org/10.3390/s22072712>

Para bibliografía completa, ver [sports-biomechanics-pose-estimation.md](../../research/sports-biomechanics-pose-estimation.md).

______________________________________________________________________

**Última Actualización:** 6 de noviembre, 2025
