from pages.book_publication_page import BookPublicationPage

import os
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
BOOK_PUBLICATION_URL = "https://devanttest.in/him_test/#/staff-information/book-publication"

EMAIL = "admin@admin.com"
PASSWORD = "12345678"

STAFF_NAME = "Shyam Samanta"

RANDOM_NUMBER = random.randint(1000, 9999)

BOOK_NAME = f"Test Book {RANDOM_NUMBER}"
PUBLISHER_NAME = f"Test Publisher {RANDOM_NUMBER}"
ISBN_NUMBER = f"414214{RANDOM_NUMBER}"
CHAPTER_FULL_BOOK = f"Test Full Book {RANDOM_NUMBER}"
CHAPTER_NAME = f"Test Chapter {RANDOM_NUMBER}"
PAGE_NUMBER = f"217{RANDOM_NUMBER}"

EDIT_BOOK_NAME = f"Updated Book {RANDOM_NUMBER}"
EDIT_PUBLISHER_NAME = f"Updated Publisher {RANDOM_NUMBER}"
EDIT_ISBN_NUMBER = f"515215{RANDOM_NUMBER}"
EDIT_CHAPTER_FULL_BOOK = f"Updated Full Book {RANDOM_NUMBER}"
EDIT_CHAPTER_NAME = f"Updated Chapter {RANDOM_NUMBER}"
EDIT_PAGE_NUMBER = f"318{RANDOM_NUMBER}"

UPLOAD_FILE_PATH = r"C:\Users\Devant\Downloads\book_list (1).pdf"


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


def verify_file_uploaded(driver):
    file_inputs = driver.find_elements(
        By.XPATH,
        "//label[normalize-space()='Upload File']/following::input[@type='file'][1]"
    )

    assert len(file_inputs) > 0, "Book publication file input was not found"

    return True


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
                f"Validation error found after submit/search: {visible_errors}"
            )

        time.sleep(1)

    raise AssertionError(
        "Book publication record was not loaded. "
        "After clicking Submit/Search, no row appeared in the Book Publication table. "
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

    table_text = ""

    try:
        table_text = driver.find_element(By.XPATH, "//table//tbody").text
    except Exception:
        table_text = driver.find_element(By.XPATH, "//body").text

    raise AssertionError(
        f"Exact book publication row not found after waiting 30 seconds. "
        f"Expected values: {expected_values}. "
        f"Actual table/page text: {table_text}"
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
        "\nBook Publication Delete Verification Failed\n"
        "-------------------------------------------\n"
        "Expected Result : Updated book publication row should be deleted from the table.\n"
        "Actual Result   : Updated book publication row is still visible after delete confirmation.\n\n"
        f"Deleted Values  : {deleted_values}\n\n"
        "Possible Reason :\n"
        "1. Delete confirmation popup was not clicked successfully.\n"
        "2. Delete API failed in the application.\n"
        "3. Table did not refresh after delete.\n"
        "4. Delete button clicked but record was not removed from database.\n\n"
        f"Still Visible Row:\n{matching_row_text}\n\n"
        f"Actual Table Text:\n{table_text}"
    )


def fill_book_publication_form(page):
    page.select_staff_shyam_samanta()
    page.enter_book_name(BOOK_NAME)
    page.enter_publisher_name(PUBLISHER_NAME)
    page.enter_isbn_number(ISBN_NUMBER)
    page.enter_chapter_full_book(CHAPTER_FULL_BOOK)
    page.enter_chapter_name(CHAPTER_NAME)
    page.enter_page_number(PAGE_NUMBER)
    page.upload_file(UPLOAD_FILE_PATH)


def fill_edit_book_publication_form(page):
    page.select_staff_shyam_samanta()
    page.enter_book_name(EDIT_BOOK_NAME)
    page.enter_publisher_name(EDIT_PUBLISHER_NAME)
    page.enter_isbn_number(EDIT_ISBN_NUMBER)
    page.enter_chapter_full_book(EDIT_CHAPTER_FULL_BOOK)
    page.enter_chapter_name(EDIT_CHAPTER_NAME)
    page.enter_page_number(EDIT_PAGE_NUMBER)
    page.upload_file(UPLOAD_FILE_PATH)


def test_book_publication_add_show_edit_delete_flow(driver):
    steps = []
    wait = WebDriverWait(driver, 20)

    try:
        page = BookPublicationPage(driver)

        assert os.path.exists(UPLOAD_FILE_PATH), (
            f"Upload file does not exist: {UPLOAD_FILE_PATH}"
        )

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

        driver.get(BOOK_PUBLICATION_URL)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))

        assert "book-publication" in driver.current_url.lower(), (
            f"Book Publication page did not open. Current URL: {driver.current_url}"
        )

        add_step(steps, driver, "Open Book Publication Page")

        page.click_add_book_publication()
        add_step(steps, driver, "Click Add Book Publication")

        fill_book_publication_form(page)
        verify_file_uploaded(driver)
        add_step(steps, driver, "Fill Book Publication Form")

        page.click_submit()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Submit Button")

        verify_no_validation_error(driver)

        page.click_show_book_publication()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Show Book Publication")

        page.search_book_publication(STAFF_NAME)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Search Book Publication")

        wait_for_table_or_validation(driver, timeout=30)
        add_step(steps, driver, "Load Book Publication List")

        EXPECTED_ROW_VALUES = [
            STAFF_NAME,
            BOOK_NAME,
            ISBN_NUMBER,
            PUBLISHER_NAME,
            CHAPTER_FULL_BOOK,
            CHAPTER_NAME,
            PAGE_NUMBER
        ]

        verify_exact_table_row_added(
            driver,
            EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Book Publication Added")

        page.click_download_for_exact_row(
            EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Click Download Book Publication File")

        page.click_edit_for_exact_row(
            EXPECTED_ROW_VALUES
        )
        wait.until(EC.presence_of_element_located(page.UPDATE_BUTTON))
        add_step(steps, driver, "Click Edit Button")

        fill_edit_book_publication_form(page)
        verify_file_uploaded(driver)
        add_step(steps, driver, "Edit Book Publication Form")

        page.click_update()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Update Button")

        verify_no_validation_error(driver)

        page.click_show_book_publication()
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Click Show Updated Book Publication")

        page.search_book_publication(STAFF_NAME)
        wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
        add_step(steps, driver, "Search Updated Book Publication")

        wait_for_table_or_validation(driver, timeout=30)
        add_step(steps, driver, "Load Updated Book Publication List")

        EDIT_EXPECTED_ROW_VALUES = [
            STAFF_NAME,
            EDIT_BOOK_NAME,
            EDIT_ISBN_NUMBER,
            EDIT_PUBLISHER_NAME,
            EDIT_CHAPTER_FULL_BOOK,
            EDIT_CHAPTER_NAME,
            EDIT_PAGE_NUMBER
        ]

        verify_exact_table_row_added(
            driver,
            EDIT_EXPECTED_ROW_VALUES
        )
        add_step(steps, driver, "Verify Book Publication Updated")

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
        add_step(steps, driver, "Verify Book Publication Deleted")

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
        create_pdf_report("Book_Publication_Test_Report", steps)