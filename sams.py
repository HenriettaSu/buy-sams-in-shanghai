import requests, json, time, re, os, sys
from datetime import datetime, date, timedelta
from userInfo import *
sys.setrecursionlimit(1000000000)

requests.adapters.DEFAULT_RETRIES = 5
session = requests.session()
session.keep_alive = False

def weekdayFormatter (weekday):
    weekdayList = ['周一', '周二', '周三', '周四', '周五', '周六', '周天']
    return weekdayList[weekday]

def getTomorrow ():
    tomorrow = date.today() + timedelta(days= 1)
    return tomorrow.strftime("%Y/%m/%d") + ' ' + weekdayFormatter(tomorrow.weekday())

def getTimestamp (type = 'today', hour = '09:00:00'):
    if type == 'today':
        theDate = date.today()
    elif type == 'yesterday':
        theDate = date.today() + timedelta(days=-1)
    elif type == 'tomorrow':
        theDate = date.today() + timedelta(days=1)
    timeArray = time.strptime(theDate.strftime("%Y-%m-%d") + ' ' + hour, "%Y-%m-%d %H:%M:%S")
    timeStamp = int(time.mktime(timeArray))
    # print(datetime.fromtimestamp(timeStamp))
    return timeStamp * 1000

arrivedConfigs = {
    'arrivedInNextDay': {
        'storeInfo': {
            "areaBlockId": "1191464773401845014",
            "storeId": "6988",
            "storeType": 2
        },
        'deliveryInfoVO': {
            "storeType": 2,
            "storeDeliveryTemplateId": "1194213985508061974",
            "deliveryModeId": "1003"
        },
        'cartDeliveryType': 2,
        'deliveryType': 2,
        'sceneCode': 1089,
        'expectArrivalTime': getTimestamp('tomorrow', '9:00:00'),
        'expectArrivalEndTime': getTimestamp('tomorrow', '21:00:00'),
        'deliveryName': getTomorrow()
    },
    'arrivedInToday': {
        'storeInfo': {
            "areaBlockId": "1203904505587066134",
            "storeId": "6683",
            "storeType": 4
        },
        'deliveryInfoVO': {
            "storeType": 4,
            "storeDeliveryTemplateId": "1204029271518126870",
            "deliveryModeId": "1009"
        },
        'cartDeliveryType': 1,
        'deliveryType': 1,
        'sceneCode': 1007,
        'expectArrivalTime': getTimestamp('today', '13:00:00'),
        'expectArrivalEndTime': getTimestamp('today', '16:00:00'),
        'deliveryName': date.today().strftime("%Y/%m/%d") + ' ' + weekdayFormatter(datetime.today().weekday())
    }
}

config = {}
storeList = []

# 獲取商店信息
def getMiniUnLoginStoreList (storeType = 4):
    result = None
    data = json.dumps({
        "latitude": latitude,
        "longitude": longitude,
        "requestType": "location_recmd",
        "uid": uid,
        "appId": "wxb344a8513eaaf849",
        "saasId": "1818"
    })
    res = requests.post(url='https://api-sams.walmartmobile.cn/api/v1/sams/merchant/storeApi/getMiniUnLoginStoreList',
                        data=data,
                        headers={'Content-Type': 'application/json', "auth-token":authToken})

    if res:
        res.close()
        json_data = json.loads(res.text)
        if json_data['success'] == True:
            for item in json_data['data']['storeList']:
                storeList.append({
                    "storeType": item['storeType'],
                    "storeId": item['storeId'],
                    "areaBlockId": item['storeAreaBlockVerifyData']['areaBlockId'],
                    "storeDeliveryTemplateId": item['storeRecmdDeliveryTemplateData']['storeDeliveryTemplateId']
                })
                if item['storeType'] == storeType:
                    result = {
                        'areaBlockId': item['storeAreaBlockVerifyData']['areaBlockId'],
                        'storeDeliveryTemplateId': item['storeRecmdDeliveryTemplateData']['storeDeliveryTemplateId']
                    }
            if result == None:
                print('還沒開門')
                time.sleep(0.2)
                return getMiniUnLoginStoreList(storeType)
            else:
                return result
        else:
            time.sleep(0.2)
            return getMiniUnLoginStoreList(storeType)
    else:
        time.sleep(0.2)
        return getMiniUnLoginStoreList(storeType)

