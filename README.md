# tipi-engine
Motor de tareas y procesos internos de Tipi

## Requerimientos
Install setup and it will install all dependencies and libraries
```
./setup.sh
```
Setup database configuration in database/variables.py
=======
```
config = {
    
    "MONGO_USERNAME": None,
    "MONGO_PASSWORD": None,
    "MONGO_HOST": "HOST",
    "MONGO_PORT": PORT,
    "MONGO_DB_NAME": "dbname",
    
}


```


Init Luigi
=======
Inside Virtualenv:
```
./base.py
```
or exec cron.sh
```
./cron.sh
```

Add to Crontab /etc/crontab
=======
```
0 2	*/3 * * root	bash /path/to/cron.sh
```

Reset blacklist
=======
Access to redis-cli and flush:
```
flushall
```
If you want only flush a specific db:
```
select [number db]
flushdb
```
