# Testing Guidelines for StrategyBuilder

## Overview
Comprehensive testing should cover the full user workflow from creation to retrieval to usage, with proper validation and error handling at each step.

## Test Structure

### 1. **Unit Tests** (Repository/Service Layer)
- Test business logic directly without API server
- Use temporary databases for isolation
- Fast execution, no network dependencies

### 2. **Integration Tests** (Full Workflow)
- Test complete user workflows
- Example: Create preset → Retrieve preset → Use in backtest → Verify results

### 3. **Validation Tests**
- Test invalid inputs return proper error messages
- Test field validation (e.g., string where number expected)
- Test boundary conditions

## What Every Test Should Cover

### ✅ **CRUD Operations**
```python
def test_create_and_retrieve():
    """Create entity, then retrieve it and verify all fields match"""
    pass

def test_list_with_filters():
    """Create multiple entities, test listing with various filters"""
    pass

def test_update():
    """Create entity, update fields, verify changes persisted"""
    pass

def test_delete():
    """Create entity, delete it, verify it's gone"""
    pass
```

### ✅ **Validation**
```python
def test_duplicate_prevention():
    """Ensure unique constraints are enforced"""
    pass

def test_invalid_input():
    """Test that invalid data returns proper error messages"""
    # Example: string where number expected should return
    # "Field 'cash' expects a number, got string 'abc'"
    pass

def test_missing_required_fields():
    """Test that missing required fields are caught"""
    pass
```

### ✅ **Complete Workflows**
```python
def test_full_preset_workflow():
    """
    1. Create preset with specific parameters
    2. Retrieve preset and verify parameters
    3. Use preset in a backtest
    4. Verify backtest results match expected strategy behavior
    5. Update preset parameters
    6. Run backtest again with updated parameters
    7. Verify results changed appropriately
    """
    pass
```

### ✅ **Edge Cases**
```python
def test_empty_results():
    """Test behavior when no data matches query"""
    pass

def test_large_datasets():
    """Test performance with realistic data volumes"""
    pass

def test_concurrent_access():
    """Test that concurrent operations don't corrupt data"""
    pass
```

## Domain-Specific Testing Patterns

### **Presets**
1. Create preset with strategy + parameters
2. Retrieve preset and verify all fields
3. Use preset in backtest - verify strategy executes correctly
4. Update preset parameters
5. Verify updated preset produces different backtest results
6. Delete preset and verify it's removed

### **Watchlists**
1. Create watchlist for ticker with strategy
2. Add positions (open)
3. Retrieve positions and verify status
4. Close positions with P&L
5. Update watchlist performance metrics
6. List watchlists with filters (active, by ticker)

### **Portfolios**
1. Create portfolio with multiple holdings
2. Verify weights sum to 100%
3. Update holdings
4. Retrieve portfolio and verify structure
5. Delete portfolio

### **Market Data**
1. Request data for ticker + date range + interval
2. Verify data cached properly
3. Request same data - verify cache hit (no download)
4. Request expanded range - verify only missing data downloaded
5. Request different interval - verify separate cache
6. Verify cache metadata accurate

### **Backtests**
1. Create backtest request with valid parameters
2. Execute backtest
3. Verify results structure (trades, metrics, equity curve)
4. Test invalid parameters return proper errors
5. Test with preset - verify preset parameters used
6. Compare multiple strategy results

### **Market Scans**
1. Scan S&P 500 with strategy
2. Verify top performers identified
3. Verify results sorted correctly
4. Test with custom ticker list
5. Verify caching used for repeated scans

## Error Message Standards

### **Good Error Messages**
✅ `"Field 'cash' expects a positive number, got -1000"`
✅ `"Ticker 'XYZ' not found in S&P 500 list"`
✅ `"Start date '2025-01-01' must be before end date '2024-01-01'"`
✅ `"Strategy 'invalid_strategy' not found. Available strategies: [...]"`

### **Bad Error Messages**
❌ `"Invalid input"`
❌ `"Error"`
❌ `"Validation failed"`
❌ `"TypeError: 'str' object cannot be interpreted as an integer"`

## Test Output Standards

### **Good Test Output**
```
[PASS] Create preset (ID: 123)
[PASS] Retrieve preset matches created data
[PASS] Backtest with preset executes successfully (15 trades, 12.5% return)
[PASS] Update preset parameters (fast: 12 → 26)
[PASS] Backtest with updated preset shows different results (8 trades, 8.2% return)
[PASS] Delete preset successful
```

### **Bad Test Output**
```
Test 1: OK
Test 2: OK
Test 3: OK
```

## Running Tests

### **Individual Domain**
```bash
python tests/domains/watchlists/test_watchlists.py
```

### **All Tests**
```bash
python src/shared/utils/test_everything.py
```

### **With Verbose Output**
```bash
python tests/domains/presets/test_presets.py --verbose
```

## Current Test Status

### ✅ **Comprehensive Tests** (Full workflows + validation)
- Watchlists (6/6 tests) - Repository layer, full CRUD, positions, validation

### 🔄 **Partial Tests** (Missing validation or workflows)
- Strategies (4/4 tests) - Basic import and config tests only
- Run History (4/4 tests) - CRUD tests but no workflow testing
- Market Scans (3/3 tests) - Import and model tests only
- Presets (3/3 tests) - CRUD tests but no usage workflow

### ❌ **Needs Improvement** (Requires API server or incomplete)
- Backtests - Currently requires running API server
- Optimizations - Currently requires running API server
- Portfolios - Currently requires running API server
- Market Data - Currently requires running API server

## Recommended Next Steps

1. **Update Market Data Tests**
   - Test caching functionality directly
   - Verify smart gap detection works
   - Test different intervals cached separately

2. **Update Portfolio Tests**
   - Test repository layer directly
   - Full CRUD workflow
   - Holdings validation

3. **Create Integration Tests**
   - Preset → Backtest workflow
   - Market Scan → Results verification
   - Watchlist → Position tracking

4. **Add Validation Tests to All Domains**
   - Invalid field types
   - Missing required fields
   - Constraint violations
   - Proper error messages

5. **Performance Tests**
   - S&P 500 scan timing
   - Cache hit/miss performance
   - Large backtest execution
