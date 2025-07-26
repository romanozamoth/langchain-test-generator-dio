import os
from dotenv import load_dotenv
from langchain.chat_models import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from mock_response import MOCK_TEST

load_dotenv()

MODE = os.getenv("MODE", "prod")

def carregar_codigo(caminho):
    with open(caminho, 'r', encoding='utf-8') as file:
        return file.read()

def salvar_teste(conteudo, caminho_saida):
    with open(caminho_saida, 'w', encoding='utf-8') as f:
        f.write(conteudo)

def gerar_teste_real(codigo):
    llm = AzureChatOpenAI(
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        openai_api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
        openai_api_type="azure",
        openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        temperature=0,
    )

    prompt = PromptTemplate(
        input_variables=["codigo"],
        template=f"""
Você é um gerador de testes unitários Python.
Dado o seguinte código, gere testes com Pytest que cubram os casos esperados, erros e exceções.

Código:
```python
{codigo}
```

Retorne apenas o conteúdo do arquivo test_*.py com os testes unitários gerados.
""",
    )

    chain = LLMChain(llm=llm, prompt=prompt)
    return chain.run(codigo)

def main():
    codigo = carregar_codigo("sample_code/calc.py")

    if MODE == "mock":
        print("🔁 Executando em modo MOCK")
        resultado = MOCK_TEST
    else:
        print("🚀 Executando em modo PRODUÇÃO (Azure)")
        resultado = gerar_teste_real(codigo)

    salvar_teste(resultado, "generated_tests/test_calc.py")
    print("✅ Teste gerado com sucesso! Veja em generated_tests/test_calc.py")

if __name__ == "__main__":
    main()
