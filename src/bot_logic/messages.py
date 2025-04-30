from telethon import Button

MESSAGES = {
    # ------------ / Create Filter Keyboards / ------------
    "PROPERTY_FILTERS:NAME": [
        "Пожалуйста введите имя фильтра",
        [
            [Button.inline("В меню", "/start")]
        ]
    ],
    "PROPERTY_FILTERS:PROPERTY_TYPE": [
        "Выберите тип недвижимости:",
        [
            [Button.inline("Квартира", "property_type:квартира"),
             Button.inline("Дом", "property_type:дом")],
            [Button.inline("Комната", "property_type:комната"),
             Button.inline("Участок", "property_type:участок")],
            [Button.inline("Коммерческая недвижимость", "property_type:коммерческая")],
            [Button.inline("Не важно", "property_type:-")],
            [Button.inline("В меню", "/start")]
        ]
    ],
    "PROPERTY_FILTERS:DEAL_TYPE": [
        "Выберите тип сделки:",
        [
            [Button.inline("Аренда", "deal_type:аренда"),
             Button.inline("Продажа", "deal_type:продажа")],
            [Button.inline("Не важно", "deal_type:-")],
            [Button.inline("В меню", "/start")]
        ]
    ],
    "PROPERTY_FILTERS:CITY": [
        "Введите город, если подходит любой город введите -",
        [
            [Button.inline("В меню", "/start")]
        ]
    ],
    "PROPERTY_FILTERS:AREAS": [
        "Введите район поиска, если параметр не важен введите -",
        [
            [Button.inline("В меню", "/start")]
        ]
    ],
    "PROPERTY_FILTERS:MIN_PRICE": [
        "Введите минимальную цену, если параметр не важен введите -",
        [
            [Button.inline("В меню", "/start")]
        ]
    ],
    "PROPERTY_FILTERS:MAX_PRICE": [
        "Введите максимальную цену, если параметр не важен введите -",
        [
            [Button.inline("В меню", "/start")]
        ]
    ],
    "PROPERTY_FILTERS:MIN_ROOMS": [
        "Введите минимальное количество комнат, если параметр не важен введите -",
        [
            [Button.inline("В меню", "/start")]
        ]
    ],
    "PROPERTY_FILTERS:MAX_ROOMS": [
        "Введите максимальное количество комнат, если параметр не важен введите -",
        [
            [Button.inline("В меню", "/start")]
        ]
    ],
    "PROPERTY_FILTERS:MIN_TOTAL_AREA": [
        "Введите минимальную общую площадь, если параметр не важен введите -",
        [
            [Button.inline("В меню", "/start")]
        ]
    ],
    "PROPERTY_FILTERS:MAX_TOTAL_AREA": [
        "Введите максимальную общую площадь, если параметр не важен введите -",
        [
            [Button.inline("В меню", "/start")]
        ]
    ],
    "PROPERTY_FILTERS:BALCONY": [
        "Выберите наличие балкона:",
        [
            [Button.inline("Есть", "balcony:true"),
             Button.inline("Нет", "balcony:false")],
            [Button.inline("Не важно", "balcony:-")],
            [Button.inline("В меню", "/start")]
        ]
    ],
    "PROPERTY_FILTERS:RENOVATED": [
        "Выберите состояние ремонта:",
        [
            [Button.inline("Требуется ремонт", "renovated:Нет"),
             Button.inline("С ремонтом", "renovated:Да")],
            [Button.inline("Не важно", "renovated:-")],
            [Button.inline("В меню", "/start")]
        ]
    ],
    "PROPERTY_FILTERS:MIN_DEPOSIT": [
        "Введите минимальный размер депозита, если параметр не важен или вы выбираете не аренду введите -",
        [
            [Button.inline("В меню", "/start")]
        ]
    ],
    "PROPERTY_FILTERS:MAX_DEPOSIT": [
        "Введите максимальный размер депозита, если параметр не важен или вы выбираете не аренду введите -",
        [
            [Button.inline("В меню", "/start")]
        ]
    ],
    "PROPERTY_FILTERS:FLOOR": [
        "Введите этаж, если параметр не важен введите -",
        [
            [Button.inline("В меню", "/start")]
        ]
    ],
    "PROPERTY_FILTERS:IS_ACTIVE": [
        "Присылать уведомления о новых объектах, удовлетворяющих фильтру?",
        [            
            [Button.inline("Да", "is_active:yes"),
             Button.inline("Нет", "is_active:no")],
            [Button.inline("В меню", "/start")]
        ]
    ],
    "PROPERTY_FILTERS:TOTAL_FLOORS": [
        "Введите общее количество этажей, если параметр не важен введите -",
        [
            [Button.inline("В меню", "/start")]
        ]
    ],
    "PROPERTY_FILTERS:CONFIRMATION": [
        "Подтвердить?",
        [
            [Button.inline("Да", "property_filter_confirmation:yes"),
             Button.inline("Нет", "property_filter_confirmation:no")],
            [Button.inline("В меню", "/start")]
        ]
    ],

    # ------------ / Create Filter Keyboards / ------------

    # ------------ / Update Filter Keyboards / ------------

    "UPDATE_FILTER_CHOICE":[
        "Выберете что хотите изменить",
        [
            [Button.inline("Название", "update_filter_choice:NAME"),
                Button.inline("Тип недвижимости", "update_filter_choice:PROPERTY_TYPE")],
            [Button.inline("Аренда/Продажа", "update_filter_choice:DEAL_TYPE"),
                Button.inline("Город", "update_filter_choice:CITY")],
            [Button.inline("Районы", "update_filter_choice:AREAS"),
                Button.inline("Мин. цена", "update_filter_choice:MIN_PRICE")],
            [Button.inline("Макс. цена", "update_filter_choice:MAX_PRICE"),
                Button.inline("Мин. кол-во комнат", "update_filter_choice:MIN_ROOMS")],
            [Button.inline("Макс. кол-во комнат", "update_filter_choice:MAX_ROOMS"),
                Button.inline("Мин. площадь", "update_filter_choice:MIN_TOTAL_AREA")],
            [Button.inline("Макс. площадь", "update_filter_choice:MAX_TOTAL_AREA"),
                Button.inline("Балкон", "update_filter_choice:BALCONY")],
            [Button.inline("Ремонт", "update_filter_choice:RENOVATED"),
                Button.inline("Мин. депозит", "update_filter_choice:MIN_DEPOSIT")],
            [Button.inline("Макс. депозит", "update_filter_choice:MAX_DEPOSIT"),
                Button.inline("Этаж", "update_filter_choice:FLOOR")],
            [Button.inline("Кол-во этажей", "update_filter_choice:TOTAL_FLOORS"),
                Button.inline("Получать оповещения", "update_filter_choice:IS_ACTIVE")],
            [Button.inline("В меню", "/start")]
        ]
    ],

    "UPDATE_FILTER:NAME": [
        "Пожалуйста введите имя фильтра",
        [
            [Button.inline("В меню", "/start")],
        ]
    ],
    "UPDATE_FILTER:PROPERTY_TYPE": [
        "Выберите тип недвижимости:",
        [
            [Button.inline("Квартира", "upd_property_type:квартира"),
             Button.inline("Дом", "upd_property_type:дом")],
            [Button.inline("Комната", "upd_property_type:комната"),
             Button.inline("Участок", "upd_property_type:участок")],
            [Button.inline("Коммерческая недвижимость", "upd_property_type:коммерческая")],
            [Button.inline("Не важно", "upd_property_type:-")],
            [Button.inline("В меню", "/start")]
        ]
    ],
    "UPDATE_FILTER:DEAL_TYPE": [
        "Выберите тип сделки:",
        [
            [Button.inline("Аренда", "upd_deal_type:аренда"),
             Button.inline("Продажа", "upd_deal_type:продажа")],
            [Button.inline("Не важно", "upd_deal_type:-")],
            [Button.inline("В меню", "/start")]
        ]
    ],
    "UPDATE_FILTER:CITY": [
        "Введите город, если подходит любой город введите -",
        [
            [Button.inline("В меню", "/start")]
        ]
    ],
    "UPDATE_FILTER:AREAS": [
        "Введите районы поиска через запятую в таком формате: Район1, Район2, ...\
             если параметр не важен введите -",
        [
            [Button.inline("В меню", "/start")]
        ]
    ],
    "UPDATE_FILTER:MIN_PRICE": [
        "Введите минимальную цену, если параметр не важен введите -",
        [
            [Button.inline("В меню", "/start")]
        ]
    ],
    "UPDATE_FILTER:MAX_PRICE": [
        "Введите максимальную цену, если параметр не важен введите -",
        [
            [Button.inline("В меню", "/start")]
        ]
    ],
    "UPDATE_FILTER:MIN_ROOMS": [
        "Введите минимальное количество комнат, если параметр не важен введите -",
        [
            [Button.inline("В меню", "/start")]
        ]
    ],
    "UPDATE_FILTER:MAX_ROOMS": [
        "Введите максимальное количество комнат, если параметр не важен введите -",
        [
            [Button.inline("В меню", "/start")]
        ]
    ],
    "UPDATE_FILTER:MIN_TOTAL_AREA": [
        "Введите минимальную общую площадь, если параметр не важен введите -",
        [
            [Button.inline("В меню", "/start")]
        ]
    ],
    "UPDATE_FILTER:MAX_TOTAL_AREA": [
        "Введите максимальную общую площадь, если параметр не важен введите -",
        [
            [Button.inline("В меню", "/start")]
        ]
    ],
    "UPDATE_FILTER:BALCONY": [
        "Выберите наличие балкона:",
        [
            [Button.inline("Есть", "upd_balcony:yes"),
             Button.inline("Нет", "upd_balcony:no")],
            [Button.inline("Не важно", "upd_balcony:-")],
            [Button.inline("В меню", "/start")]
        ]
    ],
    "UPDATE_FILTER:RENOVATED": [
        "Выберите состояние ремонта:",
        [
            [Button.inline("Требуется ремонт", "upd_renovated:Нет"),
             Button.inline("С ремонтом", "upd_renovated:Да")],
            [Button.inline("Не важно", "upd_renovated:-")],
            [Button.inline("В меню", "/start")]
        ]
    ],
    "UPDATE_FILTER:MIN_DEPOSIT": [
        "Введите минимальный размер депозита, если параметр не важен или вы выбираете не аренду введите -",
        [
            [Button.inline("В меню", "/start")]
        ]
    ],
    "UPDATE_FILTER:MAX_DEPOSIT": [
        "Введите максимальный размер депозита, если параметр не важен или вы выбираете не аренду введите -",
        [
            [Button.inline("В меню", "/start")]
        ]
    ],
    "UPDATE_FILTER:FLOOR": [
        "Введите этаж, если параметр не важен введите -",
        [
            [Button.inline("В меню", "/start")]
        ]
    ],
    "UPDATE_FILTER:IS_ACTIVE": [
        "Присылать уведомления о новых объектах, удовлетворяющих фильтру?",
        [            
            [Button.inline("Да", "upd_is_active:yes"),
             Button.inline("Нет", "upd_is_active:no")],
            [Button.inline("В меню", "/start")]
        ]
    ],
    "UPDATE_FILTER:TOTAL_FLOORS": [
        "Введите общее количество этажей, если параметр не важен введите -",
        [
            [Button.inline("В меню", "/start")]
        ]
    ],

    # ------------ / Update Filter Keyboards / ------------

    # ------------ / Property Keyboards / ------------

    "CREATING_PROPERTY:RETURN_CONTACT": [
        "Пожалуйста введите имя объекта",
        [
            [Button.inline("В меню", "/start")]
        ]
    ],
    "CREATING_PROPERTY:PROPERTY_TYPE": [
        "Выберите тип недвижимости:",
        [
            [Button.inline("Квартира", "квартира"),
             Button.inline("Дом", "дом")],
            [Button.inline("Комната", "комната"),
             Button.inline("Участок", "участок")],
            [Button.inline("Коммерческая недвижимость", "коммерческая")],
            [Button.inline("В меню", "/start")]
        ],
        "property_type",
        "str"
    ],
    "CREATING_PROPERTY:DEAL_TYPE": [
        "Выберите тип сделки:",
        [
            [Button.inline("Аренда", "creating_property_deal_type:аренда"),
             Button.inline("Продажа", "creating_property_deal_type:продажа")],
            [Button.inline("В меню", "/start")]
        ],
        "deal_type",
        "str"
    ],
    "CREATING_PROPERTY:PRICE": [
        "Введите цену",
        [
            [Button.inline("В меню", "/start")]
        ],
        "price",
        "int"
    ],
    "CREATING_PROPERTY:CITY": [
        "Введите город",
        [
            [Button.inline("В меню", "/start")]
        ],
        "city",
        "str"
    ],
    "CREATING_PROPERTY:AREAS": [
        "Введите район",
        [
            [Button.inline("В меню", "/start")]
        ],
        "area",
        "str"
    ],
    "CREATING_PROPERTY:STREET": [
        "Введите улицу",
        [
            [Button.inline("В меню", "/start")]
        ],
        "street",
        "str"
    ],
    "CREATING_PROPERTY:HOUSE_NUMBER": [
        "Введите номер дома",
        [
            [Button.inline("В меню", "/start")]
        ],
        "house_number",
        "str"
    ],
    "CREATING_PROPERTY:APARTMENT_NUMBER": [
        "Введите номер квартиры",
        [
            [Button.inline("В меню", "/start")]
        ],
        "apartment_number",
        "str"
    ],
    "CREATING_PROPERTY:ROOMS": [
        "Введите количество комнат",
        [
            [Button.inline("В меню", "/start")]
        ],
        "rooms",
        "int"
    ],
    "CREATING_PROPERTY:BALCONY": [
        "Выберите наличие балкона:",
        [
            [Button.inline("Есть", "creating_property_balcony:true"),
             Button.inline("Нет", "creating_property_balcony:false")],
            [Button.inline("В меню", "/start")]
        ],
        "balcony",
        "bool"
    ],
    "CREATING_PROPERTY:RENOVATED": [
        "Выберите состояние ремонта:",
        [
            [Button.inline("Требуется ремонт", "creating_property_renovated:Нет"),
             Button.inline("С ремонтом", "creating_property_renovated:Да")],
            [Button.inline("В меню", "/start")]
        ],
        "renovated",
        "str"
    ],
    "CREATING_PROPERTY:TOTAL_AREA": [
        "Введите общую площадь",
        [
            [Button.inline("В меню", "/start")]
        ],
        "total_area",
        "int"
    ],
    "CREATING_PROPERTY:FLOOR": [
        "Введите этаж",
        [
            [Button.inline("В меню", "/start")]
        ],
        "floor",
        "int"
    ],
    "CREATING_PROPERTY:TOTAL_FLOORS": [
        "Введите общее количество этажей",
        [
            [Button.inline("В меню", "/start")]
        ],
        "total_floors",
        "int"
    ],
    "CREATING_PROPERTY:DEPOSIT": [
        "Введите размер депозита, если депозита нет или вы выбираете не аренду введите 0",
        [
            [Button.inline("В меню", "/start")]
        ],
        "deposit",
        "int"
    ],
    "CREATING_PROPERTY:DESCRIPTION": [
        "Напишите описание объекта",
        [
            [Button.inline("В меню", "/start")]
        ],
        "description",
        "str"
    ],
    "CREATING_PROPERTY:CONFIRMATION": [
        "Пришлите изображения(не более 10) одним сообщением.",
        [ 
            [Button.inline("В меню", "/start")]
        ],
        "confirmation",
        "bool"
    ],

    # ------------ / Property Keyboards / ------------

}
