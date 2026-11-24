"""본인 촬영 영상으로 측정하는 스크립트 (보고서용 수치 수집, 서버 업로드 없음).

detect.py 와 같은 모델·임계값(yolov5s.pt, 640, conf 0.25, IoU 0.45, person 클래스)으로
프레임마다 다음을 기록한다.
  - persons      : YOLO 가 검출한 사람 수 (1-3 변화 감지의 입력)
  - faces_raw    : 원본 프레임에서 얼굴 검출기(--face-detector)가 찾은 얼굴 수
  - faces_blur   : blur_boxes(F1) 적용 후 같은 검출기가 찾은 얼굴 수
  - faces_blur_outside : faces_blur 중 얼굴 중심이 어떤 사람 박스에도 들어가지 않는 수
                         (YOLO 가 사람을 놓쳐서 블러가 안 된 경우 = 인식 단계 실패)

사용:
  venv/Scripts/python measure_input.py --source <영상> --out <결과 폴더> [--face-detector none|haar|yunet --face-model <onnx>]
  - haar : OpenCV 4.x 의 cv2.CascadeClassifier 가 있어야 함 (OpenCV 5.0 에는 없음)
  - yunet: cv2.FaceDetectorYN + face_detection_yunet ONNX 모델 파일 필요
결과: <out>/per_frame.csv, <out>/summary.json
"""
import argparse
import csv
import json
import sys
import time
from collections import Counter
from pathlib import Path

import cv2
import torch

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from changedetection import blur_boxes  # noqa: E402
from models.common import DetectMultiBackend  # noqa: E402
from utils.dataloaders import LoadImages  # noqa: E402
from utils.general import check_img_size, non_max_suppression, scale_boxes  # noqa: E402
from utils.torch_utils import select_device  # noqa: E402

# Haar 검출 파라미터 (OpenCV 기본 예제 값)
HAAR_SCALE, HAAR_NEIGHBORS, HAAR_MIN = 1.1, 5, (30, 30)
YUNET_SCORE = 0.9  # YuNet 기본 예제 값


def make_face_detector(kind, model_path=None):
    """(name, fn) 반환. fn(img) -> [(x, y, w, h), ...]. kind='none' 이면 None."""
    if kind == 'none':
        return None
    if kind == 'haar':
        cc = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        assert not cc.empty(), 'Haar cascade 로드 실패'

        def fn(img):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            return [tuple(r) for r in cc.detectMultiScale(gray, scaleFactor=HAAR_SCALE,
                                                          minNeighbors=HAAR_NEIGHBORS, minSize=HAAR_MIN)]
        return fn
    if kind == 'yunet':
        assert model_path and Path(model_path).exists(), 'YuNet 모델 파일(--face-model)이 필요함'
        det = cv2.FaceDetectorYN.create(str(model_path), '', (320, 320), YUNET_SCORE, 0.3, 5000)

        def fn(img):
            det.setInputSize((img.shape[1], img.shape[0]))
            _, faces = det.detect(img)
            return [] if faces is None else [tuple(f[:4]) for f in faces]
        return fn
    raise ValueError(kind)


def inside_any(cx, cy, boxes):
    return any(x1 <= cx <= x2 and y1 <= cy <= y2 for x1, y1, x2, y2 in boxes)


