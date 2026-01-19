import requests
import json
import re
import time
import unicodedata
import os
from datetime import datetime
import random
import subprocess
from module import *

base_message = f"""

function getMailCode(user, domain)
    local json, curl = require("json"), require("lcurl")
    local function otp(s)
        s = tostring(s or ""):gsub("%s+", "")
        return s:match("%d%d%d%d%d%d%d%d") or s:match("%d%d%d%d%d%d%d") or s:match("%d%d%d%d%d%d") or s:match("%d%d%d%d%d")
    end
    local u, d = tostring(user):match("^([^@]+)@(.+)$"); if u then user, domain = u, domain ~= "" and domain or d end
    for _ = 1, 10 do
        local buf = {{}}
        curl.easy{{
            url = ("https://tinyhost.shop/api/email/%s/%s/?page=1&limit=1"):format(domain, user),
            ssl_verifypeer = false, ssl_verifyhost = false,
            writefunction = function(s) buf[#buf+1] = s; return #s end
        }}:perform():close()
        local ok, data = pcall(json.decode, table.concat(buf))
        local m = ok and data and data.emails and data.emails[1]
        local code = m and (otp(m.subject) or otp(m.text_body) or otp(m.html_body))
        if code then return code end
        if usleep then usleep(5000000) else if sleep then sleep(5) end end
    end
    return nil
end

function findTextAndTap(targets, x1, y1, x2, y2, timeFind)
  timeFind = timeFind or 15
  local startTime = os.time()

  local list = {{}}
  if type(targets) == "table" then
    for _, v in ipairs(targets) do
      list[#list+1] = tostring(v):lower()
    end
  else
    list[1] = tostring(targets):lower()
  end

  toast("🔍 OCR finding: " .. table.concat(list, ", "))

  while (os.time() - startTime) < timeFind do
    local opt = {{
      method = OCR_METHOD.IOS_VISION,
      region = (x1 and y1 and x2 and y2) and {{x1, y1, x2, y2}} or nil,
      languages = {{"en-US"}},
      correct = true,
      timeout = 2,
      debug = false,
    }}

    local r = ocr(opt)
    if type(r) == "table" then
      for _, it in pairs(r) do
        local t = tostring(it.text or ""):lower()

        for _, target in ipairs(list) do
          if t:find(target, 1, true) then
            local tl, br = it.rectangle.topLeft, it.rectangle.bottomRight
            local lx, ly, rx, ry = tl.x, tl.y, br.x, br.y

            local left, right = math.min(lx, rx), math.max(lx, rx)
            local top, bottom = math.min(ly, ry), math.max(ly, ry)

            local x = math.random(math.floor(left + 2), math.floor(right - 2))
            local y = math.random(math.floor(top + 2), math.floor(bottom - 2))

            toast(string.format("✅ Found: %s | Tap (%d,%d)", target, x, y))

            tap(x, y)
            usleep(1500000)

            return true, target
          end
        end
      end
    end

    usleep(200000)
  end

  toast("❌ Not found (timeout): " .. table.concat(list, ", "))
  return false
end


function tapAddCommentWait5s(image_path, rx, ry, rz, rt)
    local startTime = os.time()
    local timeout = 5
    local region = (rx and ry and rz and rt) and {{rx, ry, rz, rt}} or nil

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

function random_first_name1()
    local names = {{
        "nam","trung","kien","vinh","linh","giang","quang","trang","ngoc","binh",
        "tung","minh","lien","trong","truong","hai","hanh","hang","truc","luyen",
        "gung","muong","khuyen","thanh","son","lam","thu","nga","hue","loan",
        "my","thuong","duong","tien","ngan","tam","phong","tinh","hieu","cuong",
        "phuc","dat","khoa","thao","yen","mai","dao","huong","tu","nhi"
    }}

    return names[math.random(1, #names)]
    end

function randomAge()
    return math.random(22, 60)
end

function fill_text_phim_so(chuoi)
    local BASE_W, BASE_H = 1242, 2208
    local TARGET_W, TARGET_H = 750, 1334
    local sx, sy = TARGET_W / BASE_W, TARGET_H / BASE_H

    local function k(x,y)
        return {{ math.floor(x*sx+0.5), math.floor(y*sy+0.5) }}
    end

    local banPhimToaDo = {{
        ["1"]=k(212,1595), ["2"]=k(624,1595), ["3"]=k(1040,1595),
        ["4"]=k(212,1770), ["5"]=k(624,1770), ["6"]=k(1040,1770),
        ["7"]=k(212,1935), ["8"]=k(624,1935), ["9"]=k(1040,1935),
        ["0"]=k(620,2130)
    }}

    chuoi = tostring(chuoi or "")
    for i=1,#chuoi do
        local ch = chuoi:sub(i,i)
        local p = banPhimToaDo[ch]
        if p then
        random_fill_text()
        tap(p[1], p[2])
        random_fill_text()
        end
    end
end

function random_gender()
    local list = {{"male", "female"}}
    return list[math.random(1, #list)]
    end

function random_gmail(a,b,c)
    a=tostring(a or ""):lower():gsub("%s+",""):gsub("[^a-z0-9]","")
    b=tostring(b or ""):lower():gsub("%s+",""):gsub("[^a-z0-9]","")
    c=tostring(c or ""):lower():gsub("%s+",""):gsub("[^a-z0-9]","")

    local letters,digits="",""
    for i=1,4 do letters = letters .. string.char(math.random(97,122)) end
    for i=1,3 do digits  = digits  .. tostring(math.random(0,9)) end

    return a..b..c..letters..digits..'@gmail.com'
    end

function random_tinyhost(a,b,c)
    a=tostring(a or ""):lower():gsub("%s+",""):gsub("[^a-z0-9]","")
    b=tostring(b or ""):lower():gsub("%s+",""):gsub("[^a-z0-9]","")
    c=tostring(c or ""):lower():gsub("%s+",""):gsub("[^a-z0-9]","")

    local letters,digits="",""
    for i=1,4 do letters = letters .. string.char(math.random(97,122)) end
    for i=1,3 do digits  = digits  .. tostring(math.random(0,9)) end

    return a..b..c..letters..digits
    end

function random_password(a,b,c)
    a = tostring(a or "")
    b = tostring(b or "")
    c = tostring(c or "")

    local letters = ""
    for i=1,4 do
        letters = letters .. string.char(math.random(97,122))
    end

    return a .. b .. c .. letters .. "@"
    end

function get_uid_from_cookie(text)
    text = tostring(text or "")
    local uid = text:match("c_user=(%d+)")
    return uid
    end

local function url_encode(s)
    s = tostring(s or "")
    s = s:gsub{("\n", "\r\n")}
    s = s:gsub("([^%w%-_%.~])", function(c)
        return string.format("%%%02X", string.byte(c))
    end)
    return s
end


function swipeDuoiLenTren()
    local times = math.random(1, 2)

    for i = 1, times do
        touchDown(1, 200, 900)
        for y = 900, 300, -30 do
            usleep(8000)
            touchMove(1, 200, y)
        end
        touchUp(1, 200, 300)
        -- Delay ngẫu nhiên 4 đến 6 giây
        usleep(math.random(1000000, 2000000))
    end
end

function fill_text_phim_chu1(chuoi)
    local BASE_W, BASE_H = 1242, 2208
    local TARGET_W, TARGET_H = 750, 1334
    local sx, sy = TARGET_W / BASE_W, TARGET_H / BASE_H

    local function k(x,y)
        return {{ math.floor(x*sx+0.5), math.floor(y*sy+0.5) }}
    end

    local banPhimToaDo = {{
        q=k(65,1625), w=k(185,1625), e=k(305,1625), r=k(425,1625), t=k(545,1625),
        y=k(665,1625), u=k(785,1625), i=k(905,1625), o=k(1025,1625), p=k(1145,1625),

        a=k(130,1795), s=k(250,1795), d=k(370,1795), f=k(490,1795), g=k(610,1795),
        h=k(730,1795), j=k(850,1795), k=k(970,1795), l=k(1090,1795),

        z=k(250,1965), x=k(370,1965), c=k(490,1965), v=k(610,1965),
        b=k(730,1965), n=k(850,1965), m=k(970,1965),

        [" "]=k(680,2130),
        ["!"]=k(78,2131),          -- nút chuyển ABC <-> 123
        ["@"]={{425,1284}},
        ["."]={{547,1284}},

        ["1"]=k(70,1620), ["2"]=k(200,1620), ["3"]=k(330,1620), ["4"]=k(460,1620),
        ["5"]=k(590,1620), ["6"]=k(720,1620), ["7"]=k(850,1620), ["8"]=k(980,1620),
        ["9"]=k(1110,1620), ["0"]=k(1240,1620),

        CAPS=k(80,1960)
    }}

    chuoi = tostring(chuoi or "")

    for i=1,#chuoi do
        local ch = chuoi:sub(i,i)
        local lower = ch:lower()
        local p = banPhimToaDo[lower]
        if p then
        -- nếu là số: bấm ! -> số -> ! (đổi qua 123 rồi đổi về ABC)
        if ch:match("%d") then
            random_fill_text(); tap(banPhimToaDo["!"][1], banPhimToaDo["!"][2])
            random_fill_text(); tap(p[1], p[2])
            random_fill_text(); tap(banPhimToaDo["!"][1], banPhimToaDo["!"][2])

        -- chữ hoa
        elseif ch:match("%u") then
            random_fill_text(); tap(banPhimToaDo.CAPS[1], banPhimToaDo.CAPS[2])
            random_fill_text(); tap(p[1], p[2])
            random_fill_text()

        -- chữ thường/ký tự khác có map
        else
            random_fill_text(); 
            tap(p[1], p[2])
            random_fill_text(); 
        end
    end
end
end

function random_fill_text()
    local time = math.random(100000, 250000)
    usleep(time)
end


"""



