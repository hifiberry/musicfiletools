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
import json
import shutil

def get_artist_picture(artist,albumdir):
    
    checkdirs=list(albumdir.parents)
    checkdirs.insert(0,albumdir)
    for d in checkdirs:
        for f in Path(d).glob("artist.*"):
            if f.suffix in [".jpg","jpeg",".png"]:
                return f
    
    return None
        

def process_directory(directory, artistdir):
    
    p = Path(directory)
    picdir=Path(artistdir)
    
    for d in p.glob("**/album.json"):
        try:    
            with open(d) as json_file:
                data = json.load(json_file)
                logging.info("%s: %s",d, data)
                aa = data.get("albumArtist","")
                if len(aa)>0:
                    filebase=aa.lower().replace("/","-")
                    if len(list(picdir.glob(filebase+".*")))>0:
                        logging.debug("artist image for %s exists",aa)
                    else:
                        img=get_artist_picture(aa,d.parents[0])
                        if img is not None:
                            logging.info("using %s for %s",img, aa)
                            dst=Path(artistdir,filebase+img.suffix)
                            shutil.copy(img, dst)
                            logging.info("copied")

        except:
            pass            

if __name__ == '__main__':
    
    directory="."
    
    update_music_files = False
    
    try:
        if "-v" in sys.argv:
            sys.argv.remove("-v")
            logging.basicConfig(format='%(levelname)s: %(name)s - %(message)s',
                                level=logging.DEBUG)
            loggingconf=True
            logging.info("enabled verbose logging")
        else:
            logging.basicConfig(format='%(levelname)s: %(name)s - %(message)s',
                        level=logging.INFO)
        
        musicdir=Path(sys.argv[1]).absolute()
        artistdir=Path(sys.argv[2]).absolute()
    except:
        print("missing command line argument")
        sys.exit(1)
        
    logging.info("Extracting album information from %s, artist directory %s",musicdir, artistdir)
    process_directory(musicdir, artistdir)
