#####THIS FILE NOT IN USE CURRENTLY


import mediacloud, json, datetime, csv
import pandas as pd
import requests
import os
from pathlib import Path
import pkg_resources
assert pkg_resources.get_distribution("requests").version >= '1.2.3'

#My API key given by Mediacloud
MY_API_KEY = '0b048304d2f7398cb91248b7e07b3b153d32840c1a8c42ab4006f58aaa8a440a'

#media_id's of some fake news sites
INFOWARS = 18515
RT = 305385
NAT_NEWS = 24030

mc = mediacloud.MediaCloud(MY_API_KEY)

def get_stories_from_media(media_name, num_stories = 1000):
    """
    Args: media_name: name of media source to get stories from
          num_stories: number of stories to get from media_name

    Get stories from media source corresponding to given media_name
    """

    # Get the media source of interest and set var defaults
    with open( './csv_storage/media.csv', 'r', newline="") as fh:
        sources = pd.read_csv(fh, header=0)

    media_id = sources[sources['name'] == media_name]['media_id'].get(0)
    start = 0
    count = 0
    rows  = 100
    opened = False
    stories = []

    # field names to populate our new outlinks csv
    fieldnames = [
        u'stories_id',
        u'title',
        u'publish_date'
    ]

    while True:
        # populate params with topics-api stories/list call
        params = {
            'last_processed_stories_id': start,
            'rows': rows,
            'q': 'media_id:{}'.format(str(media_id)),
            'fq': 'publish_date:[2016-01-01T00:00:00Z TO 2017-1-20T00:00:00Z]',
            'key': MY_API_KEY
        }

        print ("Fetching {} stories starting from {}".format( rows, start))
        r = requests.get( 'https://api.mediacloud.org/api/v2/stories_public/list/', params = params, headers = { 'Accept': 'application/json'} )
        data = r.json()

        # If no more data, stop collecting and process already collected data
        if len(data) == 0:
            break

        # Only collect stories up to specified limit (prune off anything after num_stories exceeded)
        count += len(data)
        prune = num_stories - count
        if prune <= 0:
            stories.extend(data[:-prune])
            break

        stories.extend( data )
        start = stories[-1][ 'processed_stories_id' ]

    # Process info here (write in to CSV file)
    media_name = media_name.replace(' ', '_')
    with open( './csv_storage/media_' + media_name + '.csv', 'a', newline="") as csvfile:
        print ("\nOpened file: Dumping story content for media_name:{}\n".format(media_name))
        cwriter = csv.DictWriter( csvfile, fieldnames, extrasaction='ignore')
        if not opened:
            cwriter.writeheader()
            opened = True

        cwriter.writerows( stories )
