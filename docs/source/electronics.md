# Electrónica — Sensores y batería para el cuadrupedo minero

**Resumen:** este informe recoge la selección recomendada de sensores para detección de gases (CO, SO₂, O₂, CO₂ y otros), la clasificación por gamas (A/B/C), bloques de acondicionamiento, consideraciones de PCB/carcasa, integración con el procesamiento (Jetson Nano + MCU) y procedimientos operativos. Incluye además una sección dedicada a la elección de la batería.

---

## Clasificación (Clase A / B / C)

- **Clase A** — Máxima calidad, seguridad y confiabilidad. Recomendados para uso industrial/minero y versiones finales del robot.  
- **Clase B** — Buen balance costo/precisión. Idóneos para prototipos avanzados y pruebas de campo.  
- **Clase C** — Bajo costo. Solo para I+D, prototipado y mapeo no crítico.

**Objetivo:** garantizar detección fiable de gases peligrosos en galerías y asistir en búsqueda/evacuación.

---

## 1. Detección por gas

### 1.1 Monóxido de Carbono (CO)
- **Clase A — Alphasense CO-A4**  
  Tipo: celda electroquímica industrial. Rango: 0–1000 ppm. Precisión: alta (≈±2%). Ventaja: estabilidad a largo plazo y bajo ruido.
- **Clase B — SPEC Sensors 3SP-CO-1000**  
  Tipo: electroquímico compacto. Rango: 0–1000 ppm. t90 < 30 s. Fácil integración con MCU/IoT.
- **Clase C — MQ-7**  
  Tipo: MOX (óxido metálico). Rango: 20–2000 ppm. Requiere calentador (más consumo). Uso: prototipos y mapeo.

---

### 1.2 Dióxido de Azufre (SO₂)
- **Clase A — Alphasense SO2-A4**  
  Tipo: electroquímico de alta precisión. Rango: 0–50 ppm. Sensibilidad ≈ 320–500 nA/ppm. Recomendado para ambiente minero.
- **Clase B — SPEC Sensors 3SP-SO2-20**  
  Tipo: electroquímico compacto. Rango: 0–20 ppm. t90 < 30 s. Buena opción económica para integración.
- **Clase C** — No seleccionada por baja disponibilidad/confiabilidad para aplicaciones de seguridad.

---

### 1.3 Oxígeno (O₂)
- **Clase A — Alphasense O2-A2**  
  Tipo: electroquímico industrial. Rango: 0–25% vol. Precisión: ±0.1% vol. Cumple normas de seguridad minera.
- **Clase B — Winsen ME2-O2**  
  Tipo: electroquímico de costo medio. Rango: 0–25% vol. t90 < 15 s. Buen balance costo/precisión.
- **Clase C** — No recomendada por la criticidad de medir O₂ correctamente.

---

### 1.4 Dióxido de Carbono (CO₂)
- **Clase A — Sensirion SCD41 (NDIR)**  
  Tipo: NDIR de alta precisión. Rango: 400–5000 ppm. Precisión: ±(40 ppm + 5% lectura). Incluye compensación T/H. Recomendado como estándar; no se consideraron versiones B/C por seguridad/fiabilidad.

---

## 2. Sensores adicionales (NO₂, CH₄, H₂S)

### NO₂
- **A — Alphasense NO₂-B43F** (electroquímico). Salida en corriente → TIA necesaria. Precio estimado USD 80–200.
- **B — SPEC Sensors NO₂** (módulo OEM). USD 20–80.
- **C — MiCS-6814** (MOX multigas). USD 20–35. Solo prototipado.

### CH₄ (gases inflamables / LEL)
- **A — Honeywell Sensepoint XCD (IR/NDIR)**: detector completo, salidas 4–20 mA / Modbus. Muy robusto; precio elevado.
- **B — Pellistor (Amphenol / SGX VQ)**: cabezal pellistor. Económico, necesita O₂ y puede "envenenarse".
- **C — Figaro TGS2611 (MOX)**: barato, solo para mapeo/no crítico.

