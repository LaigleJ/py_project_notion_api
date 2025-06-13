from functools import wraps
from datetime import datetime
from colorama import Fore, Style, init
init(autoreset=True)

def log_action(nom_fonction):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            maintenant = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"{Fore.CYAN}🔍 [{maintenant}] – Début de `{nom_fonction}`")
            result = func(*args, **kwargs)
            print(f"{Fore.GREEN}✅ [{nom_fonction}] terminé avec succès\n")
            return result
        return wrapper
    return decorator