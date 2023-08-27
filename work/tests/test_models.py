from django.test import TestCase

from work.models import Work


class TestWork(TestCase):

    def test_meta_ordering(self):
        obj = Work.objects.get(id=1)
        ordering = obj._meta.ordering
        self.assertEqual(ordering, ['-created_at'])
