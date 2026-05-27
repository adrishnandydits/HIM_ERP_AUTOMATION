from pages.send_login_credentials_page import SendLoginCredentialsPage

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
SEND_LOGIN_CREDENTIALS_URL = "https://devanttest.in/him_test/#/student-information/send-login-credentials"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

COURSE = "BBA (Hospital Management)"
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


def verify_send_login_credentials_page(driver):
    page_text = " ".join(
        driver.find_element(By.XPATH, "//body").text.lower().split()
    )

    assert "send login credentials" in page_text, (
        "Send Login Credentials page heading was not found."
    )

    assert "select course" in page_text, (
        "Select Course field was not found on Send Login Credentials page."
    )

    assert "select semester" in page_text, (
        "Select Semester field was not found on Send Login Credentials page."
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


def wait_for_student_list_or_validation(driver, timeout=25):
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
                    f"Validation error found after search: {visible_errors}"
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
                    f"No student data found after search. Message shown: {visible_no_data}"
                )

            rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

            for row in rows:
                try:
                    if row.is_displayed() and row.text.strip():
                        return True
                except StaleElementReferenceException:
                    continue

        except StaleElementReferenceException:
            pass

        time.sleep(1)

    raise AssertionError(
        "Student list was not loaded after clicking Search. "
        "No stable table row appeared for selected Course and Semester."
    )


def verify_table_headers(driver):
    header_text = " ".join(
        driver.find_element(By.XPATH, "//table//thead").text.lower().split()
    )

    expected_headers = [
        "name",
        "gender",
        "date of birth",
        "email",
        "send"
    ]

    for header in expected_headers:
        assert header in header_text, (
            f"Expected Send Login Credentials table header not found: {header}. "
            f"Actual header text: {header_text}"
        )

    return True


def verify_first_row_has_send_button(driver, timeout=25):
    end_time = time.time() + timeout

    while time.time() < end_time:
        try:
            rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

            for row in rows:
                if not row.is_displayed() or not row.text.strip():
                    continue

                send_buttons = row.find_elements(
                    By.XPATH,
                    ".//button[contains(normalize-space(),'Send')]"
                )

                if len(send_buttons) > 0 and send_buttons[0].is_displayed():
                    return True

        except StaleElementReferenceException:
            pass

        time.sleep(1)

    raise AssertionError("Send button was not found in a stable student row.")


def verify_send_confirmation_popup(driver):
    popup_text = " ".join(
        driver.find_element(By.XPATH, "//body").text.lower().split()
    )

    assert "send credentials" in popup_text, (
        "Send Credentials confirmation popup was not found."
    )

    assert "new password will be generated and sent" in popup_text, (
        "Send Credentials confirmation message was not found."
    )

    return True


def verify_mail_sent_success(driver):
    success_messages = driver.find_elements(
        By.XPATH,
        "//*[contains(normalize-space(),'Mail Sent') or contains(normalize-space(),'mail sent')]"
    )

    visible_success = []

    for message in success_messages:
        try:
            if message.is_displayed() and message.text.strip():
                visible_success.append(message.text.strip())
        except StaleElementReferenceException:
            continue

    assert len(visible_success) > 0, (
        "Mail Sent success message was not visible after confirming send credentials."
    )

    return True


def verify_still_on_send_login_credentials_page(driver):
    current_url = driver.current_url.lower()

    assert "send-login-credentials" in current_url, (
        f"Page redirected unexpectedly. "
        f"Expected to stay on Send Login Credentials page. "
        f"Actual URL: {driver.current_url}"
    )

    page_text = " ".join(
        driver.find_element(By.XPATH, "//body").text.lower().split()
    )

    assert "send login credentials" in page_text, (
        "After sending mail, Send Login Credentials page content was not found."
    )

    return True


def fill_send_login_credentials_filter(page):
    selected_course = page.select_course()
    selected_semester = page.select_semester()

    return selected_course, selected_semester


def test_send_login_credentials_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = SendLoginCredentialsPage(driver)

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

        driver.get(SEND_LOGIN_CREDENTIALS_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "send-login-credentials" in driver.current_url.lower()

        add_step(steps, driver, "Open Send Login Credentials Page")

        verify_send_login_credentials_page(driver)
        add_step(steps, driver, "Verify Send Login Credentials Page")

        SELECTED_COURSE, SELECTED_SEMESTER = fill_send_login_credentials_filter(page)
        add_step(steps, driver, "Fill Send Login Credentials Filter")

        verify_selected_values(
            driver,
            SELECTED_COURSE,
            SELECTED_SEMESTER
        )
        add_step(steps, driver, "Verify Selected Course And Semester")

        page.click_search()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Search Button")

        verify_no_validation_error(driver)

        wait_for_student_list_or_validation(driver, timeout=25)
        add_step(steps, driver, "Load Student Login Credentials List")

        verify_table_headers(driver)
        add_step(steps, driver, "Verify Send Login Credentials Table Headers")

        first_student_row_text = page.get_first_student_row_text()
        add_step(
            steps,
            driver,
            "Verify First Student Row",
            "PASS",
            reason=f"First row found: {first_student_row_text}"
        )

        verify_first_row_has_send_button(driver)
        add_step(steps, driver, "Verify Send Button In First Row")

        page.click_send_for_first_row()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Send Button For First Student")

        page.wait_for_send_confirmation_popup()
        verify_send_confirmation_popup(driver)
        add_step(steps, driver, "Verify Send Credentials Confirmation Popup")

        page.confirm_send()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Confirm Send Credentials")

        # page.wait_for_mail_sent_popup(timeout=30)
        # verify_mail_sent_success(driver)
        # add_step(steps, driver, "Verify Mail Sent Success Message")
        success_message = page.wait_for_mail_sent_popup(timeout=30)

        add_step(
            steps,
            driver,
            "Verify Mail Sent Success Message",
            "PASS",
            reason=f"Success message: {success_message}"
        )

        verify_still_on_send_login_credentials_page(driver)
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
        create_pdf_report("Send_Login_Credentials_Test_Report", steps)