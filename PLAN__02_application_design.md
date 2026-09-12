# Application design and development plan

Initial proposal by Codex, 2026-09-11, for [issue #5: Develop design plan](https://github.com/birkin/playwright_access_checker/issues/5). Work branch: `issue-5-develop-design-plan`.

This task produces a plan only. Application implementation, live frequency trials, and network setup are future work. Repository conventions are in [AGENTS.md](AGENTS.md).

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

Recommend a Python CLI using synchronous Playwright, one visible Chromium browser, one fresh browser context per trial, and one tab. Each run accepts one collection identifier and one target average interval. Record requests from the first collection access, open item pages sequentially, and stop at the first relevant challenge, denial, error, or run limit. Write local JSON records and a readable Markdown report. Change network exits manually between trials using a separate setup.
- BIRKIN-FEEDBACK: you noted "one tab". My sense is that, for a recent "blocked" report we got, the researcher accessed a  particular collection that contains thumbnail-links to item-pages. My understanding is that the researcher right-clicked to open (one after another) numerous thumbnail-links to open each item-page in its own tab for future review. This will become one interaction-flow that we'll have playwright test. We'll likely have others.

The user's clarification calls for variation around the target pace: for example, intervals between 4.5 and 5.5 seconds for an average of five seconds. This plan recommends seeded pseudorandom variation, so the intended sequence can be reproduced. Other details below remain design proposals.

An observed block is a result under recorded conditions, not proof of a universal request threshold. Cloudflare's bot assessment can use headers, session characteristics, and browser signals; its rate-limiting rules can count selected traffic using characteristics beyond IP address. Small timing variations model browsing rhythm but do not establish equivalence to a human-operated browser. [Cloudflare bot scores](https://developers.cloudflare.com/bots/concepts/bot-score/), [rate-limiting parameters](https://developers.cloudflare.com/waf/rate-limiting-rules/parameters/).
- BIRKIN-FEEDBACK: Good point -- there will be many things we can control for (ie we will be able to configure headers and many browser-indicators) -- but the end-report should contain a section listing factors we're aware of that we don't know about (ie -- if we were to use TOR for getting a new IP, it's possible that Cloudflare may have different sensitivities for traffic coming from different IP regaions). This section isn't intended to be an exhaustive list of everything we can imagine we don't know -- simply a way to remind ourselves of the limits of the evidence we're gathering.


## Trial procedure and timing

### One trial

1. Record a user-supplied Cloudflare settings label and notes, when those settings took effect, and the network exit being used. Keep settings unchanged throughout the trial. Start with an exit expected to be unblocked; document any known recent use or cooldown.
2. Open a fresh browser context, retaining its cookies and cache throughout this trial. Attach network observers before making the first BDR request. Use the collection visit itself as the initial access check, rather than silently making extra BDR probes beforehand.
3. Visit the collection, gather a bounded list of item links through its public listing pages, then open those items sequentially. Pace collection pagination too. Label discovery and item-browsing events separately, but include both in the overall traffic history.
4. Keep the target average interval unchanged. Stop issuing new navigation actions as soon as an interference signal is observed. Also stop on the duration limit, item limit, exhausted collection, interruption, or an error that prevents reliable measurement. Preserve partial results.
5. End and save the trial before changing IP or browser state. A new exit starts a new trial with a new identifier. A challenge on the initial collection visit is an initial-access failure; it does not establish a threshold caused by this trial.

The initial successful collection visit establishes observed access, not an empty Cloudflare counter or a clean IP history. Discovery traffic may itself cause interference and must never disappear from the report.

### Timing definition

The interval is measured from the start of one item navigation to the start of the next. It is not an extra five-second sleep after page loading. Collection listing navigations use the same pacing rule, with their own recorded intervals; the transition into item browsing also includes a paced wait.
- BIRKIN-FEEDBACK: yes -- this is important, given my "multiple-tab" comment on your "one-tab" text, above.

For target interval `T` and variation `J`, draw each planned interval independently from a uniform distribution between `T - J` and `T + J`, using a recorded integer seed. Require finite values with `T > 0` and `0 <= J < T`. For `T=5` and `J=0.5`, the expected mean is five seconds; a finite trial will usually have a slightly different mean. Record the planned sequence and the achieved intervals. Exact mean balancing can be added later if needed; it is unnecessary for the first version.
- BIRKIN-FEEDBACK: agreed; we're not mixing dangerous chemicals -- a good ballpark effort is good-enough.

Use a monotonic clock for elapsed times and UTC timestamps for correlation with Central IT. Schedule the next navigation relative to the previous actual start. Wait for both the scheduled time and a ready page, including a short minimum viewing time after readiness (proposed default: one second). If a slow page prevents the planned interval, record the overrun and proceed when ready. Do not launch overlapping navigations or accelerate later actions to recover lost time. Report the achieved mean and range prominently.
- BIRKIN-FEEDBACK: no UTC timestamps; use local-EST timestamps

Readiness means the expected collection or item content is visible, within a bounded timeout. Check for challenges and denials while waiting. Use navigation and locator waits, rather than treating a fixed sleep or `networkidle` as evidence of success. During deliberate pacing waits in synchronous Playwright, use short Playwright waits that continue processing browser events, rechecking the stop condition and deadline between them. Playwright documents both its readiness behavior and the problem with blocking its event processing using `time.sleep()`. [Page API](https://playwright.dev/python/docs/api/class-page), [library guidance](https://playwright.dev/python/docs/library#timesleep-leads-to-outdated-state).

### Comparing runs

Start with one target pace, such as five seconds with half-second variation. Collect multiple access-frequency data points by trying other paces in separate trials under the same existing Cloudflare configuration. The 30-, 60-, 120-, and 300-second windows describe traffic within a trial; they do not substitute for trials at different browsing paces. Hold the item order, browser version, viewport, cache policy, seed, discovery limits, and network type constant where possible. Record any differences in the discovered item list or discovery workload. Repeat a useful condition, ideally three times initially, and report the individual results and range. This is a practical comparison, not a statistical guarantee.

Retain trials with no interference alongside challenged or denied trials, showing their observed duration and workload; retain inconclusive and partial trials with their limitations. Together these supply evidence about the effects of the existing configuration for discussion with Central IT. Once Central IT changes settings, use a new configuration label and effective time, then compare the same paces and recorded conditions after the expected cooldown or on another documented exit. Changing IP also changes a condition; do not combine results from unlike networks into a single threshold. A short manually operated browser session can later help assess how well the scripted workflow represents researcher behavior.

## Two application designs

| Design | How it works | Advantages | Costs and limits |
| --- | --- | --- | --- |
| **A. One-command browser-led runner — recommended initially** | One CLI command resolves the collection, gathers a bounded item list in the browser, browses it sequentially, and writes the report. A few small modules separate configuration, navigation, timing, and results. | Small implementation; browser requests follow one session and network route; easy to watch and debug; no database or asynchronous framework. | Collection discovery consumes requests in each run. Listing changes can change the workload. Selectors need maintenance. |
| **B. Separate discovery and trial commands** | A discovery command saves an ordered item-list file. A trial command visits the collection and browses that saved list using sequential Playwright. Discovery could use the public collection API, with `httpx2` as required by repository guidance. | Reuses an exact item list across trials; avoids repeated enumeration on the measured IP; easier later comparison and replay. | More commands, file validation, and stale-list handling. API discovery may not exercise the same browser path or protection. Discovery must happen outside the measured session, with its IP and time recorded. |

Choose A first because it directly matches the requested collection-to-browser workflow and keeps installation and use simple. Save the ordered list in its results so B can be added without changing the measurement definitions. Both designs keep application navigation sequential; neither needs concurrent workers, queues, or a service.

BIRKIN_FEEDBACK: Choose A -- it meshes well with the description of a reported block that I mentioned above.

Suggested organization for A:

- `main.py`: argument parsing and orchestration only.
- `config.py`: `.env`, environment, CLI precedence, validation, and redacted configuration snapshot.
- `browser_flow.py`: collection resolution, bounded discovery, page readiness, and sequential browsing.
- `measurement.py`: seeded intervals, event classification, and window counts.
- `results.py`: incremental event output and final summaries, including partial-run recovery.

Use the repository's pinned Python runtime and `uv`. Add Playwright and its Chromium installation during implementation; retain `python-dotenv`. Review unused inherited dependencies then. Browser navigation and page-generated fetches belong to Playwright; any separately authored HTTP calls must use `httpx2`. A separate HTTP client is not needed for design A's browsing workload. Synchronous Playwright suits this linear workflow and has a documented Python API. [Playwright library](https://playwright.dev/python/docs/library).

## Collection access and browser behavior

Before implementing, verify the accepted collection identifier and its public Studio URL using a maintainer-selected collection. The phrase “collection-PID” must not lead to assuming it has an item PID's format: Brown's documentation shows collection API identifiers such as `403`, and distinguishes item web-view URLs from item API URLs. The exact input forms, Studio route, pagination, and selectors remain to be confirmed. [Brown collection API examples](https://github.com/Brown-University-Library/bdr_api_documentation/wiki/Collection-API-examples).

Initial discovery should:

- Visit public Studio listing pages in their displayed order, retaining the collection's effective sort and filters in the run record.
- Collect only direct public item-page links; deduplicate without changing their order. Follow bounded listing pagination when necessary, without opening subcollections recursively.
- Stop discovery at the item limit, listing-page limit, end of listing, run deadline, or access interference. Record whether enumeration was complete or capped.
- Recognize nested-collection-only and empty collections explicitly. They should produce an explanation, not an accidental crawl of unrelated collections.
- Save the collection URL, ordered item URLs, discovery duration, and discovered count for comparison. Do not claim a five-minute item-browsing observation if discovery or an exhausted list prevented it.

- BIRKIN_FEEDBACK: Let's have two workflows, both of which will be exercised.
    - First workflow... (I'll give roughly real human numbers -- but of course the purpose will be to vary them to explore failure)
        - The researcher will go to the collection-pid. That page will load a list of items.
        - The researcher right-clicks, about 1-second-apart, every other item-thumbnail on the collection page, to be opened in a separate tab -- up to 20 items.
        - The researcher than spends about 5 seconds examining each page(-tab). I'm aware this may not be useful for playwright to mimic if it's determined that info is only loaded on the instantiation of the tab; I'm just describing a workflow.
        - End.
    - Second workflow...
        - The researcher will go to the collection-pid. That page will load a list of items. (Same as first workflow.)
        - The researcher does the following 20-times -- in the same tab:
            - Open a thumbnail.
            - Examines it for five seconds.
            - Hits the back-to-collection link to see the thumbnail overview again.
            - Scrolls if necessary to find the next item.
            - Clicks that thumbnail.
            - Examines it for five seconds.
            - etc.
        - Notes:
            - Give the same collection as in the first workflow, and that the order of the thumbnails is the same, the same every-other-item selection mechanism should be used for both workflows (ie either first, third, fifth -- or second, fourth, sixth).
            - We're soon rolling out a new feature that researchers might like: being on an image and selecting "nex-page". Ignore that for now -- and assume that to get to a different page you need to click a url that gets you back to an overview.

For the first version, navigate directly to the discovered item URLs in the same tab. This represents a researcher working through a prepared list of item links. It does not model returning to the collection between every item, searching, opening downloads, or using viewers deeply. Those actions produce different workloads and can be separate future browsing profiles.

Keep normal JavaScript, images, stylesheets, cookies, and caching behavior enabled. Do not suppress assets to improve throughput or intercept requests in a way that changes cache behavior during real trials. One deliberate navigation at a time still produces the browser's normal overlapping resource requests; observe those requests without trying to serialize them. Record the headed mode, viewport, locale, browser version, and fresh-context policy. Do not reuse a personal browsing profile or add fingerprint disguises or challenge-solving behavior.

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

Observe main-document and BDR subresource responses. A challenged API call or image can disrupt an item whose HTML loaded successfully. For the first version, stop on a challenge or denial from any configured BDR hostname and label whether the affected resource was a document, API request, or asset. Treat this conservative resource-level endpoint separately from a confirmed inability to use the whole page. Third-party errors remain separate observations. Define the measured BDR hostnames before trials; do not assume all assets use the Studio hostname.

At the first signal, set a stop flag and retain its timestamp and request identifier. Browser work already in progress may finish; label any traffic after that signal and exclude it from counts at the endpoint. Close the browser after saving evidence. Do not retry blocked requests, solve challenges, or poll automatically for recovery. Measuring challenge recovery or persistent-block duration is later work.

### What a “request” means

Keep three distinct counts:

1. **Item navigation attempts and successes:** one attempted item opening is one action; retain success, challenge, denial, and error outcomes separately.
2. **BDR document requests:** collection pages, item documents, and redirect hops, each counted when issued.
3. **Browser-observed BDR HTTP requests:** documents plus scripts, images, API calls, and other resources to the configured hostnames. Break down by hostname, resource type, and discovery versus item phase; report third-party traffic separately.

Assign an internal ID to each observed request and link its response or failure to it. Do not add request and response events together as two requests. Redirects can issue additional requests, and HTTP error responses do not necessarily produce Playwright's `requestfailed` event. [Playwright request lifecycle](https://playwright.dev/python/docs/api/class-request).

These are browser-observed counts, not authoritative Cloudflare counter values. Cache behavior, service workers, requests from other clients sharing the exit, and Cloudflare's matching/counting rules can create differences. Retain normal browser behavior and ask Central IT to correlate the evidence with the actual matching rule, action, and available logs. Ray IDs help, but sampled Security Events may omit requests; absence from a sampled view is not proof that an event did not happen. [Playwright network behavior](https://playwright.dev/python/docs/network), [Cloudflare rate-limiting parameters](https://developers.cloudflare.com/waf/rate-limiting-rules/parameters/), [Ray ID lookup](https://developers.cloudflare.com/fundamentals/reference/cloudflare-ray-id/).

### The four requested time windows

Start the run clock at the first BDR collection request. Record item-browsing start separately. At the first interference signal, or the end of observation if there was none, calculate trailing counts for **30, 60, 120, and 300 seconds** from the event timestamps, including the affected request if its start falls in the window. For duration `W` and endpoint time `t`, use request starts in `(t - W, t]` when `t >= W`; for shorter observed history, use `[0, t]`. Cumulative checkpoints include the initial event at elapsed zero. Record the affected request's start and the later detection time separately. Count an item as successful only if its readiness was observed by the endpoint, retaining unresolved attempts separately.

For each window, show observed coverage, item attempts/successes, document requests, total BDR requests, and endpoint classification. A block 42 seconds after run start gives full coverage of the preceding 30 seconds and only 42 seconds of history for the longer windows. Label those longer rows **partial observation**; do not extrapolate them to one, two, or five minutes.

Also produce cumulative counts from run start at the 30-, 60-, 120-, and 300-second checkpoints that were actually reached. These answer the separate question “what happened during the first N seconds?” Unreached checkpoints are unavailable, not zero. A completed run with no block is reported as “no interference observed within these limits”; it does not establish a safe maximum rate. Counts and coverage are computed after the run from the event log, so checkpoint reporting needs no extra requests.

Suggested report wording, with placeholders rather than fabricated measurements:

> On `<UTC date/time>`, with user-supplied configuration `<label>`, the trial first observed `<challenge/denial>` after `<elapsed>` seconds. The requested item interval was 5.0 seconds with ±0.5 seconds variation; achieved mean was `<value>`. In the preceding 30 seconds, the browser attempted `<N>` item openings and observed `<M>` BDR HTTP requests, including `<D>` document requests. Evidence: `<status, resource type, Ray ID>`. Cloudflare rule attribution: `<pending/confirmed>`.

Include analogous rows for 60, 120, and 300 seconds, with the coverage qualification above. Avoid the unqualified statement “Cloudflare blocks at N requests.”

## Configuration and results

Proposed precedence: explicit CLI flags, then process environment, then the selected `.env` file, then defaults. Save the effective non-secret settings and where each came from. A no-network configuration preview should make this easy to check. Cloudflare notes should identify relevant enabled bot protections, rule/version references, actions, and any known rate-counting periods or mitigation durations. Keep unknown details explicit; the app records the operator's description without interpreting or changing Cloudflare configuration.

| Setting | Proposed initial value or requirement |
| --- | --- |
| Collection identifier | Required positional argument; supported forms confirmed before implementation. |
| `INTERVAL_SECONDS` / `--interval-seconds` | `5.0`; target navigation start interval. |
| `JITTER_SECONDS` / `--jitter-seconds` | `0.5`; absolute variation on either side of the target. |
| `SEED` / `--seed` | Optional integer; generate and record one if omitted. |
| `MAX_DURATION_SECONDS` / `--max-duration-seconds` | `300`; overall observation deadline, including discovery. |
| `MAX_ITEMS` / `--max-items` | `100`; caps discovered items and attempted item openings. |
| `MAX_COLLECTION_PAGES` / `--max-collection-pages` | `10`; explicit bounded discovery. |
| `NAVIGATION_TIMEOUT_SECONDS` | `30`, further limited by the remaining run time. |
| `MIN_VIEW_SECONDS` | `1.0`; can make the achieved interval exceed the planned interval. |
| `CF_SETTINGS_LABEL`, `CF_SETTINGS_NOTES` | Required operator-recorded reference and description of the existing configuration; allow `unknown` explicitly, with a report limitation. Include settings effective time, reuse the label for unchanged settings, and use a new label when settings change. |
| `NETWORK_LABEL`, `EXIT_IP` | Network description and operator-recorded public exit IP; mark unverified values as such. Keep actual IP details in local results and reviewed Central IT material. |
| `PROXY_SERVER` | Optional fixed proxy for the whole trial; credentials come from separate environment values and are never logged. |
| `OUTPUT_DIR` | Relative directory `runs/`; one unique subdirectory per trial. |

Reject invalid identifiers, non-finite or negative timings, nonpositive limits, malformed proxy configuration, and an unwritable output location before BDR access. The maximum duration governs observation and new actions; cleanup may finish afterward and is reported separately. Collection exhaustion ends a run without cycling through the same items. Thus five minutes is a maximum, not a promise of five minutes of item access.

Illustrative future command; it does not work in the starter application yet:

```bash
uv run ./main.py "$COLLECTION_ID" --interval-seconds 5 --jitter-seconds 0.5 --seed 42 --max-duration-seconds 300 --max-items 100
```

Keep `.env`, `runs/`, and any browser artifacts out of Git when implementation begins. The current `.gitignore` does not cover them yet. Commit only a placeholder `.env.example`. Never record authorization headers, cookies, proxy passwords, raw browser state, or full environment dumps. Store only necessary public URL information, removing sensitive query values. Screenshots, HTML, HAR files, and traces should be optional local diagnostics reviewed before sharing; omit them from the first version.

Each run should write:

- `run.json`: run identifier, UTC times, effective configuration, code revision/dirty state, Python/Playwright/browser versions, network information, browser settings, ordered item list, seed and planned intervals, discovery facts, and final stop reason. User-supplied Cloudflare settings are labeled as such, not treated as automatically verified configuration.
- `events.jsonl`: incremental navigation, request, response/failure, readiness, timing, and interference records using elapsed time, UTC time, and internal IDs. Include sanitized requested and final URLs linked to each navigation outcome, and sanitized URLs for observed resource requests. Flush regularly so interruption preserves useful evidence.
- `summary.md`: readable conditions, achieved pace, first interference evidence or no-interference outcome, the four trailing windows, reached checkpoints, limitations, and space for Central IT's later finding. Include a chronological table of collection and item URLs actually attempted, with UTC start time, discovery/item phase, final URL, and outcome, including unresolved attempts. Links merely discovered are not checked URLs. Resource requests remain separately identifiable in the event log. JSON supplies machine-readable counts; no database or separate spreadsheet export is needed initially.

Each summary should also contain a compact comparison row: run identifier and UTC date/time, Cloudflare settings label, target interval and variation, achieved item interval mean/range, observed duration, item attempts/successes, stop reason, and a relative link to the detailed report. If too few item navigations occurred to calculate an interval, show it as unavailable. For the initial version, the operator can copy these rows into a reviewed Markdown comparison table grouped by configuration and target pace, keeping each repeat visible. The linked reports supply the checked URLs, all four window counts, and the network and workload qualifications. This makes multiple frequency results ready for Central IT discussions without requiring automated trial batches or a comparison interface.

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
| **Confirm the Studio browsing contract** | Verify one representative public collection, accepted identifier forms, Studio URL resolution, item links, pagination, readiness signals, and relevant hostnames. Obtain sanitized example challenge/denial responses if available. | Recursive subcollections, searches, downloads, and complex viewer interactions. |
| **Implement configuration and sequential browsing** | CLI/`.env` validation, one fixed average pace with seeded variation, bounded discovery, one headed browser/context/tab, normal assets, fixed optional proxy, duration/item/page limits, and graceful interruption. | Reusable discovery command, multiple browser types, persisted profiles, automated trial batches, exact mean balancing. |
| **Implement evidence and reports** | Observe document/subresource outcomes, stop at first relevant signal, retain partial event records, record conditions and actually attempted URLs, calculate all four windows plus reached checkpoints, and include a reusable comparison row for each trial. | Central IT log integration, optional reviewed screenshots/traces, report comparison UI, richer challenge recovery analysis. |
| **Verify the measurement before live comparisons** | Focused `unittest` tests and a local browser fixture; then one small manually observed BDR trial under agreed settings when implementation is authorized. Compare event order/counts with browser evidence and Central IT's available logs. | Broader collection/browser coverage, repeated configuration studies, longer cooldown studies. |
| **Document one controlled exit setup separately** | Manual exit selection and verification, fixed exit per run, explicit network records, and a check that selected exits receive the intended Cloudflare rules. | Tor experimentation or container packaging as separate setup work. |

Implement in that order, combining adjacent issues if that keeps the work manageable. Reporting and limits belong in the first working version: without them, a blocked browser cannot answer the original question reliably.

Meaningful initial tests should cover configuration precedence and invalid input; reproducible bounded intervals; slow-page overruns without catch-up bursts; duplicate and paginated item links; collection exhaustion; challenge/denial/network-error distinctions; a challenged subresource; redirect counting; exact time-window boundaries and partial coverage; exclusion of unvisited discovered links from checked-URL reports; comparison rows for interference, no-interference, and inconclusive runs, including unavailable timing values; and preservation of results on timeout or interruption. Use saved/synthetic events and a local fixture server, not repeated production traffic, for automated tests. Run `uv run ./run_tests.py` according to repository instructions.

The initial implementation is complete when an operator can supply a collection and settings reference, watch sequential browsing at a recorded varying pace, obtain the dated checked-URL record, an honest stop reason, and the four requested window summaries, and start an independent trial after changing exits externally. Saved reports must support a manually assembled comparison of multiple browsing paces under one configuration and, later, across configuration changes. Source-code implementation and live measurements await a later user request.
