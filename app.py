from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from beanie import init_beanie
from starlette.staticfiles import StaticFiles
from api.auth.config import get_current_user_for_socket
from models import (db, user_model, company_model, auth, news_model, contact, feedback,
                    real_history, swims_tariffs, description_tariffs, company_tariffs, navy,
                    paymentHistory, settings_global, vacancy, notifications)
from api.api_routers import api_router
from datetime import datetime
import asyncio
from bson import ObjectId

loop = asyncio.get_event_loop()

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

async def daily_task():
    await notifications.delete_all()

def run_daily_task():
    asyncio.run_coroutine_threadsafe(daily_task(), loop)

@asynccontextmanager
async def lifespan(app: FastAPI):

    scheduler = BackgroundScheduler()

    scheduler.add_job(
        run_daily_task,
        CronTrigger(hour=21, minute=0),
        id='daily_task',
        name='Run task every day at 21:00',
        replace_existing=True
    )

    scheduler.start()

    await init_beanie(
        database=db,
        document_models=[
            user_model,
            auth,
            news_model,
            contact,
            feedback,
            real_history,
            swims_tariffs,
            description_tariffs,
            company_tariffs,
            navy,
            company_model,
            paymentHistory,
            settings_global,
            vacancy,
            notifications,
        ],
    )
    yield

scheduler = BackgroundScheduler()

app = FastAPI(lifespan=lifespan, title="a-flot backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", " *"],
    allow_credentials=True,
    allow_methods=["*", " *"],
    allow_headers=["*", " *"]
)

app.include_router(api_router)

app.mount('/static', StaticFiles(directory='static'), name='static')

sailor_clients = {}
company_clients = {}

@app.websocket("/wss/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    await websocket.accept()
    current_user = await get_current_user_for_socket(token=token)

    if not isinstance(current_user, dict):
        await websocket.close()
        return

    if current_user['role'] == 'Моряк':
        sailor_clients[str(current_user['id'])] = websocket
    else:
        company_clients[str(current_user['id'])] = websocket

    try:
        while True:
            data = await websocket.receive_json()
            message = data.get("message", {})
            receiver_id = data.get("receiver_id")
            receiver_role = data.get("role")
            if receiver_role == 'Компания':
                receiver = await auth.find_one({"resumeID": ObjectId(receiver_id) })
                receiver_id = str(receiver.id)

            if receiver_role == 'Моряк':
                receiver = await auth.find_one({"resumeID": ObjectId(receiver_id) })
                receiver_id = str(receiver.id)

            notif = await notifications.find_one({"user_id": receiver_id})

            should_send_notification = False

            if notif:
                if message not in notif.guests:
                    notif.guests.append(message)
                    await notifications.update({"user_id": receiver_id}, {"$set": {"guests": notif.guests}})
                    should_send_notification = True
            else:
                notif = notifications(user_id=receiver_id, guests=[message])
                await notifications.insert_one(notif)
                should_send_notification = True

            if receiver_role == 'Моряк':
                notify_user_socket = sailor_clients.get(receiver_id)
            else:
                notify_user_socket = company_clients.get(receiver_id)

            if notify_user_socket and should_send_notification:
                await notify_user_socket.send_json({"notification": data})

    except WebSocketDisconnect:
        if current_user['role'] == 'Моряк':
            sailor_clients.pop(current_user['id'], None)
        else:
            company_clients.pop(current_user['id'], None)

        print(f"User {current_user['id']} disconnected")