# Application design and development plan

Initial proposal by Codex, 2026-09-11, for [issue #5: Develop design plan](https://github.com/birkin/playwright_access_checker/issues/5). Work branch: `issue-5-develop-design-plan`.

This task produces a plan only. Application implementation, live frequency trials, and network setup are future work. This revision incorporates the maintainer's feedback through commit `06ba65d`: application design A is selected, and both browsing workflows below belong in the initial implementation. Review paused at “Collection access and browser behavior”; later sections have been updated for consistency and remain subject to review. Repository conventions are in [AGENTS.md](AGENTS.md).

Contents:

- [Purpose and recommended starting point](#purpose-and-recommended-starting-point)
- [Trial procedure and timing](#trial-procedure-and-timing)
- [Two application designs](#two-application-designs)
- [Collection access and browser behavior](#collection-access-and-browser-behavior)
- [Recognizing interference and counting requests](#recognizing-interference-and-counting-requests)
- [Configuration and results](#configuration-and-results)
- [Two ways to change IP addresses](#two-ways-to-change-ip-addresses)
- [Development steps and initial scope](#development-steps-and-initial-scope)

## Purpose and recommended starting point

Build a repeatable way to describe when a researcher-like browsing session encounters access interference for an existing Cloudflare configuration. Purpose: to gather objective data for when we work with Central IT to make Cloudflare configuration changes. Objective: for a given Cloudflare configuration, for us to be able to supply the date, urls-checked, and multiple access-frequency data-points -- to assess the real-world implications of a given configuration.

Use a Python CLI with synchronous Playwright, one visible Chromium browser, and one fresh browser context per trial. Each run accepts one collection identifier, one workflow, and that workflow's timing settings. Both initial workflows select every other item thumbnail, up to 20 items: **open separate tabs, then review them**, and **open, review, and return to the overview in one tab**. The first models the maintainer's description of a researcher opening numerous item tabs before being blocked. Exercise both workflows in separate trials. Record requests from the first collection access and stop all further browsing actions at the first relevant challenge, denial, error, or observation deadline. Write local JSON records and a readable Markdown report. Change network exits manually between trials using a separate setup.

Use seeded pseudorandom variation around the selected timing values, so the intended sequence can be reproduced. The maintainer accepts an approximate average; exact mean balancing is unnecessary. The workflows and application choice are requested behavior; the detailed settings and implementation choices below remain design proposals.

An observed block is a result under recorded conditions, not proof of a universal request threshold. Cloudflare's bot assessment can use headers, session characteristics, and browser signals; its rate-limiting rules can count selected traffic using characteristics beyond IP address. Small timing variations model browsing rhythm but do not establish equivalence to a human-operated browser. [Cloudflare bot scores](https://developers.cloudflare.com/bots/concepts/bot-score/), [rate-limiting parameters](https://developers.cloudflare.com/waf/rate-limiting-rules/parameters/).

Each report must include a short **Known unknowns and evidence limits** section. Record relevant uncertainties actually identified for the run, such as exit history or geography, unconfirmed Cloudflare behavior, and differences between automated and manual tab behavior. Keep it useful and specific; an exhaustive list of hypothetical concerns is unnecessary.

## Trial procedure and timing

### One trial

1. Record the workflow, timing settings, thumbnail selection, user-supplied Cloudflare settings label and notes, settings effective time, and network exit. Keep these conditions unchanged throughout the trial. Start with an exit expected to be unblocked; document any known recent use or cooldown.
2. Open a fresh browser context, retaining its cookies and cache throughout this trial and sharing it across any item tabs. Attach context-wide network observers before the first BDR request. Use the collection visit itself as the initial access check, rather than making extra BDR probes beforehand.
3. Visit the collection overview and select a bounded, ordered set of every-other-item thumbnail links. Carry out the selected workflow below. Record discovery, item opening, tab review, return-to-overview, and scrolling actions separately while retaining the complete traffic history.
4. Keep the chosen timing targets unchanged. Stop all further actions on interference, the duration limit, interruption, or an error that prevents reliable measurement, and preserve partial results. Reaching the item cap or the end of the available selection prevents more item openings but allows the remaining review/return steps to finish within the deadline. Finish normally when the workflow is complete.
5. Save the trial and close all its tabs before changing IP or browser state. A new exit or workflow starts a new trial with a new identifier. A challenge on the initial collection visit is an initial-access failure; it does not establish a threshold caused by this trial.

The initial successful collection visit establishes observed access, not an empty Cloudflare counter or a clean IP history. Discovery traffic may itself cause interference and must never disappear from the report.

### Timing definition

Keep **item-opening intervals** distinct from **viewing durations**. An opening interval runs from one item-opening action's start to the next; record the associated document-request starts separately. A viewing duration starts when the item is selected for review and its expected content is ready. It is time spent examining the item, so it excludes waiting for content. This distinction matters because the two workflows produce different opening frequencies:

| Workflow | Proposed starting timing | What controls the next item opening |
| --- | --- | --- |
| `tabs` — open tabs, then review | Open a new item tab about every `1.0` second with `±0.1` second variation; after opening the selection, review each tab for `5.0` seconds with `±0.5` second variation. | The opening schedule and availability of the next collection thumbnail. Earlier item tabs may still be loading. Viewing happens after the opening phase. |
| `return` — item and overview in one tab | Review each item for `5.0` seconds with `±0.5` second variation, then follow its back-to-collection link and find the next selected thumbnail. | Completion of item readiness, viewing, return navigation, overview readiness, and any needed scrolling. The achieved opening interval includes all these steps and will usually exceed five seconds. |

For each timing target `T` and variation `J`, draw planned values independently from a uniform distribution between `T - J` and `T + J`, using a recorded integer seed and a fixed draw order. Require finite values with `T > 0` and `0 <= J < T`. For `T=5` and `J=0.5`, the expected mean is five seconds; a finite trial will usually have a slightly different mean. Record the planned opening and viewing sequences separately from actual timings. Approximate averages are sufficient; do not rebalance later actions to force an exact mean.

Use a monotonic clock for elapsed times and window calculations. Record all wall-clock timestamps in local Eastern time, interpreting the maintainer's “local-EST” as `America/New_York`: EST in winter and EDT during daylight saving time. Include the numeric offset and timezone name so dates remain unambiguous; this applies to JSON, event records, reports, and settings effective times. Use Python's `zoneinfo` support for the conversion. [Python timezone support](https://docs.python.org/3.12/library/zoneinfo.html).

In `tabs`, schedule the next opening relative to the previous actual opening start. Issue one deliberate action at a time, but allow the browser's tab loads and requests to overlap naturally. Do not wait for the previous item to finish loading or be viewed before opening the next tab. Keep page-event handlers brief, track pending tabs and their deadlines, and do not make waiting for a popup's first response a prerequisite for every subsequent opening. If the chosen action method, scrolling, or browser work delays an opening, record the overrun and resume from the actual start, without catch-up bursts. In `return`, wait for each required page and complete its viewing/return steps before the next thumbnail click. Report achieved opening intervals and viewing durations separately, with mean and range.

Readiness means the expected collection or item content is available for review, within a bounded timeout. Record background-tab content readiness separately from foreground review start; allow a separately recorded foreground readiness wait for content that loads only on activation. Missing initial navigation or identifiable challenge/denial evidence must not wait until that tab's review turn. Use bounded navigation/locator checks rather than a fixed sleep or `networkidle` as evidence of success. During pacing and viewing, use short Playwright waits and brief checks that continue processing events across the context, checking every pending navigation deadline and the global stop condition. A slow tab must not freeze observation of the others. [Page API](https://playwright.dev/python/docs/api/class-page), [event-processing guidance](https://playwright.dev/python/docs/library#timesleep-leads-to-outdated-state).

### Comparing runs

Exercise both workflows under a recorded configuration in separate trials. For `tabs`, vary the opening interval while holding viewing duration constant initially; for `return`, vary viewing duration and measure the resulting opening intervals. The 30-, 60-, 120-, and 300-second windows describe traffic within a trial; they do not substitute for trials at different browsing paces. Hold the collection, displayed order, every-other-item starting position, item cap, browser version, viewport, cache policy, seed, discovery limits, and network type constant where possible. Record any differences in selected URLs, initial discovery, returns, or scrolling. Group results by workflow and timing settings; the same numeric viewing duration does not make the workflows equivalent workloads. Repeat a useful condition, ideally three times initially, and report the individual results and range. This is a practical comparison, not a statistical guarantee.

Retain trials with no interference alongside challenged or denied trials, showing their observed duration and workload; retain inconclusive and partial trials with their limitations. Together these supply evidence about the effects of the existing configuration for discussion with Central IT. Once Central IT changes settings, use a new configuration label and effective time, then compare the same paces and recorded conditions after the expected cooldown or on another documented exit. Changing IP also changes a condition; do not combine results from unlike networks into a single threshold. A short manually operated browser session can later help assess how well the scripted workflow represents researcher behavior.

## Two application designs

| Design | How it works | Advantages | Costs and limits |
| --- | --- | --- | --- |
| **A. One-command browser-led runner — selected by the maintainer** | One CLI command opens the collection, selects thumbnail links in the browser, carries out either requested workflow, and writes the report. A few small modules separate configuration, browser actions, timing, and results. | Small implementation; collection browsing and item access share one measured session and route; easy to watch; no database or asynchronous framework. | Collection discovery consumes requests in each run. Listing changes can change the workload. Thumbnail and return-link selectors need maintenance. |
| **B. Separate discovery and trial commands — deferred alternative** | A discovery command saves an ordered item-list file; a trial command uses that file as input. Discovery could use the public collection API, with `httpx2` as required by repository guidance. | Reuses an exact intended item list across trials; easier later comparison and replay. | More commands, file validation, and stale-list handling. Reproducing thumbnail clicks and returns would still require matching the saved items to the current overview. Discovery outside the measured session needs its IP and time recorded. |

Implement A first, as requested. The choice between A and B concerns preparing the item list; the two browsing workflows are both part of A. Save the selected list in each run's results for comparison. Use one sequence of operator-like actions; the multi-tab workflow deliberately permits overlapping browser loads without adding concurrent application workers, queues, or a service.

Suggested organization for A:

- `main.py`: argument parsing and orchestration only.
- `config.py`: `.env`, environment, CLI precedence, validation, and redacted configuration snapshot.
- `browser_flow.py`: collection resolution, shared thumbnail selection, both workflows, tab tracking, and page readiness.
- `measurement.py`: seeded intervals, event classification, and window counts.
- `results.py`: incremental event output and final summaries, including partial-run recovery.

Use the repository's pinned Python runtime and `uv`. Add Playwright and its Chromium installation during implementation; retain `python-dotenv`. Review unused inherited dependencies then. Browser navigation and page-generated fetches belong to Playwright; any separately authored HTTP calls must use `httpx2`. A separate HTTP client is not needed for design A's browsing workload. Start with synchronous Playwright and an event-aware action loop; verify that opening tabs and checking readiness preserve the requested pace before live trials. Playwright documents multiple pages within a browser context and both synchronous and asynchronous APIs. [Playwright pages](https://playwright.dev/python/docs/pages).

## Collection access and browser behavior

Before implementing, verify the accepted collection identifier and its public Studio URL using a maintainer-selected collection. The phrase “collection-PID” must not lead to assuming it has an item PID's format: Brown's documentation shows collection API identifiers such as `403`, and distinguishes item web-view URLs from item API URLs. The exact input forms, Studio route, overview behavior, and selectors remain to be confirmed. [Brown collection API examples](https://github.com/Brown-University-Library/bdr_api_documentation/wiki/Collection-API-examples).

### Shared thumbnail selection

Use the same selection procedure for both workflows. Read public item-thumbnail links in their displayed order on the collection overview, deduplicate repeated links to the same item without changing order, and retain the effective sort and filters. Select positions 1, 3, 5, and so on by default; a starting-position setting of 2 selects positions 2, 4, 6, and so on. Record the positions and URLs, and cap the selected items at 20 by default. With the same overview order, starting position, and cap, both workflows must select the same intended items.

For the initial version, stay within the initial overview listing page; automatic listing pagination and recursive subcollections are deferred. Reading links already present in the page adds no deliberate navigation. Scroll only as needed to expose or click thumbnails; if additional links appear only after scrolling, use the same bounded discovery procedure for both workflows and count any resulting requests. Bound discovery by the duration limit and a scroll-action cap, and collect only enough candidates for the requested every-other-item selection. Record whether discovery was complete or capped. Empty, nested-collection-only, or shorter listings produce explicit results; use fewer items if necessary, without cycling or changing the selection pattern to fill the quota.

Save the overview URL, displayed and selected order, selection settings, discovery actions/duration, and available count. Match each later click to the selected item's link, including after a return; do not silently substitute another item if a listing changes or a link disappears. Record that condition and end the trial as unable to complete the intended workflow. A changed list between trials must be visible in the comparison report.

### Workflow 1: Open separate tabs, then review them

1. Open the collection overview and obtain the shared selection.
2. From that overview, open each selected thumbnail link in its own tab, targeting starts about one second apart with the configured variation. Retain the overview and all opened item tabs in the same browser context; with the default cap, there are at most 21 intended tabs. Keep working from the overview while opening the selection, scrolling as needed.
3. After opening the selection, activate the item tabs in opening order. Once each item is ready for review, spend about five seconds viewing it with the configured variation. Keep all the tabs open through this phase. Record activation, readiness, viewing start/end, and any additional traffic; tab activation alone is not another item-opening attempt.
4. End after the last selected tab's review, save the report, and close the context. Interference, an error, or the observation deadline ends the trial earlier, even if some tabs have not yet been reviewed.

The intended interaction is the researcher's “open link in new tab” behavior. During implementation, verify an appropriate browser link action, such as a platform-specific modifier or middle click, rather than driving the browser's native right-click menu. Record the actual method, verify that it preserves the selected destination and expected referrer behavior, and verify whether focus remains on the overview. Do not silently replace thumbnail interaction with unrelated direct URL navigation.

Keep the review phase even if a preliminary check finds no new requests during activation or viewing; that observation is useful evidence. Do not reload tabs to manufacture review traffic. Playwright documents that its pages behave as active pages, so do not assume it reproduces an ordinary background tab's throttling or visibility behavior. Validate activation and loading behavior with a local fixture and record any remaining difference in the report's evidence limits. [Playwright multiple pages](https://playwright.dev/python/docs/pages#multiple-pages), [tab activation](https://playwright.dev/python/docs/api/class-page#page-bring-to-front).

### Workflow 2: Open an item and return to the overview

1. Open the collection overview and obtain the same shared selection.
2. Click the first selected thumbnail in the same tab. Wait for the expected item content, then view it for about five seconds with the configured variation.
3. Click the page's back-to-collection link to return to the thumbnail overview. Wait for the overview, verify the expected collection/sort/filter state, and scroll if needed to find the next selected item.
4. Repeat the open/view/return cycle for the remaining selected items, up to 20 by default. After the final item's view and return to the overview, end and save the trial. Interference, an error, or the deadline ends it earlier.

Use the actual overview link and thumbnail links. Browser-history Back and direct URL visits are not substitutes for this workflow. Observe any return or scroll traffic without forcing reloads or inventing requests when the browser serves content locally. If the required return link is unavailable, report that the workflow cannot be completed. The upcoming image “next-page” feature is outside this initial scope, as are downloads, searches, and deeper viewer interaction.

Keep normal JavaScript, images, stylesheets, cookies, and caching enabled in both workflows. Do not suppress assets to improve throughput or intercept requests in a way that changes cache behavior. Observe the browser's natural overlapping requests across all tabs. Record headed mode, viewport, locale, browser version, fresh-context policy, and any deliberately configured non-secret header or browser-setting overrides; keep those settings fixed within a trial. Use ordinary browser defaults initially, without personal profiles, fingerprint disguises, or challenge-solving behavior.

## Recognizing interference and counting requests

### Classify evidence before stating a cause

| Observation | Result and initial behavior |
| --- | --- |
| Expected Studio content is visible, with no relevant interference evidence | Record successful access. A status of 200 alone is insufficient. |
| Response contains `cf-mitigated: challenge` | Record a confirmed Cloudflare challenge and stop new navigations. This is access interference, not necessarily a persistent block. |
| An identifiable denial page prevents access | Record denial evidence and its apparent source; label Cloudflare attribution as suspected until sufficiently supported or confirmed by Central IT. |
| HTTP 403 or 429 without decisive Cloudflare evidence | Record denied or rate-limited access with source unknown. Neither status alone proves Cloudflare caused it. |
| Timeout, DNS/TLS/proxy failure, HTTP 5xx, unexpected page, or missing expected content | Record the specific network, application, or unknown error and end the trial as inconclusive for a bot-protection threshold. |

Cloudflare documents `cf-mitigated: challenge` for its Challenge Pages. A `cf-ray` header helps correlate a request with Cloudflare logs, but its presence by itself does not mean Cloudflare blocked the request. Preserve observed HTTP status, allowlisted response headers, final URL, page title, and short classification evidence. [Challenge response detection](https://developers.cloudflare.com/cloudflare-challenges/challenge-types/challenge-pages/detect-response/), [Cloudflare Ray IDs](https://developers.cloudflare.com/fundamentals/reference/cloudflare-ray-id/).

Observe main-document and BDR subresource responses across the entire browser context, including background tabs, the overview, returns, and tab-review periods. A challenged API call or image can disrupt an item whose HTML loaded successfully. For the first version, stop on a challenge or denial from any configured BDR hostname and label whether the affected resource was a document, API request, or asset, along with its tab and workflow step. Treat this conservative resource-level endpoint separately from a confirmed inability to use the whole page. Third-party errors remain separate observations. Define the measured BDR hostnames before trials; do not assume all assets use the Studio hostname.

Attach context-level request, response, and failure listeners before initial navigation, and track new tabs and their opener/action associations. A popup's first request can precede availability of its Page object; listening only after the tab appears would miss that evidence. Retain initially unassigned requests and attach the tab identity when available, without dropping or counting them twice. [Playwright context request events](https://playwright.dev/python/docs/api/class-browsercontext#browser-context-on-request), [new-page event timing](https://playwright.dev/python/docs/api/class-browsercontext#browser-context-on-page).

At the first signal in any tab, set a context-wide stop flag and retain its timestamp, tab, action, and request identifier. Stop new openings, tab activations, returns, and scrolling; a signal during the last viewing period is still part of the trial. Browser work already in progress may finish; label any traffic after that signal and exclude it from counts at the endpoint. Close all tabs after saving evidence. Do not retry blocked requests, solve challenges, or poll automatically for recovery. Measuring challenge recovery or persistent-block duration is later work.

### What a “request” means

Keep three distinct counts:

1. **Item-opening attempts and successes:** one thumbnail-opening action is one attempt, whether it uses a new tab or the current one. Record readiness, completed foreground viewing, challenge, denial, error, and pending status separately. Activating an existing tab or returning to the overview is not another item-opening attempt.
2. **BDR document requests:** initial collection visits, item documents, return-to-overview documents, and redirect hops, each counted when actually issued. A return action need not produce a new document request; count observed requests, not assumed ones.
3. **Browser-observed BDR HTTP requests:** documents plus scripts, images, API calls, and other resources to configured hostnames across all tabs. Break down by hostname, resource type, originating tab/page role, and the workflow phase at request start; report third-party traffic separately. Keep tab origin separate from the current phase because an earlier tab may still load while another is being opened or reviewed.

Assign an internal ID to each observed request and link its response or failure to it. Do not add request and response events together as two requests. Redirects can issue additional requests, and HTTP error responses do not necessarily produce Playwright's `requestfailed` event. [Playwright request lifecycle](https://playwright.dev/python/docs/api/class-request).

These are browser-observed counts, not authoritative Cloudflare counter values. Cache behavior, service workers, requests from other clients sharing the exit, and Cloudflare's matching/counting rules can create differences. Retain normal browser behavior and ask Central IT to correlate the evidence with the actual matching rule, action, and available logs. Ray IDs help, but sampled Security Events may omit requests; absence from a sampled view is not proof that an event did not happen. [Playwright network behavior](https://playwright.dev/python/docs/network), [Cloudflare rate-limiting parameters](https://developers.cloudflare.com/waf/rate-limiting-rules/parameters/), [Ray ID lookup](https://developers.cloudflare.com/fundamentals/reference/cloudflare-ray-id/).

### The four requested time windows

Start the run clock at the first BDR collection request. Record opening, review, and return phases separately, and keep observation running through the final view or return required by the chosen workflow. At the first interference signal, or the end of observation if there was none, calculate trailing counts for **30, 60, 120, and 300 seconds** across all tabs from the event timestamps, including the affected request if its start falls in the window. For duration `W` and endpoint time `t`, use request starts in `(t - W, t]` when `t >= W`; for shorter observed history, use `[0, t]`. Cumulative checkpoints include the initial event at elapsed zero. Record the affected request's start and the later detection time separately. Item-attempt window counts use opening-action starts; among those attempts, count success only when readiness was observed by the endpoint, retaining unresolved attempts separately. A tab that was opened but not yet reviewed must not be reported as a completed view.

For each window, show observed coverage, item attempts/successes, document requests, total BDR requests, and endpoint classification. A block 42 seconds after run start gives full coverage of the preceding 30 seconds and only 42 seconds of history for the longer windows. Label those longer rows **partial observation**; do not extrapolate them to one, two, or five minutes.

Also produce cumulative counts from run start at the 30-, 60-, 120-, and 300-second checkpoints that were actually reached. These answer the separate question “what happened during the first N seconds?” Unreached checkpoints are unavailable, not zero. A completed run with no block is reported as “no interference observed within these limits”; it does not establish a safe maximum rate. Counts and coverage are computed after the run from the event log, so checkpoint reporting needs no extra requests.

Suggested report wording, with placeholders rather than fabricated measurements:

> On `<local Eastern date/time with offset>`, with user-supplied configuration `<label>` and workflow `<tabs/return>`, the trial first observed `<challenge/denial>` after `<elapsed>` seconds during `<workflow step>` in tab `<ID>`. Requested timing: `<opening interval and variation, if applicable; viewing duration and variation>`. Achieved opening interval mean/range: `<values>`. In the preceding 30 seconds, the browser attempted `<N>` item openings and observed `<M>` BDR HTTP requests across all tabs, including `<D>` document requests. Evidence: `<status, resource type, Ray ID>`. Cloudflare rule attribution: `<pending/confirmed>`.

Include analogous rows for 60, 120, and 300 seconds, with the coverage qualification above. Avoid the unqualified statement “Cloudflare blocks at N requests.”

## Configuration and results

Proposed precedence: explicit CLI flags, then process environment, then the selected `.env` file, then defaults. Save the effective non-secret settings and where each came from. A no-network configuration preview should make this easy to check. Cloudflare notes should identify relevant enabled bot protections, rule/version references, actions, and any known rate-counting periods or mitigation durations. Keep unknown details explicit; the app records the operator's description without interpreting or changing Cloudflare configuration.

| Setting | Proposed initial value or requirement |
| --- | --- |
| Collection identifier | Required positional argument; supported forms confirmed before implementation. |
| `WORKFLOW` / `--workflow` | Required choice: `tabs` or `return`; one workflow per trial, both included in the initial implementation. |
| `OPEN_INTERVAL_SECONDS` / `--open-interval-seconds` | `1.0` for `tabs`; target time between item-opening action starts. Not applicable to `return`. |
| `OPEN_JITTER_SECONDS` / `--open-jitter-seconds` | `0.1` for `tabs`; absolute variation around its opening interval. |
| `VIEW_SECONDS` / `--view-seconds` | `5.0` for both workflows; viewing time after activation and readiness. |
| `VIEW_JITTER_SECONDS` / `--view-jitter-seconds` | `0.5`; absolute variation around viewing duration. |
| `SELECTION_START` / `--selection-start` | `1` selects the first, third, fifth items; `2` selects the second, fourth, sixth. Fixed stride of two in both workflows. |
| `SEED` / `--seed` | Optional integer; generate and record one if omitted. |
| `MAX_DURATION_SECONDS` / `--max-duration-seconds` | `300`; overall observation deadline, including discovery. |
| `MAX_ITEMS` / `--max-items` | `20`; selectable range 1–20 initially. Caps item openings, not the remaining review/return steps. In `tabs`, allow only the overview plus this many intended item tabs. |
| `MAX_SCROLL_ACTIONS` / `--max-scroll-actions` | `20`; cap per initial discovery or search for the next selected thumbnail. All scrolling also obeys the observation deadline. Automatic listing pagination is deferred. |
| `NAVIGATION_TIMEOUT_SECONDS` | `30`, further limited by remaining run time; applies to navigation progress and required foreground readiness, without serially waiting for background-tab content that requires activation. |
| Timestamp timezone | `America/New_York`; local Eastern dates/times with explicit numeric offset and EST/EDT label in saved records and reports. |
| `CF_SETTINGS_LABEL`, `CF_SETTINGS_NOTES` | Required operator-recorded reference and description of the existing configuration; allow `unknown` explicitly, with a report limitation. Include settings effective time, reuse the label for unchanged settings, and use a new label when settings change. |
| `NETWORK_LABEL`, `EXIT_IP` | Network description and operator-recorded public exit IP; mark unverified values as such. Keep actual IP details in local results and reviewed Central IT material. |
| `PROXY_SERVER` | Optional fixed proxy for the whole trial; credentials come from separate environment values and are never logged. |
| `OUTPUT_DIR` | Relative directory `runs/`; one unique subdirectory per trial. |

Reject invalid identifiers, unknown workflows, invalid selection starts, timings outside the stated bounds, nonpositive limits, item caps above 20, malformed proxy configuration, and an unwritable output location before BDR access. Mark opening-interval settings inapplicable in `return`; reject explicit CLI opening-timing flags for that workflow and show any unused environment values in the no-network preview. The maximum duration governs observation and new actions; cleanup may finish afterward and is reported separately. If the item cap or selection is exhausted, finish the already scheduled viewing/return steps within the deadline. Report workflow completion, no eligible items, selection/scroll limitations, deadline expiry, interruption, and errors distinctly. Five minutes is a maximum; a successfully completed workflow may provide less than five minutes of observation.

Illustrative future commands, one independent trial at a time; they do not work in the starter application yet. Use the same collection, selection start, and item cap when comparing workflows, with the recorded settings and exit preparation described above:

```bash
uv run ./main.py "$COLLECTION_ID" --workflow tabs --open-interval-seconds 1 --open-jitter-seconds 0.1 --view-seconds 5 --view-jitter-seconds 0.5 --selection-start 1 --seed 42 --max-items 20
uv run ./main.py "$COLLECTION_ID" --workflow return --view-seconds 5 --view-jitter-seconds 0.5 --selection-start 1 --seed 42 --max-items 20
```

Keep `.env`, `runs/`, and any browser artifacts out of Git when implementation begins. The current `.gitignore` does not cover them yet. Commit only a placeholder `.env.example`. Never record authorization headers, cookies, proxy passwords, raw browser state, or full environment dumps. Store only necessary public URL information, removing sensitive query values. Screenshots, HTML, HAR files, and traces should be optional local diagnostics reviewed before sharing; omit them from the first version.

Each run should write:

- `run.json`: run identifier, local Eastern times and timezone, workflow, effective configuration, code revision/dirty state, Python/Playwright/browser versions, network information, browser settings and opening method, ordered selection with positions, seed and planned opening/viewing sequences, discovery facts, tab inventory, known unknowns, and final stop reason. User-supplied Cloudflare settings are labeled as such, not treated as automatically verified configuration.
- `events.jsonl`: incremental opening, navigation, request, response/failure, readiness, tab activation, viewing, return, scroll, and interference records using monotonic elapsed time, local Eastern time with offset, and internal action/tab/request IDs. Include sanitized requested and final URLs linked to each navigation outcome, and sanitized resource URLs. Preserve originating tab and workflow phase at each request start, pending associations, and unresolved attempts. Flush regularly so interruption preserves useful evidence.
- `summary.md`: readable conditions, achieved opening and viewing timings, workflow progress, first interference evidence or no-interference outcome, the four trailing windows, reached checkpoints, and space for Central IT's later finding. Include a chronological table of collection and item URLs actually attempted, with local Eastern start time/offset, workflow step, tab ID, final URL, and outcome, including unresolved attempts and repeated overview returns. Distinguish selected links, opened items, ready items, and completed views. Tab switches are separate actions; resource requests remain identifiable in the event log. JSON supplies machine-readable counts; no database or separate spreadsheet export is needed initially.

Each summary should also contain a compact comparison row: run identifier and local Eastern date/time with offset, Cloudflare settings label, workflow, selection start/cap, requested opening/viewing timings as applicable, achieved opening interval mean/range, observed duration, item attempts/successes/completed views, stop reason, and a relative link to the detailed report. If too few item openings occurred to calculate an interval, show it as unavailable. For the initial version, the operator can copy these rows into a reviewed Markdown comparison table grouped by configuration, workflow, and timing settings, keeping each repeat visible. The linked reports supply selected and checked URLs, all four window counts, and network/workload qualifications. This supports Central IT discussions without requiring automated trial batches or a comparison interface.

The report's **Known unknowns and evidence limits** section should distinguish recorded conditions from relevant unverified factors. Examples include the selected exit's previous traffic/reputation, whether geography or Tor status affects the applicable protection, unknown rule details or shared-IP traffic, and any unverified background-tab/activation behavior. Identify these as uncertainties, not claims about Cloudflare's configuration. Include observed limitations such as a shorter selection, changed overview order, delayed readiness detection, or an unreached time window. Keep the list short and specific to the trial, with room for operator notes and later Central IT findings.

Support interrupted and partial runs, explicit error reporting, and deterministic summary calculation from saved events. Keep a reviewed shareable report separate from raw local diagnostics. Central IT can fill in rule/action confirmation using timestamps, affected URLs, IP, and Ray IDs; automatic Cloudflare administration or log retrieval is outside the first version.

## Two ways to change IP addresses

These are the two proposed approaches. In both, end the trial first, change the exit, verify the route, and start a fresh browser context and trial. Changing a container or browser context alone is not a mechanism for changing the public IP.

### 1. Controlled VPN or proxy exits, managed separately — recommended

Use a small set of fixed, known public exits supplied by Central IT or an approved VPN/proxy setup. The operator selects a different exit between trials. A system VPN needs no app integration; an explicit browser proxy uses the optional fixed proxy setting. These are variants of the same externally managed exit approach. Playwright supports HTTP and SOCKS proxy configuration. [Playwright proxy support](https://playwright.dev/python/docs/network#http-proxy).

The separate setup is responsible for providing genuinely different public IPs, maintaining one route throughout a trial, and making its connection status visible. Record the selected exit and observed IP before the trial without extra BDR probes. Verify a browser proxy through that browser route, rather than using a direct shell request that could show a different IP. Central IT's BDR-side logs provide stronger confirmation of the source used for the actual requests. If the proxy fails, end the trial rather than falling back to direct access.

This approach offers more control over network type, geography, and repeated use. It requires access to multiple exits, and their prior reputation still matters. Several connections can share one public IP; reconnecting a VPN does not by itself prove a changed address. Do not add an allow rule that disables the protection being measured. Record any existing exception for the chosen exit.

Recommend keeping this setup outside the Python app initially. Its only optional app interface is one proxy endpoint held fixed for a complete run. This avoids making IP rotation part of the measurement loop.

### 2. Tor SOCKS proxy, with a separate Tor process or container

Run Tor separately and configure the Playwright browser to use its SOCKS proxy. Between completed trials, a separate operator tool can request new circuits through Tor's authenticated control interface and then start a new browser session. A later container setup could package the browser and Tor as separate services; containerization is packaging, while Tor supplies the changed exit.

Tor's `NEWNYM` signal applies clean circuits to new application requests and may be rate-limited. It does not promise a previously unused exit IP. Existing connections must not be treated as automatically moved, and a fresh exit must be checked. [Tor control specification](https://spec.torproject.org/control-spec/commands.html#signal).

This is inexpensive infrastructure to explore, but weaker for clean comparisons. Public Tor exits may already be denied, and changed exits introduce other traffic history and network differences. Tor itself documents that sites can identify and block Tor traffic. My recommendation follows from that limitation: use Tor for explicitly labeled Tor trials, rather than as the default baseline for typical researcher access. [Tor website-blocking guidance](https://support.torproject.org/tor-browser/general/website-blocking-tor-exits/).

A separate Tor setup must account for possible exit changes during a run and destination-dependent routing. An IP-check website alone cannot prove which exit BDR saw throughout the trial. Use BDR-side correlation when available; otherwise mark exit stability as unverified and avoid treating the trial as a clean single-IP threshold measurement. Playwright through Tor also remains a Playwright-controlled browser, not Tor Browser's full privacy configuration. Automated circuit selection, retries to obtain an unblocked exit, and Docker orchestration are deferred.

## Development steps and initial scope

The items below are candidate implementation issues to create after review of this plan. Only the design-plan issue is part of the present task.

| Candidate issue | Initial lightweight work | Later work or concern |
| --- | --- | --- |
| **Confirm the Studio browsing contract** | Verify one representative public collection, identifier/URL forms, thumbnail order, every-other-item selection, scrolling/lazy loading, actual back-to-collection links, new-tab link behavior, readiness signals, and relevant hostnames. Obtain sanitized example challenge/denial responses if available. | Automatic listing pagination, recursive subcollections, searches, downloads, image next-page navigation, and complex viewer interactions. |
| **Implement configuration and both browsing workflows** | Select design A. Add CLI/`.env` validation, shared thumbnail selection, seeded opening/viewing timings, one headed browser/context, `tabs` and `return`, normal assets, fixed optional proxy, duration/item/scroll limits, pending-tab handling, and graceful interruption. | Reusable discovery command, additional workflows/browser types, persisted profiles, automated trial batches, exact mean balancing. |
| **Implement evidence and reports** | Observe requests and interference across all tabs from their first requests; record actions, origins, readiness and viewing separately; stop all actions at the first signal; preserve partial results; use local Eastern timestamps; calculate all four windows/checkpoints; include checked URLs, comparison rows, and known unknowns. | Central IT log integration, optional reviewed screenshots/traces, report comparison UI, richer challenge recovery analysis. |
| **Verify the measurement before live comparisons** | Focused `unittest` tests and a local browser fixture for both workflows, including slow background loads and activation-related traffic; then a small manually observed BDR trial of each workflow under agreed settings when implementation is authorized. Compare event order/counts and actual behavior with browser evidence and Central IT's available logs. | Broader collection/browser coverage, repeated configuration studies, longer cooldown studies. |
| **Document one controlled exit setup separately** | Manual exit selection and verification, fixed exit per run, explicit network records, and a check that selected exits receive the intended Cloudflare rules. | Tor experimentation or container packaging as separate setup work. |

Implement in that order, combining adjacent issues if that keeps the work manageable. Reporting and limits belong in the first working version: without them, a blocked browser cannot answer the original question reliably.

Meaningful initial tests should cover:

- Configuration precedence, workflow-specific settings, invalid timings/limits, and local Eastern timestamps with offsets across daylight saving transitions; monotonic window calculations must remain independent of wall-clock changes.
- The same ordered every-other-item selection for both workflows, both starting positions, duplicate links, fewer than 20 available items, bounded lazy loading/scrolling, and a missing or changed selected link after a return.
- Reproducible opening/viewing sequences; `tabs` opening later items while earlier tabs load; slow-action overruns without catch-up bursts; a maximum of 20 item tabs plus the overview; review of all opened tabs after reaching the item cap; and correct one-tab open/view/actual-link-return order in `return`.
- Context-wide capture of each new tab's first request, unique counts despite later tab association, background challenges/denials, a challenged subresource, delayed or failed tab creation, per-navigation deadlines, and a signal during viewing or the final return that stops further actions.
- Activation that triggers additional requests and activation that triggers none, with neither counted as a new item opening; real overview-return traffic, redirects, overlapping tab requests, exact time-window boundaries/partial coverage, and unresolved readiness/viewing at the endpoint.
- Checked-URL reports that exclude unvisited selected links, comparison rows for interference/no-interference/inconclusive runs, unavailable timing values, known-unknown notes, and preservation of partial records on deadline expiry or interruption.

Use saved/synthetic events and a local fixture server, not repeated production traffic, for automated tests. Run `uv run ./run_tests.py` according to repository instructions.

The initial implementation is complete when an operator can supply a collection and settings reference, run either requested workflow with the same every-other-item selection, observe its recorded varying timing, and obtain local Eastern dated checked-URL records, workflow/tab evidence, an honest stop reason, all four window summaries, and a short known-unknowns section. Both workflows must be exercised during validation; neither is deferred. Saved reports must support a manually assembled comparison by workflow and timing under one configuration and, later, across configuration changes. Starting a new trial after changing exits remains an external operator step. Source-code implementation and live measurements await a later user request.
