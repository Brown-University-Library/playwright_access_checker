# Playwright access checker

## Brief overview

This app runs a repeatable browser trial against the Brown Digital Repository Studio. It records browser requests, and if/when access interference occurs. The purpose is to have objective data when working with central-IT on vendor web-traffic configuration.


## More info

Each invocation runs one trial in a new Chromium session. Both workflows request collection page 1 with 50 items per page and select every other distinct thumbnail, up to 20 items. The `tabs` workflow opens the selected links in separate tabs before viewing them in order. The `return` workflow opens, views, and follows the item's actual return link before opening the next item. Viewing includes section-by-section scrolling and pauses. The browser keeps normal images, JavaScript, cookies, and caching enabled.

The app records requests from all tabs before the first collection request and stops further actions on a challenge, denial, relevant error, time limit, or interruption. A request count describes what the browser observed; it does not establish the website's request limit. Settings and public IP details are supplied by the person running the trial. The app does not change the internet connection or the website's traffic rules.

Contents:

- [Brief overview](#brief-overview)
- [More info](#more-info)
- [Local installation](#local-installation)
- [Usage](#usage)
- [Results and interpretation](#results-and-interpretation)
- [Tests](#tests)
- [Primary dependencies](#primary-dependencies)

## Local installation

Requirements: [uv](https://docs.astral.sh/uv/getting-started/installation/) is installed.


```bash
mkdir ./playwright_access_checker_stuff
cd ./playwright_access_checker_stuff
git clone git@github.com:Brown-University-Library/playwright_access_checker.git
cd ./playwright_access_checker
uv sync --locked
uv run playwright install chromium
test -e ../.env || cp ./.env.example ../.env  # if the .env file doesn't already exist, copy it from the example-file
```

That's it!

These default `.env` settings will access the Herbarium collection-page, and open items within that collection, as described further below.

Other install notes:

- Linux installations may also need Chromium's system dependencies; see [Playwright's browser installation instructions](https://playwright.dev/python/docs/browsers#install-system-dependencies).


## Usage


### Typical usage

```bash
uv run ./main.py bdr:nz9qn2kb --workflow tabs --seed 42
```

...or:

```
uv run ./main.py bdr:nz9qn2kb --workflow return --seed 42
```

### Other usage notes

The `--preview` option validates settings and checks the output location without launching a browser or making network requests:

```bash
uv run ./main.py bdr:nz9qn2kb --workflow tabs --preview
```

For a short initial check, limit the number of item openings:

```bash
uv run ./main.py bdr:nz9qn2kb --workflow tabs --max-items 1 --max-duration-seconds 30
```


## Settings

Settings take priority in this order: command-line options, environment variables, explicitly loaded `../.env`, defaults. Relative paths are interpreted from the repository root. A Studio collection-PID such as `bdr:nz9qn2kb` is required; numeric collection API identifiers and arbitrary URLs are not accepted. `--help` lists all options. 

| Setting / option | Default and meaning |
| --- | --- |
| `WORKFLOW` / `--workflow` | Required: `tabs` or `return`. |
| `CF_SETTINGS_LABEL`, `CF_SETTINGS_NOTES` | Required label and description of the vendor's traffic settings; `unknown` is allowed. Corresponding options use lowercase names with hyphens. |
| `OPEN_INTERVAL_SECONDS`, `OPEN_JITTER_SECONDS` | `1.0`, `0.1`: seconds between actual opening starts in `tabs`, with independent uniform variation. Delays do not cause later openings to speed up. |
| `VIEW_SECONDS`, `VIEW_JITTER_SECONDS` | `5.0`, `0.5`: total viewing duration, including one-second pauses and scrolls of 80% of the visible height. |
| `SELECTION_START` | `1`: select positions 1, 3, 5; use `2` for positions 2, 4, 6. |
| `SEED` | Generated when omitted; recorded so planned timings can be repeated. (A seed sets the starting point for a random-number generator, so using the same seed with the same generator produces the same sequence of numbers.) |
| `MAX_ITEMS` | `20`; accepts 1–20. Remaining viewing and return steps finish after opening this many items. |
| `MAX_DURATION_SECONDS` | `300`; measured from the first collection request, including link gathering. |
| `MAX_SCROLL_ACTIONS` | `20`; separately limits gathering links, finding a thumbnail, and finding a return link. Viewing scrolls are limited by viewing time. |
| `NAVIGATION_TIMEOUT_SECONDS` | `30`; bounds page openings and waits for required content. |
| `BDR_HOSTS` | `repository.library.brown.edu`; exact comma-separated hostnames included in counts and stopping rules. Review this list before a trial if Studio uses other BDR hosts. |
| `PROXY_SERVER` | Optional `http`, `https`, or `socks5` server with a port, prepared before the trial. Credentials use separate `PROXY_USERNAME` and `PROXY_PASSWORD` environment values. Authenticated SOCKS5 is unsupported by Chromium. |
| `OUTPUT_DIR` | `../runs`; must remain outside this Git repository. |

The `JITTER` settings are an effort to provide a touch of variation in the timings. So in the "tabs" workflow, the goal is for the user to be open "roughly" one tab-per-second; the give-or-take is the "jitter".

Enter timing values in seconds, including decimal values such as `0.5` or `1.25`; values such as infinity or `NaN` (not a number) are not allowed. The time between openings, viewing time, and time limits must each be greater than zero. Random variation must be zero or greater and less than the corresponding opening or viewing time. For example, a viewing time of 5 seconds allows variation of 0 or 1 second, but not 5 seconds. With the `return` workflow, passing `--open-interval-seconds` or `--open-jitter-seconds` causes an error. The same settings in environment variables or `.env` are listed as unused. Run the command again to try a different workflow, timing setting, or internet connection.


## Implementation notes

The app finds item links in Studio's thumbnail images (`.item-thumbnail`), checks the dropdowns for items per page and sort order, and follows “Back to Results” when that link is available. Before opening items, it checks that the collection shows page 1 with 50 items per page selected. If returning from an item changes the items-per-page setting, the app tries once to select 50 again using the dropdown. The trial stops if the sort order, filters, or item order change.

The app scrolls the main browser page without using controls inside an embedded item viewer. It does not visit additional pages of collection results, browse collections within collections, download files, operate viewer controls, solve verification challenges, or automatically retry failed actions.


## Results and interpretation

Each trial creates `../runs/<trial-id>/` containing:

- `run.json`: settings and their sources, versions, selected URLs, browser details, planned timings, request counts, and the reason the trial stopped.
- `events.jsonl`: immediately flushed actions, requests, responses, failures, content readiness, tab switches, scrolling, viewing, and stopping evidence.
- `summary.md`: conditions, checked URLs, actual timings, completed and interrupted views, preceding 30/60/120/300-second counts, totals at those marks when reached, a comparison row, and known evidence limits.

Durations use a monotonic clock. Dates use `America/New_York` with the numeric offset and EST/EDT label. Shorter observations are labeled partial; time marks not reached are unavailable. Switching tabs and scrolling are separate from item-opening attempts. Finishing a viewing duration does not mean the browser reached the bottom or finished loading every viewer file.

The browser closes after results are saved. Press Ctrl-C to stop and retain evidence. Exit status is `0` for a completed workflow, `1` for interference or an incomplete trial, `130` for interruption, and `2` for invalid arguments. Missing Chromium binaries produce a saved startup-error report; install the browser with the command above.

Rebuild a `summary.md` report from local saved events without launching a browser:

```bash
uv run ./main.py --rebuild-report ../runs/TRIAL_ID
```

Optional: To compare several trials side by side, you can copy their comparison rows into a Markdown table saved in `../runs`. Saving the table there keeps the links to individual reports working. Keep a separate row for each trial, including repeated trials with the same settings. Before sharing reports or other output, check website addresses, notes, and public IP information for anything you do not want to share.

The app does not save login credentials, cookies, complete request headers, response bodies, screenshots, browser traces, or browser sessions. It removes values from URL query parameters it does not recognize. Any requests recorded after the app decides to stop the trial are marked as occurring after that decision. They are excluded from the request counts calculated at the time of that decision.

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
