# Importing the necessary libraries
from fastapi import FastAPI                     # For building web APIs
from phi.agent import Agent                     # To import Agent class from the phi library
from phi.model.groq import Groq                 # To import Groq model
from phi.tools.duckduckgo import DuckDuckGo     # To import DuckDuckGo tool to search web
from phi.tools.yfinance import YFinanceTools    # To import YFinanceTools for financial data
from dotenv import load_dotenv                  # To load environment variables

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI application
app = FastAPI(title="Financial Analyst", version="1.0")

# Create the Web Agent with specific configurations
web_agent = Agent(
    name="Web Agent",
    model=Groq(id="llama-3.3-70b-versatile"),  # Using a specific Groq model
    tools=[DuckDuckGo()],                      # Adding DuckDuckGo as a tool for web searches
    instructions=["Always include sources"],   # Custom instructions for the agent
    show_tool_calls=True,                      # Enable showing tool calls in the output
    markdown=True                              # Enable Markdown formatting in responses
)

# Create the Finance Agent with specific configurations
finance_agent = Agent(
    name="Finance Agent",
    role="Get financial data",                    # Define the role of this agent
    model=Groq(id="llama-3.3-70b-versatile"),     # Using the same Groq model
    tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True)],  # Adding YFinanceTools
    instructions=["Use tables to display data"],  # Custom instructions for the agent
    show_tool_calls=True,                         # Enable showing tool calls in the output
    markdown=True                                 # Enable Markdown formatting in responses
)

# Combine both agents into a team for collaborative responses
agent_team = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),                               # Using the Groq model for the team
    team=[web_agent, finance_agent],                                        # Include the Web and Finance agents
    instructions=["Always include sources", "Use tables to display data"],  # Shared instructions for the team
    show_tool_calls=True,                                                   # Enable showing tool calls in the output
    markdown=True                                                           # Enable Markdown formatting in responses
)

# Define a POST endpoint to summarize stock data and news
@app.post("/summarize")
async def summarize(stock_symbol: str):
    """
    Summarize analyst recommendations and share the latest news for the given stock symbol.
    :param stock_symbol: Stock ticker symbol to summarize information for.
    """
    # Create a prompt for the agent team
    prompt = f"Summarize analyst recommendations and share the latest news for {stock_symbol}"
    try:
        # Use the agent team to get a response based on the prompt
        response = agent_team.print_response(prompt)

        # Return the response in a structured JSON format
        return {"status": "success", "response": response}
    except Exception as e:
        # Handle any exceptions and return an error message
        return {"status": "error", "message": str(e)}
    
   