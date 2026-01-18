import requests
import json
import re
import time
import unicodedata
import os
from datetime import datetime
import random


    
class traodoisub:
    def __init__(self, access_token: str, proxy:str | None = None):
        self.access_token = access_token
        self.proxy = proxy
        self.session = requests.Session()

        self.session.headers.update  = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'vi,en-US;q=0.9,en;q=0.8,fr-FR;q=0.7,fr;q=0.6',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }


        self.config_proxy()

    def config_proxy(self):
        if not self.proxy:
            self.session.proxies = {}
            self.session.trust_env = False
            return

        proxy = self.proxy.strip()
        parts = proxy.split(":")

        # ip:port
        if len(parts) == 2:
            ip, port = parts
            proxy_url = f"http://{ip}:{port}"

        # ip:port:user:pass
        elif len(parts) == 4:
            ip, port, user, password = parts
            proxy_url = f"http://{user}:{password}@{ip}:{port}"

        else:
            raise ValueError(f"Proxy format không hợp lệ: {self.proxy}")

        self.session.proxies.update({
            "http": proxy_url,
            "https": proxy_url
        })

        self.session.trust_env = False

    def get_information_user(self):
        result = self.session.get(f"https://traodoisub.com/api/?fields=profile&access_token={self.access_token}", timeout=15)
        if "error" in result.text:
            return result.text
        else:
            return int(result.json()['data']['xu'])

    def set_account(self, userTikTok: str):
        url = f"https://traodoisub.com/api/?fields=tiktok_run&id={userTikTok}&access_token={self.access_token}"
        response = self.session.get(url, timeout=15)
        data = response.json()
        return data

    def _get_proxies(self, proxy_str):
        """Chuyển đổi proxy string thành dict proxies"""
        if not proxy_str:
            return {}
        
        proxy = proxy_str.strip()
        parts = proxy.split(":")
        
        # ip:port
        if len(parts) == 2:
            ip, port = parts
            proxy_url = f"http://{ip}:{port}"
        
        # ip:port:user:pass
        elif len(parts) == 4:
            ip, port, user, password = parts
            proxy_url = f"http://{user}:{password}@{ip}:{port}"
        
        else:
            raise ValueError(f"Proxy format không hợp lệ: {proxy_str}")
        
        return {
            "http": proxy_url,
            "https": proxy_url
        }

    def getJobFollow(self, max_retry: int = 3):
        url = "https://traodoisub.com/api/"
        params = {
            "fields": "tiktok_follow",
            "access_token": self.access_token
        }
        
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'vi,en-US;q=0.9,en;q=0.8,fr-FR;q=0.7,fr;q=0.6',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }
        
        proxies = self._get_proxies(self.proxy)

        for attempt in range(max_retry):
            response = requests.get(url, params=params, headers=headers, proxies=proxies, timeout=15)
            data = response.json()
            
            # Kiểm tra lỗi "Thao tác quá nhanh"
            error = data.get("error")
            if error == "Thao tác quá nhanh vui lòng chậm lại":
                countdown = data.get("countdown", 0)
                wait_time = countdown + 5
                print(f"Thao tác quá nhanh -> đợi {wait_time} giây (countdown: {countdown}s + 5s)")
                time.sleep(wait_time)
                continue
            
            # Nếu không có lỗi, trả về jobs
            jobs = data.get("data", [])
            return jobs
        
        # Hết số lần retry
        print("Hết số lần retry getJobFollow")
        return []

    def sendCache(self, idJob):
        url = "https://traodoisub.com/api/coin/"
        params = {
        "type":"TIKTOK_FOLLOW_CACHE",
        "id" : idJob,
        "access_token": self.access_token
        }

        response = self.session.get(url, params= params, timeout=15)
        data= response.json()
        return data

    def getXuFollow(self):
        url = "https://traodoisub.com/api/coin/"
        
        params = {
        "type":"TIKTOK_FOLLOW",
        "id" : "TIKTOK_FOLLOW_API",
        "access_token": self.access_token
        }

        response = self.session.get(url, params= params, timeout=15)
        return response.json()

    def claim_xu(self, max_retry: int = 2) -> bool:
        data = self.getXuFollow()
        print("getXuFollow response:", data)

        for _ in range(max_retry):
            error = data.get("error")

            # Case: quá nhanh -> đợi rồi gọi lại
            if error == "Thao tác quá nhanh vui lòng chậm lại":
                print(f"Quá nhanh -> delay 3s rồi thử lại")
                time.sleep(3)
                data = self.getXuFollow()
                print("Retry getXuFollow:", data)
                continue

            # Case: success
            if data.get("success") == 200:
                d = data.get("data", {})
                xu_them = d.get("xu_them")
                job_success = d.get("job_success")

                # job_success có thể là số (vd 9), coi != 0 là OK
                if job_success:
                    print(f"Nhận xu thành công: +{xu_them}")
                    return {"success": True, "xu_them": xu_them, "job_success": job_success}
                else:
                    print("Nhận xu thất bại (job_success falsy)")
                    return {"success": False, "xu_them": 0, "job_success": 0}

            # Case: lỗi khác
            if error:
                print("Lỗi getXuFollow:", error)
                return False

            # Case: response lạ
            print("Response getXuFollow không đúng format:", data)
            return False

        # hết retry mà vẫn gặp "quá nhanh"
        print("Hết số lần retry getXuFollow")
        return False


