import mediacloud, json, datetime, csv
import pkg_resources
import requests
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

def get_stories_from_media(media_id, num_stories=1000):
    """
    Args: media_id: media_id or list of media_id's
          num_stories: number of stories to fetch from set of media_id(s)

    Get stories from media source(s) corresponding to given media_id(s)
    """
    fetch_size = num_stories
    stories = []
    last_processed_stories_id = 0
    while len(stories) < 2000:
        fetched_stories = mc.storyList('( trump ) OR ( election )',
                                       solr_filter=[ mc.publish_date_query( datetime.date(2016,1,1), datetime.date(2017,1,20)),
                                                                             'tags_id_media:1'],
                                        last_processed_stories_id=last_processed_stories_id, rows= fetch_size)
        stories.extend( fetched_stories)
        if len( fetched_stories) < fetch_size:
            break

        last_processed_stories_id = stories[-1]['processed_stories_id']

    print (json.dumps(stories))
