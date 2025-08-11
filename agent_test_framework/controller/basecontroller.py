
from browser_use.controller.service import Controller


class BaseController(Controller):
    def __init__(self, output_model):
        super().__init__(output_model=output_model)
        self.executed_actions = []

        # Auto-register any @action methods
        for attr_name in dir(self):
            method = getattr(self, attr_name)
            if callable(method) and hasattr(method, "_browser_use_action"):
                desc = getattr(method, "_browser_use_action")
                self.action(desc)(method)  # This registers it with the framework

