import time

import requests
import json
import logging
from fing import Finolog
from datetime import datetime, timedelta


def filling_order(type, contr_var, deal_id):
    sto = Stocrm("13581_bf2b8cec383601bad6765d4b61240dbd", "v8-centr")
    fin = Finolog("hepV7NAnFgAshnDd90adec7e4d95088359e869f3e4f89e08riNSzPykUqS6fKWN", "43768")
    deal_description = f"По сделке: {deal_id}"
    new_order = fin.create_order(type)  # создаем новый заказ в finolog
    get_info_last_order = fin.get_last_order()  # получаем данные последнего созданного заказа
    last_order_id = get_info_last_order["id"]  # получаем id последнего созданного заказа из данных
    fin.change_order_by_id(last_order_id, buyer_id=contr_var, description=deal_description, status_id=60244, number=str(deal_id))  # изменяем заказ по id добавляя нужные параметры
    time.sleep(5)


def comparing_deals(sto_id):
    sto = Stocrm("13581_bf2b8cec383601bad6765d4b61240dbd", "v8-centr")
    fin = Finolog("hepV7NAnFgAshnDd90adec7e4d95088359e869f3e4f89e08riNSzPykUqS6fKWN", "43768")
    orders_list = fin.get_all_orders()
    for i in orders_list:
        if i['description'] == f"По сделке: {sto_id}":
            return i['id']


def order_creation_with_contr_data(deal_id):
    sto = Stocrm("13581_bf2b8cec383601bad6765d4b61240dbd", "v8-centr")
    fin = Finolog("hepV7NAnFgAshnDd90adec7e4d95088359e869f3e4f89e08riNSzPykUqS6fKWN", "43768")
    type = "out"
    deal_data = sto.get_leed_by_id(deal_id) #получаем info по определнной сделке stocrm с помощью её id
    contact_phone_by_leed_id = str(deal_data['RESPONSE']['DATA'][0]['CONTACT_PROPERTY_PHONE']) #получаем номер телефона из сделки storcrm
    contr_list_7 = fin.get_contractor_by_phone('7' + contact_phone_by_leed_id[1:])
    contr_list_8 = fin.get_contractor_by_phone('8' + contact_phone_by_leed_id[1:])
    if not contr_list_7 and not contr_list_8: #если такого контрагента не сущемтвует
        fin.create_contractor(name=deal_data['RESPONSE']['DATA'][0]['CONTACT_TITLE'],
                              phone=deal_data['RESPONSE']['DATA'][0]['CONTACT_PROPERTY_PHONE'], desc=deal_id)
        contr_id = fin.get_contractor_by_phone(deal_data['RESPONSE']['DATA'][0]['CONTACT_PROPERTY_PHONE'])
        filling_order(type, contr_id, deal_id)
    else: #такой контрагент уже существует
        contr_list_universal = contr_list_7 if not contr_list_8 else contr_list_8
        contr_id = contr_list_universal[0]['id']
        filling_order(type, contr_id, deal_id)


def works_and_parts_value(deal_id):
    sto = Stocrm("13581_bf2b8cec383601bad6765d4b61240dbd", "v8-centr")
    fin = Finolog("hepV7NAnFgAshnDd90adec7e4d95088359e869f3e4f89e08riNSzPykUqS6fKWN", "43768")
    fin_order_id = comparing_deals(deal_id) #данные о заказе из fin связанный с sto
    order_data = fin.get_order_by_id(fin_order_id)
    deal_data = sto.get_leed_by_id(deal_id) #данные о сделке stocrm
    orders_sum = float(deal_data['RESPONSE']['DATA'][0]['ORDERS_SUM']) #стоимость запчастей в заказе
    products_sum = (float(deal_data['RESPONSE']['DATA'][0]['OFFER_SUM']) - orders_sum) #стоимость работ в заказе
    package_id = order_data['package_id']
    if not order_data['package']['items']:
        if orders_sum != 0:
            fin.add_package_item_by_id(package_id, 115857, count=1, price=orders_sum) #добавление стоимости запчастей в заказ
        if products_sum != 0:
            fin.add_package_item_by_id(package_id, 153056, count=1, price=products_sum) #добавление стоимости работ в заказ
    else:
        if orders_sum != 0:
            fin.change_package_item_by_id(package_id, 115857, count=1, price=orders_sum)
        if products_sum != 0:
            fin.change_package_item_by_id(package_id, 153056, count=1, price=products_sum)
    fin.update_package_by_id(package_id)

def last_x_expenses(n):
    lst_n_operations = {'RESPONSE': {}}
    lst = sto.get_expenses_list(1)
    total_count = lst['RESPONSE']['TOTAL_COUNT']
    page = 1
    while total_count > 1000:
        total_count -= 1000
        page += 1
    lst = sto.get_expenses_list(page)
    lst_n_operations['RESPONSE']['DATA'] = lst['RESPONSE']['DATA'][-n:]
    lst_n_operations['RESPONSE']['DATA'].reverse()
    return lst_n_operations

