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

    # profile
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

    # picknic
    def insertPicknic(self, toInsert):
        self.db.profile.insert(toInsert)

    def findPicknic(self, findCriteria):
        return self.db.profile.find_one(findCriteria)

    def findPicknics(self, findCriteria):
        return self.db.profile.find(findCriteria)

    def updatePicknic(self, updateCritera, change):
        self.db.profile.update(updateCritera, change)

    def removePicknic(self, toRemove):
        self.db.profile.remove(toRemove)

    def countPicknic(self, findCriteria):
        return self.db.profile.count(findCriteria)

    # badges
    def findBadge(self, findCriteria):
        return self.db.badge.find_one(findCriteria)

    def insertBadge(self, toInsert):
        self.db.badge.insert(toInsert)

    def removeBadge(self, toRemove):
        self.db.badge.remove(toRemove)

    def findBadges(self, findCriteria):
        return self.db.badge.find(findCriteria)

    # server
    def findServer(self, findCriteria):
        return self.db.server.find_one(findCriteria)

    def findMeta(self, findCriteria):
        return self.db.server.find_one(findCriteria)

    def updateServer(self, updateCriteria, change):
        self.db.server.update(updateCriteria, change)

    def insertServer(self, toInsert):
        self.db.server.insert(toInsert)

    def removeServer(self, toRemove):
        self.db.server.remove(toRemove)

    # store
    def findStoreItems(self, findCriteria):
        return self.db.store.find(findCriteria)

    def findStoreItem(self, findCriteria):
        return self.db.store.find_one(findCriteria)

    def updateStoreItem(self, updateCriteria, change):
        self.db.store.update(updateCriteria, change)

    def insertStoreItem(self, toInsert):
        self.db.store.insert(toInsert)

    def removeStoreItem(self, toRemove):
        self.db.store.remove(toRemove)

    # db
    def makeColumn(self, title, value):
        self.db.profile.update({}, {"$set": {title: value}}, upsert=False, multi=True)

    def renameColumn(self, old, new):
        self.db.profile.update({}, {"$rename": {old: new}}, upsert=False, multi=True)

    def removeColumn(self, col):
        self.db.profile.update({}, {"$unset": {col: 1}}, upsert=False, multi=True)
