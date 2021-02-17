import bs4
import sys
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
from discord_webhook import DiscordWebhook
from discord_webhook import DiscordEmbed

# Newegg credentials 
username = 'username'  # enter your username here
password = 'Password'  # enter your password here
cvv = '123'

# Product Page
url = 'https://www.newegg.com/p/N82E16812987020?Item=N82E16812987020&Description=wire&cm_re=wire-_-12-987-020-_-Product&quicklink=true' # insert your URL here. Default some cables


def time_sleep(x, driver):
    for i in range(x, -1, -1):
        sys.stdout.write('\r')
        sys.stdout.write('{:2d} seconds'.format(i))
        sys.stdout.flush()
        time.sleep(1)
    driver.execute_script('window.localStorage.clear();')
    driver.refresh()
    sys.stdout.write('\r')
    sys.stdout.write('Page refreshed\n')
    sys.stdout.flush()


def create_driver():
    """Creating driver."""
    options = Options()
    options.headless = False  # Change To False if you want to see Firefox Browser Again.
    profile = webdriver.FirefoxProfile(r'C:\Users\Root-Directory\AppData\Roaming\Mozilla\Firefox\Profiles\version')  # enter your FirefoxProdile by typing about:profiles are copying and pasting your root directory
    driver = webdriver.Firefox(profile, options=options, executable_path=GeckoDriverManager().install())
    return driver


def driver_wait(driver, find_type, selector):
    """Driver Wait Settings."""
    while True:
        if find_type == 'css':
            try:
                driver.find_element_by_css_selector(selector).click()
                break
            except NoSuchElementException:
                driver.implicitly_wait(0.5)
        elif find_type == 'name':
            try:
                driver.find_element_by_name(selector).click()
                break
            except NoSuchElementException:
                driver.implicitly_wait(0.5)


def finding_cards(driver):
    """Scanning all cards."""
    print("That piece of red text above is not an error. Not sure why they would use that color.")
    print("If you keep seeing page refreshed, the bot is working.")
    print("Goodluck!")
    # time.sleep(1)
    driver.get(url)
    while True:
        html = driver.page_source
        soup = bs4.BeautifulSoup(html, 'html.parser')
        wait = WebDriverWait(driver, 5)

        try:
            find_all_cards = soup.find('button', {'class': 'btn btn-primary btn-wide'})
            if find_all_cards:
                print(f'Button Found!: {find_all_cards.get_text()}')
                time.sleep(1)

                # Clicking Add to Cart.
                driver.find_element_by_xpath("//*[@class='btn btn-primary btn-wide']").click()
                # time.sleep(2)

                # Going To Cart.
                driver.get('https://secure.newegg.com/shop/cart')

                # Checking if item already sold out after clicking to cart.
                try:
                    out_of_stock = driver.find_element_by_xpath("//*[@class='btn btn-secondary']").is_enabled()
                    if out_of_stock:
                        driver.find_element_by_xpath("//*[@class='btn btn-secondary']").click()
                        print("Item Is Not In Cart Anymore. Retrying..")
                        time_sleep(1, driver)
                        driver.get(url)
                        time_sleep(2, driver)
                        finding_cards(driver)
                        return
                    if not out_of_stock:
                        pass
                except (TimeoutException, NoSuchElementException, ElementNotInteractableException):
                    pass

                    
                try:
                    available = driver.find_element_by_xpath("//*[@class='btn btn-primary btn-wide']").is_enabled()
                    if available:
                        driver.find_element_by_xpath("//*[@class='btn btn-primary btn-wide']").click()
                        print("Clicked Checkout Button in Cart.")
                        
                        # Discord Webhook test

                        webhook = DiscordWebhook(url='') # enter your discord webhook here
                        embed = DiscordEmbed(title= "Congrats, Check your email", description='You got it!', color=242424)
                        embed.set_timestamp()
                        webhook.add_embed(embed)

                        response = webhook.execute()
                    if not available:
                        print("Item Is Not In Cart Anymore. Retrying..")
                        time_sleep(1, driver)
                        driver.get(url)
                        time_sleep(2, driver)
                        finding_cards(driver)
                        return
                except (TimeoutException, NoSuchElementException):
                    print("Item Is Not In Cart Anymore. Retrying..")
                    driver.get(url)
                    time_sleep(3, driver)
                    finding_cards(driver)
                    return

                # sign in screen - Happens everytime u load firefox after computer shutoffs
                try:
                    login = driver.find_element_by_xpath("//*[@class='btn btn-orange']").is_enabled()
                    if login:
                        print('yes')
                    if not login: 
                        print('Cant find button')
                except (TimeoutException):
                    print("Item Is Not working. Retrying..")
                    return

                # Logging Into Account.
                try:
                    print("Attempting Sign-In.")
                    wait.until(ec.visibility_of_element_located((By.ID, "labeled-input-password")))
                    password_field = driver.find_element_by_id("labeled-input-password")
                    time.sleep(1)
                    password_field.send_keys(password)
                    password_field.send_keys(Keys.ENTER)
                except (NoSuchElementException, TimeoutException):
                    print("Could Not Login To Account With Password.")
                
                # Clicking Continue to Payment Button  
                try:
                    payment = driver.find_element_by_xpath("//*[@class='btn btn-primary checkout-step-action-done layout-quarter']").is_enabled()
                    if payment: 
                        button = driver.find_elements_by_css_selector(".layout-quarter")
                        for value in button:
                            if value.text == 'CONTINUE TO PAYMENT':
                                value.click()
                        print("Clicked Continue to Payment Button")
                    if not payment:
                        print("Item Is Not the continue to payment button")
                        time_sleep(1, driver)
                        driver.get(url)
                        time_sleep(2, driver)
                        finding_cards(driver)
                        return
                except (TimeoutException):
                    pass

                # Submit CVV Code(Must type CVV number.
                try:
                    print("Trying Credit Card CVV Number.")
                    wait.until(ec.visibility_of_element_located(
                        (By.XPATH, "//input[@class='form-text mask-cvv-4'][@type='text']")))
                    security_code = driver.find_element_by_xpath("//input[@class='form-text mask-cvv-4'][@type='text']")
                    time.sleep(.5)
                    security_code.send_keys(Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE + Keys.BACK_SPACE + cvv)
                except (AttributeError, NoSuchElementException, TimeoutException, ElementNotInteractableException):
                    print("Could Not Type CVV.")

                # Final Checkout [(use """ """) to test without checking out]
                try:
                    wait.until(ec.visibility_of_element_located((By.XPATH, "//*[@class='btn btn-primary btn-wide']")))
                    driver.find_element_by_xpath("//*[@class='btn btn-primary btn-wide']").click()
                except (NoSuchElementException, TimeoutException, ElementNotInteractableException):
                    print("Could Not proceed with Checkout.")

                # Completed Checkout. (webhook executre here for final product)
                print('Order Placed!')
                try:
                    client.messages.create(to=toNumber, from_=fromNumber, body='ORDER PLACED!')
                    # webhook.execute()
                except (NameError):
                    pass

                for i in range(3):
                    print('\a')
                    time.sleep(1)
                time.sleep(1800)
                driver.quit()
                return

        except NoSuchElementException:
            pass
        time_sleep(5, driver) 


if __name__ == '__main__':
    driver = create_driver()
    finding_cards(driver)