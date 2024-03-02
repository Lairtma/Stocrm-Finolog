from fing import Finolog
from stocrm import Stocrm
import requests
import json
def filling_order(type, contr_var, deal_id):
    deal_description = f"По сделке: {deal_id}"
    new_order = fin.create_order(type)  # создаем новый заказ в finolog
    get_info_last_order = fin.get_last_order()  # получаем данные последнего созданного заказа
    last_order_id = get_info_last_order["id"]  # получаем id последнего созданного заказа из данных
    fin.change_order_by_id(last_order_id, buyer_id=contr_var, description=deal_description, status_id=60244)  # изменяем заказ по id добавляя нужные параметры

def comparing_deals(sto_id):
    orders_list = fin.get_all_orders()
    for i in orders_list:
        if i['description'] == f"По сделке: {sto_id}":
            return i['id']

def order_creation_with_contr_data(deal_id):
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
    fin_order_id = comparing_deals(deal_id) #данные о заказе из fin связанный с sto
    order_data = fin.get_order_by_id(fin_order_id)
    deal_data = sto.get_leed_by_id(deal_id) #данные о сделке stocrm
    orders_sum = float(deal_data['RESPONSE']['DATA'][0]['ORDERS_SUM']) #стоимость запчастей в заказе
    products_sum = (float(deal_data['RESPONSE']['DATA'][0]['OFFER_SUM']) - orders_sum) #стоимость работ в заказе
    package_id = order_data['package_id']
    if deal_data['RESPONSE']['DATA'][0]["OFFER_CUSTOMER_NAME"] == "V8.CENTER":
        project_id = 358087
    elif deal_data['RESPONSE']['DATA'][0]["OFFER_CUSTOMER_NAME"] == "V8.CENTER Кузовной":
        project_id = 353644
    else:
        project_id = 345944
    fin.change_order_by_id(fin_order_id, project_id=project_id)
    if not order_data['package']['items']:
        fin.add_package_item_by_id(package_id, 115857, count=1, price=orders_sum) #добавление стоимости запчастей в заказ
        fin.add_package_item_by_id(package_id, 153056, count=1, price=products_sum) #добавление стоимости работ в заказ
    else:
        check = order_data['package']['items'][0]['item_id']
        if check == 115857:
            package_item_id = order_data['package']['items'][0]['id']
            fin.change_package_item_by_id(package_id, package_item_id, count=1, price=orders_sum,project_id = project_id)
            package_item_id = order_data['package']['items'][1]['id']
            fin.change_package_item_by_id(package_id, package_item_id, count=1, price=products_sum, project_id =project_id )
    fin.update_package_by_id(package_id)
"""
("status_id = {None:'new', 60244:'in work', 
60245: 'waiting payment, 60246:'closed', 60247:'declined'}")

id item запчасти: 115857
id item работа сервиса: 153056
"""

sto = Stocrm("13581_bf2b8cec383601bad6765d4b61240dbd", "v8-centr")
fin = Finolog("hepV7NAnFgAshnDd90adec7e4d95088359e869f3e4f89e08riNSzPykUqS6fKWN", "43768")


print(fin.get_order_by_id(410356))
fin.create_shipment(410356)
#works_and_parts_value(10892)