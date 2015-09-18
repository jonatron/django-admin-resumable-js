from .models import Foo

from django.test import client as client_module
from django.conf import settings

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import os
import pytest
import time


def create_test_file(file_path, size_in_megabytes):
    with open(file_path, 'wb') as bigfile:
        bigfile.seek(size_in_megabytes * 1024 * 1024)
        bigfile.write(b'0')


def clear_uploads():
    upload_path = os.path.join(settings.MEDIA_ROOT, 'admin_uploaded')
    if not os.path.exists(upload_path):
        return
    for the_file in os.listdir(upload_path):
        file_path = os.path.join(upload_path, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)


@pytest.mark.django_db
def test_fake_file_upload(admin_user, admin_client):
    clear_uploads()

    payload = client_module.FakePayload()

    def form_value_list(key, value):
        return ['--' + client_module.BOUNDARY,
                'Content-Disposition: form-data; name="%s"' % key,
                "",
                value]
    form_vals = []
    file_data = 'foo bar foo bar.'
    file_size = str(len(file_data))
    form_vals += form_value_list("resumableChunkNumber", "1")
    form_vals += form_value_list("resumableChunkSize", file_size)
    form_vals += form_value_list("resumableType", "text/plain")
    form_vals += form_value_list("resumableIdentifier", file_size + "-foobar")
    form_vals += form_value_list("resumableFilename", "foo.bar")
    form_vals += form_value_list("resumableTotalChunks", "1")
    form_vals += form_value_list("resumableTotalSize", file_size)
    payload.write('\r\n'.join(form_vals+[
        '--' + client_module.BOUNDARY,
        'Content-Disposition: form-data; name="file"; filename=foo.bar',
        'Content-Type: application/octet-stream',
        '',
        file_data,
        '--' + client_module.BOUNDARY + '--\r\n'
    ]))

    r = {
        'CONTENT_LENGTH': len(payload),
        'CONTENT_TYPE': client_module.MULTIPART_CONTENT,
        'PATH_INFO': "/admin_resumable/admin_resumable/",
        'REQUEST_METHOD': 'POST',
        'wsgi.input': payload,
    }
    response = admin_client.request(**r)
    assert response.status_code == 200
    upload_filename = file_size + "_foo.bar"
    upload_path = os.path.join(settings.MEDIA_ROOT,
                               'admin_uploaded',
                               upload_filename
                               )
    f = open(upload_path, 'r')
    uploaded_contents = f.read()
    assert file_data == uploaded_contents


@pytest.mark.django_db
def test_fake_file_upload_incomplete_chunk(admin_user, admin_client):
    clear_uploads()

    payload = client_module.FakePayload()

    def form_value_list(key, value):
        return ['--' + client_module.BOUNDARY,
                'Content-Disposition: form-data; name="%s"' % key,
                "",
                value]
    form_vals = []
    file_data = 'foo bar foo bar.'
    file_size = str(len(file_data))
    form_vals += form_value_list("resumableChunkNumber", "1")
    form_vals += form_value_list("resumableChunkSize", "3")
    form_vals += form_value_list("resumableType", "text/plain")
    form_vals += form_value_list("resumableIdentifier", file_size + "-foobar")
    form_vals += form_value_list("resumableFilename", "foo.bar")
    form_vals += form_value_list("resumableTotalChunks", "6")
    form_vals += form_value_list("resumableTotalSize", file_size)
    payload.write('\r\n'.join(form_vals+[
        '--' + client_module.BOUNDARY,
        'Content-Disposition: form-data; name="file"; filename=foo.bar',
        'Content-Type: application/octet-stream',
        '',
        file_data[0:1],
        # missing final boundary to simulate failure
    ]))

    r = {
        'CONTENT_LENGTH': len(payload),
        'CONTENT_TYPE': client_module.MULTIPART_CONTENT,
        'PATH_INFO': "/admin_resumable/admin_resumable/",
        'REQUEST_METHOD': 'POST',
        'wsgi.input': payload,
    }
    try:
        response = admin_client.request(**r)
    except AttributeError:
        pass  # we're not worried that this would 500

    get_url = "/admin_resumable/admin_resumable/?"
    get_args = {
        'resumableChunkNumber': '1',
        'resumableChunkSize': '3',
        'resumableCurrentChunkSize': '3',
        'resumableTotalSize': file_size,
        'resumableType': "text/plain",
        'resumableIdentifier': file_size + "-foobar",
        'resumableFilename': "foo.bar",
        'resumableRelativePath':  "foo.bar",
    }

    # we need a fresh client because client.request breaks things
    fresh_client = client_module.Client()
    fresh_client.login(username=admin_user.username, password='password')
    get_response = fresh_client.get(get_url, get_args)
    # should be a 404 because we uploaded an incomplete chunk
    assert get_response.status_code == 404


@pytest.mark.django_db
def test_real_file_upload(admin_user, live_server, driver):
    test_file_path = "/tmp/test_small_file.bin"
    create_test_file(test_file_path, 5)

    driver.get(live_server.url + '/admin/')
    driver.find_element_by_id('id_username').send_keys("admin")
    driver.find_element_by_id("id_password").send_keys("password")
    driver.find_element_by_xpath('//input[@value="Log in"]').click()
    driver.implicitly_wait(2)
    driver.get(live_server.url + '/admin/tests/foo/add/')
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "id_bar"))
    )
    driver.find_element_by_id("id_bar").send_keys("bat")
    driver.find_element_by_css_selector(
        'input[type="file"]').send_keys(test_file_path)
    status_text = driver.find_element_by_id("id_foo_uploaded_status").text
    i = 0
    while i < 5:
        if "Uploaded" in status_text:
            return  # success
        time.sleep(1)
        i += 1
    raise Exception  # something went wrong
