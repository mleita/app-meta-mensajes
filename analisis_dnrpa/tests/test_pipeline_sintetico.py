"""Prueba de la lógica con datos SINTÉTICOS (no son datos reales de DNRPA).

  python analisis_dnrpa/tests/test_pipeline_sintetico.py
"""
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import pandas as pd

SCRIPT = Path(__file__).resolve().parents[1] / "dnrpa_habitualistas_cordoba.py"
TIPOS_A_HAB = ["TRANSFERENCIA NACIONAL A COM. HAB. F17", "TRANSFERENCIA IMPORTADO A COM. HAB  C/PEDIDO.",
               "TRANSFERENCIA A COMERCIANTE HABITUALISTA"]
COLS = ["tramite_tipo", "tramite_fecha", "fecha_inscripcion_inicial", "registro_seccional_codigo",
        "registro_seccional_descripcion", "registro_seccional_provincia", "automotor_origen",
        "automotor_anio_modelo", "automotor_marca_descripcion", "automotor_modelo_descripcion"]


def fila(tipo, fecha, prov, i):
    return [tipo, fecha, "2015-01-01", str(i), "REG", prov, "N", "2015", "MARCA", f"MOD{i}"]


def main():
    tmp = Path(tempfile.mkdtemp())
    raw, out = tmp / "raw", tmp / "out"
    raw.mkdir()
    esperado = {}
    i = 0
    for anio, mes in [(2025, 1), (2025, 2), (2026, 1)]:
        filas = []
        f = f"{anio}-{mes:02d}-10"
        tot, hab = 10 + mes, 3
        for k in range(tot - hab):
            i += 1
            filas.append(fila("TRANSFERENCIA NACIONAL", f, "Córdoba" if k % 2 else "CORDOBA ", i))
        for tipo in TIPOS_A_HAB[:hab]:  # variantes reales abreviadas: todas al numerador
            i += 1
            filas.append(fila(tipo, f, "CORDOBA", i))
        i += 1
        filas.append(fila("TRANSFERENCIA NACIONAL A COM. HAB. F17", f, "SANTA FE", i))  # otra provincia
        i += 1
        filas.append(fila("TRANSFERENCIA NACIONAL  DE COM. HAB. C/PEDIDO", f, "CORDOBA", i))  # vende: sí en total
        filas.append(filas[0])  # duplicado exacto: se informa, no se elimina por defecto
        esperado[(anio, mes)] = (tot + 2, hab)
        pd.DataFrame(filas, columns=COLS).to_csv(raw / f"dnrpa-transferencias-autos-{anio}{mes:02d}.csv",
                                                  index=False)

    # el último mes también viene dentro del ZIP anual (como publica DNRPA): no debe contarse dos veces
    with zipfile.ZipFile(raw / "dnrpa-transferencias-autos-2026.zip", "w") as z:
        z.write(raw / "dnrpa-transferencias-autos-202601.csv", "dnrpa-transferencias-autos-202601.csv")

    subprocess.run([sys.executable, str(SCRIPT), "--solo-local", "--raw-dir", str(raw), "--out-dir", str(out)],
                   check=True)
    m = pd.read_csv(out / "habitualistas_cordoba_mensual.csv")
    assert list(m.columns) == ["anio", "mes", "transferencias_totales", "transferencias_habitualistas",
                               "porcentaje_habitualistas"]
    for r in m.itertuples():
        assert (r.transferencias_totales, r.transferencias_habitualistas) == esperado[(r.anio, r.mes)], r
    ctrl = json.loads((out / "control_calidad.json").read_text())["control"]
    assert ctrl["filas_duplicadas_exactas"] == 3
    assert set(ctrl["tipos_numerador"]) == set(TIPOS_A_HAB)
    assert set(ctrl["tipos_comerciante_habitualista"]) == set(TIPOS_A_HAB) | {
        "TRANSFERENCIA NACIONAL  DE COM. HAB. C/PEDIDO"}
    assert [(o["archivo"], o["identico"]) for o in ctrl["csv_repetidos_omitidos"]] == [
        ("dnrpa-transferencias-autos-202601.csv", True)]
    assert ctrl["numerador_subconjunto_denominador"]
    r = pd.read_csv(out / "habitualistas_cordoba_resumen.csv")
    per = r[r.periodo == "Período completo"].iloc[0]
    assert per.transferencias_habitualistas == 9 and per.transferencias_totales == sum(t for t, _ in esperado.values())
    for f in ("mercado_habitualistas_cordoba_2025_2026.xlsx", "grafico_pct_habitualistas.png",
              "grafico_totales_vs_habitualistas.png", "informe.md"):
        assert (out / f).exists(), f
    print("OK — prueba sintética superada")


if __name__ == "__main__":
    main()
