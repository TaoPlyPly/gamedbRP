import sqlite3 as lite
import os
import io
import codecs
from zipfile import ZipFile
from shutil import copyfile

class Manager:
    def __init__(self):
        if not os.path.exists('sqlite'):
            print "SQLite Folder not found, exiting."
            exit()
        else:
            if not os.path.exists('roms'):
                os.makedirs('roms')
            if not os.path.exists('source'):
                os.makedirs('source')
            self.con = lite.connect('sqlite/GameDB.db')
            self.cur = self.con.cursor()

    def close(self):
        self.con.close()

    def getCRCDic(self):
        crcDic = {}
        #Test SNK Neo Geo Pocket, USA > Europe > Japan
        sql = """SELECT s.softwareName,ro.crc32,
	    MAX(CASE WHEN rfv.releaseFlagValue = "USA" THEN 3 WHEN rfv.releaseFlagValue = "Europe" THEN 2 WHEN rfv.releaseFlagValue = "Japan" THEN 1 ELSE 0 END) as Region,
	    MAX(CASE WHEN rfv2.releaseFlagValue IS NULL THEN 0 ELSE rfv2.releaseFlagValue END) as Version
            FROM tblSystems sy
            INNER JOIN tblSoftwares s on sy.systemId = s.systemId
            INNER JOIN tblReleases r on s.softwareId = r.softwareId
            INNER JOIN tblRoms ro on r.releaseId = ro.releaseId
            LEFT JOIN tblReleaseFlagValues rfv on rfv.releaseId = r.releaseId AND rfv.releaseFlagID = 1
            LEFT JOIN tblReleaseFlagValues rfv2 on rfv2.releaseId = r.releaseId AND rfv2.releaseFlagID = 3
            WHERE sy.systemId = 44
            GROUP BY 1
            """
        self.cur.execute(sql)
        for row in self.cur:
            crcDic[row[0]]=row[1]
        return crcDic

    def listRoms(self,romPath):
        for filename in os.listdir(romPath):
            if filename.endswith("zip"):
                crc = self.getCRC(os.path.join(romPath, filename))
                print filename + ' : ' + crc
            
    def getCRC(self,filepath):
        zf = ZipFile(filepath)
        rom = zf.infolist()[0]
        return format(rom.CRC,"08X")

    def copyFiles(self,crcDic):
        for romFile in crcDic.iteritems():
            print romFile
            #copyfile(src,dst)
        
if __name__ == '__main__':
    bestRomPath='roms/'
    romPath='source/'

    manager = Manager()
    crcDic = manager.getCRCDic()
    manager.listRoms(romPath)
    print manager.getCRCDic()
    manager.close()
    
    
    
    
    
            
    
