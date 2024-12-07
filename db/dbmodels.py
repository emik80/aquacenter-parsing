from peewee import SqliteDatabase, Model, CharField, ForeignKeyField, TextField, DateTimeField, \
    IntegerField, DecimalField, FloatField, BooleanField

from config import parser_config, logger

db = SqliteDatabase(parser_config.DATABASE)


class BaseModel(Model):
    class Meta:
        database = db


class Categories(BaseModel):
    class Meta:
        db_table = 'Categories'

    cat_name = CharField()
    cat_url = CharField(unique=True)
    cat_qty = IntegerField(unique=True)


class Product(BaseModel):
    class Meta:
        db_table = 'Products'

    status = CharField(default='in queue')
    product_name = CharField()
    product_url = CharField(unique=True)
    source_category = ForeignKeyField(Categories, backref='category', field='cat_url')
    target_category = CharField(null=True)

    product_code = CharField(null=True)
    stock = IntegerField(null=True)
    price = DecimalField(null=True)

    description = TextField(null=True)
    specs_table = TextField(null=True)
    images = TextField(null=True)

    created_at = DateTimeField(formats='%Y-%m-%d %H:%M:%S')
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
            db.create_tables([Product, Categories], safe=True)
            logger.success('DB initialized')
    except Exception as ex:
        logger.error(f"Error writing data: {ex}")
        return


initialize_database(db)
