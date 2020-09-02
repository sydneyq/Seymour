import pymongo
import secret

class Database:

    def __init__(self):
        self.dbclient = pymongo.MongoClient(secret.DB_KEY)
        self.db = self.dbclient.seymour

    def openDatabase(self):
        self.dbclient = pymongo.MongoClient(secret.DB_KEY)
        self.db = self.dbclient.seymour

    def closeDatabase(self):
        self.dbclient.close()

    #profile
    def insertProfile(self, toInsert):
        self.db.profile.insert(toInsert)

    def findProfile(self, findCriteria):
        return self.db.profile.find_one(findCriteria)

    def findProfiles(self, findCriteria):
        return self.db.profile.find(findCriteria)

    def updateProfile(self, updateCritera, change):
        self.db.profile.update(updateCritera, change)

    def removeProfile(self, toRemove):
        self.db.profile.remove(toRemove)

    def countProfiles(self, findCriteria):
        return self.db.profile.count(findCriteria)

    #soulmate
    def insertSoulmatePair(self, toInsert):
        self.db.soulmate.insert(toInsert)

    def findSoulmatePair(self, findCriteria):
        return self.db.soulmate.find_one(findCriteria)

    def findSoulmatePairs(self, findCriteria):
        return self.db.soulmate.find(findCriteria)

    def updateSoulmatePair(self, updateCritera, change):
        self.db.soulmate.update(updateCritera, change)

    def removeSoulmatePair(self, toRemove):
        self.db.soulmate.remove(toRemove)

    def countSoulmatePairs(self, findCriteria):
        return self.db.soulmate.count(findCriteria)

    #quote
    def insertQuote(self, toInsert):
        self.db.quote.insert(toInsert)

    def findQuotes(self, findCriteria):
        return self.db.quote.find(findCriteria)

    def findQuote(self, findCriteria):
        return self.db.quote.find_one(findCriteria)

    def removeQuote(self, toRemove):
        self.db.quote.remove(toRemove)

    def countQuotes(self, findCriteria):
        return self.db.quote.count(findCriteria)

    #modlog
    def insertModLog(self, toInsert):
        self.db.modlog.insert(toInsert)

    def findModLogs(self, findCriteria):
        return self.db.modlog.find(findCriteria)

    def findModLog(self, findCriteria):
        return self.db.modlog.find_one(findCriteria)

    def removeModLog(self, toRemove):
        self.db.modlog.remove(toRemove)

    def countModLogs(self, findCriteria):
        return self.db.modlog.count(findCriteria)

    def updateModLog(self, updateCritera, change):
        self.db.modlog.update(updateCritera, change)

    #modprofile
    def insertModProfile(self, toInsert):
        self.db.modprofile.insert(toInsert)

    def findModProfile(self, findCriteria):
        return self.db.modprofile.find_one(findCriteria)

    def removeModProfile(self, toRemove):
        self.db.modprofile.remove(toRemove)

    def updateModProfile(self, updateCritera, change):
        self.db.modprofile.update(updateCritera, change)

    #badges
    def findBadge(self, findCriteria):
        return self.db.badge.find_one(findCriteria)

    #meta
    def findMeta(self, findCriteria):
        return self.db.meta.find_one(findCriteria)

    def updateMeta(self, updateCritera, change):
        self.db.meta.update(updateCritera, change)

    #db
    def makeColumn(self, title, value):
        self.db.profile.update({},{"$set": {title: value}},upsert=False,multi=True)

    def renameColumn(self, old, new):
        self.db.profile.update({},{"$rename": {old: new}},upsert=False,multi=True)

    def removeColumn(self, col):
        self.db.profile.update({},{"$unset":{col: 1}},upsert=False,multi=True)
