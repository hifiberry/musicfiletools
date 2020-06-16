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

import cv2

# Load the cascade



def process_directory(directory, update_music_files=False):

    dirs = ["/usr/share/OpenCV/haarcascades"]
    try:
        dirs.append(cv2.data.haarcascades)
    except:
        pass
    
    for d in dirs:
        face_cascade = cv2.CascadeClassifier(d + '/haarcascade_frontalface_default.xml')
        if not(face_cascade.empty()):
            break
        
    if face_cascade.empty():
        logging.error("couldn't load face cascade")
        return
    
    p = Path(directory)
    
    for f in p.glob("**/*"):
        if f.suffix in [".jpg",".jpeg",".png"]:
            
            facesfile=f.with_suffix(".faces")
            if facesfile.exists():
                logging.debug("won't process %s, faces file already exists", f)
                continue
            
            img = cv2.imread(str(f),cv2.IMREAD_GRAYSCALE)
            if img is None:
                logging.info("couldn't read %s",f)
                continue
            else:
                logging.info("processing %s",f)

            # Detect faces
            faces = face_cascade.detectMultiScale(img, 1.1, 4)
            
            # Write to JSON
            fl = []
            minx=100000
            miny=100000
            maxx=0
            maxy=0
            for f in faces:
                x1=int(f[0])
                y1=int(f[1])
                x2=x1+int(f[2])
                y2=y1+int(f[3])
                
                if x1<minx:
                    minx=x1
                if x2>maxx:
                    maxx=x2
                if y1<miny:
                    miny=y1
                if y2>maxy:
                    maxy=y2
                
                fl.append({"x1":x1,
                            "y1":y1,
                            "x2":x2,
                            "y2":y2})
            
            try:
                with open(facesfile, 'w') as outfile:
                    res={"faces":fl}
                    if len(faces)>0:
                        res["focalpoint"]={"x":minx+(maxx-minx)/2,
                                           "y":miny+(maxy-miny)/2}
                        res["bounds"]={"x1": minx,
                                       "y1": miny,
                                       "x2": maxx,
                                       "y2": maxy }
                        logging.debug("%s",res)
                    json.dump({"faces":res}, outfile)
            except Exception as _e:
                logging.error("couldn't write to %s",facesfile)
            

if __name__ == '__main__':
    
    update_music_files = False
    
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
    else:
        print("command line argument missing")
        sys.exit(1)
                            
    p=Path(sys.argv[1]).absolute()
    logging.info("Detecting faces in %s",p)
    process_directory(p, update_music_files=update_music_files)
    
