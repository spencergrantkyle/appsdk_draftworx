"""
Draftworx MCP Server - Main application
Ported from Cloudflare Workers TypeScript implementation to FastMCP/Python
"""

import json
from typing import List, Optional
import httpx
from mcp.server.fastmcp import FastMCP

from config import get_config, validate_config
from models import (
    TrialBalanceEntryInput,
    CashbookEntryInput,
    JournalEntryInput,
)
from utils import (
    map_to_dto,
    fetch_and_filter_data,
    transform_cashbook_entry,
    transform_journal_entry,
)

# Initialize FastMCP server
mcp = FastMCP("Draftworx Cloud MCP Server")

# Get configuration
config = get_config()

# Define fields for each DTO type (from index.ts)
PRACTICE_FIELDS = ['id', 'name', 'telephone', 'mobile', 'email', 'address1', 'address2', 'address3', 'address4', 'addressCode']
CLIENT_FIELDS = ['id', 'name', 'taxYear']
FINANCIAL_YEAR_FIELDS = ['id', 'start', 'end', 'current', 'year']
TRIAL_BALANCE_FIELDS = [
    'id',
    'account',
    'name',
    'leadReference',
    'workingPaperReference',
    'openingBalance',
    'accountMapping'
]
CASHBOOK_ENTRY_LINE_FIELDS = [
    'id',
    'date',
    'description',
    'exclusive',
    'tax',
    'total',
    'useTax',
    'order',
    'account',
    'sourceId'
]
CASHBOOK_ENTRY_FIELDS = [
    'id',
    'exclusive',
    'tax',
    'total',
    'bankAccount',
    'taxAccount',
    'lines'
]
JOURNAL_ENTRY_LINE_FIELDS = [
    'id',
    'date',
    'amount',
    'order',
    'account'
]
JOURNAL_ENTRY_FIELDS = [
    'id',
    'adjustmentType',
    'description',
    'reference',
    'number',
    'status',
    'exportSourceId',
    'exportMessage',
    'lines'
]


# Temporary access token storage (in production, this would come from OAuth)
# For now, we'll use environment variable or parameter
ACCESS_TOKEN: Optional[str] = None


def get_headers() -> dict:
    """Get common headers for API requests"""
    headers = {
        "PracticeId": config.draftworx_practice_id,
        "ClientId": config.draftworx_client_id,
    }
    if ACCESS_TOKEN:
        headers["Authorization"] = f"Bearer {ACCESS_TOKEN}"
    return headers


async def get_financial_year_id(year: Optional[int] = None) -> str:
    """
    Get financial year ID by year number or return default.

    Args:
        year: Optional year to look up

    Returns:
        Financial year ID
    """
    if not year:
        return config.draftworx_financialyear_id

    # Fetch all financial years and find matching one
    response = await list_financial_years()
    if response.get("isError"):
        raise Exception("Failed to fetch financial years")

    # Parse the JSON response
    content = response["content"][0]["text"]
    financial_years = json.loads(content)

    # Find matching year
    for fy in financial_years:
        if fy.get("year") == year:
            return fy["id"]

    raise Exception(f"No financial year found for year {year}")


# MCP Tools

@mcp.tool()
async def list_practices() -> str:
    """Lists all Draftworx Practices with contact information"""
    url = f"{config.api_server_url}/practices"

    response = await fetch_and_filter_data(
        url=url,
        headers=get_headers(),
        transform_fn=lambda practice: map_to_dto(practice, PRACTICE_FIELDS),
        access_token=ACCESS_TOKEN
    )

    # Return the text content directly for MCP
    return response["content"][0]["text"]


@mcp.tool()
async def list_clients() -> str:
    """Lists all Draftworx Clients"""
    url = f"{config.api_server_url}/clients"

    response = await fetch_and_filter_data(
        url=url,
        headers=get_headers(),
        transform_fn=lambda client: map_to_dto(client, CLIENT_FIELDS),
        access_token=ACCESS_TOKEN
    )

    return response["content"][0]["text"]


@mcp.tool()
async def current_client() -> str:
    """Returns the current Draftworx Client"""
    url = f"{config.api_server_url}/clients/getCurrent"

    response = await fetch_and_filter_data(
        url=url,
        headers=get_headers(),
        transform_fn=lambda client: map_to_dto(client, CLIENT_FIELDS),
        is_single=True,
        access_token=ACCESS_TOKEN
    )

    return response["content"][0]["text"]


@mcp.tool()
async def list_financial_years() -> str:
    """Lists all Draftworx Financial Years"""
    url = f"{config.api_server_url}/financialyears"

    def transform_financial_year(fy: dict) -> dict:
        mapped = map_to_dto(fy, FINANCIAL_YEAR_FIELDS)
        # Extract year from end date
        if fy.get('end'):
            from datetime import datetime
            end_date = datetime.fromisoformat(fy['end'].replace('Z', '+00:00'))
            mapped['year'] = end_date.year
        return mapped

    response = await fetch_and_filter_data(
        url=url,
        headers=get_headers(),
        transform_fn=transform_financial_year,
        access_token=ACCESS_TOKEN
    )

    return response["content"][0]["text"]


