# github development approach

## Approach

- Give each issue one clear outcome. Include the goal, relevant public context, constraints, and what would count as completion. Say whether the requested output is advice, a plan, or code. The immediate/near/eventual distinction in this issue is particularly useful.
- Use comments for the back-and-forth. Ask Codex to read the issue and its current comments, then post a response. Add corrections and follow-up prompts here and explicitly ask Codex to read them when continuing locally.
- Record the accepted decision. After discussion, add a short decision comment and link it from a “Current decision” note in the issue body. Preserve earlier comments so readers can follow why the approach changed. Clearly distinguish a Codex proposal from a maintainer’s decision.
- Create a separate issue when the next substantial task is ready. Once the GitHub approach is chosen, a follow-up issue can request the application design/development plan. Later, break the accepted plan into smaller implementation issues. Link related issues; GitHub also supports parent issues and sub-issues. 
- Generally, use a linked pull request for file changes (though during this setup phase it's ok to update the `main` branch). Describe the problem, resulting behavior, and verification there. Close the relevant issue when its stated outcome is complete.


## Suggested issue structure

```
## Goal

## Public context

## In scope

<!-- (Try this for a while; delete if it doesn't work for me.) -->

## Out of scope

<!-- (Try this for a while; delete if it doesn't work for me.) -->

## Requested output
<!-- Advice, decision proposal, documentation, or implementation -->

## Completion criteria

## Current decision
<!-- Added or updated by the maintainer after discussion -->
```

## Issue decisions structure

**Maintainer decision**

- Decision:
- Rationale:
- Follow-up issue:
- Supersedes:

## Suggested issue labels

type:discussion
type:planning
type:implementation
status:needs-decision
status:ready
status:blocked


## Issue-comment prompt suggestion

- Read <issue url>, all its comments, and all applicable repository AGENTS.md files. 
- Address the latest maintainer request within its stated scope, resolving older comments in favor of newer maintainer guidance. 
- Post a comment beginning with "Codex response". 
- State whether the response is an answer, advice, a proposal, an implementation report, etc. 
- Use only information suitable for this public repository. 
- Do not modify files, create commits, or begin implementation unless explicitly requested.
- Do not publish secrets, private endpoints, full local paths, cookies, session data, or unreviewed browser artifacts.

---
