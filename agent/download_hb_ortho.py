import math
import os
import requests
from io import BytesIO
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)

def download_tile(z, x, y, output_dir):
    url = f"https://gis.huntingtonbeachca.gov/arcgis/rest/services/1994OrthosHybrid/MapServer/WMTS/tile/1.0.0/1994OrthosHybrid/default/default028mm/{z}/{y}/{x}.jpg"
    filename = os.path.join(output_dir, f"{z}_{x}_{y}.jpg")
    
    if os.path.exists(filename):
        return filename, Image.open(filename)
        
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            return filename, Image.open(BytesIO(response.content))
        else:
            return filename, None
    except Exception as e:
        return filename, None

def stitch_ortho(min_lat, max_lat, min_lon, max_lon, zoom=21):
    print(f"Calculating tile grid for bounding box at Zoom {zoom}...")
    x_min, y_max = deg2num(min_lat, min_lon, zoom)
    x_max, y_min = deg2num(max_lat, max_lon, zoom)
    
    print(f"X range: {x_min} to {x_max} ({x_max - x_min + 1} tiles)")
    print(f"Y range: {y_min} to {y_max} ({y_max - y_min + 1} tiles)")
    
    total_tiles = (x_max - x_min + 1) * (y_max - y_min + 1)
    print(f"Total tiles to download: {total_tiles}")
    
    if total_tiles > 500:
        print("Too many tiles! Reduce bounding box or lower zoom level.")
        return None
        
    output_dir = "tiles_temp"
    os.makedirs(output_dir, exist_ok=True)
    
    tasks = []
    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            tasks.append((zoom, x, y, output_dir))
            
    print("Downloading tiles concurrently...")
    tiles_data = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(download_tile, *task) for task in tasks]
        for idx, f in enumerate(futures):
            _, img = f.result()
            if img:
                task = tasks[idx]
                tiles_data[(task[1], task[2])] = img
                
    print("Stitching image...")
    width = (x_max - x_min + 1) * 256
    height = (y_max - y_min + 1) * 256
    
    final_image = Image.new('RGB', (width, height))
    
    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            img = tiles_data.get((x, y))
            if img:
                paste_x = (x - x_min) * 256
                paste_y = (y - y_min) * 256
                final_image.paste(img, (paste_x, paste_y))
                
    output_filename = "HB_1994_Ortho_Target.jpg"
    final_image.save(output_filename)
    print(f"Success: Final image saved as {output_filename}")
    
    return output_filename

if __name__ == "__main__":
    # Test coordinates for Huntington Beach Navigation Center footprint
    # ENV-HBNC-001 (Approx: 33.714, -117.986)
    min_lat = 33.7135
    max_lat = 33.7145
    min_lon = -117.9870
    max_lon = -117.9850
    
    image_path = stitch_ortho(min_lat, max_lat, min_lon, max_lon, zoom=21)
    
    if image_path:
        from google.cloud import storage
        print("Uploading to Cloud Vault...")
        try:
            client = storage.Client(project="project-743aab84-f9a5-4ec7-954")
            bucket = client.bucket("osint-ai-evidence-vault-m4")
            blob = bucket.blob("imagery/HB_1994_Ortho_Target.jpg")
            blob.upload_from_filename(image_path)
            print("Success: Uploaded to gs://osint-ai-evidence-vault-m4/imagery/HB_1994_Ortho_Target.jpg")
        except Exception as e:
            print(f"Upload failed: {e}")
