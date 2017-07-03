# tipi-engine
Motor de tareas y procesos internos de Tipi

## Requirements
Install setup and it will install all dependencies and libraries
```
./setup.sh
```

## Configuration

* Setup database configuration in database/variables.py (based on database/variables.py.example)
* Setup email configuration in alerts/settings.py (based on alerts/settings.py.example)


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
