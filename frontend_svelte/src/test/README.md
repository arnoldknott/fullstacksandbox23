# Frontend unit tests

## Reveal.js timer cleanup

[`RevealJS.test.ts`](../components/RevealJS.test.ts) exercises the real Reveal.js
implementation with Vitest fake timers. Use `vi.waitFor` to advance timers while
awaiting readiness and throttled slide-address updates.

Teardown unmounts components and runs pending callbacks while the browser test
environment is still available, then clears recurring timers before restoring
real timers. Reveal.js deck destruction does not cancel its bundled text fitter's
delayed window resize callbacks or its scroll-prevention interval.
