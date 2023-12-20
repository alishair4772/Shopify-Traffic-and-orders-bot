import datetime
import zipfile
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import names
import random_address
from selenium.webdriver.support.ui import Select
import random
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import os



class ShopifyBot():

    def useragent_rotate(self):
        with open("userAgents.txt", "r") as f:
            lines = f.readlines()

            return random.choice(lines)

    def proxy_rotate(self,file):
        with open(file, "r") as f:
            lines = f.readlines()
            line = random.choice(lines)
            splitedLine = line.split(':')
            output = {
                'address': splitedLine[0],
                'port': splitedLine[1],
                'user': splitedLine[2],
                'pass': splitedLine[3].replace('\n', '')
            }
            return output



    def manifest_json(self):
        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """
        return manifest_json

    def background_js(self,file):
        proxy = self.proxy_rotate(file=file)
        PROXY_HOST = proxy['address']
        PROXY_PORT = proxy['port']
        PROXY_USER = proxy['user']
        PROXY_PASS = proxy['pass']
        background_js = """
        var config = {
                mode: "fixed_servers",
                rules: {
                  singleProxy: {
                    scheme: "http",
                    host: "%s",
                    port: parseInt(%s)
                  },
                  bypassList: ["localhost"]
                }
              };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """ % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)
        return background_js


    def get_chromedriver(self, use_proxy, user_agent, headless,file):

        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        #chrome_options.add_argument('--disable-gpu')

        if use_proxy:
            pluginfile = 'proxy_auth_plugin.zip'

            with zipfile.ZipFile(pluginfile, 'w') as zp:
                zp.writestr("manifest.json", self.manifest_json())
                zp.writestr("background.js", self.background_js(file=file))
            chrome_options.add_extension(pluginfile)
        if user_agent:
            chrome_options.add_argument('--user-agent=%s' % self.useragent_rotate())
        if headless:
            chrome_options.add_argument('---headless')

        driver = webdriver.Chrome(options=chrome_options)

        return driver

    def formData(self):

        first_name = names.get_first_name()
        last_name = names.get_first_name()
        domains = ['gmail.com', 'yahoo.com', 'aol.com', 'mail.com', 'protonmail.com', 'zoho.com']
        number = random.randint(0, 100)
        email = f"{first_name}{last_name}{number}@{random.choice(domains)}"
        addressDict = random_address.real_random_address()
        address = addressDict['address1']
        city = addressDict['city']
        state = addressDict['state']
        postalCode = addressDict['postalCode']

        txt = open('areacodes')
        a = txt.readlines()
        areacodes = []
        states = []
        for i in a:
            striped = i.strip()
            split = striped.split(" ")
            areacodes.append(split[0])
            states.append(split[1])
        dictionary = dict(zip(states, areacodes))
        ph_no = []
        areaCode = dictionary[f'{state}']
        ph_no.append(areaCode)
        for i in range(1, 8):
            ph_no.append(str(random.randint(0, 9)))
        s = " ".join(ph_no)
        phoneNumber = s.replace(" ", '')
        output = {'firstName': first_name, 'lastName': last_name, 'email': email, 'address': address, 'city': city,
                  'state': state, 'postalCode': postalCode, 'phoneNumber': phoneNumber}

        return output


    def launchChrome(self,use_proxy,user_agent,headless,file):
        print(f"{datetime.datetime.now()} : LAUNCHING CHROME")
        self.driver = self.get_chromedriver(use_proxy=use_proxy, user_agent=user_agent, headless=headless,file=file)
        self.driver.maximize_window()



    def getProductPage(self,productUrl,avgStay):
        print(f"{datetime.datetime.now()} : GETTING PRODUCT PAGE")
        try:
            self.driver.get(productUrl)
            time.sleep(avgStay)
            return True
        except:
            with open('failed.txt','a') as f:
                f.write("failed\n")
            return False

    def addToCart(self,quantity):
        print(f"{datetime.datetime.now()} : ADDING TO CART")
        try:
            addToCart = WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,"//span[contains(text(),'Add to cart')]")))
            self.driver.execute_script("arguments[0].click();", addToCart)
            quantitySelector = WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,'//div[@class="QuantitySelector"]/input')))
            quantitySelector.click()
            time.sleep(0.5)
            quantitySelector.send_keys(Keys.CONTROL + "a")
            quantitySelector.send_keys(Keys.DELETE)
            quantitySelector.clear()
            time.sleep(0.5)
            quantitySelector.send_keys(quantity)
            return True
        except:
            return False

    def checkout(self):
        print(f"{datetime.datetime.now()} : CHECKING OUT")
        try:
            checkoutButton = WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,"//span[contains(text(),'Checkout')]")))
            self.driver.execute_script("arguments[0].click();", checkoutButton)
            continueShipping = WebDriverWait(self.driver,60).until(EC.presence_of_element_located((By.XPATH,"//span[contains(text(),'Continue to shipping')]")))
            time.sleep(3)
            data = self.formData()
            try:
                email = WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Email"]')))
                email.send_keys(data['email'])
            except:
                email = WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Email or mobile phone number"]')))
                email.send_keys(data['email'])
            try:
                WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, '//select[@placeholder="Country/region"]')))
                sel = Select(self.driver.find_element(By.XPATH, '//select[@placeholder="Country/region"]'))
                sel.select_by_value('United States')
                time.sleep(1)
            except:
                WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, '//select[@autocomplete="shipping country"]')))
                sel = Select(self.driver.find_element(By.XPATH, '//select[@autocomplete="shipping country"]'))
                sel.select_by_value('United States')
                time.sleep(1)
            WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="First name"]')))
            firstName = self.driver.find_element(By.XPATH, '//input[@placeholder="First name"]')
            firstName.send_keys(data['firstName'])
            time.sleep(0.5)
            lastName = self.driver.find_element(By.XPATH, '//input[@placeholder="Last name"]')
            lastName.send_keys(data['lastName'])
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="Address"]')))
            address = self.driver.find_element(By.XPATH, '//input[@placeholder="Address"]')
            address.send_keys(data['address'])
            time.sleep(0.5)
            city = self.driver.find_element(By.XPATH, '//input[@placeholder="City"]')
            city.send_keys(data['city'])

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//select[@autocomplete="shipping address-level1"]')))

            sel = Select(self.driver.find_element(By.XPATH, '//select[@autocomplete="shipping address-level1"]'))
            sel.select_by_value(data['state'])
            time.sleep(2)
            # WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="ZIP code"]')))

            try:
                postalCode = self.driver.find_element(By.XPATH, '//input[@placeholder="ZIP code"]')
                postalCode.send_keys(data['postalCode'])
            except:
                postalCode = self.driver.find_element(By.XPATH, '//input[@placeholder="Postal code"]')
                postalCode.send_keys(data['postalCode'])
            try:
                phone = self.driver.find_element(By.XPATH, '//input[@placeholder="Phone"]')
                phone.send_keys(data['phoneNumber'])
            except:
                pass
            time.sleep(1)
            continueShipping = self.driver.find_element(By.XPATH, "//span[contains(text(),'Continue to shipping')]")
            self.driver.execute_script("arguments[0].click();", continueShipping)
            continuePayment = WebDriverWait(self.driver, 40).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Continue to payment')]")))
            return True
        except:
            return False

    def placeOrder(self):
        try:
            continuePayment = WebDriverWait(self.driver, 40).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Continue to payment')]")))
            print(f"{datetime.datetime.now()} : PLACING ORDER")
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", continuePayment)

            checkboxes_element = self.driver.find_elements(By.XPATH, '//input[@type="radio"]')
            checkboxes = len(checkboxes_element)
            while checkboxes <= 1:
                checkboxes_element = self.driver.find_elements(By.XPATH, '//input[@type="radio"]')
                checkboxes = len(checkboxes_element)
            time.sleep(2)
            WebDriverWait(self.driver,10).until(EC.presence_of_all_elements_located((By.XPATH,'//input[@type="radio"]')))
            selectBank = self.driver.find_element(By.XPATH, '(//input[@type="radio"])[3]')
            self.driver.execute_script("arguments[0].click();", selectBank)

            time.sleep(2)
            try:
                payNow = self.driver.find_element(By.XPATH, "//span[contains(text(),'Pay now')]")
                self.driver.execute_script("arguments[0].click();", payNow)

            except:
                completeOrder = self.driver.find_element(By.XPATH, "//span[contains(text(),'Complete order')]")
                self.driver.execute_script("arguments[0].click();", completeOrder)
            time.sleep(15)
            return True
        except:
            return False
    def quitBrowser(self):
        print(f"{datetime.datetime.now()} : QUITING BROWSER")
        self.driver.quit()
    def getUrl(self,url):
        self.driver.get(url)
    def deleteZip(self):
        os.remove("proxy_auth_plugin.zip")
