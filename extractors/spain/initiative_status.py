import re

from tipi_data.models.initiative import Initiative


def get_current_status(reference):
    try:
        initiative = Initiative.all.get(reference=reference)
        if not initiative:
            return ''
        return initiative['status']
    except Exception:
        return ''

def has_finished(reference):
    NOT_FINAL_STATUS = [
            'En tramitación',
            'Desconocida'
            ]
    if get_current_status(reference) in NOT_FINAL_STATUS:
        return False
    return True