class Proxy:
    def getProxy(apikey):
        api = f"https://api.xoayproxy.com/webservice/changeIP?key={apikey}&location=mienbac"
        try:
            response = requests.get(api).json()
            if response['status'] == 'OK':
                proxy = response['data']['ipv4']
                return proxy
            elif response['status'] == 'Chưa đến thời gian đổi IP':
                proxy = response['data']['ipv4']
                return proxy
        except Exception as e:
            print(f"Error fetching proxy: {e}")
            return None

    def regnvrGmail(serverlocal, appName:str):
        proxy = Proxy.getProxy(apikey="BDRuBh3wFxJMndDhsaG60MH9wIIv0tiN")
        ip, port = proxy.split(":")
        message = f"""
        {base_message}

        toast("Stop app Apps Manager", 1)
        appKill("com.tigisoftware.ADManager")
        usleep(2000000)
        toast("Open app Apps Manager", 1)
        appRun("com.tigisoftware.ADManager")
        usleep(5000000)

        local result_search = tapAddCommentWait5s("images/search.png", 85, 245, 200, 90)
        if result_search then
            inputText("Facebook")
        end

        tapAddCommentWait5s("images/fbIcon.png", 11, 150, 120, 120)
        swipeDuoiLenTren()

        findTextAndTap("Wipe", 6, 1107, 170, 110)
        findTextAndTap("Wipe Facebook data")

        toast("Dừng app Shadow Rocket", 0.5)
        appKill("com.liguangming.Shadowrocket")
        usleep(500000)

        toast("Bật app Shadow Rocket", 0.5)
        appRun("com.liguangming.Shadowrocket")
        usleep(5000000)
        toast("OFF PROXY SHADOWROCKET")
        local okClick, x, y = tapAddCommentWait5s("images/shadow_on.png", 570, 170, 200, 100)

        local okClick, x, y = tapAddCommentWait5s("images/info_proxy.png", 625, 670, 80, 80)
        if not okClick then
            return
        end

        local result = findTextAndTap("Port")
        if not result then
            return
        end
        usleep(500000)
        tap(704, 1171)
        usleep(100000)
        tap(704, 1171)
        usleep(100000)

        tap(704, 1171)
        usleep(100000)

        tap(704, 1171)

        usleep(100000)
        tap(704, 1171)

        usleep(100000)
        inputText("{port}")

        local result = findTextAndTap("Save")
        usleep(3000000)

        tapAddCommentWait5s("images/shadow_off.png", 560, 180, 200, 90) 

        toast("Dừng app {appName}", 1)
        appKill("com.facebook.Facebook")
        usleep(2000000)
        toast("Mở app {appName}", 1)
        appRun("com.facebook.Facebook")
        usleep(8000000)


        local result_create = findTextAndTap("Create new account")
        if not result_create then
            findTextAndTap("get started")
        end

        findTextAndTap("Create new account")

        findTextAndTap("First name")
        local firstName1 = random_first_name1()
        local firstName2 = random_first_name1()
        fill_text_phim_chu1(firstName1.." "..firstName2)

        findTextAndTap("Last name")
        local lastName1 = random_first_name1()
        fill_text_phim_chu1(lastName1)
        findTextAndTap("Next")
        
        findTextAndTap("Next")
        findTextAndTap("Next")

        findTextAndTap("Age")
        local age = randomAge()
        fill_text_phim_so(age)
        findTextAndTap("Next")
        usleep(1500000)
        findTextAndTap("OK")
        usleep(1500000)
        local sex = random_gender()
        findTextAndTap(sex)
        findTextAndTap("Next")
        usleep(3000000)
        findTextAndTap("Sign up with email")
        findTextAndTap("Email", 50, 380, 200, 60)
        local gmail = random_gmail(firstName1, firstName2, lastName1)
        log(tostring(gmail))
        fill_text_phim_chu1(gmail)
        findTextAndTap("Next")
        findTextAndTap("Continue creating account", nil, nil, nil, nil, 5)
        local resutl, target= findTextAndTap("Password", 50, 420, 250, 100)
        local password = random_password(firstName1, firstName2, lastName1)
        inputText(password)
        findTextAndTap("Next")

        findTextAndTap("Not now")
        findTextAndTap("I agree")

        local resutl, target= findTextAndTap("Confirmation code", 50, 405, 350, 80, 30)
        if not resutl then
            return
        end

        toast("Lấy cookie lưu account", 1)
        usleep(2000000)
        appKill("com.facebook.Facebook")
        usleep(2000000)
        appRun("com.facebook.Facebook")
        usleep(10000000)

        local text = clipText()
        local uid =  get_uid_from_cookie(text)
        local message = uid.."|"..password.."|"..text
        log(tostring(message))

        local curl = require("lcurl")
        local localip = getLocalIP()

        local url = string.format(
        "http://{serverlocal}:5000/api?action=saveaccount&localip=%s&message=%s",
        url_encode(localip),
        url_encode(message)
        )

        curl.easy{{
        url = url,
        httpheader = {{
            "X-Test-Header1: Header-Data1",
            "X-Test-Header2: Header-Data2",
        }},
        }}:perform():close()

        

        local url1 = string.format(
        "http://{serverlocal}:5000/api?action=updateStatus&localip=%s&message=Jobdone",
        url_encode(localip)
        )

        curl.easy{{
        url = url1,
        httpheader = {{
            "X-Test-Header1: Header-Data1",
            "X-Test-Header2: Header-Data2",
        }},
        }}:perform():close()

        
        """
        return message

    def regnvrGmailVerPhone(serverlocal, appName:str):
        proxy = Proxy.getProxy(apikey="BDRuBh3wFxJMndDhsaG60MH9wIIv0tiN")
        ip, port = proxy.split(":")
        message = f"""
        {base_message}

        toast("Stop app Apps Manager", 1)
        appKill("com.tigisoftware.ADManager")
        usleep(2000000)
        toast("Open app Apps Manager", 1)
        appRun("com.tigisoftware.ADManager")
        usleep(5000000)

        local result_search = tapAddCommentWait5s("images/search.png", 85, 245, 200, 90)
        if result_search then
            inputText("Facebook")
        end

        tapAddCommentWait5s("images/fbIcon.png", 11, 150, 120, 120)
        swipeDuoiLenTren()

        findTextAndTap("Wipe", 6, 1107, 170, 110)
        findTextAndTap("Wipe Facebook data")

        toast("Dừng app Shadow Rocket", 0.5)
        appKill("com.liguangming.Shadowrocket")
        usleep(500000)

        toast("Bật app Shadow Rocket", 0.5)
        appRun("com.liguangming.Shadowrocket")
        usleep(5000000)
        toast("OFF PROXY SHADOWROCKET")
        local okClick, x, y = tapAddCommentWait5s("images/shadow_on.png", 570, 170, 200, 100)

        local okClick, x, y = tapAddCommentWait5s("images/info_proxy.png", 625, 670, 80, 80)
        if not okClick then
            return
        end

        local result = findTextAndTap("Port")
        if not result then
            return
        end
        usleep(500000)
        tap(704, 1171)
        usleep(100000)
        tap(704, 1171)
        usleep(100000)

        tap(704, 1171)
        usleep(100000)

        tap(704, 1171)

        usleep(100000)
        tap(704, 1171)

        usleep(100000)
        inputText("{port}")

        local result = findTextAndTap("Save")
        usleep(3000000)

        tapAddCommentWait5s("images/shadow_off.png", 560, 180, 200, 90) 

        toast("Dừng app {appName}", 1)
        appKill("com.facebook.Facebook")
        usleep(2000000)
        toast("Mở app {appName}", 1)
        appRun("com.facebook.Facebook")
        usleep(8000000)
        findTextAndTap("Create new account")
        findTextAndTap("Create new account")

        findTextAndTap("First name")
        local firstName1 = random_first_name1()
        local firstName2 = random_first_name1()
        fill_text_phim_chu1(firstName1.." "..firstName2)

        findTextAndTap("Last name")
        local lastName1 = random_first_name1()
        fill_text_phim_chu1(lastName1)
        findTextAndTap("Next")
        
        findTextAndTap("Next")
        findTextAndTap("Next")

        findTextAndTap("Age")
        local age = randomAge()
        fill_text_phim_so(age)
        findTextAndTap("Next")
        usleep(1500000)
        findTextAndTap("OK")
        usleep(1500000)
        local sex = random_gender()
        findTextAndTap(sex)
        findTextAndTap("Next")
        usleep(3000000)
        findTextAndTap("Sign up with email")
        findTextAndTap("Email", 50, 380, 200, 60)
        local gmail = random_gmail(firstName1, firstName2, lastName1)
        log(tostring(gmail))
        fill_text_phim_chu1(gmail)
        findTextAndTap("Next")

        local resutl, target= findTextAndTap("Password", 50, 420, 250, 100)
        local password = random_password(firstName1, firstName2, lastName1)
        inputText(password)
        findTextAndTap("Next")

        findTextAndTap("Not now")
        findTextAndTap("I agree")

        local resutl, target= findTextAndTap("Confirmation code", 50, 405, 350, 80, 30)
        if not resutl then
            return
        end

        findTextAndTap("I didn't get the code", 207, 677, 320, 65, 10)
        findTextAndTap("Confirm by mobile number")
        findTextAndTap("Mobile number")

        ## Nhập số điện thoại giả lập ở đây
        local phone_number = "1234567890"
        inputText(phone_number)
        findTextAndTap("Next")

        findTextAndTap("Confirm your mobile number with Whatsapp")
        findTextAndTap("Send code via SMS")

        local code_very = "123456"
        inputText(phone_number)
        findTextAndTap("Next")

        usleep(10000000)
        findTextAndTap("Skip")








        local text = clipText()
        local uid =  get_uid_from_cookie(text)
        local message = uid.."|"..password.."|"..text
        log(tostring(message))

        local curl = require("lcurl")
        local localip = getLocalIP()

        local url = string.format(
        "http://192.168.1.2:5000/api?action=saveaccount&localip=%s&message=%s",
        url_encode(localip),
        url_encode(message)
        )

        curl.easy{{
        url = url,
        httpheader = {{
            "X-Test-Header1: Header-Data1",
            "X-Test-Header2: Header-Data2",
        }},
        }}:perform():close()

        
        """
        return message

    def regverTinyHost(serverlocal, appName:str):
        message = f"""
        {base_message}
        
        

        

        local sex = random_gender()
        findTextAndTap(sex)
        findTextAndTap("Next")
        usleep(3000000)

        findTextAndTap("Sign up with email")
        findTextAndTap("Email", 50, 380, 200, 60)
        local mailTiny = random_tinyhost(firstName1, firstName2, lastName1)

        local mailTinyHost = mailTiny.."@apeleon.net"
        inputText(mailTinyHost)
        findTextAndTap("Next")
        findTextAndTap("Continue creating account")

        local resutl, target= findTextAndTap("Password", 50, 420, 250, 100)
        local password = random_password(firstName1, firstName2, lastName1)
        inputText(password)
        findTextAndTap("Next")

        findTextAndTap("Not now")
        findTextAndTap("I agree", 307, 888, 140, 80)

        local resutl, target= findTextAndTap("Confirmation code", 50, 405, 350, 80, 30)
        if not resutl then
            return
        end

        local code = getMailCode(mailTiny, "apeleon.net")
        inputText(code)
        findTextAndTap("Next")
        usleep(10000000)

        openURL("fb://profile")

        appKill("com.facebook.Facebook")
        usleep(2000000)
        appRun("com.facebook.Facebook")
        usleep(6000000)

        local text = clipText()
        local uid =  get_uid_from_cookie(text)
        local message = uid.."|"..password.."|"..mailTinyHost.."|"..text
        log(tostring(message))

        local curl = require("lcurl")
        local localip = getLocalIP()

        local url = string.format(
        "http://{serverlocal}:5000/api?action=saveaccount&localip=%s&message=%s",
        url_encode(localip),
        url_encode(message)
        )

        curl.easy{{
        url = url,
        httpheader = {{
            "X-Test-Header1: Header-Data1",
            "X-Test-Header2: Header-Data2",
        }},
        }}:perform():close()

        

        local url1 = string.format(
        "http://{serverlocal}:5000/api?action=updateStatus&localip=%s&message=Jobdone",
        url_encode(localip)
        )

        curl.easy{{
        url = url1,
        httpheader = {{
            "X-Test-Header1: Header-Data1",
            "X-Test-Header2: Header-Data2",
        }},
        }}:perform():close()

        
        """
        return message


