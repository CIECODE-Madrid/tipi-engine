from os import environ as env


config = {
    # MONGO CONFIG
    "MONGO_USERNAME": env.get('SERVER_NAME', 'tipi'),
    "MONGO_PASSWORD": env.get('MONGO_PASSWORD', 'tipi'),
    "MONGO_HOST": env.get('MONGO_HOST', 'mongo'),
    "MONGO_PORT": int(env.get('MONGO_PORT', '27017')),
    "MONGO_DB_NAME": env.get('MONGO_DB_NAME', 'tipidb'),
}

