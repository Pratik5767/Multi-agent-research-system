from src.agents.agents import build_search_agent, build_reader_agent, writer_chain, critic_chain
from langchain_core.messages import ToolMessage



def run_research_pipeline(topic: str) -> dict:
    # state memmory
    state = {}

    # search agent working
    print("\n"+" ="*50)
    print("Step 1 - Search agent is working ...")
    print("="*50)

    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })

    # pull raw tool output
    tool_output = [
        m.content for m in search_result['messages'] if isinstance(m, ToolMessage)
    ]

    state['search_results'] = "\n\n".join(tool_output) if tool_output else search_result['messages'][-1].content
    print("\n search result ",state['search_results'])


    # reader agent working
    print("\n"+" ="*50)
    print("Step 2 - Reader agent is scraping top resources ...")
    print("="*50)

    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:1500]}"
        )]
    })

    # pull raw tool output
    tool_output = [
        m.content for m in reader_result['messages'] if isinstance(m, ToolMessage)
    ]

    state['scraped_content'] = "\n\n".join(tool_output) if tool_output else reader_result['messages'][-1].content
    print("\nscraped content: \n", state['scraped_content'])


    # writer agent working
    print("\n"+" ="*50)
    print("Step 3 - Writer agent is drafting the report...")
    print("="*50)

    research_combined = (
        f"SEARCH RESULTS : \n {state['search_results']} \n\n"
        f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke({
        "topic" : topic,
        "research" : research_combined
    })

    print("\n Final Report\n",state['report'])


    # critic report 
    print("\n"+" ="*50)
    print("Step 4 - Critic is reviewing the report ")
    print("="*50)

    state["feedback"] = critic_chain.invoke({
        "report":state['report']
    })

    print("\n critic report \n", state['feedback'])

    return state

