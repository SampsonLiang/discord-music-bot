import os
from yt_dlp import YoutubeDL

def get_video(search):
    '''
    Search for a link on YouTube and play audio from the first matching search result.
    '''
    options = {'format': 'bestaudio/best', 'noplaylist': True, 'extractor-args': 'youtube:player_client=web'}
    try:
        info = YoutubeDL(options).extract_info(f'ytsearch:{search}', download = False)['entries'][0]
    except Exception:
        return
    
    url = info['url']
    title = info['title']

    return url, title
