from pages.collect_fees_page import CollectFeesPage

import pytest
import random
import time

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.screenshot import take_screenshot
from utils.pdf_report import create_pdf_report


LOGIN_URL = "https://devanttest.in/him_test/#/auth/login"
COLLECT_FEES_URL = "https://devanttest.in/him_test/#/fees-collection/collect-fees"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

TRANSACTION_ID = f"TXN{random.randint(100000, 999999)}"
BATCH_NUMBER = f"BATCH{random.randint(1000, 9999)}"

PAYMENT_DATE = "14-05-2026"
RECEIVED_DATE = "14-05-2026"


@pytest.fixture()
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()


def add_step(steps, driver, name, status="PASS", reason=""):
    image_path = ""

    try:
        image_path = take_screenshot(
            driver,
            name.lower().replace(" ", "_")
        )
    except Exception:
        image_path = ""

    steps.append({
        "name": name,
        "status": status,
        "reason": reason,
        "image": image_path
    })


def verify_no_validation_error(driver):
    errors = driver.find_elements(
        By.XPATH,
        "//*[contains(text(),'required') or contains(text(),'Required') or contains(text(),'invalid') or contains(text(),'Invalid')]"
    )

    visible_errors = []

    for error in errors:
        try:
            if error.is_displayed() and error.text.strip():
                visible_errors.append(error.text.strip())
        except StaleElementReferenceException:
            continue

    assert len(visible_errors) == 0, f"Validation error found: {visible_errors}"


def verify_collect_fees_page(driver):
    wait = WebDriverWait(driver, 30)

    wait.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//select[@formcontrolname='course_id']"
            )
        )
    )

    page_text = " ".join(
        driver.find_element(By.XPATH, "//body").text.lower().split()
    )

    assert "select course" in page_text, (
        "Select Course dropdown was not found."
    )

    assert "search" in page_text, (
        "Search button was not found."
    )

    return True


def wait_for_student_result_and_collect_button(driver, timeout=35):
    end_time = time.time() + timeout

    while time.time() < end_time:
        try:
            collect_buttons = driver.find_elements(
                By.XPATH,
                "//*[self::button or self::a][contains(normalize-space(),'Collect Fees')]"
            )

            for collect_button in collect_buttons:
                try:
                    if collect_button.is_displayed():
                        driver.execute_script(
                            "arguments[0].scrollIntoView({block:'center'});",
                            collect_button
                        )
                        return True

                except StaleElementReferenceException:
                    continue
                except Exception:
                    continue

            body_text = " ".join(
                driver.find_element(By.XPATH, "//body").text.lower().split()
            )

            assert "no data" not in body_text, (
                "No data found after searching collect fees."
            )

        except StaleElementReferenceException:
            pass

        time.sleep(1)

    page_text = ""

    try:
        page_text = driver.find_element(By.XPATH, "//body").text
    except Exception:
        page_text = "Unable to read page text."

    raise AssertionError(
        "\nCollect Fees Button Not Found\n"
        "-----------------------------\n"
        "Expected Result : Collect Fees button should be visible after searching course.\n"
        "Actual Result   : Collect Fees button was not found after search.\n\n"
        "Possible Reason :\n"
        "1. Selected course has no payable/unpaid student record.\n"
        "2. Collect Fees button text/class changed in the UI.\n"
        "3. Search result table did not load properly.\n"
        "4. Student fee is already paid, so Collect Fees button is not shown.\n\n"
        f"Actual Page Text:\n{page_text}"
    )


def verify_payment_popup_fields(driver):
    wait = WebDriverWait(driver, 30)

    wait.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//input[@placeholder='Enter Transaction Id']"
            )
        )
    )

    page_text = " ".join(
        driver.find_element(By.XPATH, "//body").text.lower().split()
    )

    assert "payment for" in page_text, (
        "Payment popup/header was not found."
    )

    assert "transaction id" in page_text, (
        "Transaction Id field was not found."
    )

    assert "payment date" in page_text, (
        "Payment Date field was not found."
    )

    assert "received date" in page_text, (
        "Received Date field was not found."
    )

    assert "mode" in page_text, (
        "Payment Mode field was not found."
    )

    assert "bank" in page_text, (
        "Bank field was not found."
    )

    return True


