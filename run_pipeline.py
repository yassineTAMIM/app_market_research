"""
Main Pipeline Runner
Executes the complete data pipeline from ingestion to dashboard
"""
import sys
import os

def run_pipeline():
    """Run all pipeline steps in sequence"""
    
    print("=" * 60)
    print("STARTING DATA PIPELINE")
    print("=" * 60)
    
    # Step 1: Data Ingestion
    print("\n[STEP 1/4] Data Ingestion")
    print("-" * 60)
    try:
        import importlib
        mod = importlib.import_module('src.01_ingest_data')
        mod.main()
    except Exception as e:
        print(f"ERROR in data ingestion: {e}")
        print("Continuing with existing raw data if available...")
    
    # Step 2: Data Transformation
    print("\n[STEP 2/4] Data Transformation")
    print("-" * 60)
    try:
        import importlib
        mod = importlib.import_module('src.02_transform_data')
        mod.main()
    except Exception as e:
        print(f"ERROR in data transformation: {e}")
        sys.exit(1)
    
    # Step 3: Serving Layer
    print("\n[STEP 3/4] Creating Serving Layer")
    print("-" * 60)
    try:
        import importlib
        mod = importlib.import_module('src.03_create_serving_layer')
        mod.main()
    except Exception as e:
        print(f"ERROR in serving layer creation: {e}")
        sys.exit(1)
    
    # Step 4: Dashboard
    print("\n[STEP 4/4] Creating Dashboard")
    print("-" * 60)
    try:
        import importlib
        mod = importlib.import_module('src.04_create_dashboard')
        mod.main()
    except Exception as e:
        print(f"ERROR in dashboard creation: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\nOutputs:")
    print("  - Raw data: data/raw/")
    print("  - Processed data: data/processed/")
    print("  - Dashboard: data/processed/dashboard.html")

if __name__ == "__main__":
    # Ensure we're in the right directory
    if not os.path.exists('data'):
        print("ERROR: Run this script from the project root directory")
        sys.exit(1)
    
    run_pipeline()