from pages.hostel_room_page import HostelRoomPage

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
HOSTEL_ROOM_URL = "https://devanttest.in/him_test/#/hostel/addHostelRooms"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

RANDOM_NUMBER = random.randint(1000, 9999)

ROOM_NAME = f"Test Room {RANDOM_NUMBER}"
NO_OF_BED = "3"
COST_PER_BED = "100"
DESCRIPTION = f"Test Description {RANDOM_NUMBER}"

EDIT_ROOM_NAME = f"Updated Room {RANDOM_NUMBER}"
EDIT_NO_OF_BED = "4"
EDIT_COST_PER_BED = "200"
EDIT_DESCRIPTION = f"Updated Description {RANDOM_NUMBER}"


@pytest.fixture()
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()


def add_step(steps, driver, name, status="PASS"):
    steps.append({
        "name": name,
        "status": status,
        "image": take_screenshot(driver, name.lower().replace(" ", "_"))
    })


def verify_no_validation_error(driver):
    errors = driver.find_elements(
        By.XPATH,
        "//*[contains(text(),'required') or contains(text(),'Required')]"
    )

    visible_errors = [
        error.text for error in errors
        if error.is_displayed() and error.text.strip()
    ]

    assert len(visible_errors) == 0, f"Validation error found: {visible_errors}"


def verify_exact_table_row_added(driver, expected_values):
    expected_values = [
        str(value).lower().strip()
        for value in expected_values
    ]

    end_time = time.time() + 30

    while time.time() < end_time:
        rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

        if len(rows) > 0:
            for row in rows:
                row_text = " ".join(row.text.lower().split())

                if all(value in row_text for value in expected_values):
                    return True

        time.sleep(1)

    table_text = driver.find_element(By.XPATH, "//table//tbody").text

    raise AssertionError(
        f"Exact hostel room row not found after waiting 30 seconds. "
        f"Expected values: {expected_values}. "
        f"Actual table text: {table_text}"
    )


def verify_exact_table_row_deleted(driver, deleted_values):
    deleted_values = [
        str(value).lower().strip()
        for value in deleted_values
    ]

    end_time = time.time() + 30
    matching_row_text = ""

    while time.time() < end_time:
        rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

        deleted_row_found = False

        for row in rows:
            row_text = " ".join(row.text.lower().split())

            if all(value in row_text for value in deleted_values):
                deleted_row_found = True
                matching_row_text = row.text
                break

        if not deleted_row_found:
            return True

        time.sleep(1)

    table_text = ""

    try:
        table_text = driver.find_element(By.XPATH, "//table//tbody").text
    except Exception:
        table_text = driver.find_element(By.XPATH, "//body").text

    raise AssertionError(
        "\nHostel Room Delete Verification Failed\n"
        "--------------------------------------\n"
        "Expected Result : Updated hostel room row should be deleted from the table.\n"
        "Actual Result   : Updated hostel room row is still visible after delete confirmation.\n\n"
        f"Deleted Values  : {deleted_values}\n\n"
        "Possible Reason :\n"
        "1. Delete confirmation popup was not clicked successfully.\n"
        "2. Delete API failed in the application.\n"
        "3. Table did not refresh after delete.\n"
        "4. Delete button clicked but record was not removed from database.\n\n"
        f"Still Visible Row:\n{matching_row_text}\n\n"
        f"Actual Table Text:\n{table_text}"
    )


def test_hostel_room_add_edit_delete_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = HostelRoomPage(driver)

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

        driver.get(HOSTEL_ROOM_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "addhostelrooms" in driver.current_url.lower(), (
            f"Hostel Room page did not open. Current URL: {driver.current_url}"
        )

        add_step(steps, driver, "Open Hostel Room Page")

        page.enter_name(ROOM_NAME)
        add_step(steps, driver, "Enter Room Name")

        SELECTED_HOSTEL = page.select_hostel()
        add_step(steps, driver, "Select Hostel")

        SELECTED_ROOM_TYPE = page.select_room_type()
        add_step(steps, driver, "Select Room Type")

        page.enter_no_of_bed(NO_OF_BED)
        add_step(steps, driver, "Enter No Of Bed")

        page.enter_cost_per_bed(COST_PER_BED)
        add_step(steps, driver, "Enter Cost Per Bed")

        page.enter_description(DESCRIPTION)
        add_step(steps, driver, "Enter Description")

        page.click_submit()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Submit Button")

        verify_no_validation_error(driver)

        EXPECTED_ROW_VALUES = [
            ROOM_NAME,
            SELECTED_HOSTEL,
            SELECTED_ROOM_TYPE,
            NO_OF_BED,
            COST_PER_BED
        ]

        verify_exact_table_row_added(
            driver,
            EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Hostel Room Added")

        page.click_edit_for_exact_row(
            EXPECTED_ROW_VALUES
        )
        wait.until(EC.presence_of_element_located(page.UPDATE_BUTTON))
        add_step(steps, driver, "Click Edit Button")

        page.enter_name(EDIT_ROOM_NAME)
        add_step(steps, driver, "Edit Room Name")

        EDIT_SELECTED_HOSTEL = page.select_hostel()
        add_step(steps, driver, "Edit Hostel")

        EDIT_SELECTED_ROOM_TYPE = page.select_room_type()
        add_step(steps, driver, "Edit Room Type")

        page.enter_no_of_bed(EDIT_NO_OF_BED)
        add_step(steps, driver, "Edit No Of Bed")

        page.enter_cost_per_bed(EDIT_COST_PER_BED)
        add_step(steps, driver, "Edit Cost Per Bed")

        page.enter_description(EDIT_DESCRIPTION)
        add_step(steps, driver, "Edit Description")

        page.click_update()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Update Button")

        verify_no_validation_error(driver)

        EDIT_EXPECTED_ROW_VALUES = [
            EDIT_ROOM_NAME,
            EDIT_SELECTED_HOSTEL,
            EDIT_SELECTED_ROOM_TYPE,
            EDIT_NO_OF_BED,
            EDIT_COST_PER_BED
        ]

        verify_exact_table_row_added(
            driver,
            EDIT_EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Hostel Room Updated")

        page.click_delete_for_exact_row(
            EDIT_EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Click Delete Button")

        page.confirm_delete_if_present()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Confirm Delete")

        verify_exact_table_row_deleted(
            driver,
            EDIT_EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Hostel Room Deleted")

    except Exception as e:
        add_step(steps, driver, "Test Failed", "FAIL")
        raise e

    finally:
        create_pdf_report("Hostel_Room_Test_Report", steps)