### H₂S
- **A — Alphasense H2S-AE** (electroquímico). Alta fiabilidad industrial.
- **B — SPEC Sensors H2S** (módulo OEM).
- **C — Breakout DFRobot / MEMS** (prototipado).

---

## 3. Bloques de lectura y arquitectura recomendada

### Arquitectura general recomendada
```

Sensor heads -> Front-end PCB (TIA / bridge / NDIR driver) -> MCU (ESP32/STM32) con ADC -> Jetson Nano (procesamiento, visión)

```
- Separar adquisición y preprocesado en MCU intermedio (calibración, filtros, empaquetado).
- Comunicación: UART/USB-serial, CAN (recomendado en entornos ruidosos), RS-485/Modbus para transmitters.

### Electroquímicos (NO₂, H₂S, CO, SO₂)
- Señal: corriente (nA–µA). Usar **Transimpedance Amplifier (TIA)**.  
- Vref: Vcc/2 (ej. 1.65 V con 3.3 V) para permitir swings diferenciales.  
- ADC recomendados: ADS1115 (16-bit) para básicos; ADS1248/ADS1299 para mayor resolución.  
- Op-amps sugeridos (baja fuga/ruido): LMP7721, ADA4528, OPA376.

### Pellistor (LEL)
- Condicionamiento: puente Wheatstone -> amplificador diferencial (INA/AD8226) -> LPF -> ADC.  
- Alternativa: usar transmitter 4–20 mA y medir a través de shunt.

### NDIR / IR (CO₂, CH₄)
- Interfaz: UART/I²C/analógico según módulo. Considerar micropump para muestreo activo en baja convección.

### MOX / MQ (prototoipos)
- Señal: variación de resistencia. Driver del calefactor por MOSFET + PWM; warm-up necesario.

---

## 4. Diseño de PCB y consideraciones ambientales

- Carcasa IP65–IP67; usar mallas sinterizadas o membranas hidrofóbicas en entradas de gas.  
- Protección contra vibración: pads antivibración; conectores M12.  
- Protección contra polvo/corrosión: conformal coating (evitar ventana óptica).  
- EMI: separación analog/digital GND, guard rings, ferrite beads, filtros LC y decoupling próximo a IC.  
- Protecciones: TVS, fusibles, PTC, protección contra inversión de polaridad.  
- Layout: rutas cortas desde sensor al TIA; guard ring para entradas de alta impedancia.  
- Integrar sensor T/H (ej. SHT3x) para compensación.

---

## 5. Integración con Jetson Nano (arquitectura y protocolos)

- MCU intermedio (ESP32/STM32) hace adquisición, calibración y envía paquetes al Jetson.  
- Protocolos: UART/USB-serial, CAN (preferible en ruido), RS-485/Modbus si transmitters.  
- Formato: JSON simple con timestamp, pose y lecturas.  
- Frecuencia mínima recomendada: 1 Hz; en eventos críticos enviar mensajes inmediatos.

---

## 6. BOM orientativo (resumen)
- Sensores NO₂, CH₄, H₂S: ver sección 2.  
- ADCs: ADS1115 (~USD 10), ADS1248 (~USD 30–60).  
- Op-amps: LMP7721 / ADA4528 (~USD 2–6).  
- MCU: ESP32 dev kit (USD 5–15) o STM32 dev kit (USD 7–20).  
- Otros: TVS, ferritas, fusibles, mallas sinterizadas, conectores M12, cajas IP (USD 50–200).  

---

## 7. Procedimientos operativos mínimos (MOP)
1. **Bump test** antes de cada jornada o misión crítica.  
2. **Calibración formal** cada 6–12 meses según sensor y condiciones.  
3. **Pruebas ambientales**: polvo, humedad y vibración antes de galería.  
4. **Registro**: almacenar lecturas con timestamps y pose.  
5. **Plan de repuestos**: stock mínimo 2× celdas electroquímicas por gas crítico.  
6. **Acción ante alarma**: robot detiene misión, marca posición y notifica operador.

