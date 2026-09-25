# % captado por habitualistas — Córdoba (DNRPA)

Indicador mensual para la provincia de Córdoba:

| columna | definición |
|---|---|
| `transferencias_totales` | filas del dataset DNRPA *Transferencias de autos* con `registro_seccional_provincia` = CORDOBA, cualquier `tramite_tipo` |
| `transferencias_habitualistas` | las mismas filas con `tramite_tipo` de transferencia **a** comerciante habitualista: en el dataset figura abreviado como `A COM. HAB.` (`TRANSFERENCIA NACIONAL A COM. HAB. F17`, `TRANSFERENCIA IMPORTADO A COM. HAB. F17 C/PEDIDO.`, etc.). Los tipos `DE COM. HAB.` (vende el comerciante) cuentan en el total pero no en el numerador |
| `porcentaje_habitualistas` | habitualistas / totales × 100 |

El mes sale de `tramite_fecha`. El % acumulado de un período es Σ habitualistas / Σ totales, no el promedio de los porcentajes mensuales.

**Qué mide:** qué parte de las transferencias inscriptas en Córdoba tuvo como comprador a un comerciante habitualista, es decir, vehículos que entran formalmente al stock de reventa.
**Qué no mide:** las ventas de las agencias a consumidores finales, las compras informales de agencias que no usan la figura de habitualista, ni la cantidad de vehículos distintos (una fila = un trámite; el dataset no trae dominio).

## Fuente

Sólo DNRPA / Ministerio de Justicia: <https://datos.jus.gob.ar/dataset/transferencias-de-autos>.
El script lista los recursos con la API CKAN (`package_show?id=transferencias-de-autos`) y descarga los `dnrpa-transferencias-autos-AAAAMM.csv` del período. En `data/raw/manifest.json` guarda URL, fecha y SHA-256 de cada archivo.

## Uso (y actualización mensual)

```bash
pip install -r analisis_dnrpa/requirements.txt
python analisis_dnrpa/dnrpa_habitualistas_cordoba.py                     # 2025-01 .. lo último publicado
python analisis_dnrpa/dnrpa_habitualistas_cordoba.py --hasta 2026-09     # tope explícito
python analisis_dnrpa/dnrpa_habitualistas_cordoba.py --solo-local        # CSV ya bajados a data/raw/
```

Cada vez que se corre, descarga sólo los meses nuevos y regenera todo en `output/`:

- `habitualistas_cordoba_mensual.csv` (anio, mes, transferencias_totales, transferencias_habitualistas, porcentaje_habitualistas)
- `habitualistas_cordoba_resumen.csv`: total por año, acumulado 2026, % acumulado y promedio simple
- `mercado_habitualistas_cordoba_2025_2026.xlsx`: hojas Resumen, Mensual, Datos - control y Metodología
- `grafico_pct_habitualistas.png`, `grafico_totales_vs_habitualistas.png`
- `validacion_externa_2025.csv`: comparación con los totales de referencia (sólo sanity check)
- `control_calidad.json`, `informe.md`: estructura detectada (encoding, separador, columnas, formato de fecha), todos los `tramite_tipo`, variantes de Córdoba, duplicados, nulos, tipos de comerciante habitualista (`COM. HAB.`) y cuáles entran en el numerador, CSV mensuales repetidos (sueltos y dentro del ZIP anual; se leen una sola vez), tipos que parezcan anulaciones o rectificaciones, y la comprobación de que el numerador está incluido en el denominador

Las filas duplicadas exactas **se informan pero no se eliminan** por defecto, porque el dataset no tiene ID y dos trámites reales pueden coincidir en todas las columnas. `--eliminar-duplicados` las descarta.

## Prueba

`python analisis_dnrpa/tests/test_pipeline_sintetico.py` corre el pipeline con datos **sintéticos** para verificar la lógica. No produce resultados reales.