class tuongtaccheo:
    def __init__(self, access_token: str, proxy:str | None = None):
        self.access_token = access_token
        self.proxy = proxy
        self.session = requests.Session()

        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ""AppleWebKit/537.36 (KHTML, like Gecko) ""Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
        })

        self.user = None
        self.sodu = None
        self._logged_in = False
        self.config_proxy()

    def config_proxy(self):
        if not self.proxy:
            self.session.proxies = {}
            self.session.trust_env = False
            return

        proxy = self.proxy.strip()
        parts = proxy.split(":")

        # ip:port
        if len(parts) == 2:
            ip, port = parts
            proxy_url = f"http://{ip}:{port}"

        # ip:port:user:pass
        elif len(parts) == 4:
            ip, port, user, password = parts
            proxy_url = f"http://{user}:{password}@{ip}:{port}"

        else:
            raise ValueError(f"Proxy format không hợp lệ: {self.proxy}")

        self.session.proxies.update({
            "http": proxy_url,
            "https": proxy_url
        })

        self.session.trust_env = False

    def login(self) -> bool:
        url = f"https://tuongtaccheo.com/logintoken.php"
        payload = {"access_token": self.access_token}

        r = self.session.post(url, data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=15)
        r.raise_for_status()

        data = r.json()
        if data.get("status") == "success":
            info = data.get("data", {})
            self.user = info.get("user")
            try:
                self.sodu = int(info.get("sodu", 0))
            except Exception:
                self.sodu = info.get("sodu")

            self._logged_in = True
            return True

        self._logged_in = False
        return False
    
    def _require_login(self):
        if not self._logged_in:
            raise RuntimeError("Chưa login. Gọi ttc.login() trước.")


    CONFUSABLE_MAP = {
        # Greek
        "α": "a", "Α": "A", "ν": "v", "Ν": "N",
        "ο": "o", "Ο": "O",

        # Cyrillic
        "һ": "h", "Һ": "H", "о": "o", "О": "O",
        "і": "i", "І": "I", "ⅼ": "l", "Ь": "B",

        # Latin extended / weird
        "ḣ": "h", "ṫ": "t", "ϲ": "c", "ḋ": "d",
        "ɡ": "g",
    }

    ZERO_WIDTH = re.compile(r"[\u200b\u200c\u200d\u2060\ufeff]")

    def fix_vietnamese_text(self, text: str) -> str:
        if not text:
            return text

        # 1) normalize unicode
        text = unicodedata.normalize("NFKC", text)

        # 2) remove zero-width chars
        text = self.ZERO_WIDTH.sub("", text)

        # 3) replace confusable chars
        text = "".join(self.CONFUSABLE_MAP.get(c, c) for c in text)

        # 4) normalize spaces
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def add_tiktok(self, nickchay: str) -> bool:
        self._require_login()
        
        url = "https://tuongtaccheo.com/cauhinh/addtiktok.php"

        params = {
            "link": nickchay,
            "nickchay": nickchay
        }

        headers = {
            "Accept": "*/*",
            "Accept-Language": "vi,en-US;q=0.9,en;q=0.8",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://tuongtaccheo.com/tiktok/kiemtien/cmtcheo/",
        }

        response = self.session.get(
            url,
            headers=headers,
            params=params,
            timeout=15
        )

        text = response.text.strip()
        print("Response:", text)

        # ======================
        # THÀNH CÔNG
        # ======================
        if text.startswith("1"):
            return True

        return False

    def getJobCmtTikTok(self):
        self._require_login()
        
        url = "https://tuongtaccheo.com/tiktok/kiemtien/cmtcheo/getpost.php"

        headers = {
            "X-Requested-With": "XMLHttpRequest",
        }

        r = self.session.get(url, headers=headers, timeout=15)

        try:
            data = r.json()
            # print(data)
        except Exception:
            return {"total": 0, "jobs": [], "error": "Response không phải JSON"}

        # ======================
        # 1️⃣ CHECK DELAY / COUNTDOWN
        # ======================
        if isinstance(data, dict) and ("msg" in data or "error" in data):
            text = str(data)
            match = re.search(r"(\d+)\s*giây", text)
            countdown = int(match.group(1)) if match else data.get("time", 60)

            print(f"⏳ Bị delay, chờ {countdown} giây...")
            for i in range(countdown, 0, -1):
                print(f"\r⏱️  Còn {i} giây...", end="", flush=True)
                time.sleep(1)

            print("\n✅ Hết delay, tiếp tục...")
            return {"total": 0, "jobs": [], "delay": countdown}

        # ======================
        # 2️⃣ XỬ LÝ JOB BÌNH THƯỜNG
        # ======================
        jobs = []
        items = data.values() if isinstance(data, dict) else data

        for item in items:
            idpost = item.get("idpost")
            link = item.get("link")
            nd_raw = item.get("nd")

            nd_first = None
            try:
                nd_list = json.loads(nd_raw) if isinstance(nd_raw, str) else nd_raw
                if isinstance(nd_list, list) and nd_list:
                    nd_first = self.fix_vietnamese_text(nd_list[1])  # ✅ FIX NGAY Ở ĐÂY
            except Exception:
                pass

            jobs.append({
                "idpost": idpost,
                "link": link,
                "nd_first": nd_first
            })

        return {"total": len(jobs), "jobs": jobs}


    def nhan_tien_cmtcheo(self, comment_id: str):
        self._require_login()

        url = "https://tuongtaccheo.com/tiktok/kiemtien/cmtcheo/nhantien.php"

        headers = {
            "Accept": "*/*",
            "Accept-Language": "vi,en-US;q=0.9,en;q=0.8",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://tuongtaccheo.com",
            "X-Requested-With": "XMLHttpRequest"
        }

        data = {"id": comment_id}

        max_retry = 5
        timeout_sec = 15

        for attempt in range(1, max_retry + 1):
            try:
                response = self.session.post(
                    url,
                    headers=headers,
                    data=data,
                    timeout=timeout_sec
                )

                # retry nếu server lỗi / bị limit
                if response.status_code in (429, 500, 502, 503, 504):
                    if attempt < max_retry:
                        sleep_time = (2 ** attempt) + random.uniform(0.3, 1.2)
                        time.sleep(sleep_time)
                        continue

                return {
                    "status_code": response.status_code,
                    "text": response.text
                }

            except (requests.exceptions.ReadTimeout,
                    requests.exceptions.ConnectTimeout,
                    requests.exceptions.ProxyError,
                    requests.exceptions.SSLError,
                    requests.exceptions.ConnectionError) as e:

                if attempt == max_retry:
                    return {
                        "status_code": -1,
                        "text": f"Request failed after {max_retry} retries: {e}"
                    }

                sleep_time = (2 ** attempt) + random.uniform(0.3, 1.2)
                time.sleep(sleep_time)




