import time

import requests
import json
from fing import Finolog
from datetime import datetime


class Stocrm:
    def __init__(self, api_token, domain):
        self.api_token = api_token
        self.domain = domain

    def get_dds(self):
        url = f"https://{self.domain}.stocrm.ru/api/external/v1/finances/get_filtered_transactions"
        params = {
            "SID": self.api_token,
            "LIMIT": 40,
        }
        req = requests.get(url, params=params)
        json_acceptable_string = req.text.replace("'", "\"")
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


sto = Stocrm("13581_bf2b8cec383601bad6765d4b61240dbd", "v8-centr")  # подключение по api к stocrm и финолог
fin = Finolog("hepV7NAnFgAshnDd90adec7e4d95088359e869f3e4f89e08riNSzPykUqS6fKWN", "43768")

used_id = []    # получение списка добавленных транзакций
with open("used_id.txt") as fr:
    used_id = fr.readlines()
    for i in range(len(used_id)):
        used_id[i] = int(used_id[i].replace("\n", ""))

while True:    # основной цикл для повторения раз в 5 минут
    start_time = time.time()

    k = sto.get_dds()["RESPONSE"]["DATA"][::-1]     # получение последних 40 записей из ддс
    for i in k:
        if i["TRANSACTION_TYPE"] == "MOVE" and i["CURRENCY_TYPE"] == "CASH" and float(i["CURRENCY_VALUE"]) > 0 and (i["COMMENT_HUMAN"] == "Предоплата в сделку" or i["COMMENT_HUMAN"] == "Полная оплата"):
            if i["ID"] in used_id:  # пропуск уже добавленных
                continue
            used_id.append(i["ID"])
            res = [i["COMMENT_HUMAN"], float(i["CURRENCY_VALUE"]), "физ. лицо" if "Физ. лицо" in i["FROM_ENTITY_TYPE_HUMAN"] else "юр. лицо"]
            try:
                res.append(i['FROM_ENTITY_FULL_NAME'])
                res.append(i["OFFER_ID"])
                leed = sto.get_leed_by_id(i["OFFER_ID"])["RESPONSE"]["DATA"][0]
                res.append("8" + str(leed["CONTACT_PROPERTY_PHONE"][1::]))
            except Exception:
                res.append("Error")
            print(res)  # сбор данных об оплате

            if res[0] == "Предоплата в сделку":

                contractor = fin.get_contractor_by_phone(res[-1])  # получение контрагента в финологе по номеру телефона или создание нового
                if contractor:
                    contractor = contractor[0]
                else:
                    fin.create_contractor(res[-3], res[-1], res[-4])
                    contractor = fin.get_contractor_by_phone(res[-1])[0]
                f = fin.create_transaction(to_id=166457, date=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                                           category_id=3, contractor_id=contractor['id'], value=res[1],
                                           status="regular", description="Предоплата по " + str(res[-2]))  # создание предоплаты
            elif res[0] == "Полная оплата":

                contractor = fin.get_contractor_by_phone(res[-1])   # получение контрагента в финологе по номеру телефона или создание нового
                if contractor:
                    contractor = contractor[0]
                else:
                    fin.create_contractor(res[-3], res[-1], res[-4])
                    contractor = fin.get_contractor_by_phone(res[-1])[0]
                final_trans = fin.create_transaction(category_id=864177,
                                                     contractor_id=contractor['id'], date=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                                                     to_id=166457, value=res[1], status="regular",
                                                     description=res[-2])   # создание оплаты
                pre_trans = fin.get_transaction_by_desc("Предоплата по " + str(res[-2]))   # поиск предоплаты
                try:
                    if len(pre_trans) != 0:
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
                        print(pre, f, end="\n")
                except Exception as e:
                    print(e)
                    print("Error")
        elif i["COMMENT_HUMAN"] == "Полный возврат" and i["TRANSACTION_TYPE"] == "MOVE":
            if i["ID"] in used_id:
                continue
            used_id.append(i["ID"])
            res = [i["COMMENT_HUMAN"], float(i["CURRENCY_VALUE"]),
                   "физ. лицо" if "Физ. лицо" in i["DESTINATION_ENTITY_TYPE_HUMAN"] else "юр. лицо"]
            try:
                res.append(i['DESTINATION_ENTITY_FULL_NAME'])
                res.append(i['FROM_ENTITY_ID'])
                leed = sto.get_leed_by_id(i['FROM_ENTITY_ID'])["RESPONSE"]["DATA"][0]
                res.append("8" + str(leed["CONTACT_PROPERTY_PHONE"][1::]))
            except Exception:
                res.append("Error")
            print(res)   # сбор информации о возврате
            contractor = fin.get_contractor_by_phone(res[-1])   # получение контрагента в финологе по номеру телефона или создание нового
            if contractor:
                contractor = contractor[0]
            else:
                fin.create_contractor(res[-3], res[-1], res[-4])
                contractor = fin.get_contractor_by_phone(res[-1])[0]
            f = fin.create_transaction(from_id=166457, date=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), category_id=1013974, contractor_id=contractor['id'],
                                   value=-1 * int(res[1]), status="regular", description="Возврат по " + str(res[-2]))

    exit(0)

    if len(used_id) > 100:
        used_id = used_id[50::]   # очищение памяти
    with open("used_id.txt", "w") as fw:   # сохранение добавленных записей
        for i in used_id:
            fw.write(str(i) + "\n")
    while time.time() - start_time < 300:   # пауза в 5 минут - время работы
        print(time.time() - start_time)
        time.sleep(10)
