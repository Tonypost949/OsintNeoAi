// api.js — HTTP layer with retry logic (ES module).
// Ported from adobe-bulk-download-v1.5.3.js lines 339-382, 484-660.

import { getToken } from './token.js';
import { events } from './events.js';
import { config } from './config.js';
import { state, waitForResume } from './state.js';

/** Simple async sleep. */
export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// --- Error helpers (v1.5.3 lines 339-382) ---

export function _classifyError(error, response, responseBody) {
  if (error) {
    if (error.name === 'AbortError') return 'network_timeout';
    if (error instanceof TypeError) return 'network_error';
    if (error.message?.includes('stopped')) return 'user_stopped';
    if (error.message?.includes('empty') && error.message?.includes('0 bytes')) return 'empty_response';
    if (error.message?.includes('smaller than expected')) return 'size_mismatch';
  }
  if (response) {
    const st = response.status;
    if (st === 429) return 'rate_limit';
    // Adobe asset APIs: 403 = token issue (origin-agnostic endpoints)
    if (st === 401 || st === 403) return 'auth_expired';
    if (st === 404) return 'not_found';
    if (st === 400) {
      if (responseBody?.includes('responsetoolarge')) return 'response_too_large';
      return 'bad_request';
    }
    if (st >= 500) return 'server_error';
  }
  return 'unknown';
}

// §10.2 fix: ReferenceError/SyntaxError are re-thrown directly in the catch block (line 107),
// so they never reach classification. No 'programming_error' category needed.
export const _nonRetryableCategories = new Set(['response_too_large', 'auth_expired']);

export async function _safeResponseBody(response) {
  try {
    const text = await response.text();
    return text.slice(0, 500);
  } catch {
    return null;
  }
}

export function _captureHeaders(response) {
  const names = [
    'Retry-After', 'X-RateLimit-Limit', 'X-RateLimit-Remaining',
    'X-RateLimit-Reset', 'X-Request-Id', 'x-amzn-RequestId', 'Content-Type',
  ];
  const result = {};
  let found = false;
  for (const name of names) {
    const val = response.headers.get(name);
    if (val != null) { result[name] = val; found = true; }
  }
  return found ? result : null;
}

// --- fetchWithRetry (v1.5.3 lines 484-660, with §10.2 + §10.5 fixes) ---

