# Social Media Creator Analytics Dashboard (Instagram)

What drives engagement for small creators on Instagram, and where could a platform realistically improve it?

**Data:** Bright Data's free public sample, 2,180 public Instagram profiles (coding/GitHub-hashtag creators) and their 24,910 most recent posts. Snapshot from mid-2021.
Source: https://github.com/luminati-io/Instagram-dataset-samples
**Tools:** Python (pandas, statsmodels), Power BI (DAX)
**Privacy:** personal fields (names, bios, emails, images, URLs) dropped; account IDs hashed. Only aggregated metrics are used.

## Method
1. Cleaned and flattened the nested post data (JSON) into profile-level and post-level tables.
2. Engagement rate per post = (likes + comments) / followers. The 99th percentile is capped when averaging because of extreme outliers.
3. Compared segments (audience size, account type, posting volume, content type, hashtags, caption length, day and hour).
4. Because audience size drives engagement rate, I fitted a regression on log engagement rate with follower count as a control, clustering standard errors by account (posts from one account are not independent).
5. Built a clearly labelled what-if scenario from the one effect that held up.

## Findings
| Finding | Evidence |
|---|---|
| Engagement rate falls sharply as audience grows | Median 12.7% for <250 followers vs 1.9% for 5k+. Doubling followers is associated with roughly 27% lower engagement rate. |
| Frequent posters have lower engagement rates | Median 11.1% for <50 posts vs 1.5% for 1k+ posts (overlaps with audience size). |
| **Videos underperform images** | Videos get about 14% lower engagement rate than image posts from comparable audience sizes (95% CI about 7% to 20%). The gap shows up in all five follower tiers. |
| Hashtags: raw medians look flat, but adjusted for audience size they are associated with higher engagement | Roughly +10% to +20% for 5-20 hashtags vs none. Observational, so not proof of cause. |
| Caption length is **not** a real driver | Short captions looked better in the raw data, but the effect disappears after controlling for audience size (-3%, CI includes zero). |
| Posting day and hour matter little | Sunday is slightly higher; weekdays and hours are close together. |

## What-if scenario
Videos are 13.7% of posts and 12.1% of total engagement rate. If product changes (better recommendations and editing tools for video) closed part of the video gap:

| Share of video gap closed | Effect on average engagement rate |
|---|---|
| 25% | about +0.5% |
| 50% | about +1.0% |
| 100% (videos match comparable images) | about +2.0% |

This is an upper-bound illustration, not a forecast. It assumes the video gap is a quality or recommendation problem rather than an audience preference, which this data cannot confirm.

## Limitations
- Snapshot from 2021; Instagram's algorithm and Reels have changed a lot since.
- Niche sample (coding creators), mostly small accounts; only 2 verified accounts, so verification could not be analysed.
- Observational data: associations, not causal effects. Engagement rate also mechanically falls with follower count.
- Likes and comments only (no reach, saves or shares).

## Files
- `analysis.py` reproduces everything from the source Excel file
- `data/profiles_clean.csv`, `data/posts_clean.csv` (inputs for the Power BI dashboard)
- `POWERBI_STEPS.md` dashboard build guide
- `screenshots/` add your dashboard screenshots here
