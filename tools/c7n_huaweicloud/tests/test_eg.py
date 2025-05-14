# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

from unittest import mock
import os

from tools.c7n_huaweicloud.tests.huaweicloud_common import BaseTest


class EventStreamingTest(BaseTest):
    """Test EventStreaming resources, filters, and actions."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        os.environ['HUAWEICLOUD_SDK_REGION_EG_AP_SOUTHEAST_1'] = "https://eg.ap-southeast-1.myhuaweicloud.com"

    def test_eg_subscriptions_query(self):
        """Test basic query functionality for event streaming."""
        factory = self.replay_flight_data('eg_subscriptions_query')
        p = self.load_policy({
            'name': 'subscriptions-query-test',
            'resource': 'huaweicloud.eg-subscription'
        }, session_factory=factory)
        resources = p.run()
        # Verify VCR: eg_eventstreaming_query should return 1 resource
        self.assertEqual(len(resources), 1)

    def test_filter_tag_count_match(self):
        """Test the 'tag-count' filter."""
        factory = self.replay_flight_data('eg_subscriptions_filter_tag_count')
        # Mock augment to simulate tag data, avoiding TMS client issues
        with mock.patch('c7n_huaweicloud.resources.eg.Subscription.augment') as mock_augment:
            def mock_augment_implementation(resources):
                for resource in resources:
                    if resource['id'] == '63cfd150-65fd-4180-ba32-e9710100d100':
                        resource['tags'] = [
                            {'key': 'RequiredTag', 'value': 'RequiredValue'},
                        ]
                    else:
                        resource['tags'] = []
                return resources
            mock_augment.side_effect = mock_augment_implementation
            expected_tag_count = 1
            p = self.load_policy({
                'name': 'subscriptions-tag-count-match',
                'resource': 'huaweicloud.eg-subscription',
                'filters': [{'type': 'tag-count', 'count': expected_tag_count, 'op': 'eq'}]
            }, session_factory=factory)
            resources = p.run()
            # Verify VCR: tag_count should contain one resource with exactly 2 tags
            self.assertEqual(len(resources), 1)
            self.assertEqual(resources[0]['id'], '63cfd150-65fd-4180-ba32-e9710100d100')
