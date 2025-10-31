import pandas as pd

def run_quality_checks(df: pd.DataFrame, qc_cfg: dict = None):
    """Ejecuta pruebas de control de calidad sobre el DataFrame final."""

    tests = {
        "precios_no_negativos": (df["price"] >= 0).all(),
        "stock_valido": (df["current_stock"].apply(lambda x: isinstance(x, (int, float)) and x >= 0)).all(),
        "categorias_no_nulas": df["category"].notna().all()
    }

    passed = all(tests.values())

    if passed:
        print(" Todos los tests de calidad pasaron correctamente.")
    else:
        print(" Algunos tests de calidad fallaron:")
        for test, result in tests.items():
            if not result:
                print(f"    {test}")

    return passed, tests
