# Usage Examples

## Python Client Examples

### Basic Scan

```python
import requests
import time

API_URL = "http://localhost:8004"

# 1. Create a scan
response = requests.post(f"{API_URL}/api/scans", json={
    "path": "/mnt/data/my-files",
    "max_depth": 10,
    "include_hidden": False,
    "follow_symlinks": False
})

scan = response.json()
scan_id = scan["id"]
print(f"Created scan {scan_id}")

# 2. Wait for scan to complete
while True:
    response = requests.get(f"{API_URL}/api/scans/{scan_id}")
    scan = response.json()

    print(f"Status: {scan['status']} - Files: {scan['total_files']}")

    if scan["status"] == "completed":
        print(f"Scan complete! Found {scan['total_files']} files")
        break
    elif scan["status"] == "failed":
        print(f"Scan failed: {scan['error_message']}")
        break

    time.sleep(2)

# 3. View scan results
print(f"Total files: {scan['total_files']:,}")
print(f"Total directories: {scan['total_directories']:,}")
print(f"Total size: {scan['total_size']:,} bytes")
```

### Run Analysis with Ollama

```python
# 1. Create analysis
response = requests.post(f"{API_URL}/api/analysis", json={
    "scan_id": scan_id,
    "provider": "ollama",
    "mode": "fast"
})

analysis = response.json()
analysis_id = analysis["id"]
print(f"Created analysis {analysis_id}")

# 2. Wait for analysis to complete
while True:
    response = requests.get(f"{API_URL}/api/analysis/{analysis_id}")
    analysis = response.json()

    if analysis["status"] == "completed":
        print("Analysis complete!")
        print(f"Tokens used: {analysis['tokens_used']}")
        print(f"Duration: {analysis['duration']:.2f}s")
        print(f"\nResponse:\n{analysis['response']}")
        break
    elif analysis["status"] == "failed":
        print(f"Analysis failed: {analysis.get('error_message')}")
        break

    time.sleep(2)

# 3. Get recommendations
response = requests.get(f"{API_URL}/api/analysis/{analysis_id}/recommendations")
recommendations = response.json()

print(f"\nFound {len(recommendations)} recommendations:")
for rec in recommendations:
    print(f"\n- {rec['title']}")
    print(f"  Type: {rec['type']}")
    print(f"  Confidence: {rec['confidence']:.2%}")
    print(f"  Affected files: {rec['affected_count']}")
    print(f"  {rec['description'][:200]}...")
```

### Multi-Model Comparison

```python
# Run analyses with different providers
providers = ["ollama", "gemini"]  # Add "claude" if configured
analyses = []

for provider in providers:
    response = requests.post(f"{API_URL}/api/analysis", json={
        "scan_id": scan_id,
        "provider": provider,
        "mode": "deep"
    })
    analyses.append(response.json())
    print(f"Started {provider} analysis")

# Wait for all to complete
all_complete = False
while not all_complete:
    all_complete = True
    for analysis in analyses:
        response = requests.get(f"{API_URL}/api/analysis/{analysis['id']}")
        status = response.json()["status"]
        if status not in ["completed", "failed"]:
            all_complete = False
    time.sleep(3)

# Compare results
print("\n=== Comparison Results ===\n")
for analysis in analyses:
    response = requests.get(f"{API_URL}/api/analysis/{analysis['id']}")
    result = response.json()

    print(f"{result['provider'].upper()} ({result['model']}):")
    print(f"  Duration: {result['duration']:.2f}s")
    print(f"  Tokens: {result['tokens_used']:,}")
    print(f"  Cost: ${result['cost']:.4f}")

    # Get recommendations
    recs_response = requests.get(
        f"{API_URL}/api/analysis/{analysis['id']}/recommendations"
    )
    recs = recs_response.json()
    print(f"  Recommendations: {len(recs)}")
    print()
```

### Get Scan Files by Category

```python
# Get all code files from a scan
response = requests.get(f"{API_URL}/api/scans/{scan_id}/files", params={
    "category": "code",
    "limit": 100
})

code_files = response.json()
print(f"Found {len(code_files)} code files:")
for file in code_files[:10]:
    print(f"  {file['path']} ({file['size']:,} bytes)")
```

### Find Duplicates

```python
# Get all files from scan
response = requests.get(f"{API_URL}/api/scans/{scan_id}/files", params={
    "limit": 10000
})
files = response.json()

# Group by hash
from collections import defaultdict
hash_groups = defaultdict(list)

for file in files:
    if file.get("hash"):
        hash_groups[file["hash"]].append(file)

# Find duplicates
duplicates = {h: files for h, files in hash_groups.items() if len(files) > 1}

print(f"Found {len(duplicates)} groups of duplicate files:")
for hash_val, duplicate_files in list(duplicates.items())[:5]:
    print(f"\nDuplicate group (hash: {hash_val}):")
    for file in duplicate_files:
        print(f"  - {file['path']} ({file['size']:,} bytes)")
```

