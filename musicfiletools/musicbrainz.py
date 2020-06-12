'''
Copyright (c) 2019 Modul 9/HiFiBerry

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import musicbrainzngs
import logging
from Cryptodome.SelfTest.Signature.test_dss import res

musicbrainzngs.set_useragent("hifiberry tagger","2020")
musicbrainzngs.set_hostname("musicbrainz.hifiberry.com")

from expiringdict import ExpiringDict

cache = ExpiringDict(max_len=100, max_age_seconds=600)


def add_query_str(query, searchfield, key, data):
    if key in data and data[key] is not None:
        if len(query)>0:
            query=query+" AND "
        
        value = data[key]
        if " " in value:
            value='"' + value +'"' 
        query = query + searchfield +":"+value
        
    return query

def artist_data(artistname):
    try:
        data = musicbrainzngs.search_artists(query=artistname, limit=1, strict=False)
        if len(data["artist-list"]) >= 1:
            return data["artist-list"][0]
    except Exception as e:
        logging.warning("error while loading musicbrainz data for %s: %s",
                        artistname, e)
        
        
        
def album_data(data):
    q = ""
    if data.get("albumArtist") is not None:
        q = add_query_str(q, "artistname", "albumArtist", data)
    else:
        q = add_query_str(q, "artistname", "artist", data)
    
    q=add_query_str(q, "release", "album", data)

    key="album/"+q
    if key in cache:
        return cache.get(key)
    else:
        res = musicbrainzngs.search_releases(q, 1)
        cache[key]=res
        return res


def album_data_from_song(data):
    
    q = ""
    if data.get("albumArtist") is not None:
        q = add_query_str(q, "artistname", "albumArtist", data)
    else:
        q = add_query_str(q, "artistname", "artist", data)
    
    q=add_query_str(q, "release", "album", data)
    
    key="recording/"+q
    if key in cache:
        return cache.get(key)
    else:
        res = musicbrainzngs.search_recordings(q, 1)
        cache[key]=res
        return res
    
    
