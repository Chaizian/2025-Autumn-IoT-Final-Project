import urllib.request
import os

libs = {
    "chart.min.js": "https://unpkg.com/chart.js@3.9.1/dist/chart.min.js",
    "axios.min.js": "https://unpkg.com/axios@1.3.4/dist/axios.min.js"
}

print("Downloading libraries locally to avoid CDN issues...")

for filename, url in libs.items():
    print(f"Downloading {filename}...")
    try:
        urllib.request.urlretrieve(url, filename)
        print(f"Success: {filename}")
    except Exception as e:
        print(f"Failed to download {filename} from {url}")
        print(f"Error: {e}")
        # Try backup source (cdnjs)
        try:
            backup_url = url.replace("unpkg.com", "cdnjs.cloudflare.com/ajax/libs").replace("/dist", "")
            if "chart.js" in url:
                backup_url = "https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"
            elif "axios" in url:
                backup_url = "https://cdnjs.cloudflare.com/ajax/libs/axios/1.3.4/axios.min.js"
            
            print(f"Trying backup source for {filename}...")
            urllib.request.urlretrieve(backup_url, filename)
            print(f"Success: {filename}")
        except Exception as e2:
            print(f"Failed backup source too: {e2}")

print("Done.")
