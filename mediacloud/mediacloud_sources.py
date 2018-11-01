import mediacloud
import json
import csv
import argparse
import pandas as pd
import requests
import os
import xml.etree.ElementTree as ET
import tldextract
from collections import defaultdict

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
"therundownlive", "thespoof", "theuspatriot", "truthfrequencyradio", "twitchy", "unconfirmedsources", "usatoday.com.co", "usuncut", "veteranstoday", "wakingupwisconsin", "weeklyworldnews", "wideawakeamerica", "winningdemocrats", "witscience", "wnd", "worldnewsdailyreport", "worldtruth",
"yournewswire", "dcleaks.com", "russia today"]


def get_media(chunk_size = 100, start_num=0, instance=0):
    """
    Args: chunk_size: max # of media sources that can be written per iteration

    Write the media_id, url, and names of known media sources in a CSV file
    """
    media = []
    start = start_num
    rows = chunk_size
    while True:
        params = { 'last_media_id': start, 'rows': rows, 'key': MY_API_KEY }
        print "start:{} rows:{}".format( start, rows)
        r = requests.get( 'https://api.mediacloud.org/api/v2/media/list', params = params, headers = { 'Accept': 'application/json'} )
        data = r.json()

        if len(data) == 0:
            break

        start += rows
        media.extend( data )
        write_to_csv(media, instance)
        media = []
        instance += 1

def write_to_csv(media, instance=0):

    fieldnames = [
        u'media_id',
        u'url',
        u'name'
    ]

    with open( './tmp/media.csv', 'a+') as csvfile:
        print "open"
        try:
            cwriter = csv.DictWriter( csvfile, fieldnames, extrasaction='ignore')
            if instance == 0:
                cwriter.writeheader()
            cwriter.writerows( media )
        except UnicodeEncodeError as ue:
            pass


def parse_XML():
    #Iterate through edges and add using a dict
    media_conns = defaultdict(list)
    tree = ET.parse('link-map-2345-213924.gexf')
    root = tree.getroot()
    with open('./tmp/media.csv', 'r') as fh:
        table = pd.read_csv(fh, header=0)
        for edge in root.iter("{http://www.gexf.net/1.2draft}edge"):
            src = map_id_to_name(table, int(edge.get('source')))
            target = map_id_to_name(table, int(edge.get('target')))
            weight = edge.get('weight')
            media_conns[src].append((target, weight))
    return media_conns

def postprocess_and_write_csv(media_conns):
    edges_dict = defaultdict(list)

    for src in media_conns:
        for outlink_tuple in media_conns[src]:
            edges_dict['hostname'].append(src)
            edges_dict['outlink'].append(outlink_tuple[0])
            edges_dict['count'].append(outlink_tuple[1])

    path_name = './edges.csv'
    keys = ["hostname", "outlink", "count"]
    with open(path_name, 'wb') as csvfile:
        cwriter = csv.writer(csvfile)
        cwriter.writerow(keys)
        cwriter.writerows(zip(*[edges_dict[key] for key in keys]))

def prune_non_fake():
    path_name = './edges.csv'
    with open(path_name, 'r') as fh:
        table = pd.read_csv(fh, header=0)

    fake_set = set(hoaxy_media_lst)
    pruned = table[(table['hostname'].str.lower().isin(fake_set)) | (table['outlink'].str.lower().isin(fake_set))]
    pruned.to_csv('./pruned/edges.csv', index=False)

def modify_domain_name():
    path_name = './pruned/edges.csv'
    with open(path_name, 'r') as fh:
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

def map_id_to_name(table, id):
    try:
        name = table[table['media_id'] == id]['name'].iloc[0]
    except IndexError as ie:
        return id
    return name


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

def check_requests():
    r = requests.get('https://api.mediacloud.org/api/v2/auth/profile', params ={'key': MY_API_KEY}, headers = { 'Accept': 'application/json'})
    print (r.json())

def main():
    # check_requests()
    # get_media(chunk_size=5, start_num=18265, instance=1)
    media_conns = parse_XML()
    postprocess_and_write_csv(media_conns)
    prune_non_fake()
    #modify_domain_name()

if __name__ == "__main__":
    main()
