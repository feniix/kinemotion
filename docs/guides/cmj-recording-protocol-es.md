# 📹 Protocolo de Grabación CMJ: Ángulo Óptimo de Cámara para MediaPipe

**Recomendación:** Usar **vista oblicua de 45°** para mejor precisión de tracking con MediaPipe

**Basado en:** Estudio de validación empírica (Diciembre 2025) que demuestra que 45° proporciona tracking superior vs 90° lateral

______________________________________________________________________

## ⚡ Lo Esencial

| Elemento                | Especificación                               |
| ----------------------- | -------------------------------------------- |
| **Ángulo de Cámara**    | **45° oblicuo** (RECOMENDADO)                |
| **¿Por qué 45°?**       | Mejor separación de landmarks para MediaPipe |
| **Evitar 90°**          | Vista lateral causa oclusión de landmarks    |
| **Resolución**          | 1080p mínimo                                 |
| **Frame Rate**          | 60fps mínimo (120fps preferido)              |
| **Protocolo**           | Manos en cadera, vista oblicua de 45°        |
| **Tracking de Tobillo** | Esperar 120-150° en despegue                 |

______________________________________________________________________

## 📸 Setup de Cámara

**Posición:**

- Distancia: 4m (óptimo) o 3-5m
- Altura cámara: Nivel del pecho/torso medio del atleta (~100-120cm)
- **Ángulo de cámara: 45° oblicuo** (RECOMENDADO)
  - Posicionar cámara entre lateral (90°) y frontal (0°)
  - Atleta visible desde ~45° hacia el lado
  - ✅ **¿Por qué 45°?** Mejor separación de landmarks de tobillo para MediaPipe
  - ❌ **Evitar 90° lateral:** Causa superposición de landmarks → tracking deficiente

**Configuración:**

- Formato: MP4 o MOV, H.264
- Iluminación: Uniforme, sin sombras en tobillo
- Fondo: Contraste alto con ropa atleta
- Estabilización: Tripié seguro y nivelado

______________________________________________________________________

## 🎬 Protocolo de Grabación

**Setup Recomendado (vista oblicua de 45°):**

1. **Posicionar cámara a ángulo de 45°** al lado del atleta
1. **Marcar posición del atleta:** Posición fija en piso, misma ropa y calzado
1. **Grabar saltos:** Un video por salto (1-3 saltos recomendados)
1. **Mantener consistencia:** Mismo ángulo, iluminación y distancia

**Importante:**

- Capturar un video por salto—no grabar múltiples saltos en un archivo
- Mantener cámara a 45° oblicuo para todas las grabaciones
- Asegurar que landmarks de tobillo (talón, tobillo, dedos) estén claramente visibles y separados

______________________________________________________________________

### ¿Por qué 45° Oblicuo? (Evidencia Empírica)

**Resultados del Estudio de Validación (Diciembre 2025):**

- **45° oblicuo**: 140.67° promedio de ángulo de tobillo ✅ (preciso)
- **90° lateral**: 112.00° promedio de ángulo de tobillo ⚠️ (subestimado)
- **Causa Raíz**: En 90° lateral, una pierna oculta la otra → MediaPipe **confunde pie izquierdo/derecho**

**Conclusión Clave:** MediaPipe no puede distinguir cuál pie es cuál en 90° lateral. En 45° oblicuo, ambas piernas están claramente separadas, permitiendo tracking preciso izquierda/derecha.

______________________________________________________________________

## ✅ Requisitos Críticos

- ✅ **Ángulo de cámara de 45° oblicuo** (óptimo para MediaPipe)
- ✅ **Manos en cadera fijas** durante TODO el movimiento
- ✅ **Iluminación consistente** (sin sombras en tobillo)
- ✅ **Un video por salto** (archivos independientes)
- ✅ **Buena forma:** CMJ profundo, extensión explosiva, sin brazos
- ✅ **Landmarks de tobillo visibles:** Talón, tobillo y dedos claramente separados

❌ **No hacer:**

- Usar vista lateral pura de 90° (causa oclusión de landmarks)
- Grabar múltiples saltos en un video
- Grabar con mala iluminación (afecta detección de landmarks)
- Posicionar cámara muy cerca (\< 3m) o muy lejos (> 5m)

______________________________________________________________________

## 📊 Frame Rate y Configuración

| Frame Rate | Configuración iPhone/Android                                      |
| ---------- | ----------------------------------------------------------------- |
| **60fps**  | Settings → Camera → Record Video: 1080p at 60fps                  |
| **120fps** | Settings → Camera → Record Video: 1080p at 120fps (si disponible) |

**Nota:** 120fps requiere mejor iluminación que 60fps

______________________________________________________________________

## 📝 Checklist Antes de Grabar

- [ ] Tripié estable, nivel
- [ ] Atleta en posición, con mismo calzado
- [ ] Iluminación uniforme, sin sombras
- [ ] Frame rate correcto en ajustes
- [ ] Prueba de 5 segundos grabada
- [ ] Atleta visible de cabeza a pies
- [ ] Manos en cadera (posición inicial verificada)

______________________________________________________________________

## 🎯 Criterios de Aceptación

Cada video debe tener:

- ✅ Vista lateral clara (45° o 90°)
- ✅ Cuerpo completo visible
- ✅ Tobillo bien iluminado, visible
- ✅ Manos en cadera durante TODO el movimiento
- ✅ CMJ profundo y explosivo
- ✅ Plantarflexión clara en despegue
- ✅ Forma de investigación evidente

______________________________________________________________________

## 📋 Referencia Rápida: Ángulos de Tobillo (en vista de 45°)

**Posición inicial (neutral):** ~80-90° (pie perpendicular a pierna)
**Despegue (plantarflexión):** ~120-150° (pie apuntando abajo)
**Esperado en despegue:** ~140° promedio según estudio de validación
**Progresión objetivo:** Al menos 30° de extensión de tobillo durante salto

**Nota:** Estos valores son para vista oblicua de 45°. Vista lateral de 90° muestra ángulos artificialmente bajos (~112° prom) debido a problemas de tracking.

______________________________________________________________________

## 📚 Referencias Técnicas

Basado en:

- `docs/guides/camera-setup.md` - Setup de cámara del proyecto
- `docs/technical/framerate.md` - Análisis de frame rates
- Issue #10 - Validación de ángulo de tobillo CMJ

**Versión:** 2.0 | Diciembre 2025 (Actualizado con hallazgos de validación empírica)
