import pytest
import allure
import os
import shutil
from pathlib import Path
from time import sleep
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()

@pytest.fixture(scope="function")
def page(browser):
    video_dir = Path("./videos")
    video_dir.mkdir(parents=True, exist_ok=True)
    context = browser.new_context(record_video_dir=str(video_dir))
    page = context.new_page()
    page.set_default_timeout(20000)
    yield page
    context.close()

def pytest_runtest_makereport(item, call):
    if call.when == 'call' and call.excinfo is not None:
        page = item.funcargs['page']
        
        # Save screenshot
        screenshot_dir = Path('./screenshots') / item.nodeid.replace("::", "_").rsplit("/", 1)[0]
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        screenshot_path = screenshot_dir / f'{item.nodeid.replace("::", "_").split("/")[-1]}.png'
        page.screenshot(path=str(screenshot_path))
        allure.attach.file(str(screenshot_path), name='screenshot', attachment_type=allure.attachment_type.PNG)
        
        # Ensure video is properly finalized
        sleep(1)  # Small delay to ensure the video file is no longer in use
        video_path = page.video.path()

        if not video_path:
            return
        
        # Move the video
        video_dest_dir = Path('./videos') / item.nodeid.replace("::", "_").rsplit("/", 1)[0]
        video_dest_dir.mkdir(parents=True, exist_ok=True)
        video_dest_path = video_dest_dir / f'{item.nodeid.replace("::", "_").split("/")[-1]}.webm'
        
        for _ in range(3):
            try:
                shutil.move(video_path, str(video_dest_path))
                break
            except PermissionError:
                sleep(1)

        # Close the context to release the video file
        page.context.close()

        # Ensure the original video file is deleted if it exists in the source directory
        if os.path.exists(video_path):
            try:
                os.remove(video_path)
            except Exception as e:
                print(f"Error deleting video file: {e}")

        # Attach the moved video
        allure.attach.file(str(video_dest_path), name='video', attachment_type=allure.attachment_type.WEBM)

 #Add a fixture to clean up screenshots and videos folders before test run
@pytest.fixture(scope="session", autouse=True)
def cleanup_folders():
    screenshots_dir = Path("./screenshots")
    videos_dir = Path("./videos")

    # Clean up screenshots folder
    if screenshots_dir.exists() and screenshots_dir.is_dir():
        shutil.rmtree(screenshots_dir)

    # Clean up videos folder
    if videos_dir.exists() and videos_dir.is_dir():
        shutil.rmtree(videos_dir)
    yield

# Configure pytest to generate HTML report
def pytest_configure(config):
    config.option.htmlpath = './pytest_report/report.html'
