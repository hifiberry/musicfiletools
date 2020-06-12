'''
Copyright (c) 2020 Modul 9/HiFiBerry

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

import json 
import logging 

from urllib.request import urlopen


APIKEY="749a8fca4f2d3b0462b287820ad6ab06"

def get_cover(mbid):
    url = "http://webservice.fanart.tv/v3/music/{}?api_key={}".format(mbid, APIKEY)
    try:
        data = json.loads(urlopen(url).read())

        # Try to find the album cover first
        try:
            coverurl = data["albums"][mbid]["albumcover"]["url"]
            logging.debug("found album cover on fanart.tv")
            return coverurl
        except KeyError:
            logging.debug("found no album cover on fanart.tv")
            
    except Exception as e:
        logging.debug("couldn't retrieve data from fanart.tv (%s)",e)
        
        
def get_artist_cover(artist_mbid):
    url = "http://webservice.fanart.tv/v3/music/{}?api_key={}".format(artist_mbid, APIKEY)
    try:
        data = json.loads(urlopen(url).read())

        # Try to find the album cover first
        try:
            coverurl = data["artistthumb"][0]["url"]
            logging.debug("found artist picture on fanart.tv")
            return coverurl
        except KeyError:            
            logging.debug("found no artist picture on fanart.tv")
        
        try:
            coverurl = data["artistbackground"][0]["url"]
            logging.debug("found artistbackground on fanart.tv")
            return coverurl
        except KeyError:            
            logging.debug("found no artist background on fanart.tv")

            
    except Exception as e:
        logging.debug("couldn't retrieve data from fanart.tv (%s)",e)