def test_collect_fees_payment_status_paid_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 25)

    try:
        page = CollectFeesPage(driver)

        driver.get(LOGIN_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Open Login Page")

        page.enter_text(page.EMAIL, EMAIL)
        add_step(steps, driver, "Enter Email")

        page.enter_text(page.PASSWORD, PASSWORD)
        add_step(steps, driver, "Enter Password")

        page.click(page.LOGIN_BUTTON)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Login Button")

        driver.get(COLLECT_FEES_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        time.sleep(3)

        assert "collect-fees" in driver.current_url.lower()

        add_step(steps, driver, "Open Collect Fees Page")

        verify_collect_fees_page(driver)
        add_step(steps, driver, "Verify Collect Fees Page")

        SELECTED_COURSE = page.select_course_bba()

        add_step(
            steps,
            driver,
            "Select Course",
            "PASS",
            reason=f"Selected Course: {SELECTED_COURSE}"
        )

        page.click_search()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Search Button")

        page.wait_for_collect_fees_button(timeout=35)
        wait_for_student_result_and_collect_button(driver, timeout=35)
        add_step(steps, driver, "Verify Student Result And Collect Fees Button")

        page.click_collect_fees()
        page.wait_for_collect_fees_popup(timeout=30)
        add_step(steps, driver, "Click Collect Fees Button")

        verify_payment_popup_fields(driver)
        add_step(steps, driver, "Verify Payment Popup Fields")

        page.click_fees_checkbox()
        add_step(steps, driver, "Select Fees Checkbox")

        page.enter_transaction_id(TRANSACTION_ID)
        add_step(
            steps,
            driver,
            "Enter Transaction Id",
            "PASS",
            reason=f"Transaction Id: {TRANSACTION_ID}"
        )

        page.enter_payment_date(PAYMENT_DATE)
        add_step(
            steps,
            driver,
            "Enter Payment Date",
            "PASS",
            reason=f"Payment Date: {PAYMENT_DATE}"
        )

        page.enter_received_date(RECEIVED_DATE)
        add_step(
            steps,
            driver,
            "Enter Received Date",
            "PASS",
            reason=f"Received Date: {RECEIVED_DATE}"
        )

        page.select_payment_mode_cash()
        add_step(steps, driver, "Select Payment Mode UPI")

        page.select_bank_allahabad_bank()
        add_step(steps, driver, "Select Bank Allahabad Bank")

        page.enter_batch_number(BATCH_NUMBER)
        add_step(
            steps,
            driver,
            "Enter Batch Number",
            "PASS",
            reason=f"Batch Number: {BATCH_NUMBER}"
        )

        page.select_beneficiary_bank_state_bank_of_india()
        add_step(steps, driver, "Select Beneficiary Bank Name State Bank Of India")

        page.select_beneficiary_branch_haldia()
        add_step(steps, driver, "Select Beneficiary Branch Name Haldia")

        page.click_calculate_total()
        add_step(steps, driver, "Click Calculate Total")

        verify_no_validation_error(driver)

        page.click_submit()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Submit Button")

        page.wait_for_yes_save_it_popup(timeout=25)
        add_step(steps, driver, "Verify Yes Save It Confirmation Popup")

        page.click_yes_save_it()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        time.sleep(3)
        add_step(steps, driver, "Click Yes Save It Button")

        verify_no_validation_error(driver)

        page.wait_for_paid_status(timeout=35)
        add_step(steps, driver, "Verify Payment Status Changed To Paid")

        #page.click_print_latest_payment()
        #add_step(steps, driver, "Click Print Latest Payment")

        page.verify_payment_status_paid_for_selected_row(timeout=35)
        add_step(steps, driver, "Assert Payment Status Paid")

    except Exception as e:
        error_reason = str(e).strip()

        if not error_reason:
            error_reason = "No detailed error message returned by Selenium."

        error_reason = f"{type(e).__name__}: {error_reason}"

        try:
            add_step(
                steps,
                driver,
                "Test Failed",
                "FAIL",
                reason=error_reason
            )
        except Exception:
            steps.append({
                "name": "Test Failed",
                "status": "FAIL",
                "reason": error_reason,
                "image": ""
            })

        raise e

    finally:
        create_pdf_report("Collect_Fees_Test_Report", steps)