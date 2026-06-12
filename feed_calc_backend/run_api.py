# run_api.py
import os
import sys
import traceback
from pathlib import Path
from waitress import serve
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

# 強制讀取單機版設定
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.desktop')

def _apilog(msg):
    print(msg, flush=True)
    if getattr(sys, 'frozen', False):
        log_path = Path(os.getenv('APPDATA', '')) / 'FeedCalc' / 'startup.log'
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(msg + '\n')
        except Exception:
            pass

_apilog(f"[run_api] starting, frozen={getattr(sys, 'frozen', False)}, __name__={__name__}")

try:
    application = get_wsgi_application()
    _apilog("[run_api] wsgi application ready")
except Exception:
    _apilog(f"[run_api] ERROR loading wsgi application:\n{traceback.format_exc()}")
    raise

# 設定 Tauri 專屬通訊 Port
PORT = 8042

def _load_seed_fixture():
    """Load bundled ingredient seed on first install (empty DB)."""
    try:
        from ingredients.models import Ingredient
        if Ingredient.objects.count() > 0:
            _apilog("[run_api] ingredients already seeded, skipping fixture load")
            return
        _apilog("[run_api] ingredients table empty — loading seed fixture...")
        if getattr(sys, 'frozen', False):
            fixture_path = Path(sys._MEIPASS) / 'ingredients' / 'fixtures' / 'crawled_seed.json'
        else:
            fixture_path = Path(__file__).parent / 'ingredients' / 'fixtures' / 'crawled_seed.json'
        if not fixture_path.exists():
            _apilog(f"[run_api] WARNING: seed fixture not found at {fixture_path}")
            return
        call_command('loaddata', str(fixture_path), verbosity=1)
        _apilog(f"[run_api] seed fixture loaded from {fixture_path}")
    except Exception:
        _apilog(f"[run_api] ERROR loading seed fixture:\n{traceback.format_exc()}")


if __name__ == '__main__':
    _apilog("[run_api] __main__ block entered")
    try:
        _apilog("[run_api] running migrations...")
        call_command('migrate', '--no-input', verbosity=0)
        _apilog("[run_api] migrations done")
    except Exception:
        _apilog(f"[run_api] ERROR during migrate:\n{traceback.format_exc()}")
        raise
    _load_seed_fixture()
    _apilog(f"[run_api] calling serve() on port {PORT}")
    serve(application, host='127.0.0.1', port=PORT, expose_tracebacks=True)