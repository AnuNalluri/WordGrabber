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

    fieldnames = [
        u'media_id',
        u'url',
        u'name'
    ]

    while True:
        params = { 'last_media_id': last_media_id, 'rows': rows, 'name': media_name[media_idx], 'key': MY_API_KEY }
        print ("start:{} rows:{}".format( last_media_id, rows))
        r = requests.get( 'https://api.mediacloud.org/api/v2/media/list', params = params, headers = { 'Accept': 'application/json'} )
        data = r.json()

        if not len(data):

            # If there are more media_names, write what we have to csv file and continue
            path_name = './csv_storage/media.csv'
            with open( path_name, 'a', newline="") as csvfile:
                print ("\nOpened file: Dumping media source content for {}\n".format(media_name[media_idx]))

                # Flush media buffer to csv file
                cwriter = csv.DictWriter( csvfile, fieldnames, extrasaction='ignore')

                if not os.path.getsize(path_name):
                    cwriter.writeheader()

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

def get_outlinks_from_media(num_stories=200):
    """
    Args: num_stories: max number of out-linked stories we want to grab from each media_name in media.csv

    Gets the stories hyperlinked to by media sources present in our media.csv file.
    """
    def write_to_csv(media=[]):
        # print (media)
        fieldnames = [
            u'stories_id',
            u'url',
            u'media_name',
            u'media_id',
            u'title',
            u'publish_date',
            u'snapshots_id',
            u'foci_id',
            u'timespans_id',
            u'inlink_count',
            u'outlink_count',
            u'foci',
            u'facebook_share_count'
        ]

        path_name = './csv_storage/media_' + media_name + '_outlinks.csv'
        with open(path_name, 'a', newline="") as csvfile:
            cwriter = csv.DictWriter( csvfile, fieldnames, extrasaction='ignore')

            if not os.path.getsize(path_name):
                cwriter.writeheader()

            cwriter.writerows( media )

    with open('./csv_storage/media.csv', 'r', newline="") as fh:
        table = pd.read_csv(fh, header=0)

    idx = 0

    hoaxy_media_lst = ["americannewsx", "21stcenturywire", "70news", "abcnews.com.co", "activistpost", "addictinginfo", "amplifyingglass", "anonews", "beforeitsnews", "bigamericannews",  "bipartisanreport", "bluenationreview", "breitbart", "burrardstreetjournal", "callthecops", "christiantimes", "christwire", "chronicle", "civictribune",
    "clickhole", "coasttocoastam", "collective-evolution", "consciouslifenews", "conservativeoutfitters", "countdowntozerotime", "counterpsyops", "creambmp", "dailybuzzlive", "dailycurrant", "dailynewsbin", "dcclothesline", "demyx", "denverguardian", "derfmagazine", "disclose", "duffelblog",  "duhprogressive", "empireherald", "empirenews", "empiresports", "mediamass", "endingthefed", "enduringvision", "flyheight",
    "fprnradio", "freewoodpost", "geoengineeringwatch", "globalassociatednews", "globalresearch", "gomerblog", "govtslaves", "gulagbound", "hangthebankers", "humansarefree", "huzlers", "ifyouonlynews", "infowars", "intellihub", "itaglive", "jonesreport", "lewrockwell",  "liberalamerica", "libertymovementradio", "libertytalk", "libertyvideos", "lightlybraisedturnip", "nationalreport", "naturalnews", "ncscooper",
    "newsbiscuit", "newslo", "newsmutiny", "newswire-24",  "nodisinfo", "now8news", "nowtheendbegins",  "occupydemocrats",  "other98",  "pakalertpress", "politicalblindspot", "politicalears", "politicops", "politicususa", "prisonplanet", "react365", "realfarmacy", "realnewsrightnow", "redflagnews", "redstate", "rilenews", "rockcitytimes", "satiratribune", "stuppid", "theblaze",
    "thebostontribune", "thedailysheeple", "thedcgazette", "thefreethoughtproject", "thelapine", "thenewsnerd", "theonion", "theracketreport", "therundownlive", "thespoof", "theuspatriot", "truthfrequencyradio", "twitchy", "unconfirmedsources", "USAToday.com.co", "usuncut", "veteranstoday", "wakingupwisconsin", "weeklyworldnews", "wideawakeamerica", "winningdemocrats", "witscience", "wnd", "worldnewsdailyreport", "worldtruth",
    "yournewswire", "dcleaks.com", "russiatoday"]

    table['mod_name'] = table['name'].str.lower()
    table['mod_name'] = table['mod_name'].str.replace(' ', '')

    media_set = set()
    for src in table['mod_name']:
        for hoaxy_src in hoaxy_media_lst:
            if hoaxy_src in src:
                media_set.add(src)
                break

    ids = table[table['mod_name'].isin(media_set)]

    while idx < ids.shape[0]:
        media_id = ids['media_id'].iloc[idx]
        media_name = ids['name'].iloc[idx].replace(' ', '_')
        stories = []


        params = {
            # 'last_processed_stories_id': start,
            'limit': num_stories,
            'link_from_media_id': '{}'.format(str(media_id)),
            'key': MY_API_KEY
        }
        print ("Fetching {} stories linking from {}".format(str(num_stories), str(media_name)))
        r = requests.get( 'https://api.mediacloud.org/api/v2/topics/1404/stories/list', params = params, headers = { 'Accept': 'application/json'})
        data = r.json()
        print (len(data['stories']))
        stories.extend(data['stories'])


        write_to_csv(stories)

        idx += 1

