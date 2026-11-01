# Execution orchestration

Scientific generation and evaluation implementations were sealed before paid generations. Later scheduling, audit and assembly helpers do not alter those implementations or source data.

The two-task access pilot generated H02 and K01 once per snapshot. The remaining GPT-4.1 requests ran sequentially. The remaining GPT-5 work ran as distinct single-task subprocesses, with three concurrent requests. The initial sequential GPT-5 client was paused while its A09 response buffered; after resumption it saved that response and stopped at the sealed partial-attempt guard for A14, whose disjoint worker was already active. No second A14 provider call was made. The 60 distinct task/model keys, provider response IDs and request-cost entries are the call-level evidence.

An earlier sandbox restriction blocked 28 local GPT-5 loopback invocations before provider dispatch. Those local records are archived separately, and identical sealed requests resumed with the required network permission. See `transport-amendment.json`; these are not failed model generations and consume no provider tokens.

A separate scheduler waited for complete retained submissions and launched at most two scientific evaluation cases at once. Each case invoked the frozen runner with the pinned scientific interpreter and dependency paths, with numerical library threads fixed to one. Scheduler subprocess timeouts were 3,900 seconds; the runner independently enforced its original 180-second procedure and 1,800-second scoring limits. Saved-output auditing never reran prediction procedures or requested new generations. Successful codecs had separate-process reconstruction checks before receiving a numeric result.

`scripts/audit_generation_extension.py` audits newly completed successful outputs and retains earlier audit identities, rather than repeating previous audits. `scripts/assemble_generation_extension.py` requires all 60 provider attempts, all 74 slice outcomes, successful saved-output audits, unchanged output/submission hashes and spending within $15 before producing the consolidated result. It creates the decentralized task pages without modifying the original experiment folders.

After the final API response, the memory-only access bridge was stopped. See `access-closed.json`. No key was written to disk or added to repository/website assets. The initially pasted, unused key was revoked before its replacement was used.
