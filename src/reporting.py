import pandas as pd
import os
from datetime import datetime

def generate_report(results, tests, output_path):
    """
    Genera un reporte completo en formato texto y exporta CSVs con los resultados del pipeline.
    
    Args:
        results: Diccionario con dataframes procesados
            - 'merged': DataFrame principal con todos los datos unidos
            - 'stock_critico': DataFrame con productos con stock bajo
            - 'top_productos': DataFrame con ranking de productos más vendidos
            - 'ventas_categoria': DataFrame con ventas agregadas por categoría
        tests: Diccionario con resultados de tests de calidad
        output_path: Ruta donde guardar el reporte
    
    Returns:
        str: Ruta del archivo de reporte generado
    """
    # Crear directorio si no existe
    os.makedirs(output_path, exist_ok=True)
    
    # Timestamp para nombres únicos
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"{output_path}/pipeline_report_{timestamp}.txt"
    
    # DataFrame principal
    df = results["merged"]
    stock_critico = results["stock_critico"]
    top_productos = results["top_productos"]
    ventas_categoria = results.get("ventas_categoria", pd.DataFrame())
    
    # ============================================================
    # GENERAR REPORTE EN TEXTO
    # ============================================================
    with open(report_file, 'w', encoding='utf-8') as f:
        # --- ENCABEZADO ---
        f.write("=" * 70 + "\n")
        f.write("         REPORTE DE EJECUCIÓN - PIPELINE E-COMMERCE\n")
        f.write("=" * 70 + "\n")
        f.write(f"Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write("=" * 70 + "\n\n")
        
        # --- SECCIÓN 1: TESTS DE CALIDAD DE DATOS ---
        f.write("-" * 70 + "\n")
        f.write("1. TESTS DE CALIDAD DE DATOS\n")
        f.write("-" * 70 + "\n\n")
        
        all_passed = all(tests.values())
        if all_passed:
            f.write("✓ ESTADO GENERAL: TODOS LOS TESTS PASARON\n\n")
        else:
            f.write("✗ ESTADO GENERAL: ALGUNOS TESTS FALLARON\n\n")
        
        f.write("Resultados detallados:\n")
        for test_name, result in tests.items():
            status = "✓ PASÓ" if result else "✗ FALLÓ"
            status_symbol = "  [OK]" if result else "  [FALLO]"
            f.write(f"  {status_symbol} {test_name.replace('_', ' ').title()}: {status}\n")
        
        f.write("\n")
        
        # --- SECCIÓN 2: ESTADÍSTICAS GENERALES ---
        f.write("-" * 70 + "\n")
        f.write("2. ESTADÍSTICAS GENERALES DEL PIPELINE\n")
        f.write("-" * 70 + "\n\n")
        
        f.write(f"  Total de registros procesados: {len(df):,}\n")
        f.write(f"  Productos únicos: {df['product_id'].nunique():,}\n")
        f.write(f"  Categorías distintas: {df['category'].nunique():,}\n")
        f.write(f"  Total de unidades vendidas: {df['quantity'].sum():,.0f}\n")
        
        if 'total_sale_value' in df.columns:
            f.write(f"  Valor total de ventas: ${df['total_sale_value'].sum():,.2f}\n")
        
        if 'rentabilidad' in df.columns:
            rentabilidad_total = df['rentabilidad'].sum()
            f.write(f"  Rentabilidad total: ${rentabilidad_total:,.2f}\n")
            if rentabilidad_total > 0:
                f.write(f"  Margen promedio: {(rentabilidad_total / df['total_sale_value'].sum() * 100):.2f}%\n")
        
        f.write("\n")
        
        # --- SECCIÓN 3: PRODUCTOS CON STOCK CRÍTICO ---
        f.write("-" * 70 + "\n")
        f.write("3. ALERTA: PRODUCTOS CON STOCK CRÍTICO\n")
        f.write("-" * 70 + "\n\n")
        
        if len(stock_critico) > 0:
            f.write(f"  ATENCIÓN: {len(stock_critico)} producto(s) con stock por debajo del mínimo\n\n")
            f.write(f"{'Producto':<40} {'Stock Actual':>12} {'Stock Mínimo':>12} {'Déficit':>10}\n")
            f.write("-" * 70 + "\n")
            
            for _, row in stock_critico.iterrows():
                product_name = str(row['title'])[:38] if 'title' in row else f"ID: {row['product_id']}"
                current = int(row['current_stock'])
                minimum = int(row['min_stock'])
                deficit = minimum - current
                
                f.write(f"{product_name:<40} {current:>12} {minimum:>12} {deficit:>10}\n")
            
            f.write("\n RECOMENDACIÓN: Reabastecer estos productos urgentemente.\n")
        else:
            f.write("✓ Excelente: No hay productos con stock crítico.\n")
            f.write("  Todos los productos tienen inventario por encima del mínimo requerido.\n")
        
        f.write("\n")
        
        # --- SECCIÓN 4: TOP PRODUCTOS MÁS VENDIDOS ---
        f.write("-" * 70 + "\n")
        f.write("4. TOP 10 PRODUCTOS MÁS VENDIDOS\n")
        f.write("-" * 70 + "\n\n")
        
        top_10 = top_productos.head(10)
        f.write(f"{'#':<4} {'Producto':<45} {'Unidades':>15}\n")
        f.write("-" * 70 + "\n")
        
        for idx, row in top_10.iterrows():
            rank = idx + 1
            product_name = str(row['title'])[:43] if 'title' in row else f"ID: {row['product_id']}"
            cantidad_col = 'total_vendido' if 'total_vendido' in row else 'quantity'
            cantidad = int(row[cantidad_col])
            
            f.write(f"{rank:<4} {product_name:<45} {cantidad:>15,}\n")
        
        f.write("\n")
        
        # --- SECCIÓN 5: VENTAS POR CATEGORÍA ---
        f.write("-" * 70 + "\n")
        f.write("5. ANÁLISIS DE VENTAS POR CATEGORÍA\n")
        f.write("-" * 70 + "\n\n")
        
        if not ventas_categoria.empty:
            f.write(f"{'Categoría':<25} {'Unidades':>12} {'Valor Total':>15} {'Rentabilidad':>15}\n")
            f.write("-" * 70 + "\n")
            
            for _, row in ventas_categoria.iterrows():
                categoria = str(row['category'])[:23]
                unidades = int(row['unidades_vendidas'])
                ventas = float(row['ventas_totales'])
                rentab = float(row['rentabilidad_total'])
                
                f.write(f"{categoria:<25} {unidades:>12,} ${ventas:>14,.2f} ${rentab:>14,.2f}\n")
        else:
            # Si no existe el dataframe de ventas_categoria, calcularlo desde merged
            ventas_cat = df.groupby('category').agg({
                'quantity': 'sum',
                'total_sale_value': 'sum' if 'total_sale_value' in df.columns else 'count'
            }).sort_values('quantity', ascending=False)
            
            f.write(f"{'Categoría':<40} {'Unidades Vendidas':>25}\n")
            f.write("-" * 70 + "\n")
            
            for categoria, row in ventas_cat.iterrows():
                f.write(f"{str(categoria):<40} {int(row['quantity']):>25,}\n")
        
        f.write("\n")
        
        # --- SECCIÓN 6: RESUMEN DE RENTABILIDAD ---
        if 'rentabilidad' in df.columns:
            f.write("-" * 70 + "\n")
            f.write("6. ANÁLISIS DE RENTABILIDAD\n")
            f.write("-" * 70 + "\n\n")
            
            rentabilidad_por_producto = df.groupby('title')['rentabilidad'].sum().sort_values(ascending=False)
            
            f.write("Top 5 productos más rentables:\n")
            f.write(f"{'Producto':<45} {'Rentabilidad':>20}\n")
            f.write("-" * 70 + "\n")
            
            for producto, rentab in rentabilidad_por_producto.head(5).items():
                producto_name = str(producto)[:43]
                f.write(f"{producto_name:<45} ${rentab:>19,.2f}\n")
            
            f.write("\n")
        
        # --- PIE DE PÁGINA ---
        f.write("=" * 70 + "\n")
        f.write("FIN DEL REPORTE\n")
        f.write("=" * 70 + "\n")
        f.write(f"\nArchivos exportados:\n")
        f.write(f"  - Reporte principal: {report_file}\n")
        f.write(f"  - Stock crítico: {output_path}/stock_critico_{timestamp}.csv\n")
        f.write(f"  - Top productos: {output_path}/top_productos_{timestamp}.csv\n")
        if not ventas_categoria.empty:
            f.write(f"  - Ventas por categoría: {output_path}/ventas_categoria_{timestamp}.csv\n")
        f.write("\n")
    
    # ============================================================
    # EXPORTAR ARCHIVOS CSV
    # ============================================================
    
    # CSV 1: Stock crítico
    if len(stock_critico) > 0:
        stock_critico_export = stock_critico[['product_id', 'title', 'category', 'current_stock', 'min_stock']].copy()
        stock_critico_export['deficit'] = stock_critico_export['min_stock'] - stock_critico_export['current_stock']
        stock_critico_export.to_csv(
            f"{output_path}/stock_critico_{timestamp}.csv", 
            index=False, 
            encoding='utf-8-sig'  # Para Excel
        )
    
    # CSV 2: Top productos
    top_productos.to_csv(
        f"{output_path}/top_productos_{timestamp}.csv", 
        index=False, 
        encoding='utf-8-sig'
    )
    
    # CSV 3: Ventas por categoría
    if not ventas_categoria.empty:
        ventas_categoria.to_csv(
            f"{output_path}/ventas_categoria_{timestamp}.csv", 
            index=False, 
            encoding='utf-8-sig'
        )
    
    # CSV 4: Dataset completo procesado (opcional, útil para análisis posteriores)
    df.to_csv(
        f"{output_path}/datos_procesados_{timestamp}.csv",
        index=False,
        encoding='utf-8-sig'
    )
    
    # ============================================================
    # MENSAJE DE CONFIRMACIÓN EN CONSOLA
    # ============================================================
    print(f"\n{'=' * 70}")
    print(f" REPORTES GENERADOS EXITOSAMENTE")
    print(f"{'=' * 70}")
    print(f" Reporte principal: {report_file}")
    print(f" Directorio de salida: {output_path}")
    print(f" Archivos CSV exportados: 4")
    print(f"{'=' * 70}\n")
    
    return report_file


def generate_html_report(results, tests, output_path):
    """
    [OPCIONAL] Genera un reporte en formato HTML con visualizaciones básicas.
    Requiere que tengas los datos procesados.
    
    Esta función es una mejora futura que podrías implementar.
    """
    # Esta sería una extensión futura para generar reportes HTML más visuales
    pass