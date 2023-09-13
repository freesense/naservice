from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from urllib3 import ProxyManager
import logging, time, os.path, yaml

with open('./config.yaml', 'rt', encoding='utf8') as f:
    config = yaml.safe_load(f.read())
config = config['noipverify']

def update_stealthjs():
    if os.path.exists(config['stealthjs']):
        filetime = time.gmtime(os.path.getmtime(config['stealthjs']))
        today = time.gmtime()
        if filetime.tm_year==today.tm_year and filetime.tm_mon==today.tm_mon and filetime.tm_mday==today.tm_mday:
            return True
    url = 'https://raw.githubusercontent.com/requireCool/stealth.min.js/main/stealth.min.js'
    proxy = ProxyManager(config['proxy'])
    r = proxy.request('GET', url)
    if (r.status != 200):
        logging.error(f'update_stealthjs failed, status={r.status}.')
        return False
    logging.info(f'{config["stealthjs"]} updated.')
    with open(config['stealthjs'], 'w') as f:
        f.write(r.data.decode('utf8'))
    return True

def main():
    logging.basicConfig(filename=config['logname'], format='%(asctime)s - %(levelname)s: %(message)s', level=eval(config['loglevel'])) 
    logging.info('====================')

    if not update_stealthjs():
        return

    options = Options()
    options.add_argument('--headless')
    browser = webdriver.Edge(options=options)
    with open(config['stealthjs'], 'r') as f:
        js = f.read()

    browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': js})
    browser.get('https://my.noip.com/')
    wait = WebDriverWait(browser, 30)
    button_login = wait.until(EC.presence_of_element_located((By.ID, 'clogs-captcha-button')))
    input_username = browser.find_element(By.ID, 'username')
    input_password = browser.find_element(By.ID, 'password')
    input_username.send_keys(config['user'])
    input_password.send_keys(config['pwd'])
    button_login.click()
    hostname_button = browser.find_element(By.XPATH, "//div[@class='col-md-9']")
    hostname_button.click()
    wait.until(EC.presence_of_element_located((By.LINK_TEXT, config['domain'])))
    button_confirm = browser.find_elements(By.XPATH, "//button[@class='btn btn-labeled btn-success']")
    if len(button_confirm)==0:
        logging.info(f'domain {config["domain"]} is safe.')
    else:
        button_confirm[0].click()
        logging.info(f'domain {config["domain"]} confirmed.')
        time.sleep(10.0)
    browser.close()
    #wait.until(EC.url_contains('baidu.com'))

if __name__ == '__main__':
    main()
