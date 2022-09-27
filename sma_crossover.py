import pandas as pd
from tabulate import tabulate

df = pd.read_csv('../Data/USD_JPY_15min.csv')


data = df.iloc[::-1].reset_index(drop = True) 
data["open"] = data["open"] * 100
data["high"] = data["high"] * 100
data["low"] = data["low"] * 100
data["close"] = data["close"] * 100

data['MA20'] = data["close"].rolling(window=20).mean()
data['MA100'] = data["close"].rolling(window=100).mean()

print(data)
if(data.iloc[99]["MA20"] > data.iloc[99]["MA100"]):
    startPos = "SELL"
else:
    startPos = "BUY"

profitPIP = 15
stoplossPIP = 15

isTrade = False
tradeType = ''
tradeStartTime = ''
tradeStartValue = ''
tradeEndTime = ''
tradeEndValue = ''
outcome = ''
result = []
plValue = 0

totalpl = 0

for index, row in data.iterrows():
    if index < 100:
        continue

    if index == (len(data.index) - 1):
        break
    
    #Looking for Sell 
    if(startPos == "SELL"):
        if(data.iloc[index-1]["MA20"] < data.iloc[index-1]["MA100"]) and not isTrade:
            isTrade = True
            tradeType = "SELL"
            tradeStartValue = data.iloc[index]["open"]
            tradeStartTime = data.iloc[index]["timestamp"]            
    else:
        if(data.iloc[index-1]["MA20"] > data.iloc[index-1]["MA100"]) and not isTrade:
            isTrade = True
            tradeType = "BUY"
            tradeStartValue = data.iloc[index]["open"]
            tradeStartTime = data.iloc[index]["timestamp"]            

    if(isTrade):
        if(tradeType == "SELL"):
            if(row["MA20"] > row["MA100"]):                
                isTrade = False
                tradeEndTime = row["timestamp"]
                tradeEndValue = row["close"] 
                if(tradeEndValue > tradeStartValue):
                    outcome = "Loss"                   
                else:
                    outcome = "Profit"
                plValue = tradeStartValue - tradeEndValue
                totalpl = totalpl + plValue
                result.append([tradeType, outcome, round(plValue,2), tradeStartTime, tradeStartValue, tradeEndTime, tradeEndValue])
                continue

            if(row["low"] < (tradeStartValue - profitPIP)) and (row["high"] > (tradeStartValue + stoplossPIP)):
                outcome = "Not Sure"
                isTrade = False
                result.append([tradeType, outcome, "", tradeStartTime, "", "", tradeEndValue])
                startPos = "BUY"

            elif(row["low"] < (tradeStartValue - profitPIP)):
                outcome = "Profit"
                isTrade = False
                tradeEndTime = row["timestamp"]
                tradeEndValue = row["low"]
                totalpl = totalpl + profitPIP
                result.append([tradeType, outcome, profitPIP, tradeStartTime, tradeStartValue, tradeEndTime, tradeEndValue])
                startPos = "BUY"

            elif(row["high"] > (tradeStartValue + stoplossPIP)):
                outcome = "Loss"
                isTrade = False
                tradeEndTime = row["timestamp"]
                tradeEndValue = row["high"] 
                totalpl = totalpl - stoplossPIP
                result.append([tradeType, outcome, stoplossPIP*(-1), tradeStartTime, tradeStartValue, tradeEndTime, tradeEndValue])
                startPos = "BUY"

        else:
            if(row["MA20"] < row["MA100"]):                
                isTrade = False
                tradeEndTime = row["timestamp"]
                tradeEndValue = row["close"] 
                if(tradeEndValue > tradeStartValue):
                    outcome = "Profit"                   
                else:
                    outcome = "Loss"
                plValue = tradeEndValue - tradeStartValue
                totalpl = totalpl + plValue
                result.append([tradeType, outcome, round(plValue,2), tradeStartTime, tradeStartValue, tradeEndTime, tradeEndValue])
                continue

            if(row["high"] > (tradeStartValue + profitPIP)) and (row["low"] < (tradeStartValue - stoplossPIP)):
                outcome = "Not Sure"
                isTrade = False
                result.append([tradeType, outcome, "", tradeStartTime, "", "", tradeEndValue])
                startPos = "SELL"

            elif(row["high"] > (tradeStartValue + profitPIP)):
                outcome = "Profit"
                isTrade = False
                tradeEndTime = row["timestamp"]
                tradeEndValue = row["high"]
                totalpl = totalpl + profitPIP
                result.append([tradeType, outcome, profitPIP, tradeStartTime, tradeStartValue, tradeEndTime, tradeEndValue])
                startPos = "SELL"

            elif(row["low"] < (tradeStartValue - stoplossPIP)):
                outcome = "Loss"
                isTrade = False
                tradeEndTime = row["timestamp"]
                tradeEndValue = row["low"]
                totalpl = totalpl - stoplossPIP
                result.append([tradeType, outcome, stoplossPIP*(-1), tradeStartTime, tradeStartValue, tradeEndTime, tradeEndValue])
                startPos = "SELL"

print("--------------------------------")
print("Profit/Loss: $",round(totalpl,2))
print("--------------------------------")
print(tabulate(result, headers=["Direction", "P/L", "P/L Value", "Trade Open Time", "Trade Open Value", "Trade Close Time", "Trade Close Value"]))
