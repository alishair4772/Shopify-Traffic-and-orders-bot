from classes import ShopifyBot
import random
import time

def shopifyStores(proxyfile,visits,products,minimumSale,maximumSale,hours):
    quantity = [1, 2, 3, 1, 1]

    li = []

    for i in range(1, visits + 1):
        li.append((i / visits) * 100)

    random.shuffle(li)
    wait_time = 4
    start = time.time()
    PERIOD_OF_TIME = int(hours) * 60 * 60

    for chance in li:
        if time.time() > start + PERIOD_OF_TIME:
            break
        bot = ShopifyBot()
        try:
            bot.launchChrome(use_proxy=True,user_agent=True,headless=False,file=proxyfile)
        except:
            continue
        getProduct = bot.getProductPage(productUrl=random.choice(products.split(",")),avgStay=wait_time)
        if chance < random.uniform(10.0, 12.0):
            if getProduct is True:
                getAddToCart = bot.addToCart(quantity=random.choice(quantity))
                if chance <= random.uniform(7.0,8.0):
                    if getAddToCart is True:
                        getCheckout = bot.checkout()
                        if chance <= random.uniform(minimumSale,maximumSale):
                            if getCheckout is True:
                                bot.placeOrder()

        bot.quitBrowser()