class messageSource:
    def openApp(bundleID: str):
        return f'at.appRun("{bundleID}")'

    def openURL(url: str):
        return f'at.openURL("{url}")'

    def comment(link: str, text: str):
        message = f"""
    function tapAddCommentWait5s(image_path, rx, ry, rz, rt)
        local startTime = os.time()
        local timeout = 5
        local region = {{rx, ry, rz, rt}}

        while (os.time() - startTime) < timeout do
            local result = findImage(image_path, 1, 0.95, region, true, 1)

            if result ~= nil and #result > 0 then
                local x = result[1][1]
                local y = result[1][2]

                tap(x, y)
                usleep(1500000)
                return true, x, y
            end

            usleep(200000)
        end

        return false, nil, nil
    end

    local curl = require('lcurl')
    local localip = getLocalIP()
    openURL("{link}")
    toast("Chờ 6 giây", 6)
    usleep(6000000)
    tap(692, 760)
    usleep(1500000)
    

    copyText("{text}")
    local okAdd, x, y = tapAddCommentWait5s("addcomment.png", 120, 1215, 80, 50)
    if okAdd then
        usleep(2000000)
        local okAdd, x, y = tapAddCommentWait5s("addcomment.png", 80, 500, 200, 300)
        if okAdd then
            local okAdd, x, y = tapAddCommentWait5s("paste.png", 80, 500, 200, 300)
            if okAdd then
                local okAdd, x, y = tapAddCommentWait5s("sendcomment.png", 610, 750, 200, 300)
                if okAdd then
                    usleep(5000000)
                    
                    local url = string.format(
                    "http://192.168.1.2:5000/api?action=updateStatus&localip=%s&message=Jobdone",
                    tostring(localip)
                    )
                    curl.easy{{
                        url = url,
                        httpheader = {{
                        "X-Test-Header1: Header-Data1",
                        "X-Test-Header2: Header-Data2",
                        }},
                    }}
                    :perform()
                    :close()

                else
                    local url = string.format(
                    "http://192.168.1.2:5000/api?action=updateStatus&localip=%s&message=Jobfail",
                    tostring(localip)
                    )
                    curl.easy{{
                        url = url,
                        httpheader = {{
                        "X-Test-Header1: Header-Data1",
                        "X-Test-Header2: Header-Data2",
                        }},
                    }}
                    :perform()
                    :close()
                end
            else
                local url = string.format(
                "http://192.168.1.2:5000/api?action=updateStatus&localip=%s&message=Jobfail",
                tostring(localip)
                )
                curl.easy{{
                    url = url,
                    httpheader = {{
                    "X-Test-Header1: Header-Data1",
                    "X-Test-Header2: Header-Data2",
                    }},
                }}
                :perform()
                :close()           
            end
        else
            local url = string.format(
            "http://192.168.1.2:5000/api?action=updateStatus&localip=%s&message=Jobfail",
            tostring(localip)
            )
            curl.easy{{
                url = url,
                httpheader = {{
                "X-Test-Header1: Header-Data1",
                "X-Test-Header2: Header-Data2",
                }},
            }}
            :perform()
            :close()
        end
    else
        local url = string.format(
        "http://192.168.1.2:5000/api?action=updateStatus&localip=%s&message=Jobfail",
        tostring(localip)
        )
        curl.easy{{
            url = url,
            httpheader = {{
            "X-Test-Header1: Header-Data1",
            "X-Test-Header2: Header-Data2",
            }},
        }}
        :perform()
        :close()
    end
        """
        return message

    def follow(link: str):
        message = f"""
    function tapAddCommentWait5s(image_path, rx, ry, rz, rt)
        local startTime = os.time()
        local timeout = 5
        local region = {{rx, ry, rz, rt}}

        while (os.time() - startTime) < timeout do
            local result = findImage(image_path, 1, 0.95, region, false, 1)

            if result ~= nil and #result > 0 then
                local x = result[1][1]
                local y = result[1][2]

                tap(x, y)
                usleep(1500000)
                return true, x, y
            end

            usleep(200000)
        end

        return false, nil, nil
    end


    openURL("{link}")
    toast("Chờ 6 giây", 6)
    usleep(6000000)

    local okAdd, x, y = tapAddCommentWait5s("fl.png", 100, 400, 300, 300)
    if okAdd then
        usleep(5000000)
        local curl = require('lcurl')
        local localip = getLocalIP()
        local url = string.format(
        "http://192.168.1.2:5000/api?action=updateStatus&localip=%s&message=Jobdone",
        tostring(localip)
        )
        curl.easy{{
            url = url,
            httpheader = {{
            "X-Test-Header1: Header-Data1",
            "X-Test-Header2: Header-Data2",
            }},
        }}
        :perform()
        :close()

    else
        local curl = require('lcurl')
        local localip = getLocalIP()
        local url = string.format(
        "http://192.168.1.2:5000/api?action=updateStatus&localip=%s&message=Jobfail",
        tostring(localip)
        )
        curl.easy{{
            url = url,
            httpheader = {{
            "X-Test-Header1: Header-Data1",
            "X-Test-Header2: Header-Data2",
            }},
        }}
        :perform()
        :close()
    end

    """
        return message

    def luot_tiktok_truoc_khi_chay():
        message = f"""
        function swipeVertically()
            local times = math.random(3, 6)

            for i = 1, times do
                -- Random clickLove mỗi lần vuốt (true/false)
                local clickLove = (math.random(1, 2) == 1)

                touchDown(1, 200, 900)
                for y = 900, 300, -30 do
                    usleep(8000)
                    touchMove(1, 200, y)
                end
                touchUp(1, 200, 300)

                -- Nếu clickLove = true thì click love
                if clickLove then
                    usleep(2000000)
                    toast("Click love")
                    log("Click love")
                    tap(688, 620)
                end

                -- Delay ngẫu nhiên 4 đến 6 giây
                usleep(math.random(8000000, 8000000))
            end
        end

        toast("Open app TikTok delay 10s", 10)
        appActivate("com.ss.iphone.ugc.Ame")
        usleep(10000000)
        toast("Tiến hành lướt video")
        swipeVertically()

        local localip = getLocalIP()
        local url = string.format(
        "http://192.168.1.2:5000/api?action=updateStatus&localip=%s&message=Jobdone",
        tostring(localip)
        )
        openURL(url)

        """
        return message
    
