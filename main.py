from src.tools.tools import web_search, scrape_url



result = web_search.invoke("Can tell the todays whether")
print(result)

result2 = scrape_url("https://www.anthropic.com/news")
print(result2)
