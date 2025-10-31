import pandas as pd

def transform_data(df_api, df_sales, df_inventory):
    """
    Une datos y genera métricas de negocio.
    
    Args:
        df_api: DataFrame con productos de la API (id, title, price, category)
        df_sales: DataFrame con ventas (product_id, quantity, sale_date, cost)
        df_inventory: DataFrame con inventario (product_id, current_stock, [min_stock opcional])
    
    Returns:
        dict con 'merged', 'stock_critico', 'top_productos', 'ventas_categoria'
    """
    
    # --- 1. NORMALIZAR NOMBRES DE COLUMNAS ---
    df_api.columns = [c.lower().strip() for c in df_api.columns]
    df_sales.columns = [c.lower().strip() for c in df_sales.columns]
    df_inventory.columns = [c.lower().strip() for c in df_inventory.columns]
    
    # --- 2. ESTANDARIZAR NOMBRE DE CLAVES ---
    if "id" in df_api.columns:
        df_api.rename(columns={"id": "product_id"}, inplace=True)
    
    # --- 3. VERIFICAR COLUMNAS CRÍTICAS ---
    required_api = ["product_id", "title", "price", "category"]
    required_sales = ["product_id", "quantity"]
    required_inventory = ["product_id", "current_stock"]
    
    missing_api = [c for c in required_api if c not in df_api.columns]
    missing_sales = [c for c in required_sales if c not in df_sales.columns]
    missing_inventory = [c for c in required_inventory if c not in df_inventory.columns]
    
    if missing_api:
        raise ValueError(f" Faltan columnas en df_api: {missing_api}. Disponibles: {df_api.columns.tolist()}")
    if missing_sales:
        raise ValueError(f" Faltan columnas en df_sales: {missing_sales}. Disponibles: {df_sales.columns.tolist()}")
    if missing_inventory:
        raise ValueError(f" Faltan columnas en df_inventory: {missing_inventory}. Disponibles: {df_inventory.columns.tolist()}")
    
    print(f"✓ df_api: {len(df_api)} productos, columnas: {df_api.columns.tolist()}")
    print(f"✓ df_sales: {len(df_sales)} ventas, columnas: {df_sales.columns.tolist()}")
    print(f"✓ df_inventory: {len(df_inventory)} registros, columnas: {df_inventory.columns.tolist()}")
    
    # --- 4. AGREGAR MIN_STOCK SI NO EXISTE ---
    if "min_stock" not in df_inventory.columns:
        print("  Columna 'min_stock' no encontrada. Usando valor por defecto = 5")
        df_inventory["min_stock"] = 5
    
    # --- 5. AGREGAR COST SI NO EXISTE EN SALES ---
    if "cost" not in df_sales.columns:
        print("  Columna 'cost' no encontrada en sales. Usando costo por defecto = 0")
        df_sales["cost"] = 0.0
    
    # --- 6. LIMPIAR COLUMNAS DUPLICADAS ANTES DEL MERGE ---
    # Eliminar 'price' de df_sales si existe (usaremos el precio del API)
    if "price" in df_sales.columns:
        print(f"  Eliminando columna 'price' de df_sales (usaremos precio del API)")
        df_sales = df_sales.drop(columns=["price"])
    
    # Eliminar 'category' de df_inventory si existe (usaremos categoría del API)
    if "category" in df_inventory.columns:
        print(f"  Eliminando columna 'category' de df_inventory (usaremos categoría del API)")
        df_inventory = df_inventory.drop(columns=["category"])
    
    # --- 7. UNIR DATASETS ---
    # Primero: sales + inventory (left join para mantener todas las ventas)
    df = df_sales.merge(df_inventory, on="product_id", how="left")
    print(f"✓ Después de merge sales+inventory: {len(df)} registros")
    
    # Segundo: resultado + api (left join para mantener ventas incluso si falta info de API)
    df = df.merge(
        df_api[["product_id", "title", "category", "price"]], 
        on="product_id", 
        how="left"
    )
    print(f"✓ Después de merge con API: {len(df)} registros")
    print(f"✓ Columnas finales: {df.columns.tolist()}")
    
    # --- 8. VERIFICAR QUE EL MERGE FUNCIONÓ ---
    if "price" not in df.columns:
        raise ValueError(f" Columna 'price' no existe después del merge. Columnas: {df.columns.tolist()}")
    if "quantity" not in df.columns:
        raise ValueError(f" Columna 'quantity' no existe después del merge. Columnas: {df.columns.tolist()}")
    
    # --- 9. LIMPIAR DATOS INVÁLIDOS ---
    initial_count = len(df)
    df = df[df["price"].notna() & df["quantity"].notna()]
    if len(df) < initial_count:
        print(f"  Se eliminaron {initial_count - len(df)} registros con price o quantity nulos")
    
    # --- 10. CALCULAR MÉTRICAS DE NEGOCIO ---
    
    # 10.1 Valor total de venta
    df["total_sale_value"] = df["quantity"] * df["price"]
    
    # 10.2 Rentabilidad por producto (ventas - costo)
    df["rentabilidad"] = df["total_sale_value"] - (df["cost"] * df["quantity"])
    
    # 10.3 Ventas totales por categoría
    df["ventas_totales_categoria"] = df.groupby("category")["quantity"].transform("sum")
    
    print(f"✓ Métricas calculadas: total_sale_value, rentabilidad, ventas_totales_categoria")
    
    # --- 11. PRODUCTOS CON STOCK CRÍTICO ---
    stock_critico = df[
        (df["current_stock"].notna()) & 
        (df["min_stock"].notna()) & 
        (df["current_stock"] < df["min_stock"])
    ].copy()
    
    # Remover duplicados en stock crítico (un producto solo debe aparecer una vez)
    stock_critico = stock_critico.drop_duplicates(subset=["product_id"])
    
    print(f" Productos con stock crítico: {len(stock_critico)}")
    
    # --- 12. RANKING DE PRODUCTOS MÁS VENDIDOS ---
    top_productos = (
        df.groupby(["product_id", "title"])["quantity"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"quantity": "total_vendido"})
    )
    
    print(f"✓ Top productos calculado: {len(top_productos)} productos únicos")
    
    # --- 13. VENTAS POR CATEGORÍA ---
    ventas_categoria = (
        df.groupby("category")
        .agg({
            "quantity": "sum",
            "total_sale_value": "sum",
            "rentabilidad": "sum"
        })
        .sort_values("quantity", ascending=False)
        .reset_index()
        .rename(columns={
            "quantity": "unidades_vendidas",
            "total_sale_value": "ventas_totales",
            "rentabilidad": "rentabilidad_total"
        })
    )
    
    print(f"✓ Ventas por categoría calculadas: {len(ventas_categoria)} categorías")
    
    # --- 14. RESULTADO FINAL ---
    resultados = {
        "merged": df,
        "stock_critico": stock_critico,
        "top_productos": top_productos,
        "ventas_categoria": ventas_categoria
    }
    
    print(f"\n RESUMEN DE TRANSFORMACIÓN:")
    print(f"   - Registros finales: {len(df)}")
    print(f"   - Productos únicos: {df['product_id'].nunique()}")
    print(f"   - Categorías: {df['category'].nunique()}")
    print(f"   - Stock crítico: {len(stock_critico)} productos")
    print(f"   - Ventas totales: {df['quantity'].sum():.0f} unidades")
    print(f"   - Rentabilidad total: ${df['rentabilidad'].sum():.2f}\n")
    
    return resultados