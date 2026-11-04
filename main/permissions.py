from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsPortfolioOwnerOrReadOnly(BasePermission):
    message = "Only the portfolio owner can manage projects."

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_superuser


class IsPortfolioOwnerOrEditorOrReadOnly(BasePermission):
    message = "Only the owner can create/delete; Editors may update existing items."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        if request.method not in ("PUT", "PATCH"):
            return False
        model = view.resource_model
        return request.user.groups.filter(name="Editor").exists() or request.user.has_perm(
            f"{model._meta.app_label}.change_{model._meta.model_name}"
        )
