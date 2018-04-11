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

def write_csv_media(media_name, chunk_size = 100):
    """
    Args: media_names: media source name (can have multiple) in list format
          chunk_size: max # of media sources that can be written per iteration

    Write the media_id, url, and names of the given media_name(s) in a CSV file
    """
    media = []
    media_idx = 0
    last_media_id = 0
    rows  = chunk_size
    opened = False

    fieldnames = [
        u'media_id',
        u'url',
        u'moderated',
        u'moderation_notes',
        u'name'
    ]

    while True:
        params = { 'last_media_id': last_media_id, 'rows': rows, 'name': media_name[media_idx], 'key': MY_API_KEY }
        print ("start:{} rows:{}".format( last_media_id, rows))
        r = requests.get( 'https://api.mediacloud.org/api/v2/media/list', params = params, headers = { 'Accept': 'application/json'} )
        data = r.json()

        if not len(data):

            # If there are more media_names, write what we have to csv file and continue
            with open( './csv_storage/media.csv', 'a', newline="") as csvfile:
                print ("\nOpened file: Dumping media source content for {}\n".format(media_name[media_idx]))

                # Flush media buffer to csv file
                cwriter = csv.DictWriter( csvfile, fieldnames, extrasaction='ignore')

                if not opened:
                    cwriter.writeheader()
                    opened = True

                cwriter.writerows( media )

            # Continue to next user-inputted media_name
            media_idx += 1
            last_media_id = 0
            media = []
            if media_idx < len(media_name):
                print ("Grabbing sources of next media name:{}\n".format(media_name[media_idx]))
                continue

            # Done if no more media sources to get
            break


        #add to media buffer and search for more media sources similar to current media_name
        media.extend( data )
        last_media_id = media[-1]['media_id']

def get_stories_from_media(media_name, num_stories = 1000):
    """
    Args: media_name: name of media source to get stories from
          num_stories: number of stories to get from media_name

    Get stories from media source corresponding to given media_name
    """
    with open( './csv_storage/media.csv', 'r', newline="") as fh:
        sources = pd.read_csv(fh, header=0)

    media_id = sources[sources['name'] == media_name]['media_id'].get(0)
    start = 0
    count = 0
    rows  = 100
    opened = False
    stories = []

    fieldnames = [
        u'stories_id',
        u'title',
        u'publish_date'
    ]

    while True:
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

        if len(data) == 0:
            break

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

def get_stories_from_stories(media_name, num_stories=1000, story_idx = 0):
    """
    Args: media_name: media_name for which we want out-linked stories (from pre-existing stories)
          num_stories: max number of out-linked stories we want to grab from each media_name
          story_idx: The index of the story that is currently grabbing outlinks

    Gets the stories referenced by the stories we've already grabbed from media_name
    """
    media_name = media_name.replace(' ', '_')
    with open('./csv_storage/media_' + media_name + '.csv', 'r', newline="") as fh:
        table = pd.read_csv(fh, header=0)
    story_ids = table['stories_id']
    start = 0
    rows = 100
    count = 0
    stories = []
    opened = False

    def reset_defaults():
        start = 0
        count = 0
        stories = []

    def write_to_csv(media=[]):
        fieldnames = [
            u'stories_id',
            u'title',
            u'publish_date'
        ]

        path_name = './csv_storage/media_' + media_name + '_outlinks.csv'
        with open(path_name, 'w', newline="") as csvfile:
            cwriter = csv.DictWriter( csvfile, fieldnames, extrasaction='ignore')

            if not os.path.getsize(path_name):
                cwriter.writeheader()

            cwriter.writerows( media )

    while True:

        if story_idx == len(table.index):
            break

        story_id = story_ids.get(story_idx)
        params = {
            'last_processed_stories_id': start,
            'rows': rows,
            # TODO: Need help writing the correct query to get outlinks
            'fq': '{~ timespan:1234 link_from_story:{}}'.format(str(story_id)),
            'key': MY_API_KEY
        }
        print ("Fetching {} stories starting from {}".format( rows, start))
        r = requests.get( 'https://api.mediacloud.org/api/v2/stories_public/list', params = params, headers = { 'Accept': 'application/json'})
        data = r.json()
        print (data)

        if len(data) == 0:
            story_idx += 1
            write_to_csv(stories)
            reset_defaults()
            continue

        count += len(data)
        prune = num_stories - count
        if prune <= 0:
            stories.extend(data[:-prune])
            story_idx += 1
            write_to_csv(stories)
            reset_defaults()
            continue

        stories.extend( data )
        # print (stories)
        start = stories[-1][ 'processed_stories_id' ]
