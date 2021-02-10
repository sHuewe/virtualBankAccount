# VirtualBankAccount
## Purpose
I was a happy customer of the Moneyou bank which is about to be closed in 2021. The bank has offered up to 5 accounts which were very useful for saving money for certain topics eg. larger holidays, a new car, car repairs, ... in separate accounts.

Since I didn't find a suitable alternative to Moneyou, I developed this project. The virtualBankAccount allows to virtually split real existing accounts to multiple virtual accounts. Every virtual account belongs to one real account. You can either (virtual) transfer money to the different accounts, or you can define monthly saving rates and a default virtual account. If you transfer money to the real account, the library splits the incoming money to the virtual accounts and you keep the overview of all your saving topics.

The library can be used with MongoDB as a backend or you can store your accounts and transactions in files in your local filesystem.

## Setup
You need python3 (>=3.6) for this library. You should create a new virtual environment and activate it. Install the module "virtualBankAccount" by using the setup.py. 

```bash
cd virtualBankAccount
python -m pip install -e .
```
This should install all needed dependencies which are currently: numpy, pandas and pymongo.
If you want to use the MongoDB backend, you need a MongoDB connection. This can be easily realized by the use of the MongoDB docker image.

## Run the tests
For most of the provided functions, you will find test cases in `virtualBankAccount/all_tests.py`. The test suite includes tests for both backends (the filesystem and MongoDB). You have to provide suitable credentials for MongoDB, if you want to run all test cases.

## Jupyter notebook
To get an impression of how to use the module, I recommend having a look at `notebooks/BankAccount.ipnyb`.

## Basic structure / Concept of the module
The most important class is the broker class (`virtualBankAccount.broker`). The broker is initialized with a username and a repository instance. A broker instance can create, read and manipulate all accounts of the given user. Other accounts can not be accessed. 

The repository is either an instance of `virtualBankAccount.repository.filerepo.FileRepository` or `virtualBankAccount.repository.mongorepo.MongoRepository`. One instance can and should be used for multiple users. 

An application should reuse the repo instances, but create own broker instances for all logged-in users.


