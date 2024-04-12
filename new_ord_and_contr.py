from fing import Finolog
from stocrm import Stocrm
import time


def filling_order(type, contr_var, deal_id):
    sto = Stocrm("13581_bf2b8cec383601bad6765d4b61240dbd", "v8-centr")
    fin = Finolog("hepV7NAnFgAshnDd90adec7e4d95088359e869f3e4f89e08riNSzPykUqS6fKWN", "43768")
    deal_description = f"По сделке: {deal_id}"
    new_order = fin.create_order(type)  # создаем новый заказ в finolog
    get_info_last_order = fin.get_last_order()  # получаем данные последнего созданного заказа
    last_order_id = get_info_last_order["id"]  # получаем id последнего созданного заказа из данных
    leed = sto.get_leed_by_id(deal_id)["RESPONSE"]["DATA"][0]
    if leed["OFFER_CUSTOMER_NAME"] == "V8.CENTER":
        project = {39014: 359147, 32269: 358087}
    elif leed["OFFER_CUSTOMER_NAME"] == "V8.CENTER Кузовной":
        project = {39014: 359146, 32269: 353644}
    elif leed["OFFER_CUSTOMER_NAME"] == "V8.CENTER (ОСАГО)" or leed["OFFER_CUSTOMER_NAME"] == "V8.CENTER (КАСКО)":
        project = {39014: 345944}
    else:
        project = {}
    fin.change_order_by_id(last_order_id, buyer_id=contr_var, attribute_values=project, description=deal_description, status_id=60244, number=str(deal_id))  # изменяем заказ по id добавляя нужные параметры


def comparing_deals(sto_id):
    sto = Stocrm("13581_bf2b8cec383601bad6765d4b61240dbd", "v8-centr")
    fin = Finolog("hepV7NAnFgAshnDd90adec7e4d95088359e869f3e4f89e08riNSzPykUqS6fKWN", "43768")
    orders_list = fin.get_order_by_numb(sto_id)
    for i in orders_list:
        if i["number"] == str(sto_id):
            return i['id']


def close_order_by_id(deal_id):
    fin = Finolog("hepV7NAnFgAshnDd90adec7e4d95088359e869f3e4f89e08riNSzPykUqS6fKWN", "43768")
    fin_order_id = comparing_deals(deal_id)
    order = fin.get_order_by_id(fin_order_id)
    if len(deal_id) >= 4 and order.get("description", "") and "По сделке: " in order.get("description", ""):
        works_and_parts_value(deal_id)
        if order["shipment"] == 0 and order["package"]["total_price"] == order["paid"] and order["status_id"] != 60246:
            fin.create_shipment_by_order_id(fin_order_id)
            fin.change_order_by_id(fin_order_id, status_id=60246)
            print("Изменение", deal_id, order["id"])


def close_all_orders():
    sto = Stocrm("13581_bf2b8cec383601bad6765d4b61240dbd", "v8-centr")
    fin = Finolog("hepV7NAnFgAshnDd90adec7e4d95088359e869f3e4f89e08riNSzPykUqS6fKWN", "43768")
    orders = fin.get_all_orders()
    for i in orders:
        try:
            lead_status = sto.get_leed_by_id(i["number"])["RESPONSE"]["DATA"][0]["STATUS_NAME"]
        except Exception:
            lead_status = sto.get_leed_by_id(i["number"])
        if lead_status == 'Успешно реализовано ':
            close_order_by_id(i["number"])


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
    else: #такой контрагент уже существует
        contr_list_universal = contr_list_7 if not contr_list_8 else contr_list_8
        contr_id = contr_list_universal[0]['id']

    deal_description = f"По сделке: {deal_id}"
    leed = sto.get_leed_by_id(deal_id)["RESPONSE"]["DATA"][0]
    if leed["OFFER_CUSTOMER_NAME"] == "V8.CENTER":
        project = {39014: 359147, 32269: 358087}
    elif leed["OFFER_CUSTOMER_NAME"] == "V8.CENTER Кузовной":
        project = {39014: 359146, 32269: 353644}
    elif leed["OFFER_CUSTOMER_NAME"] == "V8.CENTER (ОСАГО)" or leed["OFFER_CUSTOMER_NAME"] == "V8.CENTER (КАСКО)":
        project = {39014: 345944}
    else:
        project = {}
    fin.create_order(type="out", buyer_id=contr_id, attribute_values=project, description=deal_description,
                     status_id=60244, number=str(deal_id))  # изменяем заказ по id добавляя нужные параметры


def works_and_parts_value(deal_id):
    sto = Stocrm("13581_bf2b8cec383601bad6765d4b61240dbd", "v8-centr")
    fin = Finolog("hepV7NAnFgAshnDd90adec7e4d95088359e869f3e4f89e08riNSzPykUqS6fKWN", "43768")
    fin_order_id = comparing_deals(deal_id) #данные о заказе из fin связанный с sto
    if not fin_order_id:
        order_creation_with_contr_data(deal_id)
    fin_order_id = comparing_deals(deal_id)
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

def expens_creation_n_filling(lst):
    total = lst['RESPONSE']['DATA'][0]['FULL_COUNT']
    date = lst['RESPONSE']['DATA'][0]['DATE']
    name = lst['RESPONSE']['DATA'][0]['EC_COUNTERPARTY_NAME']
    contr = fin.get_contractor_by_name(name)
    if contr is not None:
        id = contr[0]["id"]
        fin.create_transaction(from_id=170973, date=date, value=-total, type="out", status="regular",
                               category_id=822319, contractor_id=id)
    else:
        fin.create_contractor(name," ", " ")
        last_c = fin.get_contractor_by_name(name)
        last_c_id = last_c[0]["id"]
        fin.create_transaction(from_id=170973, date=date, value=-total, type="out", status="regular",
                               category_id=822319, contractor_id=last_c_id)



#project_id = 358087
#17097
#68413849
#'2024-04-04 13:37:16'

sto = Stocrm("13581_bf2b8cec383601bad6765d4b61240dbd", "v8-centr")
fin = Finolog("hepV7NAnFgAshnDd90adec7e4d95088359e869f3e4f89e08riNSzPykUqS6fKWN", "43768")
lst = sto.get_expens_by_id(8083353)
expens_creation_n_filling(lst)
#print(fin.get_transaction_by_id(68413849))
#print(fin.get_contractor_by_id(4527430))
