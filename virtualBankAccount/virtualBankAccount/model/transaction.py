from virtualBankAccount.model.account import Account
from virtualBankAccount.model.jsonable import jsonable
import uuid,datetime
mandatory_field=[("user",None),("accounts",[]),("date",0)]

class Transaction(jsonable):
    def __init__(self,description,**kwargs):
        self.description=description
        for attr in kwargs:
            setattr(self,attr,kwargs[attr])
        if not hasattr(self,"_id"):
            self._id=uuid.uuid4().hex
        for mandField in mandatory_field:
            if not hasattr(self,mandField[0]):
                setattr(self,mandField[0],mandField[1])
        if "accounts" not in kwargs:
            self.accounts=[]

    def addValueToAccount(self,account:Account,valueToAdd: float):
        account.addValue(valueToAdd)
        self.accounts.append({"id":account._id,"name":account.name,"change":valueToAdd,"value":account.value})
        return account

    def toDisplayData(self):
        res = super().toDisplayData()
        res["date"]=datetime.datetime.fromtimestamp(res["date"])
        displAccount=""
        for ac in self.accounts:
            displAccount+=ac["name"]+":"+str(ac["change"])+","
        displAccount=displAccount[:-1]
        res["accounts"]=displAccount
        return res