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

import logging
import requests
import json
    
    
def get_cover(mbid):
    if mbid is None:
        return 

    try:
        url = "http://coverartarchive.org/release/{}/".format(mbid)
        data = requests.get(url)
        if data.status_code > 299:
            return None
        
        if data is not None:
            coverdata=json.loads(data.text)
        else:
            return None
        
        if coverdata is not None:
            for img in coverdata["images"]:
                if img["front"]:
                    url = img["image"]
                    logging.debug("found cover from coverartarchive: %s", url)
    
            return url
    
    except Exception as e:
        logging.error("could not get cover from coverartarchive for %s: %s",
                      mbid,
                      e)
        logging.exception(e)
