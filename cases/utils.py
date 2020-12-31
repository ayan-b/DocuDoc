GROUP_TO_IDX = {
    1: 'patient',
    2: 'hospital',
    3: 'pharmacy',
    4: 'diagnosis_center',
}


def get_group(user):
    for idx, group in GROUP_TO_IDX.items():
        if user.groups.filter(name=group).exists():
            return idx
