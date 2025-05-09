from django.contrib.auth.mixins import UserPassesTestMixin


class OperationsGroupRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name="Operations").exists()
