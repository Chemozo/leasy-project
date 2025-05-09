from django.contrib.auth.mixins import UserPassesTestMixin


class SalesGroupRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name="Sales").exists()
