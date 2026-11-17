"""정적 이미지 한 장을 업로드해 서버 연동을 확인한다.
사용: python post_test.py <image.jpg> <person_count> [config.json]"""
import sys

import cv2

sys.stdout.reconfigure(encoding="utf-8")

from changedetection import ChangeDetection, load_config

img_path, count = sys.argv[1], int(sys.argv[2])
cfg = load_config(sys.argv[3] if len(sys.argv) > 3 else 'config.json')
cd = ChangeDetection(cfg)
frame = cv2.imread(img_path)
assert frame is not None, f'이미지를 읽을 수 없음: {img_path}'
print(cd.upload(frame, count, title='static image test'))
