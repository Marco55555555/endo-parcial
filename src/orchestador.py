import yaml
import logging
from src.ingestion import ingest_data
from src.tansformation import transform_data  # ← CORREGIDO: era "tansformation"
from src.quality_checks import run_quality_checks
from src.reporting import generate_report  # ← AGREGADO: para generar reportes

class EcommerceDataPipeline:
    def __init__(self, config_path):
        """Inicializa el pipeline cargando la configuración y los logs."""
        self.config = self.load_config(config_path)
        self.setup_logging()

    def load_config(self, config_path):
        """Carga el archivo YAML con las rutas y parámetros."""
        with open(config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)

    def setup_logging(self):
        """Configura el sistema de logging."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("pipeline_execution.log", encoding='utf-8'),  # ← CORREGIDO: encoding
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def run_pipeline(self):
        """Ejecuta todo el flujo del pipeline."""
        self.logger.info(" Iniciando pipeline de e-commerce...")

        try:
            # --- Cargar configuración ---
            api_cfg = self.config["api"]
            data_cfg = self.config["data_sources"]
            proc_cfg = self.config["processing"]
            qc_cfg = self.config.get("quality_checks", {})  # ← CORREGIDO: usar .get() para evitar KeyError
            output_cfg = self.config.get("output", {})

            # --- FASE 1: INGESTA ---
            self.logger.info(" Iniciando ingesta de datos...")
            df_api, df_sales, df_inventory = ingest_data(
                api_cfg["url"],
                data_cfg["sales_file"],
                data_cfg["inventory_file"],
                proc_cfg["output_path"]
            )
            self.logger.info(" Ingesta completada.")

            # --- FASE 2: TRANSFORMACIÓN ---
            self.logger.info(" Aplicando transformaciones...")
            results = transform_data(df_api, df_sales, df_inventory)
            self.logger.info(" Transformación completada.")

            # --- FASE 3: PRUEBAS DE CALIDAD ---
            self.logger.info("🔍 Ejecutando verificaciones de calidad...")
            passed, tests = run_quality_checks(results["merged"])

            if passed:
                self.logger.info(" Todos los tests de calidad pasaron.")
            else:
                self.logger.warning(f" Algunos tests fallaron: {tests}")
                # Opcional: Puedes decidir si detener el pipeline aquí
                # raise ValueError("Tests de calidad fallaron. Pipeline detenido.")

            # --- FASE 4: GENERACIÓN DE REPORTES ---
            self.logger.info(" Generando reportes...")
            reports_path = output_cfg.get("reports_path", "reports")
            report_file = generate_report(results, tests, reports_path)
            self.logger.info(f" Reporte generado: {report_file}")

            # --- RESUMEN FINAL ---
            self.logger.info("=" * 60)
            self.logger.info(" PIPELINE EJECUTADO EXITOSAMENTE")
            self.logger.info("=" * 60)
            self.logger.info(f" Registros procesados: {len(results['merged'])}")
            self.logger.info(f"  Productos con stock crítico: {len(results['stock_critico'])}")
            self.logger.info(f" Top productos: {len(results['top_productos'])}")
            self.logger.info(f" Reporte guardado en: {report_file}")
            self.logger.info("=" * 60)

        except FileNotFoundError as e:
            self.logger.error(f" Archivo no encontrado: {e}")
            self.logger.error(" Verifica que los archivos CSV existan en la ruta especificada.")
            raise

        except KeyError as e:
            self.logger.error(f" Clave faltante en configuración: {e}")
            self.logger.error(" Revisa tu archivo pipeline_config.yaml")
            raise

        except ValueError as e:
            self.logger.error(f" Error de validación de datos: {e}")
            raise

        except Exception as e:
            self.logger.error(f" Error inesperado durante la ejecución del pipeline: {e}")
            self.logger.error(" Revisa el archivo pipeline_execution.log para más detalles")
            raise  # Re-lanzar para ver el traceback completo


if __name__ == "__main__":
    # Ejecutar el pipeline
    pipeline = EcommerceDataPipeline("config/pipeline_config.yaml")
    pipeline.run_pipeline()