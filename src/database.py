from src import config
from sqlalchemy import create_engine, MetaData, Table

connection_url = config.get_settings().POSTGRES_URI
engine = create_engine(
    connection_url, pool_pre_ping=True, isolation_level="SERIALIZABLE"
)

metadata_obj = MetaData()
book_log = Table("book_log", metadata_obj, autoload_with=engine)
