from tipi_data.models.initiative import Initiative


UNKNOWN = 'Desconocida'

def get_current_status(reference):
    try:
        initiative = Initiative.all.filter(reference=reference).first()
        if initiative['status'] is None:
            return UNKNOWN
        return initiative['status']
    except Exception:
        return UNKNOWN

def has_finished(reference):
    NOT_FINAL_STATUS = [
            'En tramitación',
            UNKNOWN
            ]
    if get_current_status(reference) in NOT_FINAL_STATUS:
        return False
    return True
