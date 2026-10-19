# Maven Central SDK — TASK-010

**Namespace:** `io.github.tonypost949` verified via Sonatype `https://central.sonatype.com/publishing/namespaces` (TASK-003 DONE)
**Artifact:** `osintneoai-sdk` 0.1.0 — thin client for `/api/tasks` `/api/scan` `/api/maps` + `public/syncfusion_grid.html`

**build.gradle.kts snippet (add to :sdk module):**
```kotlin
plugins { id("com.vanniktech.maven.publish") version "0.32.0" }
group = "io.github.tonypost949"
version = "0.1.0"
mavenPublishing { coordinates("io.github.tonypost949", "osintneoai-sdk", "0.1.0") }
```
**Publish:**
```
./gradlew :sdk:publish --no-daemon
# GPG: set ORG_GRADLE_PROJECT_signingInMemoryKey + signingInMemoryKeyPassword (from 1Password)
# Sonatype token from central.sonatype.com → `gradle.properties` `mavenCentralUsername/Password`
```

**Verify:** https://central.sonatype.com/artifact/io.github.tonypost949/osintneoai-sdk

*SDK wraps `cli/gcp_free_ai_demo.py` + `public/gods_eye_view_max_data.html` data loaders.*
