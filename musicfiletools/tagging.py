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
from pathlib import Path
import logging 
import sys
import json
import datetime

from functools import reduce

import mutagen
import mutagen.mp3
import mutagen.mp4
import mutagen.flac
import mutagen.id3

from musicfiletools import musicbrainz as mb
from musicfiletools.filesystem import music_files

def flatten(arr):
    if arr is None:
        return None
    else:
        try:
            return ", ".join(arr)
        except:
            return str(arr)
        
def get_date(s_date):
    date_patterns = ["%d-%m-%Y", "%Y-%m-%d", "%Y"]

    for pattern in date_patterns:
        try:
            return datetime.datetime.strptime(s_date, pattern).date()
        except:
            pass
    
def get_named_tag(d, tagnames):
    for t in tagnames:
        if t in d.keys():
            return flatten(d.get(t))
        

def get_tags(filename, ignore_errors=True):
    tags={}
    
    try:
        mgfile = mutagen.File(filename)
    
        tags["artist"]=get_named_tag(mgfile,["TPE1", "artist", "TPE2","\xa9ART"])
        tags["albumArtist"]=get_named_tag(mgfile,["TPE2","TPE1","ALBUMARTIST","ALBUM ARTIST","aART"])
        tags["title"]=get_named_tag(mgfile, ["TIT2","title","TIT1","\xa9nam"])
        tags["album"]=get_named_tag(mgfile, ["TALB", "album","\xa9alb"])
        tags["date"]=get_named_tag(mgfile,["TORY","TDRC","date","\xa9day"])
        tags["tracknumber"]=get_named_tag(mgfile,["TRCK","tracknumber","trkn"])
        
    except Exception as e:
        if not(ignore_errors): 
            raise e
    
    return tags



def fix_tags(data):
    if data is None:
        return 
    
    if "date" in data:
        data["date"]=get_date(data["date"])
    

def update_tags(filename, updatedict, ignore_errors=True):
    try:
        mgfile = mutagen.File(filename)
        t = type(mgfile)
        if t == mutagen.mp3.MP3:
            update_mp3_tags(mgfile, updatedict)
        elif t == mutagen.mp4.MP4:
            update_mp4_tags(mgfile, updatedict)
        elif t == mutagen.flac.FLAC:
            update_vorbis_tags(mgfile, updatedict)
        else:
            logging.error("don't know how to deal with type %s",t)
            sys.exit(1)
    except Exception as e:
        if not(ignore_errors): 
            raise e
        
        
def update_mp3_tags(mgfile, updatedict):
    tags = mgfile.tags
    
    if updatedict.get("albumArtist") is not None:
        tags.add(mutagen.id3.TPE2(text=updatedict.get("albumArtist")))
                 
    if updatedict.get("album") is not None:
        tags.add(mutagen.id3.TALB(text=updatedict.get("album")))
    
    if updatedict.get("date") is not None:
        tags.add(mutagen.id3.TDRC(text=updatedict.get("date").strftime("%Y")))
        
    if updatedict.get("album_mbid") is not None:
        tags.add(mutagen.id3.TXXX(text=updatedict.get("album_mbid"), desc="album_mbid"))
        
    tags.update_to_v24()
    
    mgfile.save()
    
    
def update_mp4_tags(mgfile, updatedict):
    tags = mgfile.tags
        
    if updatedict.get("albumArtist") is not None:
        tags["aART"]=updatedict.get("albumArtist")
                 
    if updatedict.get("album") is not None:
        tags["\xa9alb"]=updatedict.get("album")
    
    if updatedict.get("date") is not None:
        tags["\xa9day"]=updatedict.get("date").strftime("%Y")
        
        
    mgfile.save()
    
    
def update_vorbis_tags(mgfile, updatedict):
    tags = mgfile.tags
        
    if updatedict.get("albumArtist") is not None:
        tags["ALBUMARTIST"]=updatedict.get("albumArtist")
                 
    if updatedict.get("ALBUM") is not None:
        tags["ALBUM"]=updatedict.get("album")
    
    if updatedict.get("date") is not None:
        tags["DATE"]=updatedict.get("date").strftime("%Y")
        
    if updatedict.get("album_mbid") is not None:
        tags["ALBUMMBID"]=updatedict.get("album_mbid")

        
    mgfile.save()
    
    

def retrieve_album_data(data, overwrite=True):
    allDataOk = True
    for key in ["albumArtist", "date","coverUrl"]:
        if data.get(key) is None:
            allDataOk=False
            
    if allDataOk:
        return 
    
    album = mb.album_data(data)
    if album["release-count"]>0:
        album=album["release-list"][0]
    else:
        # TODO: try to get it from song
        pass
        
    if (overwrite and album.get("date") is not None) \
        or data.get("albumArtist") is None:
        try:
            artists = []
            
            for ac in album["artist-credit"]:
                artists.append(ac["artist"]["name"])
            if len(artists)>0:
                data["albumArtist"]=", ".join(artists)
        except:
            pass
        
    if (overwrite and album.get("date") is not None) \
        or data.get("date") is None:
        data["date"]=album.get("date")
        
    if overwrite or data.get("album_mbid") is None:
        data["album_mbid"]=album.get("id")
        
    for ac in album["artist-credit"]:
        artist_mbids = []
        artist_mbids.append(ac["artist"]["id"])
    data["artist_mbids"]=artist_mbids
        
        
