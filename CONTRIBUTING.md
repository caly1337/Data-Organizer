# Contributing to Data-Organizer

## Development Workflow

### 1. Setup Development Environment

```bash
cd F:\AI-PROD\projects\Data-Organizer
.\setup.ps1  # Windows
# or
./setup.sh   # Linux/Mac
```

### 2. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Make Changes

Follow the code style and architectural patterns:

**Backend:**
- Use async/await for all I/O operations
- Add type hints to all functions
- Follow Pydantic models for data validation
- Add docstrings to public functions
- Use logging instead of print()

**Frontend:**
- Use TypeScript for type safety
- Follow React best practices
- Use Tailwind for styling
- Create reusable components

### 4. Test Your Changes

```bash
# Backend tests
cd backend
pytest

# Type checking
mypy app/

# Code formatting
black app/
flake8 app/

# Frontend tests
cd frontend
npm run type-check
npm run lint
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: Add your feature description

- Detail 1
- Detail 2

Co-Authored-By: Your Name <your.email@example.com>"
```

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

## Code Style

### Python (Backend)

- Follow PEP 8
- Use Black for formatting (line length: 100)
- Use type hints
- Maximum function length: 50 lines
- Maximum file length: 500 lines

Example:
```python
async def process_scan(
    scan_id: int,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Process a filesystem scan

    Args:
        scan_id: ID of scan to process
        db: Database session

    Returns:
        Dictionary with scan results

    Raises:
        ValueError: If scan not found
    """
    result = await db.execute(select(Scan).where(Scan.id == scan_id))
    scan = result.scalar_one_or_none()

    if not scan:
        raise ValueError(f"Scan {scan_id} not found")

    # Process scan...
    return {"status": "success"}
```

### TypeScript (Frontend)

- Use TypeScript strict mode
- Define interfaces for all data structures
- Use functional components with hooks
- Use descriptive variable names

Example:
```typescript
interface ScanData {
  id: number;
  path: string;
  status: string;
  totalFiles: number;
}

async function fetchScan(scanId: number): Promise<ScanData> {
  const response = await fetch(`/api/scans/${scanId}`);
  if (!response.ok) {
    throw new Error('Failed to fetch scan');
  }
  return response.json();
}
```

## Commit Message Format

Follow conventional commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Example:**
```
feat(scanner): Add support for compressed file scanning

- Detect and categorize .zip, .tar.gz, .7z files
- Add optional decompression for analysis
- Update file categorization logic

Closes #123
```

## Testing Requirements

### Backend

All new features must include:
- Unit tests for services/utilities
- Integration tests for API endpoints
- Minimum 80% code coverage

```python
# Example test
@pytest.mark.asyncio
async def test_create_scan():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/scans", json={
            "path": "/test/path",
            "max_depth": 5
        })
        assert response.status_code == 201
        data = response.json()
        assert data["path"] == "/test/path"
        assert data["status"] == "pending"
```

### Frontend

- Component tests with React Testing Library
- E2E tests for critical flows (optional)

## Documentation Requirements

Update documentation when:
- Adding new API endpoints → Update `docs/API.md`
- Adding new features → Update `README.md`
- Changing configuration → Update `.env.example` and docs
- Adding dependencies → Update `requirements.txt` or `package.json`

## Review Process

1. Code must pass all tests
2. Code must be formatted correctly
3. Documentation must be updated
4. At least one approval required
5. All CI checks must pass

## Architecture Guidelines

### Service Layer

- Keep services focused and single-purpose
- Use dependency injection
- Make services testable
- Handle errors gracefully

### API Layer

- Use Pydantic for request/response validation
- Return consistent error formats
- Use appropriate HTTP status codes
- Add OpenAPI documentation

### Database Layer

- Use async SQLAlchemy
- Add appropriate indexes
- Use migrations for schema changes
- Never commit direct SQL (use ORM)

## Common Tasks

### Adding New LLM Provider

1. Create provider class in `app/services/llm_service.py`
2. Extend `BaseLLMProvider`
3. Add configuration in `app/core/config.py`
4. Update documentation
5. Add tests

### Adding New Analysis Mode

1. Update analyzer prompts in `app/services/analyzer.py`
2. Add mode to settings
3. Update API schema
4. Test with different providers
5. Document in API.md

### Adding New Recommendation Type

1. Add type to `Recommendation` model
2. Update analyzer parsing logic
3. Create execution handler (future phase)
4. Add UI components (future phase)
5. Document behavior

## Questions?

For questions or issues:
1. Check existing documentation
2. Review similar code in the project
3. Check git history for context
4. Ask in team chat

## License

See LICENSE file. This is proprietary software owned by LMP HQ.
