from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive


@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    open_robot_order_website()
    orders = get_orders()
    for order in orders:
        close_annoying_modal()
        fill_the_form(order)
        preview_the_robot()
        submit_the_order()
        pdf_file = store_receipt_as_pdf(order["Order number"])
        screenshot = screenshot_robot(order["Order number"])
        embed_screenshot_to_receipt(screenshot, pdf_file)
        order_another_robot()
    create_zip_archive()


def open_robot_order_website():
    """
    Opens the RobotSpareBin Industries Inc. website in a browser.
    """
    browser.goto("https://robotsparebinindustries.com/#/robot-order")


def get_orders():
    """
    Gets the orders from the RobotSpareBin Industries Inc. website.
    Overwrites the downloaded file if it already exists.
    """
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    tables = Tables()
    orders = tables.read_table_from_csv("orders.csv", header=True)
    return orders


def close_annoying_modal():
    """
    Closes the annoying modal that appears on the RobotSpareBin Industries Inc. website.
    """
    page = browser.page()
    page.click("button.btn.btn-dark:has-text('OK')")


def fill_the_form(order):
    """
    Fills the form on the RobotSpareBin Industries Inc. website.
    """
    page = browser.page()
    page.select_option("#head", order["Head"])
    page.check(f"input[name='body'][value='{order['Body']}']")
    page.fill("input[placeholder='Enter the part number for the legs']", order["Legs"])
    page.fill("#address", order["Address"])


def preview_the_robot():
    """
    Previews the robot on the RobotSpareBin Industries Inc. website.
    """
    page = browser.page()
    page.click("#preview")


def submit_the_order():
    """
    Submits the order on the RobotSpareBin Industries Inc. website.
    """
    page = browser.page()
    while True:
        page.click("#order")
        if not page.is_visible(".alert.alert-danger"):
            break


def store_receipt_as_pdf(order_number):
    """
    Stores the receipt of the order as a PDF file in a subfolder named "receipts". The PDF file is named "receipt_{order_number}.pdf"  and return a result (the file system path to the PDF file).
    """
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf_path = f"output/receipts/receipt_{order_number}.pdf"
    pdf.html_to_pdf(receipt_html, pdf_path)
    return pdf_path


def screenshot_robot(order_number):
    """
    Takes a screenshot of the ordered robot and saves it as "robot_{order_number}.png" in the "output/robots" folder.
    """
    page = browser.page()
    screenshot_path = f"output/robots/robot_{order_number}.png"
    page.screenshot(path=screenshot_path)
    return screenshot_path


def embed_screenshot_to_receipt(screenshot, pdf_file):
    """
    Embeds the screenshot of the robot to the PDF receipt.
    """
    pdf = PDF()
    pdf.add_files_to_pdf(files=[screenshot], target_document=pdf_file, append=True)


def order_another_robot():
    """
    Clicks the "Order Another Robot" button on the RobotSpareBin Industries Inc. website to reset the form for the next order.
    """
    page = browser.page()
    page.click("#order-another")


def create_zip_archive():
    """
    Creates a ZIP archive of the receipts and the images in the "output" folder.
    The ZIP file is named "robot_orders.zip".
    """
    lib = Archive()
    lib.archive_folder_with_zip(
        folder="output", archive_name="output/robot_orders.zip", recursive=True
    )
