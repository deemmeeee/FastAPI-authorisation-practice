# My best project


## 1. how to build/setup

## 2. how to run



## Structure

/clients
    /sqlite (sql, mong)
        client.py
            SQLiteClient
                get_entity
                update_entity
                delete_entity
                create_entity
                ....
        models.py
            UserToCreat
            UserToGet
            MenuToCreate
            MenuToGet
            TableToCreate
            TableToGet
    /mongo
    ...
/storage
    UserStorage
    self.client = SQLiteClient()
    self.table = users_table
        get
        update
        delete
        create
    TableStorage
        get
        update
        delete
        create
    MenuStorage
        get
        update
        delete
        create
    MessageStorage

/manager
    UserManager
    message_storage = MessageStorage()    
        register
            sef.user_storage.create()
            self.message_storage.create()
        update_email
        update_phone
        sign

/routes