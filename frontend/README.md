# Vue 3 + Vite

# AWS hackathon

## Features

- MCP web scrapping
- Design parameters: color, material, size
- User input: Text to image/Image to image
- Keywords/Tags (類似 hackmd 設計用 tags 分類)
- user can grab current image in db to generate new imgs
- Bedrock image generation: Stability AI / Nova Canvas (at least 4~5 or 10~15)
- User can reproduce the design the partial of prototype (局部重生成)
- User can use some functions(u v) in Nova Canvas to modify image
- User can manually modify the image, And they can continue to step 3 to upload their own blueprints
- User can store the designed image to db

## pages

### Project Page

- User project design history (can be filtered by tag or 風格)
- Create from template or new project
  ![messageImage_1745592196001](https://hackmd.io/_uploads/SJLEHmYyel.jpg)

### design data input

- MCP web scrapping
- Design parameters: color, material, size
- User input: Text to image/Image to image
- Keywords/Tags (類似 hackmd 設計用 tags 分類)
- user can grab current image in db to generate new imgs
- User can also fetch design gallery image

![messageImage_1745592424335](https://hackmd.io/_uploads/SkyMH7Kygl.jpg)

### AI generate

- Bedrock image generation: Stability AI / Nova Canvas (at least 4~5 or 10~15)
- Reproduce All image
- Save images

### Designer revisions (明天去問)

- User can use some functions(u v) in Nova Canvas to modify image
- User can manually modify the image, And they can continue to step 3 to upload their own blueprints
- Inpainting 局部重生(2d or 3d)

### Integration into brand design gallery(柴)

- User can store the designed images to project
- Save project as template
- add tags for new imgs

## API design

POST

- /img/generate
  - batch_count:int
  - text:string
  - imgs:array
  - seed:string?
  - parameters:dict
    - response
      - id:string -> task id to query progress
- /project/save
  - id:string?
  - tags:array -> array of tag
  - images:array -> array of image ids
- /img/save
  - id:string?
  - projectId:string
  - data:base64Str
  - type:mime-type
  - seed:string?
  - prompt:string?
- /template/save
  - projectId:string
- /txt/optimize
  - text:string
    - response
      - text:string

GET

- /project/{id}
  - response
    - id -> projectId
    - tags:array -> array of tag
    - images:array -> array of image ids
    - created:datetime
    - modified:datetime
- /img/result/{taskId}
  - response
    - status -> success/error/xx%
    - data:array<base64str>?
- /template/all

## Model

- LLM: Claude, Nova
- Img Model: Stability, Nova Canvas

## Deploy

- EC2

## 分工

- frontend: wilson ivy
- backend: jack sardelka
- aws: frank jack
- ec2: sardelka
- vlog: frank yvonne :+1:
- sleeping & valoranting: Yuan
- gay: frank

回上一步: 前端處理 => 刪除 new image 然後回到上一個圖片

MCP crawl cosmo [Github-firecrawl](https://github.com/mendableai/firecrawl-mcp-server)

雙語

- 後面可做
  使用 tags 組合生成圖片，合成新的 tag

```python=
 system_list = [
            {
                'text': 'You are an expert at improving image generation prompts by adding specific details about composition, lighting, style, and technical aspects.',
                'cachePoint': {'type': 'default'},
            }
        ]

        # Define message
        message_list = [
            {
                'role': 'user',
                'content': [
                    {
                        'text': f"""Enhance prompt with specific details:
                        - Composition: layout, perspective, focal point
                        - Lighting: direction, intensity, shadows
                        - Style: artistic technique, medium, texture
                        - Mood: atmosphere, emotion, time of day
                        - Technical: resolution, aspect ratio

                        Provide concise output (<1000 chars): {prompt}"""
                    }
                ],
            }
        ]

```
