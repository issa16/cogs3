from system.models import System


def get_system(system):
    valid_systems = {
        'CF': 'Hawk',
        'SW': 'Sunbird',
    }
    try:
        return System.objects.get(name__iexact=valid_systems[system])
    except Exception:
        raise Exception(f"System '{system}' not found.")
