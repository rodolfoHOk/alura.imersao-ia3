import os
from dotenv import load_dotenv

from google.genai import types
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search

from rich.markdown import Markdown
from rich import print as rich_print
from datetime import date
import textwrap
import requests
import warnings

load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

warnings.filterwarnings("ignore")

# from google import genai
# client = genai.Client()

# MODEL_ID = 'gemini-2.0-flash'

# contents = 'Quando é a próxima Imersão IA com Google Gemini da Alura?'

# response = client.models.generate_content(
#     model = MODEL_ID, 
#     contents=contents
# )

# tools = [{'google_search': {}}]

# config = types.GenerateContentConfig(
#     tools=tools
# )

# response = client.models.generate_content(
#     model = MODEL_ID, 
#     contents=contents,
#     config=config
# )

# print(Markdown(f"Resposta:\n\n {response.text}"))

# print(f"Busca realizada: {response.candidates[0].grounding_metadata.web_search_queries}")
# print(f"Páginas utilizadas na resposta: {', '.join([site.web.title for site in response.candidates[0].grounding_metadata.grounding_chunks])}")

# Abrir conteúdo HTML no web browser
# import tempfile
# import webbrowser
# html_content = response.candidates[0].grounding_metadata.search_entry_point.rendered_content
# with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as tmp_file:
#     tmp_file.write(html_content)
# file_url = f'file://{os.path.abspath(tmp_file.name)}'
# webbrowser.open(file_url)

def call_agent(agent: Agent, message_text: str) -> str:
    session_service = InMemorySessionService()
    session_service.create_session(app_name=agent.name, user_id="user1", session_id="session1")
    runner = Runner(agent=agent, app_name=agent.name, session_service=session_service)
    content = types.Content(role="user", parts=[types.Part(text=message_text)])

    final_response = ""
    for event in runner.run(user_id="user1", session_id="session1", new_message=content):
        if event.is_final_response():
          for part in event.content.parts:
            if part.text is not None:
              final_response += part.text
              final_response += "\n"
    return final_response

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

##########################################
# --- Agente 1: Buscador de Notícias --- #
##########################################

def search_agent(topic: str, todayDate: str) -> str:
    agent = Agent(
        name="search_agent",
        model="gemini-2.0-flash",
        description="Agente que busca informações no Google",
        tools=[google_search],
        instruction="""
            Você é um assistente de pesquisa. A sua tarefa é usar a ferramenta de busca do google (google_search)
            para recuperar as últimas notícias de lançamentos muito relevantes sobre o tópico abaixo.
            Foque em no máximo 5 lançamentos relevantes, com base na quantidade e entusiasmo das notícias sobre ele.
            Se um tema tiver poucas notícias ou reações entusiasmadas, é possível que ele não seja tão relevante assim
            e pode ser substituído por outro que tenha mais.
            Esses lançamentos relevantes devem ser atuais, de no máximo um mês antes da data de hoje.
            """
    )
    search_agent_input = f"Tópico: {topic}\nData de hoje: {todayDate}"
    releases = call_agent(agent, search_agent_input)
    return releases


#########################################
# --- Agente 2: Planejador de posts --- #
#########################################

def planning_agent(topic: str, releases_sought: str) -> str:
    agent = Agent(
        name="planning_agent",
        model="gemini-2.0-flash",
        description="Agente que planeja posts",
        tools=[google_search],
        instruction="""
            Você é um planejador de conteúdo, especialista em redes sociais. Com base na lista de
            lançamentos mais recentes e relevantes buscados, você deve:
            Usar a ferramenta de busca do Google (google_search) para criar um plano sobre
            quais são os pontos mais relevantes que poderíamos abordar em um post sobre
            cada um deles. Você também pode usar o (google_search) para encontrar mais
            informações sobre os temas e aprofundar.
            Ao final, você irá escolher o tema mais relevante entre eles com base nas suas pesquisas
            e retornar esse tema, seus pontos mais relevantes, e um plano com os assuntos
            a serem abordados no post que será escrito posteriormente.
            """
    )
    planning_agent_input = f"Tópico:{topic}\nLançamentos buscados: {releases_sought}"
    post_plan = call_agent(agent, planning_agent_input)
    return post_plan

#####################################
# --- Agente 3: Redator do Post --- #
#####################################

def writing_agent(topic: str, post_plan: str) -> str:
    agent = Agent(
        name="writing_agent",
        model="gemini-2.5-flash-preview-04-17",
        description="Agente redator de posts engajadores para Instagram",
        instruction="""
            Você é um Redator Criativo especializado em criar posts virais para redes sociais.
            Você escreve posts para a empresa Alura, a maior escola online de tecnologia do Brasil.
            Utilize o tema fornecido no plano de post e os pontos mais relevantes fornecidos e, com base nisso,
            escreva um rascunho de post para Instagram sobre o tema indicado.
            O post deve ser engajador, informativo, com linguagem simples e incluir 2 a 4 hashtags no final.
            """
    )
    writing_agent_input = f"Tópico: {topic}\nPlano de post: {post_plan}"
    draft = call_agent(agent, writing_agent_input)
    return draft

##########################################
# --- Agente 4: Revisor de Qualidade --- #
##########################################

def review_agent(topic: str, draft: str) -> str:
    agent = Agent(
        name="review_agent",
        model="gemini-2.5-flash-preview-04-17",
        description="Agente revisor de post para redes sociais.",
        instruction="""
            Você é um Editor e Revisor de Conteúdo meticuloso, especializado em posts para redes sociais, com foco no Instagram.
            Por ter um público jovem, entre 18 e 30 anos, use um tom de escrita adequado.
            Revise o rascunho de post de Instagram abaixo sobre o tópico indicado, verificando clareza, concisão, correção e tom.
            Se o rascunho estiver bom, responda apenas 'O rascunho está ótimo e pronto para publicar!'.
            Caso haja problemas, aponte-os e sugira melhorias.
            """
    )
    review_agent_input = f"Tópico: {topic}\nRascunho: {draft}"
    revised_text = call_agent(agent, review_agent_input)
    return revised_text

##############################
# --- Programa principal --- #
###############################

todayDate = date.today().strftime("%d/%m/%Y")

print("🚀 Iniciando o Sistema de Criação de Posts para Instagram com 4 Agentes 🚀")

topic = input("❓ Por favor, digite o TÓPICO sobre o qual você quer criar o post de tendências: ")

if not topic:
    print("Você esqueceu de digitar o tópico!")
else:
    print(f"Maravilha! Vamos então criar o post sobre novidades em {topic}")

    releases_sought = search_agent(topic=topic, todayDate=todayDate)
    print("\n### 📝 Resultado do Agente 1 (Buscador) ###\n")
    rich_print(to_markdown(releases_sought))
    print("--------------------------------------------------------------")

    post_plan = planning_agent(topic=topic, releases_sought=releases_sought)
    print("\n### 📝 Resultado do Agente 2 (Planejador) ###\n")
    rich_print(to_markdown(post_plan))
    print("--------------------------------------------------------------")

    post_draft = writing_agent(topic=topic, post_plan=post_plan)
    print("\n### 📝 Resultado do Agente 3 (Redator) ###\n")
    rich_print(to_markdown(post_draft))
    print("--------------------------------------------------------------")

    final_post = review_agent(topic=topic, draft=post_draft)
    print("\n### 📝 Resultado do Agente 4 (Revisor) ###\n")
    rich_print(to_markdown(final_post))
    print("--------------------------------------------------------------")
