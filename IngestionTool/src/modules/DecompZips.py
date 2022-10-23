from pathlib import Path
from zipfile import ZipFile

class DecompZips:
    def __init__(self, dir):
        self.dir = dir

    def decompose(self):
        zips = [str(f) for f in self.dir.iterdir() if f.is_file() and f.suffix==".zip"]
        zips.sort()
        sorted_zips = []
        
        for path in zips:    
            repath = Path(path)
            sorted_zips.append(repath)
        
        for zf in sorted_zips:
            with ZipFile(str(zf), 'r') as zip:
                zip.extractall(self.dir)
            
            
            

        