# def get_outlinks_from_media(media_name, num_stories=1000):
#     """
#     Args: media_name: media_name for which we want out-linked stories (from pre-existing stories)
#           num_stories: max number of out-linked stories we want to grab from each media_name
#
#     Gets the stories referenced by media_name present in our media.csv file.
#     """
#
#     with open('./csv_storage/media.csv', 'r', newline="") as fh:
#         table = pd.read_csv(fh, header=0)
#
#     media_id = table[table['name'] == media_name]['media_id'].iloc[0]
#     media_name = media_name.replace(' ', '_')
#     stories = []
#
#     def write_to_csv(media=[]):
#         # print (media)
#         fieldnames = [
#             u'stories_id',
#             u'url',
#             u'media_name',
#             u'media_id',
#             u'title',
#             u'publish_date',
#             u'snapshots_id',
#             u'foci_id',
#             u'timespans_id',
#             u'inlink_count',
#             u'outlink_count',
#             u'foci',
#             u'facebook_share_count'
#         ]
#
#         path_name = './csv_storage/media_' + media_name + '_outlinks.csv'
#         with open(path_name, 'w', newline="") as csvfile:
#             cwriter = csv.DictWriter( csvfile, fieldnames, extrasaction='ignore')
#
#             if not os.path.getsize(path_name):
#                 cwriter.writeheader()
#
#             cwriter.writerows( media )
#
#
#     params = {
#         # 'last_processed_stories_id': start,
#         'limit': num_stories,
#         'link_from_media_id': '{}'.format(str(media_id)),
#         'key': MY_API_KEY
#     }
#     # print (str(story_id) + '\n\n')
#     print ("Fetching {} stories linking from {}".format(str(num_stories), str(media_name)))
#     r = requests.get( 'https://api.mediacloud.org/api/v2/topics/1404/stories/list', params = params, headers = { 'Accept': 'application/json'})
#     data = r.json()
#     print (len(data['stories']))
#     stories.extend(data['stories'])
#
#
#     write_to_csv(stories)

def get_topics():
    params = {
        'name':'election',
        'key': MY_API_KEY,
        'limit': 1000
    }
    r = requests.get( 'https://api.mediacloud.org/api/v2/topics/list', params= params, headers = { 'Accept': 'application/json'})
    data = r.json()
    print (data)

def get_topic():
    params = {
        'key': MY_API_KEY
    }

    r = requests.get('https://api.mediacloud.org/api/v2/topics/single/1404', params = params, headers = { 'Accept': 'application/json'})
    print (r.json())
