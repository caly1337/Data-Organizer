# Data-Organizer API Documentation

## Base URL

- Development: `http://localhost:8004`
- Production: `http://spark.lmphq.net:8004`

## Authentication

Currently no authentication required. JWT authentication will be added in future phase.

## Endpoints

### Health & Status

#### GET /
Root endpoint with API information

**Response:**
```json
{
  "name": "Data-Organizer",
  "version": "0.1.0",
  "status": "running",
  "docs": "/docs"
}
```

#### GET /health
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "database": "connected"
}
```

### Scans

#### POST /api/scans
Create and start a new filesystem scan

**Request Body:**
```json
{
  "path": "/mnt/data/my-directory",
  "max_depth": 10,
  "include_hidden": false,
  "follow_symlinks": false
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "path": "/mnt/data/my-directory",
  "status": "pending",
  "started_at": "2026-01-17T12:00:00Z",
  "completed_at": null,
  "total_files": 0,
  "total_directories": 0,
  "total_size": 0,
  "error_message": null,
  "errors_count": 0,
  "metadata": null
}
```

**Status Values:**
- `pending` - Scan created, not started
- `scanning` - Scan in progress
- `completed` - Scan finished successfully
- `failed` - Scan failed with errors

#### GET /api/scans
List all scans with pagination

**Query Parameters:**
- `skip` (default: 0) - Number of records to skip
- `limit` (default: 20, max: 100) - Number of records to return
- `status` (optional) - Filter by status

**Response:** `200 OK`
```json
{
  "scans": [...],
  "total": 42,
  "page": 1,
  "page_size": 20
}
```

#### GET /api/scans/{scan_id}
Get detailed scan information

**Query Parameters:**
- `include_files` (default: false) - Include file list (limited to 1000)

**Response:** `200 OK`
```json
{
  "id": 1,
  "path": "/mnt/data/my-directory",
  "status": "completed",
  "started_at": "2026-01-17T12:00:00Z",
  "completed_at": "2026-01-17T12:05:00Z",
  "total_files": 5423,
  "total_directories": 342,
  "total_size": 15728640000,
  "error_message": null,
  "errors_count": 0,
  "metadata": null,
  "files": [...]
}
```

#### DELETE /api/scans/{scan_id}
Delete a scan and all associated data

**Response:** `200 OK`
```json
{
  "message": "Scan deleted successfully"
}
```

#### GET /api/scans/{scan_id}/files
Get files from a specific scan

**Query Parameters:**
- `skip` (default: 0)
- `limit` (default: 100, max: 1000)
- `category` (optional) - Filter by file category

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "scan_id": 1,
    "path": "/mnt/data/my-directory/file.txt",
    "name": "file.txt",
    "extension": ".txt",
    "size": 1024,
    "is_directory": false,
    "is_symlink": false,
    "created_at": "2025-01-01T00:00:00Z",
    "modified_at": "2026-01-10T15:30:00Z",
    "hash": "abc123def456",
    "mime_type": "text/plain",
    "category": "document"
  }
]
```

### Analysis

#### POST /api/analysis
Create and start a new analysis

**Request Body:**
```json
{
  "scan_id": 1,
  "provider": "ollama",
  "mode": "fast"
}
```

**Parameters:**
- `provider`: `ollama`, `gemini`, or `claude`
- `mode`: `fast`, `deep`, or `comparison`

**Response:** `201 Created`
```json
{
  "id": 1,
  "scan_id": 1,
  "provider": "ollama",
  "model": "qwen2.5:7b",
  "mode": "fast",
  "response": "",
  "tokens_used": null,
  "cost": null,
  "duration": null,
  "status": "pending",
  "created_at": "2026-01-17T12:10:00Z",
  "completed_at": null
}
```

#### GET /api/analysis/{analysis_id}
Get analysis details

**Response:** `200 OK`
```json
{
  "id": 1,
  "scan_id": 1,
  "provider": "ollama",
  "model": "qwen2.5:7b",
  "mode": "fast",
  "response": "Detailed analysis from LLM...",
  "tokens_used": 1523,
  "cost": 0.0,
  "duration": 12.5,
  "status": "completed",
  "created_at": "2026-01-17T12:10:00Z",
  "completed_at": "2026-01-17T12:10:12Z"
}
```

#### GET /api/analysis/{analysis_id}/recommendations
Get recommendations from analysis

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "analysis_id": 1,
    "type": "reorganize",
    "action": "move",
    "title": "Consolidate image files",
    "description": "Move all image files to a dedicated 'Images' directory",
    "reasoning": "Images are scattered across multiple directories...",
    "confidence": 0.85,
    "impact_score": 0.7,
    "affected_count": 234,
    "status": "pending",
    "priority": 8
  }
]
```

#### GET /api/analysis/scan/{scan_id}
Get all analyses for a specific scan

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "scan_id": 1,
    "provider": "ollama",
    "model": "qwen2.5:7b",
    ...
  },
  {
    "id": 2,
    "scan_id": 1,
    "provider": "gemini",
    "model": "gemini-2.5-flash",
    ...
  }
]
```

## Common Workflows

### 1. Basic Scan and Analysis

```bash
# 1. Create scan
SCAN_ID=$(curl -X POST http://localhost:8004/api/scans \
  -H "Content-Type: application/json" \
  -d '{"path": "/mnt/data/test"}' | jq -r '.id')

# 2. Wait for scan to complete
while [ "$(curl -s http://localhost:8004/api/scans/$SCAN_ID | jq -r '.status')" != "completed" ]; do
  sleep 5
done

# 3. Create analysis
ANALYSIS_ID=$(curl -X POST http://localhost:8004/api/analysis \
  -H "Content-Type: application/json" \
  -d "{\"scan_id\": $SCAN_ID, \"provider\": \"ollama\", \"mode\": \"fast\"}" | jq -r '.id')

# 4. Wait for analysis
while [ "$(curl -s http://localhost:8004/api/analysis/$ANALYSIS_ID | jq -r '.status')" != "completed" ]; do
  sleep 5
done

# 5. Get recommendations
curl http://localhost:8004/api/analysis/$ANALYSIS_ID/recommendations | jq
```

### 2. Multi-Model Comparison

```bash
# Run analyses with different providers
curl -X POST http://localhost:8004/api/analysis \
  -H "Content-Type: application/json" \
  -d '{"scan_id": 1, "provider": "ollama", "mode": "deep"}'

curl -X POST http://localhost:8004/api/analysis \
  -H "Content-Type: application/json" \
  -d '{"scan_id": 1, "provider": "gemini", "mode": "deep"}'

# Compare recommendations
curl http://localhost:8004/api/analysis/scan/1 | jq
```

## Error Responses

All errors follow this format:

```json
{
  "error": "Error type",
  "message": "Detailed error message"
}
```

**Common Status Codes:**
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error

## Rate Limits

Currently no rate limits. Will be added in future phase.

## WebSocket Support

Real-time updates for scan progress (planned for future phase):

```javascript
const ws = new WebSocket('ws://localhost:8004/ws/scans/{scan_id}');
ws.onmessage = (event) => {
  const progress = JSON.parse(event.data);
  console.log(`Progress: ${progress.files_scanned} files`);
};
```

## Interactive API Documentation

Visit `http://localhost:8004/docs` for interactive Swagger UI documentation where you can test all endpoints directly in your browser.