def stability_stats(counts, fps, stable_frames=30, min_interval=60.0):
    """프레임별 인원 수 시퀀스의 흔들림 통계 + 규칙 시뮬레이션(오프라인 계산)."""
    changes = sum(1 for a, b in zip(counts, counts[1:]) if a != b)
    runs = []  # (value, length)
    for c in counts:
        if runs and runs[-1][0] == c:
            runs[-1][1] += 1
        else:
            runs.append([c, 1])
    short_runs = sum(1 for _, n in runs if n < stable_frames)

    def simulate(stable, interval):
        state, cand, streak, last, ups = None, None, 0, float('-inf'), []
        for f, c in enumerate(counts):
            now = f / fps
            if c == state:
                cand, streak = None, 0
                continue
            if c == cand:
                streak += 1
            else:
                cand, streak = c, 1
            if streak >= stable and now - last >= interval:
                ups.append({'frame': f, 'time_s': round(now, 2), 'persons': c})
                state, cand, streak, last = c, None, 0, now
        return ups

    return {
        'frames': len(counts),
        'count_distribution': dict(sorted(Counter(counts).items())),
        'frame_to_frame_changes': changes,
        'runs_total': len(runs),
        f'runs_shorter_than_{stable_frames}_frames': short_runs,
        'longest_run_frames': max((n for _, n in runs), default=0),
        'sim_count_rule_default': simulate(stable_frames, min_interval),
        'sim_count_rule_no_interval': simulate(stable_frames, 0.0),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--weights', default=str(ROOT / 'yolov5s.pt'))
    ap.add_argument('--imgsz', type=int, default=640)
    ap.add_argument('--conf-thres', type=float, default=0.25)
    ap.add_argument('--iou-thres', type=float, default=0.45)
    ap.add_argument('--device', default='')
    ap.add_argument('--face-detector', choices=['none', 'haar', 'yunet'], default='none')
    ap.add_argument('--face-model', default=None, help='yunet ONNX 경로')
    opt = ap.parse_args()

    out = Path(opt.out)
    out.mkdir(parents=True, exist_ok=True)
    detect_faces = make_face_detector(opt.face_detector, opt.face_model)

    device = select_device(opt.device)
    model = DetectMultiBackend(opt.weights, device=device)
    stride, pt = model.stride, model.pt
    imgsz = check_img_size((opt.imgsz, opt.imgsz), s=stride)
    dataset = LoadImages(opt.source, img_size=imgsz, stride=stride, auto=pt)
    model.warmup(imgsz=(1, 3, *imgsz))
    fps = dataset.cap.get(cv2.CAP_PROP_FPS) or 30

    rows, counts = [], []
    t0 = time.time()
    for _path, im, im0s, _cap, _s in dataset:
        im = torch.from_numpy(im).to(model.device).float() / 255
        if im.ndim == 3:
            im = im[None]
        det = non_max_suppression(model(im), opt.conf_thres, opt.iou_thres, classes=[0], max_det=1000)[0]
        frame = dataset.frame
        raw = im0s.copy()
        boxes = []
        if len(det):
            det[:, :4] = scale_boxes(im.shape[2:], det[:, :4], raw.shape).round()
            boxes = det[:, :4].tolist()
        counts.append(len(boxes))
        row = {'frame': frame, 'time_s': round((frame - 1) / fps, 3), 'persons': len(boxes)}
        if detect_faces:
            faces_raw = detect_faces(raw)
            faces_blur = detect_faces(blur_boxes(raw.copy(), boxes))
            row.update(faces_raw=len(faces_raw), faces_blur=len(faces_blur),
                       faces_blur_outside=sum(1 for (x, y, w, h) in faces_blur
                                              if not inside_any(x + w / 2, y + h / 2, boxes)))
        rows.append(row)
    elapsed = time.time() - t0

    tag = opt.face_detector
    with open(out / f'per_frame_{tag}.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    summary = {
        'source_name': Path(opt.source).name,
        'fps': fps,
        'video_seconds': round(len(rows) / fps, 2),
        'processing_seconds': round(elapsed, 1),
        'settings': {'weights': Path(opt.weights).name, 'imgsz': opt.imgsz, 'conf': opt.conf_thres,
                     'iou': opt.iou_thres, 'classes': [0], 'face_detector': tag,
                     'face_model': Path(opt.face_model).name if opt.face_model else None},
        'persons': stability_stats(counts, fps),
    }
    if detect_faces:
        summary['faces'] = {
            'total_raw': sum(r['faces_raw'] for r in rows),
            'total_blur': sum(r['faces_blur'] for r in rows),
            'frames_with_face_raw': sum(1 for r in rows if r['faces_raw']),
            'frames_with_face_blur': sum(1 for r in rows if r['faces_blur']),
            'blur_faces_outside_person_box': sum(r['faces_blur_outside'] for r in rows),
            'frames_with_face_but_no_person': sum(1 for r in rows if r['faces_raw'] and not r['persons']),
        }
    (out / f'summary_{tag}.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
