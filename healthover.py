import streamlit as st
import requests
from datetime import datetime, timedelta

# YouTube API Key
API_KEY = "AIzaSyDoKDvnL-hxlEh-1qBpB3um3fb2T0c87Pw"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# Streamlit App Title
st.title("YouTube Viral Topics Tool")

# Input Fields
days = st.number_input("Enter Days to Search (1-30):", min_value=1, max_value=30, value=5)

# List of broader keywords
keywords = [
    "over 60 health tips", "build muscle after 60", "reverse muscle loss after 60",
    "Reddit over 60 health tips", "foods for seniors", "AITA Update",
    "best protein for seniors", "vitamins for seniors", "supplements for seniors",
    "senior fitness exercises", "reverse sarcopenia naturally Reddit", "healthy aging tips",
    "longevity secrets", "senior nutrition guide", "anti-aging foods for seniors",
    "natural remedies for seniors", "over 60 diet plan", "regain strength after 60",
    "foods that boost energy after 60", "live longer after 60", "senior muscle recovery",
    "doctor recommended foods for seniors", "healthy lifestyle after 60", "memory improvement for seniors"
]

# Fetch Data Button
if st.button("Fetch Data"):
    try:
        start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
        all_results = []

        for keyword in keywords:
            st.write(f"🔍 Searching for keyword: **{keyword}**")

            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 5,
                "key": API_KEY,
            }

            response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
            data = response.json()

            if "items" not in data or not data["items"]:
                st.warning(f"No videos found for keyword: {keyword}")
                continue

            videos = data["items"]
            video_ids = [v["id"]["videoId"] for v in videos if "id" in v and "videoId" in v["id"]]
            channel_ids = [v["snippet"]["channelId"] for v in videos if "snippet" in v and "channelId" in v["snippet"]]

            if not video_ids or not channel_ids:
                continue

            # Fetch video stats
            stats_response = requests.get(YOUTUBE_VIDEO_URL, params={
                "part": "statistics",
                "id": ",".join(video_ids),
                "key": API_KEY
            })
            stats_data = stats_response.json()

            # Fetch channel stats
            channel_response = requests.get(YOUTUBE_CHANNEL_URL, params={
                "part": "statistics,snippet",
                "id": ",".join(channel_ids),
                "key": API_KEY
            })
            channel_data = channel_response.json()

            if "items" not in stats_data or "items" not in channel_data:
                continue

            video_stats = stats_data["items"]
            channel_stats = {ch["id"]: ch for ch in channel_data["items"]}

            # Match each video to its stats and channel
            for video, stat in zip(videos, video_stats):
                channel_id = video["snippet"]["channelId"]
                channel = channel_stats.get(channel_id, {})

                # Safely get subscriber count
                subs = channel.get("statistics", {}).get("subscriberCount")
                if subs is None:
                    continue  # Skip hidden subscriber count

                subs = int(subs)
                if subs >= 3000:
                    continue  # Skip big channels

                title = video["snippet"].get("title", "N/A")
                description = video["snippet"].get("description", "")[:200]
                video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                views = int(stat["statistics"].get("viewCount", 0))
                channel_title = channel.get("snippet", {}).get("title", "Unknown Channel")

                all_results.append({
                    "Title": title,
                    "Description": description,
                    "URL": video_url,
                    "Views": views,
                    "Subscribers": subs,
                    "Channel": channel_title
                })

        # Display results
        if all_results:
            st.success(f"✅ Found {len(all_results)} small channels (<3,000 subs)!")
            for result in all_results:
                st.markdown(
                    f"**🎬 Title:** {result['Title']}  \n"
                    f"**📺 Channel:** {result['Channel']}  \n"
                    f"**📝 Description:** {result['Description']}  \n"
                    f"**🔗 URL:** [Watch Video]({result['URL']})  \n"
                    f"**👁️ Views:** {result['Views']}  \n"
                    f"**👤 Subscribers:** {result['Subscribers']}"
                )
                st.write("---")
        else:
            st.warning("⚠️ No small channels (<3,000 subs) found.")

    except Exception as e:
        st.error(f"❌ Error: {e}")
