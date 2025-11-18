#!/usr/bin/env python3
"""
Simple setup validation script for Draftworx MCP Server.
Run this to verify your configuration before starting the server.
"""

import sys
from pathlib import Path


def test_imports():
    """Test that all required packages are installed"""
    print("Testing imports...")

    try:
        import mcp
        print("✓ mcp package installed")
    except ImportError:
        print("✗ mcp package NOT installed - run: pip install mcp")
        return False

    try:
        import httpx
        print("✓ httpx package installed")
    except ImportError:
        print("✗ httpx package NOT installed - run: pip install httpx")
        return False

    try:
        import pydantic
        print("✓ pydantic package installed")
    except ImportError:
        print("✗ pydantic package NOT installed - run: pip install pydantic")
        return False

    try:
        from pydantic_settings import BaseSettings
        print("✓ pydantic-settings package installed")
    except ImportError:
        print("✗ pydantic-settings package NOT installed - run: pip install pydantic-settings")
        return False

    return True


def test_configuration():
    """Test that configuration loads correctly"""
    print("\nTesting configuration...")

    try:
        from config import get_config, validate_config
        config = get_config()
        print(f"✓ Configuration loaded")
        print(f"  - API Server: {config.api_server_url}")
        print(f"  - Practice ID: {config.draftworx_practice_id[:8] + '...' if config.draftworx_practice_id else 'NOT SET'}")
        print(f"  - Client ID: {config.draftworx_client_id[:8] + '...' if config.draftworx_client_id else 'NOT SET'}")

        # Try to validate
        try:
            validate_config()
            print("✓ Configuration is valid!")
            return True
        except ValueError as e:
            print(f"✗ Configuration validation failed: {e}")
            return False

    except Exception as e:
        print(f"✗ Failed to load configuration: {e}")
        return False


def test_models():
    """Test that models can be imported"""
    print("\nTesting models...")

    try:
        from models import (
            PracticeDTO,
            ClientDTO,
            FinancialYearDTO,
            TrialBalanceEntryInput,
            CashbookEntryInput,
            JournalEntryInput,
        )
        print("✓ All models imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import models: {e}")
        return False


def test_utils():
    """Test that utilities can be imported"""
    print("\nTesting utilities...")

    try:
        from utils import (
            remove_null_fields,
            map_to_dto,
            fetch_and_filter_data,
            format_account_reference,
        )
        print("✓ All utilities imported successfully")

        # Test remove_null_fields
        test_data = {"a": 1, "b": None, "c": 0, "d": False, "e": ""}
        result = remove_null_fields(test_data)
        expected = {"a": 1, "c": 0, "d": False, "e": ""}
        assert result == expected, f"remove_null_fields failed: {result} != {expected}"
        print("✓ remove_null_fields works correctly")

        return True
    except Exception as e:
        print(f"✗ Failed to test utilities: {e}")
        return False


def test_main():
    """Test that main module can be imported"""
    print("\nTesting main module...")

    try:
        import main
        print("✓ Main module imported successfully")
        print(f"✓ MCP server name: {main.mcp.name}")
        return True
    except Exception as e:
        print(f"✗ Failed to import main module: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Draftworx MCP Server - Setup Validation")
    print("=" * 60)

    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("\n⚠ Warning: .env file not found!")
        print("  Copy .env.example to .env and configure it before running the server.")
        print()

    tests = [
        ("Package Imports", test_imports),
        ("Configuration", test_configuration),
        ("Data Models", test_models),
        ("Utilities", test_utils),
        ("Main Module", test_main),
    ]

    results = []
    for name, test_fn in tests:
        try:
            result = test_fn()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Unexpected error in {name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:10} - {name}")

    all_passed = all(result for _, result in results)

    if all_passed:
        print("\n✓ All tests passed! Server is ready to run.")
        print("\nTo start the server, run:")
        print("  python main.py")
        return 0
    else:
        print("\n✗ Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Configure .env file: cp .env.example .env && edit .env")
        return 1


if __name__ == "__main__":
    sys.exit(main())