class Stocrm:
    def __init__(self, api_token, domain):
        self.api_token = api_token
        self.domain = domain

    def get_dds(self):
        url = f"https://{self.domain}.stocrm.ru/api/external/v1/finances/get_filtered_transactions"
        params = {
            "SID": self.api_token,
            "LIMIT": 80,
        }
        req = requests.get(url, params=params)
        json_acceptable_string = req.text
        lst = json.loads(json_acceptable_string)
        return lst

    def get_leed_by_contact_id(self, id):
        url = f"https://{self.domain}.stocrm.ru/api/external/v1/offers/get_from_filter?SID={self.api_token}&FILTER[CONTACT_ID][0]={id}&REQUIRED_FIELDS[0]=WORKS_SUM&REQUIRED_FIELDS[1]=ORDERS_SUM"
        req = requests.get(url)
        json_acceptable_string = req.text.replace("'", "\"")
        lst = json.loads(json_acceptable_string)
        return lst

    def get_leed_by_id(self, id):
        url = f"https://{self.domain}.stocrm.ru/api/external/v1/offers/get_from_filter?SID={self.api_token}&FILTER[OFFER_ID][0]={id}&REQUIRED_FIELDS[0]=WORKS_SUM&REQUIRED_FIELDS[1]=ORDERS_SUM"
        req = requests.get(url)
        json_acceptable_string = req.text.replace("'", "\"")
        lst = json.loads(json_acceptable_string)
        return lst
    def get_works_from_deal_by_id(self, id):
        url = f"https://{self.domain}.stocrm.ru/api/external/v1/work/get_filtered?SID={self.api_token}&FILTER[OFFER_ID]={id}"
        req = requests.get(url)
        json_acceptable_string = req.text.replace("'", "\"")
        lst = json.loads(json_acceptable_string)
        return lst

    def get_products_from_deal_by_id(self, id):
        url = f"https://{self.domain}.stocrm.ru/api/external/v1/products/get_filtered_orders?SID={self.api_token}&FILTER[OFFER_ID]={id}"
        req = requests.get(url)
        json_acceptable_string = req.text.replace("'", "\"")
        lst = json.loads(json_acceptable_string)
        return lst


    def get_expenses_list(self, page):
        url = f"https://{self.domain}.stocrm.ru/api/external/v1/finances/expenses?SID={self.api_token}"
        params = {
            "PAGE": page,
            "LIMIT": 1000
        }
        req = requests.get(url, params=params)
        json_acceptable_string = req.text.replace("'", "\"")
        lst = json.loads(json_acceptable_string)
        return lst


sto = Stocrm("13581_bf2b8cec383601bad6765d4b61240dbd", "v8-centr")
fin = Finolog("hepV7NAnFgAshnDd90adec7e4d95088359e869f3e4f89e08riNSzPykUqS6fKWN", "43768")
used_id = []


