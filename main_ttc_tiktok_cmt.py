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
        luot_tiktok_truoc_khi_chay = False

        localip, access_token, proxy, userTikTok = account_data.split("|")
        ip, _ = localip.split(":")
        
        # Thêm dữ liệu vào UI
        ui.add_row(localip, access_token, userTikTok, "Đang khởi tạo...")
        
        ttc = tuongtaccheo(access_token=access_token, proxy=proxy)
        ttc.login()


        

        if luot_tiktok_truoc_khi_chay:
            ui.update_status(localip, "Lướt Tiktok trước khi chạy job...")
            serverJob.deleteJob(localip=ip)
            time.sleep(1)
            serverJob.createJob(localip=ip)
            time.sleep(1)
            autoTouch.post_lua_payload(localip, message=messageSource.luot_tiktok_truoc_khi_chay(), name_file="test.lua")
            autoTouch.get_playSource(localip, name_file="test.lua")
        
            ui.update_status(localip, "Kiểm tra lướt Tiktok trước khi chạy job...")
            statusJob = serverJob.checkStatusJob(localip=ip, max_retry=15, retry_interval=5)
            serverJob.deleteJob(localip=ip)
            if statusJob:
                ui.update_status(localip, "Lướt Tiktok trước khi chạy job thành công")
            else:
                ui.update_status(localip, "Lướt Tiktok trước khi chạy job thất bại")
            
        countJob = 0
        maxJobDone = 400

        failJob = 0
        maxFailJob = 5
        
        jobcache_done = 0
        job_success_paid = 0
        total_xu_them = 0
        
        ui.update_job_progress(localip, jobcache_done, job_success_paid)
        ui.update_xu_them(localip, total_xu_them)
        
        while countJob < maxJobDone:
            ui.update_status(localip, "Đang lấy job...")
            jobs_response = ttc.getJobCmtTikTok()
            
            # Kiểm tra cấu trúc response
            if not isinstance(jobs_response, dict):
                ui.update_status(localip, "Lỗi: Response không hợp lệ")
                time.sleep(10)
                continue
            
            jobs = jobs_response.get("jobs", [])
            if len(jobs) == 0:
                ui.update_status(localip, "Không có job, đợi 10s...")
                time.sleep(10)
                continue
            
            for job in jobs:
                if countJob >= maxJobDone:
                    print(f"[{localip}] Đã làm đủ job")
                    ui.update_status(localip, "Đã làm đủ job")
                    return
                
                print(f"[{localip}] idjob: {job.get('idpost')}")
                print(f"[{localip}] Link: {job.get('link')}")
                print(f"[{localip}] Nội dung: {job.get('nd_first')}")
                
                ui.update_status(localip, "Tạo job trên server...")
                serverJob.deleteJob(localip=ip)
                time.sleep(1)
                if not serverJob.createJob(localip=ip):
                    print(f"[{localip}] Không thể tạo job trên server")
                    ui.update_status(localip, "Lỗi: Không tạo được job")
                    continue
                
                ui.update_status(localip, "Gửi job đến auto touch...")
                autoTouch.post_lua_payload(localip, message=messageSource.comment(job["link"], job["nd_first"]), name_file="test.lua")
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

                if jobdone:
                    jobcache_done += 1
                    ui.update_job_progress(localip, jobcache_done, job_success_paid)
                
                ui.update_status(localip, f"Job {job['idpost']} đã done, lưu vào file chờ nhận xu...")
                print("======================================")
                WaitGetXuManager.add_job(job["idpost"], ip)
                time.sleep(15)
                
                ui.update_status(localip, "Kiểm tra các job đã đủ thời gian chờ...")
                countJob, failJob, xu_them_received = WaitGetXuManager.process_ready_jobs(ttc, ip, failJob, maxFailJob, countJob, maxJobDone, min_wait_seconds=180)
                
                # Cập nhật số xu thêm và số job đã hoàn thành
                if xu_them_received > 0:
                    total_xu_them += xu_them_received
                    job_success_paid += xu_them_received  # Số job thành công = số xu nhận được (mỗi job = 1 xu)
                    ui.update_job_progress(localip, jobcache_done, job_success_paid)
                    ui.update_xu_them(localip, total_xu_them)
                    print(f"[{localip}] 📊 Tổng xu thêm: {total_xu_them}, Job thành công: {job_success_paid}")

                if countJob >= maxJobDone or failJob >= maxFailJob:
                    if countJob >= maxJobDone:
                        print(f"\n✅ Đã hoàn thành đủ {maxJobDone} job(s), dừng chương trình!")
                        ui.update_status(localip, f"Đã hoàn thành đủ {maxJobDone} job")
                    elif failJob >= maxFailJob:
                        print("Acc nhả mẹ rồi, stop")
                        ui.update_status(localip, f"Đã fail {maxFailJob} job, dừng")
                    return  # Return khỏi hàm để dừng hoàn toàn

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
