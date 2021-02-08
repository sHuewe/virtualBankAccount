from virtualBankAccount.repository.filerepo import FileRepository
from virtualBankAccount.model.account import Account
from virtualBankAccount.model.transaction import Transaction
from dateutil.relativedelta import relativedelta

import datetime

import pandas as pd

ADMIN_USER="admin"



class Broker:
    def __init__(self,userName=None,repo=None):
        if userName is None:
            raise ValueError("Broker has to be started with an user name")
        if repo is None:
            repo=FileRepository()
        self.userName=userName
        self._repo=repo

    def createAccount(self,accountName,parentId=None):
        parent=self.getAccountById(parentId)
        if parentId is not None and parent is None:
            raise ValueError(f'No account available with id "{parentId}"')
        account=Account(accountName,realAccount=parent,user=self.userName)
        account.lastModified=datetime.datetime.now().timestamp()
        self.saveAccount(account)
        if parent is not None:
            parent.withChild(account)
            self.saveAccount(parent)
        return account

    def saveAccount(self,account):
        if account.user != self.userName:
            raise ValueError(f'Unable to save account with other user name than "{self.userName}"')
        self._repo.saveAccount(account)

    def setMonthlyPaiment(self,accountName,value,nMonth=1,monthOffset=1):
        acc=self._requireVirtual(accountName,"Monthly paiment only available for virtual accounts")
        self.saveAccount(acc.withPeriodicValue(value,nMonth,monthOffset=monthOffset))

    def setDefaultAccount(self,accountName):
        acc=self._requireVirtual(accountName,"Require a virtual account")
        self.saveAccount(acc.withPeriodicValue(-1,1))       

    def saveTransaction(self,transaction):
        if len(transaction.accounts)==0:
            return
        transaction.date=datetime.datetime.now().timestamp()
        self._repo.saveTransaction(transaction)

    def getTransactions(self,n=5):
        return self._repo.getLastTransactions(self.userName,n=n)

    def invertTransaction(self,transaction: Transaction):
        if transaction is None:
            return
        if len(transaction.accounts)==0:
            return
        invertTransaction=Transaction(description=f'Invert "{transaction.description}"',user=self.userName)
        accounts=[]
        accountValues={}
        for accountData in transaction.accounts:
            acc=self.getAccountById(accountData["id"])
            if acc is None:
                raise ValueError(f'Cannot invert transaction. No account with id "{accountData["id"]}" found')
            accounts.append(acc)
            accountValues[acc._id]=-accountData["change"]
        #We have found all accounts -> undo transaction
        for acc in accounts:
            invertTransaction.addValueToAccount(acc,accountValues[acc._id])
            self.saveAccount(acc)
        self.saveTransaction(invertTransaction)

    def getAccounts(self,**kwargs):
        kwargs["userName"]=self.userName
        return self._repo.getAccounts(**kwargs)

    def getAccountByName(self,name):
        return self._repo.getAccountByName(name,userName=self.userName)

    def getAccountById(self,accountId):
        return self._repo.getAccountById(accountId,userName=self.userName)

    def getTransactionDf(self,size=10):
        transactions=self.getTransactions(n=size)
        transactions=[t.toDisplayData() for t in transactions]
        return pd.DataFrame(transactions)[["date","description","accounts"]]

    def getAccountsDf(self):
        accounts=self.getAccounts(userName=self.userName)
        accounts=[self.getAccountById(a).toDisplayData() for a in accounts]
        return pd.DataFrame(accounts)[["name","lastModified","value"]]

    def addValue(self,accountName,valueToAdd,transaction: Transaction=None):
        if valueToAdd == 0:
            return
        ac=self.getAccountByName(accountName)
        if ac is None:
            raise ValueError(f'No account with name "{accountName}" available')
        transActionCreated=transaction is None
        if transaction is None:
            if valueToAdd > 0:
                description=f'Transfer to {accountName}'
            else:
                description=f'Remove from {accountName}'
            transaction = Transaction(description=description,user=self.userName)
            
        if not ac.isVirtual() and valueToAdd<0:
            #Only possible if there is free money which is not transfered to virtual accounts
            moneyOnVirtuals = 0
            for childAc in self.getChildsFrom(ac):
                moneyOnVirtuals+=childAc.value
            if ac.value - moneyOnVirtuals +valueToAdd < 0:
                raise ValueError(f'Not enough money on "{ac.name}" which was not transfered to child')
        transaction.addValueToAccount(ac,valueToAdd)
        if ac.isVirtual():
            parent=ac.realAccount
            if not isinstance(parent,Account):
                parent=self.getAccountById(parent)
            transaction.addValueToAccount(parent,valueToAdd)
            self.saveAccount(parent)
        
        self.saveAccount(ac)
        if transActionCreated:
            self.saveTransaction(transaction)


    def getChildsFrom(self,account=None):
        if account is None:
            raise ValueError("You have to provide an accountname or account instance to obtain childs from")
        ac=self._requireReal(account,"Childs not available for virtual accounts")
        res=[]
        if hasattr(ac,"child"):
            for childId in ac.child:
                res.append(self.getAccountById(childId))
        return res

    def transfer(self,accountName):
        ac=self._requireReal(accountName,"Transfer can only be used for a real account to transfer to the virtual childs")
        transaction =Transaction(description=f'Transfer money from {ac.name} to childs',user=self.userName)
        totalValue=ac.value
        virtualValue=0
        today=datetime.datetime.today()
        fallBackAccount=None
        accountWaiting=[]
        for childAccount in self.getChildsFrom(ac):
            if not hasattr(childAccount,"periodical"):
                continue
            childPeriodical=childAccount.periodical
            if childPeriodical["value"]!=-1:
                if today > datetime.datetime.fromtimestamp(childPeriodical["nextDate"]):
                    print(childAccount.name)
                    accountWaiting.append(childAccount)
            else:
                fallBackAccount=childAccount
            virtualValue+=childAccount.value
        if len(accountWaiting)>0:
            print(f'Following accounts wait for paiment: {[a.name for a in accountWaiting]}')
        if totalValue == virtualValue :
            print("All money was transfered before")
        else:
            freeMoney=totalValue-virtualValue
            count=0
            for waitingAcc in accountWaiting:
                perValue=waitingAcc.periodical["value"]
                if perValue <= freeMoney:
                    transaction.addValueToAccount(waitingAcc,perValue)
                    oldNextDate=waitingAcc.periodical["nextDate"]
                    nextDate=datetime.datetime.fromtimestamp(oldNextDate)+ relativedelta(months=waitingAcc.periodical["month"])
                    waitingAcc.periodical["nextDate"]=nextDate.timestamp()
                    freeMoney+=-perValue
                    self.saveAccount(waitingAcc)
                    count+=1
            if count == len(accountWaiting):
                if fallBackAccount is not None:
                    transaction.addValueToAccount(fallBackAccount,freeMoney)
                    self.saveAccount(fallBackAccount)
        self.saveTransaction(transaction)

    def _requireReal(self,account,msg):
        res=None
        if isinstance(account,Account):
            res=account
        else:
            res=self.getAccountByName(account)
        if res is None:
            raise ValueError(f'Account "{account}" is not available')
        if res.isVirtual():
            raise ValueError(msg)
        return res

    def _requireVirtual(self,account,msg):
        res=None
        if isinstance(account,Account):
            res=account
        else:
            res=self.getAccountByName(account)
        if res is None:
            raise ValueError(f'Account "{account}" is not available')
        if not res.isVirtual():
            raise ValueError(msg)
        return res
