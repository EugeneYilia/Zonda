import os
import subprocess
import shutil

def extract_face_from_video(video_path, output_assets_dir):
    """从视频中提取素材图像（调用 prepare_data.py）"""
    if not os.path.exists(output_assets_dir) or not os.listdir(output_assets_dir):
        print(f"从视频提取素材图像：{video_path} → {output_assets_dir}")
        cmd = [
            "python", "prepare_data.py",
            "--video_path", video_path,
            "--output_dir", os.path.dirname(output_assets_dir)
        ]
        subprocess.run(cmd, check=True)
    else:
        print("素材图像目录已存在，跳过提取")

def run_dh_live_demo(video_path, audio_path, output_name):
    assets_dir = os.path.join(os.path.splitext(video_path)[0], "assets")

    # Step 1: 提取人脸图像
    extract_face_from_video(video_path, assets_dir)

    # Step 2: 找一张图像作为驱动图
    supported_ext = ['.jpg', '.png']
    img_file = None
    for fname in os.listdir(assets_dir):
        if os.path.splitext(fname)[1].lower() in supported_ext:
            img_file = os.path.join(assets_dir, fname)
            if fname == '0.jpg':
                break
    if not img_file:
        raise Exception("未在 assets 目录中找到图片")

    print(f"使用图片：{img_file}")
    print(f"使用音频：{audio_path}")

    # Step 3: 调用 demo.py
    result_dir = "results"
    os.makedirs(result_dir, exist_ok=True)

    cmd = [
        "python", "demo.py",
        "--driven_audio", audio_path,
        "--source_image", img_file,
        "--result_dir", result_dir,
        "--still",
        "--preprocess", "full"
    ]
    print("运行命令：", ' '.join(cmd))
    subprocess.run(cmd, check=True)

    # Step 4: 拷贝输出结果
    result_video = os.path.join(result_dir, "result.mp4")
    if not os.path.exists(result_video):
        raise Exception("结果视频未生成")

    shutil.copy(result_video, output_name)
    print(f"✅ 已生成视频：{output_name}")


# 示例调用
if __name__ == "__main__":
    run_dh_live_demo(
        video_path="video_data/laoliu_nospeak.mp4",
        audio_path="video_data/audio0.wav",
        output_name="1.mp4"
    )
