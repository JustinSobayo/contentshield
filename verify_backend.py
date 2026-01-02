import http.client
import mimetypes
import os

def test_local_analyze():
    host = "localhost:8000"
    path = "/analyze"
    
    test_file_path = "test_video_dummy.mp4"
    with open(test_file_path, "wb") as f:
        # Just enough to satisfy a basic file check
        f.write(b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x01mp42isom")
        
    try:
        print(f"Sending request to http://{host}{path}...")
        
        # Manually construct multipart form data using built-in http.client
        boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
        with open(test_file_path, "rb") as f:
            file_content = f.read()

        payload = (
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="file"; filename="{test_file_path}"\r\n'
            f'Content-Type: video/mp4\r\n\r\n'
        ).encode('utf-8') + file_content + (
            f'\r\n--{boundary}\r\n'
            f'Content-Disposition: form-data; name="platform"\r\n\r\n'
            f'TikTok\r\n'
            f'--{boundary}--\r\n'
        ).encode('utf-8')

        headers = {
            'Content-Type': f'multipart/form-data; boundary={boundary}',
            'Content-Length': str(len(payload))
        }

        conn = http.client.HTTPConnection(host)
        conn.request("POST", path, body=payload, headers=headers)
        
        response = conn.getresponse()
        data = response.read().decode('utf-8')
        
        print(f"Status Code: {response.status}")
        print(f"Response: {data}")
        
        if response.status == 200:
            print("\n✅ LOCAL BACKEND IS WORKING CORRECTLY!")
        else:
            print("\n❌ LOCAL BACKEND FAILED. Check logs in the first terminal.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

if __name__ == "__main__":
    test_local_analyze()
