from module import *
from ui import TikTokTDSUI
import threading
from concurrent.futures import ThreadPoolExecutor
import time


# Khởi tạo UI
ui = TikTokTDSUI()

# Hiển thị dialog nhập liệu trước
ui.show_input_dialog()

# Lấy giá trị
total_threads = ui.total_threads
concurrent_threads = ui.concurrent_threads

if total_threads is None or concurrent_threads is None:
    print("Đã hủy!")
    exit()

if concurrent_threads > total_threads:
    concurrent_threads = total_threads
    print(f"Điều chỉnh số luồng đồng thời thành {concurrent_threads}")

# Lấy danh sách account
accounts = []
for i in range(total_threads):
    account_data = get_acc_safeum()
    if not account_data:
        print(f"Không đủ account! Chỉ lấy được {len(accounts)} account")
        break
    accounts.append(account_data)

# Thông báo nếu có account bị lặp lại
if accounts:
    unique_accounts = len(set(accounts))
    if unique_accounts < len(accounts):
        print(f"Lưu ý: Đang sử dụng {unique_accounts} account unique cho {len(accounts)} luồng (có lặp lại)")

if not accounts:
    ui.add_row("", "", "", "Không có account")
    ui.run()
    exit()

def run_jobs_for_device(account_data):
    """Chạy các job cho một thiết bị"""
    try:
        serverlocal = messageSource.get_ipv4_from_ipconfig()
        luot_tiktok_truoc_khi_chay = False

        localip, access_token, proxy, userTikTok = account_data.split("|")
        ip, _ = localip.split(":")
        
        # Thêm dữ liệu vào UI
        ui.add_row(localip, access_token, userTikTok, "Đang khởi tạo...")
        
        tds = traodoisub(access_token=access_token, proxy=proxy)
        
        # set_account_result = tds.set_account(userTikTok)
        # ui.update_status(localip, "Delay sau khi set acc 15s...")
        # time.sleep(15)

        if luot_tiktok_truoc_khi_chay:
            ui.update_status(localip, "Lướt Tiktok trước khi chạy job...")
            serverJob.deleteJob(localip=ip)
            time.sleep(1)
            serverJob.createJob(localip=ip)
            time.sleep(1)
            autoTouch.post_lua_payload(localip, message=messageSource.luot_tiktok_truoc_khi_chay(serverlocal), name_file="test.lua")
            autoTouch.get_playSource(localip, name_file="test.lua")
        
            ui.update_status(localip, "Kiểm tra lướt Tiktok trước khi chạy job...")
            for i in range(15):
                statusJob = serverJob.checkStatusJob(localip=ip)
                if statusJob:
                    ui.update_status(localip, "Lướt Tiktok trước khi chạy job thành công")
                    serverJob.deleteJob(localip=ip)
                    break
                else:
                    time.sleep(5)
            
        countJob = 0
        maxJobDone = 400
        
        jobcache_done = 0
        job_success_paid = 0
        total_xu_them = 0
        
        ui.update_job_progress(localip, jobcache_done, job_success_paid)
        ui.update_xu_them(localip, total_xu_them)
        
        while countJob < maxJobDone:
            ui.update_status(localip, "Đang lấy job...")
            jobs = tds.getJobFollow()
            
            if len(jobs) == 0:
                ui.update_status(localip, "Không có job, đợi 60s...")
                time.sleep(60)
                continue
            
            for job in jobs:
                if countJob >= maxJobDone:
                    print(f"[{localip}] Đã làm đủ job")
                    ui.update_status(localip, "Đã làm đủ job")
                    return
                
                print(f"[{localip}] idjob: {job.get('id')}")
                print(f"[{localip}] Link: {job.get('link')}")
                
                ui.update_status(localip, "Tạo job trên server...")
                serverJob.deleteJob(localip=ip)
                time.sleep(1)
                if not serverJob.createJob(localip=ip):
                    print(f"[{localip}] Không thể tạo job trên server")
                    ui.update_status(localip, "Lỗi: Không tạo được job")
                    continue
                
                ui.update_status(localip, "Gửi job đến auto touch...")
                autoTouch.post_lua_payload(localip, message=messageSource.follow(serverlocal, job["link"]), name_file="test.lua")
                time.sleep(2)
                
                ui.update_status(localip, "Chạy job trên iOS...")
                autoTouch.get_playSource(localip, name_file="test.lua")
                time.sleep(2)
                
                ui.update_status(localip, "Kiểm tra job...")
                jobdone = serverJob.checkStatusJob(localip=ip)
                serverJob.deleteJob(localip=ip)
                
                if not jobdone:
                    ui.update_status(localip, "Lỗi: Job không hoàn thành")
                    time.sleep(8)
                    continue
                
                ui.update_status(localip, "Job hoàn thành")
                time.sleep(8)
                
                ui.update_status(localip, "Gửi cache...")
                response = tds.sendCache(idJob=job["id"])
                
                error = response.get("error")
                if error:
                    ui.update_status(localip, f"Lỗi: {error}")
                    return
                
                msg = response.get("msg")
                if msg == "Thành công":                    
                    jobcache_done += 1
                    ui.update_job_progress(localip, jobcache_done, job_success_paid)
                
                else:
                    print(f"[{localip}] sendCache trả msg không như kỳ vọng: {msg}")
                    ui.update_status(localip, f"Lỗi: {msg}")
                    return
                
                cache = response.get("cache", 0)
                if cache >= 8:
                    ui.update_status(localip, "Nhận xu...")
                    print(f"[{localip}] Cache đủ 8 -> tiến hành nhận xu")
                    result = tds.claim_xu()
                    if result.get("success"):
                        xu_them_received = result.get("xu_them", 0)
                        total_xu_them += xu_them_received
                        print(f"[{localip}] ✅ Nhận xu thành công: +{xu_them_received}")
                        print(f"[{localip}] 📊 Tổng xu thêm: {total_xu_them}")
                        job_success_paid += result.get("job_success")
                        ui.update_job_progress(localip, jobcache_done, job_success_paid)
                        ui.update_xu_them(localip, total_xu_them)
                        time.sleep(5)
                        print(f"[{localip}] ==================================================")
                    else:
                        print(f"[{localip}] Nhận xu thất bại")
                        ui.update_status(localip, "❌ Nhận xu thất bại")
                        print(f"[{localip}] ==================================================")
                        return
                else:
                    ui.update_status(localip, f"Đang chạy - Cache: {cache}/8")
                    print(f"[{localip}] ==================================================")
                
                countJob += 1
                
    except Exception as e:
        print(f"[{account_data.split('|')[0] if '|' in account_data else 'Unknown'}] Lỗi: {e}")
        if '|' in account_data:
            localip = account_data.split("|")[0]
            ui.update_status(localip, f"Lỗi: {str(e)}")

def run_all_devices():
    """Chạy jobs cho tất cả thiết bị trong background"""
    if accounts:
        # Sử dụng ThreadPoolExecutor để quản lý threads
        with ThreadPoolExecutor(max_workers=concurrent_threads) as executor:
            futures = [executor.submit(run_jobs_for_device, account) for account in accounts]
            
            # Đợi tất cả threads hoàn thành
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    print(f"Lỗi khi chạy thread: {e}")

# Chạy jobs trong background thread để không block UI
if accounts:
    job_thread = threading.Thread(target=run_all_devices, daemon=True)
    job_thread.start()

# Chạy UI (blocking)
ui.run()
