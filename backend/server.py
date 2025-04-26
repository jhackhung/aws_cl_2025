from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict
from datetime import datetime
import os
from dotenv import load_dotenv
import mysql.connector
import uuid
from datetime import datetime

load_dotenv()

DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_USERNAME = os.getenv('DATABASE_USERNAME')
DATABASE_ENDPOINT = os.getenv('DATABASE_ENDPOINT')

from img_generate.img_generator import generate_images, save_images, get_image_size, process_images
import uuid
import threading
import asyncio
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI()

model_id = "amazon.nova-canvas-v1:0"

image_tasks = {}
image_tasks_lock = threading.Lock()

task_result=dict()


def run_image_generation_task(task_id, text, imgs, batch_count, height, width,
                              cfg_scale, seed):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            generate_image_logic(task_id, text, imgs, batch_count, height,
                                 width, cfg_scale, seed))
        loop.close()

        with image_tasks_lock:
            image_tasks[task_id]["status"] = "done"
            image_tasks[task_id]["result"] = result
    except Exception as e:
        with image_tasks_lock:
            image_tasks[task_id]["status"] = "error"
            image_tasks[task_id]["error"] = str(e)


async def generate_image_logic(task_id, text, imgs, batch_count, height, width,
                               cfg_scale, seed):

    if imgs:
        uploaded_image_bytes = [await img.read() for img in imgs]

        # 可依第一張圖片大小補高度寬度
        if not height or not width:
            first_image_size = await get_image_size(uploaded_image_bytes[0])
            height = height or first_image_size["height"]
            width = width or first_image_size["width"]

        img_list = process_images(
            model_id=model_id,
            task_id=task_id,
            prompt=text,
            image_bytes_list=uploaded_image_bytes,
            batch_count=batch_count,
            height=height,
            width=width,
            cfg_scale=cfg_scale,
            seed=seed)
        task_result = save_images(task_id, img_list)
        

    else:
        img_list = generate_images(model_id=model_id,
                                            task_id=task_id,
                                            prompt=text,
                                            batch_count=batch_count,
                                            height=height,
                                            width=width,
                                            cfg_scale=cfg_scale,
                                            seed=seed)
        task_result = save_images(task_id, img_list)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/img/generate")
async def generate_image(
        batch_count: int = Form(...),
        text: str = Form(...),
        imgs: Optional[List[str]] = Form(None),
        cfg_scale: float = Form(...),
        seed: Optional[str] = Form(None),
        parameters: Optional[Dict] = Form(None),
):
    seed = seed or 0

    height = parameters.get("height") if parameters else 1024
    width = parameters.get("width") if parameters else 1024

    task_id = str(uuid.uuid4())  # Generate a unique task ID

    task = {"id": task_id, "status": "queued", "result": None, "error": None}
    logger.info(f"Received image generation task: {task_id}, {task}")
    with image_tasks_lock:
        image_tasks[task_id] = task

    # 啟動線程執行圖片生成任務
    threading.Thread(target=run_image_generation_task,
                     args=(task_id, text, imgs, batch_count, height, width,
                           cfg_scale, seed),
                     daemon=True).start()

    return {"id": task_id}


@app.post("/project/create")
async def create_project(name: str = Form(...), templateId: Optional[str] = Form(None)):
    try:
        cursor = conn.cursor()

        # Generate unique project ID
        project_id = str(uuid.uuid4())
        current_time = datetime.now()

        # Insert project into database
        insert_query = """
        INSERT INTO projects (id, name, template_id, created_at, modified_at)
        VALUES (%s, %s, %s, %s, %s)
        """
        values = (project_id, name, templateId, current_time, current_time)
        
        cursor.execute(insert_query, values)
        conn.commit()

        cursor.close()

        return {"id": project_id}

    except mysql.connector.Error as err:
        return {"error": f"Database error: {str(err)}"}, 500
    except Exception as e:
        return {"error": f"Server error: {str(e)}"}, 500

        