@mcp.tool()
async def list_trial_balance_entries(year: Optional[int] = None) -> str:
    """
    Lists all Trial Balance Entries for the specified year or current financial year.

    Args:
        year: Optional year to filter by (e.g., 2024)
    """
    financial_year_id = await get_financial_year_id(year)
    url = f"{config.api_server_url}/financialData/{financial_year_id}?$expand=*"

    response = await fetch_and_filter_data(
        url=url,
        headers=get_headers(),
        transform_fn=lambda tb: map_to_dto(tb, TRIAL_BALANCE_FIELDS),
        access_token=ACCESS_TOKEN
    )

    return response["content"][0]["text"]


@mcp.tool()
async def list_cashbook_entries(year: Optional[int] = None) -> str:
    """
    Lists all Cashbook Entries for the specified year or current financial year.

    Args:
        year: Optional year to filter by (e.g., 2024)
    """
    financial_year_id = await get_financial_year_id(year)
    url = f"{config.api_server_url}/cashbookEntries?$expand=*/account&$filter=financialYearId eq {financial_year_id}"

    response = await fetch_and_filter_data(
        url=url,
        headers=get_headers(),
        transform_fn=lambda entry: transform_cashbook_entry(entry, CASHBOOK_ENTRY_FIELDS, CASHBOOK_ENTRY_LINE_FIELDS),
        access_token=ACCESS_TOKEN
    )

    return response["content"][0]["text"]


@mcp.tool()
async def list_journal_entries(year: Optional[int] = None) -> str:
    """
    Lists all Journal Entries for the specified year or current financial year.

    Args:
        year: Optional year to filter by (e.g., 2024)
    """
    financial_year_id = await get_financial_year_id(year)
    url = f"{config.api_server_url}/journalEntries?$expand=*/account&$filter=financialYearId eq {financial_year_id}"

    response = await fetch_and_filter_data(
        url=url,
        headers=get_headers(),
        transform_fn=lambda entry: transform_journal_entry(entry, JOURNAL_ENTRY_FIELDS, JOURNAL_ENTRY_LINE_FIELDS),
        access_token=ACCESS_TOKEN
    )

    return response["content"][0]["text"]


@mcp.tool()
async def save_trial_balance_entries(entries: List[TrialBalanceEntryInput]) -> str:
    """
    Saves multiple Trial Balance Entries.

    Args:
        entries: List of trial balance entries to save
    """
    # Add financial year and client IDs to each entry
    entries_data = [
        {
            **entry.model_dump(),
            "financialYearId": config.draftworx_financialyear_id,
            "clientId": config.draftworx_client_id
        }
        for entry in entries
    ]

    url = f"{config.api_server_url}/trialBalanceEntries"
    headers = {
        **get_headers(),
        "Content-Type": "application/json"
    }
    if ACCESS_TOKEN:
        headers["Authorization"] = f"Bearer {ACCESS_TOKEN}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=entries_data, headers=headers)
            response.raise_for_status()
        except httpx.HTTPError as e:
            return json.dumps({
                "error": f"Failed to save trial balance entries: {str(e)}",
                "isError": True
            }, indent=2)

    saved_entries = response.json()
    # Transform to DTOs
    if isinstance(saved_entries, list):
        result = [map_to_dto(entry, TRIAL_BALANCE_FIELDS) for entry in saved_entries]
    else:
        result = [map_to_dto(saved_entries, TRIAL_BALANCE_FIELDS)]

    return json.dumps(result, indent=2)


# Note: save_cashbook_entry and save_journal_entry are commented out in the original
# Keeping them here for completeness but not registering as tools

async def save_cashbook_entry(entry: CashbookEntryInput) -> str:
    """
    Saves a Cashbook Entry (not currently active).

    Args:
        entry: Cashbook entry to save
    """
    entry_data = {
        **entry.model_dump(),
        "financialYearId": config.draftworx_financialyear_id,
        "clientId": config.draftworx_client_id
    }

    url = f"{config.api_server_url}/cashbookEntries"
    headers = {
        **get_headers(),
        "Content-Type": "application/json"
    }
    if ACCESS_TOKEN:
        headers["Authorization"] = f"Bearer {ACCESS_TOKEN}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=entry_data, headers=headers)
            response.raise_for_status()
        except httpx.HTTPError as e:
            return json.dumps({
                "error": f"Failed to save cashbook entry: {str(e)}",
                "isError": True
            }, indent=2)

    saved_entry = response.json()
    result = map_to_dto(saved_entry, CASHBOOK_ENTRY_FIELDS)

    return json.dumps(result, indent=2)


async def save_journal_entry(entry: JournalEntryInput) -> str:
    """
    Saves a Journal Entry (not currently active).

    Args:
        entry: Journal entry to save
    """
    entry_data = {
        **entry.model_dump(),
        "financialYearId": config.draftworx_financialyear_id,
        "clientId": config.draftworx_client_id
    }

    url = f"{config.api_server_url}/journalEntries"
    headers = {
        **get_headers(),
        "Content-Type": "application/json"
    }
    if ACCESS_TOKEN:
        headers["Authorization"] = f"Bearer {ACCESS_TOKEN}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=entry_data, headers=headers)
            response.raise_for_status()
        except httpx.HTTPError as e:
            return json.dumps({
                "error": f"Failed to save journal entry: {str(e)}",
                "isError": True
            }, indent=2)

    saved_entry = response.json()
    result = map_to_dto(saved_entry, JOURNAL_ENTRY_FIELDS)

    return json.dumps(result, indent=2)


if __name__ == "__main__":
    # Validate configuration before starting
    try:
        validate_config()
    except ValueError as e:
        print(f"Configuration error: {e}")
        exit(1)

    # Run the MCP server
    mcp.run()
