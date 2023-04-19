# -*- coding: utf-8 -*-

import yaml
import spotipy
import warnings
import requests
from math import ceil
from lxml import html


def grouped_index(length, group_length):
    """
    Constructs a generator of indices for grouping an item of *length* into
    groups of *group_length* size. If *group_length* is not a divisor of 
    *length*, the last group will be the remainder.
    For example:
        >>> for i1, i2 in grouped_index(10, 3):
                print(i1, i2)
        ...
        <<< 0 2
            3 5
            6 8
            9 10
    """
    for i in range(ceil(length / group_length)):
        i1 = i * group_length
        i2 = min(group_length*(i+1)-1, length)
        yield i1, i2


def get_playlist(spotify, config, fields=""):
    # Maximum limit of 100 items per request neccitates this function
    response = spotify.playlist_items(config["playlist_id"], fields=fields,
                                      market=config["market"])
    tracks = response["items"]
    while response["next"]:
        response = spotify.next(response)
        tracks.extend(response["items"])
    return tracks


def get_new_releases(spotify, config, limit=0):
    """
    The new_releases endpoint of Spotify Web API does NOT differentiate between
    songs created in a country, and songs appearing in a country. The best bet
    of obtaining all songs released in a country is by scraping Every Noise at
    Once New Releases using requests and xpath.
    """
    page = requests.get(config["scraping"]["url"])
    tree = html.fromstring(page.content)
    uris = tree.xpath(config["scraping"]["xpath"])
    uris = list(map(str, uris))
    if int(config["track_limit"]):
        return uris[:limit]
    else:
        return uris


def generate_uris(tracks):
    # Cannot be generated inline due to NoneType hidden tracks
    # Cannot replicate this bug, but it appears in some playlists
    uris = []
    for track in tracks:
        try:
            uris.append(track["track"]["uri"])
        except TypeError:
            warnings.warn("Invalid track URI")
    return uris


def clear_playlist(spotify, config):
    """
    WARNING: This function is sometimes incapable of clearing due to a
    Spotify API bug, in which some tracks cannot be removed by their URI.
    Pulling the URI from a song from an alternative version of some collection
    (e.g. extended album) produces the URI of the non-alternative version,
    which prevents it from being removed correctly.
    Example: 'Boring Angel' on 'R Plus Seven (Bonus Track Version)'
        spotify:album:6MEswIpaIGVN8M68FGr550
    """
    # Retrieves only the URI by delving into object in fields parameter
    # Only URI is needed and this saves bandwidth & computation time
    tracks = get_playlist(spotify, config, fields="items(track(uri)),next")
    uris = generate_uris(tracks)
    # Only accepts 100 removals at a time
    for i1, i2 in grouped_index(len(tracks), 100):
        spotify.playlist_remove_all_occurrences_of_items(
            config["playlist_id"], uris[i1:i2])


def get_first_tracks(spotify, config, uris):
    tracks = []
    for i1, i2 in grouped_index(len(uris), 20):
        response = spotify.albums(uris[i1:i2], market=config["market"])
        for album in response["albums"]:
            tracks.append(album["tracks"]["items"][0]["uri"])
    return tracks


if __name__ == "__main__":
    with open("config.yaml") as file:
        config = yaml.load(file.read(), yaml.BaseLoader)
    scope = "playlist-modify-private,playlist-modify-public"
    oauth = spotipy.SpotifyOAuth(**config["credentials"], scope=scope)
    spotify = spotipy.Spotify(client_credentials_manager=oauth)
    releases = get_new_releases(spotify, config)
    tracks = get_first_tracks(spotify, config, releases)
    clear_playlist(spotify, config)
    for i1, i2 in grouped_index(len(tracks), 100):
        spotify.playlist_add_items(config["playlist_id"], tracks[i1:i2])
