from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from authlib.integrations.starlette_client import OAuth, OAuthError, StarletteOAuth2App
from apps.config import  GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
from fastapi.staticfiles import StaticFiles


app = FastAPI(debug=True)
app.add_middleware(SessionMiddleware, secret_key="09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")

app.mount("/static", StaticFiles(directory="static"), name="static")

oauth = OAuth()



#Register for GITHUB
oauth.register(
    name='github',
    client_id=GITHUB_CLIENT_ID,
    client_secret=GITHUB_CLIENT_SECRET,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    authorize_token_params=None,
    refresh_token_url=None,
    redirect_uri='http://localhost:8000/auth-github',
    client_kwargs={'scope': 'user'},
)

templates = Jinja2Templates(directory="templates")


@app.get("/")
def index(request: Request):
    user = request.session.get('user')
    if user:
        return RedirectResponse('welcome')

    return templates.TemplateResponse(
        name="home.html",
        context={"request": request}
    )


@app.get('/welcome')
def welcome(request: Request):
    user = request.session.get('user')
    print(user)
    if not user:
        return RedirectResponse('/')
    return templates.TemplateResponse(
        name='welcome.html',
        context={'request': request, 'user': user}
    )



@app.get('/login-github')
async def login_github(request: Request):
    redirect_uri = 'http://localhost:8000/auth-github'
    return await oauth.github.authorize_redirect(request, redirect_uri)


@app.get('/auth-github')
async def auth_github(request: Request, redirect_uri='http://localhost:8000/auth-github'):
    try:
        print(f"Authorization Request: {request.url}")
        token = await oauth.github.authorize_access_token(request)
        print(f"Access Token: {token}")
    except OAuthError as e:
        print("GitHub OAuth Error:", e)
        return templates.TemplateResponse(
            name='error.html',
            context={'request': request, 'error': e.error}
        )
    user = await oauth.github.parse_id_token(request, token)
    if user:
        request.session['user'] = dict(user)
    return RedirectResponse('welcome')


# @app.get('/auth-github')
# async def auth_github(request: Request, redirect_uri='http://localhost:8000/auth-github'):
#     try:
#         token = await oauth.github.authorize_access_token(request)

#     except OAuthError as e:
#         print("GitHub OAuth Error:", e)
#         return templates.TemplateResponse(
#             name='error.html',
#             context={'request': request, 'error': e.error}
#         )
#     user = await oauth.github.parse_id_token(request, token)
#     if user:
#         request.session['user'] = dict(user)
#     return RedirectResponse('welcome')


@app.get('/logout')
def logout(request: Request):
    request.session.pop('user')
    return RedirectResponse(url="https://accounts.github.com/logout", status_code=302)
