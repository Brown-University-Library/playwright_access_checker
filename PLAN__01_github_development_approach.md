# GitHub development approach

The earlier GitHub-first method felt too slow. This plan describes a lighter development pattern to try: use issues to organize pieces of work, branches for the associated changes, and issue comments to preserve prompts and a readable history of Codex's responses and work.

[AGENTS.md](AGENTS.md) remains the canonical source of repository instructions. Keep this plan consistent with its change-workflow, issue-comment, and privacy guidance.

## Working pattern

1. Create an issue for a piece of work with one clear outcome. When the user supplies a prompt and asks to post it as an issue, reproduce that exact prompt in the issue description after a separate Codex attribution line, as described below. When asked to draft an issue instead, use a short **Goal**, **Context**, and **Tasks** structure; add completion criteria only when useful and say whether the requested output is advice, a plan, documentation, or implementation.
2. Create a branch for changes associated with that issue. Include the issue number and a short description in the branch name, such as `issue-3-update-github-development-approach`, and record the branch in the issue when reporting work.
3. Work directly from the current user request. Issues organize the work, but creating an issue, posting the prompt, preliminary discussion, labels, and formal decision comments are not prerequisites for authorized local work. If work starts locally, create the issue and associated branch when practical.
4. Use issue comments to record the user's prompts and a narrative of Codex's responses and work. Record the initial prompt, substantive follow-up prompts, and work reports at useful milestones; avoid making every local exchange wait on a GitHub update.
5. Link relevant commits and pull requests as they become available. Report what is complete and what remains, including whether changes are local, committed, or pushed. Close the issue when its intended outcome is complete.

Keep the process proportional to the task. Separate substantial new work into another issue and link related issues when helpful. Decisions can be recorded in ordinary comments; no separate decision template or preliminary discussion phase is required.

### Attribution on every GitHub post

Every GitHub post or text update must visibly identify Codex as the agent that created or edited it, including issue descriptions, pull-request descriptions, comments, reviews, and discussions. Do not rely on the displayed account name to convey authorship. Begin new issue descriptions with `Created by Codex at the user's request.` For other posts or edits, use an accurate visible attribution such as `Posted by Codex` or `Edited by Codex`; comments retain the `Codex response` prefix.

Keep attribution separate from the user's prompt. Distinguish who posted the material from who wrote it: reproduced prompts are the user's words; summaries, proposals, and work reports written by Codex must be identified as Codex's work. Follow [AGENTS.md's GitHub attribution guidance](AGENTS.md#github-attribution).

### Exact prompts in issue descriptions

When the user supplies a prompt, including a Goal/Context/Tasks prompt, and asks to post it as an issue, put the complete, exact prompt in the issue description after the separate Codex attribution line. Preserve wording, spelling, punctuation, Markdown, links, paragraph breaks, and order. Do not summarize, interpret, correct, reorganize, omit parts, or add completion criteria to the prompt. Recording the exact prompt in a comment does not substitute for using it in the issue body. Put any authorized Codex interpretation or work report in a separately attributed comment.

The only exception is required privacy redaction: mark each omission explicitly and explain outside the prompt that redactions were necessary. Otherwise, leave the prompt unchanged. The suggested Goal/Context/Tasks structure applies when Codex is asked to draft an issue; it must not override the exact-prompt rule.

Use a structured body argument when available, or a temporary file with `--body-file` when using `gh`. After posting, fetch the issue and compare the prompt portion of its body against the original prompt, allowing only explicitly marked privacy redactions; also verify the visible Codex attribution and return the issue link. Follow [AGENTS.md's issue-body guidance](AGENTS.md#issue-bodies-and-exact-prompts).

## Issue comments

Follow [AGENTS.md's GitHub issue comments guidance](AGENTS.md#github-issue-comments). Post comments when the user asks or has already authorized them. Authorization to maintain prompt and work records for an issue can cover later updates within that scope; implementing a change alone does not authorize posting comments, and commenting alone does not authorize implementation or commits.

Before posting, read the target issue, all its comments, and applicable `AGENTS.md` files. Follow the current request and use newer maintainer guidance to resolve older conflicting comments.

- Begin each comment with `Codex response` and identify its type, such as **prompt record**, **answer**, **advice**, **proposal**, or **implementation report**. Distinguish proposals from accepted maintainer decisions.
- For a prompt record, use `Codex response — **prompt record**`, identify the prompt as coming from the local work session, and preserve the user's wording in a Markdown blockquote. Keep explanations outside the quotation and explicitly mark any redactions.
- For a work report, use `Codex response — **implementation report**` and provide a concise narrative of what changed and why, what was actually verified, any remaining work, and whether changes are local, committed, or pushed. Include the branch name and relevant links when available.
- Use a structured comment-body argument when available. If using `gh`, write multiline Markdown to a temporary file and pass it with `--body-file` to preserve literal text. Verify the posted text and return its direct link; check for an existing comment before retrying an uncertain posting attempt.

## Privacy and publication

This repository is public, so reviewing material before publishing is especially important. The same privacy values and restrictions apply to private repositories.

- Do not publish secrets, credentials, private endpoints, full local or server filesystem paths, cookies, session data, or unreviewed browser artifacts. Apply this to repository files, documentation, examples, agent notes, issues, comments, and pull requests.
- Use relative paths or variable names instead of full filesystem paths. Review quoted prompts, logs, screenshots, and attachments before posting; redact sensitive content and mark omissions explicitly, including within prompt quotations.
- Keep full server filesystem paths out of documentation, examples, and agent notes. Keep all server-deployment documentation, including any mention of deployment caller scripts, outside READMEs.

These reminders match [AGENTS.md](AGENTS.md#privacy-and-publication). Update both files when this guidance changes.
