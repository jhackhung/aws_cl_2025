## API design

### POST

- `/img/generate`

  - `batch_count`: `int` (Form)
  - `text`: `str` (Form)
  - `imgs`: `Optional[List[str]]` (Form) - List of existing image IDs to use as input
  - `cfg_scale`: `float` (Form)
  - `seed`: `Optional[str]` (Form) - Defaults to 0 if not provided
  - `similarityStrength`: `Optional[float]` (Form) - Used for image-to-image generation
  - `parameters`: `Optional[Dict]` (Form) - Additional parameters (e.g., height, width, style). Height/width default to 1024 if not in params. Other params are appended to the text prompt.
  - **Response**
    - `id`: `str` - Task ID to query progress

- `/img/inpainting`

  - `batch_count`: `int` (Form)
  - `text`: `str` (Form)
  - `imgs`: `Optional[List[str]]` (Form) - List of existing image IDs to use as input
  - `mask_prompt`: `Optional[str]` (Form)
  - `mask_image`: `Optional[UploadFile]` (Form)
  - `negative_prompt`: `str` (Form)
  - `cfg_scale`: `float` (Form)
  - `seed`: `Optional[str]` (Form) - Defaults to 0 if not provided
  - `parameters`: `Optional[Dict]` (Form) - Additional parameters (e.g., height, width). Height/width default to 1024 if not in params. Other params are appended to the text prompt.
  - **Response**
    - `id`: `str` - Task ID to query progress

- `/project/create`

  - `name`: `str` (Form)
  - `templateId`: `Optional[str]` (Form) - ID of template to create this project from (optional)
  - **Response**
    - `id`: `str` - ID of the newly created project

- `/project/save`

  - `id`: `str` (Form) - Project ID to save
  - `name`: `str` (Form) - New name for the project
  - `tags`: `List[str]` (Form) - Array of tags
  - `images`: `List[str]` (Form) - Array of image IDs associated with the project
  - **Response**
    - `message`: `str` - Confirmation message
    - `id`: `str` - Project ID

- `/img/save`

  - `projectId`: `str` (Form)
  - `file`: `UploadFile` (Form) - The image file to save
  - `id`: `Optional[str]` (Form) - Optional image ID (UUID generated if not provided)
  - `seed`: `Optional[str]` (Form)
  - `prompt`: `Optional[str]` (Form)
  - `parameters`: `Optional[Dict]` (Form) - Additional parameters (e.g., color, material, size, style...)
  - **Response**
    - `id`: `str` - ID of the saved image

- `/template/create`

  - `projectId`: `str` (Form) - ID of the project to create a template from
  - `name`: `Optional[str]` (Form) - Optional name for the template
  - **Response**
    - `templateId`: `str` - ID of the template created from this project
    - `name`: `str` - Name of the template
    - `sourceProjectId`: `str` - ID of the source project
    - `created`: `str` - ISO format timestamp

- `/txt/optimize`
  - `text`: `str` (Form)
  - **Response** (Placeholder implementation)
    - `text`: `str` - Optimized text

### GET

- `/project/{id}`

  - **Response**
    - `id`: `str` - Project ID
    - `name`: `str`
    - `templateId`: `Optional[str]`
    - `readonly`: `bool`
    - `tags`: `List[str]`
    - `images`: `List[Dict]` - Array of image objects, each containing:
      - `id`: `str`
      - `type`: `str` (mime-type)
      - `seed`: `Optional[str]`
      - `prompt`: `Optional[str]`
      - `parameters`: `Optional[Dict]`
    - `created`: `str` - ISO format timestamp
    - `modified`: `str` - ISO format timestamp

- `/templates`

  - **Response**
    - `templates`: `List[str]` - Array of template IDs (projects where readonly=TRUE)

- `/projects`

  - **Response**
    - `projects`: `List[str]` - Array of project IDs (projects where readonly=FALSE)

- `/template/{id}`

  - **Response**
    - _Same structure as `/project/{id}`_

- `/img/result/{taskId}`

  - **Response**
    - `status`: `str` - Status of the generation task (e.g., "queued", "done", "error")
    - `urls`: `Optional[List[str]]` - List of URLs/paths to the generated images if status is "done"

- `/img/{id}`
  - **Response** (Returns JSONResponse)
    - `id`: `str`
    - `projectId`: `str`
    - `data`: `str` - Base64 encoded image data fetched from S3
    - `type`: `str` - Mime-type of the image
    - `seed`: `Optional[str]`
    - `prompt`: `Optional[str]`
    - `parameters`: `Dict` - Additional parameters (e.g., color, material, size, style...)