serverlocal = messageSource.get_ipv4_from_ipconfig()
localip = "192.168.1.40:8080"

# proxy = Proxy.getProxy(apikey="BDRuBh3wFxJMndDhsaG60MH9wIIv0tiN")
# autoTouch.post_lua_payload(localip, message=Proxy.changeProxy(serverlocal, proxy=proxy), name_file="testreg.lua")
# autoTouch.get_playSource(localip, name_file="testreg.lua")

# autoTouch.post_lua_payload(localip, message=Proxy.wipeApp(serverlocal,appName="Facebook"), name_file="testreg.lua")
# autoTouch.get_playSource(localip, name_file="testreg.lua")

# while True:
#     i = 0
#     serverJob.createJob(localip)
#     autoTouch.post_lua_payload(localip, message=Proxy.regverTinyHost(serverlocal, appName="Facebook"), name_file="testreg.lua")
#     autoTouch.get_playSource(localip, name_file="testreg.lua")
#     print("Waiting for job to complete...")
#     statusJob = serverJob.checkStatusJob(localip, max_retry=100, retry_interval=5)
#     if statusJob == "Jobdone":
#         print(f"Job completed successfully. {i+1}")
#         i += 1
#     else:
#         print("Job did not complete in expected time.")

autoTouch.post_lua_payload(localip, message=Proxy.regverTinyHost(serverlocal, appName="Facebook"), name_file="testreg.lua")
autoTouch.get_playSource(localip, name_file="testreg.lua")