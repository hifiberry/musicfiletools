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

from musicfiletools.musicdb import get_artist_cover
from musicfiletools.httphelper import retrieve_url
from musicfiletools.image import save_image

# make sure, updater runs only once for each artist
processing=set()

class ArtistUpdater(Thread):
    
    def __init__(self, name, mbid, directory, max_dim=1000):
        super().__init__()
        self.name = name
        self.mbid = mbid
        self.directory = directory
        self.max_dim = max_dim
    
    def run(self):
        global processing
        if self.name in processing:
            logging.debug("artist %s already processing",self.name)
            return 
        else:
            processing.add(self.name)
        
        logging.debug("retrieving artist picture for %s, storing to %s",
                      self.name,
                      self.directory)
        
        # Check local files
        artistfile=Path(self.directory,"{}-thumb.jpg".format(self.name.lower()))
        if artistfile.exists():
            return
        
        picurl=get_artist_cover(self.name, self.mbid)
        if picurl is not None:
            resp = retrieve_url(picurl)
            if resp.ok:
                try:
                    save_image(resp.content, self.max_dim, self.max_dim, artistfile)
                    logging.info("created %s", artistfile)
                    return True
                except Exception as e:
                    logging.exception(e)
            