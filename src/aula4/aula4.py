import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

client = genai.Client()

# for model in client.models.list():
#     print(model.name)

model = 'gemini-2.0-flash'

# response = client.models.generate_content(model=model, contents='Quem é a empresa por trás dos modelos Gemini?');
# print(response.text)

# chat = client.chats.create(model=model)

# response = chat.send_message('Oi, tudo bem?')
# print(response.text)

# response = chat.send_message('O que é Inteligência Artificial?')
# print(response.text)

# response = chat.send_message('Você é um assistente pessoal e você sempre responde de forma sucinta. O que é Inteligência Artificial?')
# print(response.text)

chat_config = types.GenerateContentConfig(
    system_instruction='Você é um assistente pessoal e você sempre responde de forma sucinta'
)

chat = client.chats.create(model=model, config=chat_config)

# response = chat.send_message('O que é computação quântica?')
# print(response.text)
# print(chat.get_history())

print('Digite fim para finalizar o chat')

prompt = input('Esperando a pergunta ou comando: ')

while prompt.lower() != 'fim' and prompt.lower() != 'fim.':
    response = chat.send_message(prompt)
    print(f'Resposta: {response.text} \n')
    prompt = input('Esperando o prompt: ')

print(chat.get_history())

# chat_config_2 = types.GenerateContentConfig(
#     system_instruction = "Você é um assistente pessoal que sempre responde de forma muito sarcástica.",
# )

# chat_2 = client.chats.create(model=model, config=chat_config_2)

# response_2 = chat_2.send_message("O que é computação quântica?")
# print(response_2.text)
