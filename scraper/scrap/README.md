# Scrap
Install packages:
```bash
apt-get install build-essential autoconf libtool pkg-config python-opengl python-imaging python-pyrex python-pyside.qtopengl idle-python2.7 qt4-dev-tools qt4-designer libqtgui4 libqtcore4 libqt4-xml libqt4-test libqt4-script libqt4-network libqt4-dbus python-qt4 python-qt4-gl libgle3 python-dev libxml2-dev libxslt1-dev zlib1g-dev libssl-dev

```
Create virtenv:

```bash
virtualenv scrap
source scrap/bin/activate
```

Install python libraries:

```bash
pip install -r requirements.txt

```
Enter into the Scrap directory project:
```bash
cd scrap/

```
Execute Scrapy for members:

```bash
scrapy crawl members
```


And execute Scrapy for initiatives
```bash
scrapy crawl initiatives

```
