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

import sys
import logging
from pathlib import Path

import mutagen
from mutagen.id3 import PictureType
from mutagen.mp4 import AtomDataType

MUSICEXT = [".mp3",".flac",".ogg",".m4a"]

stats = {}


def cover(directory):
    p = Path(directory)
    for f in p.glob("*.???*"):
        if f.suffix in [".jpg",".jpeg",".png"]:
            if f.stem.lower() in ["folder", "front", "albumart","cover"]:
                return f
    
    return None


def apicToFile(apic, directory, filebase="cover"):
    if apic.type in [PictureType.COVER_FRONT, PictureType.OTHER]: 
        cover = None
        if apic.mime.lower()=="image/jpeg":
            cover = Path(directory, filebase+".jpg")
        elif apic.mime.lower() == "image/png":
            cover = Path(directory, filebase+".png")
        
        if cover is not None:
            with cover.open("wb") as f:
                f.write(apic.data)
                logging.info(" created %s", cover)
                return True
    
    return False

def covrToFile(covr, directory, filebase="cover"):
    coverfile = None
    if covr.imageformat == AtomDataType.JPEG:
        coverfile = Path(directory, filebase+".jpg")
    elif covr.imageformat == AtomDataType.PNG:
        coverfile = Path(directory, filebase+".png")
        
    if coverfile is not None:
        with coverfile.open("wb") as f:
            f.write(covr)
            logging.info(" created %s", coverfile)
            return True
    
    return False


def pictureToFile(picture, directory, filebase="cover"):
    coverfile = None
    if picture.mime.lower() == "image/jpeg":
        coverfile = Path(directory, filebase+".jpg")
    elif picture.mime.lower() == "image/png":
        coverfile = Path(directory, filebase+".png")
        
    if coverfile is not None:
        with coverfile.open("wb") as f:
            f.write(picture.data)
            logging.info(" created %s", coverfile)
            return True
    
    return False

def extractCoverFromFiles(directory):
    p = Path(directory)
    for f in p.glob("*.???*"):
        if f.suffix.lower() in MUSICEXT:
            try:
                songfile = mutagen.File(f)
                logging.debug(" %s", songfile.keys())
                
                if "APIC:" in songfile.keys():
                    apic = songfile.get("APIC:")
                    if apicToFile(apic, p):
                        return True
                    
                if "covr" in songfile.keys():
                    cover = songfile.get("covr")[0]
                    if covrToFile(cover, p):
                        return True
                    
                try:
                    pic = songfile.pictures[0]
                    if pictureToFile(pic, p):
                        return True
                    
                except:
                    pass
                    
            except Exception as _e:
                logging.warning("can't handle %s", f)
                
            
    return False
        
    
def hasMusic(directory):
    p = Path(directory)
    for f in p.glob("*.???*"):
        if f.suffix.lower() in MUSICEXT:
            return True
        
    return False
        
        
def processDirectory(directory, depth=30):
    
    global stats
    
    p = Path(directory)
    
    if depth>0:
        for d in p.glob("*"):
            if d.is_dir():
                processDirectory(d, depth-1)
                
    if hasMusic(p):
        logging.debug("found music in %s",p)
        
        c = cover(p)
        if c is None:
            logging.debug("no cover found")
            if extractCoverFromFiles(p):
                stats["coversExtracted"]=stats.get("coversExtracted",0)+1
                
        else:
            logging.debug("cover: %s", c)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if "-v" in sys.argv:
            logging.basicConfig(format='%(levelname)s: %(name)s - %(message)s',
                                level=logging.DEBUG)
            logging.debug("enabled verbose logging")
    else:
        logging.basicConfig(format='%(levelname)s: %(name)s - %(message)s',
                            level=logging.INFO)

    processDirectory("Z:/65daysofstatic", 4)
    processDirectory("Z:/", 4)
    
    logging.info("Stats: %s", stats)