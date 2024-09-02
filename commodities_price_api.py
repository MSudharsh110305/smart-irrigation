from flask import Flask, request, jsonify
import json
import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def close_popup(driver):
    """
    Closes any popup that appears on the website.
    """
    try:
        # Check if the popup is present
        popup = driver.find_element(By.CLASS_NAME, 'popup-onload')
        
        # If the popup is present, click on the anchor tag with class 'close'
        close_button = popup.find_element(By.CLASS_NAME, 'close')
        close_button.click()
        
        print("Popup closed")
    except NoSuchElementException:
        print("Popup not found")

def script(state, commodity, market):
    """
    Automates interaction with the website to fetch market data.
    
    Args:
        state (str): The state to select.
        commodity (str): The commodity to select.
        market (str): The market to select.

    Returns:
        list: A list of dictionaries containing market data.
    """
    # URL of the website with the dropdown fields
    initial_url = "https://agmarknet.gov.in/SearchCmmMkt.aspx"

    # Initialize the WebDriver (you may need to specify the path to the ChromeDriver)
    driver = webdriver.Chrome()
    driver.get(initial_url)

    # Close the popup if it exists
    close_popup(driver)

    print("Selecting Commodity")
    dropdown = Select(driver.find_element(By.ID, 'ddlCommodity'))
    dropdown.select_by_visible_text(commodity)

    print("Selecting State")
    dropdown = Select(driver.find_element(By.ID, 'ddlState'))
    dropdown.select_by_visible_text(state)

    print("Setting Date")
    today = datetime.now()
    desired_date = today - timedelta(days=7)
    date_input = driver.find_element(By.ID, "txtDate")
    date_input.clear()
    date_input.send_keys(desired_date.strftime('%d-%b-%Y'))

    print("Submitting Form")
    button = driver.find_element(By.ID, 'btnGo')
    button.click()

    time.sleep(3)  # Wait for the page to load

    print("Selecting Market")
    dropdown = Select(driver.find_element(By.ID, 'ddlMarket'))
    dropdown.select_by_visible_text(market)

    print("Submitting Form Again")
    button = driver.find_element(By.ID, 'btnGo')
    button.click()

    time.sleep(1)  # Wait for the page to load

    driver.implicitly_wait(10)
    # Wait for the table to be present
    table = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'cphBody_GridPriceData'))
    )
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    data_list = []
    # Iterate over each row
    for row in soup.find_all("tr"):
        data_list.append(row.text.replace("\n", "_").replace("  ", "").split("__"))

    jsonList = []
    for i in data_list[4:len(data_list) - 1]:
        d = {}
        d["S.No"] = i[1]
        d["City"] = i[2]
        d["Commodity"] = i[4]
        d["Min Prize"] = i[7]
        d["Max Prize"] = i[8]
        d["Model Prize"] = i[9]
        d["Date"] = i[10]
        jsonList.append(d)

    driver.quit()
    return jsonList

app = Flask(__name__)

@app.route('/', methods=['GET'])
def homePage():
    """
    Home page route that returns a simple message.
    """
    dataSet = {"Page": "Home Page navigate to request page", "Time Stamp": time.time()}
    return jsonify(dataSet)

@app.route('/request', methods=['GET'])
def requestPage():
    """
    Handles requests for market data based on query parameters.

    Query Parameters:
        commodity (str): The commodity to query.
        state (str): The state to query.
        market (str): The market to query.

    Returns:
        JSON: A JSON list of market data or an error message if parameters are missing or an exception occurs.
    """
    commodityQuery = request.args.get('commodity')
    stateQuery = request.args.get('state')
    marketQuery = request.args.get('market')

    if not commodityQuery or not stateQuery or not marketQuery:
        return jsonify({"error": "Missing query parameters"})

    try:
        json_data = json.dumps(script(stateQuery, commodityQuery, marketQuery), indent=4)
        return json_data
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)  # Enable debug mode for development
