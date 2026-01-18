import requests
import json
import re
import time
import unicodedata
import os
from datetime import datetime
import random
import subprocess


class Proxy:
    def getProxy(apikey):
        api = f"https://api.xoayproxy.com/webservice/statusIP?key={apikey}"
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


    def changeProxy(serverlocal):
        message = f"""
            function findImage(image_path, rx, ry, rz, rt)
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
                    
            appRun("com.liguangming.Shadowrocket")
            usleep(5000000)

            toast("OFF SHADOWROCKET")
            local okClick, x,y = findImage("images/shadow_on.png", 570, 170, 200, 100)






        """
        return message



proxy = Proxy.getProxy("IwucTpoAQae5e5REZojuqivAUSsJKtGS")
print(proxy)
    