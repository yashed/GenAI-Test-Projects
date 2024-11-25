from fastapi import FastAPI
from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware

from DatabaseCreator import Delete_index, CreateDatabase
from llm import chatfree, chatpro, chatEntaprices, deletechat

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message1(BaseModel):
    message: str
    session_id: str

class Message2(BaseModel):
    enterprise_id: str
    url: str
class Message3(BaseModel):
    enterprise_id: str
class Message4(BaseModel):
    message: str
    session_id: str
    enterprise_id: str
class Message5(BaseModel):
    session_id: str


@app.post("/pro")
async def send_message(data : Message1, response_class=None, response_content_type="text/plain"):
    res = chatpro(data.message,data.session_id)
    return str(res)


@app.post("/free")
async def send_messages(data : Message1, response_class=None, response_content_type="text/plain"):
    res = chatfree(data.message,data.session_id)
    return str(res)

@app.post("/CreateDatabase")
async def send_messages(data : Message2, response_class=None, response_content_type="text/plain"):
    res = CreateDatabase(data.enterprise_id,data.url)
    if res:
        return "Created Successfully"

@app.delete("/DeleteDatabase")
async def send_messages(data : Message3, response_class=None, response_content_type="text/plain"):
    Delete_index(data.enterprise_id)
    return "Deleted Successfully"
@app.post("/enterprise")
async def send_messages(data : Message1, response_class=None, response_content_type="text/plain"):
    res = chatEntaprices(data.message,data.session_id,data.enterprise_id)
    return str(res)
@app.post("/deletechat")
async def send_messages(data : Message5, response_class=None, response_content_type="text/plain"):
    res = deletechat(data.session_id)
    return str(res)
@app.post("/test")
async def send_messages(response_class=None, response_content_type="text/plain"):

    return """ Title: Certificates and solemnization of marriages upon alteration of divisions\n Law sections and its subsections related to question: Section 4 ([8, 22 of 1955]), Section 10 ([10, 22 of 1946]), Section 14 ([7, 34 of 1946]) and Section 28 ([7, of 1944])\n Answer: For a marriage certificate to be issued by a district registrar from the old or new division when an area undergoes a transition as outlined in Law [7, of 1944] Section 28, a marriage must be solemnized in pursuance of Section 33 of the law without any of the preliminaries prescribed by Sections 4 and 10. The required acts must be done by a District Registrar of the old division or the new division nominated by the District Registrar within the District, and the Registrar-General must periodically publish a list of Registrars of Marriages in Sri Lanka, and the buildings they administer, as laid down by Section 14 ([7, 34 of 1946]).\n Conclusion: In conclusion, marriage certificates may be issued by a district registrar from the old or new division when an area undergoes a transition as outlined in Law [7, of 1944] Section 28 under the following conditions: a marriage must be solemnized in pursuance of"""