---

## 8. Anexos técnicos (esquemas rápidos)

### A) Esquema TIA (concepto)
```

Sensor EC (Iout) --> TIA (OpAmp LMP7721)

* Non-inv input = Vref (1.65 V)
* Inverting node = sensor current summing node
* Feedback Rf (ej. 50kΩ–200kΩ) -> Cf (10 nF)
  Vout = Vref + I\_sensor \* Rf -> RC anti-alias -> ADC (ADS1115) -> MCU

```

### B) Pellistor bridge (concepto)
```

Pellistor activo + referencia -> Wheatstone Bridge -> INA differential amp -> LPF -> ADC
Alternativa: transmitter 4–20 mA -> leer shunt en MCU ADC

```

---

## 9. Referencias y enlaces útiles
- Alphasense, SPEC Sensors, Honeywell Sensepoint, Amphenol/SGX, Figaro, Sensirion, Mouser, DigiKey, Analog Devices (app notes TIA/ADC).
---

# Elección de la batería (sección dedicada)

## 1 — Resumen ejecutivo

* Objetivo: **1 h de autonomía** mínima real en el robot con 12 motores Unitree GO-M8010, Jetson Nano, LIDAR, cámaras, 7 sensores de gas, IMU y electrónica adicional.
* Se estudiaron tres familias de packs: **MaxAmps Li-ion 7S8P 25.2 V 40 Ah**, **MaxAmps 7S10P 25.2 V 50 Ah**, y **Power-Sonic LiFePO₄ 25.6 V 40 Ah (PSL-BT-24400-G24)**.
* **Balance de criterios**: energía útil (Wh), capacidad de descarga (A cont./pico), peso/volumen, seguridad química (LiFePO₄ > Li-ion), ciclo de vida y facilidad de integración (BMS, telemetría).
* **Recomendación práctica inicial**: pack **50 Ah Li-ion (25.2 V)** si necesitas robustez ante picos y mayor margen de autonomía; **LiFePO₄ 40 Ah** si priorizas seguridad y ciclo de vida y estás dispuesto a añadir soluciones para picos (paralelo o buffer). Para pruebas en mina, preferir seguridad (LiFePO₄) a menos que el peso/pico sea crítico.

---

## 2 — Requisitos del proyecto y supuestos (inputs usados en cálculos)

* Autonomía objetivo: **1 hora** (mínimo).
* Bus nominal objetivo: **≈25.2 V (Li-ion)** o **25.6 V (LiFePO₄)**.
* Consumos estimados (valores usados en cálculos):

  * Electrónica (sensors, Jetson, LiDAR, cámaras, imu, periferia) ≈ **61 W**.
  * Motores: 12 × (escenarios)

    * Escenario Optimista (A): **30 W/motor** → 360 W total.
    * Escenario Realista (B): **60 W/motor** → 720 W total.
    * Escenario Conservador (C): **100 W/motor** → 1200 W total.
  * Total (B): **Ptot ≈ 781 W** (usado como caso representativo).
* Tensión pack asumida para cálculos: **25.2 V** (li-ion) o **25.6 V** (LiFePO₄).
* Margen de diseño recomendado: **+20%** Ah para envejecimiento/pérdidas.

---

## 3 — Packs analizados (resumen técnico)

> Datos tomados de cotizaciones/SDS/datasheets que suministraste.

### A) MaxAmps Li-ion 7S8P — **25.2 V / 40 Ah (1008 Wh)**

* Peso: ≈ **4.02 kg**
* Max continuous discharge: **200 A**
* Max peak discharge: **640 A** (condición de pulso; confirmar duración)
* Internal impedance (ej. datasheet): **\~21 mΩ**
* Charge rate: 20–40 A (0.5–1C)

### B) MaxAmps Li-ion 7S10P — **25.2 V / 50 Ah (1260 Wh)**

