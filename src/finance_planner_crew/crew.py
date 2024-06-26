from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, crew, agent, task
from langchain_openai import ChatOpenAI
from langchain_community.llms import HuggingFaceEndpoint
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv()

@CrewBase
class FinancePlannerCrew:

    # Load agents and tasks config from yaml
    agents_config = 'configs/agents.yaml'
    tasks_config = 'configs/tasks.yaml'

    def __init__(self):
        load_dotenv(find_dotenv())
        HUGGINGFACEHUB_API_TOKEN = os.environ["HUGGINGFACEHUB_API_TOKEN"]

        repo_id = "mistralai/Mistral-7B-Instruct-v0.2"
        self.llm = HuggingFaceEndpoint(
            repo_id=repo_id,
            max_new_tokens=1024,
            temperature=0.3,
            repetition_penalty=1.1,
        )
        self.fpagents = []  # Initialize with an empty list
        self.fptasks = []   # Initialize with an empty list

    def set_single_agent(self, agent):
        self.fpagents = [agent]

    def set_single_task(self, task):
        self.fptasks = [task]

    # @agent
    def spending_reduction_rececommendation_expert_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['spending_reduction_rececommendation_expert_agent'],
            llm=self.llm
        )

    # @task
    def generate_spending_reduction_recommendation_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_spending_reduction_recommendation_task'],
            agent=self.spending_reduction_rececommendation_expert_agent()
        )

    # @agent
    def debt_negotiation_advisor_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['debt_negotiation_advisor_agent'],
            llm=self.llm
        )

    # @task
    def generate_debt_negotiation_recommendation_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_debt_negotiation_recommendation_task'],
            agent=self.debt_negotiation_advisor_agent()
        )
    
    def Resercher_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['Resercher_agent'],
            llm=self.llm,
            # tools=[SerperDevTool()], # Example of custom tool, loaded on the beginning of file
            verbose=True,
			allow_delegation=False
        )
    def recommendation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['recommendation_agent'],
            llm=self.llm,
            # tools=[SerperDevTool()], # Example of custom tool, loaded on the beginning of file
            verbose=True,
			allow_delegation=False
        )

    # @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
            agent=self.Resercher_agent()
        )

  


    # @task
    def Suggetion_task(self) -> Task:
        return Task(
            config=self.tasks_config['Suggetion_task'],
            agent=self.recommendation_agent(),
            output_file='Suggestions.md'
			#human_input=True
        )

    @crew
    def crew(self) -> Crew:
        # Ensure to use only the set agents and tasks
        if not self.fpagents or not self.fptasks:
            raise ValueError("Agents and tasks must be set before creating the crew.")
        return Crew(
            agents=self.fpagents,
            tasks=self.fptasks,
            process=Process.sequential,
            verbose=2,
            max_rpm=250,
        )

    

if __name__ == "__main__":
    finance_planner = FinancePlannerCrew()
    


    # To set a single agent and create the crew
    finance_planner.set_single_agent(finance_planner.spending_reduction_rececommendation_expert_agent())
    finance_planner.set_single_task(finance_planner.generate_spending_reduction_recommendation_task())
    crew_instance = finance_planner.crew()

    # Start the crew
    crew_instance.kickoff()
