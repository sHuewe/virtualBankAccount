from virtualBankAccount.model.account import Account
from virtualBankAccount.model.transaction import Transaction

class Repository:
    def __init__(self):
        pass

    def saveAccount(self,account:Account):
        acc_from_id=self.getAccountById(account._id,userName=account.user)
        acc_from_name=self.getAccountByName(account.name,userName=account.user)
        if acc_from_name is None and acc_from_id is None:
            self.saveNewAccount(account)
        else:
            if acc_from_name is not None:
                if acc_from_name._id != account._id:
                    raise ValueError(f'The name "{account.name}" is already used by another account')
            self.saveUpdatedAccount(account)

    def saveTransaction(self,transaction: Transaction):
        raise NotImplementedError("not implemented")
    
    def getLastTransactions(self,userName=None,n=5):
        raise NotImplementedError("not implemented")

    def saveNewAccount(self,account):
        raise NotImplementedError("not implemented")


    def getAccountById(self,id,userName=None):
        raise NotImplementedError("not implemented")

    def getAccountByName(self,name,userName=None):
        raise NotImplementedError("not implemented")

    def saveUpdatedAccount(self,account):
        raise NotImplementedError("not implemented")

    def getAccounts(self,name=None,iban=None,userName=None):
        raise NotImplementedError("not implemented")

    def clearCache(self):
        raise NotImplementedError("not implemented")