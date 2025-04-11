def pytest_addoption(parser):
    parser.addoption("--data", action="store")


def pytest_generate_tests(metafunc):
    option_value = metafunc.config.option.data
    if "data" in metafunc.fixturenames and option_value is not None:
        metafunc.parametrize("data", [option_value])
