from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

@CrewBase
class FullStack():
    """FullStack crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    
    @agent
    def engineering_lead(self) -> Agent:
        return Agent(
            config=self.agents_config['engineering_lead'], # type: ignore[index]
            verbose=True
        )
    
    @agent
    def backend_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['backend_engineer'], # type: ignore[index]
            verbose=True,
            allow_code_execution=True,
            code_execution_mode='safe',
            max_execution_time=500,
            max_retry_limit=3,
        )

    @agent
    def frontend_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['frontend_engineer'], # type: ignore[index]
            verbose=True
        )

    @agent
    def test_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['test_engineer'], # type: ignore[index]
            verbose=True,
            allow_code_execution=True,
            code_execution_mode='safe',
            max_execution_time=500,
            max_retry_limit=3,
        )
    
    @agent  
    def report_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['report_writer'], # type: ignore[index]
            verbose=True
        )
    


    @task
    def design_task(self) -> Task:
        return Task(
            config=self.tasks_config['design_task'], # type: ignore[index]
        )

    @task
    def code_task(self) -> Task:
        return Task(
            config=self.tasks_config['code_task'], # type: ignore[index]
            
        )

    @task
    def frontend_task(self) -> Task:
        return Task(
            config=self.tasks_config['frontend_task'], # type: ignore[index]
            
        )
    
    @task
    def test_task(self) -> Task:
        return Task(
            config=self.tasks_config['test_task'], # type: ignore[index]
            output_file='report.md'
        )
    
    @task
    def report_task(self) -> Task:
        return Task(
            config=self.tasks_config['report_task'], # type: ignore[index]
            
        )

    @crew
    def crew(self) -> Crew:
        """Creates the FullStack crew"""

        project_manager = Agent(
            config=self.agents_config['project_manager'], # type: ignore[index]
            verbose=True,
            allow_delegation=True,
        )

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
