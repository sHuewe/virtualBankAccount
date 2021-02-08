from virtualBankAccount.repository.mongorepo import MongoRepository
from virtualBankAccount.test.broker import A_BrokerTest

class MongoDbBrokerTest(A_BrokerTest):

    def withServerData(self,**kwargs):
        self.serverData=kwargs
        return self
        
    def getRepoInstance(self):
        return MongoRepository(dbName="test_virtualBankAccount",**self.serverData)

    def tearDownRepo(self):
        self.broker._repo.client.drop_database("test_virtualBankAccount")
