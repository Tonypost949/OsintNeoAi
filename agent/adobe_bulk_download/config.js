// config.js — Extension configuration constants (leaf module, no imports).

/**
 * Extension configuration. Same shape as v1.5.3 ABD.config minus localStoragePrefix
 * (replaced with storageKeyPrefix for chrome.storage.local key naming).
 */
export const config = {
  concurrentDownloads: 10,
  requestDelay: 1000,
  maxRetries: 3,
  max429Retries: 10,
  maxConversionRetries: 1,
  retryBaseDelay: 2000,
  maxAdaptiveDelay: 5000,
  requestTimeout: 60000,
  apiKey: 'CCHomeWeb1',
  photoshopApi: 'https://photoshop-api.adobe.io/v2',
  storageKeyPrefix: 'abd_progress_',
  maxPsdcPolls: 60,
  psdcPollInitialDelay: 2000,
  psdcPollDelay: 4000,
  maxPropagationAttempts: 3,
  largePropagationAttempts: 8,
  largePropagationThreshold: 50 * 1024 * 1024, // 50 MB
  propagationDelay: 2000,
  conversionRetryDelay: 5000,
  senseiApi: 'https://sensei-ue1.adobe.io/services/v2/predict',
  senseiStatusApi: 'https://senseicore-ue1.adobe.io/services/v2/status',
  senseiEngineId: 'Feature:sensei-demo:Service-efcddebf2b4141e9ae7252091c6a2398',
  maxAicPolls: 60,
  aicPollInitialDelay: 1000,
  aicPollDelay: 1000,
  keepaliveAlarmName: 'abd_keepalive',       // Alarm that fires periodically to prevent SW termination
  resumePollAlarmName: 'abd_resume_poll',
  maxScanDepth: 50,
  maxDataUrlBytes: 50 * 1024 * 1024,
  activeTaskKey: 'abd_activeTask',
  resumePromptTimeoutMs: 30000,   // ms — uses setTimeout (SW alive via keepalive during downloads)
  maxTokenLength: 8192,           // char limit for incoming tokens (Base64url-encoded JWT)
  maxPathLength: 250,             // max download filename length (chars) — Windows MAX_PATH safety
  blobUrlTimeoutMs: 60000,        // ms — safety timeout for revoking blob URLs if download state change never fires (legacy blob tier only)
  downloadPollIntervalMs: 5000,   // ms — downloads.search polling cadence in saveFileByUrl (stall detection + SW keepalive)
  downloadStallTimeoutMs: 45000,  // ms — no bytesReceived growth for this long = stalled download, cancel + retry
  downloadAbsoluteCapMs: 7200000, // ms — 2 h absolute cap on a single download before it's cancelled as a zombie
  truncationMaxRetries: 2,        // max retries for truncated downloads per file (separate from maxRetries)
  primaryRetryDelayMs: 2000,      // ms — backoff before the single Tier-1 retry in the converted-PSDC tier sequence
  tokenExpiryWarningMs: 5 * 60 * 1000,     // warn 5 min before expiry
  expiryCheckAlarmName: 'abd_token_expiry', // alarm name for periodic expiry checks
  resumePromptKey: 'abd_resume_prompt',           // session storage key for pending resume prompt
  resumeAnswerKey: 'abd_resume_answer',            // session storage key for user's resume answer
  resumePromptExtendedTimeoutMs: 60000,            // ms — timeout for persisted resume prompt poll
  resumePromptPollIntervalMs: 2000,                // ms — poll interval for checking resume answer
  conversionJobsKey: 'abd_conversion_jobs',              // session storage key for in-flight conversion job map
  conversionJobRecoveryPollMs: 30000,                   // max ms to spend re-polling a recovered jobId
  activeDownloadsKey: 'abd_active_downloads',           // session storage key for in-flight downloadId map (P2 reconciliation)
  directUrlDownload: true, // primary download path: direct URL via chrome.downloads (true) vs legacy blob (false)
  failedFilesKey: 'abd_failed_files',   // session storage key for persisted failed files list
  filesListKey: 'abd_files_list',
  scanContextKey: 'abd_scan_context',
  recoveryCountKey: 'abd_recovery_count',
  maxAutoRecoveries: 3,
  capabilitiesKey: 'abd_capabilities',
  downloadSubfolder: 'Adobe Downloads',  // user-specified subfolder name prepended to all download paths
  diagnosticLevel: 'INFO', // 'DEBUG' | 'INFO' | 'WARN' | 'ERROR' — minimum severity for ring buffer writes
  freeFileLimit: 50,
  analyticsOptOutKey: 'abd_analytics_optout',
  licenseStorageKey: 'abd_license_paid',
  emailStorageKey: 'abd_license_email',
  userIdStorageKey: 'abd_user_id',
  gaiaIdStorageKey: 'abd_gaia_id',
  freeFilesUsedKey: 'abd_free_files_used',
  licenseApiUrl: 'https://abd-license-api.the-pharmer.workers.dev',
  licenseVerifyAlarmName: 'abd_license_verify',
  licenseLastVerifiedKey: 'abd_license_verified_at',
  licenseVerifyTtlMs: 4 * 60 * 60 * 1000, // 4 hours
  licenseVerifyErrorTtlMs: 15 * 60 * 1000, // 15 minutes — shorter TTL for error/no-email paths
  stripeCheckoutUrl: 'https://buy.stripe.com/8x2aEX1j3bJl3oP2hkfnO00',
  feedbackFormUrl: 'https://docs.google.com/forms/d/e/1FAIpQLSfOVkPTLe-SR5ifm1oBr0H3l3ScXufCAezOnS4znAPtnxKOXA/viewform',
  feedbackFormFields: {
    version: 'entry.2076493216',
    chrome: 'entry.673208223',
    platform: 'entry.1500568127',
    license: 'entry.1506199560',
    errorContext: 'entry.877327354',
  },
  cwsReviewUrl: 'https://chromewebstore.google.com/detail/cojbhhjiinmondnmgpfkeehkfbbfmnpo/reviews',
  upgradePendingKey: 'abd_upgrade_pending',
  reviewDismissedKey: 'abd_review_dismissed',
  uninstallSurveyUrl: 'https://saltydalton.com/abd/uninstall',
  diagDbName: 'abd_diagnostics_db',
  diagStoreName: 'logs',
  diagMaxEntries: 200000,
  diagTtlMs: 7 * 24 * 60 * 60 * 1000, // 7 days
};
