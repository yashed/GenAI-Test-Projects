from langchain_community.chat_models import ChatOpenAI
import openai
from langchain_openai import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory, ConversationSummaryBufferMemory
from pinecone import Pinecone as pinecone
from langchain_community.vectorstores import Pinecone
from langchain.prompts.prompt import PromptTemplate
from dotenv import load_dotenv
import os

from langchain_community.chat_message_histories import MongoDBChatMessageHistory

from promptTemplates import template, template2

load_dotenv()

OPENAI_KEY = os.getenv("apikey")
PINECONE_API_KEY=os.getenv("PINECONE_API_KEY")
print(PINECONE_API_KEY)
os.environ["PINECONE_API_KEY"] =PINECONE_API_KEY


prompt = PromptTemplate(input_variables=["chat_history", "question", "context"], template=template)
prompt2 = PromptTemplate(input_variables=["chat_history", "question", "context"], template=template2)

pc = pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("justibot")
embeddings = OpenAIEmbeddings(openai_api_key = OPENAI_KEY)


openai = ChatOpenAI(temperature=1, openai_api_key=OPENAI_KEY, model="ft:gpt-3.5-turbo-1106:personal:justibot-1-0:9QdL7lzy")
vectorstore = Pinecone(embedding=embeddings, index=index, text_key="text")




chat_llm_free = ConversationalRetrievalChain.from_llm(
    openai,
    retriever=vectorstore.as_retriever(search_type="mmr", search_kwargs={'k': 3, 'fetch_k': 30}),
    combine_docs_chain_kwargs={"prompt": prompt2},
    verbose=True,
)
chat_llm_pro = ConversationalRetrievalChain.from_llm(
    openai,
    retriever=vectorstore.as_retriever(search_type="mmr", search_kwargs={'k': 8, 'fetch_k': 50}),
    combine_docs_chain_kwargs={"prompt": prompt},
    verbose=True,
)





def get_messages_within_limit(messages, limit):
    total_chars = 0
    selected_messages = []

    # Iterate through messages in reverse order
    for message in reversed(messages):
        message_length = len(message.content)

        # Check if adding this message exceeds the limit
        if total_chars + message_length <= limit:
            selected_messages.insert(0, message)  # Insert at the beginning to maintain original order
            total_chars += message_length
        else:
            break  # Stop iterating once the limit is reached

    return selected_messages



def chatfree(query,session_id):
    chat_message_history = MongoDBChatMessageHistory(
        session_id=session_id,
        connection_string="mongodb+srv://justibotadmin:C5ymKcaFMnvANEwj@serverlessinstance0.uvfg4ot.mongodb.net/?retryWrites=true&w=majority",
        database_name="ChatData",
        collection_name="chat_histories",
    )

    selected_messages = get_messages_within_limit(chat_message_history.messages, 2000)
    res = chat_llm_free({"question": query, "chat_history": selected_messages})
    chat_message_history.add_user_message(query)
    chat_message_history.add_ai_message(res['answer'])
    return res['answer']


def chatpro(query,session_id):
    chat_message_history = MongoDBChatMessageHistory(
        session_id=session_id,
        connection_string="mongodb+srv://justibotadmin:C5ymKcaFMnvANEwj@serverlessinstance0.uvfg4ot.mongodb.net/?retryWrites=true&w=majority",
        database_name="ChatData",
        collection_name="chat_histories",
    )

    selected_messages = get_messages_within_limit(chat_message_history.messages, 1000)
    res = chat_llm_pro({"question": query, "chat_history": selected_messages})
    chat_message_history.add_user_message(query)
    chat_message_history.add_ai_message(res['answer'])
    return res['answer']

def chatEntaprices(query,session_id,enterprise_id):
    chat_message_history = MongoDBChatMessageHistory(
        session_id=session_id,
        connection_string="mongodb+srv://justibotadmin:C5ymKcaFMnvANEwj@serverlessinstance0.uvfg4ot.mongodb.net/?retryWrites=true&w=majority",
        database_name="ChatData",
        collection_name="chat_histories",
    )
    index = pc.Index(enterprise_id)
    ownedvectorstore = Pinecone(embedding=embeddings, index=index, text_key="text")
    chat_llm_enterprices = ConversationalRetrievalChain.from_llm(
        openai,
        retriever=ownedvectorstore.as_retriever(search_type="mmr", search_kwargs={'k': 8, 'fetch_k': 50}),
        combine_docs_chain_kwargs={"prompt": prompt},                                                       #prompt2
        verbose=True,
    )
    selected_messages = get_messages_within_limit(chat_message_history.messages, 1000)
    res = chat_llm_enterprices({"question": query, "chat_history": selected_messages})
    chat_message_history.add_user_message(query)
    chat_message_history.add_ai_message(res['answer'])
    return res['answer']

def deletechat(session_id):
    chat_message_history = MongoDBChatMessageHistory(
        session_id=session_id,
        connection_string="mongodb+srv://justibotadmin:C5ymKcaFMnvANEwj@serverlessinstance0.uvfg4ot.mongodb.net/?retryWrites=true&w=majority",
        database_name="ChatData",
        collection_name="chat_histories",
    )
    chat_message_history.clear()
    return "Chat history deleted successfully"