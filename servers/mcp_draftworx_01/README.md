# Draftworx Cloud MCP Server

A Model Context Protocol (MCP) server for Draftworx cloud accounting platform. This server provides AI assistants with access to Draftworx accounting data through a standardized interface.

**Ported from:** Cloudflare Workers TypeScript implementation
**Framework:** FastMCP (Python)
**API Version:** v0.5.0

## Features

- **Practice & Client Management** - Access practice and client information
- **Financial Years** - Query financial year periods
- **Trial Balance** - Read and write trial balance entries
- **Cashbook** - Access cashbook entries and transactions
- **Journal Entries** - Query journal entries and adjustments
- **Data Validation** - Pydantic models for type safety
- **Environment-based Configuration** - Secure credential management

## Project Structure

```
servers/mcp_draftworx_01/
├── main.py              # FastMCP server with MCP tools
├── models.py            # Pydantic models (DTOs and input schemas)
├── utils.py             # Utility functions for data transformation
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
├── .env.example         # Example environment variables
└── README.md            # This file
```

## Installation

### 1. Prerequisites

- Python 3.11 or higher
- pip or uv package manager
- Access to Draftworx API credentials

### 2. Create Virtual Environment

```bash
cd servers/mcp_draftworx_01
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` and set the following required variables:

```bash
# Required
API_SERVER_URL=https://api.cloud.draftworx.com
DRAFTWORX_PRACTICE_ID=your-practice-guid
DRAFTWORX_CLIENT_ID=your-client-guid
DRAFTWORX_FINANCIALYEAR_ID=your-financial-year-guid

# Optional (for OAuth in future)
AUTH_SERVER_URL=https://login.cloud.draftworx.com
CLIENT_ID=your-oauth-client-id
CLIENT_SECRET=your-oauth-client-secret
```

## Usage

### Running the Server

#### Standard Mode

```bash
python main.py
```

#### Development Mode with Auto-reload

```bash
# Using uvicorn (if installed)
uvicorn main:mcp --reload
```

### Testing with MCP Inspector

The MCP SDK provides an inspector tool for testing:

```bash
# Install MCP inspector
pip install mcp-inspector

# Run inspector
mcp-inspector python main.py
```

## Available MCP Tools

### 1. `list-practices`

Lists all Draftworx practices with contact information.

**Parameters:** None

**Returns:** Array of practices
```json
[{
  "id": "guid",
  "name": "Practice Name",
  "email": "contact@practice.com",
  "telephone": "+1234567890",
  "address1": "123 Main St",
  ...
}]
```

---

### 2. `list-clients`

Lists all clients for the configured practice.

**Parameters:** None

**Returns:** Array of clients
```json
[{
  "id": "guid",
  "name": "Client Name",
  "taxYear": "2024"
}]
```

---

### 3. `current-client`

Returns the currently configured client.

**Parameters:** None

**Returns:** Single client object

---

### 4. `list-financial-years`

Lists all financial years for the current client.

**Parameters:** None

**Returns:** Array of financial years
```json
[{
  "id": "guid",
  "start": "2024-01-01",
  "end": "2024-12-31",
  "year": 2024,
  "current": true
}]
```

---

### 5. `list-trial-balance-entries`

Lists trial balance entries for a financial year.

**Parameters:**
- `year` (optional, int): Financial year to query (e.g., 2024). Defaults to current year.

**Returns:** Array of trial balance entries
```json
[{
  "id": "guid",
  "account": "1000",
  "name": "Cash",
  "openingBalance": 10000.00,
  "leadReference": "A1",
  "workingPaperReference": "WP-001"
}]
```

---

### 6. `list-cashbook-entries`

Lists cashbook entries for a financial year.

**Parameters:**
- `year` (optional, int): Financial year to query

**Returns:** Array of cashbook entries with lines
```json
[{
  "id": "guid",
  "bankAccount": "1000 - Cash",
  "exclusive": 1000.00,
  "tax": 150.00,
  "total": 1150.00,
  "lines": [{
    "account": "4000 - Sales",
    "description": "Invoice #123",
    "exclusive": 1000.00,
    "tax": 150.00,
    "total": 1150.00
  }]
}]
```

---

### 7. `list-journal-entries`

Lists journal entries for a financial year.

**Parameters:**
- `year` (optional, int): Financial year to query

**Returns:** Array of journal entries with lines
```json
[{
  "id": "guid",
  "adjustmentType": "Normal Adjusting",
  "description": "Year-end adjustment",
  "reference": "ADJ-001",
  "lines": [{
    "account": "1000 - Cash",
    "amount": 500.00,
    "date": "2024-12-31"
  }]
}]
```

