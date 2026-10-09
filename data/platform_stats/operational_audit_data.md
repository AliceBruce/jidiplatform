# Operational Audit: Platform Evaluation Performance Analysis

**Date**: September 24, 2026  
**Scope**: 15 environments (4 Snake, 8 Olympics, 3 Google Football), full historical records  
**Statistics**: 16,696 submissions, 3,902,471 deduplicated tasks (3,432,107 with valid completion times)

---

## Summary of Key Metrics (Paper §3.4)

| Metric | Value | Sample Size |
|--------|-------|-------------|
| **First-result latency P50** | 71.67 s | 10,380 submissions with results |
| **First-result latency P95** | 63.02 min (3,781.36 s) | 10,380 submissions |
| **Execution time P50** | 1.94 s | 3,432,107 successful tasks |
| **Execution time P95** | 59.41 s | 3,432,107 successful tasks |
| **Peak hourly throughput** | 4,158 matches/hour | 2021-09-24 18:00-19:00 |
| **Peak daily throughput** | 57,774 matches/day | 2021-08-30 |
| **1-hour result coverage** | 87.8% | 10,982 code-test-passed submissions |
| **24-hour result coverage** | 91.6% | 10,982 code-test-passed submissions |

---

## Metric 1: First Successful Result Latency

**Definition**: Time from submission to first successful match completion.  
**Method**: `first_result_latency = min(valid_success_end_time) - submission.create_time`

### Per-Environment Results

| Environment | Submissions | Tasks | Results | P50 | P95 |
|-------------|-------------|-------|---------|-----|-----|
| Snake 1v1 | 3,671 | 1,318,721 | 2,140 | 26.10 s | 25.69 min |
| Snake 5p | 51 | 37,018 | 32 | 9.93 min | 17.81 hr |
| Snake 3v3 | 2,673 | 938,271 | 1,677 | 47.72 s | 33.73 min |
| Snake 2p | 2,056 | 415,307 | 80 | 28.80 min | 22.43 min |
| Olympics Running | 514 | 292,213 | 324 | 1.33 min | 1.11 hr |
| Olympics Table Hockey | 365 | 28,570 | 279 | 1.21 min | 5.73 min |
| Olympics Football | 410 | 57,379 | 157 | 4.85 min | 1.26 days |
| Olympics Wrestling | 4,369 | 500,613 | 3,535 | 56.69 s | 6.86 min |
| Olympics Billiards | 20 | 8,703 | 13 | 5.76 s | 20.12 hr |
| Olympics Curling | 327 | 62,390 | 177 | 24.72 min | 6.20 days |
| Olympics Integrated | 1,023 | 106,369 | 495 | 7.95 min | 23.70 hr |
| Olympics Billiards Comp | 253 | 18,980 | 143 | 43.86 s | 3.13 min |
| GRF 11v11 Kaggle | 127 | 24,358 | 82 | 7.61 min | 3.33 hr |
| GRF 11v11 Stochastic | 474 | 46,802 | 215 | 20.60 min | 18.63 hr |
| GRF 5v5 MALib | 363 | 46,777 | 309 | 9.12 min | 16.81 hr |

**Key Finding**: Among 16,696 submissions, 10,380 (62.2%) have computable results. The median is 71.67 s, P95 is 63.02 min. Significant variation across environments reflects differences in match duration and scheduling.

---

## Metric 2: Task Startup Latency & Execution Time

**Definition**: 
- Startup latency = `steps[0].time - task.create_time`
- Execution time = `end_time - steps[0].time` (successful matches only)

### Aggregate Statistics

| Metric | P50 | P95 | Sample Size |
|--------|-----|-----|-------------|
| Startup latency | 88 s | 12.47 hr | All started tasks |
| Execution time | 1.94 s | 59.41 s | 3,432,107 successful |

**Note**: These come from different sample sets and cannot be summed. 57,174 legacy tasks restarted after July 16, 2026 restoration significantly affect P95 tails.

---

## Metric 3: Hourly/Daily Throughput

**Definition**: Number of successful tasks completed per time window.

