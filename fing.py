import requests
import json


class Finolog:
    def __init__(self, api_token, biz_id):
        self.api_token = api_token
        self.biz_id = biz_id

    def create_transaction(self, *args, **kwargs):
        url = f"https://api.finolog.ru/v1/biz/{self.biz_id}/transaction"
        params = {
            "api_token": self.api_token
        }
        for i in kwargs.keys():
            params[i] = kwargs[i]
        req = requests.post(url, data=params)
        # нераспределённые - category_id = 3 864177
        json_acceptable_string = req.text.replace("'", "\"")
        lst = json.loads(json_acceptable_string)
        return lst

    def get_all_transaction(self):
        url = f"https://api.finolog.ru/v1/biz/{self.biz_id}/transaction"
        params = {
            "api_token": self.api_token
        }
        req = requests.get(url, params=params)
        # нераспределённые - category_id = 3 864177
        json_acceptable_string = req.text.replace("'", "\"")
        lst = json.loads(json_acceptable_string)
        return lst

    def get_transaction_by_id(self, id):
        url = f"https://api.finolog.ru/v1/biz/{self.biz_id}/transaction/{id}"
        params = {
            "api_token": self.api_token
        }
        req = requests.get(url, params=params)
        json_acceptable_string = req.text.replace("'", "\"")
        lst = json.loads(json_acceptable_string)
        return lst

    def get_transaction_by_desc(self, desc):
        url = f"https://api.finolog.ru/v1/biz/{self.biz_id}/transaction"
        params = {
            "api_token": self.api_token,
            "description": desc
        }
        req = requests.get(url, params=params)
        json_acceptable_string = req.text.replace("'", "\"")
        lst = json.loads(json_acceptable_string)
        return lst

    def change_transaction_by_id(self, id, *args, **kwargs):
        url = f"https://api.finolog.ru/v1/biz/{self.biz_id}/transaction/{id}"
        params = {
            "api_token": self.api_token
        }
        for i in kwargs.keys():
            params[i] = kwargs[i]
        req = requests.put(url, params=params)
        json_acceptable_string = req.text.replace("'", "\"")
        lst = json.loads(json_acceptable_string)
        return lst

    def get_category_by_id(self, id):
        url = f"https://api.finolog.ru/v1/biz/{self.biz_id}/category/{id}"
        params = {
            "api_token": self.api_token
        }
        req = requests.get(url, params=params)
        json_acceptable_string = req.text.replace("'", "\"")
        lst = json.loads(json_acceptable_string)
        return lst

    def get_contractor_by_phone(self, phone):
        url = f"https://api.finolog.ru/v1/biz/{self.biz_id}/contractor"
        params = {
            "api_token": self.api_token,
            "query": phone
        }
        req = requests.get(url, params=params)
        # нераспределённые - category_id = 3 822319
        json_acceptable_string = req.text.replace("'", "\"")
        lst = json.loads(json_acceptable_string)
        return lst

    def create_contractor(self, name, phone, desc):
        url = f"https://api.finolog.ru/v1/biz/{self.biz_id}/contractor"
        params = {
            "api_token": self.api_token,
            "name": name,
            "phone": phone,
            "description": desc,
        }
        req = requests.post(url, params=params)
        # нераспределённые - category_id = 3 822319
        json_acceptable_string = req.text.replace("'", "\"")
        lst = json.loads(json_acceptable_string)
        return lst

    def get_all_category(self):
        url = f"https://api.finolog.ru/v1/biz/{self.biz_id}/category"
        params = {
            "api_token": self.api_token
        }
        req = requests.get(url, params=params)
        # нераспределённые - category_id = 3 822319
        json_acceptable_string = req.text.replace("'", "\"")
        lst = json.loads(json_acceptable_string)
        return lst

    def change_category_by_id(self, id, *args, **kwargs):
        url = f"https://api.finolog.ru/v1/biz/{self.biz_id}/category/{id}"
        params = {
            "api_token": self.api_token
        }
        for i in kwargs.keys():
            params[i] = kwargs[i]
        req = requests.put(url, params=params)
        json_acceptable_string = req.text.replace("'", "\"")
        lst = json.loads(json_acceptable_string)
        return lst

    def del_category_by_id(self, id):
        url = f"https://api.finolog.ru/v1/biz/{self.biz_id}/category/{id}"
        params = {
            "api_token": self.api_token
        }
        req = requests.delete(url, params=params)
        json_acceptable_string = req.text.replace("'", "\"")
        lst = json.loads(json_acceptable_string)
        return lst

    def split_transaction_by_id(self, id, items):
        url = f"https://api.finolog.ru/v1/biz/{self.biz_id}/transaction/{id}/split"
        params = {
            "api_token": self.api_token
        }
        data = {
            "items": items
        }
        req = requests.post(url, params=params, json=data)
        json_acceptable_string = req.text.replace("'", "\"")
        lst = json.loads(json_acceptable_string)
        return lst


if __name__ == "__main__":
    fin = Finolog("hepV7NAnFgAshnDd90adec7e4d95088359e869f3e4f89e08riNSzPykUqS6fKWN", "43768")
    k = fin.get_all_category()
    f = fin.get_contractor_by_phone(89772518087)[0]
    print(1)
