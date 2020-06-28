#!/usr/bin/env python3
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

import sys
import logging
from pathlib import Path
import concurrent.futures

from musicfiletools import tagging
from musicfiletools.coverupdater import CoverUpdater
from musicfiletools.artistupdater import ArtistUpdater
from musicfiletools.config import IGNOREDIRS

executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

class Notifier:
    
    def __init__(self):
        self.notifies = 0
        
    def notify_updated(self):
        self.notifies += 1
        
    def received_notifies(self):
        return self.notifies > 0
        
notifier = Notifier()
            

def process_directory(directory, 
                      update_music_files=False, 
                      get_covers=True,
                      artist_directory=None):
    
    p = Path(directory)
    
    for d in p.glob("**/*"):
        if d.is_dir():
            if d.name in IGNOREDIRS:
                continue
            
            logging.info("processing %s",d)
            data = tagging.albumdata_from_dir(d)
            if data is not None:
                if get_covers and "album_mbid" in data:
                    cu = CoverUpdater(data["album_mbid"],
                                      d,
                                     update_notifier=notifier)
                    executor.submit(cu.run)
                
                if artist_directory is not None and "albumArtist" in data:
                    try:
                        mbid=data["artist_mbids"][0]
                    except:
                        mbid=None
                        
                    au=ArtistUpdater(name=data["albumArtist"],
                                     mbid=mbid,
                                     directory=artist_directory,
                                     max_dim=500,
                                     update_notifier=notifier)
                    executor.submit(au.run)
                    
            if data != {} and update_music_files:
                tagging.writeback_album_data(d, data)
                


if __name__ == '__main__':
    
    directory="."
    
    update_music_files = False
    get_covers = False
    artist_directory=None
    retcode=False
    
    if "-v" in sys.argv:
        logging.basicConfig(format='%(levelname)s: %(name)s - %(message)s',
                            level=logging.DEBUG)
        loggingconf=True
        logging.info("enabled verbose logging")
        sys.argv.remove("-x")
    else:
        logging.basicConfig(format='%(levelname)s: %(name)s - %(message)s',
                    level=logging.INFO)

    if "-u" in sys.argv:
        logging.info("writing back album information to music files")
        update_music_files = True
        sys.argv.remove("-u")
        
    if "-c" in sys.argv:
        logging.info("retrieving covers from web services")
        get_covers = True
        sys.argv.remove("-c")
        
    if "-a" in sys.argv:
        logging.info("retrieving artist pictures from web services")
        artist_directory="/data/library/artists"
        sys.argv.remove("-a")
        
    if "-x" in sys.argv:
        logging.info("return code 0 only if new covers were found")
        retcode=True
        sys.argv.remove("-x")

    for a in sys.argv:
        if Path(a).is_dir():
            directory=a
                
    p=Path(directory).absolute()
    logging.info("Extracting album information from %s",p)
    process_directory(p, 
                      update_music_files=update_music_files, 
                      get_covers=get_covers,
                      artist_directory=artist_directory)
    
    executor.shutdown(wait=True)
    
    if notifier.received_notifies():
        logging.info("Downloaded %s files", notifier.notifies)
        sys.exit(0)
    else:
        if retcode:
            sys.exit(1)
        else:
            sys.exit(0)
    
