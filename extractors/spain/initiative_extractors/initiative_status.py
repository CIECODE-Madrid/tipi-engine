import re

from tipi_data.models.initiative import Initiative

from .status_map import STATUS_MAP


UNKNOWN = 'Desconocida'

def __any_match(regex_list, string):
    for regex in regex_list:
        if re.search(regex, string, re.IGNORECASE):
            return True
    return False

def get_status(history=list(), initiative_type=''):
    if not history:
        return UNKNOWN
    for status_map_item in STATUS_MAP:
        if __any_match(
                status_map_item['latest_history_items'],
                history[-1]):
            includes = status_map_item['initiative_type']['includes']
            excludes = status_map_item['initiative_type']['excludes']
            if not includes and not excludes:
                return status_map_item['status']
            if initiative_type in includes or initiative_type not in excludes:
                return status_map_item['status']
    return UNKNOWN

def __get_current_status(reference):
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
    return __get_current_status(reference) not in NOT_FINAL_STATUS
