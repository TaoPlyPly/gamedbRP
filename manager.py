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

    def getSystems(self):
        systemDic = {}
        sql = "SELECT systemManufacturer || ' - ' || systemName, systemId FROM tblSystems"
        self.cur.execute(sql)
        for row in self.cur:
            systemDic[row[1]]=row[0]
        return systemDic 

    def getCRCDic(self,systemId,userInput):
        crcDic = {}

        selectSQL = "SELECT s.softwareName,ro.crc32,"

        REGION_US_EU_JP = "MAX(CASE WHEN rfv.releaseFlagValue = 'USA' THEN 3 WHEN rfv.releaseFlagValue = 'Europe' THEN 2 WHEN rfv.releaseFlagValue = 'Japan' THEN 1 ELSE 0 END) as Region,"
        REGION_JP_US_EU = "MAX(CASE WHEN rfv.releaseFlagValue = 'USA' THEN 2 WHEN rfv.releaseFlagValue = 'Europe' THEN 1 WHEN rfv.releaseFlagValue = 'Japan' THEN 3 ELSE 0 END) as Region,"
        REGION_EU_US_JP = "MAX(CASE WHEN rfv.releaseFlagValue = 'USA' THEN 2 WHEN rfv.releaseFlagValue = 'Europe' THEN 3 WHEN rfv.releaseFlagValue = 'Japan' THEN 1 ELSE 0 END) as Region,"
        REGION_EU_ONLY = " AND rfv.releaseFlagValue = 'Europe'"
        REGION_US_ONLY = " AND rfv.releaseFlagValue = 'USA'"
        REGION_JP_ONLY = " AND rfv.releaseFlagValue = 'Japan'"
        
        RELEASE_FLAG_VALUE = "MAX(CASE WHEN rfv2.releaseFlagValue IS NULL THEN 0 ELSE rfv2.releaseFlagValue END) as Version"

        tableSQL = """ FROM tblSystems sy
                    INNER JOIN tblSoftwares s on sy.systemId = s.systemId
                    INNER JOIN tblReleases r on s.softwareId = r.softwareId
                    INNER JOIN tblRoms ro on r.releaseId = ro.releaseId
                    LEFT JOIN tblReleaseFlagValues rfv on rfv.releaseId = r.releaseId AND rfv.releaseFlagID = 1
                    LEFT JOIN tblReleaseFlagValues rfv2 on rfv2.releaseId = r.releaseId AND rfv2.releaseFlagID = 3"""

        whereSQL = " WHERE sy.systemId = " + str(systemId)
        groupBySQL = " GROUP BY 1"
            
        if userInput == 1:
            sql = selectSQL + REGION_US_EU_JP + RELEASE_FLAG_VALUE + tableSQL + whereSQL + groupBySQL
        if userInput == 2:
            sql = selectSQL + REGION_JP_US_EU + RELEASE_FLAG_VALUE + tableSQL + whereSQL + groupBySQL
        if userInput == 3:
            sql = selectSQL + REGION_EU_US_JP + RELEASE_FLAG_VALUE + tableSQL + whereSQL + groupBySQL
        if userInput == 4:
            sql = selectSQL + RELEASE_FLAG_VALUE + tableSQL + whereSQL + REGION_EU_ONLY + groupBySQL
        if userInput == 5:
            sql = selectSQL + REGION_USEUJP + RELEASE_FLAG_VALUE + tableSQL + REGION_US_ONLY + groupBySQL
        if userInput == 6:
            sql = selectSQL + REGION_USEUJP + RELEASE_FLAG_VALUE + tableSQL + REGION_JP_ONLY + groupBySQL
            
        self.cur.execute(sql)
        for row in self.cur:
            crcDic[row[1]]=row[0]
        return crcDic

    def copyFiles(self,romPath,bestRomPath,userInput):
        systemDic = self.getSystems()
        for systemId,systemName in systemDic.iteritems():
            if (os.path.isdir(romPath + systemName)):
                romDir = romPath + systemName
                bestRomDir = bestRomPath + systemName
                print "Copying " + romDir
                if (os.path.isdir(bestRomDir)):
                    pass
                else:
                    os.makedirs(bestRomDir)
                crcDic = self.getCRCDic(systemId,userInput)
                for filename in os.listdir(romDir):
                    if filename.endswith("zip"):
                        crc = self.getCRC(os.path.join(romDir, filename))
                        if crc in crcDic:
                            copyfile(os.path.join(romDir, filename),os.path.join(bestRomDir, filename))

    def getCRC(self,filepath):
        zf = ZipFile(filepath)
        rom = zf.infolist()[0]
        return format(rom.CRC,"08X")
        
if __name__ == '__main__':
    bestRomPath='roms/'
    romPath='source/'

    manager = Manager()
    while True:
        try:
            userInput = int(raw_input("What copy method would u like to use ? \n1.USA > Europe > Japan\n2.Japan > USA > Europe\n3.Europe > USA > Japan\n4.Europe Only\n5.USA Only\n6.Japan Only\n\nYour choice (then press Enter): "))
            if int(userInput) in range(1,7):
                manager.copyFiles(romPath,bestRomPath,userInput)
                manager.close()
                break
            else:
                print "RTFM - Between 1 AND 6?\n\n"
        except:
            print "There was a catch here"
            manager.close()
            break
