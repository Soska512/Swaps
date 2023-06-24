# Swaps

Софт крутит agEUR между сетями CELO и Gnosis. Соответственно, нужно пополнить эти сети на комсу.

УСТАНОВКА И ЗАПУСК:
    Переносите все файлы в папку
    
    1. win+R -> cmd
    2. cd *директорияСкрипта* (Пример: cd C:\Users\user\SWAPS)
    3. pip install -r requirements.txt
    4. python swaps.py

ПЕРЕД ЗАПУСКОМ:
    
    1. CELO покупаете на бирже, а xDAI в гносис можно пополнить через Bungee: https://bungee.exchange/refuel

    2. Покупаете agEUR на панкейке, например, в BSC https://pancakeswap.finance/swap?outputCurrency=0x12f31B73D812C6Bb0d735a218c086d44D5fe5f89 , любое количество, хоть 0.01

    3. Заходите сюда https://app.angle.money/bridges-agEUR и бриджите ваши $agEUR из BSC в сеть Gnosis

    4. В keys.txt вставляете все приватники без пробелов и лишних знаков, 1 строка - 1 ключ

    5. Если Gnosis и CELO пополнены на комиссии, а agEUR куплен, можете запускать софт. В количество прокрутов вы указываете, сколько круток будет делаться на каждый аккаунт. На 1 транзакцию затраты около 0.03$
