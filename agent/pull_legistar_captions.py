import re
import json
import logging
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def extract_granicus_captions(legistar_video_url):
    """
    Given a Granicus/Legistar video player URL (e.g., for City Council meetings),
    this extracts the hidden closed captions (VTT/SRT transcript) and parses them
    for keyword searching.
    """
    logger.info(f"Targeting municipal video URL: {legistar_video_url}")
    
    # 1. Fetch the video player page
    try:
        response = requests.get(legistar_video_url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to fetch video page: {e}")
        return []

    # 2. Granicus players often embed a JSON configuration or a direct <track> tag 
    #    with the .vtt file.
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Try finding standard HTML5 track tags first
    track_tag = soup.find('track', kind='captions')
    vtt_url = None
    
    if track_tag and track_tag.has_attr('src'):
        vtt_url = track_tag['src']
        logger.info(f"Found standard <track> tag VTT: {vtt_url}")
    else:
        # Fallback: Regex search the page source for the transcript URL
        # e.g., "TranscriptUrl": "https://archive-media.granicus.com/.../transcript.vtt"
        match = re.search(r'"TranscriptUrl"\s*:\s*"([^"]+\.vtt)"', response.text, re.IGNORECASE)
        if match:
            vtt_url = match.group(1)
            logger.info(f"Regex extracted Granicus VTT URL: {vtt_url}")

    if not vtt_url:
        logger.warning("Could not locate closed captions file in page source.")
        return []

    # Ensure the URL is absolute
    if vtt_url.startswith('/'):
        from urllib.parse import urlparse
        parsed_uri = urlparse(legistar_video_url)
        vtt_url = f"{parsed_uri.scheme}://{parsed_uri.netloc}{vtt_url}"

    # 3. Download the VTT file
    try:
        vtt_response = requests.get(vtt_url, timeout=10)
        vtt_response.raise_for_status()
        vtt_text = vtt_response.text
        
        # 4. Basic VTT parser
        # VTT format generally has timestamps followed by text on the next lines
        lines = vtt_text.splitlines()
        captions = []
        current_time = "00:00:00"
        
        for line in lines:
            line = line.strip()
            if '-->' in line:
                current_time = line.split(' --> ')[0]
            elif line and not line.startswith('WEBVTT') and not line.isdigit():
                captions.append({
                    "timestamp": current_time,
                    "text": line
                })
                
        logger.info(f"Successfully extracted {len(captions)} caption lines.")
        return captions

    except Exception as e:
        logger.error(f"Failed to download or parse VTT file: {e}")
        return []

def search_captions(captions, keywords):
    """
    Searches the parsed captions for specific OSINT keywords (e.g., 'Chromium', 'Shelter').
    """
    matches = []
    for cap in captions:
        for kw in keywords:
            if kw.lower() in cap['text'].lower():
                matches.append((cap['timestamp'], cap['text']))
                break
    return matches

if __name__ == "__main__":
    # Test simulation for Huntington Beach Legistar
    test_url = "https://huntingtonbeach.granicus.com/MediaPlayer.php?view_id=1&clip_id=9999"
    keywords = ["cameron", "homeless", "chromium", "environmental", "cleanup"]
    
    logger.info("Initializing Granicus/Legistar Closed Captions extractor...")
    # NOTE: In a real run, this would target the actual video ID from the Legistar file.
    logger.info("Script is armed and ready to extract VTT tracks from municipal meeting videos.")
