from pages.library_item_stock_page import LibraryItemStockPage

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
LIBRARY_ITEM_STOCK_URL = "https://devanttest.in/him_test/#/library/item-stock"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

RANDOM_NUMBER = random.randint(1000, 9999)

BOOK_TITLE = f"Test Book {RANDOM_NUMBER}"
QUANTITY = "45"
REMAINING_QUANTITY = "34"
ISBN_NO = f"214{RANDOM_NUMBER}"
PUBLISHER_NAME = f"Publisher {RANDOM_NUMBER}"
AUTHOR_NAME = f"Author {RANDOM_NUMBER}"
RACK_NUMBER = f"Rack {RANDOM_NUMBER}"
BOOK_PRICE = "342"
FINE_PER_DAY = "1"
DESCRIPTION = f"Test Description {RANDOM_NUMBER}"

EDIT_BOOK_TITLE = f"Updated Book {RANDOM_NUMBER}"
EDIT_QUANTITY = "50"
EDIT_REMAINING_QUANTITY = "40"
EDIT_ISBN_NO = f"314{RANDOM_NUMBER}"
EDIT_PUBLISHER_NAME = f"Updated Publisher {RANDOM_NUMBER}"
EDIT_AUTHOR_NAME = f"Updated Author {RANDOM_NUMBER}"
EDIT_RACK_NUMBER = f"Updated Rack {RANDOM_NUMBER}"
EDIT_BOOK_PRICE = "400"
EDIT_FINE_PER_DAY = "2"
EDIT_DESCRIPTION = f"Updated Description {RANDOM_NUMBER}"


@pytest.fixture()
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()


def add_step(steps, driver, name, status="PASS", reason=""):
    steps.append({
        "name": name,
        "status": status,
        "reason": reason,
        "image": take_screenshot(driver, name.lower().replace(" ", "_"))
    })


def verify_no_validation_error(driver):
    errors = driver.find_elements(
        By.XPATH,
        "//*[contains(text(),'required') or contains(text(),'Required') or contains(text(),'invalid') or contains(text(),'Invalid')]"
    )

    visible_errors = [
        error.text.strip()
        for error in errors
        if error.is_displayed() and error.text.strip()
    ]

    assert len(visible_errors) == 0, f"Validation error found: {visible_errors}"


def wait_for_table_or_validation(driver, timeout=30):
    end_time = time.time() + timeout

    while time.time() < end_time:
        rows = driver.find_elements(By.XPATH, "//table//tbody//tr")

        if len(rows) > 0:
            return True

        errors = driver.find_elements(
            By.XPATH,
            "//*[contains(text(),'required') or contains(text(),'Required') or contains(text(),'invalid') or contains(text(),'Invalid')]"
        )

        visible_errors = [
            error.text.strip()
            for error in errors
            if error.is_displayed() and error.text.strip()
        ]

        if visible_errors:
            raise AssertionError(
                f"Validation error found after submit: {visible_errors}"
            )

        time.sleep(1)

    raise AssertionError(
        "Library book record was not added. "
        "After clicking Submit, no row appeared in the Books List table. "
        "Please check whether the form was submitted successfully or whether the server rejected the request."
    )


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
        f"Exact library book row not found after waiting 30 seconds. "
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
        "\nLibrary Book Delete Verification Failed\n"
        "---------------------------------------\n"
        "Expected Result : Updated library book row should be deleted from the table.\n"
        "Actual Result   : Updated library book row is still visible after delete confirmation.\n\n"
        f"Deleted Values  : {deleted_values}\n\n"
        "Possible Reason :\n"
        "1. Delete confirmation popup was not clicked successfully.\n"
        "2. Delete API failed in the application.\n"
        "3. Table did not refresh after delete.\n"
        "4. Delete button clicked but record was not removed from database.\n\n"
        f"Still Visible Row:\n{matching_row_text}\n\n"
        f"Actual Table Text:\n{table_text}"
    )