## Bash/cURL Examples

### Quick Scan

```bash
# Start scan
curl -X POST http://localhost:8004/api/scans \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/mnt/data/test",
    "max_depth": 5
  }'

# Check status
curl http://localhost:8004/api/scans/1 | jq

# Get files
curl "http://localhost:8004/api/scans/1/files?limit=10" | jq
```

### Analyze with Gemini

```bash
# Create analysis
curl -X POST http://localhost:8004/api/analysis \
  -H "Content-Type: application/json" \
  -d '{
    "scan_id": 1,
    "provider": "gemini",
    "mode": "deep"
  }'

# Get results
curl http://localhost:8004/api/analysis/1 | jq

# Get recommendations
curl http://localhost:8004/api/analysis/1/recommendations | jq
```

## JavaScript/TypeScript Examples

### React Hook for Scans

```typescript
import { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8004';

function useScan(scanId: number) {
  const [scan, setScan] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchScan = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/scans/${scanId}`);
        setScan(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching scan:', error);
        setLoading(false);
      }
    };

    fetchScan();

    // Poll for updates if scan is not complete
    const interval = setInterval(() => {
      if (scan?.status === 'pending' || scan?.status === 'scanning') {
        fetchScan();
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [scanId]);

  return { scan, loading };
}

// Usage
function ScanStatus({ scanId }) {
  const { scan, loading } = useScan(scanId);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h2>Scan #{scan.id}</h2>
      <p>Status: {scan.status}</p>
      <p>Files: {scan.total_files.toLocaleString()}</p>
      <p>Size: {formatBytes(scan.total_size)}</p>
    </div>
  );
}
```

### Create Scan with Axios

```typescript
import axios from 'axios';

async function createScan(path: string) {
  try {
    const response = await axios.post('http://localhost:8004/api/scans', {
      path,
      max_depth: 10,
      include_hidden: false,
      follow_symlinks: false
    });

    console.log('Scan created:', response.data.id);
    return response.data;
  } catch (error) {
    console.error('Error creating scan:', error);
    throw error;
  }
}

// Usage
createScan('/mnt/data/downloads')
  .then(scan => console.log('Scan ID:', scan.id));
```

## Advanced Examples

### Custom Analysis Script

```python
#!/usr/bin/env python3
"""
Custom scan and analysis script
"""
import requests
import time
import argparse

def run_full_analysis(path: str, provider: str = "ollama"):
    """Run complete scan and analysis"""

    api_url = "http://localhost:8004"

    # 1. Create scan
    print(f"Scanning {path}...")
    response = requests.post(f"{api_url}/api/scans", json={
        "path": path,
        "max_depth": 10,
        "include_hidden": False
    })
    scan_id = response.json()["id"]

    # 2. Wait for scan
    while True:
        scan = requests.get(f"{api_url}/api/scans/{scan_id}").json()
        if scan["status"] == "completed":
            break
        elif scan["status"] == "failed":
            print(f"Scan failed: {scan['error_message']}")
            return
        time.sleep(2)

    print(f"Scan complete: {scan['total_files']:,} files, {scan['total_size']:,} bytes")

    # 3. Create analysis
    print(f"\nAnalyzing with {provider}...")
    response = requests.post(f"{api_url}/api/analysis", json={
        "scan_id": scan_id,
        "provider": provider,
        "mode": "deep"
    })
    analysis_id = response.json()["id"]

    # 4. Wait for analysis
    while True:
        analysis = requests.get(f"{api_url}/api/analysis/{analysis_id}").json()
        if analysis["status"] == "completed":
            break
        elif analysis["status"] == "failed":
            print(f"Analysis failed: {analysis.get('error_message')}")
            return
        time.sleep(2)

    print(f"Analysis complete in {analysis['duration']:.2f}s")
    print(f"Tokens used: {analysis['tokens_used']:,}")

    # 5. Get recommendations
    recs = requests.get(
        f"{api_url}/api/analysis/{analysis_id}/recommendations"
    ).json()

    print(f"\n=== Recommendations ({len(recs)}) ===\n")
    for i, rec in enumerate(recs, 1):
        print(f"{i}. {rec['title']}")
        print(f"   Type: {rec['type']} | Confidence: {rec['confidence']:.0%}")
        print(f"   {rec['description'][:200]}...")
        print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Data-Organizer analysis")
    parser.add_argument("path", help="Path to scan")
    parser.add_argument("--provider", default="ollama", choices=["ollama", "gemini", "claude"])
    args = parser.parse_args()

    run_full_analysis(args.path, args.provider)
```

### Monitor Multiple Scans

```python
import requests
from datetime import datetime

