import click
import shutil
import os
import pytest
from agent_test_framework.core.test_generator import generate_all_tests

DEFAULT_OUTPUT_DIR = "generated_tests"

@click.command(context_settings=dict(ignore_unknown_options=True))
@click.option('--test-specs-dir', default='test_specs/', help='Directory with test YAMLs')
@click.option('--run', is_flag=True, help='Run pytest after generating tests')
@click.argument('pytest_args', nargs=-1, type=click.UNPROCESSED)
def cli(test_specs_dir, run, pytest_args):
    """
    Generate tests from YAML specs and optionally run pytest with extra arguments.

    Example:
        agent-test-cli --run -m smoke --alluredir=allure-results --env=dev
    """
    print(f"[INFO] Cleaning previous tests in: {DEFAULT_OUTPUT_DIR}")
    if os.path.exists(DEFAULT_OUTPUT_DIR):
        shutil.rmtree(DEFAULT_OUTPUT_DIR)

    print(f"[INFO] Generating tests from: {test_specs_dir}")
    generate_all_tests(test_specs_dir=test_specs_dir, output_dir=DEFAULT_OUTPUT_DIR)

    if run:
        print(f"[INFO] Running pytest with args: {' '.join(pytest_args)}")
        pytest.main([DEFAULT_OUTPUT_DIR] + list(pytest_args))
