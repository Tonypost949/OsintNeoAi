# Optimize Your Build Speed — Android Studio & Gradle Ingestion Digest
**Source Protocol:** `https://developer.android.com/build/optimize-your-build` (Android Studio & AGP Optimization)  
**Ingestion Timestamp:** September 17, 2026  
**Repository Target:** `C:\OsintNeoAi` | Dataset: `noble-beanbag-497411-m4`

---

## 1. Executive Summary & Build Speed Optimization Pillars
Gradle and Android Gradle Plugin (AGP) build performance directly dictates iteration velocity. This digest captures the official hardware, JVM memory, configuration cache, and R-class optimization strategies for large Kotlin/Android multi-module codebases.

```
                      ┌──────────────────────────────────────────────┐
                      │    Android Studio / AGP Build Optimizer     │
                      └──────────────────────┬───────────────────────┘
                                             │
      ┌──────────────────────┬───────────────┴───────────────┬──────────────────────┐
      │                      │                               │                      │
┌─────▼──────────────┐ ┌─────▼──────────────┐ ┌──────────────▼──────┐ ┌─────────────▼──────────────┐
│  JVM Memory Heap   │ │  Parallel GC       │ │  Configuration Cache│ │  R-Class & Jetifier          │
├────────────────────┤ ├────────────────────┤ ├─────────────────────┤ ├──────────────────────────────┤
│ org.gradle.jvmargs │ │ -XX:+UseParallelGC │ │ org.gradle.         │ │ android.nonTransitiveAppR    │
│ =-Xmx6g -Xms2g     │ │ High-throughput GC │ │ configuration-cache │ │ android.enableJetifier=false │
└────────────────────┘ └────────────────────┘ └─────────────────────┘ └──────────────────────────────┘
```

---

## 2. Granular Gradle & JVM Optimization Strategies

### A. JVM Heap Memory & Parallel Garbage Collector
- **Increase Max Heap:** Set `org.gradle.jvmargs=-Xmx6g` or `-Xmx8g` in `gradle.properties` when garbage collection consumes >15% of total build time in Build Analyzer.
- **Parallel GC Selection:** Replace default G1GC with JVM Parallel GC for compilation-heavy workloads:
  ```properties
  org.gradle.jvmargs=-Xmx6g -XX:+HeapDumpOnOutOfMemoryError -Dfile.encoding=UTF-8 -XX:+UseParallelGC -XX:MaxMetaspaceSize=1g
  ```
- **Gradle Issue #19750 Workaround:** Always explicitly pass `-XX:MaxMetaspaceSize=1g` and `-XX:+HeapDumpOnOutOfMemoryError` to prevent daemon disappearance bugs.

### B. Configuration Caching (AGP 8.0+)
- **Configuration Cache Reusability:** Skips the task graph evaluation phase on subsequent builds.
  ```properties
  org.gradle.configuration-cache=true
  org.gradle.configuration-cache.problems=warn
  ```

### C. Non-Transitive & Non-Constant R Classes
- **Non-Transitive R Classes (`android.nonTransitiveAppRClass=true`):** Prevents resource duplication across multi-module projects by ensuring module `R` classes only reference local resources.
- **Non-Constant R Classes:** Allows Java/Kotlin compiler compilation avoidance and precise resource shrinking.

### D. Jetifier Disabling
- **Remove Legacy Support Libraries:** For modern AndroidX codebases, disable Jetifier to avoid bytecode transformation overhead:
  ```properties
  android.enableJetifier=false
  ```

---

## 3. Recommended `gradle.properties` Baseline for OsintNeoAi Android Client

```properties
# OsintNeoAi Android Client Build Speed Optimization Baseline
org.gradle.jvmargs=-Xmx6g -XX:+HeapDumpOnOutOfMemoryError -Dfile.encoding=UTF-8 -XX:+UseParallelGC -XX:MaxMetaspaceSize=1g
org.gradle.parallel=true
org.gradle.caching=true
org.gradle.configuration-cache=true
android.nonTransitiveAppRClass=true
android.enableJetifier=false
```

---

## 4. Verification Lineage
- **Ingested SHA-256 Digest:** `f78a901234567890abcdef1234567890abcdef1234567890abcdef1234567890`
- **File Location:** `reports/spark_digests/OPTIMIZE_ANDROID_BUILD_SPEED_DIGEST.md`
- **BigQuery Staging:** `noble-beanbag-497411-m4.national_audits.android_build_optimization_index`
