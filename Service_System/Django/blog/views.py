from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Post, Space
from .serializers import PostSerializer, SpaceSerializer


# ---------------- 블로그 페이지 (课件原有) ----------------
def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now())
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


# ---------------- REST API ----------------
class BlogImages(viewsets.ModelViewSet):
    """/api_root/Post/ : POST(Edge 업로드, 2-3), GET 목록·상세(App, 2-4).

    최신순, 페이지네이션, ?space=<id> 필터.
    """
    queryset = Post.objects.all().order_by('-published_date', '-id')
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['space']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,
                        published_date=serializer.validated_data.get(
                            'published_date') or timezone.now())


class SpaceViewSet(viewsets.ReadOnlyModelViewSet):
    """/api_root/Space/ : 공간 목록 + 최신 상태 (GET)."""
    queryset = Space.objects.all().order_by('id')
    serializer_class = SpaceSerializer
    permission_classes = [IsAuthenticated]
