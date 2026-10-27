from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.agent import HelpdeskAgent, AgentError
from app.config import MODEL, configuration_ready
from app.retrieval import KnowledgeBase, ROOT
from app.schemas import AskRequest

kb = KnowledgeBase()
app = FastAPI(title='Campus Desk', description='Fictional university IT handbook assistant', version='1.0.0', docs_url=None, redoc_url=None)
agent = HelpdeskAgent(kb)

@app.middleware('http')
async def response_headers(request, call_next):
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'"
    if request.url.path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-store'
    return response

@app.get('/api/health')
def health():
    return {'status':'ok','configured':configuration_ready(),'model':MODEL,'articles':len(kb.articles),'fictional':True}

@app.get('/api/articles')
def articles():
    return {'articles':kb.articles,'fictional':True}

@app.post('/api/ask')
def ask(body: AskRequest):
    try:
        return agent.run(body.question)
    except AgentError as e:
        raise HTTPException(status_code=503, detail=str(e)) from None

app.mount('/static',StaticFiles(directory=ROOT/'static'),name='static')

@app.get('/', include_in_schema=False)
def index():
    return FileResponse(ROOT/'static/index.html')
