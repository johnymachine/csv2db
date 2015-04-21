import sys
from sqlalchemy import engine


def create_engine():
    import db_config
    url = engine.url.URL('postgresql+psycopg2', **(db_config.connection_settings))
    return engine.create_engine(url, **(db_config.engine_settings))


def main(argv):
    engine = create_engine()
    engine.connect()


if __name__ == "__main__":
    main(sys.argv)
