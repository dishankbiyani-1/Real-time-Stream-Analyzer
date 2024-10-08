from django.conf import settings

DEJAVU_URL = settings.DEJAVU_CONTAINER_URL
API_URL_FOR_FEED_SONGS_DATA_TO_DEJAVU = f"{DEJAVU_URL}/feed-audio-to-dejavu/"
API_URL_FOR_IDENTIFY_SONG_IN_AUDIO_FILE = f"{DEJAVU_URL}/check-song/"