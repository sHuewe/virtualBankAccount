from virtualBankAccount.repository.repo import Repository
from virtualBankAccount.model.account import Account
from virtualBankAccount.model.transaction import Transaction

from pymongo import MongoClient

class MongoRepository(Repository):

    #kwargs should match MongoClient (host,port,username,password)
    def __init__(self,dbName="virtualBankAccount",**kwargs):
        super().__init__()
        self.client=MongoClient(**kwargs)
        self.db=self.client[dbName]


    def getAccountById(self,id,userName=None):
        mongoData=self.db.accounts.find_one({"_id":id,"user":userName})
        if mongoData is None:
            return
        return Account(**mongoData)


    def getAccountByName(self,name,userName=None):
        mongoData=self.db.accounts.find_one({"name":name,"user":userName})
        if mongoData is None:
            return
        return Account(**mongoData)

    def saveNewAccount(self,account):
        self.db.accounts.insert_one(account.toJsonData())
        return

    def saveUpdatedAccount(self,account):
        self.db.accounts.update_one({"_id":account._id},{"$set":account.toJsonData()})
        return

    def getAccounts(self,name=None,iban=None,userName=None):
        mongoData=self.db.accounts.find({"user":userName})
        if mongoData.count() == 0:
            return []
        res=[]
        for data in mongoData:
            res.append(data["_id"])
        return res

    def saveTransaction(self,transaction: Transaction):
        self.db.transactions.insert_one(transaction.toJsonData())

    def getLastTransactions(self,userName=None,n=5):
        res=[]
        for transactionData in self.db.transactions.find({"user":userName}).sort("date",-1).limit(n):
            res.append(Transaction(**transactionData))
        return res


    def clearCache(self):
        pass