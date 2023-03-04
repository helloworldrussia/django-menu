class MenuError(Exception):
    default_message = 'Error forming the menu.'

    def __init__(self, message=default_message):
        self.message = message

    def __str__(self):
        return self.message


class NoMenuItemOfCurrentPage(MenuError):
    pass


class ParentNotInMenu(MenuError):
    pass
