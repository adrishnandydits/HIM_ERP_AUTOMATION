from pages.caution_money_page import CautionMoneyPage

import pytest
import time

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from utils.screenshot import take_screenshot
from utils.pdf_report import create_pdf_report


LOGIN_URL = "https://devanttest.in/him_test/#/auth/login"
CAUTION_MONEY_URL = "https://devanttest.in/him_test/#/student-information/caution-money"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

COURSE = "Bachelor of Optometry"
SEMESTER = "2nd Sem"


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


def verify_caution_money_page(driver):
    page_text = " ".join(
        driver.find_element(By.XPATH, "//body").text.lower().split()
    )

    assert "caution money" in page_text, (
        "Caution Money page heading was not found."
    )

    assert "select course" in page_text, (
        "Select Course field was not found on Caution Money page."
    )

    assert "select semester" in page_text, (
        "Select Semester field was not found on Caution Money page."
    )

    return True


def verify_selected_values(driver, selected_course, selected_semester):
    course_select_element = driver.find_element(
        By.XPATH,
        "//label[contains(normalize-space(),'Select Course')]/following::select[1]"
    )

    semester_select_element = driver.find_element(
        By.XPATH,
        "//label[contains(normalize-space(),'Select Semester')]/following::select[1]"
    )

    selected_course_text = Select(course_select_element).first_selected_option.text.strip()
    selected_semester_text = Select(semester_select_element).first_selected_option.text.strip()

    assert selected_course.lower() in selected_course_text.lower(), (
        f"Selected course mismatch. "
        f"Expected: {selected_course}, Actual: {selected_course_text}"
    )

    assert selected_semester.lower() in selected_semester_text.lower(), (
        f"Selected semester mismatch. "
        f"Expected: {selected_semester}, Actual: {selected_semester_text}"
    )

    return True


def wait_for_caution_money_result_or_validation(driver, timeout=25):
    end_time = time.time() + timeout

    while time.time() < end_time:
        try:
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

            if visible_errors:
                raise AssertionError(
                    f"Validation error found after submit: {visible_errors}"
                )

            no_data_elements = driver.find_elements(
                By.XPATH,
                "//*[contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'no data') "
                "or contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'no record') "
                "or contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'no records') "
                "or contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'not found') "
                "or contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'data not found')]"
            )

            visible_no_data = []

            for element in no_data_elements:
                try:
                    if element.is_displayed() and element.text.strip():
                        visible_no_data.append(element.text.strip())
                except StaleElementReferenceException:
                    continue

            if visible_no_data:
                raise AssertionError(
                    f"No caution money data found after submit. Message shown: {visible_no_data}"
                )

            rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

            for row in rows:
                try:
                    if row.is_displayed() and row.text.strip():
                        return True
                except StaleElementReferenceException:
                    continue

            result_elements = driver.find_elements(
                By.XPATH,
                "//table | //div[contains(translate(normalize-space(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'caution money')]"
            )

            visible_results = []

            for element in result_elements:
                try:
                    if element.is_displayed() and element.text.strip():
                        visible_results.append(element)
                except StaleElementReferenceException:
                    continue

            if len(visible_results) > 0 and len(rows) > 0:
                return True

        except StaleElementReferenceException:
            pass

        time.sleep(1)

    raise AssertionError(
        "Caution Money result was not loaded. "
        "After clicking Submit, no table row or result data appeared."
    )


def verify_result_headers_if_table_available(driver):
    tables = driver.find_elements(By.XPATH, "//table")

    if len(tables) == 0:
        return True

    header_elements = driver.find_elements(By.XPATH, "//table//thead")

    if len(header_elements) == 0:
        return True

    header_text = " ".join(header_elements[0].text.lower().split())

    assert header_text != "", "Caution Money result table header is empty."

    return True


def verify_result_has_data(driver):
    rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

    visible_rows = []

    for row in rows:
        try:
            if row.is_displayed() and row.text.strip():
                visible_rows.append(row)
        except StaleElementReferenceException:
            continue

    assert len(visible_rows) > 0, (
        "Caution Money result table has no visible data rows."
    )

    first_row_text = " ".join(visible_rows[0].text.split())

    assert first_row_text != "", "First Caution Money result row text is empty."

    return first_row_text


def verify_still_on_caution_money_page(driver):
    current_url = driver.current_url.lower()

    assert "caution-money" in current_url, (
        f"Page redirected unexpectedly. "
        f"Expected to stay on Caution Money page. "
        f"Actual URL: {driver.current_url}"
    )

    page_text = " ".join(
        driver.find_element(By.XPATH, "//body").text.lower().split()
    )

    assert "caution money" in page_text, (
        "After submit, Caution Money page content was not found."
    )

    return True


def fill_caution_money_form(page):
    selected_course = page.select_course()
    selected_semester = page.select_semester()

    return selected_course, selected_semester


def test_caution_money_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = CautionMoneyPage(driver)

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

        driver.get(CAUTION_MONEY_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "caution-money" in driver.current_url.lower()

        add_step(steps, driver, "Open Caution Money Page")

        verify_caution_money_page(driver)
        add_step(steps, driver, "Verify Caution Money Page")

        SELECTED_COURSE, SELECTED_SEMESTER = fill_caution_money_form(page)
        add_step(steps, driver, "Fill Caution Money Form")

        verify_selected_values(
            driver,
            SELECTED_COURSE,
            SELECTED_SEMESTER
        )
        add_step(steps, driver, "Verify Selected Course And Semester")

        page.click_submit()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Submit Button")

        verify_no_validation_error(driver)

        wait_for_caution_money_result_or_validation(driver, timeout=25)
        add_step(steps, driver, "Load Caution Money Result")

        verify_result_headers_if_table_available(driver)
        add_step(steps, driver, "Verify Caution Money Result Headers")

        first_row_text = verify_result_has_data(driver)
        add_step(
            steps,
            driver,
            "Verify Caution Money Result Data",
            "PASS",
            reason=f"First row found: {first_row_text}"
        )

        verify_still_on_caution_money_page(driver)
        add_step(steps, driver, "Verify Page Did Not Redirect")

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
        create_pdf_report("Caution_Money_Test_Report", steps)