* Peso ≈ **5.02 kg**
* Max continuous discharge: **250 A**
* Mayor autonomía y margen de pico frente al 40 Ah.

### C) Power-Sonic LiFePO₄ PSL-BT-24400-G24 — **25.6 V / 40 Ah (1024 Wh)**

* Peso: ≈ **9.3 kg** (mucho mayor)
* Max continuous discharge: **40 A**
* Química LiFePO₄ → **mejor seguridad térmica y 2000 ciclos** aprox.
* Recomendado en entornos con altos requisitos de seguridad.

---

## 4 — Cálculos paso a paso

### 4.1 Energía del pack (Wh)

* 7S8P 40 Ah Li-ion: `E = 25.2 V × 40 Ah = 1008 Wh`
* 7S10P 50 Ah Li-ion: `E = 25.2 V × 50 Ah = 1260 Wh`
* LiFePO₄ 25.6 V × 40 Ah: `E = 25.6 × 40 = 1024 Wh`

### 4.2 Autonomía estimada (h) = `Epack / Ptot`

Usando caso **Realista (B) Ptot = 781 W**:

* 40 Ah Li-ion: `1008 / 781 = 1.29 h (≈ 1 h 17 min)`
* 50 Ah Li-ion: `1260 / 781 = 1.61 h (≈ 1 h 37 min)`
* 40 Ah LiFePO₄: `1024 / 781 = 1.31 h (≈ 1 h 19 min)`

### 4.3 Corriente promedio en el bus `Iavg = Ptot / Vnom`

Con `Vnom ≈ 25.2 V`:

* Iavg (B) = `781 / 25.2 ≈ 31.0 A`

### 4.4 Pérdidas por resistencia interna `Ploss = I² · Rint`

Ejemplo con Rint = 0.021 Ω (pack MaxAmps):

* En operación promedio (I ≈ 31 A): `Ploss ≈ 31² × 0.021 ≈ 20 W` (moderado)
* A 200 A: `200² × 0.021 = 840 W` (elevado — requiere disipación)
* A picos (480 A): `480² × 0.021 ≈ 4.8 kW` (no sostenible)

**Interpretación:** packs con baja Rint son mejores para picos; aunque el pack declare picos altos, la caída de tensión y disipación térmica limitan duración del pulso. Diseñar buffers y limitar la duración de picos.

### 4.5 Ejemplo dimensionado de celdas (21700 5000 mAh)

Para Pack 25.2 V × 40 Ah (7s8p): `7 series × 8 parallel = 56 celdas`.
Corriente por celda si 31 A pack: `31 / 8 ≈ 3.9 A` → C≈0.78C (aceptable si celda soporta >1C). Para picos, celdas en paralelo ayudan a repartir corriente.

---

## 5 — Comparativa técnica y decisión estratégica

### Ventajas Li-ion MaxAmps (40 / 50 Ah)

* Alta densidad energética → menor peso.
* Alta corriente continua / pico (200–250 A cont.; picos declarados).
* Packs “listos para montar” y upgrades (hard case, balance lead, DroneCAN).

### Inconvenientes Li-ion MaxAmps

* Química NMC / Li-ion → mayor riesgo térmico que LiFePO₄.
* Requiere gestión térmica y plan de emergencia en trabajo de campo (SDS).
* Si esperas picos simultáneos extremos puede necesitar buffer adicional o packs en paralelo.

### Ventajas Power-Sonic LiFePO₄

* Muy segura térmicamente (menor riesgo thermal runaway).
* Ciclo de vida mayor (\~2000 ciclos).
* Menos requisitos de extinción crítica.

### Inconvenientes LiFePO₄ (Power-Sonic)

* **Corriente continua baja** (40 A) → potencia de salida limitada frente a demandas pico de motores; gran **peso** (\~9.3 kg) y volumen.
* Si se desea alta corriente hay que paralelizar packs (2×→80 A) o usar buffer.

