import pandas as pd

def run_quality_checks(df: pd.DataFrame):

    # Verificar precios negativos
    precios_ok = (df["price"] >= 0).all()

    #  Validar que stock sea número entero positivo
    stock_ok = df["current_stock"].apply(lambda x: isinstance(x, (int, float)) and x >= 0).all()

    # Confirmar que todas las categorías existan
    categorias_ok = df["category"].notna().all() and (df["category"] != "").all()

    #  Verificar que fechas de venta sean válidas

    if "sale_date" in df.columns:
        try:
            pd.to_datetime(df["sale_date"], errors="raise")  # Lanza error si alguna fecha es inválida
            fechas_ok = True
        except Exception:
            fechas_ok = False
    elif "date" in df.columns:
        try:
            pd.to_datetime(df["date"], errors="raise")
            fechas_ok = True
        except Exception:
            fechas_ok = False
    else:
        # Si no existe la columna de fecha, se considera que el test no pasa
        fechas_ok = False

    # --- Resultados de todos los tests ---
    tests = {
        "precios_no_negativos": precios_ok,
        "stock_entero_positivo": stock_ok,
        "categorias_existentes": categorias_ok,
        "fechas_validas": fechas_ok
    }

    passed = all(tests.values())

    # --- Mensaje informativo en consola ---
    if passed:
        print(" Todos los tests de calidad pasaron correctamente.")
    else:
        print(" Algunos tests de calidad fallaron:")
        for test, result in tests.items():
            if not result:
                print(f"   {test}")

    return passed, tests
