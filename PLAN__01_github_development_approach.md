# github development approach

## Approach

- Give each issue one clear outcome. Include the goal, relevant public context, constraints, and what would count as completion. Say whether the requested output is advice, a plan, or code. The immediate/near/eventual distinction in this issue is particularly useful.
- Use comments for the back-and-forth. Ask Codex to read the issue and its current comments, then post a response. Add corrections and follow-up prompts here and explicitly ask Codex to read them when continuing locally.
- Record the accepted decision. After discussion, add a short decision comment and link it from a “Current decision” note in the issue body. Preserve earlier comments so readers can follow why the approach changed. Clearly distinguish a Codex proposal from a maintainer’s decision.
- Create a separate issue when the next substantial task is ready. Once the GitHub approach is chosen, a follow-up issue can request the application design/development plan. Later, break the accepted plan into smaller implementation issues. Link related issues; GitHub also supports parent issues and sub-issues. About GitHub issues.
- Generally, use a linked pull request for file changes (though during this setup phase it's ok to update the `main` branch). Describe the problem, resulting behavior, and verification there. Close the relevant issue when its stated outcome is complete.


## Issue-comment prompt suggestion

Read issue, all its comments, and any applicable repository AGENTS.md. Address the latest maintainer request within its stated scope. Post your response as a comment on that issue, identifying it as a Codex response. Use only information suitable for this public repository. Do not begin implementation/coding unless the request explicitly includes it.

---