def monitor_scans():
    """Monitor all active scans"""

    api_url = "http://localhost:8004"

    while True:
        # Get all scans
        response = requests.get(f"{api_url}/api/scans", params={"limit": 100})
        data = response.json()

        # Filter active scans
        active = [s for s in data["scans"] if s["status"] in ["pending", "scanning"]]

        if active:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Active scans: {len(active)}")
            for scan in active:
                print(f"  Scan #{scan['id']}: {scan['status']} - {scan['total_files']:,} files")
        else:
            print("No active scans")

        time.sleep(5)

if __name__ == "__main__":
    monitor_scans()
```

## Common Patterns

### Scan and Analyze Workflow

```python
class DataOrganizerClient:
    def __init__(self, api_url: str = "http://localhost:8004"):
        self.api_url = api_url

    def create_scan(self, path: str, **kwargs):
        response = requests.post(f"{self.api_url}/api/scans", json={
            "path": path,
            **kwargs
        })
        return response.json()

    def wait_for_scan(self, scan_id: int, timeout: int = 3600):
        start = time.time()
        while time.time() - start < timeout:
            scan = self.get_scan(scan_id)
            if scan["status"] in ["completed", "failed"]:
                return scan
            time.sleep(2)
        raise TimeoutError(f"Scan {scan_id} did not complete in {timeout}s")

    def get_scan(self, scan_id: int):
        response = requests.get(f"{self.api_url}/api/scans/{scan_id}")
        return response.json()

    def analyze(self, scan_id: int, provider: str = "ollama", mode: str = "fast"):
        response = requests.post(f"{self.api_url}/api/analysis", json={
            "scan_id": scan_id,
            "provider": provider,
            "mode": mode
        })
        return response.json()

    def wait_for_analysis(self, analysis_id: int, timeout: int = 600):
        start = time.time()
        while time.time() - start < timeout:
            analysis = self.get_analysis(analysis_id)
            if analysis["status"] in ["completed", "failed"]:
                return analysis
            time.sleep(2)
        raise TimeoutError(f"Analysis {analysis_id} did not complete in {timeout}s")

    def get_analysis(self, analysis_id: int):
        response = requests.get(f"{self.api_url}/api/analysis/{analysis_id}")
        return response.json()

    def get_recommendations(self, analysis_id: int):
        response = requests.get(
            f"{self.api_url}/api/analysis/{analysis_id}/recommendations"
        )
        return response.json()

# Usage
client = DataOrganizerClient()

# Run full workflow
scan = client.create_scan("/mnt/data/documents")
scan = client.wait_for_scan(scan["id"])
print(f"Scanned {scan['total_files']} files")

analysis = client.analyze(scan["id"], provider="ollama", mode="fast")
analysis = client.wait_for_analysis(analysis["id"])
print(f"Analysis took {analysis['duration']:.2f}s")

recommendations = client.get_recommendations(analysis["id"])
for rec in recommendations:
    print(f"- {rec['title']} (confidence: {rec['confidence']:.0%})")
```

## Integration Examples

### Scheduled Scans (using cron)

```bash
# crontab entry for daily scans
0 2 * * * /usr/local/bin/python3 /path/to/daily_scan.py

# daily_scan.py
import requests
from datetime import datetime

scan = requests.post("http://localhost:8004/api/scans", json={
    "path": "/mnt/data/important",
    "max_depth": 10
}).json()

print(f"[{datetime.now()}] Started daily scan {scan['id']}")
```

### Webhook Integration

```python
# Send scan results to webhook when complete
def on_scan_complete(scan_id: int, webhook_url: str):
    scan = requests.get(f"http://localhost:8004/api/scans/{scan_id}").json()

    if scan["status"] == "completed":
        payload = {
            "scan_id": scan_id,
            "path": scan["path"],
            "total_files": scan["total_files"],
            "total_size": scan["total_size"],
            "completed_at": scan["completed_at"]
        }

        requests.post(webhook_url, json=payload)
```

### Export Results to CSV

```python
import csv
import requests

def export_scan_to_csv(scan_id: int, output_file: str):
    """Export scan results to CSV"""

    # Get all files
    files = requests.get(
        f"http://localhost:8004/api/scans/{scan_id}/files",
        params={"limit": 10000}
    ).json()

    # Write to CSV
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['path', 'name', 'size', 'category', 'modified_at', 'hash']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for file in files:
            writer.writerow({
                'path': file['path'],
                'name': file['name'],
                'size': file['size'],
                'category': file.get('category', 'unknown'),
                'modified_at': file.get('modified_at', ''),
                'hash': file.get('hash', '')
            })

    print(f"Exported {len(files)} files to {output_file}")

# Usage
export_scan_to_csv(1, "scan_results.csv")
```
