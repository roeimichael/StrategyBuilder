"""
Test script for Presets domain endpoints.

Tests:
- GET /presets - List presets
- POST /presets - Create preset
- GET /presets/{id} - Get preset
- PATCH /presets/{id} - Update preset
- DELETE /presets/{id} - Delete preset
"""

import sys
import os
import tempfile

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))


def test_imports():
    """Test that preset components can be imported."""
    print("  Testing imports...")
    try:
        from src.domains.presets.repository import PresetRepository
        from src.domains.presets.models import CreatePresetRequest, PresetResponse
        print("  ✓ Preset components imported successfully")
        return True
    except Exception as e:
        print(f"  ✗ Failed to import components: {e}")
        return False


def test_config_loading():
    """Test that presets config loads correctly."""
    print("  Testing config loading...")
    try:
        from src.shared.utils.config_reader import ConfigReader

        config = ConfigReader.load_domain_config('presets')
        print(f"  ✓ Config loaded: MAX_PRESETS = {config.MAX_PRESETS}")
        print(f"    DB_NAME = {config.DB_NAME}")
        return True
    except Exception as e:
        print(f"  ✗ Config loading failed: {e}")
        return False


def test_preset_repository_crud():
    """Test PresetRepository CRUD operations."""
    print("  Testing PresetRepository CRUD...")
    try:
        from src.domains.presets.repository import PresetRepository
        from src.domains.presets.models import PortfolioHolding

        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            temp_db = f.name

        try:
            repo = PresetRepository(db_path=temp_db)

            # Create
            preset_data = {
                'name': 'Test Preset',
                'description': 'A test preset',
                'strategy': 'bollinger_bands_strategy',
                'parameters': {'period': 20, 'devfactor': 2.0},
                'interval': '1d',
                'cash': 10000.0
            }

            preset_id = repo.create_preset(preset_data)
            print(f"  ✓ Preset created with ID: {preset_id}")

            # Read
            retrieved = repo.get_preset_by_id(preset_id)
            if retrieved and retrieved['name'] == 'Test Preset':
                print("  ✓ Preset retrieved successfully")
            else:
                print("  ✗ Failed to retrieve preset")
                return False

            # Update
            updates = {'description': 'Updated description'}
            success = repo.update_preset(preset_id, updates)
            if success:
                print("  ✓ Preset updated successfully")
            else:
                print("  ✗ Failed to update preset")
                return False

            # List
            presets = repo.list_presets()
            if len(presets) == 1:
                print(f"  ✓ List presets successful ({len(presets)} preset)")
            else:
                print(f"  ✗ List presets unexpected count: {len(presets)}")
                return False

            # Delete
            deleted = repo.delete_preset(preset_id)
            if deleted:
                print("  ✓ Preset deleted successfully")
            else:
                print("  ✗ Failed to delete preset")
                return False

            return True

        finally:
            if os.path.exists(temp_db):
                os.unlink(temp_db)

    except Exception as e:
        print(f"  ✗ CRUD test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_tests():
    """Run all presets endpoint tests."""
    print("\n" + "=" * 60)
    print("Testing Presets Domain")
    print("=" * 60)

    tests = [
        test_imports,
        test_config_loading,
        test_preset_repository_crud,
    ]

    passed = 0
    failed = 0

    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1

    print(f"\n  Results: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
