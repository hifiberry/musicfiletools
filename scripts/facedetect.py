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
    
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    if (face_cascade.empty()):
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
            logging.info(faces)
            
            # Write to JSON
            try:
                with open(facesfile, 'w') as outfile:
                    json.dump({"faces":faces}, outfile)
            except:
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
    
