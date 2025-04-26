from PIL import Image, ImageDraw

# 建立一張白色背景的圖片 (白色表示「不遮罩」)
width, height = 1024, 1024
mask = Image.new("L", (width, height), 255)  # "L" 表示灰階模式，255 = 白色

# 在圖片中央畫一個黑色矩形 (黑色表示「遮罩區域」)
draw = ImageDraw.Draw(mask)

# # 定義遮罩區域大小，例如中央 512x512 正方形
# mask_width, mask_height = 512, 512
# top_left = ((width - mask_width) // 2, (height - mask_height) // 2)
# bottom_right = (top_left[0] + mask_width, top_left[1] + mask_height)

# draw.rectangle([top_left, bottom_right], fill=0)  # fill=0 表示黑色遮罩

# 儲存成 PNG
mask.save("mask_image.png")
print("Mask image saved as mask_image.png")
