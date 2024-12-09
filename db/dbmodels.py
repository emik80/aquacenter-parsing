from datetime import datetime

from peewee import SqliteDatabase, Model, CharField, TextField, DateTimeField, IntegerField, BooleanField

from config import parser_config, logger

db = SqliteDatabase(parser_config.DATABASE)


class BaseModel(Model):
    class Meta:
        database = db


class Task(BaseModel):
    class Meta:
        db_table = 'Tasks'

    source_url = CharField()
    source_category_name = CharField(null=True)
    target_category = CharField()
    status = CharField()
    urls = TextField(null=True)
    cat_qty = IntegerField(null=True)
    start = DateTimeField(formats='%Y-%m-%d %H:%M:%S')
    end = DateTimeField(null=True, formats='%Y-%m-%d %H:%M:%S')


class Product(BaseModel):
    class Meta:
        db_table = 'Products'

    product_url = CharField(null=True)
    product_name = CharField(null=True)
    target_category = CharField()

    product_code = CharField(null=True)
    price = IntegerField(null=True)
    stock = IntegerField(null=True)

    description = TextField(null=True)
    specs_table = TextField(null=True)
    images = TextField(null=True)

    status = CharField(default='new')
    created_at = DateTimeField(default=datetime.now(), formats='%Y-%m-%d %H:%M:%S')
    modified_at = DateTimeField(null=True, formats='%Y-%m-%d %H:%M:%S')


class User(BaseModel):
    class Meta:
        db_table = 'Users'
    tg_user_id = CharField(unique=True, max_length=32)
    tg_username = CharField(null=True)
    is_admin = BooleanField(default=False)


def initialize_database(db: SqliteDatabase):
    try:
        with db:
            db.create_tables([Task, Product], safe=True)
            logger.success('DB initialized')
    except Exception as ex:
        logger.error(f"Error writing data: {ex}")
        return


initialize_database(db)
