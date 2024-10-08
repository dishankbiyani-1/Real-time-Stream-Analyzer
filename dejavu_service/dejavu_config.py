from dejavu import Dejavu

config = {
    "database": {
        "host": "db",
        "user": "postgres",
        "password": "password", 
        "database": "dejavu"
    },
    "database_type" : "postgres",
}

djv = Dejavu(config)
