# njuskalo-notifier
njuskalo.hr scraper that alerts when new ads matching given filters appear

### Install:
```
pip3 install -r requirements.txt
python3 setup.py install
```

### Usage:
```$ njuskalo-notifier --help```
```
usage: njuskalo-notifier [-h] [-c CONFIG]

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        path to config file
```
Specify in `config_example.ini` URLs you want to parse, email settings, pipelines...

To disable email notifications simply comment out line `sniffer_scraper.pipeline.EmailPipeline = 400`
By default SQLite database `ads_dump.db` is created with all parsed information.

#### Single run
```njuskalo-notifier -c config_example.ini```

#### Scrapper loop
Scheduled run every `n_seconds` is achieved using bash command `watch`

```
watch -n <n_seconds> njuskalo-notifier -c config_example.ini
```
### Note: 
Not tested on Windows - possible additional dependencies required. Should work using WSL (Windows Subsystem for Linux)
