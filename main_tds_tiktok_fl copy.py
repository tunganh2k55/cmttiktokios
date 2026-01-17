from module import *

data = get_acc_safeum()
if not data:
    print("Không có account")
    exit()

localip, access_token, proxy, userTikTok = data.split("|")
ip, _ = localip.split(":")

tds = traodoisub(access_token=access_token, proxy=proxy)

data = tds.set_account(userTikTok)
print(data)


countJob = 0
maxJobDone = 10


while countJob < maxJobDone:
    jobs = tds.getJobFollow()

    if len(jobs) == 0:
        print("Không có job nào! Thử lấy lại sau 10 giây")
        continue

    for job in jobs:
        print("idjob :", job.get("id"))
        print("Link :", job.get("link"))
        
        print("Tiến hành tạo job trên server")
        if not serverJob.createJob(localip=ip):
            print("Không thể tạo job trên server")
            continue

        print("Gửi job đến auto touch")
        autoTouch.post_lua_payload(localip, message=messageSource.follow(job["link"]), name_file="test.lua")
        time.sleep(2)

        print("Tiến hành chạy job trên local ios")
        autoTouch.get_playSource(localip, name_file="test.lua")
        time.sleep(2)

        jobdone = False
        print("Tiến hành kiểm tra job trên server")
        for i in range(10):
            statusJob = serverJob.checkStatusJob(localip=ip)
            if statusJob:
                jobdone = True
                break
            else:
                time.sleep(5)

        if not jobdone:
            print("Job không hoàn thành")
            exit()

        response = tds.sendCache(idJob= job["id"])

        error = response.get("error")
        if error:
            print("Gửi job thất bại: ", error)
            exit()

        msg = response.get("msg")
        if msg == "Thành công":
            print(f"Cache: {response.get('cache')}")
        else:
            # nếu API báo không thành công dù không có error
            print("sendCache trả msg không như kỳ vọng:", msg)
            exit()


        cache = response.get("cache", 0)
        if cache >= 8:
            print("Cache đủ 8 -> tiến hành nhận xu")
            ok = tds.claim_xu()
            if ok:
                print("✅ Nhận xu thành công")
                time.sleep(5)
                print("==================================================")
            else:
                print("❌ Nhận xu thất bại")
                print("==================================================")
        else:
            print(f"Chưa đủ cache ({cache}/8)")
            print("==================================================")