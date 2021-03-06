#!/usr/bin/env python3

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
import json
import subprocess

import mutagen
from mutagen.id3 import PictureType
from mutagen.mp4 import AtomDataType

from musicfiletools.config import MUSICEXT

stats = {}

processed = {}


def cover(directory):
    p = Path(directory)
    ct = Path(directory, "cover-thumb.jpg")
    if not(ct.exists()):
        ct = None
        
    for f in p.glob("*.???*"):
        if f.suffix in [".jpg",".jpeg",".png",".gif"]:
            if f.stem.lower() in ["folder", "front", "albumart","cover"]:
                return f, ct
                
    return None, ct

def fileid(path):
    # use path/mtime combination as a unique id for a patch
    return "{}/{}".format(path.resolve(),path.stat().st_mtime)


def apic_to_file(apic, directory, filebase="cover"):
    if apic.type in [PictureType.COVER_FRONT, PictureType.OTHER]: 
        cover = None
        if apic.mime.lower() in ["image/jpeg", "image/jpg"]:
            cover = Path(directory, filebase+".jpg")
        elif apic.mime.lower() == "image/png":
            cover = Path(directory, filebase+".png")
        elif apic.mime.lower() == "image/gif":
            cover = Path(directory, filebase+".gif")
        
        if cover is not None:
            with cover.open("wb") as f:
                f.write(apic.data)
                logging.info(" created %s", cover)
                return True
    
    return False

def covr_to_file(covr, directory, filebase="cover"):
    coverfile = None
    if covr.imageformat == AtomDataType.JPEG:
        coverfile = Path(directory, filebase+".jpg")
    elif covr.imageformat == AtomDataType.PNG:
        coverfile = Path(directory, filebase+".png")
    elif covr.imageformat == AtomDataType.GIF:
        coverfile = Path(directory, filebase+".gif")
        
    if coverfile is not None:
        with coverfile.open("wb") as f:
            f.write(covr)
            logging.info(" created %s", coverfile)
            return True
    
    return False


def picture_to_file(picture, directory, filebase="cover"):
    coverfile = None
    if picture.mime.lower() == "image/jpeg" or picture.mime.lower() == "image/jpg":
        coverfile = Path(directory, filebase+".jpg")
    elif picture.mime.lower() == "image/png":
        coverfile = Path(directory, filebase+".png")
    elif picture.mime.lower() == "image/gif":
        coverfile = Path(directory, filebase+".gif")
        
    if coverfile is not None:
        with coverfile.open("wb") as f:
            f.write(picture.data)
            logging.info(" created %s", coverfile)
            return True
    
    return False


def album_data(mutagenFile):
    md = {}
    logging.warn(mutagenFile.keys())
    
    if "TALB" in mutagenFile:
        md["album"]=mutagenFile.get("TALB")
        
    if "TPE2" in mutagenFile:
        md["albumartist"]=mutagenFile.get("TPE2")
    elif "TPE1" in mutagenFile:
        md["albumartist"]=mutagenFile.get("TPE1")
    
    return md


def create_cover_thumb(cover):
    cf = Path(cover)
    thumbfile = Path(cf.parents[0],"cover-thumb.jpg")
    subprocess.run(["convert", str(cover), "-resize", "400x400>", "-quality", "70%", str(thumbfile)])
    
    if not(str(cover).endswith("over.jpg")):
        coverfile = Path(cf.parents[0],"cover.jpg")
        subprocess.run(["convert", str(cover), "-resize", "1000x1000>", "-quality", "70%", str(coverfile)])
           
    

def extract_cover_from_files(directory):
    global processed
    
    p = Path(directory)
    for f in p.glob("*.???*"):
        if f.suffix.lower() in MUSICEXT:
            try:
                
                if fileid(f) in processed:
                    logging.debug("processed %s already",f)
                    continue
                else:
                    logging.debug("processing %s",f)
                
                songfile = mutagen.File(f)
                coverFound=False
                logging.debug(" %s", songfile.keys())
                
                for k in songfile.keys():
                    if k.startswith("APIC:"):
                        apic = songfile.get(k)
                        coverFound=apic_to_file(apic, p)
                    
                if "covr" in songfile.keys():
                    cover = songfile.get("covr")[0]
                    coverFound=covr_to_file(cover, p)
                    
                try:
                    pic = songfile.pictures[0]
                    coverFound=picture_to_file(pic, p)
                except:
                    # This is normal as this will only work
                    # with FLAC files
                    pass

                processed[fileid(f)]=1
                
                if coverFound:
                    return True
                    
                ## logging.info("data: %s ",album_data(songfile))
                    
            except Exception as _e:
                logging.warning("can't handle %s", f)
                
            
    return False
        
    
def has_music(directory):
    p = Path(directory)
    for f in p.glob("*.???*"):
        if f.suffix.lower() in MUSICEXT:
            return True
        
    return False
        
        
def process_directory(directory, depth=30):
    
    global stats
    found = False
    
    p = Path(directory)
    
    if depth>0:
        for d in p.glob("*"):
            if d.is_dir():
                if process_directory(d, depth-1):
                    found = True 
                
    if has_music(p):
        logging.info("%s",p)
        
        c,c_thumb = cover(p)
        if c is None:
            logging.debug("no cover found")
            if extract_cover_from_files(p):
                stats["coversExtracted"]=stats.get("coversExtracted",0)+1
                found = True
                c,c_thumb = cover(p)
                logging.info("got cover for %s",p)
                
        if c_thumb is None and c is not None:
            logging.info("creating thumbnail for %s", c)
            create_cover_thumb(c)
            found=True
        else:
            logging.debug("cover: %s", c)
            
    return found
    


if __name__ == '__main__':
    
    directory="."
    retcode=False
    loggingconf=False
    ignoreGetCovers=False
    
    if len(sys.argv) > 1:
        if "-v" in sys.argv:
            logging.basicConfig(format='%(levelname)s: %(name)s - %(message)s',
                                level=logging.DEBUG)
            loggingconf=True
            logging.info("enabled verbose logging")
            sys.argv.remove("-v")
        else:
            logging.basicConfig(format='%(levelname)s: %(name)s - %(message)s',
                        level=logging.INFO)
            
        if "-x" in sys.argv:
            logging.info("return code 0 only if new covers were found")
            retcode=True
            sys.argv.remove("-x")
            
        if "-i" in sys.argv:
            logging.info("ignoring getcovers.log")
            ignoreGetCovers=True
            sys.argv.remove("-i")
            
            
    else:
        print("command line arguments missing")
        sys.exit(1)
            
            
    p=Path(sys.argv[1]).absolute()
    
    
    processedFile=Path(p,"getcovers.log")
    if processedFile.exists() and not ignoreGetCovers:
        try:
            with open(processedFile) as json_file:
                processed = json.load(json_file)
                logging.info("loaded processed files from %s",processedFile)
        except Exception as e:
            logging.warning(e)
            processed = {}
    
    logging.info("Extracting covers from %s",p)
    found = process_directory(p)
    
    try:
        with open(processedFile, 'w') as outfile:
            json.dump(processed, outfile)
            logging.info("saved processed files to %s",processedFile)
    except:
        processed = {}
            
    
    logging.info("Stats: %s", stats)
    
    # if "-x" is set, return with code 0 only if covers are found
    if retcode and not(found):
        sys.exit(1)
    
    