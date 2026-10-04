import streamlit as st
import random
import pandas as pd
from datetime import datetime
from utils.database import add_entity, save_scan_result
from utils.api_clients import lookup_social_username

PLATFORMS = {
    "Twitter/X": {"icon": "🐦", "url": "https://twitter.com/{}", "profile_fields": ["followers", "following", "tweets", "joined"]},
    "Instagram": {"icon": "📸", "url": "https://instagram.com/{}", "profile_fields": ["followers", "following", "posts"]},
    "LinkedIn": {"icon": "💼", "url": "https://linkedin.com/in/{}", "profile_fields": ["connections", "position", "company"]},
    "Facebook": {"icon": "📘", "url": "https://facebook.com/{}", "profile_fields": ["friends", "groups", "location"]},
    "TikTok": {"icon": "🎵", "url": "https://tiktok.com/@{}", "profile_fields": ["followers", "following", "likes"]},
    "Reddit": {"icon": "🤖", "url": "https://reddit.com/u/{}", "profile_fields": ["karma", "account_age", "subreddits"]},
    "GitHub": {"icon": "💻", "url": "https://github.com/{}", "profile_fields": ["repos", "followers", "contributions"]},
    "YouTube": {"icon": "📺", "url": "https://youtube.com/@{}", "profile_fields": ["subscribers", "videos", "views"]},
    "Telegram": {"icon": "✈️", "url": "https://t.me/{}", "profile_fields": ["username", "bio"]},
    "Pinterest": {"icon": "📌", "url": "https://pinterest.com/{}", "profile_fields": ["followers", "pins"]},
}

def generate_mock_profile(username, platform):
    followers = random.randint(100, 50000)
    return {
        "username": username,
        "platform": platform,
        "profile_url": PLATFORMS[platform]["url"].format(username),
        "found": True,
        "followers": followers,
        "following": random.randint(50, 2000),
        "posts": random.randint(10, 500),
        "account_age_years": round(random.uniform(0.5, 10), 1),
        "bio": f"Simulated profile for @{username} on {platform}",
        "location": "Not disclosed",
        "verified": random.choice([True, False]),
        "private": random.choice([True, False]),
        "engagement_rate": f"{random.uniform(0.5, 8.0):.1f}%",
        "note": "⚠️ Simulated data — add API keys in Secrets for live results",
        "scanned_at": datetime.now().isoformat(),
    }

def get_profile(username, platform):
    """Try real API first, fall back to mock data."""
    api_result = lookup_social_username(username, platform)
    if api_result and "error" not in api_result and api_result.get("found") is True:
        return api_result
    return generate_mock_profile(username, platform)

