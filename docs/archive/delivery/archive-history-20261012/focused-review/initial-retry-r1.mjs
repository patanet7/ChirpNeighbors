// src/lib/client/page-navigation.ts
function createPageNavigation(initial, load, changed) {
  let state = {
    value: initial,
    loading: false,
    error: "",
    index: 0,
    historyStart: 0
  };
  let history = initial?.page ? [{ cursor: initial.page.cursor, limit: initial.page.limit }] : [{}];
  let epoch = 0, alive = true;
  let controller;
  let retry;
  const publish = () => changed({ ...state });
  async function go(request, index, preceding) {
    if (!alive) return;
    const current = ++epoch;
    controller?.abort();
    const active = new AbortController();
    controller = active;
    state = { ...state, loading: true, error: "" };
    retry = () => go(request, index, preceding);
    publish();
    try {
      const value = await load(request, active.signal);
      if (!alive || current !== epoch || active.signal.aborted) return;
      if (!value.page) throw new Error("Page information is unavailable. Refresh the list.");
      history = [...preceding.slice(-63), { cursor: value.page.cursor, limit: value.page.limit }];
      state = { value, loading: false, error: "", index, historyStart: index - history.length + 1 };
      retry = void 0;
      publish();
    } catch (cause) {
      if (!alive || current !== epoch || active.signal.aborted) return;
      state = {
        ...state,
        loading: false,
        error: cause instanceof Error ? cause.message : "The page could not be loaded. Retry or refresh the list."
      };
      publish();
    }
  }
  return {
    next: () => {
      const page = state.value?.page;
      return page?.nextCursor ? go(
        { cursor: page.nextCursor, limit: page.limit },
        state.index + 1,
        history.slice(0, state.index - state.historyStart + 1)
      ) : Promise.resolve();
    },
    previous: () => state.index > state.historyStart ? go(
      history[state.index - state.historyStart - 1] ?? {},
      state.index - 1,
      history.slice(0, state.index - state.historyStart - 1)
    ) : Promise.resolve(),
    refresh: () => go({}, 0, []),
    current: () => go(
      history[state.index - state.historyStart] ?? {},
      state.index,
      history.slice(0, state.index - state.historyStart)
    ),
    retry: () => retry?.() ?? Promise.resolve(),
    invalidate: () => {
      epoch++;
      controller?.abort();
      state = { ...state, loading: false };
      publish();
    },
    destroy: () => {
      alive = false;
      epoch++;
      controller?.abort();
    }
  };
}

// <stdin>
var calls = 0;
var nav = createPageNavigation({ jobs: [] }, async () => {
  calls++;
  return { jobs: [], page: { cursor: "a.b", nextCursor: null, limit: 5 } };
}, () => {
});
await nav.retry();
console.log(JSON.stringify({ initialRetryRequests: calls }));
await nav.refresh();
console.log(JSON.stringify({ afterRestartRequests: calls }));
