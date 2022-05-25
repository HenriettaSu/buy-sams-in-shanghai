# buy-sams-in-shanghai 1.0.1

離我上次離開小區已經2個月了，為了給mi preciosa買到榴槤千層，連續一個星期11點開始蹲山姆套餐蹲，浪費了我至少10個小時，最後還特麼沒買到

我生氣了，於是就有了這個腳本

已通過本腳本買了大半個月的山姆，買到了兩萬多塊的物資，養活了整棟樓的人，放心可用

## 腳本流程

本腳本主要完成了以下流程

1. 獲取商店信息及配送信息
2. 獲取本日套餐 -> 加入購物車（如果是套餐的話）
3. 獲取購物車
4. 下單預檢查
5. 獲取待支付信息
6. 獲取配送時間
7. 下單

**當聽到提示音樂響起，你可以到app上支付了**

## 環境及工具

python3

Charles

## 前置步驟

在運行之前，你需要先從**微信小程序中抓包**出你的山姆帳號uid、收貨地址和坐標

抓包教程網上有很多，這裡不作介紹

## 運行

```shell
python3 sams.py
```

## 配置項

```
COLLECT_LIST = ['鲜食'] # 想買的套餐名稱，模糊匹配
authToken = ''
uid = '' # 山姆帳號uid（String）
addressId = "" # 收貨地址（String）
latitude = 29 # 坐標（Number）
longitude = 29 # 坐標（Number）
```

## 執行方法

主要需要執行的方法有四個

### 等待極速達開店

`waitForArrivedInToday(date, startTime)`

執行本代碼，程序將sleep到指定時間再開始刷購物車

入參：

`date[String]`：開店日。今天 `today` 或明天 `tomorrow`

`startTime[String]`：具體開店時間，時分秒。默認 `08:00:00`

### 初始化配置

 `initConfig(type, loop)` 

入參：

`type[String]`：購買類型。極速達為`arrivedInToday`，全城送為`arrivedInNextDay`，默認為 `arrivedInNextDay`

`loop [Boolean]`：下單成功後是否繼續檢查購物車。默認 `False`

返回：

 `config`

### 獲取購物車

`getUserCart()`

### 獲取本日套餐

`getPageData()`

## 使用方法

本腳本支持三種場景：

1. 極速達
2. 全城送
3. 套餐全城送


### 極速達

```python
waitForArrivedInToday('today', '08:00:00') # 已經開店的話可以註釋本行
config = initConfig('arrivedInToday', True)
getUserCart()
```

### 全城送

```python
config = initConfig('arrivedInNextDay', False)
getUserCart()
```

### 套餐全城送

```python
config = initConfig('arrivedInNextDay', False)
getPageData()
```

## 更新日誌

v 1.0.1

- 修復帳號獲取失敗問題，增加更多必須修改的配置，並單獨抽出 `userInfo.py`；
- 修復查詢購物車時，storeList被固定寫死的問題；

## 聯繫與討論

QQ：3088680950

如果發現八阿哥了或者有功能上的建議，推薦通過 `issue` 發起討論。

~~我已經幾年沒上QQ了（~~

## License

[MIT license](https://opensource.org/licenses/MIT). 有好的想法歡迎提供。
