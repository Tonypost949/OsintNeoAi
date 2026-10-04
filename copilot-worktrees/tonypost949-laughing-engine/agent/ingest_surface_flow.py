from ingest_arcgis import ingest_arcgis_layer

def main():
    url = "https://gis.huntingtonbeachca.gov/arcgis/rest/services/SurfaceFlow/MapServer/0"
    table_name = "hb_surface_flow"
    
    try:
        print(f"Starting ingestion of {table_name} from {url}")
        ingest_arcgis_layer(url, table_name)
        print("Ingestion complete.")
    except Exception as e:
        print(f"Error ingesting {table_name}: {e}")

if __name__ == "__main__":
    main()
