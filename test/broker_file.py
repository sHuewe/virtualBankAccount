from virtualBankAccount.repository.filerepo import FileRepository
from virtualBankAccount.test.broker import A_BrokerTest

import os

class FileRepoBrokerTest(A_BrokerTest):

    def setUp(self):
        if os.path.exists("test_accounts.json"):
            self.tearDownRepo()
        super().setUp()

    def getRepoInstance(self):
        return FileRepository(fileNameAccounts=os.path.join("test_accounts.json"),fileNameTransactions=os.path.join("test_transactions.json"))

    def tearDownRepo(self):
        for fileName in [os.path.join("test_accounts.json"),os.path.join("test_transactions.json")]:
            if os.path.exists(fileName):
                os.remove(fileName)
