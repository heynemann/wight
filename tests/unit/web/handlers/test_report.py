#!/usr/bin/env python
# -*- coding: utf-8 -*-

# wight load testing
# https://github.com/heynemann/wight

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2013 Bernardo Heynemann heynemann@gmail.com
from datetime import datetime

from preggy import expect
import mock

from tests.unit.base import WebTestCase
from wight.web.handlers.base import format_date
from wight.web.handlers.report import ReportHandler


class datetime_mock():
    def now(self):
        return datetime.strptime("12/12/2012", "%d/%m/%Y")


class ReportHandlerTest(WebTestCase):

    @mock.patch('wight.web.handlers.report.datetime', new=datetime_mock())
    @mock.patch.object(ReportHandler, 'version')
    @mock.patch.object(ReportHandler, 'render')
    @mock.patch.object(ReportHandler, '_get_last_result')
    @mock.patch.object(ReportHandler, 'get_api')
    def test_get(self, get_mock, last_result_mock, get_render, version_mock):

        response_mock = mock.Mock(status_code=200, content='{"results":["a"],"team":[], "project":[], "createdBy":[], "lastModified":[]}')
        get_mock.return_value = response_mock
        last_result_mock.return_value = '123'
        version_mock.return_value = '0.2.22'
        response = self.fetch('/report/123/')
        expect(response.code).to_equal(200)

        get_render.assert_called_with('report.html', uuid=u'123', runAt=[], last_result='123', project=[],
                                      report_date='12/12/2012 00:00:00', version='0.2.22', createdBy=[], team=[],
                                      test=u'a', format_date=format_date)

    @mock.patch('wight.web.handlers.report.datetime', new=datetime_mock())
    @mock.patch.object(ReportHandler, 'version')
    @mock.patch.object(ReportHandler, 'render')
    @mock.patch.object(ReportHandler, 'get_api')
    def test_api_was_called_correctly(self, get_mock, render_mock, version_mock):

        response_mock = mock.Mock(status_code=302)
        get_mock.return_value = response_mock
        version_mock.return_value = '0.2.22'
        self.fetch('/report/123/')
        get_mock.assert_called_with("load-test-result/123/")
        render_mock.assert_called_with('report.html', uuid=u'123',
                                       report_date='12/12/2012 00:00:00', version='0.2.22',
                                       test=None, format_date=format_date)

    def test_web_returns_404_if_no_uuid(self):
        response = self.fetch('/report/')
        expect(response.code).to_equal(404)
