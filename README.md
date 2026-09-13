# Playwright access checker

## Brief overview

Runs repeatable, visible browser trials against Brown Digital Repository Studio. It records when access interference occurs and saves evidence for discussions with Central IT.

## More info

Each invocation runs one trial in a new Chromium session. Both workflows request collection page 1 with 50 items per page and select every other distinct thumbnail, up to 20 items. `tabs` opens the selected links in separate tabs before viewing them in order. `return` opens, views, and follows the item's actual return link before opening the next item. Viewing includes section-by-section scrolling and pauses. The browser keeps normal images, JavaScript, cookies, and caching enabled.

The app records requests from all tabs before the first collection request and stops further actions on a challenge, denial, relevant error, time limit, or interruption. It also recognizes a Turnstile verification page when expected Studio content is absent, even if the HTTP status is 200; the presence of a widget beside accessible content alone is not a denial. A request count describes what the browser observed; it does not establish a Cloudflare request limit. Settings and public IP details are supplied by the person running the trial. Connection changes and Cloudflare configuration remain outside the app.

The implementation follows [the application plan](PLAN__02_application_design.md) and is tracked in [issue #9](https://github.com/birkin/playwright_access_checker/issues/9). The repository began with the [script_project template](https://github.com/birkin/birkin_coding_tools/tree/main/script_project/).

Contents:

- [Brief overview](#brief-overview)
- [More info](#more-info)
- [Local installation](#local-installation)
- [Usage](#usage)
- [Results and interpretation](#results-and-interpretation)
- [Tests](#tests)
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
uv run playwright install chromium
test -e ../.env || cp .env.example ../.env
```

Edit `../.env` in the enclosing `playwright_access_checker_stuff` directory. Supply the Cloudflare settings label and notes; use `unknown` when the settings have not been confirmed. Record when the settings took effect as an ISO date/time with an offset, or `unknown`. Record the connection, public IP, and any relevant recent activity. The app does not independently verify these details. Linux installations may also need Chromium's system dependencies; see [Playwright's browser installation instructions](https://playwright.dev/python/docs/browsers#install-system-dependencies).

## Usage

Run these commands from the repository root. Preview validates settings and checks the output location without launching a browser or making network requests:

```bash
uv run ./main.py bdr:224400 --workflow tabs --preview
```

Run one trial at a time:

```bash
uv run ./main.py bdr:224400 --workflow tabs --seed 42
uv run ./main.py bdr:224400 --workflow return --seed 42
```

For a short initial check, limit the number of item openings:

```bash
uv run ./main.py bdr:224400 --workflow tabs --max-items 1 --max-duration-seconds 30
```

Settings take priority in this order: command-line options, environment variables, explicitly loaded `../.env`, defaults. Relative paths are interpreted from the repository root. A Studio PID such as `bdr:224400` is required; numeric collection API identifiers and arbitrary URLs are not accepted. `--help` lists all options. `.env` interpolation is disabled so settings are read as written.

| Setting / option | Default and meaning |
| --- | --- |
| `WORKFLOW` / `--workflow` | Required: `tabs` or `return`. |
| `CF_SETTINGS_LABEL`, `CF_SETTINGS_NOTES` | Required label and description; `unknown` is allowed. Corresponding options use lowercase names with hyphens. |
| `OPEN_INTERVAL_SECONDS`, `OPEN_JITTER_SECONDS` | `1.0`, `0.1`: seconds between actual opening starts in `tabs`, with independent uniform variation. Delays do not cause later openings to speed up. |
| `VIEW_SECONDS`, `VIEW_JITTER_SECONDS` | `5.0`, `0.5`: total viewing duration, including one-second pauses and scrolls of 80% of the visible height. |
| `SELECTION_START` | `1`: select positions 1, 3, 5; use `2` for positions 2, 4, 6. |
| `SEED` | Generated when omitted; recorded so planned timings can be repeated. |
| `MAX_ITEMS` | `20`; accepts 1–20. Remaining viewing and return steps finish after opening this many items. |
| `MAX_DURATION_SECONDS` | `300`; measured from the first collection request, including link gathering. |
| `MAX_SCROLL_ACTIONS` | `20`; separately limits gathering links, finding a thumbnail, and finding a return link. Viewing scrolls are limited by viewing time. |
| `NAVIGATION_TIMEOUT_SECONDS` | `30`; bounds page openings and waits for required content. |
| `BDR_HOSTS` | `repository.library.brown.edu`; exact comma-separated hostnames included in counts and stopping rules. Review this list before a trial if Studio uses other BDR hosts. |
| `PROXY_SERVER` | Optional `http`, `https`, or `socks5` server with a port, prepared before the trial. Credentials use separate `PROXY_USERNAME` and `PROXY_PASSWORD` environment values. Authenticated SOCKS5 is unsupported by Chromium. |
| `OUTPUT_DIR` | `../runs`; must remain outside this Git repository. |

All timing values must be finite. Targets must be positive, and variation must be nonnegative and smaller than the target. Explicit opening-timing options are rejected for `return`; opening-timing values from the environment or `.env` are shown as unused. Use a new invocation for another workflow, timing target, or connection.

Studio's current adapter uses `.item-thumbnail` links, the page-size and sort dropdowns, and “Back to Results” when available. The first listing must actually show page 1 and 50 per page. A return that loses the 50-item setting gets one restoration attempt through the actual dropdown. Changed sorting, filters, or item order stop the trial. Scrolling uses `window.scrollBy` to target the outer page, keeping embedded viewer controls untouched. Additional listing pages, collection nesting, downloads, viewer controls, challenge solving, and automatic retries are excluded.

## Results and interpretation

Each trial creates `../runs/<trial-id>/` containing:

- `run.json`: settings and their sources, versions, selected URLs, browser details, planned timings, request counts, and the reason the trial stopped.
- `events.jsonl`: immediately flushed actions, requests, responses, failures, content readiness, tab switches, scrolling, viewing, and stopping evidence.
- `summary.md`: conditions, checked URLs, actual timings, completed and interrupted views, preceding 30/60/120/300-second counts, totals at those marks when reached, a comparison row, and known evidence limits.

Durations use a monotonic clock. Dates use `America/New_York` with the numeric offset and EST/EDT label. Shorter observations are labeled partial; time marks not reached are unavailable. Switching tabs and scrolling are separate from item-opening attempts. Finishing a viewing duration does not mean the browser reached the bottom or finished loading every viewer file.

The browser closes after results are saved. Press Ctrl-C to stop and retain evidence. Exit status is `0` for a completed workflow, `1` for interference or an incomplete trial, `130` for interruption, and `2` for invalid arguments. Missing Chromium binaries produce a saved startup-error report; install the browser with the command above.

Rebuild a report from local saved events without launching a browser:

```bash
uv run ./main.py --rebuild-report ../runs/TRIAL_ID
```

Copy reviewed comparison rows into a Markdown table in the parent `runs` directory so their relative report links work. Keep repetitions visible. Before sharing any material, review local URLs, notes, and public IP information. Credentials, cookies, full request headers, response bodies, screenshots, traces, and saved browser sessions are not recorded. Unknown URL query values and Cloudflare verification tokens in URL paths are removed. Requests after the stopping signal remain identifiable and do not enter counts measured at that signal.

## Tests

Run all tests:

```bash
uv run ./run_tests.py
```

Run a single test with verbose output:

```bash
uv run ./run_tests.py tests.test_measurement --verbose
```

The suite uses `unittest` and a loopback-only local website with real headless Chromium. It requires installed Chromium and permission to start a local HTTP server. It tests both workflows, overlapping loads, page-size restoration, scrolling, redirects, interruption, request counts, and interference in background tabs and supporting requests. Automated tests do not contact BDR. See [run_tests.py](run_tests.py) for module and class selection and [AGENTS.md](AGENTS.md) for coding instructions.

## Primary dependencies

The declarations in [pyproject.toml](pyproject.toml), imports in the application, and resolved dependencies in [uv.lock](uv.lock) identify two primary packages:

| Package | Intended purpose | Current usage |
| --- | --- | --- |
| `playwright` | Chromium browser automation and request observation | Synchronous API in `lib/browser_flow.py` and `lib/observation.py`; browser installation through its CLI. |
| `python-dotenv` | Read local settings | `dotenv_values` in `lib/config.py` explicitly reads `../.env`. |

[uv.lock](uv.lock) records Playwright's supporting packages `greenlet` and `pyee`; `pyee` requires `typing-extensions`. These are not direct application requirements. The unused starter declarations `httpx2` and `trio` were removed when implementing the browser workflows. The application makes no separate HTTP-client calls. Tests use the standard library, including `unittest` and `http.server`, plus the same Playwright installation. The `local`, `staging`, and `prod` groups remain empty.

`uv` manages dependencies and execution. [ruff.toml](ruff.toml) supplies formatting and lint settings for a separately installed Ruff; Ruff is not declared as an application dependency.
