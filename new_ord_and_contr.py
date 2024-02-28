from fing import Finolog
from stocrm import Stocrm
import requests
import json
def filling_order(type, contr_var, deal_id):
    deal_description = f"По сделке: {deal_id}"
    new_order = fin.create_order(type)  # создаем новый заказ в finolog
    get_info_last_order = fin.get_last_order()  # получаем данные последнего созданного заказа
    last_order_id = get_info_last_order["id"]  # получаем id последнего созданного заказа из данных
    fin.change_order_by_id(last_order_id, buyer_id=contr_var, description = deal_description)  # изменяем заказ по id добавляя нужные параметры

def comparing_deals(sto_id):
    orders_list = fin.get_all_orders()
    for i in orders_list:
        desc = i['description']
        if desc != '' and desc is not None:
            deal_id = int(''.join(i for i in desc if i.isdigit()))
            if deal_id == int(sto_id):
                return deal_id

def order_creation_with_contr_data(id,type):
    type = "out"
    deal_data = sto.get_leed_by_id(id) #получаем info по определнной сделке stocrm с помощью её id
    print(deal_data)
    contact_phone_by_leed_id = str(deal_data['RESPONSE']['DATA'][0]['CONTACT_PROPERTY_PHONE']) #получаем номер телефона из сделки storcrm
    contr_list_7 = fin.get_contractor_by_phone('7' + contact_phone_by_leed_id[1:])
    contr_list_8 = fin.get_contractor_by_phone('8' + contact_phone_by_leed_id[1:])

    if not contr_list_7 and not contr_list_8: #если такого контрагента не сущемтвует
        fin.create_contractor(name=deal_data['RESPONSE']['DATA'][0]['CONTACT_TITLE'],
                              phone=deal_data['RESPONSE']['DATA'][0]['CONTACT_PROPERTY_PHONE'], desc=id)
        contr_id = fin.get_contractor_by_phone(deal_data['RESPONSE']['DATA'][0]['CONTACT_PROPERTY_PHONE'])
        print(contr_id)
        filling_order(type, contr_id, id)
    else: #такой контрагент уже существует
        contr_list_universal = contr_list_7 if not contr_list_8 else contr_list_8
        contr_id = contr_list_universal[0]['id']
        print(contr_list_universal)
        filling_order(type,contr_id, id)

sto = Stocrm("13581_bf2b8cec383601bad6765d4b61240dbd", "v8-centr")
fin = Finolog("hepV7NAnFgAshnDd90adec7e4d95088359e869f3e4f89e08riNSzPykUqS6fKWN", "43768")

(order_creation_with_contr_data(10715, "out"))
print(comparing_deals(10715))
