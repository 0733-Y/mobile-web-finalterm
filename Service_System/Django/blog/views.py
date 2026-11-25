from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Post, Space
from .permissions import IsUploaderOrReadOnly
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
    """/api_root/Post/ : POST(Edge 업로드, 2-3, edge 계정만), GET 목록·상세(App, 2-4, 로그인한 모든 계정).

    최신순, 페이지네이션, ?space=<id> 필터.
    """
    queryset = Post.objects.all().order_by('-published_date', '-id')
    serializer_class = PostSerializer
    permission_classes = [IsUploaderOrReadOnly]  # 쓰기는 edge(blog.add_post) 만
    filterset_fields = ['space']

    def perform_create(self, serializer):
        # 게시 시각은 서버 시계로 정한다. Edge PC 의 시계가 서버보다 빠르면 클라이언트가 보낸
        # published_date 가 '미래'가 되어 홈 화면(published_date <= now 필터)에 한동안 안 보이기 때문.
        serializer.save(author=self.request.user, published_date=timezone.now())


class SpaceViewSet(viewsets.ReadOnlyModelViewSet):
    """/api_root/Space/ : 공간 목록 + 최신 상태 (GET)."""
    queryset = Space.objects.all().order_by('id')
    serializer_class = SpaceSerializer
    permission_classes = [IsAuthenticated]