### Peak Throughput by Environment

| Environment | Total Success | Peak Hour | Peak Day |
|-------------|---------------|-----------|----------|
| Snake 1v1 | 1,225,848 | 1,598 | 27,501 |
| Snake 3v3 | 869,702 | 1,008 | 21,985 |
| Snake 2p | 414,994 | 2,490 | 17,855 |
| Olympics Wrestling | 388,130 | 618 | 3,165 |
| Olympics Running | 254,587 | 217 | 2,076 |
| Olympics Integrated | 52,734 | 104 | 1,006 |
| GRF 11v11 Kaggle | 20,667 | 102 | 288 |
| GRF 11v11 Stochastic | 32,177 | 75 | 393 |
| GRF 5v5 MALib | 38,687 | 55 | 557 |

**Overall Peak**: 4,158 matches/hour (2021-09-24 18:00-19:00), 57,774 matches/day (2021-08-30)

---

## Metric 4: Fixed-Window Result Coverage

**Definition**: Proportion of submissions with ≥K successful results within time window T.  
**Method**: `coverage = submissions_with_≥K_results / submissions_with_full_observation_window`

### 1-Hour Coverage (K=1)

| Environment | Submissions | 5-min | 1-hour | 24-hour |
|-------------|-------------|-------|--------|---------|
| Snake 1v1 | 3,671 | 42.5% | 57.4% | 58.2% |
| Snake 3v3 | 2,673 | 43.0% | 60.7% | 62.2% |
| Olympics Wrestling | 4,369 | 75.1% | 79.9% | 80.8% |
| Olympics Table Hockey | 365 | 72.1% | 76.4% | 76.4% |
| GRF 5v5 MALib | 363 | 18.5% | 66.1% | 84.6% |

**Code-test-passed subset**: 10,982 submissions → 87.8% within 1 hour, 91.6% within 24 hours

---

## Data Quality & Reproducibility

**Extraction period**: 2026-09-24 04:30:50 to 05:59:21 UTC  
**Database**: MySQL 5.7.35-0ubuntu0.18.04.2  
**Task ID upper bound**: 8,220,229 (exclusive)

### Validation Checks

| Check | Count |
|-------|-------|
| Target tasks | 3,902,471 |
| Tasks without logs | 381,766 |
| Successful but no valid end time | 0 |
| First step before task creation | 0 |
| End before first step | 0 |
| Logs passing JSON validation | 414 |
| Validation failures | 0 |

### Task Status Distribution

| Status | Count |
|--------|-------|
| Successful | 3,432,107 |
| Failed | 100,868 |
| Pending container allocation | 280,168 |
| Pending processing | 28,336 |
| Deprecated | 60,992 |

---

## Suggested Paper Text (§3.4)

> We analyzed retained daily-evaluation records for 15 Snake, Olympics, and Google Football environments, comprising 16,696 submissions and 3,902,471 distinct tasks. Competition tables were excluded. We linked submissions to tasks through deduplicated submission-task associations and extracted the first-step and end timestamps from retained match logs.
>
> Among 10,380 submissions with an observable successful result, the median and 95th-percentile submission-to-first-result latencies were 71.67 s and 3,781.36 s (63.02 min), respectively. The highest observed calendar-hour completion count was 4,158 successful matches. For 3,432,107 successful compressed replays, stored payloads occupied 41.07 GiB compared with 308.22 GiB after decompression, a size-weighted reduction of 86.7%.
>
> These measurements describe the retained operational workload, rather than maximum system capacity or isolated scheduler overhead. Missing historical records may delay the first observable result and reduce measured fixed-window coverage. We therefore report sample counts and separate tasks created before, but started after, the July 16, 2026 restoration event.

---

## Notes

- P50 = median (50th percentile), P95 = 95th percentile (linear interpolation)
- All timestamps in UNIX epoch, converted to Beijing time for calendar grouping
- First step: `steps[0].time`; end time: root node `end_time` (not `task.update_time`)
- Historical log gaps may delay first observable result and reduce coverage measurements
- This is measurement on retained workloads, not a controlled capacity study
