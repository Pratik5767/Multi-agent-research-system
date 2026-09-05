# from src.tools.tools import web_search, scrape_url
from src.pipelines.pipeline import run_research_pipeline



# result = web_search.invoke("Can tell the todays whether")
# print(result)

# result2 = scrape_url("https://www.anthropic.com/news")
# print(result2)


topic = "The impact of AI on job market 2024"
run_research_pipeline(topic)