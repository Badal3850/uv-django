from django.http import JsonResponse
import requests

def get_active_jobs(request):
    url = "https://cat-fact.herokuapp.com/facts/random?amount=1"
    response = requests.get(url)
    print(response.json())
    return JsonResponse(response.json(), safe=False)

def get_stock_news(request):
    tickers = ['AAPL', 'MSFT', 'GOOGL']\
    # add multiple tickers here
    # url = 'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=AAPL,MSFT,GOOGL&apikey=70YVO1G2P43U8JJ7'
    url = 'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=AAPL&apikey=70YVO1G2P43U8JJ7'
    r = requests.get(url)
    json_data = r.json()
    feeds = json_data['feed']
    new_r = {"news":[]}
    news = new_r['news']
    for feed in feeds:
        news.append({
            'title': feed['title'],
            'url': feed['url'],
            'summary': feed['summary'],
            'time_published': feed['time_published'],
            'source': feed['source'],
        })
        
    return JsonResponse(new_r)