"""Social Media Creator Analytics: cleaning + analysis.
Source: Bright Data free sample 'Instagram Profiles - Github Hashtag.xlsx'
(github.com/luminati-io/Instagram-dataset-samples), 2,180 public profiles, scraped mid-2021.
Run: python analysis.py "Instagram Profiles - Github Hashtag.xlsx"
"""
import sys, json, hashlib
import numpy as np, pandas as pd
import statsmodels.formula.api as smf

src = sys.argv[1]
raw = pd.read_excel(src)

# ---------- 1. Clean profiles (drop personal data, pseudonymise IDs) ----------
raw["profile_id"] = raw["id"].astype(str).map(lambda x: hashlib.sha256(x.encode()).hexdigest()[:10])
prof = pd.DataFrame({
    "profile_id": raw.profile_id,
    "followers": raw.followers, "following": raw.following,
    "posts_count": raw.posts_count, "highlights_count": raw.highlights_count,
    "engagement_rate_pct": raw.avg_engagement * 100,          # missing for ~3% of profiles
    "is_business": raw.is_business_account.eq("yes"),
    "is_professional": raw.is_professional_account.eq("yes"),
    "country_code": raw.country_code,
    "category": raw.category_name.str.title(),
})
prof["followers_to_following"] = prof.followers / prof.following.replace(0, np.nan)
prof["follower_tier"] = pd.cut(prof.followers, [0, 250, 500, 1000, 5000, 1e7],
                               labels=["<250", "250-500", "500-1k", "1k-5k", "5k+"])
prof["posting_volume"] = pd.cut(prof.posts_count, [-1, 50, 200, 500, 1000, 1e7],
                                labels=["<50", "50-200", "200-500", "500-1k", "1k+"])

# ---------- 2. Flatten posts ----------
rows = []
for pid, fol, js in zip(raw.profile_id, raw.followers, raw.posts):
    for p in json.loads(js):
        if p.get("likes") is None or p.get("comments") is None or p.get("datetime") is None:
            continue
        cap = p.get("caption") or ""
        rows.append(dict(profile_id=pid, followers=fol, likes=p["likes"], comments=p["comments"],
                         post_type="Video" if p.get("video_view_count") is not None else "Image",
                         posted_at=pd.to_datetime(p["datetime"], unit="s"),
                         hashtag_count=cap.count("#"), caption_length=len(cap)))
posts = pd.DataFrame(rows)
posts = posts[(posts.likes >= 0) & (posts.comments >= 0)]
posts["engagement"] = posts.likes + posts.comments
posts["engagement_rate_pct"] = posts.engagement / posts.followers * 100
posts["day_of_week"] = posts.posted_at.dt.day_name()
posts["hour"] = posts.posted_at.dt.hour
posts["caption_band"] = pd.cut(posts.caption_length, [-1, 0, 100, 300, 800, 1e5],
                               labels=["none", "<100", "100-300", "300-800", "800+"])
posts["follower_tier"] = pd.cut(posts.followers, [0, 250, 500, 1000, 5000, 1e7],
                                labels=["<250", "250-500", "500-1k", "1k-5k", "5k+"])
prof.to_csv("data/profiles_clean.csv", index=False)
posts.to_csv("data/posts_clean.csv", index=False)

# ---------- 3. Findings ----------
print("profiles", len(prof), "| posts", len(posts))
print("\nMedian profile engagement rate by follower tier\n", prof.groupby("follower_tier", observed=True).engagement_rate_pct.agg(["median", "count"]).round(2))
print("\nMedian post ER by type\n", posts.groupby("post_type").engagement_rate_pct.agg(["median", "count"]).round(2))

# Adjusted model: does post type / caption / hashtags matter once audience size is controlled?
m = posts[posts.engagement_rate_pct > 0].copy()
m["log_er"] = np.log(m.engagement_rate_pct); m["log_fol"] = np.log(m.followers)
m["video"] = (m.post_type == "Video").astype(int); m["long_cap"] = (m.caption_length >= 300).astype(int)
m["log_tags"] = np.log1p(m.hashtag_count)
fit = smf.ols("log_er ~ log_fol + video + long_cap + log_tags", m).fit(
    cov_type="cluster", cov_kwds={"groups": pd.factorize(m.profile_id)[0]})   # cluster by account
print("\n", fit.summary().tables[1])
b = fit.params; ci = fit.conf_int()
for k in ["video", "long_cap", "log_tags"]:
    print(f"{k}: {np.exp(b[k]) - 1:+.1%}  (95% CI {np.exp(ci.loc[k, 0]) - 1:+.1%} to {np.exp(ci.loc[k, 1]) - 1:+.1%})")

# ---------- 4. What-if: close part of the video engagement gap ----------
w = posts.engagement_rate_pct.clip(upper=posts.engagement_rate_pct.quantile(.99))
vid = posts.post_type.eq("Video")
video_share_of_er = w[vid].sum() / w.sum()
gap_uplift = 1 / np.exp(b["video"]) - 1          # uplift if a video performed like a comparable image
print(f"\nvideos = {vid.mean():.1%} of posts, {video_share_of_er:.1%} of total engagement rate")
print(f"video->image-level uplift on a video post: {gap_uplift:+.1%}")
for f in (0.25, 0.5, 1.0):
    print(f"close {int(f*100)}% of video gap -> overall avg engagement rate {video_share_of_er * gap_uplift * f:+.2%}")
