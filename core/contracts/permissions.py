from django.contrib.auth.mixins import UserPassesTestMixin


class CollectionsGroupRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name="Collections").exists()
