class DataMapper:
    db_model = None
    schema = None

    @classmethod
    def map_to_domain_entity_pyd(cls, data):
        """Превращаем модель SQLAlchemy в Pydantic schema"""
        return cls.schema.model_validate(data, from_attributes=True)

    @classmethod
    def map_to_entity_db(cls, data):
        """Превращаем схему Pydantic в SQLAlchemy модель"""
        return cls.db_model(data.model_dump())
