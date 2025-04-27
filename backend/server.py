import json
import traceback
import random
import boto3
from fastapi import FastAPI, UploadFile, Form, HTTPException, File
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict
from datetime import datetime
import os
from dotenv import load_dotenv
import mysql.connector
import uuid
from datetime import datetime
from fastapi.staticfiles import StaticFiles
from img_generate.img_generator import generate_images, save_images, get_image_size, process_images
from img_generate.img_inpainting import inpaint_images
from img_generate.prompt_enhancer import enhance_pc_case_prompt
import uuid
import threading
import asyncio
import logging
import base64
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

load_dotenv()

DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_USERNAME = os.getenv('DATABASE_USERNAME')
DATABASE_ENDPOINT = os.getenv('DATABASE_ENDPOINT')


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
app.mount("/generated_images",
          StaticFiles(directory="generated_images"),
          name="images")


app.mount("/static",
          StaticFiles(directory="static"),
          name="static")

model_id = "amazon.nova-canvas-v1:0"

image_tasks = {}
image_tasks_lock = threading.Lock()

task_result = dict()


def run_image_generation_task(task_id, text, imgs, batch_count, height, width,
                              cfg_scale, seed, similarityStrength):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            generate_image_logic(task_id, text, imgs, batch_count, height,
                                 width, cfg_scale, seed, similarityStrength))
        loop.close()

        with image_tasks_lock:
            image_tasks[task_id]["status"] = "done"
            image_tasks[task_id]["result"] = result
    except Exception as e:
        with image_tasks_lock:
            image_tasks[task_id]["status"] = "error"
            
            logger.error(str(e))
            logger.error(traceback.format_exc())
            image_tasks[task_id]["error"] = str(e)


def run_image_inpainting_task(task_id, batch_count, text, imgs, mask_prompt,
                              mask_image, negative_prompt, height, width,
                              cfg_scale, seed):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            inpainting_image_logic(task_id, batch_count, text, imgs,
                                   mask_prompt, mask_image, negative_prompt,
                                   height, width, cfg_scale, seed))
        loop.close()

        with image_tasks_lock:
            image_tasks[task_id]["status"] = "done"
            image_tasks[task_id]["result"] = result
    except Exception as e:
        with image_tasks_lock:
            image_tasks[task_id]["status"] = "error"
            
            logger.error(str(e))
            logger.error(traceback.format_exc())
            image_tasks[task_id]["error"] = str(e)

async def generate_image_logic(task_id, text, imgs, batch_count, height, width,
                               cfg_scale, seed, similarityStrength):

    if imgs:
        # uploaded_image_bytes = [await img.read() for img in imgs]
        uploaded_image_bytes = []
        for img_id in imgs:
            img_base64 = await getImageDataB64Async(img_id)
            if img_base64:
                uploaded_image_bytes.append(img_base64)


        # 可依第一張圖片大小補高度寬度
        if not height or not width:
            first_image_size = await get_image_size(uploaded_image_bytes[0])
            height = height or first_image_size["height"]
            width = width or first_image_size["width"]

        img_list = process_images(model_id=model_id,
                                  task_id=task_id,
                                  prompt=text,
                                  base64_images=uploaded_image_bytes,
                                  batch_count=batch_count,
                                  height=height,
                                  width=width,
                                  cfg_scale=cfg_scale,
                                  seed=seed,
                                  similarityStrength=similarityStrength)
    else:
        img_list = generate_images(model_id=model_id,
                                   task_id=task_id,
                                   prompt=text,
                                   batch_count=batch_count,
                                   height=height,
                                   width=width,
                                   cfg_scale=cfg_scale,
                                   seed=seed)
    saved_paths = save_images(task_id, img_list)
    task_result[task_id] = saved_paths


