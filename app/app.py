from http.server import HTTPServer, SimpleHTTPRequestHandler
from sqlalchemy import create_engine
from sqlalchemy import text
import scrapy
from scrapy.crawler import CrawlerProcess
import json

db_name = 'database'
db_user = 'username'
db_pass = 'secret'
db_host = 'db'
db_port = '5432'

hostName = "0.0.0.0"
serverPort = 8080

# Connecto to the database
db_string = 'postgresql://{}:{}@{}:{}/{}'.format(db_user, db_pass, db_host, db_port, db_name)
db = create_engine(db_string)
conn = None

def scrapAndSaveToPostgresql():
    process = CrawlerProcess(settings={
        "FEEDS": {
            "items.json": {"format": "json"},
        },
    })
    process.crawl(FlatsSpider)
    process.start()

class FlatsSpider(scrapy.Spider):
    name = "flats"

    def start_requests(self):
        urls = [
            'https://www.sreality.cz/api/en/v2/estates?category_main_cb=1&category_type_cb=1&per_page=500&tms=1675012087286',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        print(type(response.body))
        my_json = json.loads(response.body.decode('utf8').replace("'", '"'))
        estates = my_json['_embedded']['estates']
        flats = []
        for e in estates:
            flats.append(
                {'locality': e['locality'], 'name': e['name'], 'image': str(e['_links']['images'][0]).split("\'")[3]})

        print("truncating table")
        conn.execute(text("TRUNCATE TABLE flats;"))
        print("inserting into table")
        for flat in flats:
            conn.execute(text("INSERT INTO flats VALUES (\'{}\', \'{}\', \'{}\');".format(flat['locality'], flat['name'], flat['image'])))

def readFromPostgresql():
    print("reading data")
    result = conn.execute(text("SELECT * FROM flats;"))
    data = []
    for row in result: data.append(row)
    print(data)
    return data

def makeHtml():
    print("building HTML")
    data = readFromPostgresql()
    head = "<html><head><title>flats</title><meta charset=\"utf-8\"></head>"
    body = "<body><ul style=\"font-family:arial\">"
    for line in data:
        body += "<li>{} {} <img src=\"{}\" alt=\"image\"></li>".format(line[0], line[1], line[2])
    body += "</ul></body>"
    html = head + body + "</html>"
    print(html)
    return html

class MyServer(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(makeHtml(), "utf-8"))
        else:
            self.send_response(404)
        return

def run(server_class=HTTPServer, handler_class=MyServer):
    server_address = (hostName, serverPort)
    httpd = server_class(server_address, handler_class)
    print("launching server...")
    httpd.serve_forever()

if __name__ == '__main__':
    print('Application started')
    conn = db.connect()
    scrapAndSaveToPostgresql()
    run()
    db.close()    