class serverJob:
    def createJob(localip: str):
        api = f"http://127.0.0.1:5000/api?action=createJob&localip={localip}&message=hello"
        try:
            r = requests.get(api, timeout=10)
            
            if r.status_code != 200:
                return False
            
            # Parse JSON response
            try:
                data = r.json()
                # Kiểm tra nếu status là "create done"
                if isinstance(data, dict) and data.get("status") == "create done":
                    return True
                return False
            except json.JSONDecodeError:
                return False
        except Exception as e:
            print(f"Error in createJob: {e}")
            return False

    def checkStatusJob(localip: str, max_retry: int = 10, retry_interval: int = 5):
        """
        Kiểm tra status job với retry tự động
        Returns:
            True: Job hoàn thành thành công
            False: Job thất bại hoặc hết số lần retry
        """
        api = f"http://127.0.0.1:5000/api?action=checkStatus&localip={localip}"
        
        for attempt in range(max_retry):
            try:
                r = requests.get(api, timeout=10)
                if r.status_code != 200:
                    # Nếu không phải lần cuối, đợi rồi thử lại
                    if attempt < max_retry - 1:
                        time.sleep(retry_interval)
                        continue
                    return False
                
                # Parse JSON response
                try:
                    data = r.json()
                    # Kiểm tra status field và message trong response
                    if isinstance(data, dict):
                        # Response thành công: status = true VÀ message = "Jobdone"
                        if data.get("status") == True and data.get("message") == "Jobdone":
                            return True
                        # Response fail: status = false, có error, hoặc message = "Jobfail"
                        if data.get("status") == True and data.get("message") == "Jobfail":
                            return False
                        # Nếu status = true nhưng message != "Jobdone" thì vẫn chưa done
                        # Đợi rồi thử lại (trừ lần cuối)
                        if attempt < max_retry - 1:
                            time.sleep(retry_interval)
                            continue
                        return False
                    # Không phải dict, đợi rồi thử lại (trừ lần cuối)
                    if attempt < max_retry - 1:
                        time.sleep(retry_interval)
                        continue
                    return False
                except json.JSONDecodeError:
                    # Lỗi parse JSON, đợi rồi thử lại (trừ lần cuối)
                    if attempt < max_retry - 1:
                        time.sleep(retry_interval)
                        continue
                    return False
            except Exception as e:
                print(f"Error in checkStatusJob (attempt {attempt + 1}/{max_retry}): {e}")
                # Nếu không phải lần cuối, đợi rồi thử lại
                if attempt < max_retry - 1:
                    time.sleep(retry_interval)
                    continue
                return False
        
        # Hết số lần retry
        return False

    def updateStatusJob(localip: str, message: str):
        api = f"http://127.0.0.1:5000/api?action=updateStatus&localip={localip}&message={message}"
        r = requests.get(api, timeout=10)
        return r.status_code

    def deleteJob(localip: str):
        api = f"http://127.0.0.1:5000/api?action=deleteJob&localip={localip}"
        r = requests.get(api, timeout=10)
        return r.status_code



