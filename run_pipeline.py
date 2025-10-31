from src.orchestador import EcommerceDataPipeline

if __name__ == "__main__":
    config_path = "config/pipeline_config.yaml"
    pipeline = EcommerceDataPipeline(config_path)
    pipeline.run_pipeline()
