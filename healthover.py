import streamlit as st
import requests
from datetime import datetime, timedelta

# YouTube API Key
API_KEY = "AIzaSyDoKDvnL-hxlEh-1qBpB3um3fb2T0c87Pw"

# API URLs
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# Streamlit App Title
st.title("🎯 YouTube Viral Topics Tool")

# Input Fields
days = st.number_input("Enter Days to Search (1-30):", min_value=1, max_value=30, value=5)

# List of broader keywords
keywords = [
    "over 60 health tips",
    "build muscle after 60",
    "reverse muscle loss after 60",
    "Reddit over 60 health tips",
    "foods for seniors",
    "AITA Update",
    "best protein for seniors",
    "vitamins for seniors",
    "supplements for seniors",
    "senior fitness exercises",
    "reverse sarcopenia naturally Reddit",
    "healthy aging tips",
    "longevity secrets",
    "senior nutrition guide",
    "anti-aging foods for seniors",
    "natural remedies for seniors",
    "over 60 diet plan",
    "regain strength after 60",
    "foods that boost energy after 60",
    "live longer after 60",
    "senior muscle recovery",
    "doctor recommended foods for seniors",
    "healthy lifestyle after 60",
    "memory improvement for seniors",
]

# Fetch Data Button
if st.button("🔍 Fetch Data"):
    try:
        start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
        all_results = []

        # Iterate through keywords
        for keyword in keywords:
            st.write(f"🔎 Searching for keyword: **{keyword}**")

            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 5,
                "key": API_KEY,
            }

            # Search videos
            response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
            data = response.json()

            if "items" not in data or not data["items"]:
                st.warning(f"No videos found for keyword: {keyword}")
                continue

            videos = data["items"]
            video_ids = [v["id"]["videoId"] for v in videos if "id" in v and "videoId" in v["id"]]
            channel_ids = [v["snippet"]["channelId"] for v in videos if "snippet" in v and "channelId" in v["snippet"]]

            if not video_ids or not channel_ids:
                st.warning(f"Skipping keyword: {keyword} due to missing data.")
                continue

            # Get video statistics
            stats_params = {"part": "statistics", "id": ",".join(video_ids), "key": API_KEY}
            stats_response = requests.get(YOUTUBE_VIDEO_URL, params=stats_params)
            stats_data = stats_response.json()

            if "items" not in stats_data or not stats_data["items"]:
                st.warning(f"Failed to fetch video stats for keyword: {keyword}")
                continue

            # Get channel statistics
            channel_params = {"part": "statistics", "id": ",".join(channel_ids), "key": API_KEY}
            channel_response = requests.get(YOUTUBE_CHANNEL_URL, params=channel_params)
            channel_data = channel_response.json()

            if "items" not in channel_data or not channel_data["items"]:
                st.warning(f"Failed to fetch channel stats for keyword: {keyword}")
                continue

            stats = stats_data["items"]
            channels = channel_data["items"]

            # Combine results
            for video, stat, channel in zip(videos, stats, channels):
                title = video["snippet"].get("title", "N/A")
                description = video["snippet"].get("description", "")[:200]
                video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                views = int(stat["statistics"].get("viewCount", 0))
                subs = int(channel["statistics"].get("subscriberCount", 0))

                # Filter: Only small channels (<3000 subs)
                if subs < 3000:
                    all_results.append({
                        "Title": title,
                        "Description": description,
                        "URL": video_url,
                        "Views": views,
                        "Subscribers": subs,
                    })

        # Display results
        if all_results:
            st.success(f"✅ Found {len(all_results)} viral video results from small channels!")
            sorted_results = sorted(all_results, key=lambda x: x["Views"], reverse=True)
            for result in sorted_results:
                st.markdown(f"""
                **🎥 Title:** {result['Title']}  
                **📝 Description:** {result['Description']}  
                **🔗 URL:** [Watch Here]({result['URL']})  
                **👁️ Views:** {result['Views']:,}  
                **👤 Subscribers:** {result['Subscribers']:,}
                """)
                st.write("---")
        else:
            st.warning("No viral videos found for channels under 3,000 subscribers.")

    except Exception as e:
        st.error(f"❌ An error occurred: {e}")
