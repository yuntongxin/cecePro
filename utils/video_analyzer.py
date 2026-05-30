import cv2
import numpy as np
import colorsys
import os

class VideoAnalyzer:

    def __init__(self):
        self.frame_sample_rate = 30

    def analyze(self, video_path):
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise Exception("无法打开视频文件，请确保安装了FFmpeg")

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / fps if fps > 0 else 0

        frames = self._extract_frames(cap, total_frames)

        cap.release()

        color_analysis = self._analyze_colors(frames)
        motion_analysis = self._analyze_motion(frames)
        scene_analysis = self._analyze_scenes(frames)

        return {
            'fps': round(fps, 2),
            'duration': round(duration, 2),
            'resolution': f'{width}x{height}',
            'total_frames': total_frames,
            'sampled_frames': len(frames),
            'colors': color_analysis,
            'motion': motion_analysis,
            'scenes': scene_analysis
        }

    def _extract_frames(self, cap, total_frames):
        frames = []

        if total_frames <= 0:
            return frames

        sample_rate = max(1, total_frames // 20)
        count = 0

        while count < total_frames:
            ret, frame = cap.read()
            if not ret:
                break

            if count % sample_rate == 0:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame_rgb)

            count += 1

        return frames

    def extract_key_frames(self, video_path, max_frames=5):
        """提取视频的关键帧"""
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise Exception("无法打开视频文件，请确保安装了FFmpeg")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # 确保最少提取3帧：首帧、尾帧、中间帧
        frame_count = max(3, min(max_frames, total_frames))

        # 提取关键帧：首帧、尾帧、中间均匀分布的帧
        frame_indices = []
        
        # 首帧
        frame_indices.append(0)
        
        # 中间帧：根据用户要求，总帧数减2就是中间帧数
        middle_frames = frame_count - 2
        if middle_frames > 0:
            for i in range(1, middle_frames + 1):
                # 均匀分布中间帧
                index = int((i / (middle_frames + 1)) * total_frames)
                frame_indices.append(index)
        
        # 尾帧
        frame_indices.append(total_frames - 1)

        key_frames = []
        for index in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, index)
            ret, frame = cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                key_frames.append(frame_rgb)

        cap.release()

        return key_frames

    def _analyze_colors(self, frames):
        if not frames:
            return self._default_color_analysis()

        all_pixels = np.concatenate([frame.reshape(-1, 3) for frame in frames], axis=0)
        avg_color = np.mean(all_pixels, axis=0)

        r, g, b = int(avg_color[0]), int(avg_color[1]), int(avg_color[2])

        if r > 150 and g < 100 and b < 100:
            warmth = "暖色调（红色/橙色）"
            style = "热情、活力、温暖"
        elif r < 100 and g > 100 and b < 100:
            warmth = "冷色调（绿色/青色）"
            style = "平静、自然、清新"
        elif r < 100 and g < 100 and b > 150:
            warmth = "冷色调（蓝色）"
            style = "冷静、科技、未来感"
        elif r > 150 and g > 150 and b < 100:
            warmth = "暖色调（黄色）"
            style = "明亮、愉快、欢快"
        elif r > 150 and g < 100 and b > 150:
            warmth = "混合色调（紫色/粉色）"
            style = "浪漫、神秘、梦幻"
        elif r < 100 and g > 100 and b > 100:
            warmth = "冷色调（青色/蓝绿色）"
            style = "清爽、海洋、自然"
        else:
            warmth = "中性色调"
            style = "平衡、和谐、稳重"

        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)

        if s > 0.5:
            saturation = "高饱和度"
        elif s > 0.25:
            saturation = "中等饱和度"
        else:
            saturation = "低饱和度（柔和）"

        if v > 0.7:
            brightness = "高亮度"
        elif v > 0.4:
            brightness = "中等亮度"
        else:
            brightness = "低亮度（暗色）"

        return {
            'dominant': f'RGB({r}, {g}, {b})',
            'hex': '#{:02x}{:02x}{:02x}'.format(r, g, b),
            'warmth': warmth,
            'saturation': saturation,
            'brightness': brightness,
            'style': style
        }

    def _default_color_analysis(self):
        return {
            'dominant': 'RGB(128, 128, 128)',
            'hex': '#808080',
            'warmth': '中性色调',
            'saturation': '中等饱和度',
            'brightness': '中等亮度',
            'style': '平衡、和谐、稳重'
        }

    def _analyze_motion(self, frames):
        if len(frames) < 2:
            return {
                'level': '静态',
                'description': '画面相对静止或变化较少'
            }

        motion_score = 0
        for i in range(len(frames) - 1):
            diff = np.abs(frames[i].astype(float) - frames[i+1].astype(float)).mean()
            motion_score += diff

        avg_motion = motion_score / (len(frames) - 1)

        if avg_motion < 5:
            level = "静态"
            description = "画面相对静止，如访谈、静态展示、产品拍摄"
        elif avg_motion < 15:
            level = "轻度运动"
            description = "轻微运动，如人物对话、缓慢移动、日常场景"
        elif avg_motion < 30:
            level = "中度运动"
            description = "明显运动，如行走、物体移动、体育活动"
        else:
            level = "剧烈运动"
            description = "激烈运动，如舞蹈、动作场景、高速镜头"

        return {
            'level': level,
            'description': description
        }

    def _analyze_scenes(self, frames):
        if not frames:
            return {
                'type': '未知',
                'description': '无法确定场景类型'
            }

        mid_frame = frames[len(frames) // 2]
        avg_brightness = np.mean(mid_frame)

        if avg_brightness > 180:
            scene_type = "明亮室内/户外"
            description = "光线充足的场景，如日光、照明良好的室内"
        elif avg_brightness > 100:
            scene_type = "正常光照"
            description = "自然光照下的场景，如阴天、遮阳处"
        else:
            scene_type = "暗色场景"
            description = "昏暗或夜景场景，如夜间、阴影处"

        return {
            'type': scene_type,
            'description': description
        }
