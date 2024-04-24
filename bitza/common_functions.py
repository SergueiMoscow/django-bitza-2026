from django.contrib.auth.models import User

GROUPS = {
    'owners': 'Хозяева',
    'administrators': 'Администраторы',
    'workers': 'Сотрудники',
    'electricity': 'Электричество',
}


def is_in_group(user: User, group: str):
    return user.groups.filter(name=group).exists()


def get_menu_items_by_group(group: str) -> dict:
    """Receives group name (string)
    Returns dict with Label -> url_name (urls.py)"""
    menu = {}
    if group == 'workers':
        menu['Работа'] = "work:list"
    elif group == 'owners':
        menu['Сводка'] = 'rent:summary'
        menu['Договора'] = 'rent:contracts'
        menu['Платежи'] = 'rent:payments'
        menu['Клиенты'] = 'rent:clients'
    elif group == GROUPS['administrators']:
        menu['Сводка'] = 'resume'
    return menu


def get_menu_items_by_user(user: User) -> dict:
    menu = {}
    groups = get_user_groups(user)
    if GROUPS['workers'] in groups or 'workers' in groups:
        menu['Работа'] = "work:list"
    if GROUPS['owners'] in groups or 'owners' in groups:
        menu['Сводка'] = 'rent:summary'
        menu['Договора'] = 'rent:contracts'
        menu['Платежи'] = 'rent:payments'
        menu['Клиенты'] = 'rent:clients'
    if GROUPS['administrators'] in groups or 'administrators' in groups:
        menu['Сводка'] = 'resume'
    return menu


    # if 'owners' in [group.name for group in groups]:


def get_user_groups(user: User) -> tuple:
    groups = user.groups.all()
    return tuple([group.name for group in groups])