def initConfig (type = 'arrivedInNextDay', loop = False):
    con = arrivedConfigs[type]
    con['loop'] = loop
    if type == 'arrivedInToday':
        res = getMiniUnLoginStoreList()
    else:
        res = getMiniUnLoginStoreList(2)
    con['storeInfo']['areaBlockId'] = res['areaBlockId']
    con['deliveryInfoVO']['storeDeliveryTemplateId'] = res['storeDeliveryTemplateId']
    print(con)
    return con

# 提交訂單
def commitPay (resData):
    data = json.dumps({
        "sceneCode": config['sceneCode'],
        "deliveryInfoVO": config['deliveryInfoVO'],
        "storeInfo": config['storeInfo'],
        "channel": "wechat",
        "invoiceInfo": {},
        "isSelectShoppingNotes": True,
        "addressId": addressId,
        "cartDeliveryType": config['cartDeliveryType'],
        "couponList": [],
        "floorId": 1,
        "goodsList": resData['goodsInfo']['goodsList'],
        "amount": int(resData['goodsInfo']['amount']),
        "currency": "CNY",
        "orderType": 0,
        "payMethodId": "contract",
        "payType": 0,
        "remark": "",
        "shortageDesc": "其他商品继续配送（缺货商品直接退款）",
        "shortageId": 1,
        "labelList": "[{\"attachId\":\"1651890336319-2a6ba6f0-24c4-479a-b8df-91ada7beeff3\",\"createTime\":1651897879288,\"labelType\":\"tracking_id\"},{\"attachId\":1089,\"createTime\":1651897879325,\"labelType\":\"scene_xcx\"}]",
        "settleDeliveryInfo": {
            "deliveryType": config['deliveryType'],
            "deliveryDesc": "",
            "deliveryName": config['deliveryName'],
            "expectArrivalTime": config['expectArrivalTime'],
            "expectArrivalEndTime": config['expectArrivalEndTime']
        },
        "uid": uid,
        "appId": "wxb344a8513eaaf849",
        "saasId": "1818"
    })
    res = requests.post(url='https://api-sams.walmartmobile.cn/api/v1/sams/trade/settlement/commitPay',
                        data=data.encode('utf-8'),
                        headers={'Content-Type': 'application/json', 'device-type': 'mini_program',
                                 "auth-token": authToken})

    if res:
        json_data = json.loads(res.text)
        print(res.text)
        if json_data['success'] == True:
            print('下單成功啦！')
            os.system('open 年年.ncm')
            if config['loop'] == True:
                print('再檢查一下購物車！')
                getUserCart()
            else:
                exit()
        elif json_data['success'] == False:
            # 極速達返回重新查購物車，套餐死命支付
            if config['storeInfo']['storeType'] == 4 and json_data['code'] == 'OUT_OF_STOCK':
                print(json_data['msg'])
                getUserCart()
            else:
                time.sleep(0.3)
                commitPay(resData)
        else:
            time.sleep(0.3)
            commitPay(resData)
    else:
        time.sleep(0.3)
        commitPay(resData)

def getCapacityData (resData):
    hasCapacityData = False
    config['storeInfo']['areaBlockId'] = resData['settleDelivery']['areaBlockId']
    config['deliveryInfoVO']['storeDeliveryTemplateId'] = resData['settleDelivery']['storeDeliveryTemplateId']
    data = json.dumps({
        "perDateList": [date.today().strftime("%Y-%m-%d"), (date.today() + timedelta(days=1)).strftime("%Y-%m-%d"), (date.today() + timedelta(days=2)).strftime("%Y-%m-%d"), (date.today() + timedelta(days=3)).strftime("%Y-%m-%d")],
        "storeDeliveryTemplateId": config['deliveryInfoVO']['storeDeliveryTemplateId'],
        "uid": uid,
        "appId": "wxb344a8513eaaf849",
        "saasId": "1818"
    })
    res = requests.post(url='https://api-sams.walmartmobile.cn/api/v1/sams/delivery/portal/getCapacityData',
                        data=data,
                        headers={'Content-Type': 'application/json', 'device-type': 'mini_program',
                                 "auth-token": authToken})

    if res:
        json_data = json.loads(res.text)
        if json_data['success'] == True:
            config['deliveryName'] = json_data['data']['capcityResponseList'][0]['strDate']
            print(config['deliveryName'])
            for item in json_data['data']['capcityResponseList'][0]['list']:
                print(item)
                if item['timeISFull'] is not True:
                    hasCapacityData = True
                    print('獲取到可配送時間')
                    config['expectArrivalTime'] = int(item['startRealTime'])
                    config['expectArrivalEndTime'] = int(item['endRealTime'])
                    print(config['deliveryName'], datetime.fromtimestamp(int(str(config['expectArrivalTime'])[0:10])), datetime.fromtimestamp(int(str(config['expectArrivalEndTime'])[0:10])))
                    commitPay(resData)
                    return
                else:
                    hasCapacityData = False

            if hasCapacityData == False:
                time.sleep(0.4)
                getCapacityData(resData)
        else:
            time.sleep(0.4)
            getCapacityData(resData)
    else:
        time.sleep(0.4)
        getCapacityData(resData)