class WaitGetXuManager:
    """Quản lý các job đang chờ nhận xu"""
    FILE_NAME = "waitgetxu.txt"
    
    @staticmethod
    def add_job(job_id: str, localip: str):
        """Thêm job vào file chờ nhận xu với localip"""
        current_time = time.time()
        job_data = {
            "idpost": job_id,
            "localip": localip,
            "timestamp": current_time,
            "datetime": datetime.fromtimestamp(current_time).strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Đọc file hiện tại
        jobs = []
        if os.path.exists(WaitGetXuManager.FILE_NAME):
            try:
                with open(WaitGetXuManager.FILE_NAME, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        jobs = json.loads(content)
            except Exception as e:
                print(f"Lỗi đọc file {WaitGetXuManager.FILE_NAME}: {e}")
                jobs = []
        
        # Kiểm tra xem job đã tồn tại chưa (theo idpost và localip)
        job_exists = any(j.get("idpost") == job_id and j.get("localip") == localip for j in jobs)
        if not job_exists:
            jobs.append(job_data)
            
            # Ghi lại file
            try:
                with open(WaitGetXuManager.FILE_NAME, "w", encoding="utf-8") as f:
                    json.dump(jobs, f, ensure_ascii=False, indent=2)
                print(f"Đã lưu job {job_id} (localip: {localip}) vào file chờ nhận xu")
            except Exception as e:
                print(f"Lỗi ghi file {WaitGetXuManager.FILE_NAME}: {e}")
    
    @staticmethod
    def remove_job(job_id: str):
        """Xóa job khỏi file"""
        if not os.path.exists(WaitGetXuManager.FILE_NAME):
            return
        
        try:
            with open(WaitGetXuManager.FILE_NAME, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    jobs = json.loads(content)
                    jobs = [j for j in jobs if j.get("idpost") != job_id]
                    
                    with open(WaitGetXuManager.FILE_NAME, "w", encoding="utf-8") as f:
                        json.dump(jobs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Lỗi xóa job từ file: {e}")
    
    @staticmethod
    def get_ready_jobs(ttc_instance, localip: str, min_wait_seconds: int = 30):
        """Lấy danh sách các job đã đủ thời gian chờ của máy cụ thể"""
        if not os.path.exists(WaitGetXuManager.FILE_NAME):
            return []
        
        try:
            with open(WaitGetXuManager.FILE_NAME, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                jobs = json.loads(content)
        except Exception as e:
            print(f"Lỗi đọc file {WaitGetXuManager.FILE_NAME}: {e}")
            return []
        
        current_time = time.time()
        ready_jobs = []
        
        for job in jobs:
            job_id = job.get("idpost")
            job_localip = job.get("localip")
            timestamp = job.get("timestamp")
            
            if not job_id or not timestamp:
                continue
            
            # Chỉ lấy job của máy hiện tại
            if job_localip != localip:
                continue
            
            elapsed = current_time - timestamp
            
            if elapsed >= min_wait_seconds:
                ready_jobs.append(job)
        
        return ready_jobs
    
    @staticmethod
    def process_ready_jobs(ttc_instance: 'tuongtaccheo', localip: str, failJob, maxFailJob, countJob, maxJob, min_wait_seconds: int = 30):
        """
        Xử lý các job đã đủ thời gian chờ của máy cụ thể
        Args:
            ttc_instance: Instance của class tuongtaccheo
        Returns: (countJob, failJob, total_xu_them) đã cập nhật
        """
        ready_jobs = WaitGetXuManager.get_ready_jobs(ttc_instance, localip, min_wait_seconds)
        
        if not ready_jobs:
            return countJob, failJob, 0
        
        print(f"\n🔔 Kiểm tra {len(ready_jobs)} job đã đủ thời gian chờ...")
        
        total_xu_them = 0
        
        for job_data in ready_jobs:
            job_id = job_data.get("idpost")
            elapsed = time.time() - job_data.get("timestamp")
            
            print(f"  ⏰ Job {job_id} đã chờ {elapsed:.1f} giây, tiến hành nhận xu...")
            
            try:
                # Gọi method nhan_tien_cmtcheo từ instance tuongtaccheo
                result = ttc_instance.nhan_tien_cmtcheo(job_id)
                print(f"  Result: {result}")
                
                # Parse JSON từ text response
                response_text = result.get("text", "")
                is_success = False
                xu_them = 0
                
                try:
                    # Thử parse JSON từ text
                    response_data = json.loads(response_text)
                    if isinstance(response_data, dict):
                        mess = response_data.get("mess", "")
                        if "Thành công" in mess and "cộng" in mess:
                            is_success = True
                            # Tìm số xu trong message (ví dụ: "cộng 100 xu")
                            xu_match = re.search(r"cộng\s+(\d+)", mess)
                            if xu_match:
                                xu_them = int(xu_match.group(1))
                except (json.JSONDecodeError, TypeError):
                    # Nếu không phải JSON, kiểm tra text trực tiếp
                    if "Thành công" in response_text and "cộng" in response_text:
                        is_success = True
                        # Tìm số xu trong text
                        xu_match = re.search(r"cộng\s+(\d+)", response_text)
                        if xu_match:
                            xu_them = int(xu_match.group(1))
                
                if is_success:
                    print(f"  ✅ Nhận tiền thành công cho job {job_id}: +{xu_them} xu")
                    total_xu_them += xu_them
                    failJob = 0  # Reset failJob
                    countJob += 1
                    print(f"  Hoàn thành job {countJob} / {maxJob}")
                    time.sleep(3)
                else:
                    print(f"  ❌ Nhận tiền thất bại cho job {job_id}")
                    failJob += 1
                    print(f"  Fail job {failJob} / {maxFailJob}")
                    time.sleep(3)
                
                # Xóa job khỏi file sau khi xử lý
                WaitGetXuManager.remove_job(job_id)
                
            except Exception as e:
                print(f"  ❌ Lỗi khi nhận tiền cho job {job_id}: {e}")
                failJob += 1
        
        return countJob, failJob, total_xu_them

def get_acc_safeum():
    file_path = 'cookie.txt'
    index_path = 'cookie_index.txt'

    try:
        # Đọc index hiện tại
        current_index = 0
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                index_content = f.read().strip()
                if index_content.isdigit():
                    current_index = int(index_content)
        except FileNotFoundError:
            # File index chưa tồn tại, bắt đầu từ 0
            pass
        except Exception as e:
            print(f"Cảnh báo: Không thể đọc file index: {e}")

        # Đọc tất cả các dòng từ file cookie.txt
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        if not lines:
            print(f"Cảnh báo: File '{file_path}' trống.")
            return None

        # Lấy dòng theo index hiện tại (modulo để quay vòng)
        line = lines[current_index % len(lines)]

        # Cập nhật index cho lần đọc tiếp theo
        next_index = (current_index + 1) % len(lines)
        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(str(next_index))
        except Exception as e:
            print(f"Cảnh báo: Không thể ghi file index: {e}")

        return line

    except Exception as e:
        print(f"Đã xảy ra lỗi khi xử lý file: {e}")
        return None

class autoTouch:
    def post_lua_payload(ip_port, message, name_file: str):
        url = f"http://{ip_port}/file/update?path=/{name_file}"

        payload = """
        """ + message + """
        """

        headers = {
            "Content-Type": "text/plain; charset=utf-8",
            "Accept": "application/json"
        }

        r = requests.post(url, data=payload.encode("utf-8"), headers=headers, timeout=10)


    def get_playSource(ip_port, name_file: str):
        url = f"http://{ip_port}/control/start_playing?path=%2F{name_file}"
        r = requests.get(url, timeout=10)
        return r.text

# tds = traodoisub(access_token="TDS0nIzIXZ2V2ciojIyVmdlNnIsISMhZjMxAzMxMHZ0lHc2VGZiojIyV2c1Jye", proxy="163.47.31.110:40338:Proxy_l4vj8oqt:8VPQU8ZQFK")



# data = get_acc_safeum()
# localip, access_token, userTikTok = data.split("|")


# ip, _ = localip.split(":")

# ttc = tuongtaccheo(access_token=access_token)
# if not ttc.login():
#     print("Login TTC False")
#     exit()
# else:
#     ttc.add_tiktok(nickchay=userTikTok)

# countJob = 0
# maxJob = 5
# failJob = 0
# maxFailJob = 10

# # Biến để track thời gian check waitgetxu.txt (mỗi 40 giây)
# last_check_waitxu = 0
# CHECK_WAITXU_INTERVAL = 40  # 40 giây

# while countJob < maxJob:
#     if failJob >= maxFailJob:
#         print("Acc nhả mẹ rồi, stop")
#         break
    
#     # ---------- KIỂM TRA CÁC JOB CHỜ NHẬN XU (mỗi 40 giây) ----------
#     current_time = time.time()
    
#     if current_time - last_check_waitxu >= CHECK_WAITXU_INTERVAL:
#         last_check_waitxu = current_time
#         countJob, failJob = WaitGetXuManager.process_ready_jobs(
#             ttc,
#             ip,  # Truyền localip để filter job của máy này
#             failJob,
#             maxFailJob,
#             countJob,
#             maxJob,
#             min_wait_seconds=50
#         )
        
#         # Kiểm tra sau khi xử lý waitgetxu
#         if countJob >= maxJob:
#             print(f"\n✅ Đã hoàn thành đủ {maxJob} job(s), dừng chương trình!")
#             break
        
#         if failJob >= maxFailJob:
#             print("Acc nhả mẹ rồi, stop")
#             break

#     # ---------- LẤY JOB ----------
#     resp = ttc.getJobCmtTikTok()
    
#     # Kiểm tra nếu có lỗi (có thể do session hết hạn)
#     if resp.get("error"):
#         print(f"Lỗi khi lấy job: {resp.get('error')}")
#         print("Reset session và đăng nhập lại...")
#         ttc._logged_in = False
#         continue
        
#     # Xử lý delay
#     if resp.get("delay"):
#         print(f"Bị delay {resp['delay']} giây, chờ xong delay...")
#         # Delay đã được xử lý trong getJobCmtTikTok, tiếp tục lấy job
#         continue
    
#     # Kiểm tra có jobs không
#     jobs = resp.get("jobs", [])
#     total = resp.get("total", 0)
    
#     if not jobs or total == 0:
#         print("Không có job, chờ 15 giây rồi lấy lại...")
#         time.sleep(15)
#         continue
    
#     # ---------- XỬ LÝ TỪNG JOB TRONG LIST ----------
#     print(f"Lấy được {total} job(s), bắt đầu xử lý...")
#     for job in jobs:
#         if not job.get("idpost"):
#             print("Job không có idpost, bỏ qua")
#             continue
            
#         print(f"\n=== Xử lý job: {job['idpost']} ===")
#         print(f"Link: {job['link']}")
#         print(f"Nội dung: {job['nd_first']}")

#         print("Gửi job đến auto touch")
#         autoTouch.post_lua_payload(localip, message=messageSource.comment(job["link"], job["nd_first"]), name_file="test.lua")
#         time.sleep(2)

#         print("Tiến hành chạy job...")
#         autoTouch.get_playSource(localip, name_file="test.lua")
#         time.sleep(2)

#         print("Tạo job trên server")
#         if not serverJob.createJob(localip=ip):
#             print("Không thể tạo job trên server")
#             failJob += 1
#             print(f"Fail job {failJob} / {maxFailJob}")
#             # Kiểm tra failJob sẽ được thực hiện ở cuối vòng lặp for job
#             continue
        
#         time.sleep(2)
#         job_done = False
#         for i in range(10):
#             statusJob = serverJob.checkStatusJob(localip=ip)
#             if statusJob:
#                 # Job đã done, lưu vào file chờ nhận xu thay vì nhận ngay
#                 print(f"Job {job['idpost']} đã done, lưu vào file chờ nhận xu...")
#                 WaitGetXuManager.add_job(job["idpost"], ip)  # Lưu kèm localip
#                 job_done = True
                
#                 # Xóa job trên server
#                 serverJob.deleteJob(localip=ip)
                
#                 # Kiểm tra ngay các job trong file waitgetxu.txt đã đủ thời gian
#                 print("Kiểm tra các job đã đủ thời gian chờ...")
#                 countJob, failJob = WaitGetXuManager.process_ready_jobs(
#                     ttc,
#                     ip,  # Truyền localip để filter job của máy này
#                     failJob,
#                     maxFailJob,
#                     countJob,
#                     maxJob,
#                     min_wait_seconds=50
#                 )
                
#                 # Kiểm tra lại sau khi xử lý waitgetxu
#                 if countJob >= maxJob or failJob >= maxFailJob:
#                     if countJob >= maxJob:
#                         print(f"\n✅ Đã hoàn thành đủ {maxJob} job(s), dừng chương trình!")
#                     elif failJob >= maxFailJob:
#                         print("Acc nhả mẹ rồi, stop")
#                     break  # Break khỏi vòng lặp for job in jobs
                
#                 break  # Thoát khỏi vòng lặp check status
#             else:
#                 print("Chờ job done...")
#                 time.sleep(5)
        
#         # Nếu job timeout (không done sau 10 lần check)
#         if not job_done:
#             print("Job fail (timeout)")
#             serverJob.deleteJob(localip=ip)
#             failJob += 1
#             print(f"Fail job {failJob} / {maxFailJob}")

#         # Kiểm tra điều kiện dừng sau mỗi job (tránh trùng lặp)
#         if countJob >= maxJob:
#             print(f"\n✅ Đã hoàn thành đủ {maxJob} job(s), dừng chương trình!")
#             break
        
#         if failJob >= maxFailJob:
#             print("Acc nhả mẹ rồi, stop")
#             break
        
#         print("Chờ 10 giây trước khi xử lý job tiếp theo...")
    
#     # Kiểm tra điều kiện dừng sau khi xử lý hết jobs trong list
#     # (Kiểm tra này chỉ chạy nếu không break trong vòng lặp for job)
#     if countJob >= maxJob or failJob >= maxFailJob:
#         if countJob >= maxJob:
#             print(f"\n✅ Đã hoàn thành đủ {maxJob} job(s), dừng chương trình!")
#         elif failJob >= maxFailJob:
#             print("Acc nhả mẹ rồi, stop")
#         break
    
#     # Sau khi xử lý hết jobs, quay lại lấy job mới
#     # (Vòng lặp while sẽ tự động dừng nếu countJob >= maxJob)
#     if countJob < maxJob:
#         print("\nĐã xử lý hết jobs trong list, lấy job mới...\n")

                


    