async def inpainting_image_logic(task_id, batch_count, text, imgs, mask_prompt,
                           mask_image, negative_prompt, height, width,
                           cfg_scale, seed):
    if imgs:
        # uploaded_image_bytes = [await img.read() for img in imgs]
        uploaded_image_bytes = []
        for img_id in imgs:
            img_base64 = await getImageDataB64Async(img_id)
            
            if img_base64:
                uploaded_image_bytes.append(img_base64)

        # 可依第一張圖片大小補高度寬度
        if not height or not width:
            first_image_size = await get_image_size(uploaded_image_bytes[0])
            height = height or first_image_size["height"]
            width = width or first_image_size["width"]

    
    img_list = inpaint_images(model_id=model_id,
                                 task_id=task_id,
                                 prompt=text,
                                 mask_prompt=mask_prompt,
                                 mask_image=mask_image,
                                 negative_prompt=negative_prompt,
                                 base64_images=uploaded_image_bytes,
                                 batch_count=batch_count,
                                 height=height,
                                 width=width,
                                 cfg_scale=cfg_scale,
                                 seed=seed)
    saved_paths = save_images(task_id, img_list)
    task_result[task_id] = saved_paths


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
        similarityStrength: Optional[float] = Form(None),
        parameters: Optional[Dict] = Form(None),
):
    seed = random.randint(0, 214783647) if seed is None else seed

    height = parameters.get("height") if parameters else 1024
    width = parameters.get("width") if parameters else 1024

    if parameters:
        for feature_key, feature_value in parameters.items():
            # Skip height and width since they're used for image dimensions
            if feature_key not in ["height", "width"]:
                text += f" {feature_key}:{feature_value}"

    logger.info("text: %s", text)

    task_id = str(uuid.uuid4())  # Generate a unique task ID

    task = {"id": task_id, "status": "queued", "result": None, "error": None}
    logger.info(f"Received image generation task: {task_id}, {task}")
    with image_tasks_lock:
        image_tasks[task_id] = task

    # 啟動線程執行圖片生成任務
    threading.Thread(target=run_image_generation_task,
                     args=(task_id, text, imgs, batch_count, height, width,
                           cfg_scale, seed, similarityStrength),
                     daemon=True).start()

    return {"id": task_id}


@app.post("/img/inpainting")
async def inpainting_image(
                    batch_count: int = Form(...),
                    text: str = Form(...),
                    imgs: Optional[List[str]] = Form(None),
                    mask_prompt: Optional[str] = Form(None),
                    mask_image: UploadFile = File(...),
                    negative_prompt: str = Form(...),
                    cfg_scale: float = Form(...),
                    seed: Optional[str] = Form(None),
                    parameters: Optional[Dict] = Form(None),
                ):
    seed = random.randint(0, 214783647) if seed is None else seed

    height = parameters.get("height") if parameters else 1024
    width = parameters.get("width") if parameters else 1024

    if parameters:
        for feature_key, feature_value in parameters.items():
        # Skip height and width since they're used for image dimensions
            if feature_key not in ["height", "width"]:
                text += f" {feature_key}:{feature_value}"

    # Read mask image data if provided
    mask_image_data = None
    if mask_image:
        mask_image_data = await mask_image.read()
        mask_image_data = base64.b64encode(mask_image_data).decode('utf-8')

    # logger.info("mask_image_data: %s", mask_image_data)

    task_id = str(uuid.uuid4())

    task = {"id": task_id, "status": "queued", "result": None, "error": None}
    logger.info(f"Received image inpainting task: {task_id}, {task}")
    with image_tasks_lock:
        image_tasks[task_id] = task

    threading.Thread(target=run_image_inpainting_task,
             args=(task_id, batch_count, text, imgs, mask_prompt,
               mask_image_data, negative_prompt, height, width,
               cfg_scale, seed),
             daemon=True).start()

    return {"id": task_id}

