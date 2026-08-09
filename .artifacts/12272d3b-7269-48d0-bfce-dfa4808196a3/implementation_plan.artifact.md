# Bug Fix: Browser Hijacking & Backend Stability

The app currently experiences severe stability issues, including automatic browser redirects to inappropriate content and unhandled 502 backend errors. This plan outlines the steps to resolve these issues by improving error handling in the networking layer and ensuring no automatic redirects occur on failure.

## User Review Required

> [!IMPORTANT]
> The `BASE_URL` is currently set to a Cloudflare tunnel (`https://silver-cir-solved-identify.trycloudflare.com/`). If this tunnel is compromised or returning inappropriate content, it must be updated. However, I will first focus on ensuring the app does not automatically redirect to a browser on 502 errors.

## Proposed Changes

### Networking Layer

#### [MODIFY] [NetworkModule.kt](file:///C:/repos/connect/app/src/main/java/com/example/connect/data/remote/NetworkModule.kt)
- Add `.followRedirects(false)` to `OkHttpClient` to prevent any automatic redirects at the networking level.
- Add an interceptor to handle 502 errors explicitly.

### ViewModel Error Handling

#### [MODIFY] [DashboardViewModel.kt](file:///C:/repos/connect/app/src/main/java/com/example/connect/ui/screens/DashboardViewModel.kt)
- Update `fetchData` to report errors even if the state was previously successful.
- Ensure 502 errors are caught and shown as user-friendly messages.

#### [MODIFY] [DashboardDetailViewModel.kt](file:///C:/repos/connect/app/src/main/java/com/example/connect/ui/screens/DashboardDetailViewModel.kt)
- Fix the polling loop to stop and report errors on network failure.

## Verification Plan

### Automated Tests
- Run `./gradlew :app:assembleDebug` to ensure the project builds.

### Manual Verification
- Verify that 502 errors result in an error message in the UI instead of a browser redirect.
