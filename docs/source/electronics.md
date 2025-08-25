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

---

# Documentación técnica — Sensores NO₂ / CH₄ / H₂S / 

## Índice

1. Resumen ejecutivo
2. Criterios de clasificación (Clase A / B / C)
3. Recomendaciones por gas (NO₂, CH₄, H₂S) — 3 opciones cada uno
4. Circuitos de lectura y bloques funcionales
5. Diseño de PCB y cuidados ambientales
6. Integración con Jetson Nano (arquitectura y protocolo)
7. BOM orientativo (precios estimados)
8. Procedimientos operativos mínimos
9. Anexos técnicos (esquemas TIA / bridge)
10. Referencias y enlaces

---

## 1. Resumen ejecutivo

* Priorizar sensores industriales (Clase A/B) para pruebas en galería y piloto. Electroquímicos (NO₂, H₂S) y NDIR/IR (CH₄/CO₂) son los más fiables. MOX/MQ útiles solo para prototipado y mapeo no crítico.
* Arquitectura recomendada: **Sensor heads → PCB front‑end (TIA / bridge / transmitter) → MCU (ESP32/STM32) → Jetson Nano**. Jetson no tiene ADC integrado.
* PCB y carcasa deben ser IP65–IP67, con protección EMI, conformal coating y montaje antivibración.

---

## 2. Criterios de clasificación

* **Clase A**: sensores industriales / detectores certificados. Recomendados para pruebas reales y exigencias de seguridad.
* **Clase B**: sensores OEM / heads compactos (buena relación coste/fiabilidad). Requieren acondicionamiento electrónico.
* **Clase C**: módulos low‑cost (MQ/MOX, breakouts). Solo I+D y prototipado.

---

## 3. Recomendaciones por gas (3 opciones por gas)

### A) NO₂ (dióxido de nitrógeno)

**Clase A — Alphasense NO₂‑B43F (electroquímico)**

* Tipo: electroquímico amperométrico.
* Rango & rendimiento: ppb → ppm (ver datasheet); T₉₀ en decenas de segundos.
* Salida: corriente (µA) → TIA necesaria.
* Precio estimado: **USD 80–200** (varía por distribuidor).
* Uso: montaje en caja ventilada con difusor; TIA + ADC; bump tests periódicos.
* Notas: la celda sola no es certificación ATEX/IS — el montaje final debe certificarse si aplica.

**Clase B — SPEC Sensors NO₂ (módulo OEM)**

* Tipo: electroquímico/printed film según modelo.
* Precio estimado: **USD 20–80**.
* Uso: similar a A pero más económico; ideal para integrar en transmitter.

**Clase C — MiCS‑6814 (MOX breakout)**

* Tipo: MOX multigas (NO₂/CO/NH₃).
* Precio estimado: **USD 20–35**.
* Uso: prototipado; requiere control de calefactor y no es fiable para alarmas críticas.

---

### B) CH₄ (metano / gases inflamables / LEL)

**Clase A — Honeywell Sensepoint XCD (IR CH₄)**

* Tipo: IR/NDIR para hidrocarburos.
* Rango: 0–100% LEL (configurable).
* Salida: 4–20 mA, Modbus/RS‑485, relés.
* Precio estimado: **USD 750–1,500+** (detector completo / heads).
* Ventajas: no se envenena, funciona con bajo O₂; ideal para seguridad.

**Clase B — Pellistor (Amphenol / SGX VQ series)**

* Tipo: pellistor catalítico (LEL).
* Precio estimado: **USD 55–150** por cabezal.
* Ventajas: económico y robusto; requiere O₂; susceptible a envenenamiento.

**Clase C — Figaro TGS2611 (MOX methane)**

* Tipo: MOX semiconductor.
* Precio estimado: **USD 8–35**.
* Uso: mapeo y algoritmos de búsqueda; NO para seguridad crítica.

---

### C) H₂S (sulfuro de hidrógeno)

**Clase A — Alphasense H2S‑AE (electroquímico)**

* Tipo: electroquímico amperométrico.
* Rango: ppm industriales (ver datasheet).
* Precio estimado: **USD 100–200**.
* Uso: TIA + ADC; carcasa protegida; bump tests y recambio programado.

**Clase B — SPEC Sensors H2S (OEM module)**

* Precio estimado: **USD 20–70**.
* Uso: integración compacta en transmitter.

**Clase C — DFRobot / MEMS SEN0568 (breakout)**

* Precio estimado: **USD 5–30**.
* Uso: prototipado y pruebas de algoritmo.

---

## 4. Circuitos de lectura y bloques funcionales

### Bloque general recomendado

```
Sensor heads  ->  Front-end PCB (TIA / bridge / NDIR UART)  ->  MCU (ESP32/STM32) with ADC  ->  Jetson Nano (UART / CAN / Ethernet)
```

### Electroquímicos (NO₂, H₂S)

* Señal: corriente (nA–µA). Se usa **Transimpedance Amplifier (TIA)** para convertir I->V.
* Vref recomendable: Vcc/2 (por ejemplo 1.65 V con 3.3 V) para permitir diferencial.
* ADC recomendado: ADS1115 (16‑bit) básico; ADS1248 / ADS1299 para mayor resolución.
* MCU: ESP32/STM32 para lectura y envío al Jetson.

**Ejemplo TIA (concepto):**

