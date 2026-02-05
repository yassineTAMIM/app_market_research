# Make src a Python package
from . import ingest_data as ingest_data_module
from . import transform_data as transform_data_module
from . import create_serving_layer as create_serving_layer_module
from . import create_dashboard as create_dashboard_module

# Rename imports to avoid conflicts
ingest_data = ingest_data_module
transform_data = transform_data_module
create_serving_layer = create_serving_layer_module
create_dashboard = create_dashboard_module
