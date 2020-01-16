# tipi-engine
Motor de tareas y procesos internos de Tipi

## Requirements
Install setup and it will install all dependencies and libraries
```
./setup.sh
```

## Configuration

* Setup database configuration in database/variables.py (based on database/variables.py.example)
* Disable/Enable alerts (cp alerts/settings.py.example alerts/settings.py)


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
