# Build the dashboard in Power BI (about 2 hours)

## 1. Load data
Home > Get data > Text/CSV: load `profiles_clean.csv` and `posts_clean.csv`.
In Power Query set types: `posted_at` = Date/Time; ratings and percentages = Decimal. Do not create a relationship between the tables (they are used on separate pages). Keep `follower_tier`, `posting_volume` and `caption_band` sorted in their natural order: Column tools > Sort by column (add an index column per band if needed).

## 2. Measures (Modeling > New measure)
```
Profiles = COUNTROWS(profiles_clean)
Posts Analysed = COUNTROWS(posts_clean)
Median ER % = MEDIAN(profiles_clean[engagement_rate_pct])
Median Followers = MEDIAN(profiles_clean[followers])
Median Post ER % = MEDIAN(posts_clean[engagement_rate_pct])
Video Share of Posts = DIVIDE(CALCULATE([Posts Analysed], posts_clean[post_type]="Video"), [Posts Analysed])
```
Scenario (on page 4). Create a what-if parameter: Modeling > New parameter > Range 0 to 1, step 0.05, name "Video Gap Closed". Then:
```
Video Share of ER =
DIVIDE(
  CALCULATE(SUM(posts_clean[engagement_rate_pct]), posts_clean[post_type]="Video"),
  SUM(posts_clean[engagement_rate_pct]))
Video Uplift = 0.163   -- from analysis.py (adjusted video gap)
Scenario Lift % = [Video Share of ER] * [Video Uplift] * [Video Gap Closed Value]
```
Note: in the script the 99th percentile is capped; the unadjusted share in Power BI will differ slightly. Mention that in your notes or cap the column in Power Query.

## 3. Pages
1. **Overview:** cards (Profiles, Posts Analysed, Median ER %, Median Followers) + country bar chart (top 10) + category bar chart.
2. **Audience segments:** column chart Median ER % by follower_tier; by posting_volume; clustered bars business vs personal. Slicers: country_code, is_business.
3. **Content performance:** Median Post ER % by post_type; by caption_band; by day_of_week; line chart by hour. Add a text box: "Caption length effect disappears after controlling for audience size."
4. **Growth scenario:** slider for Video Gap Closed, card for Scenario Lift %, and a text box listing the assumptions and limitations.

## 4. Publish
Take screenshots of all 4 pages into `screenshots/`, and save the `.pbix`. Commit everything to a new GitHub repo named `instagram-creator-analytics`.
