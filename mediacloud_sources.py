import mediacloud, json, datetime, csv
import pandas as pd
import requests
import os
import collections
import time
import pickle
import tldextract
from pathlib import Path
import pkg_resources
assert pkg_resources.get_distribution("requests").version >= '1.2.3'

#My API key given by Mediacloud
# MY_API_KEY = '0b048304d2f7398cb91248b7e07b3b153d32840c1a8c42ab4006f58aaa8a440a'
MY_API_KEY = '7d7ef4484ffc813fa68d616569a4f7e04577edeb8e7a9c4a7a4a0fc38d965a55'
#media_id's of some fake news sites
INFOWARS = 18515
RT = 305385
NAT_NEWS = 24030

# Python API client for accessing mediacloud Rest API
mc = mediacloud.MediaCloud(MY_API_KEY)

# Hoaxy Media List
hoaxy_media_lst = ["americannewsx", "21stcenturywire", "70news", "abcnews.com.co", "activistpost", "addictinginfo",
"amplifyingglass", "anonews", "beforeitsnews", "bigamericannews",  "bipartisanreport", "bluenationreview", "breitbart",
"burrardstreetjournal", "callthecops", "christiantimes", "christwire", "chronicle", "civictribune", "clickhole", "coasttocoastam",
"collective-evolution", "consciouslifenews", "conservativeoutfitters", "countdowntozerotime", "counterpsyops", "creambmp",
"dailybuzzlive", "dailycurrant", "dailynewsbin", "dcclothesline", "demyx", "denverguardian", "derfmagazine", "disclose", "duffelblog",
 "duhprogressive", "empireherald", "empirenews", "empiresports", "mediamass", "endingthefed", "enduringvision", "flyheight",
"fprnradio", "freewoodpost", "geoengineeringwatch", "globalassociatednews", "globalresearch", "gomerblog", "govtslaves", "gulagbound",
"hangthebankers", "humansarefree", "huzlers", "ifyouonlynews", "InfoWars", "intellihub", "itaglive", "jonesreport", "lewrockwell",
"liberalamerica", "libertymovementradio", "libertytalk", "libertyvideos", "lightlybraisedturnip", "nationalreport", "naturalnews", "ncscooper",
"newsbiscuit", "newslo", "newsmutiny", "newswire-24",  "nodisinfo", "now8news", "nowtheendbegins",  "occupydemocrats",  "other98",
"pakalertpress", "politicalblindspot", "politicalears", "politicops", "politicususa", "prisonplanet", "react365", "realfarmacy",
"realnewsrightnow", "redflagnews", "redstate", "rilenews", "rockcitytimes", "satiratribune", "stuppid", "theblaze",
"thebostontribune", "thedailysheeple", "thedcgazette", "thefreethoughtproject", "thelapine", "thenewsnerd", "theonion", "theracketreport",
"therundownlive", "thespoof", "theuspatriot", "truthfrequencyradio", "twitchy", "unconfirmedsources", "USAToday.com.co", "usuncut", "veteranstoday", "wakingupwisconsin", "weeklyworldnews", "wideawakeamerica", "winningdemocrats", "witscience", "wnd", "worldnewsdailyreport", "worldtruth",
"yournewswire", "dcleaks.com", "Russia Today"]


def list_direct_links():
    csv_files = os.listdir('./csv_storage')
    if 'media.csv' in csv_files:
        csv_files.remove('media.csv')
    if 'hyperlink_data' in csv_files:
        csv_files.remove('hyperlink_data')
    if '.DS_Store' in csv_files:
        csv_files.remove('.DS_Store')

    new_csvs = []
    for f in csv_files:
        f = 'csv_storage/' + str(f)
        new_csvs.append(f)

    return new_csvs



