from virtualBankAccount.test.broker_file import FileRepoBrokerTest
from virtualBankAccount.test.broker_mongo import MongoDbBrokerTest
import unittest

def suite(**kwargs):
    suite = unittest.TestSuite()
    suite.addTest(FileRepoBrokerTest('test_checkSetupState'))
    suite.addTest(FileRepoBrokerTest('test_double_accounts'))
    suite.addTest(FileRepoBrokerTest('test_addToSub'))
    suite.addTest(FileRepoBrokerTest('test_negative_value'))
    suite.addTest(FileRepoBrokerTest('test_addToMaster'))
    suite.addTest(FileRepoBrokerTest('test_takeFromMaster_notOnVirtual'))
    suite.addTest(FileRepoBrokerTest('test_takeFromMaster_onVirtual'))
    suite.addTest(FileRepoBrokerTest('test_takeFromSub'))
    suite.addTest(FileRepoBrokerTest('test_transfer_no_config'))
    suite.addTest(FileRepoBrokerTest('test_transfer_withFallback'))
    suite.addTest(FileRepoBrokerTest('test_transfer_withPeriod'))
    suite.addTest(FileRepoBrokerTest('test_user_tryRead'))
    suite.addTest(FileRepoBrokerTest('test_user_add'))
    suite.addTest(FileRepoBrokerTest('test_transaction_addMaster'))
    suite.addTest(FileRepoBrokerTest('test_transaction_addVirtual'))
    suite.addTest(FileRepoBrokerTest('test_transaction_undo'))
    suite.addTest(FileRepoBrokerTest('test_transaction_transfer'))
    suite.addTest(FileRepoBrokerTest('test_transaction_multiuser'))

    suite.addTest(MongoDbBrokerTest('test_checkSetupState').withServerData(**kwargs))
    suite.addTest(MongoDbBrokerTest('test_double_accounts').withServerData(**kwargs))
    suite.addTest(MongoDbBrokerTest('test_addToSub').withServerData(**kwargs))
    suite.addTest(MongoDbBrokerTest('test_negative_value').withServerData(**kwargs))
    suite.addTest(MongoDbBrokerTest('test_addToMaster').withServerData(**kwargs))
    suite.addTest(MongoDbBrokerTest('test_takeFromMaster_notOnVirtual').withServerData(**kwargs))
    suite.addTest(MongoDbBrokerTest('test_takeFromMaster_onVirtual').withServerData(**kwargs))
    suite.addTest(MongoDbBrokerTest('test_takeFromSub').withServerData(**kwargs))
    suite.addTest(MongoDbBrokerTest('test_transfer_no_config').withServerData(**kwargs))
    suite.addTest(MongoDbBrokerTest('test_transfer_withFallback').withServerData(**kwargs))
    suite.addTest(MongoDbBrokerTest('test_transfer_withPeriod').withServerData(**kwargs))
    suite.addTest(MongoDbBrokerTest('test_user_tryRead').withServerData(**kwargs))
    suite.addTest(MongoDbBrokerTest('test_user_add').withServerData(**kwargs))
    suite.addTest(MongoDbBrokerTest('test_transaction_addMaster').withServerData(**kwargs))
    suite.addTest(MongoDbBrokerTest('test_transaction_addVirtual').withServerData(**kwargs))
    suite.addTest(MongoDbBrokerTest('test_transaction_undo').withServerData(**kwargs))
    suite.addTest(MongoDbBrokerTest('test_transaction_transfer').withServerData(**kwargs))
    suite.addTest(MongoDbBrokerTest('test_transaction_multiuser').withServerData(**kwargs))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite(username="root",password="example"))