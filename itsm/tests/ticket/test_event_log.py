# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making BK-ITSM 蓝鲸流程服务 available.

Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.

BK-ITSM 蓝鲸流程服务 is licensed under the MIT License.

License for BK-ITSM 蓝鲸流程服务:
--------------------------------------------------------------------
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import json

from django.test import TestCase, override_settings
from blueapps.core.celery.celery import app

from itsm.project.models import ProjectConfig, Project
from itsm.tests.ticket.params import CREATE_TICKET_PARAMS
from itsm.ticket.models import TicketEventLog, Ticket


class TicketEventLogTestCase(TestCase):
    def setUp(self):
        app.conf.update(CELERY_ALWAYS_EAGER=True)
        Ticket.objects.all().delete()
        self.create_project_data = {
            "key": "0",
            "name": "test",
            "logo": "",
            "color": [],
            "creator": "admin",
            "create_at": "2021-05-30 17:16:40",
            "updated_by": "test_admin",
            "update_at": "2021-05-30 17:16:40",
        }
        Project.objects.create(**self.create_project_data)
        project_config = {"workflow_prefix": "test", "project_key": "0"}
        ProjectConfig.objects.create(**project_config)
        # CatalogService.objects.create(service_id=1, is_deleted=False, catalog_id=2, creator="admin")
        TicketEventLog.objects.all().delete()

    @override_settings(MIDDLEWARE=("itsm.tests.middlewares.OverrideMiddleware",))
    def test_get_index_ticket_event_log(self):
        publish_rep = self.client.post(
            path="/api/project/manager/publish/",
            data=json.dumps({"project_key": "0"}),
            content_type="application/json",
        )
        self.assertEqual(publish_rep.data["code"], "OK")
        self.assertEqual(publish_rep.data["message"], "success")

        url = "/api/ticket/receipts/create_ticket/"

        resp = self.client.post(
            path=url,
            data=json.dumps(CREATE_TICKET_PARAMS),
            content_type="application/json",
        )

        sn = resp.data["data"]["sn"]

        url = "/api/ticket/logs/get_index_ticket_event_log/"
        resp = self.client.get(url)

        self.assertEqual(resp.data["result"], True)
        self.assertEqual(resp.data["code"], "OK")
        self.assertEqual(resp.data["message"], "success")
        self.assertEqual(resp.data["data"][0]["sn"], sn)
