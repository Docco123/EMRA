from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
import os

# Uncomment the following line to use an example of a custom tool
# from edu2.tools.custom_tool import MyCustomTool

# Check our tools documentations for more information on how to use them
# from crewai_tools import SerperDevTool

#perplexity_llm = LLM(
#    model="llama-3.1-sonar-huge-128k-online",
#    base_url="https://api.perplexity.ai",
#    api_key="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",#
#	endpoint="/chat/completions#"
#)
#agent = Agent(llm=llm, ...)

from crewai_tools import(
	SerperDevTool,
)

os.environ["SERPER_API_KEY"] = "e0d7e29f61783e42a1863cabda2366952017bc33"

search_tool = SerperDevTool()

@CrewBase
class Edu2():
	"""Edu2 crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def bed_allocator(self) -> Agent:
		return Agent(
			config=self.agents_config['bed_allocator'],
			# tools=[MyCustomTool()], # Example of custom tool, loaded on the beginning of file
			verbose=True,
			#tools=[search_tool]
			#llm=perplexity_llm
		)
	@agent
	def helicopter_allocator(self) -> Agent:
		return Agent(
			config=self.agents_config['helicopter_allocator'],
			# tools=[MyCustomTool()], # Example of custom tool, loaded on the beginning of file
			verbose=True,
			#tools=[search_tool]
			#llm=perplexity_llm
		)
	
	@agent
	def medical_supply_allocator(self) -> Agent:
		return Agent(
			config=self.agents_config['medical_supply_allocator'],
			# tools=[MyCustomTool()], # Example of custom tool, loaded on the beginning of file
			verbose=True,
			#tools=[search_tool]
			#llm=perplexity_llm
		)
		
	@agent
	def medical_personnel_allocator(self) -> Agent:
		return Agent(
			config=self.agents_config['medical_personnel_allocator'],
			verbose=True
		)

	@agent
	def decision_maker(self) -> Agent:
		return Agent(
			config=self.agents_config['decision_maker'],
			verbose=True
		)

	@task
	def Bed_allocation(self) -> Task:
		return Task(
			config=self.tasks_config['Bed_allocation'],
		)

	@task
	def Helicopter_allocation(self) -> Task:
		return Task(
			config=self.tasks_config['Helicopter_allocation'],
		)

	@task
	def Medical_supply_allocation(self) -> Task:
		return Task(
			config=self.tasks_config['Medical_supply_allocation'],
		)
	
	@task
	def Medical_personnel_allocation(self) -> Task:
		return Task(
			config=self.tasks_config['Medical_personnel_allocation'],
		)

	@task
	def desicion_making_task(self) -> Task:
		return Task(
			config=self.tasks_config['desicion_making_task'],
			output_file='report.md'
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the Edu2 crew"""
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
