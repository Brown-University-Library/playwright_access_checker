# AGENTS.md — Repository Agent Instructions (Source of Truth)

This file defines the canonical coding directives for this repository.

If other instruction files exist (Copilot, IDE rules, contributor docs) and conflict with this file, follow this file and treat the others as stale.


## Table of contents

- [Project basics](#project-basics)
- [How to run code](#how-to-run-code)
- [Coding directives (Python)](#coding-directives-python)
- [Tests](#tests)
- [Change workflow expectations](#change-workflow-expectations)
- [GitHub issue comments](#github-issue-comments)
- [Privacy and publication](#privacy-and-publication)
- [If instructions are missing or ambiguous](#if-instructions-are-missing-or-ambiguous)
- [Agent project index](#agent-project-index)


## Project basics

- Repository: `playwright_access_checker`
- Current state: a Playwright CLI runs one Studio browsing trial using either the `tabs` or `return` workflow and saves local evidence.
- Primary language: Python
- Target runtime: Python 3.12 -- unless a `pyproject.toml` specifies a different version
- Dependency / execution tool: `uv`
- Project-root is the directory containing this file (and `.git/`, and `.gitignore`).


## How to run code

- Assume user is in the project-root directory.
- Do not use `python` to run scripts.
- Preview settings via: `uv run ./main.py bdr:nz9qn2kb --workflow tabs --preview`
- Configure `../.env` as described in `README.md`, then run one trial via: `uv run ./main.py bdr:nz9qn2kb --workflow tabs`
- Run tests via:
    - `uv run ./run_tests.py`
        - Note that `run_tests.py` has usage instructions about how to run more granular tests.


## Coding directives (Python)

### Type hints and imports

- Use Python 3.12 type hints everywhere (functions and important variables). (Unless a `pyproject.toml` specifies a different version.)
- Prefer builtin generics (e.g., `list[str]`, `dict[str, int]`) over `typing.List` / `typing.Dict`.
- Prefer PEP 604 unions (e.g., `str | None`) over `Optional[str]`.
- Avoid `typing` and `annotations` imports unless strictly necessary.

### Script structure

- Structure runnable modules as:
  - `def main() -> None: ...`
  - `if __name__ == '__main__': main()`
- Keep `main()` simple: parse args / orchestrate calls only.
- Put real logic into top-level helper functions and modules (no nested function definitions).
- Rarely use more than three levels of hierarchy: main() can call helper_A() which can call helper(B) which can, if necessary, can call helper(C) -- but that's it.

### Functions and control flow

- Prefer single-return functions (use local variables and a final return).
- Do not define functions inside other functions.
- Favor clarity and explicitness over cleverness.

### Logging

- When adding a log statement, when possible, format variable values as a label, followed by a comma and a space, with the value enclosed in double backticks.
- Prefer a label that matches the variable name. For example: ```log.debug(f'branch_and_commit, ``{branch_and_commit}``')```

### HTTP and networking

- Use `httpx2` for all HTTP calls.
- Do not introduce alternate HTTP libraries (e.g., `requests`, `aiohttp`) unless the repository already depends on them and there is a documented reason.

### Docstrings

- Use triple-quoted docstrings.
- Write docstrings in present tense, with triple-quotes on their own lines.
  - Good: 
    ```
    """
    Parses ...
    """
    ```
  - Avoid: `"""Parse ..."""`
- The last line of non-test function-docstrings should be: `Called by: the_caller_function()` (or, if in another class/module, `Called by: module.Class.the_caller_function()`)
- Start test-function docstring-text with "Checks..."
- For header-comments, in functions, start the comment with two hashes (e.g., `## does this`).

### Additional coding directives

- inspect the `ruff.toml` for additional coding directives, such as `max-line-length` and `quote-style`.

### Markdown formatting

- Do not use hard line-breaks in markdown files; let paragraphs wrap naturally.
- When creating a Markdown file with more than three top-level `##` headings, add a table of contents near the top with links to those `##` headings.


## Tests

- Use the standard library `unittest` framework (not pytest).
- New behavior should usually come with a focused test covering:
  - the happy path
  - at least one failure / edge case


## Change workflow expectations

When implementing a change (especially from an issue/task):

1. Read relevant surrounding code and match existing conventions.
2. Make the smallest correct change that satisfies the request.
3. Update tests and run: `uv run ./run_tests.py`
4. If you cannot run tests in your environment, still write/adjust tests and state what you would run.

### GitHub attribution

- Every GitHub post or text update must visibly identify Codex as the agent that created or edited it. This includes issue descriptions, pull-request descriptions, comments, reviews, and discussions; do not rely on the displayed account name to convey authorship.
- Begin new issue descriptions with `Created by Codex at the user's request.` Keep this attribution separate from the user's prompt. For other posts or edits, use an accurate visible attribution such as `Posted by Codex` or `Edited by Codex`; retain the required `Codex response` prefix for comments.
- Distinguish who posted the material from who wrote it: identify quoted or reproduced prompts as the user's words, and identify Codex's summaries, proposals, and reports as Codex's work. Do not imply that the user wrote agent-generated text.

### Issue bodies and exact prompts

When the user provides a prompt, including a Goal/Context/Tasks prompt, and asks to post it as an issue, use the complete, exact prompt as the issue description after the separate Codex attribution line. Preserve the wording, spelling, punctuation, Markdown, links, paragraph breaks, and order. Do not summarize, interpret, correct, reorganize, omit parts, or add completion criteria to that prompt. A prompt comment does not substitute for putting the exact prompt in the issue body. Put any authorized Codex interpretation or work report in a separately attributed comment.

The only exception to verbatim reproduction is required privacy redaction under [Privacy and publication](#privacy-and-publication): mark each omission explicitly and explain outside the prompt that redactions were necessary. Otherwise, leave the prompt unchanged.

Use a structured body argument when available, or a temporary file with `--body-file` when using `gh`. After posting, fetch the issue and compare the prompt portion of its body against the original prompt, allowing only explicitly marked privacy redactions; also verify the visible Codex attribution and return the issue link.

When the user asks Codex to draft an issue rather than reproduce a supplied prompt, prefer the following simple structure. This drafting guidance must not override the exact-prompt rule.

- **Goal:** State the intended outcome.
- **Context:** Include relevant background, links, constraints, and current behavior. Use only public information in GitHub issues.
- **Tasks:** List the requested actions and make clear whether the user wants advice, a plan, documentation, or implementation.
- **Completion criteria (optional):** Add observable results or checks when they help clarify what counts as done; omit this section when the goal and tasks already make that clear.

Keep the structure proportional to the work. Issues, formal templates, labels, preliminary discussions, and decision comments are not prerequisites for authorized local work.

### Issue-based development

- Use issues to organize pieces of work with one clear outcome, and create a branch for each issue's file changes. Include the issue number and a short description in the branch name, and record it in work reports.
- Work directly from the current user request. If work starts locally, create the issue and associated branch when practical; do not wait for preliminary discussion or decision comments before doing authorized work.
- When authorized, use issue comments to preserve the initial prompt, substantive follow-up prompts, and a narrative of Codex's responses and work at useful milestones. Every local exchange does not need a GitHub update.
- Save requested plans, documentation, and code changes locally on the issue branch, leaving them uncommitted for the user's review unless the user explicitly requests a commit. Report the files changed, checks performed, and anything needing review; link existing commits and pull requests when relevant.
- Keep the issue open for review and iteration. The user may ask questions, explain manual changes, request revisions, or request more information in comments. A finished draft or implementation report does not mean the user has accepted the work or wants the issue closed.
- See [the development approach plan](PLAN__01_github_development_approach.md) for the lightweight pattern being tried. Keep it consistent with this file.

### Commit authorization

- Create or amend a commit only when the user explicitly asks Codex to commit the changes in question. This applies to Git commands and equivalent tools or APIs. A request to develop a plan, implement a change, save files, create a branch, post a summary, or finish the work does not authorize a commit.
- Review approval, a suggested commit message, or the user saying they might commit the work is not an instruction for Codex to commit. Commit-message conventions below describe how to write an authorized commit; they do not grant permission to make one.
- Apply an explicit commit instruction only to its stated changes and scope. Permission for an earlier task or commit does not automatically cover later revisions. Do not ask again when the current changes are already covered by clear authorization.
- If commit authorization is absent or unclear, finish the authorized local work and report that it is ready for review and uncommitted. Do not delay that work to ask whether to commit.
- Permission to commit does not by itself authorize pushing, creating or merging a pull request, or closing an issue. Follow the user's instructions for each action separately.

### Issue closure and review

- Only the user closes issues unless the user specifically asks Codex to close an identified issue. Keep issues open by default, even after requested work, tests, review, commits, pushes, or merges are complete. A request to finish the task or approval of a plan is not permission to close the issue.
- Without that specific request, do not close issues through the GitHub UI, CLI, API, tools, or a comment-and-close action. Do not arrange automatic closure through commit messages, pull-request descriptions, Development links, or automation.
- Unless issue closure is explicitly authorized, use ordinary references such as `Refs #6` or an issue URL. Do not use closing keywords such as `Closes`, `Fixes`, or `Resolves` with an issue reference in commit messages or pull-request descriptions, or add links that close the issue when merged. Before an authorized merge, check for existing automatic closure instructions and links; do not merge if it would close an issue without the user's specific authorization. See [GitHub's issue-linking documentation](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue).
- For planning work, the default sequence is: develop and save the plan locally; post a summary if authorized; leave the changes uncommitted and the issue open for the user's review. Continue revisions and discussion as requested, preserving the user's manual edits. The user decides whether and when to commit, continue iterating, and eventually close the issue; these are separate decisions.

### Commit messages

- Apply these conventions only after the user has authorized a commit under [Commit authorization](#commit-authorization).
- Group related files into logical, focused commits; do not require a separate commit for every file.
- Keep each commit message brief, with no more than ten words.
- Write messages in the present tense so they complete the phrase "This commit..." Begin with a fitting verb such as "Adds," "Implements," or "Updates."


## GitHub issue comments

- Work directly from the current user request. Use issues and comments to organize and document work without requiring an issue, preliminary discussion, or decision comment before doing authorized local work.
- Post a GitHub comment only when the user asks or has already authorized it. Authorization to maintain prompt and work records for an issue can cover later updates within that scope. A request to implement a change does not by itself request a comment, and a request to comment does not by itself request implementation, commits, or other repository changes.
- Before posting, read the target issue, all its comments, and applicable `AGENTS.md` files. Address the current user request within its stated scope; use newer maintainer guidance to resolve older conflicting comments.
- Begin comments with `Codex response` and identify the response type, such as **answer**, **advice**, **proposal**, **prompt record**, or **implementation report**. Clearly distinguish an agent proposal from an accepted maintainer decision.
- Apply [GitHub attribution](#github-attribution) to all GitHub posts and text updates, not only comments. For issue creation from a user prompt, follow [Issue bodies and exact prompts](#issue-bodies-and-exact-prompts).
- When asked to add a prompt as a comment, preserve the user's wording in a Markdown blockquote under `Codex response — **prompt record**`. Identify it as a prompt from the local work session. Keep any explanation outside the quotation; do not replace the prompt with an implementation summary.
- For implementation reports, describe what changed, what was verified, any remaining work or review, and whether changes are local, committed, or pushed. Distinguish work ready for review from work accepted by the user, and state that the issue remains open for review when applicable. Posting a report does not authorize a commit or issue closure. Report only actions and checks actually completed.
- Follow [Privacy and publication](#privacy-and-publication), including when quoting prompts. Use relative paths or variable names; if a quoted prompt needs redaction, mark the omission explicitly.
- Use a structured comment-body argument when available. If using `gh`, put multiline Markdown in a temporary file and pass it with `--body-file` so newlines, backticks, and other literal text are preserved.
- Verify that the posted comment contains the intended text and return its direct link. If a posting attempt has an uncertain result, check the issue comments before retrying to avoid duplicates.


## Privacy and publication

- This repository is public, so reviewing material before publishing is especially important. The same privacy values and restrictions apply to private repositories.
- Do not publish secrets, credentials, private endpoints, full local or server filesystem paths, cookies, session data, or unreviewed browser artifacts. Apply this to repository files, documentation, examples, agent notes, issues, comments, and pull requests.
- Use relative paths or variable names instead of full filesystem paths. Review quoted prompts, logs, screenshots, and attachments before posting; redact sensitive content and mark omissions explicitly, including within prompt quotations.
- Keep full server filesystem paths out of documentation, examples, and agent notes. Keep all server-deployment documentation, including any mention of deployment caller scripts, outside READMEs.
- Keep the privacy reminders in `PLAN__01_github_development_approach.md` consistent with this section.


## If instructions are missing or ambiguous

- Do not ask questions unless absolutely necessary to proceed.
- Make reasonable assumptions, state them explicitly, then implement.
- Do not assume permission to commit or close an issue. When that permission is absent or unclear, complete the authorized local work, leave it uncommitted, and keep the issue open as described above.
- If blocked, provide:
  - what you tried
  - what you found in the repo
  - a concrete next step (command, file to edit, or minimal decision needed)


## Agent project index

- Source template: [script_project](https://github.com/birkin/birkin_coding_tools/tree/main/script_project/); incorporation is tracked in [issue #2](https://github.com/birkin/playwright_access_checker/issues/2).
- `main.py`: CLI for one trial, offline settings preview, or rebuilding a report from saved events.
- `lib/config.py`: validates settings in CLI/environment/`../.env`/default order; omits proxy credentials from saved settings. Resolves paths from the repository root above `lib/`.
- `lib/browser_flow.py`: shared thumbnail selection, actual link clicks, both workflows, timed viewing and scrolling, and result-saving on interruption.
- `lib/observation.py`: context-wide request recording, late tab attribution, content checks, and the shared stopping condition.
- `lib/measurement.py`: repeatable timings, URL redaction, response classification, and monotonic request-count periods.
- `lib/results.py`: flushed JSONL events, JSON checkpoints, readable reports, and offline report rebuilding under `../runs/` by default.
- `.env.example`: placeholder settings for the outer `../.env`; do not overwrite existing local settings.
- `tests/`: `unittest` coverage of settings and measurements plus a loopback-only website exercising both workflows with Chromium. Automated tests do not contact BDR. Browser tests require `uv run playwright install chromium` and permission to bind a local port.
- `run_tests.py`: runs all tests by default; accepts a dotted module, class, or method name and `-v` for verbose output. Run it from the repository root.
- `pyproject.toml`: repository metadata, Python 3.12 requirement, and application dependencies (`playwright`, `python-dotenv`); the `local`, `staging`, and `prod` groups are empty. The app makes no separate HTTP-client calls.
- `uv.lock`: resolved dependencies for this repository. Regenerate with `uv lock` when dependency declarations change.
- `ruff.toml`: Python 3.12 target, 125-character lines, four-space indentation, and single quotes.
- `README.md`: local installation, current usage, and dependency inventory.
- `PLAN__01_github_development_approach.md`: lightweight development pattern being tried: issues organize work, branches contain associated changes, and authorized comments preserve prompts and work reports. Changes stay local and uncommitted for review unless the user explicitly requests a commit; issues stay open unless the user specifically asks Codex to close them. It is consistent with this file and does not require preliminary discussion before authorized local work.
- The enclosing `playwright_access_checker_stuff/` directory is outside the Git repository.
- `PLAN__02_application_design.md`: design reference for the CLI implemented under issue #9. Cloudflare comparisons require recorded conditions; connection management remains separate.
- Follow [Privacy and publication](#privacy-and-publication) when maintaining this index.

---
