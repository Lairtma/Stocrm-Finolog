import time
import requests
import json
import logging
from fing import Finolog
from datetime import datetime, timedelta


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


sto = Stocrm("13581_bf2b8cec383601bad6765d4b61240dbd", "v8-centr")
fin = Finolog("hepV7NAnFgAshnDd90adec7e4d95088359e869f3e4f89e08riNSzPykUqS6fKWN", "43768")
used_id = []
"""
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
                        project = 358087
                    elif leed["OFFER_CUSTOMER_NAME"] == "V8.CENTER Кузовной":
                        project = 353644
                    else:
                        project = 345944
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
                    project = 358087
                elif leed["OFFER_CUSTOMER_NAME"] == "V8.CENTER Кузовной":
                    project = 353644
                else:
                    project = 345944
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
                        f = fin.change_transaction_by_id(f["id"], project_id=project, category_id=1089484, description=f["description"] + ". По сделке " + str(res[-2]))
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
                        f = fin.change_transaction_by_id(f["id"], project_id=project, category_id=864177, description=f["description"] + ". По сделке " + str(res[-2]))
                        if pre_trans:
                            res = fin.change_transaction_by_id(pre_trans["id"], project_id=project, category_id=866958)
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
                            pre = fin.change_transaction_by_id(pre_trans["id"], project_id=project, category_id=866958)
                            f = fin.change_transaction_by_id(final_trans["id"], project_id=project, category_id=864177, description=f["description"] + ". По сделке " + str(res[-2]))
                        elif pre_trans["value"] < order_sum and final_trans["value"] > works_sum:   # разделение оплаты
                            pre = fin.change_transaction_by_id(pre_trans["id"], project_id=project, category_id=866958)
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
                        logging.error(pre, f)
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
                    project = 358087
                elif leed["OFFER_CUSTOMER_NAME"] == "V8.CENTER Кузовной":
                    project = 353644
                else:
                    project = 345944
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
                f = fin.create_transaction(to_id=166457, project_id=project, date=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
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
                if len(pre_trans) > 1:
                    requests.post("https://api.telegram.org/bot6923328005:AAFvq9YwSTLQLGbmfLkNZh-EKj7c1nNiEDY/sendMessage?chat_id=792154034&text=" + ", ".join(list(map(str, res))) + "\n" + ", ".join(list(map(str, pre_trans))))
                final_trans = fin.create_transaction(category_id=864177, project_id=project,
                                                     contractor_id=contractor['id'], date=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                                                     to_id=166457, value=res[1], status="regular",
                                                     description=res[-2])   # создание оплаты
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
            f = fin.create_transaction(from_id=166457, date=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), category_id=1013974, contractor_id=contractor['id'],
                                   value=-1 * int(res[1]), status="regular", description="Возврат по " + str(res[-2]))

    trans = fin.get_transaction_by_desc("Зачисление средств по терминалам эквайринга от")
    date_2 = [[], []]
    date = [[], []]
    date_3 = [[], []]
    st = f"Зачисление средств по терминалам эквайринга от {date_0}. Без НДС. По сделке "
    st_1 = f"Зачисление средств по терминалам эквайринга от {date_1}. Без НДС. По сделке "
    st_2 = f"Зачисление средств по терминалам эквайринга от {date_2_of}. Без НДС. По сделке "
    for i in predoplata[0]:
        date_2[0].append({"attribute_values": {}, "value": i[1], "category_id": 866958, "description": st_1 + i[0], "contractor_id": trans[0]["contractor_id"], "project_id":i[2]})
    for i in predoplata[2]:
        date[0].append({"attribute_values": {}, "value": i[1], "category_id": 866958, "description": st + i[0], "contractor_id": trans[0]["contractor_id"], "project_id":i[2]})
    for i in predoplata[4]:
        date_3[0].append({"attribute_values": {}, "value": i[1], "category_id": 866958, "description": st_2 + i[0],
                        "contractor_id": trans[0]["contractor_id"], "project_id":i[2]})
    for i in polnaya[4]:
        date_3[1].append({"attribute_values": {}, "value": i[1], "category_id": 864177, "description": st_2 + i[0],
                          "contractor_id": trans[0]["contractor_id"], "project_id":i[2]})
    for i in polnaya[0]:
        date_2[1].append({"attribute_values": {}, "value": i[1], "category_id": 864177, "description": st_1 + i[0], "contractor_id": trans[0]["contractor_id"], "project_id":i[2]})
    for i in polnaya[2]:
        date[1].append({"attribute_values": {}, "value": i[1], "category_id": 864177, "description": st + i[0], "contractor_id": trans[0]["contractor_id"], "project_id":i[2]})
    res = ""
    logging.error(date)
    logging.error(date_2)
    logging.error(date_3)
    for i in trans:
        if date_0 in i['description']:
            if (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d') not in used_id:
                used_id.append((datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'))
                if i["value"] == predoplata[3]:
                    if len(date[0]) != 1:
                        res = fin.split_transaction_by_id(i["id"], date[0])
                    else:
                        res = fin.change_transaction_by_id(i[id], description=date[0][0]["description"], category_id=866958, project_id=predoplata[2][0][2])
                elif i["value"] == polnaya[3]:
                    if len(date[1]) != 1:
                        res = fin.split_transaction_by_id(i["id"], date[1])
                    else:
                        res = fin.change_transaction_by_id(i["id"], description=date[1][0]["description"], category_id=864177, project_id=polnaya[2][0][2])
                elif i["value"] == predoplata[3] + polnaya[3]:
                    res = fin.split_transaction_by_id(i["id"], date[0] + date[1])
                elif len(date[0] + date[1]) != 0:
                    date[1].append({"attribute_values": {}, "value": i["value"] - (predoplata[3] + polnaya[3]), "category_id": 3, "description": st[:-12:], "contractor_id": i["contractor_id"]})
                    res = fin.split_transaction_by_id(i["id"], date[0] + date[1])
                else:
                    requests.post(
                        "https://api.telegram.org/bot6923328005:AAFvq9YwSTLQLGbmfLkNZh-EKj7c1nNiEDY/sendMessage?chat_id=792154034&text=Error with date " + str(date_0))
        if date_1 in i['description']:
            if (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d') not in used_id:
                used_id.append((datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'))
                if i["value"] == predoplata[1]:
                    if len(date_2[0]) != 1:
                        res = fin.split_transaction_by_id(i["id"], date_2[0])
                    else:
                        res = fin.change_transaction_by_id(i["id"], description=date_2[0][0]["description"], category_id=866958, project_id=predoplata[0][0][2])
                elif i["value"] == polnaya[1]:
                    if len(date_2[1]) != 1:
                        res = fin.split_transaction_by_id(i["id"], date_2[1])
                    else:
                        res = fin.change_transaction_by_id(i["id"], description=date_2[1][0]["description"], category_id=864177, project_id=polnaya[0][0][2])
                elif i["value"] == predoplata[1] + polnaya[1]:
                    res = fin.split_transaction_by_id(i["id"], date_2[0] + date_2[1])
                elif len(date_2[0] + date_2[1]) != 0:
                    date_2[1].append({"attribute_values": {}, "value": i["value"] - (predoplata[1] + polnaya[1]), "category_id": 3, "description": st_1[:-12:], "contractor_id": i["contractor_id"]})
                    res = fin.split_transaction_by_id(i["id"], date_2[0] + date_2[1])
                else:
                    requests.post(
                        "https://api.telegram.org/bot6923328005:AAFvq9YwSTLQLGbmfLkNZh-EKj7c1nNiEDY/sendMessage?chat_id=792154034&text=Error with date " + str(date_1))
        if date_2_of in i['description']:
            if (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d') not in used_id:
                used_id.append((datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'))
                if i["value"] == predoplata[5]:
                    if len(date_3[0]) != 1:
                        res = fin.split_transaction_by_id(i["id"], date_3[0])
                    else:
                        res = fin.change_transaction_by_id(i["id"], description=date_3[0][0]["description"], category_id=866958, project_id=predoplata[4][0][2])
                elif i["value"] == polnaya[5]:
                    if len(date_3[1]) != 1:
                        res = fin.split_transaction_by_id(i["id"], date_3[1])
                    else:
                        res = fin.change_transaction_by_id(i["id"], description=date_3[1][0]["description"], category_id=864177, project_id=polnaya[4][0][2])
                elif i["value"] == predoplata[5] + polnaya[1]:
                    res = fin.split_transaction_by_id(i["id"], date_3[0] + date_3[1])
                elif len(date_3[0] + date_3[1]) != 0:
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
        time.sleep(10)"""
