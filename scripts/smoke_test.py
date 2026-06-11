import sys
import importlib

REQUIRED = ["pandas", "numpy", "sqlalchemy", "psycopg2", "yaml", "requests", "sklearn"]

ok = True
for pkg in REQUIRED:
    try:
        m = importlib.import_module(pkg)
        ver = getattr(m, "__version__", "ok")
        print(f"[OK] {pkg}: {ver}")
    except ImportError:
        print(f"[MISSING] {pkg}")
        ok = False

print()
print("python:", sys.executable)
if ok:
    print("[OK] All dependencies installed successfully!")
else:
    print("[ERROR] Some dependencies are missing.")
    sys.exit(1)
