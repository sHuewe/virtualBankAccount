import uuid
import datetime
from dateutil.relativedelta import relativedelta

from virtualBankAccount.model.jsonable import jsonable

mandatory_field=[("value",0),("lastModified",None)]

class Account(jsonable):
    def __init__(self,name,**kwargs):#,name=None,_id=None,iban=None,value=0,realAccount=None,lastModified=None,child=None,periodical=None
        self.name=name
        for attr in kwargs:
            setattr(self,attr,kwargs[attr])
        if not hasattr(self,"_id"):
            self._id=uuid.uuid4().hex
        for mandField in mandatory_field:
            if not hasattr(self,mandField[0]):
                setattr(self,mandField[0],mandField[1])
        if hasattr(self,"child"):
            if self.child is None:
                delattr(self,"child")
 
        #if periodical is not None:
        #    self.periodical=periodical
        if hasattr(self,"realAccount"):
            if self.realAccount is None:
                delattr(self,"realAccount")

    def isVirtual(self):
        return hasattr(self,"realAccount")

    def withChild(self,childAccount):
        if not hasattr(self,"child"):
            self.child=[]
        childId=childAccount
        if isinstance(childAccount, Account):
            childId=childAccount._id
        self.child.append(childId)
        return self

    def withPeriodicValue(self,valueToAdd,nMonth,monthOffset=1):
        today=datetime.date.today()
        today=today.replace(day=1)
        dt = datetime.datetime.combine(today, datetime.datetime.min.time())
        dt=dt + relativedelta(months=monthOffset)
        self.periodical={"month":nMonth,"value":valueToAdd,"nextDate":dt.timestamp()}
        return self

    def addValue(self,valueToAdd):
        self.value+=valueToAdd
        self.lastModified=datetime.datetime.now().timestamp()
        return self
        
    def toJsonData(self):
        res= super().toJsonData()
        if "realAccount" in res.keys():
            if isinstance(res["realAccount"],Account):
                res["realAccount"]=self.realAccount._id
        return res