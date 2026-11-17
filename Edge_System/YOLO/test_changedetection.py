"""ChangeDetection 규칙 단위 테스트 (카메라/서버 없이 인원 수 시퀀스로 확인).
실행: python -m unittest test_changedetection -v"""
import unittest

from changedetection import ChangeDetection, crowd_level

CFG = {'server': 'http://x', 'username': 'u', 'password': 'p', 'space_id': 1,
       'capacity': 10, 'stable_frames': 5, 'min_interval_sec': 60,
       'title_prefix': '5960', 'space_name': 'A'}


def run(mode, counts, fps=30):
    cd = ChangeDetection({**CFG, 'mode': mode})
    uploads = []
    for f, c in enumerate(counts):
        now = f / fps
        if cd.update(c, now):
            uploads.append((f, c))
            cd.mark_uploaded(c, now)
    return uploads


class Tests(unittest.TestCase):
    def test_count_needs_stable_frames(self):
        # 3명이 4프레임만 유지되면(5 필요) 무시, 이후 2명이 안정적이면 업로드
        seq = [0] * 10 + [3] * 4 + [0] * 3 + [2] * 10
        self.assertEqual(run('count', seq)[0][1], 0)       # 최초 상태(0명)
        self.assertNotIn(3, [c for _, c in run('count', seq)])

    def test_count_min_interval(self):
        seq = [0] * 10 + [2] * 10 + [4] * 10      # 1초 이내에 두 번 바뀜 -> 최소 간격 60초로 두 번째는 보류
        self.assertEqual([c for _, c in run('count', seq)], [0])

    def test_baseline_reacts_to_flicker(self):
        # 없음->있음 전환마다 즉시 업로드 (깜빡임에 취약)
        seq = [0, 1, 0, 1, 0, 1, 1, 1, 0, 2]
        self.assertEqual(len(run('baseline', seq)), 4)

    def test_title_has_prefix(self):
        self.assertEqual(ChangeDetection(CFG).make_title(3), '5960 | A | 3명')

    def test_level(self):
        self.assertEqual([crowd_level(n, 10) for n in (3, 4, 7, 8)], ['여유', '보통', '보통', '혼잡'])


if __name__ == '__main__':
    unittest.main()
