import pandas as pd
import requests
import os

def ingest_data(api_url, sales_path, inventory_path, output_path):
    """Descarga datos del API, carga CSV locales y guarda todo en Parquet."""
    os.makedirs(output_path, exist_ok=True)

    # --- Datos del API ---
    response = requests.get(api_url)
    response.raise_for_status()
    products = response.json()
    df_api = pd.DataFrame(products)
    df_api.to_parquet(f"{output_path}/products.parquet", index=False)

    # --- CSV locales ---
    df_sales = pd.read_csv(sales_path)
    df_inventory = pd.read_csv(inventory_path)
    df_sales.to_parquet(f"{output_path}/sales.parquet", index=False)
    df_inventory.to_parquet(f"{output_path}/inventory.parquet", index=False)

    return df_api, df_sales, df_inventory