### Estrategia práctica

* Si **priorizas seguridad y durabilidad** (pruebas en galerías, posibilidad de atmósferas hostiles): **LiFePO₄** y añadir 1–2 medidas contra picos (paralelo o supercap + control).
* Si **priorizas rendimiento/pesos y picos** (gait performance exigente, terrenos difíciles): **Li-ion 50 Ah** + buffer + buen BMS + contenedor reforzado + medidas de seguridad.
* **Modularidad:** diseñar el pack en **módulos intercambiables** (ej. dos módulos 25.2 V × 20–40 Ah) facilita test y reemplazo.

---

## 6 — Requisitos de integración mínimos (BMS / PDB / protecciones)

### BMS mínimo debe incluir:

* Overcharge, overdischarge, overcurrent (continuous + peak logic), cell balancing, overtemp/undertemp protection, communication (CAN/DroneCAN/UART) preferible.

### Protecciones eléctricas (hardware)

* **Fusible principal** (fast blow) entre pack y PDB: rated ligeramente > corriente operativa máxima esperada.
* **Contactor / pre-charge resistor** para conexión segura al PDB cuando existen capacitores.
* **Precharge resistor** para limitar inrush a capacitores.
* **TVS / varistores** y filtros EMI para proteger electrónica sensible.
* **DC-link capacitors** (low-ESR): `2000–5000 μF` @ 35–50 V cerca de motor drivers para amortiguar pulsos cortos.
* **Cableado y busbar** dimensionado para corrientes pico (recomendado ≥ 50–70 mm² para >200 A).
* **Sección de cable/calc** según norma (por confirmar con mecánica).

### Monitorización y telemetría

* Shunt + ADC o DroneCAN adapter para medir corriente real, SOC, voltaje celda a celda y temp.
* Integrar telemetría al MCU/Jetson para alarmas y logging.

---

## 7 — Gestión de picos (opciones combinadas)

### A) Buffer capacitivo (DC-link)

* `2 000–5 000 μF` low-ESR a 35–50 V por banco, cerca del motor controller, reduce picos instantáneos.

### B) Supercapacitor bank (opcional)

* Para picos repetidos intensos, un banco de supercaps (módulos comerciales de varios F a voltajes bajos con convertidor) puede absorber picos y proteger pack. Costo/volumen altos — usar sólo si pruebas lo justifican.

### C) Estrategia de control (software/hardware)

* **Stagger starts** (no arrancar todas las patas simultáneamente).
* **Limitación de corriente en motor drivers** (rampas de torque).
* **Gestión de gait** que evite picos simultáneos.

### D) Paralelizar packs

* Dos packs iguales en paralelo → disminuye Rint efectiva (≈Rint/2) y duplica corriente continua disponible. Aumenta peso y volumen.

---

## 8 — Gestión térmica (aislamiento y control)

### Objetivos térmicos

* Mantener pack dentro de **15–35 °C** ideal; no cargar bajo 0–5 °C.
* Para ambientes fríos: pre-calentamiento/control. Para calientes: enfriamiento activo.

### Recomendación constructiva

* **Caja hermética IP65/67** con aislamiento (PU foam, 20–30 mm).
* **Heater pads** (silicone) controlados por MCU (PWM a MOSFET), potencia sugerida de referencia: **50 W** para mantenimiento con buen aislamiento; **\~150 W** disponible para precalentamientos cortos.
* **Sensores de temperatura**: 3–4 puntos (centro de pack, extremos, carcasa).
* **Cálculo rápido (ejemplo)**: pack 4 kg, cp \~900 J/kg·K, ΔT=20 K, tiempo 10 min → P ≈ 120 W para subir 20 K en 10 min. Para mantener con 20 mm aislamiento y A≈0.5 m², pérdida ≈15 W. (usar estas fórmulas para afinar).

### Seguridad térmica