def albumdata_from_file(musicfile, use_artist_if_no_albumartist = False, lookup_online=True, overwrite=True):
    tags = get_tags(musicfile)
    
    for k in ["album","artist"]:
        if tags.get(k) is None:
            return {}
        
    if lookup_online:
        try:
            retrieve_album_data(tags, overwrite)
        except:
            logging.warning("couldn't retrieve album data for %s", musicfile)

    if tags.get("albumArtist") is None:
        if use_artist_if_no_albumartist:
            albumArtist = tags["artist"]
        else:
            albumArtist = None
    else:
        albumArtist=tags["albumArtist"]
                
    return {"albumArtist": albumArtist, 
            "album": tags["album"], 
            "date": tags.get("date"), 
            "album_mbid": tags.get("album_mbid"),
            "artist_mbids": tags.get("artist_mbids")}
    
    
def find_common(dict1, dict2):
    if dict1 is None:
        return dict2
    elif dict2 is None:
        return dict1
    
    res={}
    for k in set(dict1.keys()).union(set(dict2.keys())):
        v1=dict1.get(k)
        v2=dict1.get(k)
        if v1==v2:
            res[k]=v1
        elif v1 is None:
            res[k]=v2
        elif v2 is None:
            res[k]=v2
        elif isinstance(v1, set) and v2 is not None:
            v1.add(v2)
            res[k] = v1
        else:
            res[k] = set(v1,v2)
            
    return res
    
def albumdata_from_dir(directory, use_only_json=False):
    try:    
        with open(Path(directory,"album.json")) as json_file:
            data = json.load(json_file)
    except:
        if not(use_only_json):
            files = music_files(directory)
            if Path(directory,"noalbum").exists():
                logging.debug("noalbum file exists, skipping")
                return {}
            
            data = reduce(find_common, map(albumdata_from_file,files), None)
            fix_tags(data)
            if data is not None and data.get("album_mbid") is not None:
                try:
                    if data["date"] is not None:
                        data["date"]=data["date"].strftime("%Y-%m-%d")
                    with open(Path(directory,"album.json"),"w") as json_file:
                        json.dump(data, json_file)
                except:
                    pass
            else:
                logging.warning("%s : no data",directory)
                try:
                    Path(directory,"noalbum").touch(exist_ok=True)
                except:
                    pass
        else:
            data={}
    
    return data


def writeback_album_data(directory, data):
    for f in music_files(directory):
        update_tags(f, data)
    
    
        
# dev code
def demo():
    from musicfiletools.coverupdater import CoverUpdater
    logging.basicConfig(format='%(levelname)s: %(name)s - %(message)s',
                            level=logging.INFO)
    
    
    demofiles = [
        "V:/JAY_Z/Reasonable_Doubt-1996/JAY-Z-Reasonable_Doubt-03-Brooklyn's_Finest.flac",
        "V:/65daysofstatic/Silent_Running-2011/65daysofstatic-Silent Running-01-Overture.flac",
        "V:/Vangelis/1995-Voices/09 Dream In An Open Place.m4a",
        "V:/JAY_Z/Reasonable_Doubt-1996/JAY-Z-Reasonable_Doubt-04-Dead_Presidents_II.flac",
        "V:/JAY_Z/Jay-Z - The Dynasty Roc La Familia (2000) MP3/02_jay-z_-_change_the_game-satan.mp3",
        ]
    
    demodirs = [
        "V:/65daysofstatic/Silent_Running-2011",
        "V:/Vangelis/1995-Voices",
        "V:/Heather_Nova/Heather Nova - Oyster",
        "V:/JAY_Z/Reasonable_Doubt-1996",
        "V:/JAY_Z/Jay-Z - The Dynasty Roc La Familia (2000) MP3",
        ]
    
    for d in demodirs:
        logging.info("%s",d)
        data = albumdata_from_dir(d)
        if "album_mbid" in data:
            cu = CoverUpdater(data["album_mbid"],d)
            cu.run()
        writeback_album_data(d, data)
            
        
    sys.exit()
    
    for f in demofiles:
        tags = get_tags(f)
        logging.info("%s: %s", f, tags)
        
        newTags = tags.copy()
        retrieve_album_data(newTags)
        logging.info("data_orig: %s", tags)
        logging.info("data_new:  %s", newTags)
        
        if tags != newTags:
            logging.info("Changed")


# demo()