def list_recursive_links():
    csv_files = os.listdir('./csv_storage/hyperlink_data')
    if '.DS_Store' in csv_files:
        csv_files.remove('.DS_Store')

    new_csvs = []
    for f in csv_files:
        f = 'csv_storage/hyperlink_data/' + str(f)
        new_csvs.append(f)

    return new_csvs



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

        path_name = './csv_storage/media_' + media_name.replace(' ', '_') + '_outlinks.csv'
        with open(path_name, 'a', newline="") as csvfile:
            cwriter = csv.DictWriter( csvfile, fieldnames, extrasaction='ignore')

            if not os.path.getsize(path_name):
                cwriter.writeheader()

            cwriter.writerows( media )

    with open('./csv_storage/media.csv', 'r', newline="") as fh:
        table = pd.read_csv(fh, header=0)

    idx = 0

    # table['name'] = table['name'].str.replace(' ', '_')
    src_names, src_ids = table['name'].values, table['media_id'].values
    name_idx_map = {}

    node_cnt = 0
    for name in src_names:
        name_idx_map[name] = node_cnt
        node_cnt += 1

    node_lst = [node(src_name = src_names[i], src_id = src_ids[i]) for i in range(len(src_names))]


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
        media_name = ids['name'].iloc[idx]
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

        for story in stories:
            target_name = story['media_name']
            if target_name in name_idx_map:
                node_lst[name_idx_map[target_name]].inlinks_num += 1
            else:
                name_idx_map[target_name] = node_cnt
                node_lst.append(node(src_name = target_name, src_id = story['media_id']))
                node_lst[name_idx_map[target_name]].inlinks_num += 1
                node_cnt += 1

            try:
                node_lst[name_idx_map[media_name]].links[target_name] += 1
                node_lst[name_idx_map[media_name]].outlinks_num += 1
            except KeyError:
                print (media_name + ' not found in index map! continue')
                pass

        if len(stories):
            write_to_csv(stories)

        idx += 1

    return (name_idx_map, node_cnt, node_lst)



def recursive_story_search(name_idx_map, node_cnt, node_lst, num_stories=200, depth = 2, count = 2):
    """
    Args: num_stories: max number of out-linked stories we want to grab from each media_name
          ** topic_id: id to get stories associated with a particular topic --> not added yet
          depth: Specify recursive depth we want to spider for outlinks

    Gets the stories referenced by the stories we've already grabbed from media_name
    """
    if depth == 1:
        print ('Finished spidering')
        postprocess(node_lst)
        return

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

        path_name = './csv_storage/hyperlink_data/media_' + media_name.replace(' ', '_') + '_outlinks_' + 'degree' + str(count) + '.csv'
        with open(path_name, 'a', newline="") as csvfile:
            cwriter = csv.DictWriter( csvfile, fieldnames, extrasaction='ignore')

            if not os.path.getsize(path_name):
                cwriter.writeheader()

            cwriter.writerows( media )

    with open('./csv_storage/media.csv') as fh:
        table = pd.read_csv(fh, header=0)


    media_lst = table['name']
    crawled_links = set()

    for link in list_recursive_links():
        file_name_parts = link.split('/')[2].split('_')
        i = 1
        media_name = ""
        while i < len(file_name_parts) - 2:
            if i == 1:
                media_name += file_name_parts[i]
            else:
                media_name += ' ' + file_name_parts[i]
            i += 1
        crawled_links.add(media_name)


    for media_name in media_lst:
        if media_name in crawled_links:
            continue
        path_name = './csv_storage/media_' + media_name.replace(' ', '_') + '_outlinks.csv'
        try:
            with open(path_name, 'r', newline="") as fh:
                table = pd.read_csv(fh, header=0)

        except FileNotFoundError:
            continue

        idx = 0
        ids = table['stories_id']
        to_crawl_medias = table['media_name']

        while idx < ids.shape[0]:
            stories_id = ids.iloc[idx]
            to_crawl_media = to_crawl_medias.iloc[idx]
            stories = []


            params = {
                # 'last_processed_stories_id': start,
                'limit': num_stories,
                'link_from_stories_id': '{}'.format(str(stories_id)),
                'key': MY_API_KEY
            }
            # print (str(story_id) + '\n\n')
            print ("Fetching {} stories linking from {}'s story:{}'".format(str(num_stories), str(media_name), str(to_crawl_media)))
            r = requests.get( 'https://api.mediacloud.org/api/v2/topics/1404/stories/list', params = params, headers = { 'Accept': 'application/json'})
            data = r.json()
            print (len(data['stories']))
            stories.extend(data['stories'])

            for story in stories:
                target_name = story['media_name']
                if target_name in name_idx_map:
                    node_lst[name_idx_map[target_name]].inlinks_num += 1
                else:
                    name_idx_map[target_name] = node_cnt
                    node_lst.append(node(src_name = target_name, src_id = story['media_id']))
                    node_lst[name_idx_map[target_name]].inlinks_num += 1
                    node_cnt += 1
                try:
                    node_lst[name_idx_map[to_crawl_media]].links[target_name] += 1
                    node_lst[name_idx_map[to_crawl_media]].outlinks_num += 1
                except:
                    print (to_crawl_media + ' not found in index map! continue')
                    pass

            write_to_csv(stories)

            idx += 1

    recursive_story_search(name_idx_map, node_cnt, node_lst, depth = depth-1, count = count + 1)