* Vout = Vref + I\_sensor \* Rf
* Elegir Rf según sensibilidad del sensor y rango.
* Op‑amp recomendado: LMP7721 / ADA4528 / OPA376 (baja corriente/ruido).

### Pellistor (CH₄ LEL)

* Acondicionamiento: puente Wheatstone -> amplificador diferencial (INA / AD8226) -> ADC.
* Alternativa robusta: usar transmitter 4–20 mA y leer shunt en MCU.

### NDIR / IR (CH₄ / CO₂)

* Interfaz: UART / analógico / I2C según módulo.
* Muestreo activo: considerar micropump si el ambiente tiene poco flujo.

### MOX / MQ (prototoipos)

* Señal: resistencia variable -> leer en divisor resistivo -> ADC.
* Calefactor: driver MOSFET + PWM. Warm‑up requerido.

---

## 5. Diseño de PCB y cuidados ambientales

* **Carcasa:** IP65–IP67, mallas sinterizadas / membranas hidrofóbicas para entradas de gas.
* **Vibración:** pads antivibración, conectores M12 o industriales.
* **Polvo / corrosión:** conformal coating (no aplicar en ventana/óptica), conectores sellados.
* **EMI / ruido:** separación analog/digital GND, ferrite beads, filtros LC, decoupling cercano a IC.
* **Protecciones:** TVS, fusibles, PTC, protección contra inversión de polaridad.
* **Sensor T/H:** integrar SHT3x o similar para compensación.
* **Layout:** rutas cortas desde sensor al TIA, guard ring para entradas de alta impedancia.

---

## 6. Integración con Jetson Nano (arquitectura y protocolo)

* MCU intermedio (ESP32/STM32) realiza adquisición, calibración y packaging.
* Comunicación: UART/USB‑serial, CAN (recomendado para entornos ruidosos) o RS‑485/Modbus si transmitters.
* Formato de paquete sugerido (JSON simple) con timestamp, pose y lecturas.
* Frecuencia mínima: 1 Hz; en eventos críticos enviar inmediato.

---

## 7. BOM orientativo (precios estimados)

> Ver sección 3 para lista por gas. Resumen de componentes clave:

* Sensores NO₂: Alphasense NO₂‑B43F (USD 80–200), SPEC NO₂ (USD 20–80), MiCS‑6814 (USD 20–35)
* Sensores CH₄: Honeywell Sensepoint XCD IR (USD 750–1,500+), Pellistor VQ series (USD 55–150), Figaro TGS2611 (USD 8–35)
* Sensores H₂S: Alphasense H2S‑AE (USD 100–200), SPEC H2S (USD 20–70), DFRobot MEMS (USD 5–30)
* ADCs: ADS1115 (USD \~10), ADS1248 (\~USD 30–60)
* Op‑amps: LMP7721 / ADA4528 (USD 2–6)
* MCU: ESP32 dev kit (USD 5–15) o STM32 dev kits (USD 7–20)
* Otros: TVS, ferritas, fusibles, mallas sinterizadas, conectores M12, cajas IP (USD 50–200)

> **Nota:** confirmar precios exactos en Mouser/DigiKey/GasLab y distribuidores locales.

---

## 8. Procedimientos operativos mínimos

1. **Bump test** antes de cada jornada / misión crítica.
2. **Calibración formal** cada 6–12 meses según sensor y condiciones.
3. **Pruebas ambientales**: polvo, humedad y vibración antes de galería.
4. **Registro**: almacenar lecturas con timestamps + pose.
5. **Plan de repuestos**: stock mínimo 2x celdas EC por gas crítico.
6. **Acción ante alarma**: robot se detiene, marca posición y notifica operador.

---

## 9. Anexos técnicos (esquemas rápidos)

### A) Esquema TIA (texto)

```
Sensor EC (Iout) --> TIA (OpAmp LMP7721)
  - Non-inv input = Vref (1.65V)
  - Inverting node = Sensor current summing node
  - Feedback Rf (ej. 50kΩ-200kΩ) -> Cf (10nF)
Vout = Vref + I_sensor*Rf -> RC antialias -> ADC (ADS1115) -> MCU
```

### B) Pellistor bridge (texto)

```
Pellistor active + reference -> Wheatstone Bridge -> INA differential amplifier -> LPF -> ADC
Alternative: use 4-20mA transmitter -> read shunt resistor at MCU ADC
```

---

## 10. Referencias y enlaces útiles

* Alphasense: [https://www.alphasense.com](https://www.alphasense.com)
* SPEC Sensors: [https://spec-sensors.com](https://spec-sensors.com)
* Honeywell Analytics / Sensepoint XCD: [https://sps.honeywell.com](https://sps.honeywell.com)
* Amphenol / SGX: [https://www.amphenol-sensors.com](https://www.amphenol-sensors.com)
* Figaro: [https://www.figaro.co.jp/en/](https://www.figaro.co.jp/en/)
* Senseair K30: [https://senseair.com](https://senseair.com)
* DFRobot / SparkFun: [https://www.dfrobot.com](https://www.dfrobot.com) / [https://www.sparkfun.com](https://www.sparkfun.com)
* Mouser / DigiKey / Farnell / RS: [https://www.mouser.com](https://www.mouser.com) / [https://www.digikey.com](https://www.digikey.com) / [https://www.farnell.com](https://www.farnell.com) / [https://es.rs-online.com](https://es.rs-online.com)
* Analog Devices app notes (TIA/ADC interfacing): [https://www.analog.com](https://www.analog.com)

=======

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