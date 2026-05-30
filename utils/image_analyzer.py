import cv2
import numpy as np

class ImageAnalyzer:
    def __init__(self):
        pass

    def analyze(self, image_path):
        """分析图片并返回特征信息"""
        # 读取图片
        image = cv2.imread(image_path)
        if image is None:
            raise Exception(f"无法读取图片: {image_path}")

        # 获取图片基本信息
        height, width = image.shape[:2]
        channels = image.shape[2] if len(image.shape) == 3 else 1

        # 分析颜色
        colors = self._analyze_colors(image)

        # 分析场景
        scenes = self._analyze_scenes(image)

        # 分析亮度
        brightness = self._analyze_brightness(image)

        # 分析内容特征
        features = self._analyze_content(image)

        return {
            'width': width,
            'height': height,
            'channels': channels,
            'colors': colors,
            'scenes': scenes,
            'brightness': brightness,
            **features
        }

    def _analyze_colors(self, image):
        """分析图片颜色 - 使用更准确的方法"""
        # 转换为RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # 计算主要颜色（使用加权平均，考虑亮度）
        pixels = rgb_image.reshape(-1, 3).astype(float)
        # 加权计算，考虑人眼对亮度的感知
        weights = 0.299 * pixels[:, 0] + 0.587 * pixels[:, 1] + 0.114 * pixels[:, 2]
        weighted_pixels = pixels * weights[:, np.newaxis]
        dominant_color = np.sum(weighted_pixels, axis=0) / np.sum(weights)
        dominant_color = dominant_color.astype(int)

        # 计算色调（使用更智能的方法）
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv_image)
        
        # 只考虑饱和度足够高的像素来判断主色调
        saturation_threshold = 50
        valid_pixels = h[s > saturation_threshold]
        
        if len(valid_pixels) > 0:
            mean_hue = np.mean(valid_pixels)
        else:
            mean_hue = np.mean(h)

        # 判断色调风格（更准确的范围，考虑暖色占比）
        # 暖色像素统计
        warm_mask = ((h >= 0) & (h < 30)) | ((h >= 330) & (h <= 180))
        warm_pixels = h[warm_mask & (s > saturation_threshold)]
        warm_ratio = len(warm_pixels) / max(len(h[s > saturation_threshold]), 1)
        
        # 冷色像素统计
        cool_mask = (h >= 150) & (h < 270)
        cool_pixels = h[cool_mask & (s > saturation_threshold)]
        cool_ratio = len(cool_pixels) / max(len(h[s > saturation_threshold]), 1)
        
        # 绿色像素统计
        green_mask = (h >= 45) & (h < 150)
        green_pixels = h[green_mask & (s > saturation_threshold)]
        green_ratio = len(green_pixels) / max(len(h[s > saturation_threshold]), 1)
        
        # 根据占比判断主色调
        if warm_ratio > 0.3 or (mean_hue >= 0 and mean_hue < 45) or (mean_hue >= 330 and mean_hue <= 360):
            warmth = '暖色调'
        elif green_ratio > 0.4 and warm_ratio < 0.2:
            warmth = '绿色调'
        elif cool_ratio > 0.3 or (mean_hue >= 150 and mean_hue < 270):
            warmth = '冷色调'
        elif (mean_hue >= 270 and mean_hue < 330):
            warmth = '紫色调'
        else:
            warmth = '中性色调'

        # 饱和度
        mean_saturation = np.mean(s)
        if mean_saturation < 50:
            saturation = '低饱和度（柔和）'
        elif mean_saturation < 120:
            saturation = '中等饱和度'
        elif mean_saturation < 180:
            saturation = '较高饱和度'
        else:
            saturation = '高饱和度（鲜艳）'

        # 亮度
        mean_brightness = np.mean(v)
        if mean_brightness < 80:
            brightness = '偏暗'
        elif mean_brightness < 150:
            brightness = '中等亮度'
        elif mean_brightness < 200:
            brightness = '偏亮'
        else:
            brightness = '明亮'

        # 将RGB转换为十六进制
        hex_color = '#{:02x}{:02x}{:02x}'.format(dominant_color[0], dominant_color[1], dominant_color[2])

        return {
            'dominant': hex_color,
            'rgb': f'RGB({dominant_color[0]}, {dominant_color[1]}, {dominant_color[2]})',
            'warmth': warmth,
            'saturation': saturation,
            'brightness': brightness,
            'warm_ratio': float(warm_ratio),
            'cool_ratio': float(cool_ratio),
            'green_ratio': float(green_ratio)
        }

    def _analyze_scenes(self, image):
        """分析场景类型 - 更准确的方法"""
        height, width = image.shape[:2]
        
        # 检测边缘和纹理
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        edge_density = np.sum(edges) / (height * width)
        
        # 检测直线（建筑物特征）
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=50, maxLineGap=10)
        line_count = len(lines) if lines is not None else 0
        
        # 检测颜色分布（天空特征）
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # 检测天空区域（蓝色范围）
        sky_mask = cv2.inRange(hsv, (90, 20, 50), (140, 255, 255))
        sky_ratio = np.sum(sky_mask) / (height * width)
        
        # 检测植被（绿色范围）
        green_mask = cv2.inRange(hsv, (35, 40, 40), (85, 255, 255))
        green_ratio = np.sum(green_mask) / (height * width)
        
        # 判断场景类型
        if line_count > 20 or sky_ratio > 0.15:
            scene_type = '城市建筑'
        elif green_ratio > 0.2:
            scene_type = '自然风景'
        else:
            scene_type = '室内场景'

        return {
            'type': scene_type,
            'description': self._get_scene_description(scene_type),
            'sky_ratio': float(sky_ratio),
            'green_ratio': float(green_ratio),
            'line_count': line_count
        }
    
    def _get_scene_description(self, scene_type):
        """获取场景描述"""
        descriptions = {
            '城市建筑': '现代城市景观，高楼大厦，都市氛围',
            '自然风景': '自然风光，山川河流，自然美景',
            '室内场景': '室内环境，房间布置，温馨氛围',
            '人物特写': '人物肖像，面部特写，情感表达'
        }
        return descriptions.get(scene_type, '未知场景')

    def _analyze_brightness(self, image):
        """分析亮度"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        v = hsv[:, :, 2]
        mean_v = np.mean(v)
        std_v = np.std(v)
        
        return {
            'mean': float(mean_v),
            'std': float(std_v),
            'level': '高对比度' if std_v > 50 else '中等对比度' if std_v > 30 else '低对比度'
        }
    
    def _analyze_content(self, image):
        """分析图片内容特征"""
        height, width = image.shape[:2]
        
        # 检测是否有人物（简单方法：检测人脸）
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        # 分析构图
        if height > width * 1.3:
            composition = '竖构图'
        elif width > height * 1.3:
            composition = '横构图'
        else:
            composition = '正方形构图'
        
        # 分析主体位置
        center_x, center_y = width // 2, height // 2
        has_center_subject = False
        
        # 简单检测中心区域是否有明显内容
        center_region = image[max(0, center_y-50):min(height, center_y+50), 
                             max(0, center_x-50):min(width, center_x+50)]
        center_std = np.std(center_region)
        if center_std > 30:
            has_center_subject = True
        
        return {
            'has_people': len(faces) > 0,
            'people_count': len(faces),
            'composition': composition,
            'has_center_subject': has_center_subject,
            'aspect_ratio': f'{width}:{height}'
        }

        return {
            'dominant': 'RGB({}, {}, {})'.format(dominant_color[0], dominant_color[1], dominant_color[2]),
            'hex': hex_color,
            'warmth': warmth,
            'saturation': saturation,
            'brightness': brightness
        }

    def _analyze_scenes(self, image):
        """分析图片场景"""
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 计算对比度
        contrast = np.std(gray)

        # 判断场景类型
        if contrast > 80:
            scene_type = '高对比度'
            description = '明暗对比强烈，适合夜景或艺术图片'
        elif contrast > 40:
            scene_type = '中等对比度'
            description = '对比度适中，适合日常照片'
        else:
            scene_type = '低对比度'
            description = '对比度较低，适合柔和的场景'

        return {
            'type': scene_type,
            'description': description,
            'contrast': int(contrast)
        }

    def _analyze_brightness(self, image):
        """分析图片亮度"""
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 计算平均亮度
        mean_brightness = np.mean(gray)

        if mean_brightness < 85:
            brightness = '偏暗'
        elif mean_brightness < 170:
            brightness = '中等亮度'
        else:
            brightness = '偏亮'

        return {
            'value': int(mean_brightness),
            'brightness': brightness
        }