def postprocess(node_lst):
    for media_info in node_lst:
        media_info.write_edges()

    return

def prune_non_fake():
    path_name = './edges.csv'
    with open(path_name, 'r', newline="") as fh:
        table = pd.read_csv(fh, header=0)

    fake_set = set(hoaxy_media_lst)
    pruned = table[(table['hostname'].isin(fake_set)) | (table['outlink'].isin(fake_set))]
    pruned.to_csv('./pruned_edges.csv', index=False)
    return

def modify_domain_name():
    path_name = './pruned/edges.csv'
    with open(path_name, 'r', newline="") as fh:
        table = pd.read_csv(fh, header=0)

    table['hostname'] = table['hostname'].str.replace(',', '')
    table['outlink'] = table['outlink'].str.replace(',', '')

    hosts, outlinks = table['hostname'].values, table['outlink'].values
    new_hosts = []
    for host in hosts:
        if len(host.split('.')) > 1:
            domain = tldextract.extract(host).domain
        else:
            domain = host
        new_hosts.append(domain)

    new_outlinks = []
    for outlink in outlinks:
        if len(outlink.split('.')) >  1:
            domain = tldextract.extract(outlink).domain
        else:
            domain = outlink
        new_outlinks.append(domain)

    table['hostname'] = pd.Series(new_hosts)
    table['outlink'] = pd.Series(new_outlinks)

    table.to_csv('./pruned/edges', index=False)


class node:


    def __init__(self, src_name = None, src_id = None):

        self.outlinks_num = 0
        self.inlinks_num = 0
        self.links = collections.Counter()
        self.id = src_id
        self.name = src_name

        for media_name in hoaxy_media_lst:
            self.links[media_name] = 0

    def dictify(self):

        node_dict = {
                     'outlinks_num': self.outlinks_num,
                     'inlinks_num': self.inlinks_num,
                     'id': self.id,
                     'links': self.links,
                     'hostname': self.name
                    }

        return node_dict

    def write_edges(self):
        fieldnames = [
            u'hostname',
            u'outlink',
            u'count'
        ]

        edges_dict_list = []

        for key in self.links:
            if self.links[key]:
                edges_dict = {'hostname': self.name, 'count': self.links[key], 'outlink': key}
                edges_dict_list.append(edges_dict)

        path_name = './edges.csv'

        with open(path_name, 'a', newline="") as csvfile:
            cwriter = csv.DictWriter( csvfile, fieldnames, extrasaction='ignore')

            if not os.path.getsize(path_name):
                cwriter.writeheader()

            cwriter.writerows( edges_dict_list )


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


REGISTRY = None

def check_requests():
    r = requests.get('https://api.mediacloud.org/api/v2/auth/profile', params ={'key': MY_API_KEY}, headers = { 'Accept': 'application/json'})
    print (r.json())
