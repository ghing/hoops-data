from pysqlite2 import dbapi2 as sqlite

from sqlalchemy import event, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine('sqlite:///hoops.db', module=sqlite)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

@event.listens_for(engine, "connect")
def connect(dbapi_connection, connection_rec):
        dbapi_connection.enable_load_extension(True)
        dbapi_connection.execute("select load_extension('libspatialite.so.3')")

