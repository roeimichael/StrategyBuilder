import sys
print("Python path:", sys.executable)
print("=" * 80)

try:
    print("Testing imports...")
    from src.api.models import OptimizationRequest, OptimizationResponse, OptimizationResult
    print("✓ Models import successfully")
    print(f"  - OptimizationRequest: {OptimizationRequest}")
    print(f"  - OptimizationResponse: {OptimizationResponse}")
    print(f"  - OptimizationResult: {OptimizationResult}")
except Exception as e:
    print(f"✗ Failed to import models: {e}")
    sys.exit(1)

try:
    from src.core.optimizer import StrategyOptimizer
    print("✓ StrategyOptimizer imports successfully")
except Exception as e:
    print(f"✗ Failed to import StrategyOptimizer: {e}")
    sys.exit(1)

try:
    from src.api import main
    print("✓ main module imports successfully")

    # Check if the app has the optimize endpoint
    routes = [route.path for route in main.app.routes]
    print(f"\nRegistered routes: {routes}")

    if "/optimize" in routes:
        print("✓ /optimize endpoint is registered!")
    else:
        print("✗ /optimize endpoint NOT found in registered routes")

except Exception as e:
    print(f"✗ Failed to import main: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("All imports successful!")
