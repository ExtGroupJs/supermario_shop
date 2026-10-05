/**
 * Shared wrapper for the server-side (`ajax`) handlers of the DataTables views.
 *
 * Why this exists
 * ---------------
 * DataTables debounces its own search box with `DataTable.util.throttle`, which
 * is leading edge: the first keystroke fires a request immediately and whatever
 * is typed afterwards is batched into a second request `searchDelay` ms later.
 * Searching for "geely" therefore issued two requests (`search=g` and
 * `search=geely`), and the single character one is usually the slowest (an
 * `icontains` matches far more rows, so the count is bigger and more rows are
 * serialized), so it tended to land last and repaint the table with stale data.
 *
 * `serverSideAjax` wraps an ajax handler and guarantees that:
 *   - typing issues a single request, fired once the user stops typing
 *     (live search, no need to press Enter);
 *   - paging, sorting, form filters and `table.ajax.reload()` run immediately;
 *   - superseded handlers are dropped, so DataTables only draws the newest
 *     result.
 *
 * The DataTable must therefore disable DataTables' own search throttling with
 * `searchDelay: 0`, otherwise the table keeps drawing on its own schedule and
 * this debounce can never see the whole term (the leading edge draw for the
 * first character alone would already be dispatched).
 *
 * Handlers must still echo the draw counter, so DataTables can discard any
 * out-of-order response on its own:
 *
 *     callback({
 *       draw: data.draw,
 *       recordsTotal: res.data.count,
 *       recordsFiltered: res.data.count,
 *       data: res.data.results,
 *     });
 *
 * Usage
 * -----
 *     $("#tabla-de-Datos").DataTable({
 *       serverSide: true,
 *       searchDelay: 0, // the debounce below owns the live search
 *       ajax: serverSideAjax(function (data, callback) {
 *         axios.get(url, { params }).then((res) => {
 *           callback({ draw: data.draw, ... });
 *         });
 *       }),
 *     });
 */

/**
 * Wraps a DataTables server-side ajax handler with a live-search debounce.
 *
 * @param {function} handler Ajax handler with DataTables signature
 *                       `(data, callback, settings)`.
 * @param {object} [options] Optional settings.
 * @param {number} [options.searchDelay=400] Idle time in milliseconds without
 *                                          typing before the search is sent.
 * @returns {function} Handler to pass to the DataTable `ajax` option.
 */
function serverSideAjax(handler, options) {
  const searchDelay = (options && options.searchDelay) || 400;

  let timer = null;
  let waiting = null; // draw waiting for the debounce window to close
  let lastTerm = null; // search term of the last dispatched draw
  let lastDraw = 0; // draw counter of the last dispatched draw

  function cancelPending() {
    if (timer !== null) {
      clearTimeout(timer);
      timer = null;
    }
    waiting = null;
  }

  function dispatch(data, callback, settings) {
    handler.call(null, data, function (payload) {
      // A newer draw already started, so its response is the one that has to
      // be drawn: this answer is discarded without touching the table.
      if (data.draw !== lastDraw) {
        return;
      }
      callback(payload);
    }, settings);
  }

  function dispatchPending() {
    timer = null;
    const pending = waiting;
    waiting = null;
    lastTerm = pending.data.search.value;
    lastDraw = pending.data.draw;
    dispatch(pending.data, pending.callback, pending.settings);
  }

  return function (data, callback, settings) {
    const term = data.search.value;

    // First draw (page load) or same term as the last dispatched request:
    // paging, sorting, form filters or `ajax.reload()`. Always immediate.
    if (lastTerm === null || term === lastTerm) {
      cancelPending();
      lastTerm = term;
      lastDraw = data.draw;
      dispatch(data, callback, settings);
      return;
    }

    // New search term: restart the debounce window, discarding the term typed
    // in the previous one so only the last batch of keystrokes reaches the API.
    cancelPending();
    waiting = { data, callback, settings };
    timer = setTimeout(dispatchPending, searchDelay);
  };
}

if (typeof window !== "undefined") {
  window.serverSideAjax = serverSideAjax;
}