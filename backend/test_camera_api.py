import base64
import requests
import json
import os

def test_camera_detect():
    # 使用一个硬编码的 1x1 黑色像素 JPEG 图片的 Base64 字符串
    base64_image = (
        "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsK"
        "CwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQU"
        "FBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAABAAEDAREAAhEBAxEB/8QAFAABAAAAAAAAAAAAAAAAAAAAAP/EABQQAQAA"
        "AAAAAAAAAAAAAAAAAAD/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMRAD8Af/9k="
    )

    base_url = "http://localhost:8000/api"
    login_url = f"{base_url}/auth/login"
    
    print(f"正在尝试登录: {login_url}")
    try:
        # 尝试默认密码 123456
        login_res = requests.post(login_url, json={
            "username": "admin",
            "password": "123456"
        })
        
        if login_res.status_code == 200:
            res_json = login_res.json()
            # 修正 Token 获取路径
            token = res_json.get("data", {}).get("token")
            
            if not token:
                print(f"❌ 登录响应中未找到 Token: {res_json}")
                return

            print("登录成功，获取到 Token")
            
            # 发送检测请求
            detect_url = f"{base_url}/camera/detect"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            payload = {"image": base64_image}
            
            print(f"正在发送检测请求: {detect_url}")
            detect_res = requests.post(detect_url, json=payload, headers=headers)
            
            if detect_res.status_code == 200:
                result = detect_res.json()
                print("检测结果:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                if result.get("success"):
                    print("✅ 摄像头后端检测接口测试通过！")
                else:
                    print(f"❌ 接口返回失败: {result.get('message')}")
            else:
                print(f"❌ 检测请求失败: {detect_res.status_code}, {detect_res.text}")
        else:
            print(f"❌ 登录失败: {login_res.status_code}, {login_res.text}")
            print("请确保后端服务已启动且数据库中有 admin 用户。")
            
    except Exception as e:
        print(f"❌ 测试发生异常: {str(e)}")

if __name__ == "__main__":
    test_camera_detect()
