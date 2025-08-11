import os
import yaml
import glob

def sanitize_name(name):
    return name.replace("-", "_").replace(" ", "_")


def generate_test_code(yaml_spec, suite_name, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    suite_name = sanitize_name(yaml_spec.get("name", f"suite_{suite_name}"))
    fixture_name = f"{suite_name}_fixture"
    filename = os.path.join(output_dir, f"test_{suite_name}.py")

    suite_setup = yaml_spec.get("suite_setup")
    suite_teardown = yaml_spec.get("suite_teardown")

    lines = [
            # Imports
            "import pytest",
             "from agent_test_framework.core.base_test import BaseBrowserAgentTest",
             "from agent_test_framework.utils.test_hooks import run_hook",
             "from agent_test_framework.utils.import_utils import resolve",
             "",
             # Fixture
             f"@pytest.fixture(scope='module', name='{fixture_name}')",
             f"def {fixture_name}():",
             f"    run_hook({suite_setup}, stage='SUITE_SETUP')",
             f"    yield",
             f"    run_hook({suite_teardown}, stage='SUITE_TEARDOWN')",
             ""]

    for test_spec in yaml_spec["tests"]:
        test_id = test_spec.get("id", "unknown")
        test_name = f"test_{sanitize_name(test_spec['name'])}"
        task = repr(test_spec["task"])
        model = repr(test_spec["model"])
        controller = repr(test_spec.get("controller", "browser_use.controller.service.Controller"))
        expectations = repr(test_spec.get("expectations", {}))
        labels = test_spec.get("labels", [])
        setup = repr(test_spec.get("setup"))
        teardown = repr(test_spec.get("teardown"))

        # Decorators
        lines.append(f"@pytest.mark.usefixtures('{fixture_name}')")
        lines.append(f"@pytest.mark.{test_id}")
        for label in labels:
            lines.append(f"@pytest.mark.{label}")
        lines.append("@pytest.mark.asyncio")

        # Test function
        lines.append(f"async def {test_name}(test_env):")
        if setup:
            lines.append(f"    run_hook({setup}, stage='SETUP')")
        lines.append(f"    test = BaseBrowserAgentTest(")
        lines.append(f"        task={task},")
        lines.append(f"        model_cls=resolve({model}),")
        lines.append(f"        controller_cls=resolve({controller}),")
        lines.append(f"        test_env=test_env,")
        lines.append(f"        expectations={expectations}")
        lines.append(f"    )")
        lines.append("    await test.run()")
        if teardown:
            lines.append(f"    run_hook({teardown}, stage='TEARDOWN')")
        lines.append("")  # spacing

    with open(filename, "w") as f:
        f.write("\n".join(lines))

    print(f"[Generated] {filename}")


def generate_all_tests(test_specs_dir="test_specs/", output_dir="generated_tests/"):
    for file_path in (glob.glob(os.path.join(test_specs_dir, "*.yml"))
                      + glob.glob(os.path.join(test_specs_dir, "*.yaml"))):
        with open(file_path, 'r') as f:
            spec = yaml.safe_load(f)
            file_name_ext = os.path.basename(file_path)
            file_name = os.path.splitext(file_name_ext)
            print(f"file name******************* {file_name[0]}")
            generate_test_code(spec, file_name[0], output_dir)


if __name__ == "__main__":
    generate_all_tests(test_specs_dir="test_specs/", output_dir="generated_tests/")