export async function fetchWithRetry(url, options = {}, retries = config.maxRetries) {
  let lastErrorDetails = null;
  for (let attempt = 0; attempt <= retries; attempt++) {
    let response;
    const attemptStart = Date.now();

    // Inner loop: absorb 429s without burning error retries
    for (let throttleCount = 0; ; throttleCount++) {
      if (state.paused) await waitForResume();
      if (state.stopped) throw new Error('Download stopped by user');

      // Validate token before making request
      const token = getToken();
      if (!token) {
        const err = new Error('AUTH_EXPIRED: No valid auth token available');
        err.stage = 'auth';
        err.details = { error_category: 'auth_expired', message: 'No valid auth token available' };
        throw err;
      }

      let timeout;
      try {
        const controller = new AbortController();
        timeout = setTimeout(() => controller.abort(), config.requestTimeout);
        const baseHeaders = {
          Authorization: 'Bearer ' + token,
          'X-Api-Key': config.apiKey,
          Accept: '*/*',
        };
        const fetchOpts = {
          method: options.method || 'GET',
          headers: { ...baseHeaders, ...(options.headers || {}) },
          signal: controller.signal,
        };
        if (options.body) fetchOpts.body = options.body;
        response = await fetch(url, fetchOpts);
        clearTimeout(timeout);
      } catch (e) {
        if (timeout) clearTimeout(timeout);

        // §10.2 fix: re-throw programming errors instead of masking them
        if (e instanceof ReferenceError || e instanceof SyntaxError) throw e;

        if (e.message?.includes('stopped')) throw e;

        if (e?.name === 'AbortError') {
          events.emit('network_timeout', {
            url,
            timeout_ms: config.requestTimeout,
            attempt: attempt + 1,
          });
        }

        lastErrorDetails = {
          error_category: _classifyError(e, null),
          url,
          duration_ms: Date.now() - attemptStart,
          http_status: null,
          response_body: null,
          response_headers: null,
        };
        response = null;
        break;
      }

      if (response.status === 401 || response.status === 403) {
        if (state.status !== 'error') {
          state.status = 'error';
          events.emit('status_change', { status: 'error' });
        }
        const body = await _safeResponseBody(response);
        const headers = _captureHeaders(response);
        events.emit('auth_expired', {
          url,
          http_status: response.status,
          duration_ms: Date.now() - attemptStart,
          response_body: body,
          response_headers: headers,
        });
        const err = new Error('AUTH_EXPIRED: Please refresh the page and re-run the tool');
        err.details = {
          error_category: 'auth_expired', url,
          duration_ms: Date.now() - attemptStart,
          http_status: response.status, response_body: body, response_headers: headers,
        };
        throw err;
      }

      if (response.status !== 429) break;

      if (throttleCount >= config.max429Retries) {
        const err = new Error('Rate limited ' + config.max429Retries + ' times consecutively: ' + url);
        err.details = { error_category: 'rate_limit', url, http_status: 429 };
        throw err;
      }

      // Bump adaptive delay globally
      state.lastThrottleTime = Date.now();
      const oldDelay = state.adaptiveDelay;
      state.adaptiveDelay = Math.min(
        state.adaptiveDelay * 2,
        config.maxAdaptiveDelay,
      );
      if (oldDelay !== state.adaptiveDelay) {
        events.emit('adaptive_delay_increase', {
          old_delay: oldDelay,
          new_delay: state.adaptiveDelay,
          trigger: 'rate_limit',
          throttle_count: throttleCount + 1,
        });
      }

      const raw = parseInt(response.headers.get('Retry-After') || '5', 10);
      const wait = Number.isFinite(raw) && raw > 0 ? Math.min(raw, 120) : 5;
      const jitter = wait * (1.0 + Math.random() * 0.3);
      events.emit('rate_limit', {
        url,
        throttle_count: throttleCount + 1,
        wait_seconds: +jitter.toFixed(1),
        response_headers: _captureHeaders(response),
        adaptive_delay: state.adaptiveDelay,
      });
      await sleep(jitter * 1000);

      // §10.5 fix: check stopped after sleeping for 429 backoff
      if (state.stopped) throw new Error('Download stopped by user');
    }

    // Got a non-429 response (or null from network error)
    if (response && response.ok) return response;

    // Capture error details for non-ok responses
    if (response) {
      const bodyText = await _safeResponseBody(response.clone());
      const headers = _captureHeaders(response);
      const category = _classifyError(null, response, bodyText);
      lastErrorDetails = {
        error_category: category,
        url,
        duration_ms: Date.now() - attemptStart,
        http_status: response.status,
        response_body: bodyText,
        response_headers: headers,
      };

      // Short-circuit: non-retryable errors skip remaining attempts
      if (_nonRetryableCategories.has(category)) {
        events.emit('non_retryable_error', {
          url,
          http_status: response.status,
          error_category: category,
          response_body: bodyText,
          response_headers: headers,
          duration_ms: Date.now() - attemptStart,
          skipped_retries: retries - attempt,
        });
        const err = new Error(`${category}: ${url}`);
        err.details = lastErrorDetails;
        err.nonRetryable = true;
        throw err;
      }
    }

    // Failure -- use outer retry budget
    if (attempt === retries) {
      const err = new Error('HTTP ' + (response?.status ?? 'network error') + ' after ' + (retries + 1) + ' attempts: ' + url);
      err.details = lastErrorDetails;
      throw err;
    }
    const delay = config.retryBaseDelay * Math.pow(2, attempt);
    events.emit('http_retry', {
      url,
      http_status: response?.status || null,
      attempt: attempt + 1,
      max_retries: retries,
      delay_seconds: delay / 1000,
      response_body: lastErrorDetails.response_body,
      response_headers: lastErrorDetails.response_headers,
      duration_ms: lastErrorDetails.duration_ms,
      error_category: lastErrorDetails.error_category,
    });
    await sleep(delay);

    // §10.5 fix: check stopped after sleeping for retry backoff
    if (state.stopped) throw new Error('Download stopped by user');
  }
}