* Interruptor hardware (thermal cutoff) a \~60–70 °C.
* Ventilación con filtros o intercambio térmico a través de pared si fuera necesario. **En minas**: no introducir aire del túnel sin evaluación ATEX (use purga con aire limpio o intercambiador barrera).

---

## 9 — Seguridad, SDS y pruebas obligatorias

* Implementar procedimientos de emergencia según SDS: extinción (agua para enfriar packs adyacentes), PPE, contención de electrolito.
* Checklist antes de prueba en campo (ver sección 12).
* Pruebas antes de galería:

  * Charge / discharge test a Iavg y a picos (registrar voltaje, temp).
  * Pulse test: aplicar pulso a corriente pico y medir caída de tensión y temp (controlar que pack no active BMS).
  * Vibration test (en bancada con montaje antivibración).
  * Thermal cycling (cámara climática si posible).
* Verificar transporte (UN3480 etc.) y permisos de la mina.

---

## 10 — BOM mínima orientativa (componentes esenciales)

> No son links, son especificaciones para pedir.

* Batería pack (elegir 40 Ah LiFePO₄ o 40/50 Ah Li-ion MaxAmps) × 1
* BMS (si no incluido o si upgrade requerido) — rating ≥ corriente nominal operativa, support regen.
* Fusible principal (fast blow) — rating = Ioper \* 1.1\~1.5 (ej.: 250–300 A para pack 200 A cont.)
* Contactor DC 600 V / 300–400 A con driver (coil 24 V) + precharge resistor (e.g., 10–50 Ω 50–100 W)
* Capacitores DC-link: 2 × 2200–4700 μF low-ESR @ 35–50 V
* Supercap module (opcional) — especificar F, V (consultar)
* Shunt de medición o sensor de corriente Hall (capaz 200–500 A) + ADC (ADS1115 o mejor)
* Sensor(es) de temperatura NTC/PT100 × 4
* Heaters silicone 24 V 50–150 W + MOSFET driver (logic level)
* TVS diodes / varistors para protección contra transitorios
* Cables de potencia ≥ 50–70 mm² (kupper/busbar) y conectores (Anderson, XT150, M8 studs)
* Case/hardcase (si no incluido) IP65/67 y pads antivibración
* Extintor y detector de humo/CO para banco

---

## 11 — Plan de pruebas en banco (procedimiento resumido)

1. **Inspección visual** del pack y conexiones. Verificar BMS y balance lead.
2. **Carga inicial**: cargar pack a corriente recomendada y verificar temperatura y voltajes por celda.
3. **Descarga a Iavg** (31 A en caso realista) por 1 h, registrar volt/cur/temp/SOC. Confirmar autonomía cercana.
4. **Pulse test**: aplicar picos controlados (ej.: 5 s a 200 A, 10 s a 400 A si pack dice soportar pico) y medir Vdrop y Ploss. Registrar temperatura y comportamiento BMS. **No** repetir largos picos sin intervalos.
5. **Test regeneración**: simular regeneración eléctrica al pack (si el motor/driver lo permite) y observar si BMS soporta.
6. **Vibration test**: shaker o prueba manual de vibración con pack montado como en robot. Ver lecturas y conexión.
7. **Thermal cycle**: simular condiciones frías y calentar con heater para ver control.
8. **Fail test**: simular corte del BMS, fallo del contactor, reconexión y pruebas de emergencia (procedimiento de extinción).

Registrar todo en bitácora (tiempo, condiciones, gráfico).

---

---

## 10. Conclusiones generales
- **Clase A**: usar en versión final y pruebas en galería (sensores industriales electroquímicos/NDIR).  
- **Clase B**: buen equilibrio para pruebas avanzadas y validación en campo.  
- **Clase C**: solo I+D y prototipado; no para seguridad.  
- Diseñar front-end (TIA, bridges) con cuidado de ruido y layout; implementar procedimientos de bump test y calibración.  
- **Batería**: dimensionarla a partir de consumos reales medidos en banco; preferir LFP para minería por estabilidad y seguridad si el peso lo permite.
