import copy

from django import template
from django.forms import model_to_dict
from django.urls import resolve
from collections import namedtuple
from ..exceptions import ParentNotInMenu
from ..models import MenuItem

register = template.Library()


@register.inclusion_tag('menu/menu_template.html', takes_context=True)
def draw_menu(context, menu_name):
    menu, current_item = get_menu(context, menu_name)
    data = {
        'items': menu,
        'context': context,
        'current_item': current_item,
    }
    return data


def get_menu(context, menu_name):
    """
    Возвращает menu_tree - пункты меню для рендеринга в шаблоне (list),
    current_item - выбранный пункт меню (dict).
    При пустом queryset возвращает None, None.
    """
    items = MenuItem.objects.filter(
        menu__name=menu_name
    ).select_related(
        'parent'
    )
    if not items:
        return None, None
    menu_tree, current_item = get_menu_data(context, items)
    return menu_tree, current_item


def prepare_data(context, items):
    """
    Определяет выбранный пункт меню.
    Объявляет и присваивает значения переменным:
    dict_items: набор всех пунктов меню (dict) где
    ключ - id модели, значение - модель в виде словаря
    result: список из элементов dict_items, которые не имеют родителя.
    """
    current_url = context.request.path_info
    current_absolute_url = context.request.build_absolute_uri()
    current_namespace = resolve(context.request.path_info).url_name
    dict_items = {}
    result = []
    current_item = None

    for item in items:
        dict_items[item.pk] = model_to_dict(item)
        dict_items[item.pk]['children'] = []
        dict_items[item.pk]['href'] = item.get_url()
        if not item.parent:
            result.append(dict_items[item.pk])
        if item.url in (current_absolute_url, current_url):
            current_item = item
        if item.namespace == current_namespace:
            current_item = item

    if not current_item:
        current_item = namedtuple('CurrentItem', ['pk', 'parent'])
        current_item.pk, current_item.parent = 0, None

    return dict_items, result, current_item


def get_menu_data(context, items):
    """
    Помещает дочки выбранной ветки в родительские элементы.
    """
    dict_items, result, current_item = prepare_data(context, items)
    current = copy.deepcopy(current_item)
    for item in items:
        if not validate_items_parent(item, dict_items):
            continue
        if item.parent == current_item:
            replace_in_parent(dict_items, current_item.pk, item.pk)
        if item.parent == current_item.parent and item != current_item:
            replace_in_parent(dict_items, item.parent.pk, item.pk)

    while current_item.parent:
        if current_item.parent.pk in dict_items:
            replace_in_parent(dict_items, current_item.parent.pk, current_item.pk)
            current_item = current_item.parent
        else:
            raise ParentNotInMenu()

    return result, current


def validate_items_parent(item, dict_items):
    if item.parent and item.parent.pk not in dict_items:
        raise ParentNotInMenu()
    if item.parent:
        return True


def replace_in_parent(dict_items, parent_id, child_id):
    dict_items[parent_id]['children'].append(
        dict_items[child_id].copy()
    )
