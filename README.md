# Playwright access checker

## Brief overview

Starter code for a planned Playwright-based access checker. The repository currently provides a runnable Python example and a test runner; access checking is not implemented yet.

## More info

These files are adapted from the [script_project template](https://github.com/birkin/birkin_coding_tools/tree/main/script_project/) for [issue #2](https://github.com/birkin/playwright_access_checker/issues/2). The current example adds two integers and prints `3`.

TODO: define the checker’s inputs, authentication requirements, browser workflow, and result format before replacing the example.

Contents:

- [Brief overview](#brief-overview)
- [More info](#more-info)
- [Local installation](#local-installation)
- [Usage](#usage)
- [Primary dependencies](#primary-dependencies)

## Local installation

Install [uv](https://docs.astral.sh/uv/getting-started/installation/). It manages the Python 3.12 interpreter required by [pyproject.toml](pyproject.toml).

Starting in the directory where you want to keep the checkout:

```bash
mkdir playwright_access_checker_stuff
cd playwright_access_checker_stuff
git clone https://github.com/birkin/playwright_access_checker.git playwright_access_checker
cd playwright_access_checker
uv sync --locked
```

The current example requires no credentials, environment file, or browser installation.

## Usage

From the repository root, run the starter example:

```bash
uv run ./main.py
```

It prints `3` to standard output and logs the total. Set `LOG_LEVEL=DEBUG` to enable debug logging.

Run all tests:

```bash
uv run ./run_tests.py
```

Run a single test with verbose output:

```bash
uv run ./run_tests.py tests.test.TestMain.test_sum_two_numbers_returns_total --verbose
```

See [run_tests.py](run_tests.py) for module and class selection examples and [AGENTS.md](AGENTS.md) for coding instructions.

## Primary dependencies

The current [example](main.py) and [test runner](run_tests.py) use only the Python standard library, including `unittest`. [pyproject.toml](pyproject.toml) retains three initial dependencies from the template:

| Package | Intended purpose | Current usage |
| --- | --- | --- |
| `httpx` | HTTP requests | Not yet used by the example. |
| `python-dotenv` | Load environment variables from a file | Not yet used; no environment file is loaded. |
| `trio` | Asynchronous concurrency | Not yet used by the example. |

[uv.lock](uv.lock) records their resolved versions and supporting packages: HTTPX uses `httpcore`, `anyio`, `certifi`, and `idna`; Trio uses packages including `attrs`, `outcome`, and `sortedcontainers`. These supporting packages are not direct application requirements. The `local`, `staging`, and `prod` dependency groups are currently empty.

`uv` manages dependencies and execution. [ruff.toml](ruff.toml) supplies formatting and lint settings for a separately installed Ruff; Ruff is not declared as an application dependency.

TODO: review the inherited dependencies when implementing the checker and retain only those needed. Playwright and browser binaries have not been added yet.
