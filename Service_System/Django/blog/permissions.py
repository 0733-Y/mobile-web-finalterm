from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsUploaderOrReadOnly(BasePermission):
    """로그인한 사용자는 조회(GET/HEAD/OPTIONS)만 가능.
    쓰기(POST/PUT/PATCH/DELETE)는 `blog.add_post` 권한이 있는 계정(Edge 업로드용 edge, 관리자)만 가능.
    -> 평가용 viewer 계정은 읽기 전용 (학생 결정, 2026-11-25)."""
    message = '이 계정은 조회만 할 수 있습니다 (업로드 권한 없음).'

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return user.has_perm('blog.add_post')
