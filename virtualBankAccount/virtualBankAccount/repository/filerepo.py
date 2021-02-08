from virtualBankAccount.repository.repo import Repository
from virtualBankAccount.model.account import Account
from virtualBankAccount.model.transaction import Transaction
import json,os
import pandas as pd

def checkUserName(account,userName):
    if userName is None or account is None:
        return account
    if not hasattr(account,"user"):
        return None
    if account.user != userName:
        return None
    return account

class FileRepository(Repository):
    def __init__(self,fileNameAccounts="accounts.json",fileNameTransactions="transaction.json"):
        super().__init__()
        self.fileNameAccounts=fileNameAccounts
        self.fileNameTransactions=fileNameTransactions
        #Dict
        self.accounts={}
        #Dict by name name -> id
        self.accountNames={}
        #Sorted List
        self.accountIDs=[]
        #Dict
        self.transactions={}
        #Dict by name name -> id
        self.transactionNames={}
        #Sorted List
        self.transactionIDs=[]
        self.getTransactions()

    def saveAccounts(self):
        data=[]
        for accountId in self.accountIDs:
            data.append(self.accounts[accountId].toJsonData())
        with open(self.fileNameAccounts, "w") as write_file:
            json.dump(data, write_file,indent=4)
        #self.clearCache(accounts=False)


    def getAccountById(self,id,userName=None):
        if len(self.accounts) == 0:
            self.getAccounts()
        return checkUserName(self.accounts.get(id,None),userName)


    def getAccountByName(self,name,userName=None):
        if len(self.accounts) == 0:
            self.getAccounts()
        accId=self.accountNames.get(name,{}).get(userName,None)
        if accId is None:
            return None
        return checkUserName(self.accounts.get(accId,None),userName)

    def saveNewAccount(self,account):
        self.accounts[account._id]=account
        if self.accountNames.get(account.name,None) is None:
            self.accountNames[account.name]={}
        self.accountNames.get(account.name,None)[account.user]=account._id
        self.accountIDs.append(account._id)
        self.saveAccounts()

    def saveUpdatedAccount(self,account):
        self.accounts[account._id]=account
        if self.accountNames.get(account.name,None) is None:
            self.accountNames[account.name]={}
        self.accountNames.get(account.name,None)[account.user]=account._id
        self.saveAccounts()

    def getAccounts(self,name=None,iban=None,userName=None):
        data=None
        if not os.path.exists(self.fileNameAccounts):
            return self.accounts
        with open(self.fileNameAccounts) as f:
            data = json.load(f)
        self.accounts={}
        self.accountIDs=[]
        self.accountNames={}
        if data is None:
            return
        for accountJson in data:
            accObj=Account(**accountJson)
            self.accounts[accObj._id]=accObj
            self.accountIDs.append(accObj._id)
            if self.accountNames.get(accObj.name,None) is None:
                self.accountNames[accObj.name]={}
            self.accountNames.get(accObj.name,None)[accObj.user]=accObj._id
        res=self.accounts
        if userName != None:
            res=[]
            for accId in self.accounts:
                acc=self.accounts[accId]
                if not hasattr(acc,"user"):
                    continue
                if acc.user!=userName:
                    continue
                res.append(accId)
        return res

    def saveTransaction(self,transaction: Transaction):
        self.transactions[transaction._id]=transaction
        self.transactionIDs.append(transaction._id)
        self.saveTransactions()
    
    def getTransactions(self):
        data=None
        if not os.path.exists(self.fileNameTransactions):
            return []
        with open(self.fileNameTransactions) as f:
            data = json.load(f)
        self.transactions={}
        self.transactionIDs=[]
        if data is None:
            return
        for transactionJson in data:
            transactionObj=Transaction(**transactionJson)
            self.transactions[transactionObj._id]=transactionObj
            self.transactionIDs.append(transactionObj._id)


    def getLastTransactions(self,userName=None,n=5):
        if len(self.transactionIDs) == 0:
            self.getTransactions()
        userData=self.transactions
        if userName != None:
            userData=[]
            for transactionId in self.transactions:
                tr=self.transactions[transactionId]
                if not hasattr(tr,"user"):
                    continue
                if tr.user!=userName:
                    continue
                userData.append(tr)
        data=[]
        for tr in userData:
            data.append(pd.Series({"id":tr._id,"date":tr.date}))
        df=pd.DataFrame(data).sort_values("date",ascending=False)
        res=[]
        for i in range(n):
            if i<len(df):
                res.append(self.transactions[df.iloc[i]["id"]])
        return res

    def saveTransactions(self):
        data=[]
        for transactionId in self.transactionIDs:
            data.append(self.transactions[transactionId].toJsonData())
        with open(self.fileNameTransactions, "w") as write_file:
            json.dump(data, write_file,indent=4)

    def clearCache(self,accounts=True,transactions=True):
        if accounts:
            self.accounts={}
            self.accountIDs=[]
            self.accountNames={}
        if transactions:
            self.transactions={}
            self.transactionIDs=[]