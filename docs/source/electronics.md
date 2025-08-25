# Electrónica

El presente informe describe los sensores seleccionados para la detección de **CO, SO₂ y O₂**, organizados en tres gamas (A, B y C).  
La clasificación es la siguiente:  

- **Clase A** → Máxima calidad, seguridad y confiabilidad (uso industrial/minero).  
- **Clase B** → Buen balance entre costo y precisión (prototipos avanzados y pruebas en campo).  
- **Clase C** → Bajo costo, uso en prototipos simples y pruebas preliminares.  

El objetivo es garantizar que el cuadrúpedo pueda detectar gases peligrosos en minas y asistir en la búsqueda de trabajadores atrapados o en riesgo.

---

## 1. Monóxido de Carbono (CO)

### Clase A: Alphasense CO-A4
- **Tipo:** Celda electroquímica de grado industrial.  
- **Rango típico:** 0 – 1000 ppm.  
- **Precisión:** Alta sensibilidad (±2% lectura).  
- **Ventaja clave:** Estabilidad a largo plazo y bajo ruido.  

### Clase B: SPEC Sensors 3SP-CO-1000
- **Tipo:** Sensor electroquímico de montaje fácil.  
- **Rango:** 0 – 1000 ppm.  
- **Tiempo de respuesta (t90):** < 30 s.  
- **Ventaja:** Ideal para integración con microcontroladores y plataformas IoT.  

### Clase C: MQ-7
- **Tipo:** Sensor semiconductor de óxido metálico.  
- **Rango:** 20 – 2000 ppm.  
- **Consumo:** Mayor consumo eléctrico (requiere calentador).  
- **Ventaja:** Muy económico y fácil de implementar en prototipos.  

---

## 2. Dióxido de Azufre (SO₂)

### Clase A: Alphasense SO2-A4
- **Tipo:** Sensor electroquímico de alta precisión.  
- **Rango:** 0 – 50 ppm.  
- **Sensibilidad:** ~ 320–500 nA/ppm a 2 ppm SO₂.  
- **Ventaja:** Alta confiabilidad en ambientes mineros hostiles.  

### Clase B: SPEC Sensors 3SP-SO2-20
- **Tipo:** Electroquímico compacto para integración IoT.  
- **Rango:** 0 – 20 ppm.  
- **Tiempo de respuesta (t90):** < 30 s.  
- **Ventaja:** Bajo costo comparado con la gama A y fácil integración en PCBs.  

*(No se seleccionó Clase C por baja disponibilidad y confiabilidad en SO₂ para aplicaciones reales de seguridad)*  

---

## 3. Oxígeno (O₂)

### Clase A: Alphasense O2-A2
- **Tipo:** Sensor electroquímico industrial.  
- **Rango:** 0 – 25% vol. O₂.  
- **Precisión:** ±0.1% vol. O₂.  
- **Ventaja:** Alta confiabilidad, cumple normas de seguridad minera.  

### Clase B: Winsen ME2-O2
- **Tipo:** Sensor electroquímico de costo medio.  
- **Rango:** 0 – 25% vol. O₂.  
- **Tiempo de respuesta:** < 15 s.  
- **Ventaja:** Buen balance costo/precisión, fácil integración con microcontroladores.  

*(No se seleccionó Clase C para O₂ debido a la criticidad de medir correctamente este gas vital)*  

---

## 4. Dióxido de Carbono (CO₂)

### Clase A: Sensirion SCD41
- **Tipo:** Sensor NDIR (infrarrojo no dispersivo) de alta precisión.  
- **Rango:** 400 – 5000 ppm.  
- **Precisión:** ±(40 ppm + 5% de la lectura).  
- **Ventaja:** Incluye compensación automática de temperatura y humedad, bajo consumo y tamaño compacto.  
- **Ideal para:** Monitoreo confiable en espacios cerrados como minas.  

*(No se consideraron versiones B ni C, ya que el CO₂ en entornos mineros requiere mediciones confiables y seguras. El SCD41 es el estándar recomendado.)*  

---

# Conclusiones

- **Clase A**: Recomendados para la **versión final** del cuadrúpedo minero, ya que ofrecen confiabilidad y seguridad en entornos hostiles.  
- **Clase B**: Útiles para **prototipos avanzados** y pruebas de integración con Jetson o microcontroladores.  
- **Clase C**: Solo recomendados para **etapa inicial de pruebas** debido a su baja precisión y confiabilidad en condiciones mineras reales.  
