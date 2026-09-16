from agents import run_search, run_reader, writer_chain, critic_chain

def run_research_pipeline(topic: str) -> dict:

    state = {}

    # step 1 - search
    print("\n" + " ="*50)
    print("step 1 - search agent is working ...")
    print("="*50)

    state["search_results"] = run_search(topic)

    print("\n search result ", state['search_results'])

    # step 2 - reader
    print("\n" + " ="*50)
    print("step 2 - Reader agent is scraping top resources ...")
    print("="*50)

    state["scraped_content"] = run_reader(state["search_results"])

    print("\nscraped content: \n", state['scraped_content'])

    # step 3 - writer chain
    print("\n" + " ="*50)
    print("step 3 - Writer is drafting the report ...")
    print("="*50)

    research_combined = (
        f"SEARCH RESULTS : \n {state['search_results']} \n\n"
        f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })

    print("\n Final Report\n", state['report'])

    # step 4 - critic
    print("\n" + " ="*50)
    print("step 4 - critic is reviewing the report ")
    print("="*50)

    state["feedback"] = critic_chain.invoke({
        "report": state['report']
    })

    print("\n critic report \n", state['feedback'])

    return state


if __name__ == "__main__":
    topic = input("\n Enter a research topic : ")
    run_research_pipeline(topic)