def fill_library_item_stock_form(page):
    page.enter_book_title(BOOK_TITLE)
    page.select_course_bba_hospital_management()
    page.select_semester_2nd_sem()
    page.select_subject_fundamentals()
    page.enter_quantity(QUANTITY)
    page.enter_remaining_quantity(REMAINING_QUANTITY)
    page.enter_isbn_no(ISBN_NO)
    page.enter_publisher_name(PUBLISHER_NAME)
    page.enter_author_name(AUTHOR_NAME)
    page.enter_rack_number(RACK_NUMBER)
    page.enter_book_price(BOOK_PRICE)
    page.enter_fine_per_day(FINE_PER_DAY)
    page.enter_description(DESCRIPTION)


def test_library_item_stock_add_edit_delete_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = LibraryItemStockPage(driver)

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

        driver.get(LIBRARY_ITEM_STOCK_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "item-stock" in driver.current_url.lower(), (
            f"Library Item Stock page did not open. Current URL: {driver.current_url}"
        )

        add_step(steps, driver, "Open Library Item Stock Page")

        fill_library_item_stock_form(page)
        add_step(steps, driver, "Fill Library Book Form")

        page.click_submit()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Submit Button")

        verify_no_validation_error(driver)

        wait_for_table_or_validation(driver, timeout=30)
        add_step(steps, driver, "Load Books List")

        EXPECTED_ROW_VALUES = [
            BOOK_TITLE,
            QUANTITY,
            REMAINING_QUANTITY
        ]

        verify_exact_table_row_added(
            driver,
            EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Library Book Added")

        page.click_edit_for_exact_row(
            EXPECTED_ROW_VALUES
        )
        wait.until(EC.presence_of_element_located(page.UPDATE_BUTTON))
        add_step(steps, driver, "Click Edit Button")

        page.enter_book_title(EDIT_BOOK_TITLE)
        add_step(steps, driver, "Edit Book Title")

        page.select_course_bba_hospital_management()
        add_step(steps, driver, "Edit Course")

        page.select_semester_2nd_sem()
        add_step(steps, driver, "Edit Semester")

        page.enter_quantity(EDIT_QUANTITY)
        add_step(steps, driver, "Edit Quantity")

        page.enter_remaining_quantity(EDIT_REMAINING_QUANTITY)
        add_step(steps, driver, "Edit Remaining Quantity")

        page.enter_isbn_no(EDIT_ISBN_NO)
        add_step(steps, driver, "Edit ISBN No")

        page.enter_publisher_name(EDIT_PUBLISHER_NAME)
        add_step(steps, driver, "Edit Publisher Name")

        page.enter_author_name(EDIT_AUTHOR_NAME)
        add_step(steps, driver, "Edit Author Name")

        page.enter_rack_number(EDIT_RACK_NUMBER)
        add_step(steps, driver, "Edit Rack Number")

        page.enter_book_price(EDIT_BOOK_PRICE)
        add_step(steps, driver, "Edit Book Price")

        page.enter_fine_per_day(EDIT_FINE_PER_DAY)
        add_step(steps, driver, "Edit Fine Per Day")

        page.enter_description(EDIT_DESCRIPTION)
        add_step(steps, driver, "Edit Description")

        page.click_update()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Update Button")

        verify_no_validation_error(driver)

        wait_for_table_or_validation(driver, timeout=30)
        add_step(steps, driver, "Load Updated Books List")

        EDIT_EXPECTED_ROW_VALUES = [
            EDIT_BOOK_TITLE,
            EDIT_QUANTITY,
            EDIT_REMAINING_QUANTITY
        ]

        verify_exact_table_row_added(
            driver,
            EDIT_EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Library Book Updated")

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
        add_step(steps, driver, "Verify Library Book Deleted")

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
        create_pdf_report("Library_Item_Stock_Test_Report", steps)