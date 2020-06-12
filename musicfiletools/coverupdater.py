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

from threading import Thread
import logging
from pathlib import Path
from urllib.request import urlopen

import musicfiletools.fanarttv as fanarttv
import musicfiletools.coverartarchive as coverartarchive
from musicfiletools.coverarthandler import best_picture_size, best_picture_url, get_image_info, GOOD_ENOUGH_HEIGHT, GOOD_ENOUGH_WIDTH

MIN_WIDTH = 150
MIN_HEIGHT = 150

class CoverUpdater(Thread):
    
    def __init__(self, mbid, directory):
        super().__init__()
        self.mbid = mbid
        self.directory = directory
    
    def run(self):
        logging.debug("retrieving cover data for %s, storing to %s",
                      self.mbid,
                      self.directory)
        
        # Check local files
        existing_width = 0        
        existing_height = 0
        for f in ["cover.jpg","cover.png"]:
            coverfile=Path(self.directory,f)
            if coverfile.exists():
                with open(coverfile,"rb") as c:
                    _type, w, h = get_image_info(c.read())
                    if w >= GOOD_ENOUGH_WIDTH and h >= GOOD_ENOUGH_HEIGHT:
                        return
                    elif w>existing_width and h>existing_height:
                        existing_width=w
                        existing_height=h

        # Try fanart.tv first        
        try:
            best_cover = None
            
            coverurl = fanarttv.get_cover(self.mbid)
            if coverurl is not None:
                logging.debug("found cover on fanart.tv")
                best_cover = best_picture_url(self.mbid, coverurl)
            else:
                logging.debug("did not find cover on fanart.tv")
                

            # Now coverartarchive
            coverurl = coverartarchive.get_cover(self.mbid)
            if coverurl is not None:
                logging.debug("found cover on coverartarchive")
                best_cover = best_picture_url(self.mbid, coverurl)
            else:
                logging.debug("did not find cover on coverartarchive")
                
                
            (width, height) = best_picture_size(self.mbid)
            logging.debug("best cover: %sx%s: %s",width, height, best_cover)
            
            if width >= MIN_WIDTH and height >= MIN_HEIGHT and \
                width > existing_width and height > existing_height:
                logging.debug("storing cover")
                try:
                    self.update_cover(best_cover, width, height)                        
                except Exception as e:
                    logging.exception(e)
            else:
                logging.debug("no better cover found")
        
        except Exception as e:
            logging.warning("could not retrieve cover: %s",e)
            logging.exception(e)
            
            
            
    def update_cover(self, url, width, height, uuid="internal"):
        if not(url.startswith("http")):
            logging.debug("not an HTTP URL, ignoring")
            return False
        
        if url.endswith("png"):
            extension=".png"
        else:
            extension=".jpg"
            
        data = urlopen(url).read()
        cp = Path(self.directory,"cover"+extension)
        with open(cp,"wb") as coverfile:
            coverfile.write(data)
            logging.info("created %s", cp)
                
        return True
            