sto = Stocrm("13581_bf2b8cec383601bad6765d4b61240dbd", "v8-centr")
fin = Finolog("hepV7NAnFgAshnDd90adec7e4d95088359e869f3e4f89e08riNSzPykUqS6fKWN", "43768")
used_id = []
if __name__ == "__main__":
    with open("used_id.txt") as fr:
        used_id = fr.readlines()
        for i in range(len(used_id)):
            used_id[i] = used_id[i].replace("\n", "")
    start_time = time.time()
    while True:    # основной цикл для повторения раз в 5 минут
        start_time = time.time()
        k = sto.get_dds()["RESPONSE"]["DATA"][::-1]     # получение последних 40 записей из ддс
        predoplata = [[], 0, [], 0, [], 0]
        polnaya = [[], 0, [], 0, [], 0]
        for i in k:
            if i["TRANSACTION_TYPE"] == "MOVE" and i["CURRENCY_TYPE"] == 'BANK_CARD' and (i["COMMENT_HUMAN"] == "Предоплата в сделку" or i["COMMENT_HUMAN"] == "Полная оплата"):
                date_0 = (datetime.now() - timedelta(days=0)).strftime('%d.%m.%Y')
                date_1 = (datetime.now() - timedelta(days=1)).strftime('%d.%m.%Y')
                data = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                date_2_of = (datetime.now() - timedelta(days=2)).strftime('%d.%m.%Y')
                date_3 = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
                date_2 = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
                timestamp = datetime.utcfromtimestamp(i['CUSTOM_DATE_CREATE']).strftime('%Y-%m-%d')
                if timestamp in used_id:
                    continue
                logging.error(timestamp)
                if data in timestamp or date_2 in timestamp or date_3 in timestamp:
                    res = [i["COMMENT_HUMAN"], float(i["CURRENCY_VALUE"]),
                           "физ. лицо" if "Физ. лицо" in i["FROM_ENTITY_TYPE_HUMAN"] else "юр. лицо"]
                    try:
                        res.append(i['FROM_ENTITY_FULL_NAME'])
                        res.append(i["OFFER_ID"])
                        leed = sto.get_leed_by_id(i["OFFER_ID"])["RESPONSE"]["DATA"][0]
                        if leed["OFFER_CUSTOMER_NAME"] == "V8.CENTER":
                            project = {39014: 359147, 32269: 358087}
                        elif leed["OFFER_CUSTOMER_NAME"] == "V8.CENTER Кузовной":
                            project = {39014: 359146, 32269: 353644}
                        else:
                            project = {}
                        res.append("8" + str(leed["CONTACT_PROPERTY_PHONE"][1::]))
                    except Exception as e:
                        res.append("Error")
                        requests.post(
                            "https://api.telegram.org/bot6923328005:AAFvq9YwSTLQLGbmfLkNZh-EKj7c1nNiEDY/sendMessage?chat_id=792154034&text=1")
                        requests.post("https://api.telegram.org/bot6923328005:AAFvq9YwSTLQLGbmfLkNZh-EKj7c1nNiEDY/sendMessage?chat_id=792154034&text=" + str(e))
                    print(res)  # сбор данных об оплате
                    if res[0] == "Предоплата в сделку":
                        if timestamp == date_2:
                            predoplata[1] += res[1]
                            predoplata[0].append([str(res[-2]), res[1], project])
                        elif timestamp == data:
                            predoplata[3] += res[1]
                            predoplata[2].append([str(res[-2]), res[1], project])
                        else:
                            predoplata[5] += res[1]
                            predoplata[4].append([str(res[-2]), res[1], project])
                    elif res[0] == "Полная оплата":
                        if timestamp == date_2:
                            polnaya[1] += res[1]
                            polnaya[0].append([str(res[-2]), res[1], project])
                        elif timestamp == data:
                            polnaya[3] += res[1]
                            polnaya[2].append([str(res[-2]), res[1], project])
                        else:
                            polnaya[5] += res[1]
                            polnaya[4].append([str(res[-2]), res[1], project])

            elif i["TRANSACTION_TYPE"] == "MOVE" and i["CURRENCY_TYPE"] == "SBP" and (i["COMMENT_HUMAN"] == "Предоплата в сделку" or i["COMMENT_HUMAN"] == "Полная оплата"):
                if str(i["ID"]) in used_id:  # пропуск уже добавленных
                    continue
                res = [i["COMMENT_HUMAN"], float(i["CURRENCY_VALUE"]),
                       "физ. лицо" if "Физ. лицо" in i["FROM_ENTITY_TYPE_HUMAN"] else "юр. лицо"]
                try:
                    res.append(i['FROM_ENTITY_FULL_NAME'])
                    res.append(i["OFFER_ID"])
                    leed = sto.get_leed_by_id(i["OFFER_ID"])["RESPONSE"]["DATA"][0]
                    if leed["OFFER_CUSTOMER_NAME"] == "V8.CENTER":
                        project = {39014: 359147, 32269: 358087}
                    elif leed["OFFER_CUSTOMER_NAME"] == "V8.CENTER Кузовной":
                        project = {39014: 359146, 32269: 353644}
                    else:
                        project = {}
                    res.append("8" + str(leed["CONTACT_PROPERTY_PHONE"][1::]))
                except Exception as e:
                    res.append("Error")
                    requests.post(
                        "https://api.telegram.org/bot6923328005:AAFvq9YwSTLQLGbmfLkNZh-EKj7c1nNiEDY/sendMessage?chat_id=792154034&text=2")
                    requests.post("https://api.telegram.org/bot6923328005:AAFvq9YwSTLQLGbmfLkNZh-EKj7c1nNiEDY/sendMessage?chat_id=792154034&text=" + str(e))
                if res[0] == "Предоплата в сделку":
                    f = ""
                    trans = fin.get_transaction_by_desc("СБП")
                    for tran in trans:
                        if tran["category_id"] == 3:
                            if int(res[1]) == tran["value"]:
                                f = tran
                                break
                    try:
                        if f:
                            deal = comparing_deals(i["OFFER_ID"])
                            if not deal:
                                order_creation_with_contr_data(i["OFFER_ID"])
                                works_and_parts_value(i["OFFER_ID"])
                            deal = comparing_deals(i["OFFER_ID"])
                            f = fin.change_transaction_by_id(f["id"], order_id=deal, attribute_values=project, category_id=1089484, description=f["description"] + ". По сделке " + str(res[-2]))
                            used_id.append(str(i["ID"]))
                    except Exception as e:
                        logging.error(e)
                        logging.error(res)
                        requests.post(
                            "https://api.telegram.org/bot6923328005:AAFvq9YwSTLQLGbmfLkNZh-EKj7c1nNiEDY/sendMessage?chat_id=792154034&text=3")
                        requests.post("https://api.telegram.org/bot6923328005:AAFvq9YwSTLQLGbmfLkNZh-EKj7c1nNiEDY/sendMessage?chat_id=792154034&text=" + str(e))
                elif res[0] == "Полная оплата":
                    order_sum = float(leed["ORDERS_SUM"])  # сбор стоимости работ и запчастей
                    works_sum = float(leed["OFFER_SUM"]) - float(leed["ORDERS_SUM"])
                    pre_trans_sum = float(leed["OFFER_SUM"]) - res[1]
                    trans = fin.get_transaction_by_desc("СБП")
                    f, pre_trans = "", ""
                    for tran in trans[::-1]:
                        if tran["category_id"] == 3:
                            if int(res[1]) == tran["value"]:
                                f = tran
                                break
                    pre_trans = fin.get_transaction_by_desc(str(res[-2]))
                    if len(pre_trans) > 1:
                        requests.post("https://api.telegram.org/bot6923328005:AAFvq9YwSTLQLGbmfLkNZh-EKj7c1nNiEDY/sendMessage?chat_id=792154034&text=" + ", ".join(list(map(str, res))) + "\n" + ", ".join(list(map(str, pre_trans))))
                    if pre_trans:
                        pre_trans = pre_trans[0]

                    try:
                        if f:
                            deal = comparing_deals(i["OFFER_ID"])
                            if not deal:
                                order_creation_with_contr_data(i["OFFER_ID"])
                                works_and_parts_value(i["OFFER_ID"])
                            deal = comparing_deals(i["OFFER_ID"])
                            f = fin.change_transaction_by_id(f["id"], order_id=deal, attribute_values=project, category_id=864177, description=f["description"] + ". По сделке " + str(res[-2]))
                            if pre_trans:
                                res = fin.change_transaction_by_id(pre_trans["id"], order_id=deal, attribute_values=project, category_id=866958)
                            used_id.append(str(i["ID"]))
                    except Exception as e:
                        logging.error(e)
                        logging.error(res)
                        requests.post(
                            "https://api.telegram.org/bot6923328005:AAFvq9YwSTLQLGbmfLkNZh-EKj7c1nNiEDY/sendMessage?chat_id=792154034&text=4")
                        requests.post("https://api.telegram.org/bot6923328005:AAFvq9YwSTLQLGbmfLkNZh-EKj7c1nNiEDY/sendMessage?chat_id=792154034&text=" + str(e))
                    try:
                        if pre_trans and f:
                            logging.error("SBP")
                            final_trans = f
                            contractor = f["contractor_id"]
                            if pre_trans["value"] == order_sum and final_trans["value"] == works_sum:   # всё правильно, добавление статей прихода
                                pre = fin.change_transaction_by_id(pre_trans["id"], attribute_values=project, category_id=866958)
                                f = fin.change_transaction_by_id(final_trans["id"], attribute_values=project, category_id=864177, description=f["description"] + ". По сделке " + str(res[-2]))
                            elif pre_trans["value"] < order_sum and final_trans["value"] > works_sum:   # разделение оплаты
                                pre = fin.change_transaction_by_id(pre_trans["id"], attribute_values=project, category_id=866958)
                                f = fin.split_transaction_by_id(final_trans["id"], [{"value": order_sum - pre_trans["value"],
                                                                                 "category_id": 866958,
                                                                                 "contractor_id": contractor},
                                                                                {"value": works_sum,
                                                                                 "category_id": 864177,
                                                                                 "contractor_id": contractor}])
                            elif pre_trans["value"] > order_sum and final_trans["value"] < works_sum:   # разделение предоплаты
                                f = fin.change_transaction_by_id(final_trans["id"], category_id=864177, description=f["description"] + ". По сделке " + str(res[-2]))
                                pre = fin.split_transaction_by_id(pre_trans["id"], [{"value": works_sum - final_trans["value"],
                                                                                 "category_id": 864177,
                                                                                 "contractor_id": contractor},
                                                                                {"value": order_sum,
                                                                                 "category_id": 866958,
                                                                                 "contractor_id": contractor}])
                            else:
                                pre = "Errorr"
                                f = "Errorr"
                            logging.error("------------")
                            logging.error(pre)
                            logging.error(f)
                    except Exception as e:
                        logging.error(e)
                        logging.error("Error")
                        requests.post(
                            "https://api.telegram.org/bot6923328005:AAFvq9YwSTLQLGbmfLkNZh-EKj7c1nNiEDY/sendMessage?chat_id=792154034&text=5")
                        requests.post("https://api.telegram.org/bot6923328005:AAFvq9YwSTLQLGbmfLkNZh-EKj7c1nNiEDY/sendMessage?chat_id=792154034&text=" + str(e))
            elif i["TRANSACTION_TYPE"] == "MOVE" and i["CURRENCY_TYPE"] == "CASH" and float(i["CURRENCY_VALUE"]) > 0 and (i["COMMENT_HUMAN"] == "Предоплата в сделку" or i["COMMENT_HUMAN"] == "Полная оплата"):
                if str(i["ID"]) in used_id:  # пропуск уже добавленных
                    continue
                used_id.append(str(i["ID"]))
                res = [i["COMMENT_HUMAN"], float(i["CURRENCY_VALUE"]), "физ. лицо" if "Физ. лицо" in i["FROM_ENTITY_TYPE_HUMAN"] else "юр. лицо"]
                try:
                    res.append(i['FROM_ENTITY_FULL_NAME'])
                    res.append(i["OFFER_ID"])
                    leed = sto.get_leed_by_id(i["OFFER_ID"])["RESPONSE"]["DATA"][0]
                    if leed["OFFER_CUSTOMER_NAME"] == "V8.CENTER":
                        project = {39014: 359147, 32269: 358087}
                    elif leed["OFFER_CUSTOMER_NAME"] == "V8.CENTER Кузовной":
                        project = {39014: 359146, 32269: 353644}
                    else:
                        project = {}
                    res.append("8" + str(leed["CONTACT_PROPERTY_PHONE"][1::]))
                except Exception:
                    res.append("Error")
                logging.error(res)  # сбор данных об оплате

                if res[0] == "Предоплата в сделку":

                    contractor = fin.get_contractor_by_phone(res[-1])  # получение контрагента в финологе по номеру телефона или создание нового
                    if contractor:
                        contractor = contractor[0]
                    else:
                        fin.create_contractor(res[-3], res[-1], res[-4])
                        contractor = fin.get_contractor_by_phone(res[-1])[0]
                    deal = comparing_deals(i["OFFER_ID"])
                    if not deal:
                        order_creation_with_contr_data(i["OFFER_ID"])
                        works_and_parts_value(i["OFFER_ID"])
                    deal = comparing_deals(i["OFFER_ID"])
                    f = fin.create_transaction(to_id=166457, order_id=deal, attribute_values=project, date=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                                               category_id=1089484, contractor_id=contractor['id'], value=res[1],
                                               status="regular", description="Предоплата по " + str(res[-2]))  # создание предоплаты
                elif res[0] == "Полная оплата":

                    contractor = fin.get_contractor_by_phone(res[-1])   # получение контрагента в финологе по номеру телефона или создание нового
                    if contractor:
                        contractor = contractor[0]
                    else:
                        fin.create_contractor(res[-3], res[-1], res[-4])
                        contractor = fin.get_contractor_by_phone(res[-1])[0]
                    pre_trans = fin.get_transaction_by_desc(str(res[-2]))
                    deal = comparing_deals(i["OFFER_ID"])
                    if not deal:
                        order_creation_with_contr_data(i["OFFER_ID"])
                        works_and_parts_value(i["OFFER_ID"])
                    deal = comparing_deals(i["OFFER_ID"])
                    if len(pre_trans) > 1:
                        requests.post("https://api.telegram.org/bot6923328005:AAFvq9YwSTLQLGbmfLkNZh-EKj7c1nNiEDY/sendMessage?chat_id=792154034&text=" + ", ".join(list(map(str, res))) + "\n" + ", ".join(list(map(str, pre_trans))))
                    final_trans = fin.create_transaction(order_id=deal, category_id=864177, attribute_values=project,
                                                         contractor_id=contractor['id'], date=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                                                         to_id=166457, value=res[1], status="regular",
                                                         description=str(res[-2]))   # создание оплаты
                    try:
                        if pre_trans:
                            pre_trans = pre_trans[0]
                            print(pre_trans, final_trans, end="\n")
                            order_sum = float(leed["ORDERS_SUM"])   # сбор стоимости работ и запчастей
                            works_sum = float(leed["OFFER_SUM"]) - float(leed["ORDERS_SUM"])

                            if pre_trans["value"] == order_sum and final_trans["value"] == works_sum:   # всё правильно, добавление статей прихода
                                pre = fin.change_transaction_by_id(pre_trans["id"], category_id=866958)
                                f = fin.change_transaction_by_id(final_trans["id"], category_id=864177)
                            elif pre_trans["value"] < order_sum and final_trans["value"] > works_sum:   # разделение оплаты
                                pre = fin.change_transaction_by_id(pre_trans["id"], category_id=866958)
                                f = fin.split_transaction_by_id(final_trans["id"], [{"value": order_sum - pre_trans["value"],
                                                                                 "category_id": 866958,
                                                                                 "contractor_id": contractor['id']},
                                                                                {"value": works_sum,
                                                                                 "category_id": 864177,
                                                                                 "contractor_id": contractor['id']}])
                            elif pre_trans["value"] > order_sum and final_trans["value"] < works_sum:   # разделение предоплаты
                                f = fin.change_transaction_by_id(final_trans["id"], category_id=864177)
                                pre = fin.split_transaction_by_id(pre_trans["id"], [{"value": works_sum - final_trans["value"],
                                                                                 "category_id": 864177,
                                                                                 "contractor_id": contractor['id']},
                                                                                {"value": order_sum,
                                                                                 "category_id": 866958,
                                                                                 "contractor_id": contractor['id']}])
                            else:
                                pre = "Errorr"
                                f = "Errorr"
                            logging.error(str(pre))
                            logging.error(str(f))
                    except Exception as e:
                        logging.error(e)
                        logging.error("Error")
            elif i["COMMENT_HUMAN"] == "Полный возврат" and i["TRANSACTION_TYPE"] == "MOVE" and float(i["CURRENCY_VALUE"]) != 0:
                if str(i["ID"]) in used_id:
                    continue
                used_id.append(str(i["ID"]))
                res = [i["COMMENT_HUMAN"], float(i["CURRENCY_VALUE"]),
                       "физ. лицо" if "Физ. лицо" in i["DESTINATION_ENTITY_TYPE_HUMAN"] else "юр. лицо"]
                try:
                    res.append(i['DESTINATION_ENTITY_FULL_NAME'])
                    res.append(i['FROM_ENTITY_ID'])
                    leed = sto.get_leed_by_id(i['FROM_ENTITY_ID'])["RESPONSE"]["DATA"][0]
                    res.append("8" + str(leed["CONTACT_PROPERTY_PHONE"][1::]))
                except Exception:
                    res.append("Error")
                logging.error(res)   # сбор информации о возврате
                contractor = fin.get_contractor_by_phone(res[-1])   # получение контрагента в финологе по номеру телефона или создание нового
                if contractor:
                    contractor = contractor[0]
                else:
                    fin.create_contractor(res[-3], res[-1], res[-4])
                    contractor = fin.get_contractor_by_phone(res[-1])[0]
                deal = comparing_deals(i["OFFER_ID"])
                if not deal:
                    order_creation_with_contr_data(i["OFFER_ID"])
                    works_and_parts_value(i["OFFER_ID"])
                deal = comparing_deals(i["OFFER_ID"])
                f = fin.create_transaction(from_id=166457, order_id=deal, date=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), category_id=1013974, contractor_id=contractor['id'],
                                       value=-1 * int(res[1]), status="regular", description="Возврат по " + str(res[-2]))

        trans = fin.get_transaction_by_desc("Зачисление средств по терминалам эквайринга от")
        date_2 = [[], []]
        date = [[], []]
        date_3 = [[], []]
        st = f"Зачисление средств по терминалам эквайринга от {date_0}. Без НДС. По сделке "
        st_1 = f"Зачисление средств по терминалам эквайринга от {date_1}. Без НДС. По сделке "
        st_2 = f"Зачисление средств по терминалам эквайринга от {date_2_of}. Без НДС. По сделке "
        for i in predoplata[0]:
            date_2[0].append({"value": i[1], "category_id": 866958, "description": st_1 + i[0], "contractor_id": trans[0]["contractor_id"], "attribute_values":i[2]})
        for i in predoplata[2]:
            date[0].append({"value": i[1], "category_id": 866958, "description": st + i[0], "contractor_id": trans[0]["contractor_id"], "attribute_values":i[2]})
        for i in predoplata[4]:
            date_3[0].append({"value": i[1], "category_id": 866958, "description": st_2 + i[0],
                            "contractor_id": trans[0]["contractor_id"], "attribute_values":i[2]})
        for i in polnaya[4]:
            date_3[1].append({"value": i[1], "category_id": 864177, "description": st_2 + i[0],
                              "contractor_id": trans[0]["contractor_id"], "attribute_values":i[2]})
        for i in polnaya[0]:
            date_2[1].append({"value": i[1], "category_id": 864177, "description": st_1 + i[0], "contractor_id": trans[0]["contractor_id"], "attribute_values":i[2]})
        for i in polnaya[2]:
            date[1].append({"value": i[1], "category_id": 864177, "description": st + i[0], "contractor_id": trans[0]["contractor_id"], "attribute_values":i[2]})
        res = ""
        logging.error(date)
        logging.error(date_2)
        logging.error(date_3)
        for i in trans:
            if date_0 in i['description']:
                if (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d') not in used_id:
                    used_id.append((datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'))
                    if i["value"] == predoplata[3] and i["account_id"] == 166458:
                        if len(date[0]) != 1:
                            for j in range(len(date[0])):
                                idesc = int(date[0][j]["description"].split("По сделке ")[-1])
                                deal = comparing_deals(idesc)
                                if not deal:
                                    order_creation_with_contr_data(idesc)
                                    works_and_parts_value(idesc)
                                deal = comparing_deals(idesc)
                                date[0][j]["order_id"] = deal
                            res = fin.split_transaction_by_id(i["id"], date[0])
                        else:
                            idesc = int(date[0][0]["description"].split("По сделке ")[-1])
                            deal = comparing_deals(idesc)
                            if not deal:
                                order_creation_with_contr_data(idesc)
                                works_and_parts_value(idesc)
                            deal = comparing_deals(idesc)
                            res = fin.change_transaction_by_id(i["id"], description=date[0][0]["description"], order_id=deal, category_id=866958, attribute_values=predoplata[2][0][2])
                    elif i["value"] == polnaya[3] and i["account_id"] == 166455:
                        if len(date[1]) != 1:
                            for j in range(len(date[1])):
                                idesc = int(date[1][j]["description"].split("По сделке ")[-1])
                                deal = comparing_deals(idesc)
                                if not deal:
                                    order_creation_with_contr_data(idesc)
                                    works_and_parts_value(idesc)
                                deal = comparing_deals(idesc)
                                date[1][j]["order_id"] = deal
                            res = fin.split_transaction_by_id(i["id"], date[1])
                        else:
                            idesc = int(date[1][0]["description"].split("По сделке ")[-1])
                            deal = comparing_deals(idesc)
                            if not deal:
                                order_creation_with_contr_data(idesc)
                                works_and_parts_value(idesc)
                            deal = comparing_deals(idesc)
                            res = fin.change_transaction_by_id(i["id"], description=date[1][0]["description"], order_id=deal, category_id=864177, attribute_values=polnaya[2][0][2])
                    elif i["value"] == predoplata[3] + polnaya[3]:
                        for j in range(len(date[0])):
                            idesc = int(date[0][j]["description"].split("По сделке ")[-1])
                            deal = comparing_deals(idesc)
                            if not deal:
                                order_creation_with_contr_data(idesc)
                                works_and_parts_value(idesc)
                            deal = comparing_deals(idesc)
                            date[0][j]["order_id"] = deal
                        for j in range(len(date[1])):
                            idesc = int(date[1][j]["description"].split("По сделке ")[-1])
                            deal = comparing_deals(idesc)
                            if not deal:
                                order_creation_with_contr_data(idesc)
                                works_and_parts_value(idesc)
                            deal = comparing_deals(idesc)
                            date[1][j]["order_id"] = deal
                        res = fin.split_transaction_by_id(i["id"], date[0] + date[1])
                    elif len(date[0] + date[1]) != 0:
                        for j in range(len(date[0])):
                            idesc = int(date[0][j]["description"].split("По сделке ")[-1])
                            deal = comparing_deals(idesc)
                            if not deal:
                                order_creation_with_contr_data(idesc)
                                works_and_parts_value(idesc)
                            deal = comparing_deals(idesc)
                            date[0][j]["order_id"] = deal
                        for j in range(len(date[1])):
                            idesc = int(date[1][j]["description"].split("По сделке ")[-1])
                            deal = comparing_deals(idesc)
                            if not deal:
                                order_creation_with_contr_data(idesc)
                                works_and_parts_value(idesc)
                            deal = comparing_deals(idesc)
                            date[1][j]["order_id"] = deal
                        date[1].append({"attribute_values": {}, "value": i["value"] - (predoplata[3] + polnaya[3]), "category_id": 3, "description": st[:-12:], "contractor_id": i["contractor_id"]})
                        res = fin.split_transaction_by_id(i["id"], date[0] + date[1])
                    else:
                        requests.post(
                            "https://api.telegram.org/bot6923328005:AAFvq9YwSTLQLGbmfLkNZh-EKj7c1nNiEDY/sendMessage?chat_id=792154034&text=Error with date " + str(date_0))
            if date_1 in i['description']:
                if (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d') not in used_id:
                    used_id.append((datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'))
                    if i["value"] == predoplata[1] and i["account_id"] == 166458:
                        if len(date_2[0]) != 1:
                            for j in range(len(date_2[0])):
                                idesc = int(date_2[0][j]["description"].split("По сделке ")[-1])
                                deal = comparing_deals(idesc)
                                if not deal:
                                    order_creation_with_contr_data(idesc)
                                    works_and_parts_value(idesc)
                                deal = comparing_deals(idesc)
                                date_2[0][j]["order_id"] = deal
                            res = fin.split_transaction_by_id(i["id"], date_2[0])
                        else:
                            idesc = int(date_2[0][0]["description"].split("По сделке ")[-1])
                            deal = comparing_deals(idesc)
                            if not deal:
                                order_creation_with_contr_data(idesc)
                                works_and_parts_value(idesc)
                            deal = comparing_deals(idesc)
                            res = fin.change_transaction_by_id(i["id"], description=date_2[0][0]["description"], order_id=deal, category_id=866958, attribute_values=predoplata[0][0][2])
                    elif i["value"] == polnaya[1] and i["account_id"] == 166455:
                        if len(date_2[1]) != 1:
                            for j in range(len(date_2[1])):
                                idesc = int(date_2[1][j]["description"].split("По сделке ")[-1])
                                deal = comparing_deals(idesc)
                                if not deal:
                                    order_creation_with_contr_data(idesc)
                                    works_and_parts_value(idesc)
                                deal = comparing_deals(idesc)
                                date_2[1][j]["order_id"] = deal
                            res = fin.split_transaction_by_id(i["id"], date_2[1])
                        else:
                            idesc = int(date_2[1][0]["description"].split("По сделке ")[-1])
                            deal = comparing_deals(idesc)
                            if not deal:
                                order_creation_with_contr_data(idesc)
                                works_and_parts_value(idesc)
                            deal = comparing_deals(idesc)
                            res = fin.change_transaction_by_id(i["id"], description=date_2[1][0]["description"], order_id=deal, category_id=864177, attribute_values=polnaya[0][0][2])
                    elif i["value"] == predoplata[1] + polnaya[1]:
                        for j in range(len(date_2[0])):
                            idesc = int(date_2[0][j]["description"].split("По сделке ")[-1])
                            deal = comparing_deals(idesc)
                            if not deal:
                                order_creation_with_contr_data(idesc)
                                works_and_parts_value(idesc)
                            deal = comparing_deals(idesc)
                            date_2[0][j]["order_id"] = deal
                        for j in range(len(date_2[1])):
                            idesc = int(date_2[1][j]["description"].split("По сделке ")[-1])
                            deal = comparing_deals(idesc)
                            if not deal:
                                order_creation_with_contr_data(idesc)
                                works_and_parts_value(idesc)
                            deal = comparing_deals(idesc)
                            date_2[1][j]["order_id"] = deal
                        res = fin.split_transaction_by_id(i["id"], date_2[0] + date_2[1])
                    elif len(date_2[0] + date_2[1]) != 0:
                        for j in range(len(date_2[0])):
                            idesc = int(date_2[0][j]["description"].split("По сделке ")[-1])
                            deal = comparing_deals(idesc)
                            if not deal:
                                order_creation_with_contr_data(idesc)
                                works_and_parts_value(idesc)
                            deal = comparing_deals(idesc)
                            date_2[0][j]["order_id"] = deal
                        for j in range(len(date_2[1])):
                            idesc = int(date_2[1][j]["description"].split("По сделке ")[-1])
                            deal = comparing_deals(idesc)
                            if not deal:
                                order_creation_with_contr_data(idesc)
                                works_and_parts_value(idesc)
                            deal = comparing_deals(idesc)
                            date_2[1][j]["order_id"] = deal
                        date_2[1].append({"attribute_values": {}, "value": i["value"] - (predoplata[1] + polnaya[1]), "category_id": 3, "description": st_1[:-12:], "contractor_id": i["contractor_id"]})
                        res = fin.split_transaction_by_id(i["id"], date_2[0] + date_2[1])
                    else:
                        requests.post(
                            "https://api.telegram.org/bot6923328005:AAFvq9YwSTLQLGbmfLkNZh-EKj7c1nNiEDY/sendMessage?chat_id=792154034&text=Error with date " + str(date_1))
            if date_2_of in i['description']:
                if (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d') not in used_id:
                    used_id.append((datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'))
                    if i["value"] == predoplata[5] and i["account_id"] == 166458:
                        if len(date_3[0]) != 1:
                            for j in range(len(date_3[0])):
                                idesc = int(date_3[0][j]["description"].split("По сделке ")[-1])
                                deal = comparing_deals(idesc)
                                if not deal:
                                    order_creation_with_contr_data(idesc)
                                    works_and_parts_value(idesc)
                                deal = comparing_deals(idesc)
                                date_3[0][j]["order_id"] = deal
                            res = fin.split_transaction_by_id(i["id"], date_3[0])
                        else:
                            idesc = int(date_3[0][0]["description"].split("По сделке ")[-1])
                            deal = comparing_deals(idesc)
                            if not deal:
                                order_creation_with_contr_data(idesc)
                                works_and_parts_value(idesc)
                            deal = comparing_deals(idesc)
                            res = fin.change_transaction_by_id(i["id"], description=date_3[0][0]["description"], order_id=deal, category_id=866958, attribute_values=predoplata[4][0][2])
                    elif i["value"] == polnaya[5] and i["account_id"] == 166455:
                        if len(date_3[1]) != 1:
                            for j in range(len(date_3[1])):
                                idesc = int(date_3[1][j]["description"].split("По сделке ")[-1])
                                deal = comparing_deals(idesc)
                                if not deal:
                                    order_creation_with_contr_data(idesc)
                                    works_and_parts_value(idesc)
                                deal = comparing_deals(idesc)
                                date_3[1][j]["order_id"] = deal
                            res = fin.split_transaction_by_id(i["id"], date_3[1])
                        else:
                            idesc = int(date_3[1][0]["description"].split("По сделке ")[-1])
                            deal = comparing_deals(idesc)
                            if not deal:
                                order_creation_with_contr_data(idesc)
                                works_and_parts_value(idesc)
                            deal = comparing_deals(idesc)
                            res = fin.change_transaction_by_id(i["id"], description=date_3[1][0]["description"], order_id=deal, category_id=864177, attribute_values=polnaya[4][0][2])
                    elif i["value"] == predoplata[5] + polnaya[5]:
                        for j in range(len(date_3[0])):
                            idesc = int(date_3[0][j]["description"].split("По сделке ")[-1])
                            deal = comparing_deals(idesc)
                            if not deal:
                                order_creation_with_contr_data(idesc)
                                works_and_parts_value(idesc)
                            deal = comparing_deals(idesc)
                            date_3[0][j]["order_id"] = deal
                        for j in range(len(date_3[1])):
                            idesc = int(date_3[1][j]["description"].split("По сделке ")[-1])
                            deal = comparing_deals(idesc)
                            if not deal:
                                order_creation_with_contr_data(idesc)
                                works_and_parts_value(idesc)
                            deal = comparing_deals(idesc)
                            date_3[1][j]["order_id"] = deal
                        res = fin.split_transaction_by_id(i["id"], date_3[0] + date_3[1])
                    elif len(date_3[0] + date_3[1]) != 0:
                        for j in range(len(date_3[0])):
                            idesc = int(date_3[0][j]["description"].split("По сделке ")[-1])
                            deal = comparing_deals(idesc)
                            if not deal:
                                order_creation_with_contr_data(idesc)
                                works_and_parts_value(idesc)
                            deal = comparing_deals(idesc)
                            date_3[0][j]["order_id"] = deal
                        for j in range(len(date_3[1])):
                            idesc = int(date_3[1][j]["description"].split("По сделке ")[-1])
                            deal = comparing_deals(idesc)
                            if not deal:
                                order_creation_with_contr_data(idesc)
                                works_and_parts_value(idesc)
                            deal = comparing_deals(idesc)
                            date_3[1][j]["order_id"] = deal
                        date_3[1].append({"attribute_values": {}, "value": i["value"] - (predoplata[5] + polnaya[5]), "category_id": 3, "description": st_2[:-12:], "contractor_id": i["contractor_id"]})
                        res = fin.split_transaction_by_id(i["id"], date_3[0] + date_3[1])
                    else:
                        requests.post(
                            "https://api.telegram.org/bot6923328005:AAFvq9YwSTLQLGbmfLkNZh-EKj7c1nNiEDY/sendMessage?chat_id=792154034&text=Error with date " + str(date_2))
            if res:
                logging.error(res)
                res = ""
        if len(used_id) > 100:
            used_id = used_id[50::]   # очищение памяти
        with open("used_id.txt", "w") as fw:   # сохранение добавленных записей
            for i in used_id:
                fw.write(str(i) + "\n")
        while time.time() - start_time < 300:   # пауза в 5 минут - время работы
            time.sleep(10)