def render():
    st.markdown("## 📱 Social Media Intelligence")
    st.markdown("Search and extract account information from multiple social platforms.")

    tab1, tab2 = st.tabs(["🔍 Username Search", "📊 Platform Analysis"])

    with tab1:
        col_in, col_opts = st.columns([2, 1])
        with col_in:
            username = st.text_input("Enter Username / Handle", placeholder="e.g. johndoe (without @)")
        with col_opts:
            selected_platforms = st.multiselect(
                "Platforms to Search",
                list(PLATFORMS.keys()),
                default=list(PLATFORMS.keys())[:5]
            )

        col_o1, col_o2 = st.columns(2)
        with col_o1:
            save_to_master = st.checkbox("Save to Master Database", value=True)

        if st.button("🔍 Search All Platforms", type="primary", use_container_width=True):
            if not username.strip():
                st.warning("Please enter a username.")
            elif not selected_platforms:
                st.warning("Please select at least one platform.")
            else:
                clean_username = username.strip().lstrip("@")
                st.info(f"Searching for **@{clean_username}** across {len(selected_platforms)} platforms...")

                results = []
                progress = st.progress(0)
                for i, platform in enumerate(selected_platforms):
                    profile = get_profile(clean_username, platform)
                    results.append(profile)
                    progress.progress((i + 1) / len(selected_platforms))

                progress.progress(1.0)
                real_count = sum(1 for r in results if r.get("source") == "api")
                if real_count > 0:
                    st.success(f"✅ Found {len(results)} profiles ({real_count} from live APIs)")
                else:
                    st.success(f"✅ Found {len(results)} profiles (simulated) — add API keys for live data")

                # Grid display
                st.markdown("### 🎯 Profile Results")
                cols = st.columns(min(len(results), 3))
                for i, profile in enumerate(results):
                    with cols[i % 3]:
                        platform = profile["platform"]
                        icon = PLATFORMS[platform]["icon"]
                        st.markdown(f"""
                        <div style='background:#0F1628;border:1px solid #1E2D50;border-radius:8px;padding:12px;margin-bottom:8px;'>
                            <div style='font-size:1.1rem;font-weight:bold;color:#00D4FF'>{icon} {platform}</div>
                            <div style='color:#C8D8F0;font-size:0.85rem;margin-top:4px'>@{profile['username']}</div>
                            <hr style='border-color:#1E2D50;margin:8px 0'>
                            <div style='color:#5A7090;font-size:0.78rem'>Followers: <span style='color:#E8F4FF'>{profile['followers']:,}</span></div>
                            <div style='color:#5A7090;font-size:0.78rem'>Engagement: <span style='color:#E8F4FF'>{profile['engagement_rate']}</span></div>
                            <div style='color:#5A7090;font-size:0.78rem'>Private: <span style='color:#E8F4FF'>{"Yes" if profile["private"] else "No"}</span></div>
                            <div style='color:#5A7090;font-size:0.78rem'>Verified: <span style='color:#E8F4FF'>{"✅" if profile["verified"] else "❌"}</span></div>
                            <div style='margin-top:8px'><a href='{profile["profile_url"]}' target='_blank' style='color:#00D4FF;font-size:0.78rem'>View Profile →</a></div>
                        </div>
                        """, unsafe_allow_html=True)

                if save_to_master:
                    ts = int(datetime.now().timestamp())
                    for profile in results:
                        eid = f"ENT-SM-{ts}-{profile['platform'][:3].upper()}"
                        add_entity(
                            eid, "Social_Account",
                            f"@{profile['username']} ({profile['platform']})",
                            "Social Media",
                            profile.get("location", ""),
                            "Unknown",
                            profile["platform"],
                            f"Followers: {profile['followers']} | Engagement: {profile['engagement_rate']}"
                        )
                        save_scan_result(f"@{profile['username']}", f"Social:{profile['platform']}", profile)
                    st.success("💾 Profiles saved to master database!")

                # Summary table
                st.divider()
                st.markdown("### 📋 Summary Table")
                df = pd.DataFrame([{
                    "Platform": p["platform"],
                    "Username": f"@{p['username']}",
                    "Followers": f"{p['followers']:,}",
                    "Engagement": p["engagement_rate"],
                    "Private": "Yes" if p["private"] else "No",
                    "Verified": "✅" if p["verified"] else "❌",
                    "Profile URL": p["profile_url"],
                } for p in results])
                st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        st.markdown("### 📊 Platform Intelligence Overview")
        st.markdown("""
        | Platform | Data Available | API Required | Notes |
        |---|---|---|---|
        | Twitter/X | Profile, tweets, followers, following | ✅ Bearer Token | Limited by API tier |
        | Instagram | Profile, posts, followers | ✅ Graph API | Business accounts only |
        | LinkedIn | Profile, connections, work history | ✅ OAuth | Strict rate limits |
        | GitHub | Profile, repos, commits, issues | ✅ Token (optional) | Public data available |
        | Reddit | Posts, comments, karma, subreddits | ✅ OAuth | Good public access |
        | TikTok | Profile, videos, followers | ✅ API Key | Limited data |
        | Facebook | Profile, friends, groups | ✅ Graph API | Heavily restricted |
        | Telegram | Username, bio | ❌ MTProto | Bot API only |
        """)

        st.info("""
        **To enable real social media intelligence:**
        1. Go to **Settings** and add your API keys
        2. The platform will use live APIs instead of simulated data
        3. Results will be automatically saved to your master sheet
        """)