---

### 8. `save-trial-balance-entries`

Saves one or more trial balance entries.

**Parameters:**
- `entries` (array): List of trial balance entries to save

**Input Schema:**
```json
[{
  "account": "1000",
  "name": "Cash",
  "openingBalance": 10000.00,
  "leadReference": "A1",
  "workingPaperReference": "WP-001"
}]
```

**Returns:** Saved entries with IDs

---

## Data Models

### Key Enums

- **AccountType**: Unknown, BalanceSheet, IncomeStatement
- **AccountCategory**: CurrentAssets, Income, Expenses, etc.
- **AdjustmentType**: Normal Adjusting, Drafting, Overs and Unders, etc.

### Main DTOs

- `PracticeDTO` - Practice information
- `ClientDTO` - Client basics
- `FinancialYearDTO` - Financial period
- `TrialBalanceEntryDTO` - Trial balance line item
- `CashbookEntryDTO` / `CashbookEntryLineDTO` - Cashbook transactions
- `JournalEntryDTO` / `JournalEntryLineDTO` - Journal adjustments

See `models.py` for complete schemas.

## Configuration

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `API_SERVER_URL` | Yes | Draftworx API base URL | `https://api.cloud.draftworx.com` |
| `DRAFTWORX_PRACTICE_ID` | Yes | Practice GUID | - |
| `DRAFTWORX_CLIENT_ID` | Yes | Client GUID | - |
| `DRAFTWORX_FINANCIALYEAR_ID` | Yes | Default financial year GUID | - |
| `AUTH_SERVER_URL` | No | OAuth server URL | `https://login.cloud.draftworx.com` |
| `CLIENT_ID` | No | OAuth client ID | - |
| `CLIENT_SECRET` | No | OAuth client secret | - |
| `PORT` | No | Server port | `8000` |
| `HOST` | No | Server host | `0.0.0.0` |

### Authentication

**Current Implementation:** The server expects an access token to be set. OAuth flow is not yet implemented in this Python version.

**Future:** Will implement OAuth 2.0 flow similar to the original Cloudflare Workers version.

**Temporary Workaround:** You can manually set `ACCESS_TOKEN` in `main.py` for testing, or implement custom authentication.

## Development

### Code Organization

- **main.py** - MCP server initialization and tool definitions
- **models.py** - Pydantic models for request/response validation
- **utils.py** - Reusable utility functions for data transformation
- **config.py** - Environment variable management with validation

### Adding New Tools

1. Define input/output models in `models.py`
2. Add field mappings (e.g., `NEW_ENTITY_FIELDS`)
3. Implement tool function in `main.py`
4. Decorate with `@mcp.tool()`

Example:
```python
@mcp.tool()
async def my_new_tool(param: str) -> str:
    """Tool description for AI"""
    # Implementation
    return json.dumps(result)
```

## Troubleshooting

### Missing Dependencies

```bash
pip install --upgrade -r requirements.txt
```

### Configuration Errors

```
ValueError: Missing required environment variables: DRAFTWORX_PRACTICE_ID
```

**Solution:** Ensure all required variables in `.env` are set.

### Connection Errors

```
Failed to fetch data: Connection timeout
```

**Solution:** Check `API_SERVER_URL` and network connectivity.

### Import Errors

```
ModuleNotFoundError: No module named 'mcp'
```

**Solution:** Install MCP SDK: `pip install mcp`

## Migration Notes

This server was ported from the original Cloudflare Workers TypeScript implementation. Key differences:

1. **Runtime**: Cloudflare Workers → Python/FastMCP
2. **OAuth**: Not yet implemented (was using `@cloudflare/workers-oauth-provider`)
3. **Framework**: Hono → FastMCP
4. **Validation**: Zod → Pydantic
5. **HTTP Client**: fetch → httpx

## Roadmap

- [ ] Implement OAuth 2.0 authentication flow
- [ ] Add support for `save-cashbook-entry` tool
- [ ] Add support for `save-journal-entry` tool
- [ ] Add widget integration for data visualization
- [ ] Add comprehensive error handling and logging
- [ ] Add unit tests and integration tests
- [ ] Add rate limiting and caching

## Contributing

When making changes:

1. Update models in `models.py` if API schema changes
2. Keep field mappings in sync with DTOs
3. Add docstrings to all tools
4. Update this README with new tools or configuration

## License

Internal use only - Draftworx proprietary.

## Support

For issues or questions:
- Check the main repository documentation
- Review the original TypeScript implementation
- Contact the Draftworx development team
