# interfax-scrapper
Scrap all news data from interfax.ru by period of time 

## Requirements
python v3+, Scrapy 1.6.0

## How to use
In project directory run:

```sh
$ scrapy crawl jobs -a start_date="2015/01/01" -a  end_date="2015/01/02" -o new.csv
```
