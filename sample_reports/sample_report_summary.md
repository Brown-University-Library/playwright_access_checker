# Trial 20260916T091249-0400-5c4b10b7

- [Conditions and outcome](#conditions-and-outcome)
- [Request counts](#request-counts)
- [Checked URLs](#checked-urls)
- [Viewing and tab switches](#viewing-and-tab-switches)
- [Listing observations](#listing-observations)
- [Comparison row](#comparison-row)
- [Known unknowns and evidence limits](#known-unknowns-and-evidence-limits)
- [Central IT findings](#central-it-findings)

## Conditions and outcome

No interference observed within these limits.

- Started: 2026-09-16T09:12:51.178703-0400 EDT.
- Observed duration: 124.828 seconds. Workflow: tabs.
- network-filter vendor settings (user supplied): unknown. Current rules have not been supplied; do not infer a network-filter vendor request limit.
- Settings took effect: unknown.
- Connection: unknown; public IP: unknown. Public IP, recent use, and time since any previous block have not been verified.
- Included BDR hosts: repository.library.brown.edu.
- Stopped during view_item, tab unavailable, request unavailable.
- Evidence: HTTP unavailable; source: unavailable; Ray ID: unavailable.
- Affected URL: unavailable. Error: unavailable.
- Selected links: 20; item attempts: 20; ready: 20; completed views: 20.
- Total BDR page requests: 21; all BDR HTTP requests: 850; other HTTP requests: 398.
- Actual opening interval average (range): 1.067s (0.972–1.174s).
- Completed viewing duration average (range): 5.117s (4.560–5.523s).

## Request counts

Each row counts starts across all tabs. Successes were observed ready by the row’s end.

| Preceding seconds | Observed seconds | Coverage | Attempts | Ready | Completed views | Page requests | All BDR | Other hosts |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 30 | 30.000 | full | 0 | 0 | 0 | 0 | 0 | 0 |
| 60 | 60.000 | full | 0 | 0 | 0 | 0 | 0 | 0 |
| 120 | 120.000 | full | 16 | 16 | 16 | 16 | 591 | 308 |
| 300 | 124.828 | partial observation | 20 | 20 | 20 | 21 | 850 | 398 |

| Seconds from start | Attempts | Ready | Completed views | Page requests | All BDR | Other hosts |
| --- | --- | --- | --- | --- | --- | --- |
| 30 | 20 | 20 | 1 | 21 | 850 | 398 |
| 60 | 20 | 20 | 7 | 21 | 850 | 398 |
| 120 | 20 | 20 | 19 | 21 | 850 | 398 |
| 300 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |

Request breakdowns by hostname, content type, tab, page role, and stage are in `run.json`.

## Checked URLs

Only attempted visits appear here. Selected but unopened items remain in `run.json`.

| Local Eastern start | Step | Tab | Requested URL | Final URL | Result |
| --- | --- | --- | --- | --- | --- |
| 2026-09-16T09:12:51.169006-0400 EDT | collection open | tab-1 | https://repository.library.brown.edu/studio/collections/bdr:nz9qn2kb/?page=1&amp;per_page=50 | https://repository.library.brown.edu/studio/collections/bdr:nz9qn2kb/?page=1&amp;per_page=50 | ready |
| 2026-09-16T09:12:52.181317-0400 EDT | item open | tab-2 | https://repository.library.brown.edu/studio/item/bdr:597184/ | https://repository.library.brown.edu/studio/item/bdr:597184/ | ready |
| 2026-09-16T09:12:53.272705-0400 EDT | item open | tab-3 | https://repository.library.brown.edu/studio/item/bdr:597186/ | https://repository.library.brown.edu/studio/item/bdr:597186/ | ready |
| 2026-09-16T09:12:54.244873-0400 EDT | item open | tab-4 | https://repository.library.brown.edu/studio/item/bdr:741109/ | https://repository.library.brown.edu/studio/item/bdr:741109/ | ready |
| 2026-09-16T09:12:55.265017-0400 EDT | item open | tab-5 | https://repository.library.brown.edu/studio/item/bdr:747072/ | https://repository.library.brown.edu/studio/item/bdr:747072/ | ready |
| 2026-09-16T09:12:56.278460-0400 EDT | item open | tab-6 | https://repository.library.brown.edu/studio/item/bdr:597187/ | https://repository.library.brown.edu/studio/item/bdr:597187/ | ready |
| 2026-09-16T09:12:57.398645-0400 EDT | item open | tab-7 | https://repository.library.brown.edu/studio/item/bdr:758319/ | https://repository.library.brown.edu/studio/item/bdr:758319/ | ready |
| 2026-09-16T09:12:58.512046-0400 EDT | item open | tab-8 | https://repository.library.brown.edu/studio/item/bdr:597189/ | https://repository.library.brown.edu/studio/item/bdr:597189/ | ready |
| 2026-09-16T09:12:59.666969-0400 EDT | item open | tab-9 | https://repository.library.brown.edu/studio/item/bdr:745156/ | https://repository.library.brown.edu/studio/item/bdr:745156/ | ready |
| 2026-09-16T09:13:00.661005-0400 EDT | item open | tab-10 | https://repository.library.brown.edu/studio/item/bdr:752247/ | https://repository.library.brown.edu/studio/item/bdr:752247/ | ready |
| 2026-09-16T09:13:01.724787-0400 EDT | item open | tab-11 | https://repository.library.brown.edu/studio/item/bdr:597192/ | https://repository.library.brown.edu/studio/item/bdr:597192/ | ready |
| 2026-09-16T09:13:02.711341-0400 EDT | item open | tab-12 | https://repository.library.brown.edu/studio/item/bdr:597195/ | https://repository.library.brown.edu/studio/item/bdr:597195/ | ready |
| 2026-09-16T09:13:03.737884-0400 EDT | item open | tab-13 | https://repository.library.brown.edu/studio/item/bdr:597196/ | https://repository.library.brown.edu/studio/item/bdr:597196/ | ready |
| 2026-09-16T09:13:04.836253-0400 EDT | item open | tab-14 | https://repository.library.brown.edu/studio/item/bdr:597201/ | https://repository.library.brown.edu/studio/item/bdr:597201/ | ready |
| 2026-09-16T09:13:05.826419-0400 EDT | item open | tab-15 | https://repository.library.brown.edu/studio/item/bdr:756450/ | https://repository.library.brown.edu/studio/item/bdr:756450/ | ready |
| 2026-09-16T09:13:06.856657-0400 EDT | item open | tab-16 | https://repository.library.brown.edu/studio/item/bdr:758456/ | https://repository.library.brown.edu/studio/item/bdr:758456/ | ready |
| 2026-09-16T09:13:08.008580-0400 EDT | item open | tab-17 | https://repository.library.brown.edu/studio/item/bdr:742222/ | https://repository.library.brown.edu/studio/item/bdr:742222/ | ready |
| 2026-09-16T09:13:09.117427-0400 EDT | item open | tab-18 | https://repository.library.brown.edu/studio/item/bdr:754041/ | https://repository.library.brown.edu/studio/item/bdr:754041/ | ready |
| 2026-09-16T09:13:10.160998-0400 EDT | item open | tab-19 | https://repository.library.brown.edu/studio/item/bdr:743505/ | https://repository.library.brown.edu/studio/item/bdr:743505/ | ready |
| 2026-09-16T09:13:11.288783-0400 EDT | item open | tab-20 | https://repository.library.brown.edu/studio/item/bdr:749083/ | https://repository.library.brown.edu/studio/item/bdr:749083/ | ready |
| 2026-09-16T09:13:12.463192-0400 EDT | item open | tab-21 | https://repository.library.brown.edu/studio/item/bdr:752238/ | https://repository.library.brown.edu/studio/item/bdr:752238/ | ready |

## Viewing and tab switches

A completed viewing duration does not mean the entire page was seen.

| Attempt | Planned seconds | Actual seconds | Scrolls | Bottom reached | Completed |
| --- | --- | --- | --- | --- | --- |
| item-1 | 4.506 | 4.560 | 3 | True | True |
| item-2 | 5.306 | 5.361 | 3 | True | True |
| item-3 | 5.198 | 5.251 | 3 | True | True |
| item-4 | 4.840 | 4.894 | 3 | True | True |
| item-5 | 4.655 | 4.693 | 3 | True | True |
| item-6 | 5.457 | 5.514 | 3 | True | True |
| item-7 | 4.837 | 4.919 | 3 | True | True |
| item-8 | 4.593 | 4.661 | 3 | True | True |
| item-9 | 4.597 | 4.683 | 3 | True | True |
| item-10 | 5.347 | 5.418 | 3 | True | True |
| item-11 | 5.104 | 5.145 | 3 | True | True |
| item-12 | 5.307 | 5.343 | 3 | True | True |
| item-13 | 5.230 | 5.264 | 3 | True | True |
| item-14 | 5.036 | 5.092 | 3 | True | True |
| item-15 | 5.473 | 5.523 | 3 | True | True |
| item-16 | 4.879 | 4.946 | 3 | True | True |
| item-17 | 5.052 | 5.115 | 3 | True | True |
| item-18 | 5.329 | 5.378 | 3 | True | True |
| item-19 | 5.119 | 5.156 | 3 | True | True |
| item-20 | 5.362 | 5.427 | 3 | True | True |

| Switch time | Attempt | Tab |
| --- | --- | --- |
| 2026-09-16T09:13:12.580699-0400 EDT | item-1 | tab-2 |
| 2026-09-16T09:13:17.197888-0400 EDT | item-2 | tab-3 |
| 2026-09-16T09:13:22.613598-0400 EDT | item-3 | tab-4 |
| 2026-09-16T09:13:27.918566-0400 EDT | item-4 | tab-5 |
| 2026-09-16T09:13:32.891830-0400 EDT | item-5 | tab-6 |
| 2026-09-16T09:13:37.631830-0400 EDT | item-6 | tab-7 |
| 2026-09-16T09:13:43.208782-0400 EDT | item-7 | tab-8 |
| 2026-09-16T09:13:48.167280-0400 EDT | item-8 | tab-9 |
| 2026-09-16T09:13:52.870004-0400 EDT | item-9 | tab-10 |
| 2026-09-16T09:13:57.599298-0400 EDT | item-10 | tab-11 |
| 2026-09-16T09:14:03.063780-0400 EDT | item-11 | tab-12 |
| 2026-09-16T09:14:08.261216-0400 EDT | item-12 | tab-13 |
| 2026-09-16T09:14:13.666163-0400 EDT | item-13 | tab-14 |
| 2026-09-16T09:14:19.001856-0400 EDT | item-14 | tab-15 |
| 2026-09-16T09:14:24.133088-0400 EDT | item-15 | tab-16 |
| 2026-09-16T09:14:29.715436-0400 EDT | item-16 | tab-17 |
| 2026-09-16T09:14:34.704492-0400 EDT | item-17 | tab-18 |
| 2026-09-16T09:14:39.865426-0400 EDT | item-18 | tab-19 |
| 2026-09-16T09:14:45.298624-0400 EDT | item-19 | tab-20 |
| 2026-09-16T09:14:50.513091-0400 EDT | item-20 | tab-21 |

## Listing observations

Requested: page 1, 50 per page. Original item selection is retained after returns.

| Time | Step | Page | Per page | Sort | Filters |
| --- | --- | --- | --- | --- | --- |
| 2026-09-16T09:12:52.046465-0400 EDT | initial_collection | 1 | 50 | Sort by title (A-Z) | [] |

Gathered 50 distinct thumbnails in 0.065s with 0 scrolls; ended because of enough candidates.

## Comparison row

| Trial | Eastern start | Settings | Workflow | Start/limit | Opening target | Viewing target | Actual opening avg (range) | Duration | Attempts/ready/views | Stop | Report |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20260916T091249-0400-5c4b10b7 | 2026-09-16T09:12:51.178703-0400 EDT | unknown | tabs | 1/20 | 1.0 ± 0.1s | 5.0 ± 0.5s | 1.067s (0.972–1.174s) | 124.828 | 20/20/20 | workflow_complete | [report](20260916T091249-0400-5c4b10b7/summary.md) |

The report link is relative to a comparison table in the parent runs directory.

## Known unknowns and evidence limits

- network-filter vendor settings and connection details are user supplied; rule behavior and IP history are unverified.
- Browser request counts may differ from network-filter vendor counters, caches, service workers, or shared-IP traffic.
- Playwright tabs may behave differently from manually selected browser tabs.
- Readiness means the Studio title and main content are present; it does not prove every viewer file is loaded.
- Only configured BDR_HOSTS determine stopping on supporting requests; review other-host activity separately.
- Initial page responses were not observed for some items. Their HTTP status is unknown, and request counts may be incomplete.

## Central IT findings

Pending review. Record confirmed rule/action, public IP, Ray IDs, and user notes here.

These files are local diagnostics. Review their URLs, notes, and connection details before copying material for others.