# 獲取待支付信息
def getSettleInfo (validGoodsList):
    data = json.dumps({
        "couponList":[],
        "deliveryInfoVO": config['deliveryInfoVO'],
        "storeInfo": config['storeInfo'],
        "cartDeliveryType": config['cartDeliveryType'],
        "addressId": addressId,
        "floorId":1,
        "goodsList": validGoodsList,
        "uid": uid,
        "appId":"wxb344a8513eaaf849",
        "saasId":"1818"
    })
    res = requests.post(url='https://api-sams.walmartmobile.cn/api/v1/sams/trade/settlement/getSettleInfo',
                        data=data.encode('utf-8'),
                        headers={'Content-Type': 'application/json', 'device-type': 'mini_program',
                                 "auth-token": authToken})

    for good in validGoodsList:
        print(good['spuId'], good['goodsName'], str(good['quantity']) + '件')
    if res:
        json_data = json.loads(res.text)
        if json_data['success'] == True:
            resData = json_data['data']
            print('獲取待支付信息成功')
            if int(resData['goodsInfo']['amount']) < (99 * 100):
                print('要運費，要不再看看有沒有東西？')
                getUserCart()
            else:
                # 查詢一下配送時間
                getCapacityData(resData)

                # 跳過時間獲取
                # commitPay(resData)
        else:
            time.sleep(0.2)
            getSettleInfo(validGoodsList)

# 下單預檢查
def getPreSettleInfo (goodsList):
    data = json.dumps({
        "storeList":[{"storeType":32,"storeId":"9991","areaBlockId":"42295","storeDeliveryTemplateId":"1010425035346829590"},{"storeType":2,"storeId":"6988","areaBlockId":"1191464773401845014","storeDeliveryTemplateId":"1194213985508061974"},{"storeType":4,"storeId":"6683","areaBlockId":"1203904505587066134","storeDeliveryTemplateId":"1204029271518126870"},{"storeType":8,"storeId":"9996","areaBlockId":"42295","storeDeliveryTemplateId":"1147161263885953814"}],
        "checkValidGoodsVOList":[{
            "floorId":1,
            "goodsList": goodsList,
            "giveawayList":[]
        }],
        "uid": uid,
        "appId":"wxb344a8513eaaf849",
        "saasId":"1818"
    })
    res = requests.post(url='https://api-sams.walmartmobile.cn/api/v1/sams/trade/cart/getPreSettleInfo',
                        data=data,
                        headers={'Content-Type': 'application/json', 'device-type': 'mini_program',
                                 "auth-token": authToken})

    # print(res.text)
    if res:
        json_data = json.loads(res.text)
        if json_data['success'] == True:
            print('下單預檢查成功')
            validGoodsList = json_data['data']['preSettleInfoList'][0]['validGoodsList']
            # print(validGoodsList)
            getSettleInfo(validGoodsList)
        else:
            time.sleep(0.2)
            getPreSettleInfo(goodsList)
    else:
        time.sleep(0.2)
        getPreSettleInfo(goodsList)

# 獲取購物車
def getUserCart ():
    data = json.dumps({
        "storeList": storeList,
        "addressId":"",
        "uid": uid,
        "appId":"wxb344a8513eaaf849",
        "saasId":"1818"
    })
    res = requests.post(url='https://api-sams.walmartmobile.cn/api/v1/sams/trade/cart/getUserCart',
                        data=data,
                        headers={'Content-Type': 'application/json', 'device-type': 'mini_program', "auth-token":authToken})

    if res:
        res.close()
        json_data = json.loads(res.text)
        if json_data['success'] == True:
            goodsList = []
            for item in json_data['data']['miniProgramGoodsInfo']['normalGoodsList']:
                goodsList.append({
                    "isSelected": True,
                    "quantity": item['quantity'],
                    "spuId": item['spuId'],
                    "storeId": item['storeId'],
                    "warrantyExtensionList": item['warrantyExtensionList']
                })
            # print(goodsList)
            if len(goodsList) == 0:
                print('沒貨了，再試一下獲取購物車')
                time.sleep(0.2)
                getUserCart()
            else:
                print('獲取購物車成功')
                getPreSettleInfo(goodsList)
        else:
            print('再試一下獲取購物車')
            time.sleep(0.2)
            getUserCart()