@app.post("/project/save")
async def save_project(
    id: str = Form(...), name: str = Form(...), tags: List[str] = Form(...), images: List[str] = Form(...)
):
    try:
        cursor = conn.cursor()
        current_time = datetime.now()

        # Update project details
        update_project_query = """
        UPDATE projects 
        SET name = %s, modified_at = %s
        WHERE id = %s
        """
        cursor.execute(update_project_query, (name, current_time, id))

        # Delete existing tags for the project
        delete_tags_query = "DELETE FROM project_tags WHERE project_id = %s"
        cursor.execute(delete_tags_query, (id,))

        # Insert new tags
        if tags:
            insert_tags_query = """
            INSERT INTO project_tags (project_id, tag)
            VALUES (%s, %s)
            """
            tag_values = [(id, tag) for tag in tags]
            cursor.executemany(insert_tags_query, tag_values)

        # Delete existing image associations
        delete_images_query = "DELETE FROM project_images WHERE project_id = %s"
        cursor.execute(delete_images_query, (id,))

        # Insert new image associations
        if images:
            insert_images_query = """
            INSERT INTO project_images (project_id, image_id)
            VALUES (%s, %s)
            """
            image_values = [(id, image_id) for image_id in images]
            cursor.executemany(insert_images_query, image_values)

        conn.commit()
        cursor.close()

        return {"message": "Project saved successfully", "id": id}

    except mysql.connector.Error as err:
        conn.rollback()
        return {"error": f"Database error: {str(err)}"}, 500
    except Exception as e:
        conn.rollback()
        return {"error": f"Server error: {str(e)}"}, 500


@app.post("/img/save")
async def save_image(
        projectId: str = Form(...),
        data: str = Form(...),  # Assuming base64 string
        type: str = Form(...),  # Mime-type
        id: Optional[str] = Form(None),
        seed: Optional[str] = Form(None),
        prompt: Optional[str] = Form(None),
        parameters: Optional[Dict] = Form(None),
):
    # TODO: Implement image saving logic
    return {"id": "image_id"}  # Placeholder


@app.post("/template/create")
async def create_template(projectId: str = Form(...)):
    # TODO: Implement template creation logic
    return {"templateId": "template_id"}  # Placeholder


@app.post("/txt/optimize")
async def optimize_text(text: str = Form(...)):
    # TODO: Implement text optimization logic
    return {"text": "optimized_text"}  # Placeholder


# GET endpoints


@app.get("/project/{id}")
async def get_project(id: str):
    # TODO: Implement project retrieval logic
    return {
        "id": id,
        "tags": [],
        "images": [],
        "created": datetime.now(),
        "modified": datetime.now()
    }  # Placeholder


@app.get("/template/all")
async def get_all_templates():
    # TODO: Implement template retrieval logic
    return {"templateIds": ["template_id_1", "template_id_2"]}  # Placeholder


@app.get("/template/{id}")
async def get_template(id: str):
    # TODO: Implement template retrieval logic
    return {
        "id": id,
        "tags": [],
        "images": [],
        "created": datetime.now(),
        "modified": datetime.now()
    }  # Placeholder


@app.get("/img/result/{taskId}")
async def get_image_result(taskId: str):
    # TODO: Implement image result retrieval logic
    with image_tasks_lock:
        task_status = image_tasks.get(taskId)
        if not task_status:
            task_status = "error"
    return {
        "status": task_status,
        "urls": task_result.get(taskId)
    }  # Placeholder


@app.get("/img/{id}")
async def get_image(id: str):
    # TODO: Implement image retrieval logic
    return {
        "id": id,
        "projectId": "project_id",
        "data": "base64_string",
        "type": "image/png",
        "seed": "seed_value",
        "prompt": "prompt_text",
        "parameters": {
            "color": "red"
        },
    }  # Placeholder

# Create MySQL connection
conn = mysql.connector.connect(
    host=DATABASE_ENDPOINT,
    user=DATABASE_USERNAME,
    password=DATABASE_PASSWORD,
     database="backend"
)