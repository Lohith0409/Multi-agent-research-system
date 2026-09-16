from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, scrape_url
from dotenv import load_dotenv
import re

load_dotenv()

# model setup
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)


# 1st step - direct search call (no agent loop needed)
def run_search(topic: str) -> str:
    return web_search.invoke({"query": topic})


# 2nd step - direct scrape call (no agent loop needed)
def run_reader(search_results: str) -> str:
    match = re.search(r"URL:\s*(\S+)", search_results)
    if not match:
        return "No URL found to scrape."
    url = match.group(1)
    return scrape_url.invoke({"url": url})


# writer chain

writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional."""),
])

writer_chain = writer_prompt | llm | StrOutputParser()

# critic chain

critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
])

critic_chain = critic_prompt | llm | StrOutputParser()