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
import musicfiletools

executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)


from musicfiletools import tagging
from musicfiletools.coverupdater import CoverUpdater
from musicfiletools.config import IGNOREDIRS

def process_directory(directory, update_music_files=False):
    
    p = Path(directory)
    
    for d in p.glob("**/*"):
        if d.is_dir():
            if d.name in IGNOREDIRS:
                continue
            
            logging.info("processing %s",d)
            data = tagging.albumdata_from_dir(d)
            if data is not None and "mbid" in data:
                cu = CoverUpdater(data["mbid"],d)
                executor.submit(cu.run)
                #cu.run()
            if data != {} and update_music_files:
                tagging.writeback_album_data(d, data)
            

if __name__ == '__main__':
    
    directory="."
    
    update_music_files = False
    
    if len(sys.argv) > 1:
        if "-v" in sys.argv:
            logging.basicConfig(format='%(levelname)s: %(name)s - %(message)s',
                                level=logging.DEBUG)
            loggingconf=True
            logging.info("enabled verbose logging")
        else:
            logging.basicConfig(format='%(levelname)s: %(name)s - %(message)s',
                        level=logging.INFO)
            
        if "-u" in sys.argv:
            logging.info("writing back album information to music files")
            update_music_files = True
            
        for a in sys.argv:
            if Path(a).is_dir():
                directory=a
                
    p=Path(directory).absolute()
    logging.info("Extracting album information from %s",p)
    process_directory(p)
    
