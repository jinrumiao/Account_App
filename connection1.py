import os
import re
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import pandas as pd


class ConnectAccount:
    def __init__(self):
        load_dotenv()
        MONGODB_URI = os.environ["MONGODB_URI"]

        self.client = MongoClient(MONGODB_URI, tls=True, tlsAllowInvalidCertificates=True, server_api=ServerApi('1'))

        try:
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)

        self.db = self.client.Accounting

        self.collect = self.db.XinFu

    def InsertData(self, post):
        try:
            self.collect.insert_one(post)
            # print(post_id)
        except Exception as e:
            print(e)

        # self.client.close()

    def QueryData(self):
        data_list = []
        for data in self.collect.find():
            data_list.append(data)

        # self.client.close()

        return data_list

    def UpdateData(self, data: dict):
        new_data = data
        id_pair = next(iter((data.items())))
        filter_id = {id_pair[0]: id_pair[1]}
        del new_data["_id"]

        self.collect.replace_one(filter_id, new_data)

    def DeleteData(self, data: dict):
        delete_target = data
        id_pair = next(iter((data.items())))
        target_id = {id_pair[0]: id_pair[1]}

        self.collect.delete_one(target_id)

    def SummaryByCodes(self):
        pipeline = [
            {"$unwind": "$details"},
            {
                "$group": {
                    "_id": "$details.code_of_accounts",
                    "accounting_item": {"$first": "$details.accounting_item"},
                    "date": {"$first": "$date"},
                    "total_expenditure": {"$sum": "$details.expenditure_details"},
                    "total_revenues": {"$sum": "$details.revenues_details"},
                    "serial_number": {"$first": "$serial_number"},
                    "total_count": {"$sum": 1}
                }
            },
            {"$sort": {"date": 1}}
        ]

        results = self.collect.aggregate(pipeline)

        self.client.close()

        return results

    def SummaryByAccount(self):
        pipeline = [
            {
                "$group": {
                    "_id": "$account",
                    "total_revenues": {"$sum": "$revenues"},
                    "total_expenditure": {"$sum": "$expenditure"},
                }
            },
            {
                "$addFields": {
                    "total_balance": {"$subtract": ["$total_revenues", "$total_expenditure"]}
                }
            }
        ]

        results = self.collect.aggregate(pipeline)

        self.client.close()

        return results

    def SummaryByCode(self):
        pipeline = [
            {"$unwind": "$details"},
            {
                "$group": {
                    "_id": "$details.code_of_accounts",
                    "total_revenues": {"$sum": "$details.revenues_details"},
                    "total_expenditure": {"$sum": "$details.expenditure_details"},
                }
            },
        ]

        results = self.collect.aggregate(pipeline)

        self.client.close()

        return results

    def Searching(self, match: str):
        pipeline = [
            {"$unwind": "$details"},
            {
                "$group": {
                    "_id": "$details.code_of_accounts",
                    "accounting_item": {"$first": "$details.accounting_item"},
                    "description": {"$first": "$details.description"},
                    "total_revenues": {"$sum": "$details.revenues_details"},
                    "total_expenditure": {"$sum": "$details.expenditure_details"},
                }
            },
            {
                "$match": {
                    "description": match
                }
            }
        ]

        results = self.collect.aggregate(pipeline)

        self.client.close()

        return results


class ConnectWorkDiary:
    def __init__(self):
        load_dotenv()
        MONGODB_URI = os.environ["MONGODB_URI"]

        self.client = MongoClient(MONGODB_URI, tls=True, tlsAllowInvalidCertificates=True, server_api=ServerApi('1'))

        try:
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)

        self.db = self.client.Accounting

        self.collect = self.db.workdiary

    def InsertData(self, post):
        try:
            self.collect.insert_one(post)
            # print(post_id)
        except Exception as e:
            print(e)

        # self.client.close()

    def QueryData(self):
        data_list = []
        for data in self.collect.find():
            data_list.append(data)

        # self.client.close()

        return data_list

    def UpdateData(self, data: dict):
        new_data = data
        id_pair = next(iter((data.items())))
        filter_id = {id_pair[0]: id_pair[1]}
        del new_data["_id"]

        self.collect.replace_one(filter_id, new_data)

    def DeleteData(self, data: dict):
        delete_target = data
        id_pair = next(iter((data.items())))
        target_id = {id_pair[0]: id_pair[1]}

        self.collect.delete_one(target_id)


if __name__ == "__main__":
    connection = ConnectWorkDiary()

    post = {
        "date": "2023/05/06",
        "description": "允薪營造-造橋",
        "spec": "SH-200",
        "quantity": "8H",
        "price": "2000",
        "amount": "",
        "remark": ""
    }
    #
    # pattern = re.compile(r"\d+")
    #
    # print(int(pattern.findall(post["quantity"])[0]))
    #
    # post["amount"] = int(pattern.findall(post["quantity"])[0]) * int(post["price"])
    # print(post)

    # try:
    #     connection.InsertData(post)
    # except Exception as e:
    #     print(e)

    try:
        query = connection.QueryData()
        for data in query:
            print(data)
    except Exception as e:
        print(e)
