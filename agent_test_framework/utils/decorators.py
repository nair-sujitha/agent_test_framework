
def action(description):
    def decorator(func):
        func._browser_use_action = description
        return func
    return decorator
