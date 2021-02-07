import unittest

from virtualBankAccount.broker import Broker

DEFAULT_USER="adminUser"

class A_BrokerTest(unittest.TestCase):
    def setUp(self):
        self.broker : Broker=self.getBrokerInstance()
        master=self.broker.createAccount("MASTER")
        self.broker.createAccount("Sub1",parentId=master._id)
        self.broker.createAccount("Sub2",parentId=master._id)
        self.broker.createAccount("Sub3",parentId=master._id)
        #Avoid success only because of caching
        self.broker= self.getBrokerInstance()
        
    def getBrokerInstance(self,user=None):
        if user is None:
            return Broker(DEFAULT_USER,repo=self.getRepoInstance())
        return Broker(user,repo=self.getRepoInstance())

    def tearDown(self):
        self.tearDownRepo()

    def getRepoInstance(self):
        raise NotImplementedError("Test needs to provide a test repo instance")

    def tearDownRepo(self):
        raise NotImplementedError("Test needs to tear up test repo")

    def test_checkSetupState(self):

        self.assertEqual(len(self.broker.getAccounts()),4)

        #Try to read from new broker to check if read/write works (instead of use cached versions in repo)
        otherBroker = self.getBrokerInstance()
        #Check if we have two accounts
        self.assertEqual(len(self.broker.getAccounts()),4)
        
        for childName in ["Sub1","Sub2","Sub3"]:
            #Check if we can read sub and if it is connected to master
            self.assertEqual(self.broker.getAccountByName("MASTER")._id,otherBroker.getAccountByName(childName).realAccount)
            #Check if we can read master and child is set correctly
            self.assertIn(otherBroker.getAccountByName(childName)._id,otherBroker.getAccountByName("MASTER").child )

    def test_addToSub(self):
        self.broker.addValue("Sub1",1000)
        
        self.assertEqual(self.broker.getAccountByName("Sub1").value,1000)
        self.assertEqual(self.broker.getAccountByName("MASTER").value,1000)
        self.assertEqual(self.broker.getAccountByName("Sub2").value,0)
        self.assertEqual(self.broker.getAccountByName("Sub3").value,0)


    def test_transfer_no_config(self):
        self.broker.addValue("MASTER",1000)
        self.broker.transfer("MASTER")
        self.assertEqual(self.broker.getAccountByName("Sub1").value,0)
        self.assertEqual(self.broker.getAccountByName("MASTER").value,1000)
        self.assertEqual(self.broker.getAccountByName("Sub2").value,0)
        self.assertEqual(self.broker.getAccountByName("Sub3").value,0)

    def test_transfer_withFallback(self):
        self.broker.addValue("MASTER",1000)
        sub1=self.broker.getAccountByName("Sub1")
        self.broker.saveAccount(sub1.withPeriodicValue(-1,1))
        self.broker.transfer("MASTER")
        self.assertEqual(self.broker.getAccountByName("Sub1").value,1000)
        self.assertEqual(self.broker.getAccountByName("MASTER").value,1000)
        self.assertEqual(self.broker.getAccountByName("Sub2").value,0)
        self.assertEqual(self.broker.getAccountByName("Sub3").value,0)

    def test_transfer_withPeriod(self):
        self.broker.addValue("MASTER",1000)
        for name,mValue in zip(["Sub1","Sub2","Sub3"],[-1,100,200]):
            sub=self.broker.getAccountByName(name).withPeriodicValue(mValue,1,monthOffset=-1) #2 Payments should be made
            self.broker.saveAccount(sub)
        self.broker.transfer("MASTER")
        self.assertEqual(self.broker.getAccountByName("Sub1").value,700)
        self.assertEqual(self.broker.getAccountByName("MASTER").value,1000)
        self.assertEqual(self.broker.getAccountByName("Sub2").value,100)
        self.assertEqual(self.broker.getAccountByName("Sub3").value,200)
        self.broker.addValue("MASTER",400)
        self.broker.transfer("MASTER")
        self.assertEqual(self.broker.getAccountByName("Sub1").value,800)
        self.assertEqual(self.broker.getAccountByName("MASTER").value,1400)
        self.assertEqual(self.broker.getAccountByName("Sub2").value,200)
        self.assertEqual(self.broker.getAccountByName("Sub3").value,400)
        self.broker.addValue("MASTER",400)
        self.broker.transfer("MASTER")
        self.assertEqual(self.broker.getAccountByName("Sub1").value,1200)
        self.assertEqual(self.broker.getAccountByName("MASTER").value,1800)
        self.assertEqual(self.broker.getAccountByName("Sub2").value,200)
        self.assertEqual(self.broker.getAccountByName("Sub3").value,400)


    def test_addToMaster(self):
        self.broker.addValue("MASTER",1000)
        
        self.assertEqual(self.broker.getAccountByName("Sub1").value,0)
        self.assertEqual(self.broker.getAccountByName("MASTER").value,1000)
        self.assertEqual(self.broker.getAccountByName("Sub2").value,0)
        self.assertEqual(self.broker.getAccountByName("Sub3").value,0)

    def test_user_tryRead(self):
        broker = self.getBrokerInstance("testUser")
        broker._repo = self.broker._repo
        self.assertIsNone(broker.getAccountByName("MASTER"))
        self.assertIsNotNone(self.broker.getAccountByName("MASTER"))
        self.assertEqual(len(broker.getAccounts()),0)
        self.assertEqual(len(self.broker.getAccounts()),4)

    def test_user_add(self):
        broker = self.getBrokerInstance("testUser")
        #Share same repo instance
        broker._repo = self.broker._repo

        #Create accounts for new user
        master=broker.createAccount("MASTER")
        broker.createAccount("Sub1",parentId=master._id)

        #Add money to brokers
        broker.addValue("Sub1",100)
        self.broker.addValue("Sub1",1000)
        self.assertRaises(ValueError,broker.addValue,"Sub3",100)    
        
        
        self.assertEqual(self.broker.getAccountByName("MASTER").value,1000)  
        self.assertEqual(broker.getAccountByName("MASTER").value,100)   
        self.assertNotEqual(broker.getAccountByName("MASTER")._id,self.broker.getAccountByName("MASTER")._id)

    def test_double_accounts(self):
        self.assertRaises(ValueError,self.broker.createAccount,"Sub1")

    def test_takeFromMaster_notOnVirtual(self):
        self.broker.addValue("MASTER",1000)
        self.broker.addValue("MASTER",-100)
        self.assertEqual(self.broker.getAccountByName("Sub1").value,0)
        self.assertEqual(self.broker.getAccountByName("MASTER").value,900)
        self.assertEqual(self.broker.getAccountByName("Sub2").value,0)
        self.assertEqual(self.broker.getAccountByName("Sub3").value,0)

    def test_takeFromSub(self):
        self.broker.addValue("Sub1",1000)
        self.broker.addValue("Sub1",-100)
        self.assertEqual(self.broker.getAccountByName("Sub1").value,900)
        self.assertEqual(self.broker.getAccountByName("MASTER").value,900)
        self.assertEqual(self.broker.getAccountByName("Sub2").value,0)
        self.assertEqual(self.broker.getAccountByName("Sub3").value,0)

    def test_takeFromMaster_onVirtual(self):
        self.broker.addValue("Sub1",1000)
        self.assertRaises(ValueError,self.broker.addValue,"MASTER",-100)
            
        self.assertEqual(self.broker.getAccountByName("Sub1").value,1000)
        self.assertEqual(self.broker.getAccountByName("MASTER").value,1000)
        self.assertEqual(self.broker.getAccountByName("Sub2").value,0)
        self.assertEqual(self.broker.getAccountByName("Sub3").value,0)

    def test_transaction_addMaster(self):
        self.broker.addValue("MASTER",11)
        self.broker=self.getBrokerInstance()
        self.broker.addValue("MASTER",1001)
        transactions= self.broker.getTransactions()
        self.assertEqual(len(transactions),2)
        self.assertEqual(len(transactions[0].accounts),1)
        self.assertEqual(transactions[0].accounts[0]["name"],"MASTER")
        self.assertEqual(transactions[0].accounts[0]["change"],1001)
        self.assertEqual(transactions[0].accounts[0]["value"],1012)

    def test_transaction_addVirtual(self):
        self.broker.addValue("Sub1",1001)
        transactions= self.broker.getTransactions()
        self.assertEqual(len(transactions),1)
        self.assertEqual(len(transactions[0].accounts),2)
        for i in range(2):
            self.assertIn(transactions[0].accounts[i]["name"],["MASTER","Sub1"])
            self.assertEqual(transactions[0].accounts[i]["change"],1001)
            self.assertEqual(transactions[0].accounts[i]["value"],1001)

    def test_transaction_undo(self):
        self.broker.addValue("Sub1",1001)
        transactions= self.broker.getTransactions()
        self.assertEqual(len(transactions),1)
        self.assertEqual(self.broker.getAccountByName("MASTER").value,1001)
        self.assertEqual(self.broker.getAccountByName("Sub1").value,1001)
        self.broker.invertTransaction(transactions[0])
        self.assertEqual(self.broker.getAccountByName("MASTER").value,0)
        self.assertEqual(self.broker.getAccountByName("Sub1").value,0)

    def test_transaction_transfer(self):
        self.broker.addValue("MASTER",1000)
        self.broker.addValue("Sub2",200)
        for name,mValue in zip(["Sub1","Sub2","Sub3"],[-1,100,200]):
            sub=self.broker.getAccountByName(name).withPeriodicValue(mValue,1,monthOffset=-1) #2 Payments should be made
            self.broker.saveAccount(sub)
        self.assertEqual(len(self.broker.getTransactions()),2)
        self.broker.transfer("MASTER")
        self.assertEqual(len(self.broker.getTransactions()),3)

    def test_transaction_multiuser(self):
        self.broker.addValue("MASTER",1000)
        self.broker.addValue("Sub2",200)
        broker2=self.getBrokerInstance("testUser2")
        mymaster=broker2.createAccount("MYMASTER")
        broker2.createAccount("ssss",parentId=mymaster._id)
        broker2.addValue("ssss",100)
        broker2.addValue("ssss",110)
        broker2.addValue("ssss",102)
        self.assertEqual(len(broker2.getTransactions(n=100)),3)
        self.assertEqual(len(self.broker.getTransactions(n=100)),2)
        self.broker.addValue("Sub2",100)
        self.assertEqual(len(broker2.getTransactions(n=100)),3)
        self.assertEqual(len(self.broker.getTransactions(n=100)),3)