@app.post("/project/create")
async def create_project(name: str = Form(...),
                        description: Optional[str] = Form(None),
                        templateId: Optional[str] = Form(None)):
    try:
        cursor = conn.cursor()

        # Generate unique project ID
        project_id = str(uuid.uuid4())
        current_time = datetime.now()

        # Insert project into database
        insert_query = """
        INSERT INTO projects (id, name, description, template_id, created_at, modified_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (project_id, name, description, templateId, current_time, current_time)

        cursor.execute(insert_query, values)
        conn.commit()

        cursor.close()

        return {"id": project_id}

    except mysql.connector.Error as err:
        return {"error": f"Database error: {str(err)}"}, 500
    except Exception as e:
        return {"error": f"Server error: {str(e)}"}, 500


@app.post("/project/delete")
async def delete_project(id: str = Form(...)):
    try:
        cursor = conn.cursor(dictionary=True)
        
        # First verify the project exists and check if it's readonly
        verify_query = "SELECT readonly FROM projects WHERE id = %s"
        cursor.execute(verify_query, (id,))
        project = cursor.fetchone()
        
        if not project:
            return JSONResponse(
                status_code=404,
                content={"error": "Project not found"}
            )
            
        if project["readonly"]:
            return JSONResponse(
                status_code=403,
                content={"error": "Cannot delete readonly project/template"}
            )
            
        # Start deletion process
        # 1. Clear project association from images
        update_images_query = """
        UPDATE images 
        SET project_id = NULL 
        WHERE project_id = %s
        """
        cursor.execute(update_images_query, (id,))
        
        # 2. Delete project tags
        delete_tags_query = "DELETE FROM project_tags WHERE project_id = %s"
        cursor.execute(delete_tags_query, (id,))
        
        # 3. Delete project record
        delete_project_query = "DELETE FROM projects WHERE id = %s"
        cursor.execute(delete_project_query, (id,))
        
        conn.commit()
        cursor.close()
        
        return {
            "message": "Project deleted successfully",
            "id": id
        }

    except mysql.connector.Error as err:
        conn.rollback()
        logger.error(f"Database error while deleting project: {str(err)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Database error: {str(err)}"}
        )
    except Exception as e:
        conn.rollback()
        logger.error(f"Server error while deleting project: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Server error: {str(e)}"}
        )

@app.post("/img/delete")
async def delete_image(id: str = Form(...)):
    try:
        cursor = conn.cursor(dictionary=True)
        
        # First verify the image exists and get its metadata
        select_query = "SELECT project_id FROM images WHERE id = %s"
        cursor.execute(select_query, (id,))
        image = cursor.fetchone()
        
        if not image:
            return JSONResponse(
                status_code=404,
                content={"error": "Image not found"}
            )
            
        # Delete from S3
        try:
            s3_key = f"images/{id}"
            s3_client.delete_object(
                Bucket="scottish-leader",
                Key=s3_key
            )
        except Exception as e:
            logger.error(f"S3 deletion failed: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"error": f"Failed to delete image from storage: {str(e)}"}
            )

        # Delete from database
        delete_query = "DELETE FROM images WHERE id = %s"
        cursor.execute(delete_query, (id,))
        conn.commit()
        cursor.close()
        
        return {
            "message": "Image deleted successfully",
            "id": id
        }

    except mysql.connector.Error as err:
        conn.rollback()
        logger.error(f"Database error while deleting image: {str(err)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Database error: {str(err)}"}
        )
    except Exception as e:
        conn.rollback()
        logger.error(f"Server error while deleting image: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Server error: {str(e)}"}
        )

@app.post("/img/save")
async def save_image(
        projectId: str = Form(...),
        file: UploadFile = Form(...),
        id: Optional[str] = Form(None),
        seed: Optional[str] = Form(None),
        prompt: Optional[str] = Form(None),
        parameters: Optional[Dict] = Form(None),
):
    try:
        cursor = conn.cursor()
        
        # Generate image ID if not provided
        image_id = id or str(uuid.uuid4())
        
        # Convert parameters to JSON if provided
        parameters_json = json.dumps(parameters) if parameters else None
        
        # Read image data
        image_data = await file.read()
        # Log image details
        logger.info(f"Saving image {image_id} for project {projectId}. File type: {file.content_type}, Size: {len(image_data)} bytes")
        # Upload to S3
        try:
            s3_key = f"images/{image_id}"
            s3_client.put_object(
                Bucket="scottish-leader",
                Key=s3_key,
                Body=image_data,
                ContentType=file.content_type
            )
        except Exception as e:
            logger.error(f"S3 upload failed: {str(e)}")
            return {"error": f"Failed to upload image: {str(e)}"}, 500
        
        # Insert image metadata into database
        insert_query = """
        INSERT INTO images (id, project_id, type, seed, prompt, parameters)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            type = VALUES(type),
            seed = VALUES(seed),
            prompt = VALUES(prompt),
            parameters = VALUES(parameters)
        """
        values = (image_id, projectId, file.content_type, seed, prompt, parameters_json)
        
        cursor.execute(insert_query, values)
        conn.commit()
        cursor.close()
        
        return {
            "id": image_id,
        }

    except mysql.connector.Error as err:
        conn.rollback()
        return {"error": f"Database error: {str(err)}"}, 500
    except Exception as e:
        conn.rollback()
        return {"error": f"Server error: {str(e)}"}, 500

@app.post("/template/create")
async def create_template(
    projectId: str = Form(...),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
):
    try:
        cursor = conn.cursor(dictionary=True)
        template_id = str(uuid.uuid4())
        current_time = datetime.now()

        # First verify the source project exists and get its details
        cursor.execute("SELECT name, description FROM projects WHERE id = %s", (projectId,))
        source_project = cursor.fetchone()
        if not source_project:
            return JSONResponse(
                status_code=404,
                content={"error": "Source project not found"}
            )

        # Use provided name/description or generate from source project
        template_name = name or f"Template - {source_project['name']}"
        template_description = description or source_project['description']

        # Copy project metadata with readonly flag
        copy_project_query = """
        INSERT INTO projects (id, name, description, created_at, modified_at, readonly)
        VALUES (%s, %s, %s, %s, %s, TRUE)
        """
        cursor.execute(copy_project_query, 
                      (template_id, template_name, template_description, current_time, current_time))
        # Copy project tags
        copy_tags_query = """
        INSERT INTO project_tags (project_id, tag)
        SELECT %s, tag FROM project_tags WHERE project_id = %s
        """
        cursor.execute(copy_tags_query, (template_id, projectId))

        # Copy images with new project_id
        copy_images_query = """
        INSERT INTO images (id, project_id, type, seed, prompt, parameters)
        SELECT UUID(), %s, type, seed, prompt, parameters 
        FROM images 
        WHERE project_id = %s
        """
        cursor.execute(copy_images_query, (template_id, projectId))

        conn.commit()
        cursor.close()

        return {
            "templateId": template_id,
            "name": template_name,
            "sourceProjectId": projectId,
            "created": current_time.isoformat()
        }

    except mysql.connector.Error as err:
        conn.rollback()
        logger.error(f"Database error while creating template: {str(err)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Database error: {str(err)}"}
        )
    except Exception as e:
        conn.rollback()
        logger.error(f"Server error while creating template: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Server error: {str(e)}"}
        )


@app.post("/txt/optimize")
async def optimize_text(text: str = Form(...)):
    return {"text": enhance_pc_case_prompt(text)}  # Placeholder


# GET endpoints

@app.get("/project/{id}")
async def get_project(id: str):
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Get project details including template info if it exists
        project_query = """
        SELECT 
            p.id,
            p.name,
            p.description,
            p.template_id,
            p.created_at,
            p.modified_at,
            p.readonly,
            GROUP_CONCAT(DISTINCT pt.tag) as tags,
            GROUP_CONCAT(DISTINCT i.id) as image_ids
        FROM projects p
        LEFT JOIN project_tags pt ON p.id = pt.project_id
        LEFT JOIN images i ON p.id = i.project_id
        WHERE p.id = %s
        GROUP BY p.id, p.name, p.description, p.template_id, p.created_at, p.modified_at, p.readonly
        """
        
        cursor.execute(project_query, (id,))
        project = cursor.fetchone()
        
        if not project:
            cursor.close()
            return JSONResponse(
                status_code=404,
                content={"error": "Project not found"}
            )
            
        # Get associated images with their metadata
        images_query = """
        SELECT id, type, seed, prompt, parameters
        FROM images 
        WHERE project_id = %s
        """
        cursor.execute(images_query, (id,))
        images = cursor.fetchall()
        
        cursor.close()

        # Process images data
        processed_images = []
        for img in images:
            processed_images.append({
                "id": img["id"],
                "type": img["type"],
                "seed": img["seed"],
                "prompt": img["prompt"],
                "parameters": json.loads(img["parameters"]) if img["parameters"] else None
            })

        # Prepare response
        response = {
            "id": project["id"],
            "name": project["name"],
            "description": project["description"],
            "templateId": project["template_id"],
            "readonly": project["readonly"],
            "tags": project["tags"].split(",") if project["tags"] else [],
            "images": processed_images,
            "created": project["created_at"].isoformat(),
            "modified": project["modified_at"].isoformat()
        }
        
        return response

    except mysql.connector.Error as err:
        logger.error(f"Database error while fetching project: {str(err)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Database error: {str(err)}"}
        )
    except Exception as e:
        logger.error(f"Server error while fetching project: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Server error: {str(e)}"}
        )
    
@app.get("/templates")
async def get_all_templates():
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Simplified query to get only template IDs
        query = """
        SELECT id
        FROM projects
        WHERE readonly = TRUE
        ORDER BY modified_at DESC
        """
        
        cursor.execute(query)
        templates = cursor.fetchall()
        cursor.close()
        
        # Extract just the IDs
        template_ids = [template["id"] for template in templates]
        
        return {"templates": template_ids}

    except mysql.connector.Error as err:
        logger.error(f"Database error while fetching templates: {str(err)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Database error: {str(err)}"}
        )
    except Exception as e:
        logger.error(f"Server error while fetching templates: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Server error: {str(e)}"}
        )


@app.get("/projects")
async def get_all_projects():
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Simplified query to get only project IDs for non-templates
        query = """
        SELECT id
        FROM projects
        WHERE readonly = FALSE
        ORDER BY modified_at DESC
        """
        
        cursor.execute(query)
        projects = cursor.fetchall()
        cursor.close()
        
        # Extract just the IDs
        project_ids = [project["id"] for project in projects]
        
        return {"projects": project_ids}

    except mysql.connector.Error as err:
        logger.error(f"Database error while fetching projects: {str(err)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Database error: {str(err)}"}
        )
    except Exception as e:
        logger.error(f"Server error while fetching projects: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Server error: {str(e)}"}
        )


@app.get("/template/{id}")
async def get_template(id: str):
    return await get_project(id)


@app.get("/img/result/{taskId}")
async def get_image_result(taskId: str):
    # TODO: Implement image result retrieval logic
    with image_tasks_lock:
        task_status = image_tasks.get(taskId)
        if not task_status:
            task_status = "error"
    task_status["urls"]=task_result.get(taskId)
    return task_status
@app.get("/thumb/{projectId}")
async def get_thumb(projectId: str):
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Get first image ID from project
        query = """
        SELECT id 
        FROM images 
        WHERE project_id = %s 
        ORDER BY id ASC 
        LIMIT 1
        """
        
        cursor.execute(query, (projectId,))
        result = cursor.fetchone()
        cursor.close()
        
        if not result:
            # Return default thumbnail from static folder
            default_thumb_path = "static/default_thumb.webp"
            if os.path.exists(default_thumb_path):
                with open(default_thumb_path, "rb") as f:
                    image_data = f.read()
                return Response(
                    content=image_data,
                    media_type="image/webp",
                    headers={
                        "Cache-Control": "max-age=3600",
                        "Content-Disposition": "inline; filename=default_thumb.webp"
                    }
                )
            else:
                return JSONResponse(
                    status_code=404,
                    content={"error": "No images found and default thumbnail missing"}
                )
            
        # Reuse get_image_file to return the actual image
        image_id = result['id']
        return await get_image_file(image_id)

    except mysql.connector.Error as err:
        logger.error(f"Database error while fetching thumbnail: {str(err)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Database error: {str(err)}"}
        )
    except Exception as e:
        logger.error(f"Server error while fetching thumbnail: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"error": f"Server error: {str(e)}"}
        )
        
@app.get("/img/{id}")
async def get_image(id: str):
    
    logger.info(f"Fetching image metadata: id: {id}")
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Fetch image metadata from database
        select_query = "SELECT * FROM images WHERE id = %s"
        cursor.execute(select_query, (id,))
        image_metadata = cursor.fetchone()
        if not image_metadata:
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Fetch image data from S3
        # Encode image to base64
        # image_base64 = await getImageDataB64Async(id)
        
        # Prepare response
        response = {
            "id": id,
            "projectId": image_metadata['project_id'],
            # "data": image_base64,
            "type": image_metadata['type'],
            "seed": image_metadata.get('seed'),
            "prompt": image_metadata.get('prompt'),
            "parameters": json.loads(image_metadata['parameters']) if image_metadata.get('parameters') else {},
        }
        
        cursor.close()
        return JSONResponse(content=response)

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {str(err)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.get("/img/{imageId}/file")
async def get_image_file(imageId: str):
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Get image metadata first
        query = "SELECT type FROM images WHERE id = %s"
        cursor.execute(query, (imageId,))
        result = cursor.fetchone()
        cursor.close()
        
        if not result:
            return JSONResponse(
                status_code=404,
                content={"error": "Image not found"}
            )
            
        # Get the image data from S3
        content_type = result['type']
        s3_key = f"images/{imageId}"
        
        try:
            s3_response = s3_client.get_object(Bucket="scottish-leader", Key=s3_key)
            image_data = s3_response['Body'].read()
        except Exception as e:
            logger.error(f"Failed to fetch image from S3: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"error": f"Failed to fetch image: {str(e)}"}
            )
        
        # Return image file directly
        return Response(
            content=image_data,
            media_type=content_type,
            headers={
                "Cache-Control": "max-age=3600",
                "Content-Disposition": f"inline; filename={imageId}"
            }
        )

    except mysql.connector.Error as err:
        logger.error(f"Database error while fetching image: {str(err)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Database error: {str(err)}"}
        )
    except Exception as e:
        logger.error(f"Server error while fetching image: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Server error: {str(e)}"}
        )
        
async def getImageDataB64Async(id: str):
    # Fetch image data from S3
    s3_key = f"images/{id}"
    try:
        s3_response = s3_client.get_object(Bucket="scottish-leader", Key=s3_key)
        image_data = s3_response['Body'].read()
        
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        return image_base64
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch image {s3_key} from S3: {str(e)}")
        
# Create MySQL connection
conn = mysql.connector.connect(
    host=DATABASE_ENDPOINT,
    user=DATABASE_USERNAME,
    password=DATABASE_PASSWORD,
    database="backend",
    charset="utf8mb4",
    use_unicode=True,
    collation="utf8mb4_general_ci",
)


s3_client = boto3.client("s3")