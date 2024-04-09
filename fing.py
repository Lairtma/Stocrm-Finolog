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
        req = requests.post(url, json=params)
        json_acceptable_string = req.text.replace("'", "\"")
        lst = json.loads(json_acceptable_string)
        return lst

    def get_all_transaction(self):
        url = f"https://api.finolog.ru/v1/biz/{self.biz_id}/transaction" #обращаемся к ссылке
        params = {
            "api_token": self.api_token #параметр в виде апи токена

        }
        req = requests.get(url, params=params) #переменная req для получения данныех с источника
        # нераспределённые - category_id = 3 864177
        json_acceptable_string = req.text.replace("'", "\"") #замена ' на "
        lst = json.loads(json_acceptable_string) #преобразование json.obj в python.obj
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
        req = requests.put(url, json=params)
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

    def get_contractor_by_inn(self, inn):
        url = f"https://api.finolog.ru/v1/biz/{self.biz_id}/contractor"
        params = {
            "api_token": self.api_token,
            "inn": inn
        }
        req = requests.get(url, params=params)
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

    def get_all_contractors(self):
        url = f"https://api.finolog.ru/v1/biz/{self.biz_id}/contractor"
        params = {
            "api_token": self.api_token
        }
        req = requests.get(url, params=params)
        # нераспределённые - category_id = 3 822319
        json_acceptable_string = req.text.replace("'", "\"")
        lst = json.loads(json_acceptable_string)
        return lst

    def get_last_contractor(self):
        url = f"https://api.finolog.ru/v1/biz/{self.biz_id}/contractor"
        params = {
            "api_token": self.api_token
        }
        req = requests.get(url, params=params)
        # нераспределённые - category_id = 3 822319
        json_acceptable_string = req.text.replace("'", "\"")
        lst = json.loads(json_acceptable_string)
        return lst[0]

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

    def get_all_orders(self):
        url = f"https://api.finolog.ru/v1/biz/{self.biz_id}/orders/order"
        params = {
            "api_token": self.api_token
        }
        req = requests.get(url, params=params)
        json_acceptable_string = req.text.replace("'", "\"")
        lst = json.loads(json_acceptable_string)
        return lst

    def get_order_by_numb(self, number):
        url = f"https://api.finolog.ru/v1/biz/{self.biz_id}/orders/order"
        params = {
            "api_token": self.api_token,
            "number": number
        }
        req = requests.get(url, json=params)
        json_acceptable_string = req.text.replace("'", "\"")
        lst = json.loads(json_acceptable_string)
        return lst

    def get_last_order(self):
        url = f"https://api.finolog.ru/v1/biz/{self.biz_id}/orders/order"
        params = {
            "api_token": self.api_token
        }
        req = requests.get(url, params=params)
        json_acceptable_string = req.text.replace("'", "\"")
        lst = json.loads(json_acceptable_string)
        return lst[0]

    def del_order_by_id(self,id):
        url = f"https://api.finolog.ru/v1/biz/{self.biz_id}/orders/order/{id}"
        params = {
            "api_token": self.api_token,
        }
        req = requests.delete(url, params=params)
        json_acceptable_string = req.text.replace("'", "\"")
        lst = json.loads(json_acceptable_string)
        return lst

    def get_order_by_id(self,id):
        url = f"https://api.finolog.ru/v1/biz/{self.biz_id}/orders/order/{id}"
        params = {
            "api_token": self.api_token,
        }
        req = requests.get(url, params=params)
        json_acceptable_string = req.text.replace("'", "\"")
        lst = json.loads(json_acceptable_string)
        return lst

    def create_order(self,  *args, **kwargs):
        url = f"https://api.finolog.ru/v1/biz/{self.biz_id}/orders/order"
        params = {
            "api_token": self.api_token
        }
        for i in kwargs.keys():
            params[i] = kwargs[i]
        req = requests.post(url, json=params)
        json_acceptable_string = req.text.replace("'", "\"")
        lst = json.loads(json_acceptable_string)
        return lst

    def change_order_by_id(self, id,  *args, **kwargs):
        url = f"https://api.finolog.ru/v1/biz/{self.biz_id}/orders/order/{id}"
        params = {
            "api_token": self.api_token
        }
        for i in kwargs.keys():
            params[i] = kwargs[i]
        req = requests.put(url, json=params)
        json_acceptable_string = req.text.replace("'", "\"")
        lst = json.loads(json_acceptable_string)
        return lst

    def get_all_items(self):
        url = f"https://api.finolog.ru/v1/biz/{self.biz_id}/orders/item"
        params = {
            "api_token": self.api_token
        }
        req = requests.get(url, params=params)
        json_acceptable_string = req.text.replace("'", "\"")
        lst = json.loads(json_acceptable_string)
        return lst

    def add_package_item_by_id(self, package_id, item_id, count, price):
        url = f"https://api.finolog.ru/v1/biz/{self.biz_id}/orders/package/{package_id}/item"
        params = {
            "api_token": self.api_token,
            "count":count,
            "price":price,
            "item_id":item_id
        }
        req = requests.post(url, params=params)
        json_acceptable_string = req.text.replace("'", "\"")
        lst = json.loads(json_acceptable_string)
        return lst

    def get_item_by_id(self, id):
        url = f"https://api.finolog.ru/v1/biz/{self.biz_id}/orders/item/{id}"
        params = {
            "api_token": self.api_token,
        }
        req = requests.get(url, params=params)
        json_acceptable_string = req.text.replace("'", "\"")
        lst = json.loads(json_acceptable_string)
        return lst

    def update_package_by_id(self, package_id):
        url = f"https://api.finolog.ru/v1/biz/{self.biz_id}/orders/package/{package_id}"
        params = {
            "api_token": self.api_token
        }
        req = requests.put(url, params=params)
        json_acceptable_string = req.text.replace("'", "\"")
        lst = json.loads(json_acceptable_string)
        return lst

    def change_package_item_by_id(self, package_id, package_item_id, count, price):
        url = f"https://api.finolog.ru/v1/biz/{self.biz_id}/orders/package/{package_id}/item/{package_item_id}"
        params = {
            "api_token": self.api_token,
            "count": count,
            "price": price,
            "item_id": package_item_id
        }
        req = requests.put(url, params=params)
        json_acceptable_string = req.text.replace("'", "\"")
        lst = json.loads(json_acceptable_string)
        return lst

    def create_shipment_by_order_id(self, order_id):
        url = f"https://api.finolog.ru/v1/biz/{self.biz_id}/orders/document"
        order = self.get_order_by_id(order_id)
        params = {
            "api_token": self.api_token,
            "comment": "",
            "date": "2024-03-12",
            "from_contractor_id": None,
            "from_requisite_id": None,
            "items": order["package"]["items"],
            "kind": "shipment",
            "model_id": order_id,
            "model_type": "Order",
            "template": "stock",
            "to_contractor_draft": "",
            "to_contractor_id": None,
            "to_requisite_id": None,
            "vat_type": "included"
        }
        req = requests.post(url, json=params)
        json_acceptable_string = req.text.replace("'", "\"")
        lst = json.loads(json_acceptable_string)
        return lst


if __name__ == "__main__":
    fin = Finolog("hepV7NAnFgAshnDd90adec7e4d95088359e869f3e4f89e08riNSzPykUqS6fKWN", "43768")
    f = fin.get_contractor_by_inn(5044107254)
    print(f)
