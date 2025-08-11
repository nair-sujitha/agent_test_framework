import allure

import pytest

from browser_use.llm import ChatGoogle
from browser_use import Agent, BrowserSession

from dotenv import load_dotenv
from agent_test_framework.utils.assertion_handler import assert_from_bulk_json

load_dotenv()

llm = ChatGoogle(
    model='gemini-2.5-flash-lite-preview-06-17',
    api_key="AIzaSyCCtl2sJT67mX6tVOejGuWN299Ajx5S01M"
)

def load_env_config():
    import importlib

    try:
        config_module = importlib.import_module("config.env_conf")
        return getattr(config_module, "ENV_CONFIG")
    except ModuleNotFoundError:
        raise RuntimeError("User project must have a config/env_conf.py with ENV_CONFIG defined.")

class BaseBrowserAgentTest:

    def __init__(self, task: str, model_cls, controller_cls, test_env, expectations=None):
        self.task = task
        self.model_cls = model_cls
        self.expectations = expectations or {}
        self.controller = controller_cls
        self.environment = test_env
        self.browser_session = BrowserSession(
            executable_path='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'  # Windows
        )

    def _build_agent(self):
        env_config = load_env_config().get(self.environment)
        url = env_config["url"]
        allowed_domains = env_config.get("allowed_domains", [])
        initial_actions = [
            {'go_to_url': {'url': url, 'new_tab': True, 'allowed_domain': allowed_domains}}
        ]
        return Agent(
            task=self.task,
            initial_actions=initial_actions,
            llm=llm,
            controller=self.controller(output_model=self.model_cls),
            browser_session=self.browser_session
        )

    async def run(self):
        agent = self._build_agent()
        try:
            history = await agent.run()
            print(f"history********************* {history}")
            print(f"history is done ********************* {history.is_done}")
            print(f"history is successful ********************* {history.is_successful}")
            print(f"history is done or success ********************* {not (history.is_done() or history.is_successful())}")
            if not (history.is_done() or history.is_successful()):
                print("task not complete**********")
                allure.attach(body="Unexpected error/exception Agent task NOT completed successfully",
                              name="Task Error",
                              attachment_type=allure.attachment_type.TEXT)
                raise Exception(f"Agent task NOT completed successfully: {history}")
            result = history.final_result()
            if not result:
                allure.attach(body="Unexpected error/exception Agent returned no final result",
                              name="Task Error",
                              attachment_type=allure.attachment_type.TEXT)
                raise Exception("Agent returned no final result")
            parsed = self.model_cls.model_validate_json(result)
            self._assert_expectations(parsed)
            return parsed
        except AssertionError as ae:
            print(f"Assertion Error : {ae}")
            pytest.fail(f"Assertion Error in test: {ae}")
        except Exception as e:
            print(f"General Exception : {e}")
            pytest.fail(f"Unexpected Error in test: {e}")

    def _assert_expectations(self, parsed_result):
        if 'from_json' in self.expectations:
            assert_from_bulk_json(parsed_result, self.expectations['from_json'])
        else:
            for field, rule in self.expectations.items():

                actual_value = getattr(parsed_result, field, None)
                expected_type = rule.get("type")
                expected_value = rule.get("value")

                # Debug: Print the key, rule, and actual
                print(f"[ASSERT] Key: {field}, Rule: {rule}, Actual: {actual_value}")

                if not isinstance(rule, dict):
                    raise TypeError(
                        f"Invalid expectation format for '{field}': expected dict, got {type(rule).__name__} -> {rule}"
                    )

                with allure.step(f"Assert {field} matches expectations"):
                    if expected_type == "equals":
                        assert actual_value == expected_value, (
                            f"Expected {field} == {expected_value}, but got {actual_value}"
                        )
                    elif expected_type == "contains":
                        assert isinstance(actual_value, str), (
                            f"Cannot use 'contains' assertion on non-string field '{field}'"
                        )
                        assert expected_value in actual_value, (
                            f"Expected '{expected_value}' to be in '{field}', but got '{actual_value}'"
                        )
                    else:
                        raise ValueError(f"Unsupported assertion type: {expected_type} for field: {field}")
