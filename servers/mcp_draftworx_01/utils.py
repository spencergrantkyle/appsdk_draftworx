"""
Utility functions for Draftworx MCP server.
Ported from utils.ts
"""

from typing import Dict, Any, List, Optional, TypeVar, Callable
import httpx
from pydantic import BaseModel


T = TypeVar('T', bound=BaseModel)
U = TypeVar('U', bound=BaseModel)


def remove_null_fields(obj: Dict[str, Any]) -> Dict[str, Any]:
    """
    Removes null/None fields from a dictionary while keeping other falsy values (0, False, empty strings).

    Args:
        obj: The dictionary to remove null fields from

    Returns:
        A new dictionary with null fields removed
    """
    return {k: v for k, v in obj.items() if v is not None}


def map_to_dto(source: Dict[str, Any], target_fields: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Maps a source dictionary to a DTO by filtering fields.

    Args:
        source: The source dictionary to map from
        target_fields: Optional list of field names to include in output. If not provided, all fields are included.

    Returns:
        The mapped dictionary with only specified fields and no null values
    """
    if not source:
        return {}

    # If no target fields specified, return all non-null fields
    if not target_fields:
        return remove_null_fields(source)

    # Only include fields that are in the target_fields list
    mapped = {}
    for key in target_fields:
        if key in source and source[key] is not None:
            mapped[key] = source[key]

    return remove_null_fields(mapped)


async def fetch_and_filter_data(
    url: str,
    headers: Dict[str, str],
    transform_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
    is_single: bool = False,
    access_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generic function to fetch and filter data from the Draftworx API.

    Args:
        url: The API endpoint URL
        headers: Request headers
        transform_fn: Function to transform input data to output format
        is_single: Whether to expect a single item response instead of an array
        access_token: Optional access token to add to headers

    Returns:
        Formatted API response with filtered fields in MCP format
    """
    # Add authorization header if access token provided
    if access_token:
        headers = {**headers, "Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
        except httpx.HTTPError as e:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Failed to fetch data: {str(e)}"
                }],
                "isError": True
            }

    data = response.json()
    items = [data] if is_single else data

    # Transform and remove null fields from each item
    filtered_items = [remove_null_fields(transform_fn(item)) for item in items]

    # Return in MCP format
    import json
    return {
        "content": [{
            "type": "text",
            "text": json.dumps(filtered_items[0] if is_single else filtered_items, indent=2)
        }]
    }


def format_account_reference(account_obj: Optional[Dict[str, Any]]) -> Optional[str]:
    """
    Formats an account object as "code - name".

    Args:
        account_obj: Dictionary with 'account' and 'name' fields

    Returns:
        Formatted string like "1000 - Cash" or None if account_obj is None
    """
    if not account_obj:
        return None

    account_code = account_obj.get('account', '')
    account_name = account_obj.get('name', '')

    return f"{account_code} - {account_name}".strip()


def transform_cashbook_entry(entry: Dict[str, Any], cashbook_entry_fields: List[str], line_fields: List[str]) -> Dict[str, Any]:
    """
    Transforms a cashbook entry from API format to DTO format.

    Args:
        entry: Raw cashbook entry from API
        cashbook_entry_fields: Fields to include in main entry
        line_fields: Fields to include in lines

    Returns:
        Transformed cashbook entry with formatted account references
    """
    mapped_entry = map_to_dto(entry, cashbook_entry_fields)

    # Map bankAccount combining account and name
    if entry.get('bankAccount'):
        mapped_entry['bankAccount'] = format_account_reference(entry['bankAccount'])

    # Map taxAccount combining account and name
    if entry.get('taxAccount'):
        mapped_entry['taxAccount'] = format_account_reference(entry['taxAccount'])

    # Map lines including account information
    if entry.get('lines'):
        mapped_entry['lines'] = []
        for line in entry['lines']:
            mapped_line = map_to_dto(line, line_fields)
            if line.get('account'):
                mapped_line['account'] = format_account_reference(line['account'])
            mapped_entry['lines'].append(mapped_line)

    return mapped_entry


def transform_journal_entry(entry: Dict[str, Any], journal_entry_fields: List[str], line_fields: List[str]) -> Dict[str, Any]:
    """
    Transforms a journal entry from API format to DTO format.

    Args:
        entry: Raw journal entry from API
        journal_entry_fields: Fields to include in main entry
        line_fields: Fields to include in lines

    Returns:
        Transformed journal entry with formatted account references and adjustment type text
    """
    from models import AdjustmentType, get_adjustment_type_text

    mapped_entry = map_to_dto(entry, journal_entry_fields)

    # Convert adjustment type enum to text
    if 'adjustmentType' in entry:
        try:
            adj_type = AdjustmentType(entry['adjustmentType'])
            mapped_entry['adjustmentType'] = get_adjustment_type_text(adj_type)
        except (ValueError, KeyError):
            mapped_entry['adjustmentType'] = 'Unknown'

    # Map lines including account information
    if entry.get('lines'):
        mapped_entry['lines'] = []
        for line in entry['lines']:
            mapped_line = map_to_dto(line, line_fields)
            if line.get('account'):
                mapped_line['account'] = format_account_reference(line['account'])
            mapped_entry['lines'].append(mapped_line)

    return mapped_entry
