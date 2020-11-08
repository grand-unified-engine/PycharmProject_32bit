
import requests, bs4

def index_naver(code):
    url = 'https://finance.naver.com/item/coinfo.nhn?code=' + code

    req = requests.get(url)
    html = req.text
    source = bs4.BeautifulSoup(html, 'html.parse')

    # /html/body/table[1]/tbody/tr[3]/td[1]/span
    # print(source.find_all('span', class_='tah p10 gray03')[0].text)
    # stock_num = source.find_all('td', class_='num')

    stock_num = source.select('td > .num')


    print("stock_num : {}".format(stock_num))

    return stock_num