# 加入購物車
def addCartGoodsInfo (spuId, skuName):
    now = round(time.time()*1000)
    data = json.dumps({
        "cartGoodsInfoList":[{
            "spuId": spuId,
            "isSelected": True,
            "storeId":"6988",
            "increaseQuantity":1,
            "labelList":"[{\\\"attachId\\\":\\\"1651627113089-5b946e6f-5ec7-48b0-a15b-59b636f2873c\\\",\\\"createTime\\\":' + str(now) + ',\\\"labelType\\\":\\\"tracking_id\\\"},{\\\"attachId\\\":1007,\\\"createTime\\\":1651627113386,\\\"labelType\\\":\\\"scene_xcx\\\"}]"
        }],
        "uid": uid,
        "appId":"wxb344a8513eaaf849",
        "saasId":"1818"
    })
    res = requests.post(url='https://api-sams.walmartmobile.cn/api/v1/sams/trade/cart/addCartGoodsInfo',
                        data=data,
                        headers={'Content-Type': 'application/json', "auth-token":authToken})

    if res:
        json_data = json.loads(res.text)
        if json_data['success'] == True:
            COLLECT_LIST.remove(skuName)
            print('加购成功啦！')
            getUserCart()
            os.system('open 年年.ncm')
        else:
            print('再试下加购物车')
            time.sleep(0.2)
            addCartGoodsInfo(spuId, skuName)
    else:
        time.sleep(0.2)
        addCartGoodsInfo(spuId, skuName)

# 查詢套餐數據
def getPageData ():
    data = json.dumps({
        "pageContentId":"1187641882302384150",
        "pageNum":1,
        "pageSize":20,
        "latitude": latitude,
        "longitude": longitude,
        "storeInfoList":[
            {"storeId":"9991","storeType":32,"storeDeliveryAttr":[10]},
            {"storeId":"6988","storeType":2,"storeDeliveryAttr":[3,12]},
            {"storeId":"6683","storeType":4,"storeDeliveryAttr":[3,4]},
            {"storeId":"9996","storeType":8,"storeDeliveryAttr":[1]}
        ],
        "uid": uid,
        "appId":"wxb344a8513eaaf849",
        "saasId":"1818"
    })
    res = requests.post(url='https://api-sams.walmartmobile.cn/api/v1/sams/decoration/portal/show/getPageData',
                        data=data,
                        headers={'Content-Type': 'application/json', "auth-token":authToken})

    # print(res)
    if res:
        json_data = json.loads(res.text)
        # print(json_data)
        if json_data['success'] == True:
            pageModuleVOList = json_data['data']['pageModuleVOList']
            for item in pageModuleVOList:
                if 'goodsList' in item['renderContent']:
                    # print(item['renderContent']['goodsList'])
                    for spu in item['renderContent']['goodsList']:
                        # print(spu)
                        skuName = spu['title']
                        # if spu['title'] in COLLECT_LIST:
                        for collect in COLLECT_LIST:
                            if re.findall(collect, spu['title']):
                                spuId = spu['spuId']
                                print(spuId, skuName, spu['stockInfo'])
                                # 有货
                                if spu['stockInfo']['stockQuantity'] != '0':
                                    addCartGoodsInfo(spuId, collect)

        if len(COLLECT_LIST) == 0:
            print('齐活了！')
            # os.system('open 年年.ncm')
            exit()
        else:
            print(str(COLLECT_LIST) + '没货')
            time.sleep(0.2)
            getPageData()
    else:
        print(str(COLLECT_LIST) + '没货')
        time.sleep(0.2)
        getPageData()

def waitForArrivedInToday (date = 'today', startTime = '08:00:00'):
    nowTimestamp = int(round(time.time() * 1000))
    targetTimestamp = getTimestamp(date, startTime)
    leftTime = targetTimestamp - nowTimestamp
    if leftTime > 0:
        print('坐等' + str((leftTime) / 1000 / 60 / 60) + '小時')
        time.sleep((leftTime) / 1000)
    print('開始啦')

waitForArrivedInToday()
config = initConfig('arrivedInToday', True)
getUserCart()

# config = initConfig('arrivedInNextDay', False)
# getPageData()
# getUserCart()
