# conftest.py
import logging
import allure
from allure_commons.types import AttachmentType

class AllureLogHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        allure.attach(msg, name="log", attachment_type=AttachmentType.TEXT)

def pytest_configure(config):
    logger = logging.getLogger()
    handler = AllureLogHandler()
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
